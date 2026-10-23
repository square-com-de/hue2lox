"""Verify a disposable CI container without printing credentials or responses."""
import json
from pathlib import Path
import ssl
import sys
import urllib.error
import urllib.request

root = Path(sys.argv[1])
env = dict(line.split('=', 1) for line in (root / '.env').read_text().splitlines() if '=' in line and not line.startswith('#'))
public = env['HUE_PUBLIC_URL']
base = env.get('HUE2LOX_SCHEME', 'https') + '://' + env['HUE2LOX_BIND_IP'] + ':' + env['HUE2LOX_PORT']
context = ssl.create_default_context(cafile=str(root / 'health-test.crt')) if base.startswith('https:') else None
def request(path, body=None, headers=None):
    headers = dict(headers or {})
    headers.setdefault('Host', urllib.parse.urlsplit(public).netloc)
    if body is not None:
        headers['Content-Type'] = 'application/json'
    req = urllib.request.Request(base + path, data=json.dumps(body).encode() if body is not None else None, headers=headers)
    try:
        with urllib.request.urlopen(req, context=context, timeout=5) as response:
            return response.status, response.headers, response.read()
    except urllib.error.HTTPError as response:
        return response.code, response.headers, response.read()
assert request('/health')[0] == 200
assert request('/api/admin/lights')[0] == 401
code, headers, body = request('/api/admin/login', {'username': 'admin', 'password': 'admin'})
assert code == 200
assert ('; Secure' in headers['Set-Cookie']) == public.startswith('https:')
cookie = headers['Set-Cookie'].split(';')[0]
auth = {'Cookie': cookie, 'X-CSRF-Token': json.loads(body)['csrf'], 'Origin': public}
code, _, body = request('/api/overview', headers=auth)
assert code == 200 and json.loads(body)['bridges'] == []
assert json.loads(body)['features'] == {'control': True, 'rgb': True, 'white': True}
assert request('/api/admin/token', {}, {'Cookie': cookie})[0] == 403
code, _, body = request('/api/admin/token', {}, auth)
assert code == 200
assert json.loads(body)['token'] == (root / 'secrets/control_token').read_text().strip()
for path in ('/', '/assets/locales/en.js', '/assets/discovery-help.js', '/assets/sidebar-icons.svg', '/assets/sidebar-icons-license.txt', '/tutorial/en', '/licenses'):
    assert request(path)[0] == 200
assert request('/assets/discovery-help.js')[2] == (root / 'web/discovery-help.js').read_bytes()
assert b'discovery-help-platforms' in request('/')[2]
assert request('/assets/sidebar-icons.svg')[2] == (root / 'web/sidebar-icons.svg').read_bytes()
assert request('/assets/sidebar-icons-license.txt')[2] == (root / 'web/sidebar-icons-LICENSE.txt').read_bytes()
print('PASS: CI HTTP(S)/API checks; no bridge configured and no secrets printed.')
