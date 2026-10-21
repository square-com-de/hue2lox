#!/usr/bin/env python3
"""Exercise an actual native package over loopback HTTPS; no systemd or hardware."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import socket
import ssl
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parent.parent
# Applied here and in the application subprocess. Parent PYTHONPATH/audit setup
# stays inherited; this guard adds a hard restriction to IPv4 loopback traffic.
GUARD = '''
def loopback_only(event, args):
    if event in ('socket.connect', 'socket.sendto'):
        address = args[-1]
        if not isinstance(address, tuple) or address[0] != '127.0.0.1':
            raise PermissionError('Native smoke permits IPv4 loopback only')
sys.addaudithook(loopback_only)
'''
exec(GUARD)


def load_manager():
    spec = importlib.util.spec_from_file_location('native_smoke_manager', ROOT / 'deployment/native/manage.py')
    manager = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = manager  # dataclasses resolves its defining module
    spec.loader.exec_module(manager)
    return manager


def main():
    with tempfile.TemporaryDirectory(prefix='hue2lox-native-smoke-') as temporary:
        root = Path(temporary)
        subprocess.run([sys.executable, str(ROOT / 'scripts/build-native-package.py'),
                        '--version', '0.0.0-smoke', '--output', str(root / 'packages')],
                       check=True, stdout=subprocess.DEVNULL)
        package = root / 'packages/hue2lox-0.0.0-smoke-native.tar.gz'
        runtime = root / 'runtime'
        manager = load_manager()
        manager.verify_package(package, hashlib.sha256(package.read_bytes()).hexdigest(), runtime)
        manager.validate_runtime(runtime)
        private = root / 'private'
        private.mkdir()
        state, certs, secrets = (private / name for name in ('state', 'certs', 'secrets'))
        subprocess.run([sys.executable, str(runtime / 'scripts/prepare-state.py'),
                        '--state-directory', str(state), '--certificate-directory', str(certs),
                        '--secret-directory', str(secrets), '--host', '127.0.0.1'],
                       check=True, stdout=subprocess.DEVNULL)
        with socket.socket() as probe:
            probe.bind(('127.0.0.1', 0))
            port = probe.getsockname()[1]
        base = f'https://127.0.0.1:{port}'
        env = dict(os.environ, BIND_HOST='127.0.0.1', PORT=str(port),
                   TLS_CERT=str(certs / 'server.crt'), TLS_KEY=str(certs / 'server.key'),
                   HUE_STATE_DIR=str(state), HUE_REGISTRY_FILE=str(state / 'registry.json'),
                   HUE_ADMIN_AUTH_FILE=str(state / 'admin_auth.json'),
                   HUE_CONTROL_TOKEN_FILE=str(secrets / 'control_token'), HUE_PUBLIC_URL=base,
                   HUE_CA_FILE=str(runtime / 'trust/huebridge-ca.pem'), HUE_LEGACY_ENABLED='0',
                   HUE_WRITES_ENABLED='0', HUE_COLOR_ENABLED='0', HUE_WHITE_ENABLED='0',
                   PYTHONDONTWRITEBYTECODE='1')
        context = ssl.create_default_context(cafile=str(certs / 'server.crt'))
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}),
                                             urllib.request.HTTPSHandler(context=context))

        def request(path, body=None, headers=None):
            headers = dict(headers or {})
            if body is not None:
                headers['Content-Type'] = 'application/json'
            req = urllib.request.Request(base + path, data=json.dumps(body).encode() if body is not None else None, headers=headers)
            try:
                with opener.open(req, timeout=2) as response:
                    return response.status, response.headers, response.read()
            except urllib.error.HTTPError as response:
                return response.code, response.headers, response.read()

        def login(password):
            code, headers, body = request('/api/admin/login', {'username': 'admin', 'password': password})
            assert code == 200
            return {'Cookie': headers['Set-Cookie'].split(';')[0],
                    'X-CSRF-Token': json.loads(body)['csrf'], 'Origin': base}

        def snapshot():
            return {str(path.relative_to(private)): path.read_bytes() for path in private.rglob('*') if path.is_file()}

        new_password = 'native-smoke-local-test-password'
        expected = None
        previous_auth = None
        for iteration in range(2):
            launcher = 'import sys, runpy\n' + GUARD + '\nrunpy.run_path("app.py", run_name="__main__")\n'
            proc = subprocess.Popen([sys.executable, '-B', '-c', launcher], cwd=runtime / 'src', env=env,
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            try:
                for _ in range(80):
                    try:
                        if request('/health')[0] == 200:
                            break
                    except (OSError, urllib.error.URLError):
                        pass
                    if proc.poll() is not None:
                        raise AssertionError('Packaged native application exited')
                    time.sleep(.1)
                else:
                    raise AssertionError('Packaged native application failed HTTPS healthcheck')
                assert request('/api/admin/lights')[0] == 401
                assert request('/hue-go/status')[0] == 404
                if previous_auth is not None:
                    assert request('/api/overview', headers=previous_auth)[0] == 401
                auth = login('admin' if iteration == 0 else new_password)
                if iteration == 0:
                    assert request('/api/admin/password', {'current_password': 'admin', 'new_password': new_password}, auth)[0] == 200
                    assert request('/api/overview', headers=auth)[0] == 401
                    auth = login(new_password)
                    expected = snapshot()
                code, _, body = request('/api/overview', headers=auth)
                assert code == 200 and json.loads(body)['bridges'] == []
                for path in ('/', '/assets/i18n.js', '/assets/locales/de.js', '/assets/locales/en.js', '/assets/discovery-help.js', '/tutorial/en', '/licenses'):
                    assert request(path)[0] == 200, path
                assert request('/assets/discovery-help.js')[2] == (runtime / 'web/discovery-help.js').read_bytes()
                assert b'discovery-help-platforms' in request('/')[2]
                assert request('/api/admin/token', {}, {'Cookie': auth['Cookie']})[0] == 403
                code, _, body = request('/api/admin/token', {}, auth)
                assert code == 200 and json.loads(body)['token'].encode() == (secrets / 'control_token').read_bytes().strip()
                assert snapshot() == expected
                previous_auth = auth
            finally:
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait()
        print('PASS: actual native package, verified loopback HTTPS, login/password change, session invalidation, CSRF, empty overview, DE/EN assets and process restart with private state retained. No systemd or hardware qualification.')


if __name__ == '__main__':
    main()
