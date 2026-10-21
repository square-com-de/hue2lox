"""Local administrator credentials; opaque, expiring in-memory sessions."""
import base64
import hashlib
import hmac
import json
import os
from pathlib import Path
import secrets
import threading
import time
import tempfile



def secure_cookies():
    """Secure cookies need an HTTPS public URL (built-in TLS or a reverse proxy); plain HTTP gets plain cookies."""
    return os.environ.get('HUE_PUBLIC_URL', 'https://').lower().startswith('https://')


def cookie_name():
    # Browsers only accept the __Host- prefix together with Secure.
    return '__Host-hue2lox_session' if secure_cookies() else 'hue2lox_session'


def session_cookie(value, max_age):
    return cookie_name() + '=' + value + '; Path=/; HttpOnly' + ('; Secure' if secure_cookies() else '') + '; SameSite=Strict; Max-Age=' + str(max_age)
LOCK = threading.Lock()
CREDENTIAL_LOCK = threading.RLock()
SESSIONS = {}
ATTEMPTS = {}
IDLE = 1800
LIFETIME = 43200


def credential_path():
    return Path(os.environ.get('HUE_ADMIN_AUTH_FILE', '/data/admin_auth.json'))


def create_credentials(username, password):
    if type(username) is not str or not username or len(username) > 64 or type(password) is not str or not 5 <= len(password) <= 256:
        raise ValueError('Use a username and a password of 5–256 characters')
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 600000, dklen=32)
    return {'version': 1, 'algorithm': 'pbkdf2-sha256-600000', 'username': username, 'salt': base64.b64encode(salt).decode(),
            'hash': base64.b64encode(digest).decode()}


def configured():
    return credential_path().is_file()


def credential_revision():
    """Bind sessions to the saved credentials, including external CLI resets."""
    return hashlib.sha256(credential_path().read_bytes()).hexdigest()


def verify_password(username, password):
    data = json.loads(credential_path().read_text())
    salt = base64.b64decode(data['salt'], validate=True)
    expected = base64.b64decode(data['hash'], validate=True)
    actual = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 600000, dklen=32)
    return (data['version'] == 1 and data['algorithm'] == 'pbkdf2-sha256-600000' and
            hmac.compare_digest(actual, expected) and
            hmac.compare_digest(username.encode(), data['username'].encode()))


def rate_limited(address):
    now = time.monotonic()
    with LOCK:
        for key in list(ATTEMPTS):
            if now - ATTEMPTS[key]['start'] > 300:
                del ATTEMPTS[key]
        if address not in ATTEMPTS and len(ATTEMPTS) >= 100:
            return True
        record = ATTEMPTS.setdefault(address, {'start': now, 'count': 0})
        if record['count'] >= 5 or sum(v['count'] for v in ATTEMPTS.values()) >= 100:
            return True
        record['count'] += 1
    return False


def login(username, password, address):
    with CREDENTIAL_LOCK:
        return _login(username, password, address)


def _login(username, password, address):
    if rate_limited(address):
        return 'limited', None
    try:
        revision = credential_revision()
        valid = verify_password(username, password)
    except (OSError, ValueError, KeyError, TypeError):
        return 'unconfigured', None
    if not valid:
        return 'invalid', None
    now = time.monotonic()
    token = secrets.token_urlsafe(32)
    entry = {'created': now, 'seen': now, 'csrf': secrets.token_urlsafe(32), 'username': username,
             'credential_revision': revision}
    with LOCK:
        ATTEMPTS.pop(address, None)
        _prune(now)
        if len(SESSIONS) >= 100:
            SESSIONS.pop(next(iter(SESSIONS)))
        SESSIONS[hashlib.sha256(token.encode()).hexdigest()] = entry
    return token, dict(entry)


def _prune(now):
    for key, entry in list(SESSIONS.items()):
        if now - entry['seen'] >= IDLE or now - entry['created'] >= LIFETIME:
            del SESSIONS[key]


def session(cookie, touch=True):
    from http.cookies import SimpleCookie, CookieError
    try:
        parsed = SimpleCookie(); parsed.load(cookie or '')
        token = parsed[cookie_name()].value
        if len(token) > 128:
            return None, None
    except (KeyError, CookieError):
        return None, None
    key = hashlib.sha256(token.encode()).hexdigest()
    try:
        revision = credential_revision()
    except OSError:
        return None, None
    with LOCK:
        _prune(time.monotonic())
        entry = SESSIONS.get(key)
        if entry is None:
            return None, None
        if entry.get('credential_revision') != revision:
            del SESSIONS[key]
            return None, None
        if touch:
            entry['seen'] = time.monotonic()
        return key, dict(entry)


def logout(key):
    with LOCK:
        SESSIONS.pop(key, None)


def control_token():
    token = Path(os.environ.get('HUE_CONTROL_TOKEN_FILE', '/run/secrets/control_token')).read_text().strip()
    if not 32 <= len(token) <= 512 or not token.isascii() or any(ord(c) < 33 or ord(c) > 126 for c in token):
        raise ValueError('invalid control token')
    return token


def save_credentials(target, data):
    target = Path(target)
    target.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix='.' + target.name + '-', dir=str(target.parent))
    try:
        with os.fdopen(descriptor, 'w') as file:
            os.fchmod(file.fileno(), 0o600)
            if os.geteuid() == 0:
                os.fchown(file.fileno(), 10001, 10001)
            json.dump(data, file)
            file.flush()
            os.fsync(file.fileno())
        os.replace(temporary, target)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def change_password(username, current_password, new_password, address):
    if not 5 <= len(new_password) <= 256:
        raise ValueError('password length')
    with CREDENTIAL_LOCK:
        if rate_limited(address):
            return 'limited'
        try:
            valid = verify_password(username, current_password)
        except (OSError, ValueError, KeyError, TypeError):
            return 'unconfigured'
        if not valid:
            return 'invalid'
        save_credentials(credential_path(), create_credentials(username, new_password))
        with LOCK:
            SESSIONS.clear()
            ATTEMPTS.clear()
        return 'ok'


if __name__ == '__main__':
    import argparse
    import getpass
    parser = argparse.ArgumentParser(description='Create/reset local Hue2Lox administrator')
    parser.add_argument('file')
    parser.add_argument('--username', default='admin')
    parser.add_argument('--default', action='store_true', help='Explicitly set public default admin password: admin')
    args = parser.parse_args()
    if args.default:
        password = 'admin'
    else:
        password = getpass.getpass('Neues Admin-Passwort (mindestens 5 Zeichen): ')
        if password != getpass.getpass('Passwort wiederholen: '):
            raise SystemExit('Passwörter stimmen nicht überein')
    save_credentials(args.file, create_credentials(args.username, password))
    print('Administrator gespeichert. Bestehende Sitzungen sind nicht mehr gültig.')
