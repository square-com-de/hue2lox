"""TLS-verified client for one configured Hue v2 light."""
import http.client
import json
import os
from pathlib import Path
import socket
import ssl
import time
import threading
from collections import OrderedDict
from color import rgb_values, rgb_xy, loxone_rgb, kelvin_mirek, loxone_lumitech, light_parameters


BRIDGE_DEADLINE_SECONDS = 5


class BridgeConnection(http.client.HTTPSConnection):
    """Keep the transport reachable even when HTTPResponse owns its file object."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._transport_lock = threading.Lock()
        self._transport_socket = None
        self.expired = threading.Event()

    def _track(self, sock):
        with self._transport_lock:
            if self.expired.is_set():
                sock.close()
                raise TimeoutError('bridge deadline exceeded')
            self._transport_socket = sock

    def expire(self):
        with self._transport_lock:
            self.expired.set()
            sock = self._transport_socket
            if sock is not None:
                # close alone may leave a makefile read blocked; shutdown wakes it.
                try:
                    sock.shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass

    def connect(self):
        raw = socket.create_connection((self.host, self.port), self.timeout)
        self._track(raw)
        try:
            self.sock = self._context.wrap_socket(
                raw, server_hostname=self.bridge_id, do_handshake_on_connect=False)
            self._track(self.sock)
            self.sock.do_handshake()
        except BaseException:
            raw.close()
            if self.sock is not None:
                self.sock.close()
            raise


def tls_context():
    context = ssl.create_default_context(cafile=os.environ.get('HUE_CA_FILE', '/app/trust/huebridge-ca.pem'))
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    if not context.hostname_checks_common_name:
        raise RuntimeError('TLS runtime lacks required CN validation')
    context.verify_flags &= ~getattr(ssl, 'VERIFY_X509_STRICT', 0)
    return context


class BridgeRequestError(ValueError):
    """Sanitized bridge transport/protocol/response failure for API boundaries."""


def decode_json_document(raw, strict=False):
    """Bound nesting before parsing, independently of Python's recursion policy."""
    text = raw.decode('utf-8') if isinstance(raw, bytes) else raw
    depth = 0
    quoted = escaped = False
    for char in text:
        if quoted:
            if escaped:
                escaped = False
            elif char == '\\':
                escaped = True
            elif char == '"':
                quoted = False
        elif char == '"':
            quoted = True
        elif char in '[{':
            depth += 1
            if depth > 64:
                raise ValueError('JSON nesting limit exceeded')
        elif char in ']}':
            depth -= 1
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('duplicate JSON key')
            result[key] = value
        return result
    def constant(value):
        raise ValueError('non-finite JSON constant')
    return json.loads(text, object_pairs_hook=pairs, parse_constant=constant) if strict else json.loads(text)


def legacy_target():
    target = os.environ.get('HUE_LIGHT_ID')
    if os.environ.get('HUE_REGISTRY_FILE'):
        from bridge_store import read_registry
        for bridge in read_registry()['bridges']:
            for light in bridge.get('lights', []):
                matches = light['id'] == target if target else light.get('control_path') == '/hue-go/state'
                if matches and light.get('present') is not False and not light.get('ignored') and not light.get('removed'):
                    if bridge.get('enabled') is not True or not bridge.get('key_file'):
                        raise ValueError('legacy light bridge disabled')
                    return bridge, light['id']
        raise ValueError('legacy light is not configured')
    host, identity = os.environ.get('HUE_BRIDGE_IP'), os.environ.get('HUE_BRIDGE_ID')
    if not host or not identity or not target:
        raise ValueError('legacy bridge and light must be configured explicitly')
    return {'host':host, 'bridge_id':identity,
            'key_file':os.environ.get('HUE_KEY_FILE', '/run/secrets/hue_key')}, target


def default_bridge():
    return legacy_target()[0]


def request_document(method, path, payload=None, bridge=None, authenticated=True):
    bridge = bridge or default_bridge()
    conn = None
    timer = None
    response = None
    try:
        headers = {'Accept': 'application/json'}
        if authenticated:
            key = Path(bridge['key_file']).read_text().strip()
            if not key or '\n' in key or '\r' in key:
                raise ValueError('invalid key file')
            headers['hue-application-key'] = key
        conn = BridgeConnection(bridge['host'], timeout=BRIDGE_DEADLINE_SECONDS, context=tls_context())
        conn.bridge_id = bridge['bridge_id']
        timer = threading.Timer(BRIDGE_DEADLINE_SECONDS, conn.expire)
        timer.daemon = True
        started = time.monotonic()
        timer.start()
        body = None
        if payload is not None:
            body = json.dumps(payload, allow_nan=False).encode()
            headers['Content-Type'] = 'application/json'
        conn.request(method, path, body=body, headers=headers)
        response = conn.getresponse()
        body = response.read(4194305)
        if time.monotonic() - started >= BRIDGE_DEADLINE_SECONDS:
            raise TimeoutError('bridge deadline exceeded')
        if response.status != 200 or len(body) > 4194304:
            raise ValueError('bridge HTTP response invalid')
        return decode_json_document(body)
    except (OSError, http.client.HTTPException, ValueError, RecursionError):
        raise BridgeRequestError('bridge request failed') from None
    finally:
        if timer is not None:
            timer.cancel()
            timer.join()
        if response is not None:
            response.close()
        if conn is not None:
            try:
                conn.close()
            except (OSError, http.client.HTTPException):
                pass


def request_resources(bridge, kind=''):
    if kind not in ('', 'light'):
        raise ValueError('invalid resource kind')
    document = request_document('GET', '/clip/v2/resource' + ('/' + kind if kind else ''), bridge=bridge)
    if type(document) is not dict or document.get('errors') != [] or type(document.get('data')) is not list or any(type(item) is not dict for item in document['data']):
        raise BridgeRequestError('bridge API response invalid')
    return document['data']


def request_light(method, payload=None, bridge=None, target_light=None):
    if target_light is None:
        configured_bridge, light_id = legacy_target()
        bridge = bridge or configured_bridge
    else:
        light_id = target_light
    document = request_document(method, '/clip/v2/resource/light/' + light_id, payload=payload, bridge=bridge)
    resources = document.get('data') if type(document) is dict else None
    if type(document) is not dict or document.get('errors') != [] or type(resources) is not list or len(resources) != 1 or type(resources[0]) is not dict:
        raise BridgeRequestError('bridge API response invalid')
    return light_id, resources[0]


def light_status(light_id, light):
    if light.get('id') != light_id or light.get('type') != 'light':
        raise ValueError('unexpected resource')
    on = light.get('on', {}).get('on')
    brightness = light.get('dimming', {}).get('brightness')
    if type(on) is not bool:
        raise ValueError('invalid lamp state')
    if 'dimming' in light and (type(brightness) not in (int, float) or not 0 <= brightness <= 100):
        raise ValueError('invalid dimming state')
    return {'status': 'ok', 'light_id': light_id,
            'xy': light.get('color', {}).get('xy'), 'color_temperature': light.get('color_temperature'),
            'name': light.get('metadata', {}).get('name', ''),
            'on': on, 'brightness': brightness, 'tls_verified': True}


def read_status(bridge=None, light_id=None):
    if bridge is None and light_id is None:
        light_id, light = request_light('GET')
    else:
        light_id, light = request_light('GET', bridge=bridge, target_light=light_id)
    return light_status(light_id, light)


def read_bridge_statuses(bridge):
    result = {}
    for light in request_resources(bridge, 'light'):
        if light.get('type') == 'light' and isinstance(light.get('id'), str):
            try:
                result[light['id']] = light_status(light['id'], light)
            except ValueError:
                continue
    return result


def state_payload(state, light=None):
    """Validate everything before opening a bridge connection."""
    import math
    if type(state) is not dict or not state or set(state) - {'on', 'brightness', 'rgb', 'loxone_rgb', 'kelvin', 'loxone_lumitech'}:
        raise ValueError('expected supported state fields')
    if 'loxone_lumitech' in state:
        if len(state) != 1:
            raise ValueError('loxone_lumitech cannot be combined with other fields')
        return state_payload(loxone_lumitech(state['loxone_lumitech']), light)
    if 'kelvin' in state:
        if set(state) - {'kelvin','brightness','on'} or state.get('on') is False:
            raise ValueError('temperature conflicts with color or off')
        mirek = kelvin_mirek(state['kelvin'], light)
        base = state_payload({k:v for k,v in state.items() if k != 'kelvin'} or {'on':True}, light)
        if not base['on']['on']:
            return base
        return {**base,'color_temperature':{'mirek':mirek}}
    if 'loxone_rgb' in state:
        if len(state) != 1:
            raise ValueError('loxone_rgb cannot be combined with other fields')
        return state_payload(loxone_rgb(state['loxone_rgb']), light)
    if 'rgb' in state:
        values = rgb_values(state['rgb'])
        if state.get('on') is False:
            raise ValueError('rgb cannot be combined with off')
        if 'on' in state and type(state['on']) is not bool:
            raise ValueError('on must be boolean')
        if not any(values):
            if state.get('on') is True or state.get('brightness', 0) != 0:
                raise ValueError('black conflicts with on or brightness')
            if 'brightness' in state and type(state['brightness']) not in (int, float):
                raise ValueError('invalid brightness')
            return {'on': {'on': False}}
        base = state_payload({k: v for k,v in state.items() if k != 'rgb'} or {'on': True}, light)
        if base['on']['on'] is False:
            return base
        x,y = rgb_xy(state['rgb'], light)
        return {**base, 'color': {'xy': {'x': x, 'y': y}}}
    if 'on' in state and type(state['on']) is not bool:
        raise ValueError('on must be boolean')
    if 'brightness' in state:
        value = state['brightness']
        if type(value) not in (int, float) or not math.isfinite(value) or not 0 <= value <= 100:
            raise ValueError('brightness must be finite and between 0 and 100')
        if state.get('on') is False and value > 0:
            raise ValueError('off conflicts with positive brightness')
        if state.get('on') is True and value == 0:
            raise ValueError('on conflicts with zero brightness')
        if value == 0:
            return {'on': {'on': False}}
        return {'on': {'on': True}, 'dimming': {'brightness': value}}
    return {'on': {'on': state['on']}}


# Old installations acquire device limits lazily, without requiring a rescan.
# Store only conversion data, bounded in size and age; never credentials.
_PARAMETER_CACHE = OrderedDict()
_PARAMETER_LOCK = threading.Lock()


def parameters_for(bridge, light_id):
    bridge = bridge or default_bridge()
    light_id = light_id or legacy_target()[1]
    for item in bridge.get('lights', []):
        if item.get('id') == light_id and type(item.get('color_parameters')) is dict:
            return light_parameters(item['color_parameters'])
    cache_key = (bridge['host'], bridge.get('bridge_id'), light_id)
    with _PARAMETER_LOCK:
        cached = _PARAMETER_CACHE.get(cache_key)
        if cached and time.monotonic() - cached[0] < 300:
            return cached[1]
    reference, resource = request_light('GET', bridge=bridge, target_light=light_id)
    if reference != light_id or resource.get('id') != light_id or resource.get('type') != 'light':
        raise ValueError('unexpected resource for color parameters')
    parameters = light_parameters(resource)
    with _PARAMETER_LOCK:
        _PARAMETER_CACHE[cache_key] = (time.monotonic(), parameters)
        _PARAMETER_CACHE.move_to_end(cache_key)
        while len(_PARAMETER_CACHE) > 2048:
            _PARAMETER_CACHE.popitem(last=False)
    return parameters


def write_state(state, bridge=None, light_id=None):
    payload = state_payload(state)
    if 'color' in payload or 'color_temperature' in payload:
        payload = state_payload(state, parameters_for(bridge, light_id))
    if bridge is None and light_id is None:
        light_id, result = request_light('PUT', payload)
    else:
        light_id, result = request_light('PUT', payload, bridge=bridge, target_light=light_id)
    if result.get('rid') != light_id or result.get('rtype') != 'light':
        raise ValueError('unexpected command acknowledgement')
    # This confirms bridge acknowledgement, not observed physical lamp state.
    return {'status': 'accepted', 'light_id': light_id, 'requested': state,
            'tls_verified': True}


if __name__ == '__main__':
    try:
        print(json.dumps(read_status(), ensure_ascii=False))
    except Exception as error:
        print(json.dumps({'status': 'error', 'error_type': type(error).__name__}))
        raise SystemExit(1)
