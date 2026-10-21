import lamp_types
"""HTTPS health, Hue Go status and explicitly enabled state commands."""
import json
import io
import zipfile
import os
import ssl
import socket
import threading
import time
import request_monitor
import discovery
import scenes
import bridge_admin
import dashboard
import admin_auth
import loxone_export
from urllib.parse import urlsplit
from hue_client import read_status, state_payload, write_state, BridgeRequestError, decode_json_document
from pathlib import Path
import hmac
from dashboard import overview
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


def parse_request_json(raw):
    """Reject ambiguous/non-standard JSON and fail safely on excessive nesting."""
    try:
        return decode_json_document(raw, strict=True)
    except RecursionError:
        raise ValueError('JSON nesting limit exceeded') from None


class BoundedHTTPSServer(ThreadingHTTPServer):
    """Keep TLS negotiation (when a context is given) out of accept(), with bounded worker resources."""
    handshake_timeout = 5
    request_timeout = 5
    max_connections = 32

    def __init__(self, address, handler, context):
        self.tls_context = context
        self.connection_slots = threading.BoundedSemaphore(self.max_connections)
        super().__init__(address, handler)

    def process_request(self, request, client_address):
        # Never wait for a worker slot in the accept loop.
        if not self.connection_slots.acquire(blocking=False):
            self.shutdown_request(request)
            return
        try:
            super().process_request(request, client_address)
        except Exception:
            self.connection_slots.release()
            raise

    def process_request_thread(self, request, client_address):
        try:
            if self.tls_context is not None:
                request.settimeout(self.handshake_timeout)
                request = self.tls_context.wrap_socket(
                    request, server_side=True, do_handshake_on_connect=False)
                request.do_handshake()
            request.settimeout(self.request_timeout)
            # The base implementation handles HTTP errors and closes the socket.
            super().process_request_thread(request, client_address)
        except (OSError, ValueError):
            # Incomplete/invalid handshakes contain no useful application data.
            # Do not log their content or credentials.
            self.shutdown_request(request)
        finally:
            self.connection_slots.release()


class Handler(BaseHTTPRequestHandler):
    def handle_one_request(self):
        # A socket timeout is only an inactivity timeout. A client sending one
        # header byte at a time must not keep a worker indefinitely.
        self._header_deadline = time.monotonic() + getattr(self.server, 'request_timeout', 5)
        self._reading_headers = True
        def expire():
            if self._reading_headers:
                try:
                    self.connection.shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass
        self._header_timer = threading.Timer(max(0, self._header_deadline-time.monotonic()), expire)
        self._header_timer.daemon = True
        self._header_timer.start()
        try:
            super().handle_one_request()
        except OSError:
            # Disconnects and absolute deadline shutdowns are expected.
            self.close_connection = True
        finally:
            self._reading_headers = False
            self._header_timer.cancel()

    def parse_request(self):
        try:
            valid = super().parse_request()
            return valid and time.monotonic() < self._header_deadline
        finally:
            self._reading_headers = False
            self._header_timer.cancel()

    def read_body(self, length):
        deadline = time.monotonic() + getattr(self.server, 'request_timeout', 5)
        body = bytearray()
        while len(body) < length:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise ValueError('body deadline exceeded')
            self.connection.settimeout(remaining)
            chunk = self.rfile.read1(length - len(body))
            if not chunk:
                raise ValueError('incomplete body')
            body.extend(chunk)
        return bytes(body)

    def do_GET(self):
        if self.path == '/assets/hue-models.csv':
            self.send_response(302)
            self.send_header('Location', '/assets/hue-models.zip')
            self.send_header('Content-Length', '0')
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
            return
        if request_monitor.control_path(self.path):
            self.wrong_control_method()
            return
        assets = {'/assets/project-license.txt':('../LICENSE','text/plain; charset=utf-8'), '/assets/project-notice.txt':('../NOTICE','text/plain; charset=utf-8'), '/assets/third-party-notices.txt':('../THIRD-PARTY-NOTICES.md','text/plain; charset=utf-8'), '/assets/i18n.js':('i18n.js','text/javascript; charset=utf-8'), '/assets/locales/de.js':('locales/de.js','text/javascript; charset=utf-8'), '/assets/locales/en.js':('locales/en.js','text/javascript; charset=utf-8'), '/tutorial/en':('tutorial-en.html','text/html; charset=utf-8'), '/licenses':('licenses.html','text/html; charset=utf-8'), '/assets/catalog-license.txt':('../catalog/LICENSE-zigbee-herdsman-converters','text/plain; charset=utf-8'), '/assets/hue-models.zip':('../catalog/hue-models.csv','application/zip'),'/': ('index.html','text/html; charset=utf-8'),
                  '/tutorial': ('tutorial.html','text/html; charset=utf-8'),
                  '/assets/tutorial.css': ('tutorial.css','text/css; charset=utf-8'),
                  '/assets/tutorial-config.png': ('tutorial-config.png','image/png'),
                  '/assets/tutorial-commands.png': ('tutorial-commands.png','image/png'),
                  '/assets/tutorial-monitor.png': ('tutorial-monitor.png','image/png'),
                  '/assets/app.css': ('app.css','text/css; charset=utf-8'),
                  '/assets/monitor.js': ('monitor.js','text/javascript; charset=utf-8'),
                  '/assets/discovery.js': ('discovery.js','text/javascript; charset=utf-8'),
                  '/assets/scenes.js': ('scenes.js','text/javascript; charset=utf-8'),
                  '/assets/bridges.js': ('bridges.js','text/javascript; charset=utf-8'),
                  '/assets/admin.js': ('admin.js','text/javascript; charset=utf-8'),
                  '/assets/app.js': ('app.js','text/javascript; charset=utf-8'),
                  '/assets/lamp-icons.js': ('lamp-icons.js','text/javascript; charset=utf-8'),
                  '/assets/hue2lox-logo.png': ('hue2lox-logo.png','image/png'),
                  '/assets/octopus.png': ('octopus.png','image/png')}
        if self.path in assets:
            filename, content_type = assets[self.path]
            if self.path == '/assets/hue-models.zip':
                buffer = io.BytesIO()
                catalog = Path(__file__).resolve().parent.parent / 'catalog'
                with zipfile.ZipFile(buffer, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
                    for source, target in [('hue-models.csv','Hue-Modelltabelle.csv'),
                                           ('LICENSE-zigbee-herdsman-converters','LICENSE.txt'),
                                           ('README.md','SOURCE.md')]:
                        archive.writestr(target, (catalog / source).read_bytes())
                body = buffer.getvalue()
            else:
                body = (Path(__file__).resolve().parent.parent / 'web' / filename).read_bytes()
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            if self.path == '/assets/hue-models.zip':
                self.send_header('Content-Disposition','attachment; filename="Hue-Modelltabelle.zip"')
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Cache-Control','no-store')
            self.send_header('X-Content-Type-Options','nosniff')
            self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self' data:; object-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")
            self.end_headers()
            self.wfile.write(body)
            return
        if self.path == '/api/admin/session':
            entry = self.require_admin()
            if entry:
                self.send_json(200, {'status': 'ok', 'username': entry['username'], 'csrf': entry['csrf']})
            return
        if self.path == '/api/admin/bridges':
            if self.require_admin():
                try:
                    self.send_json(200, {'status':'ok', 'bridges':bridge_admin.list_bridges()})
                except (ValueError, OSError, KeyError):
                    self.send_json(503, {'status':'error', 'error':'configuration_unavailable'})
            return
        if self.path == '/api/admin/monitor':
            if self.require_admin():
                self.send_json(200, {'status':'ok', **request_monitor.snapshot()})
            return
        if self.path == '/api/admin/miniserver':
            if self.require_admin():
                try:
                    self.send_json(200, {'status':'ok','miniserver':discovery.saved_miniserver()})
                except (ValueError,OSError,KeyError):
                    self.send_json(503, {'status':'error','error':'configuration_unavailable'})
            return
        if self.path == '/api/admin/scenes':
            if self.require_admin():
                try:
                    items=scenes.available_scenes()
                    for item in items:
                        item['writes_enabled']=os.environ.get('HUE_WRITES_ENABLED') == '1'
                    self.send_json(200, {'status':'ok','base_url':loxone_export.public_url(),'scenes':items})
                except (ValueError,OSError,KeyError):
                    self.send_json(503, {'status':'error','error':'configuration_unavailable'})
            return
        if self.path == '/api/admin/lights':
            if self.require_admin():
                try:
                    self.send_json(200, {'status': 'ok', 'base_url': loxone_export.public_url(), 'lights': loxone_export.lights()})
                except (ValueError, OSError, KeyError):
                    self.send_json(503, {'status':'error', 'error':'configuration_unavailable'})
            return
        if self.path == '/api/overview':
            if not self.require_admin():
                return
            try:
                self.send_json(200, overview())
            except Exception:
                self.send_json(503, {'status':'error','error':'overview_unavailable'})
            return
        if self.path == '/health':
            result = {'status': 'ok'}
        elif self.path == '/hue-go/status':
            if os.environ.get('HUE_LEGACY_ENABLED','1') != '1':
                self.send_error(404)
                return
            try:
                result = read_status()
            except Exception as error:
                # Never include bridge response bodies, headers, or credentials.
                print('Hue status failed: ' + type(error).__name__, flush=True)
                self.send_json(502, {'status': 'error', 'error': 'bridge_unavailable'})
                return
        else:
            self.send_error(404)
            return
        self.send_json(200, result)

    def do_PUT(self):
        self.monitor_reason=None
        self.monitor_handle=request_monitor.begin(self.command,self.client_address[0],self.path)
        try:
            self.control_put()
        finally:
            self.monitor_handle=None
            self.monitor_reason=None

    def wrong_control_method(self):
        self.monitor_reason=None
        self.monitor_handle=request_monitor.begin(self.command,self.client_address[0],self.path) if request_monitor.control_path(self.path) else None
        try:
            self.close_connection=True
            self.send_response(405)
            self.send_header('Allow','PUT')
            self.send_header('Content-Length','0')
            self.security_headers()
            self.end_headers()
        finally:
            self.monitor_handle=None
            self.monitor_reason=None

    def control_put(self):
        if self.path == '/hue-go/state' and os.environ.get('HUE_LEGACY_ENABLED','1') != '1':
            self.send_json(404, {'status':'error','error':'not_found'})
            return
        try:
            scene_command = self.path.startswith('/api/scenes/')
            target = scenes.resolve_path(self.path) if scene_command else (None if self.path == '/hue-go/state' else loxone_export.resolve_path(self.path))
        except (ValueError, OSError, KeyError):
            self.send_json(503, {'status': 'error', 'error': 'configuration_unavailable'})
            return
        if self.path != '/hue-go/state' and target is None:
            self.send_error(404)
            return
        if target is not None:
            request_monitor.update(getattr(self,'monitor_handle',None),path=self.path)
        self.close_connection = True
        if os.environ.get('HUE_WRITES_ENABLED') != '1':
            self.send_json(403, {'status': 'error', 'error': 'writes_disabled'})
            return
        try:
            token = Path(os.environ.get('HUE_CONTROL_TOKEN_FILE', '/run/secrets/control_token')).read_text().strip()
        except OSError:
            self.send_json(503, {'status': 'error', 'error': 'control_not_configured'})
            return
        authorization = self.headers.get('Authorization', '')
        if len(token) < 32 or not hmac.compare_digest(authorization.encode(), ('Bearer ' + token).encode()):
            self.send_json(401, {'status': 'error', 'error': 'unauthorized'})
            return
        if self.headers.get('Transfer-Encoding') is not None or len(self.headers.get_all('Content-Length', [])) != 1:
            self.send_json(400, {'status': 'error', 'error': 'invalid_length'})
            return
        if self.headers.get_content_type() != 'application/json':
            self.send_json(415, {'status': 'error', 'error': 'expected_json'})
            return
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if not 0 < length <= 1024:
                raise ValueError('invalid length')
            self.connection.settimeout(5)
            raw = b''
            read_error = None
            deadline = time.monotonic() + getattr(self.server, 'request_timeout', 5)
            try:
                while len(raw) < length:
                    remaining = deadline-time.monotonic()
                    if remaining <= 0:
                        raise TimeoutError('body deadline exceeded')
                    self.connection.settimeout(remaining)
                    chunk = self.rfile.read1(length-len(raw))
                    if not chunk:
                        read_error = 'eof'
                        break
                    raw += chunk
            except TimeoutError:
                read_error = 'timeout'
            except OSError:
                read_error = 'io_error'
            handle = getattr(self,'monitor_handle',None)
            extra = b''
            # Diagnostic only: never use bytes beyond Content-Length for control.
            # The connection is already marked for closure and will never be reused.
            if handle is not None and len(raw) == length:
                try:
                    json.loads(raw)
                except (ValueError, UnicodeError):
                    self.connection.settimeout(0.15)
                    try:
                        extra = self.rfile.read1(64)
                    except OSError:
                        pass
            request_monitor.record_body(handle, raw)
            request_monitor.framing(handle, length, raw, extra, read_error)
            if len(raw) != length:
                raise ValueError('incomplete body')
            state = parse_request_json(raw)
            if scene_command:
                if type(state) is not dict or set(state) != {'recall'} or state['recall'] is not True:
                    raise ValueError('expected scene recall')
            else:
                state_payload(state)
        except (ValueError, OSError):
            self.send_json(400, {'status': 'error', 'error': 'invalid_state'})
            return
        request_monitor.update(getattr(self,'monitor_handle',None),values=state)
        if ('kelvin' in state or 'loxone_lumitech' in state) and os.environ.get('HUE_WHITE_ENABLED') != '1':
            self.send_json(403, {'status': 'error', 'error': 'white_disabled'})
            return
        rgb_command = ('rgb' in state or 'loxone_rgb' in state or
                       ('loxone_lumitech' in state and 0 < state['loxone_lumitech'] < 200000000))
        if rgb_command and os.environ.get('HUE_COLOR_ENABLED') != '1':
            self.send_json(403, {'status': 'error', 'error': 'color_disabled'})
            return
        try:
            if scene_command:
                result = scenes.recall(*target)
                dashboard.invalidate()
            elif target is None:
                result = write_state(state)
            else:
                result = write_state(state, bridge=target[0], light_id=target[1]['id'])
        except Exception as error:
            print('Hue command failed: ' + type(error).__name__, flush=True)
            self.send_json(502, {'status': 'error', 'error': 'bridge_command_failed'})
            return
        self.send_json(200, result)

    def admin_origin(self):
        expected = loxone_export.public_url()
        authority = urlsplit(expected).netloc
        origin = self.headers.get('Origin')
        return (self.headers.get('Host') == authority and
                (origin is None or origin == expected) and
                self.headers.get('Sec-Fetch-Site', 'same-origin') in ('same-origin', 'none'))

    def require_admin(self, csrf=False):
        try:
            valid_origin = self.admin_origin()
        except ValueError:
            valid_origin = False
        if not valid_origin:
            self.send_json(403, {'status':'error', 'error':'invalid_origin'})
            return None
        key, entry = admin_auth.session(self.headers.get('Cookie'))
        if not entry:
            self.send_json(401, {'status':'error', 'error':'login_required'})
            return None
        if csrf and not hmac.compare_digest(self.headers.get('X-CSRF-Token',''), entry['csrf']):
            self.send_json(403, {'status':'error', 'error':'invalid_csrf'})
            return None
        self.session_key = key
        return entry

    def read_admin_json(self):
        if self.headers.get('Transfer-Encoding') is not None or len(self.headers.get_all('Content-Length', [])) != 1:
            raise ValueError('invalid length')
        length = int(self.headers.get('Content-Length','0'))
        if not 0 < length <= 65536 or self.headers.get_content_type() != 'application/json':
            raise ValueError('invalid JSON request')
        raw = self.read_body(length)
        result = parse_request_json(raw)
        if type(result) is not dict:
            raise ValueError('expected object')
        return result

    def do_POST(self):
        if request_monitor.control_path(self.path):
            self.wrong_control_method()
            return
        self.close_connection = True
        paths = {'/api/admin/monitor/start', '/api/admin/monitor/stop', '/api/admin/monitor/clear', '/api/admin/discovery', '/api/admin/miniserver', '/api/admin/scenes/ignore', '/api/admin/scenes/remove', '/api/admin/scenes/export', '/api/admin/lights/icon', '/api/admin/lights/usage', '/api/admin/lights/ignore', '/api/admin/lights/remove', '/api/admin/login', '/api/admin/logout', '/api/admin/password', '/api/admin/token', '/api/admin/export', '/api/admin/bridges/add', '/api/admin/bridges/pair', '/api/admin/bridges/scan'}
        if self.path not in paths:
            self.send_error(404)
            return
        try:
            if not self.admin_origin():
                self.send_json(403, {'status':'error', 'error':'invalid_origin'})
                return
            if self.path == '/api/admin/login':
                body = self.read_admin_json()
                username, password = body.get('username'), body.get('password')
                if type(username) is not str or type(password) is not str or not 1 <= len(username) <= 64 or not 1 <= len(password) <= 256:
                    raise ValueError('invalid credentials')
                token, entry = admin_auth.login(username, password, self.client_address[0])
                if not entry:
                    code = 429 if token == 'limited' else 503 if token == 'unconfigured' else 401
                    self.send_json(code, {'status':'error', 'error': 'login_' + token})
                    return
                # Rotate any previous session on successful login.
                old_key, _ = admin_auth.session(self.headers.get('Cookie'), touch=False)
                if old_key:
                    admin_auth.logout(old_key)
                self.response_cookie = admin_auth.session_cookie(token, 43200)
                self.send_json(200, {'status':'ok', 'username':entry['username'], 'csrf':entry['csrf']})
                return
            entry = self.require_admin(csrf=True)
            if not entry:
                return
            body = self.read_admin_json()
            if self.path.startswith('/api/admin/monitor/'):
                action=self.path.rsplit('/',1)[1]
                result={'start':request_monitor.start,'stop':request_monitor.stop,'clear':request_monitor.clear}[action]()
                self.send_json(200, {'status':'ok', **result})
            elif self.path == '/api/admin/discovery':
                self.send_json(200, {'status':'ok', **discovery.search(body.get('kind'))})
            elif self.path == '/api/admin/miniserver':
                result=discovery.save_miniserver(body.get('name'),body.get('url'))
                dashboard.invalidate()
                self.send_json(200, {'status':'ok','miniserver':result})
            elif self.path in ('/api/admin/scenes/ignore','/api/admin/scenes/remove'):
                result = bridge_admin.manage_scene(body.get('bridge_id'),body.get('scene_id'),self.path.rsplit('/',1)[1],body.get('ignored',True))
                self.send_json(200, {'status':'ok', **result})
            elif self.path == '/api/admin/lights/icon':
                lamp_types.save_icon(body.get('bridge_id'),body.get('light_id'),body.get('icon'))
                dashboard.invalidate()
                self.send_json(200, {'status':'ok'})
            elif self.path == '/api/admin/lights/usage':
                lamp_types.save_modes(body.get('bridge_id'),body.get('light_id'),body.get('modes'))
                dashboard.invalidate()
                self.send_json(200, {'status':'ok'})
            elif self.path.startswith('/api/admin/lights/'):
                result = bridge_admin.manage_light(body.get('bridge_id'), body.get('light_id'), self.path.rsplit('/',1)[1], body.get('ignored',True))
                dashboard.invalidate()
                self.send_json(200, {'status':'ok', **result})
            elif self.path.startswith('/api/admin/bridges/'):
                if self.path.endswith('/add'):
                    result = {'bridge':bridge_admin.add_bridge(body.get('name'), body.get('host'))}
                elif self.path.endswith('/pair'):
                    result = bridge_admin.pair_bridge(body.get('id'), replace=body.get('replace',False))
                else:
                    result = {'bridge':bridge_admin.scan_bridge(body.get('id'))}
                dashboard.invalidate()
                self.send_json(200, {'status':'ok', **result})
            elif self.path == '/api/admin/password':
                current, new = body.get('current_password'), body.get('new_password')
                if type(current) is not str or type(new) is not str or not 1 <= len(current) <= 256 or not 5 <= len(new) <= 256:
                    raise ValueError('invalid password')
                result = admin_auth.change_password(entry['username'], current, new, self.client_address[0])
                if result != 'ok':
                    status = 429 if result == 'limited' else 403 if result == 'invalid' else 503
                    self.send_json(status, {'status':'error', 'error':'password_' + result})
                    return
                self.response_cookie = admin_auth.session_cookie('', 0)
                self.send_json(200, {'status':'ok'})
            elif self.path == '/api/admin/logout':
                admin_auth.logout(self.session_key)
                self.response_cookie = admin_auth.session_cookie('', 0)
                self.send_json(200, {'status':'ok'})
            elif self.path == '/api/admin/token':
                self.send_json(200, {'status':'ok', 'token':admin_auth.control_token()})
            elif self.path in ('/api/admin/export','/api/admin/scenes/export'):
                include = body.get('include_token', False)
                if type(include) is not bool:
                    raise ValueError('invalid option')
                token = admin_auth.control_token() if include else None
                xml = loxone_export.export_xml(body.get('scenes'), include, token, kind='scenes', language=body.get('language','de')) if self.path == '/api/admin/scenes/export' else loxone_export.export_xml(body.get('lights'), include, token, variants=body.get('variants'), language=body.get('language','de'))
                self.send_response(200)
                self.send_header('Content-Type','application/xml; charset=utf-8')
                self.send_header('Content-Disposition','attachment; filename="Hue2Lox-Loxone.xml"')
                self.send_header('Content-Length',str(len(xml)))
                self.security_headers()
                self.end_headers()
                self.wfile.write(xml)
        except bridge_admin.BridgeError as error:
            self.send_json(error.status, {'status':'error', 'error':error.code})
        except BridgeRequestError:
            self.send_json(502, {'status':'error', 'error':'bridge_unreachable'})
        except (ValueError, TypeError):
            self.send_json(400, {'status':'error', 'error':'invalid_request'})
        except (OSError, KeyError):
            self.send_json(503, {'status':'error', 'error':'configuration_unavailable'})

    def security_headers(self):
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Pragma', 'no-cache')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Referrer-Policy', 'no-referrer')
        self.send_header('X-Frame-Options', 'DENY')
        if getattr(self, 'response_cookie', None):
            self.send_header('Set-Cookie', self.response_cookie)

    def send_response(self, code, message=None):
        request_monitor.update(getattr(self,'monitor_handle',None),status=code,reason=getattr(self,'monitor_reason',None))
        super().send_response(code,message)

    def do_PATCH(self):
        self.wrong_control_method()

    def do_DELETE(self):
        self.wrong_control_method()

    def do_HEAD(self):
        self.wrong_control_method()

    def send_json(self, status, result):
        self.monitor_reason=result.get('error')
        body = json.dumps(result, separators=(',', ':')).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.security_headers()
        self.end_headers()
        self.wfile.write(body)


def tls_context(environ):
    """HTTPS context when TLS_CERT and TLS_KEY are both set, None (plain HTTP) when both are absent."""
    cert, key = environ.get('TLS_CERT'), environ.get('TLS_KEY')
    if cert is None and key is None:
        return None
    if not cert or not key:
        raise ValueError('TLS_CERT and TLS_KEY must both be set and non-empty for HTTPS; '
                         'unset both to serve plain HTTP behind a reverse proxy.')
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    context.load_cert_chain(cert, key)
    return context


if __name__ == '__main__':
    try:
        context = tls_context(os.environ)
    except ValueError as error:
        raise SystemExit('Hue2Lox: ' + str(error))
    server = BoundedHTTPSServer((os.environ.get('BIND_HOST', '0.0.0.0'),
                                int(os.environ.get('PORT', '8443'))), Handler, context)
    print('Hue2Lox ' + ('HTTPS' if context else 'HTTP') + ' service ready', flush=True)
    server.serve_forever()
