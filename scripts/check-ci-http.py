"""Verify a disposable CI container without printing credentials or responses."""
import json
from pathlib import Path
import ssl
import sys
import urllib.error
import urllib.request

root = Path(sys.argv[1])
env = dict(line.split('=', 1) for line in (root / '.env').read_text().splitlines() if '=' in line and not line.startswith('#'))
base = env['HUE_PUBLIC_URL']
context = ssl.create_default_context(cafile=str(root / 'health-test.crt'))
def request(path, body=None, headers=None):
    headers = dict(headers or {})
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
cookie = headers['Set-Cookie'].split(';')[0]
auth = {'Cookie': cookie, 'X-CSRF-Token': json.loads(body)['csrf'], 'Origin': base}
code, _, body = request('/api/overview', headers=auth)
assert code == 200 and json.loads(body)['bridges'] == []
assert request('/api/admin/token', {}, {'Cookie': cookie})[0] == 403
code, _, body = request('/api/admin/token', {}, auth)
assert code == 200
assert json.loads(body)['token'] == (root / 'secrets/control_token').read_text().strip()
for path in ('/', '/assets/locales/en.js', '/tutorial/en', '/licenses'):
    assert request(path)[0] == 200
print('PASS: CI HTTPS/API checks; no bridge configured and no secrets printed.')
