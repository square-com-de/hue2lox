"""Administrator-only bridge onboarding, physical-button pairing and read-only inventory."""
import copy
from color import light_parameters
from datetime import datetime, timezone
import hashlib
import ipaddress
import re
import socket
import ssl
import threading
from pathlib import Path

import scenes
import bridge_store
from hue_client import tls_context, request_document, request_resources

LOCK = threading.Lock()
BRIDGE_LOCKS = {}
NETWORKS = tuple(ipaddress.ip_network(value) for value in ('10.0.0.0/8', '172.16.0.0/12', '192.168.0.0/16'))


class BridgeError(Exception):
    def __init__(self, code, status=400):
        self.code, self.status = code, status
        super().__init__(code)


def local_host(value):
    try:
        address = ipaddress.ip_address(value)
        if address.version == 4 and any(address in network for network in NETWORKS):
            return str(address)
    except (ValueError, TypeError):
        pass
    raise BridgeError('invalid_bridge_ip')


def operation_lock(bridge_ref):
    if not isinstance(bridge_ref, str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,64}', bridge_ref):
        raise BridgeError('invalid_bridge_reference')
    with LOCK:
        return BRIDGE_LOCKS.setdefault(bridge_ref, threading.Lock())


def bridge_record(bridge_ref):
    for bridge in bridge_store.read_registry()['bridges']:
        if bridge['id'] == bridge_ref:
            return bridge
    raise BridgeError('bridge_not_found', 404)


def probe(host):
    host = local_host(host)
    context = tls_context()
    # Bootstrap only: verify the Hue CA, signature and expiry before learning
    # the signed bridge identity. Subsequent requests also validate its name.
    context.check_hostname = False
    context.verify_mode = ssl.CERT_REQUIRED
    try:
        with socket.create_connection((host, 443), timeout=5) as raw:
            with context.wrap_socket(raw, server_hostname=None) as connection:
                certificate = connection.getpeercert()
                der = connection.getpeercert(binary_form=True)
        identities = [value for group in certificate.get('subject', ()) for key, value in group if key == 'commonName']
        if len(identities) != 1 or not re.fullmatch(r'[0-9A-Fa-f]{16}', identities[0]):
            raise BridgeError('unsupported_bridge_identity')
        bridge_id = identities[0].upper()
        info = request_document('GET', '/api/config', bridge={'host': host, 'bridge_id': bridge_id}, authenticated=False)
        if type(info) is not dict or str(info.get('bridgeid','')).upper() != bridge_id:
            raise BridgeError('bridge_identity_mismatch', 409)
        fingerprint = ':'.join(re.findall('..', hashlib.sha256(der).hexdigest().upper()))
        return {'host':host, 'bridge_id':bridge_id, 'bridge_name':str(info.get('name', 'Hue Bridge'))[:128],
                'model':str(info.get('modelid',''))[:64], 'firmware':str(info.get('swversion',''))[:64],
                'certificate_sha256':fingerprint, 'tls_verified':True}
    except ssl.SSLCertVerificationError:
        raise BridgeError('bridge_certificate_invalid', 502) from None
    except (OSError, ValueError):
        raise BridgeError('bridge_unreachable', 502) from None


def public_bridge(bridge):
    result = {key:bridge.get(key) for key in ('id','name','host','bridge_id','model','firmware','certificate_sha256','last_scan')}
    result.update(enabled=bridge.get('enabled') is True,
                  paired=bool(bridge.get('key_file')) and Path(bridge['key_file']).is_file(),
                  light_count=sum(light.get('present') is not False and not light.get('ignored') and not light.get('removed') for light in bridge.get('lights',[])),
                  scene_count=sum(scene.get('present') is not False and not scene.get('ignored') and not scene.get('removed') for scene in bridge.get('scenes',[])),
                  ignored_count=sum(bool(light.get('ignored')) and not light.get('removed') for light in bridge.get('lights',[])),
                  missing_count=sum(light.get('present') is False for light in bridge.get('lights',[])))
    return result


def list_bridges():
    return [public_bridge(bridge) for bridge in bridge_store.read_registry()['bridges']]


def add_bridge(name, host):
    if not isinstance(name,str) or not 1 <= len(name.strip()) <= 80:
        raise BridgeError('invalid_bridge_name')
    identity = probe(host)
    def change(document):
        bridges = document['bridges']
        bridge = next((b for b in bridges if b.get('bridge_id') == identity['bridge_id']), None)
        if bridge is None:
            bridge = next((b for b in bridges if b['host'] == identity['host']), None)
        if bridge is not None and bridge.get('bridge_id') not in (None, identity['bridge_id']):
            raise BridgeError('bridge_identity_mismatch',409)
        if bridge is None:
            if len(bridges) >= 32:
                raise BridgeError('bridge_limit',409)
            bridge = {'id':'hue-'+identity['bridge_id'].lower(), 'enabled':False, 'lights':[]}
            bridges.append(bridge)
        if any(b is not bridge and b['host'] == identity['host'] for b in bridges):
            raise BridgeError('bridge_address_conflict',409)
        bridge.update({key:value for key,value in identity.items() if key not in ('bridge_name','tls_verified')})
        bridge['name'] = name.strip()
        return copy.deepcopy(bridge)
    return public_bridge(bridge_store.update_registry(change))


def collect_lights(resources):
    if type(resources) is not list or len(resources) > 20000 or any(type(item) is not dict for item in resources):
        raise BridgeError('invalid_inventory',502)
    devices = {item['id']:item for item in resources if item.get('type') == 'device' and isinstance(item.get('id'),str)}
    for item in resources:
        for field in ('metadata','owner','product_data'):
            if field in item and type(item[field]) is not dict:
                raise BridgeError('invalid_inventory',502)
        if item.get('type') == 'room' and (type(item.get('children',[])) is not list or any(type(child) is not dict for child in item.get('children',[]))):
            raise BridgeError('invalid_inventory',502)
    rooms = {}
    for item in resources:
        if item.get('type') == 'room':
            for child in item.get('children',[]):
                if child.get('rtype') == 'device':
                    rooms[child.get('rid')] = str(item.get('metadata',{}).get('name',''))[:256]
    lights = []
    seen = set()
    for item in resources:
        if item.get('type') != 'light':
            continue
        reference = item.get('id')
        if not isinstance(reference,str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,128}',reference) or reference in seen:
            raise BridgeError('invalid_inventory',502)
        seen.add(reference)
        device = devices.get(item.get('owner',{}).get('rid'), {})
        product = device.get('product_data',{})
        capabilities = ['on']
        for key, capability in [('dimming','brightness'),('color','rgb'),('color_temperature','temperature')]:
            if type(item.get(key)) is dict:
                capabilities.append(capability)
        lights.append({'id':reference, 'name':str(item.get('metadata',{}).get('name',reference))[:256],
                       'room':rooms.get(device.get('id'),''), 'model':str(product.get('model_id',''))[:64],
                       'archetype':str(product.get('product_archetype') or device.get('metadata',{}).get('archetype') or item.get('metadata',{}).get('archetype',''))[:80],
                       'product_name':str(product.get('product_name',''))[:256], 'manufacturer':str(product.get('manufacturer_name',''))[:128], 'capabilities':capabilities, 'color_parameters':light_parameters(item), 'present':True})
    if len(lights) > 1000:
        raise BridgeError('lamp_limit',409)
    return sorted(lights, key=lambda light: (light['room'].casefold(), light['name'].casefold(), light['id']))


def apply_inventory(original, discovered, discovered_scenes=None):
    def change(document):
        bridge = next((b for b in document['bridges'] if b['id'] == original['id']),None)
        if bridge is None or bridge['host'] != original['host'] or bridge.get('bridge_id') != original.get('bridge_id'):
            raise BridgeError('bridge_changed_retry',409)
        previous = {light['id']:light for light in bridge.get('lights',[])}
        merged = []
        found = set()
        for light in discovered:
            found.add(light['id'])
            # Keep stable aliases and explicit icon preferences across rescans.
            merged_light={**previous.get(light['id'],{}), **light, 'removed':False}
            # The bridge must never overwrite the user's local visual preference.
            saved_icon=previous.get(light['id'],{}).get('icon_override')
            merged_light.pop('icon_override',None)
            if saved_icon is not None: merged_light['icon_override']=saved_icon
            merged.append(merged_light)
        for reference, light in previous.items():
            if reference not in found:
                merged.append({**light,'present':False})
        bridge['lights'] = merged
        if discovered_scenes is not None:
            previous_scenes={scene['id']:scene for scene in bridge.get('scenes',[])}
            # A successful full inventory is authoritative; deleted scenes vanish.
            # Local ignore flags survive rediscovery; local removals last until rescan.
            bridge['scenes'] = [{**previous_scenes.get(scene['id'],{}), **scene, 'removed':False}
                                for scene in discovered_scenes]
        bridge['last_scan'] = datetime.now(timezone.utc).isoformat()
        bridge['enabled'] = True
        return copy.deepcopy(bridge)
    return public_bridge(bridge_store.update_registry(change))


def scan_bridge(bridge_ref):
    lock = operation_lock(bridge_ref)
    if not lock.acquire(blocking=False):
        raise BridgeError('bridge_busy',409)
    try:
        bridge = bridge_record(bridge_ref)
        if not bridge.get('key_file') or not Path(bridge['key_file']).is_file():
            raise BridgeError('pairing_required',409)
        try:
            resources = request_resources(bridge)
            discovered = collect_lights(resources)
            discovered_scenes = scenes.collect(resources)
        except (OSError, ValueError):
            raise BridgeError('inventory_unavailable',502) from None
        return apply_inventory(bridge, discovered, discovered_scenes)
    finally:
        lock.release()


def pair_bridge(bridge_ref, replace=False):
    if type(replace) is not bool:
        raise BridgeError('invalid_pairing_option')
    lock = operation_lock(bridge_ref)
    if not lock.acquire(blocking=False):
        raise BridgeError('bridge_busy',409)
    try:
        bridge = bridge_record(bridge_ref)
        identity = probe(bridge['host'])
        if bridge.get('bridge_id') not in (None,identity['bridge_id']):
            raise BridgeError('bridge_identity_mismatch',409)
        bridge.update({key:value for key,value in identity.items() if key not in ('bridge_name','tls_verified')})
        key_path = bridge_store.state_dir() / 'bridge-keys' / (bridge_ref + '.key')
        if replace or not bridge.get('key_file') or not Path(bridge['key_file']).is_file():
            if key_path.is_file() and not replace:
                bridge['key_file'] = str(key_path)
            else:
                try:
                    result = request_document('POST','/api',payload={'devicetype':'hue2lox#web'},bridge=bridge,authenticated=False)
                except (OSError,ValueError):
                    raise BridgeError('pairing_unavailable',502) from None
                if type(result) is not list or len(result) != 1 or type(result[0]) is not dict:
                    raise BridgeError('pairing_unavailable',502)
                if type(result[0].get('error',{})) is not dict or type(result[0].get('success',{})) is not dict:
                    raise BridgeError('pairing_unavailable',502)
                if result[0].get('error',{}).get('type') == 101:
                    raise BridgeError('press_link_button',409)
                username = result[0].get('success',{}).get('username')
                if not username:
                    raise BridgeError('pairing_rejected',502)
                bridge['key_file'] = bridge_store.save_bridge_key(bridge_ref, username)
        # Persist the key reference before inventory, so a retry never creates
        # another Hue application key after a transient scan failure.
        def save_pairing(document):
            current = next((b for b in document['bridges'] if b['id'] == bridge_ref),None)
            if current is None or current['host'] != bridge['host']:
                raise BridgeError('bridge_changed_retry',409)
            current.update({key:value for key,value in bridge.items() if key != 'lights'})
            current['enabled'] = True
        bridge_store.update_registry(save_pairing)
        try:
            resources = request_resources(bridge)
            discovered = collect_lights(resources)
            discovered_scenes = scenes.collect(resources)
            return {'bridge':apply_inventory(bridge,discovered,discovered_scenes),'inventory_ready':True}
        except (OSError,ValueError,BridgeError):
            return {'bridge':public_bridge(bridge_record(bridge_ref)), 'inventory_ready':False}
    finally:
        lock.release()


def manage_light(bridge_ref, light_ref, action, ignored=True):
    return manage_resource(bridge_ref,light_ref,action,ignored,'lights')


def manage_scene(bridge_ref, scene_ref, action, ignored=True):
    return manage_resource(bridge_ref,scene_ref,action,ignored,'scenes')


def manage_resource(bridge_ref, light_ref, action, ignored=True, collection='lights'):
    """Local visibility only. Tombstones retain aliases until rediscovery."""
    if not isinstance(light_ref, str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,128}', light_ref):
        raise BridgeError('invalid_light_reference')
    if action not in ('ignore', 'remove') or type(ignored) is not bool:
        raise BridgeError('invalid_light_option')
    lock = operation_lock(bridge_ref)
    if not lock.acquire(blocking=False):
        raise BridgeError('bridge_busy',409)
    try:
        def change(document):
            bridge = next((b for b in document['bridges'] if b['id'] == bridge_ref),None)
            if bridge is None:
                raise BridgeError('bridge_not_found',404)
            light = next((l for l in bridge.get(collection,[]) if l['id'] == light_ref and not l.get('removed')),None)
            if light is None:
                raise BridgeError('scene_not_found' if collection == 'scenes' else 'light_not_found',404)
            light['ignored' if action == 'ignore' else 'removed'] = ignored if action == 'ignore' else True
            return {'id':light_ref, 'ignored':bool(light.get('ignored')), 'removed':bool(light.get('removed'))}
        return bridge_store.update_registry(change)
    finally:
        lock.release()
