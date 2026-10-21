#!/usr/bin/env python3
"""Destructive native lifecycle checks ONLY inside ci-native.sh's empty OS container."""
import hashlib
import io
import json
import os
from pathlib import Path
import ssl
import subprocess
import tarfile
import urllib.error
import urllib.request

assert os.environ.get('CI') == 'true' and Path('/run/systemd/system').is_dir()
assert Path('/.dockerenv').exists(), 'Disposable test container required'
assert not Path('/etc/hue2lox').exists(), 'Refuse an existing installation'


def run(*args, success=True):
    result = subprocess.run(args, check=False)
    assert (result.returncode == 0) == success, f'Unexpected exit status: {args[0]}'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


packages = sorted(Path('/packages').glob('*.tar.gz'))
assert len(packages) == 2
installer = '/source/deployment/native/install.sh'
updater = '/source/deployment/native/update.sh'
uninstaller = '/source/deployment/native/uninstall.sh'
run('sh', installer, '--package', str(packages[0]), '--sha256', digest(packages[0]), '--host', '127.0.0.1', '--port', '18443')
settings = dict(line.split('=', 1) for line in Path('/etc/hue2lox/settings.env').read_text().splitlines() if line and not line.startswith('#') and '=' in line)
base = settings['HUE_PUBLIC_URL']
cert = Path(settings['TLS_CERT'])
context = ssl.create_default_context(cafile=str(cert))


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


def check_login(password):
    assert request('/health')[0] == 200
    assert request('/api/admin/lights')[0] == 401
    code, headers, body = request('/api/admin/login', {'username': 'admin', 'password': password})
    assert code == 200
    auth = {'Cookie': headers['Set-Cookie'].split(';')[0], 'X-CSRF-Token': json.loads(body)['csrf'], 'Origin': base}
    code, _, body = request('/api/overview', headers=auth)
    assert code == 200 and json.loads(body)['bridges'] == []
    assert request('/api/admin/token', {}, {'Cookie': auth['Cookie']})[0] == 403
    for path in ('/', '/assets/locales/en.js', '/tutorial/en', '/licenses'):
        assert request(path)[0] == 200
    return auth


auth = check_login('admin')
password = 'native-ci-local-test-password'
assert request('/api/admin/password', {'current_password': 'admin', 'new_password': password}, auth)[0] == 200
check_login(password)
# Every private persistent file is preserved across restart/update and rollback.
def snapshot():
    return {str(p): digest(p) for directory in ('/etc/hue2lox', '/var/lib/hue2lox') for p in Path(directory).rglob('*') if p.is_file() and p.name != 'install.json'}

before = snapshot()
run('systemctl', 'restart', 'hue2lox.service')
# systemctl's start completion need not mean the HTTPS listener is ready.
import time
for attempt in range(40):
    try:
        check_login(password)
        break
    except (OSError, AssertionError):
        time.sleep(0.25)
else:
    raise AssertionError('HTTPS did not recover after restart')
assert snapshot() == before
run('sh', installer, '--package', str(packages[0]), '--sha256', digest(packages[0]), '--host', '127.0.0.1', '--port', '18443', success=False)
assert snapshot() == before
# Simulate disabled startup after an initial installation failure.
run('systemctl', 'disable', 'hue2lox.service')
run('sh', updater, '--package', str(packages[1]), '--sha256', digest(packages[1]))
check_login(password)
assert snapshot() == before
run('systemctl', 'is-enabled', 'hue2lox.service')
# Late rollback must restore code and matching state after a successful update.
late_backup = next(Path('/var/backups/hue2lox').iterdir())
run('sh', '/source/deployment/native/rollback.sh', '--backup', str(late_backup))
check_login(password)
assert snapshot() == before
assert json.loads(Path('/etc/hue2lox/install.json').read_text())['version'] == '0.0.0-ci.1'
run('sh', updater, '--package', str(packages[1]), '--sha256', digest(packages[1]))
active = Path('/opt/hue2lox/current').resolve()
uid = subprocess.check_output(['systemctl', 'show', 'hue2lox.service', '-p', 'User', '--value'], text=True).strip()
assert uid and uid != 'root'
run('runuser', '-u', uid, '--', 'test', '!', '-w', str(active / 'src/app.py'))
for path in Path('/etc/hue2lox').rglob('*'):
    if path.is_file():
        assert path.stat().st_uid == 0 and not path.stat().st_mode & 0o027, 'Private configuration must be root-owned without group write or world access'
run('runuser', '-u', uid, '--', 'test', '-r', settings['TLS_KEY'])
run('runuser', '-u', uid, '--', 'test', '!', '-w', settings['TLS_KEY'])
for path in Path('/var/lib/hue2lox').rglob('*'):
    if path.is_file():
        assert not path.stat().st_mode & 0o007, 'Private state is world-accessible'
# A validly hashed package whose application cannot start must roll back.
with tarfile.open(packages[1]) as source:
    content = {m.name: source.extractfile(m).read() for m in source.getmembers() if m.isfile()}
manifest_key = 'hue2lox-native/manifest.json'
manifest = json.loads(content[manifest_key])
manifest['version'] = '0.0.0-ci.broken'
content['hue2lox-native/src/app.py'] = b'if __name__ == "__main__":\n    raise RuntimeError("CI deliberate startup failure")\n'
manifest['files']['src/app.py'] = hashlib.sha256(content['hue2lox-native/src/app.py']).hexdigest()
content[manifest_key] = json.dumps(manifest).encode()
broken = Path('/tmp/broken.tar.gz')
with tarfile.open(broken, 'w:gz') as target:
    for name, data in content.items():
        info = tarfile.TarInfo(name)
        info.size = len(data)
        info.mode = 0o644
        target.addfile(info, io.BytesIO(data))
backups_before = set(Path('/var/backups/hue2lox').iterdir())
run('sh', updater, '--package', str(broken), '--sha256', digest(broken), success=False)
assert set(Path('/var/backups/hue2lox').iterdir()) > backups_before, 'Candidate must reach activation and exercise rollback'
assert Path('/opt/hue2lox/current').resolve() == active
assert snapshot() == before
check_login(password)
# A rejected uninstall must leave the enabled, working service untouched.
alias = active / 'rejected-alias'
alias.symlink_to('/tmp/unrelated')
run('sh', uninstaller, success=False)
run('systemctl', 'is-active', 'hue2lox.service')
run('systemctl', 'is-enabled', 'hue2lox.service')
alias.unlink()
check_login(password)
run('sh', uninstaller)
assert snapshot() == before
assert not Path('/etc/systemd/system/hue2lox.service').exists()
assert Path('/var/backups/hue2lox').is_dir()
# Explicit reinstall of retained data must preserve changed credentials and flags.
# Reproduce a root shell that retained umask 077 after preparing a private backup.
previous_umask = os.umask(0o077)
try:
    run('sh', installer, '--keep-data', '--package', str(packages[1]), '--sha256', digest(packages[1]), '--host', '127.0.0.1', '--port', '18443')
finally:
    os.umask(previous_umask)
for directory in ('/opt/hue2lox', '/opt/hue2lox/releases'):
    assert Path(directory).stat().st_mode & 0o777 == 0o755
run('runuser', '-u', uid, '--', 'test', '-x', '/opt/hue2lox/current/src')
check_login(password)
assert snapshot() == before
run('systemctl', 'is-enabled', 'hue2lox.service')
run('sh', uninstaller)
run('sh', uninstaller, '--purge-data')
assert not Path('/etc/hue2lox').exists() and not Path('/var/lib/hue2lox').exists()
assert Path('/var/backups/hue2lox').is_dir(), 'Backups require a separate deliberate cleanup'
print('PASS: native install, verified HTTPS/login/CSRF, changed password retention, non-root rights, restart, update, failed-start rollback and preserving uninstall.')
