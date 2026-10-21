"""Container entrypoint: create missing first-run app state under /data, then start the app.

Existing files are never overwritten, so upgrading the image keeps credentials,
the control token and the bridge registry. The app serves plain HTTP unless
TLS_CERT and TLS_KEY are set; TLS is otherwise the job of a reverse proxy.
"""
import json
import os
from pathlib import Path
import secrets
import sys

sys.path.insert(0, '/app/src')
import admin_auth

STATE = Path(os.environ.setdefault('HUE_STATE_DIR', '/data'))
SECRETS = STATE / 'secrets'
os.environ.setdefault('HUE_REGISTRY_FILE', str(STATE / 'registry.json'))
os.environ.setdefault('HUE_ADMIN_AUTH_FILE', str(STATE / 'admin_auth.json'))
os.environ.setdefault('HUE_CONTROL_TOKEN_FILE', str(SECRETS / 'control_token'))
# Lamp control is on by default in the image; set any of these to 0 for read-only.
for flag in ('HUE_WRITES_ENABLED', 'HUE_COLOR_ENABLED', 'HUE_WHITE_ENABLED'):
    os.environ.setdefault(flag, '1')


def write_private(path, text, mode=0o600):
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, mode)
    with os.fdopen(descriptor, 'w') as handle:
        handle.write(text)


def ensure_state():
    registry = Path(os.environ['HUE_REGISTRY_FILE'])
    if not registry.exists():
        write_private(registry, json.dumps({'schema_version': 1, 'bridges': []}))
    auth = Path(os.environ['HUE_ADMIN_AUTH_FILE'])
    if not auth.exists():
        password = os.environ.get('HUE2LOX_ADMIN_PASSWORD', 'admin')
        write_private(auth, json.dumps(admin_auth.create_credentials('admin', password)))
        if password == 'admin':
            print('Initial login is admin/admin: change the password in the web interface.', flush=True)
    token = Path(os.environ['HUE_CONTROL_TOKEN_FILE'])
    if not token.exists():
        write_private(token, secrets.token_hex(32) + '\n', 0o600)


def require_writable_state():
    if not os.access(STATE, os.W_OK):
        sys.exit('Hue2Lox: %s is not writable by UID %d. Use a named volume, or for a host folder run '
                 '"chown %d:%d <folder>" before starting.' % (STATE, os.getuid(), os.getuid(), os.getgid()))


if __name__ == '__main__':
    require_writable_state()
    ensure_state()
    os.chdir('/app/src')
    os.execvp('python', ['python', '-u', 'app.py'])
