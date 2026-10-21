"""Fresh private state for deployment adapters; no Docker, systemd or network calls."""
import ipaddress
import json
import os
from pathlib import Path
import secrets
import shutil
import subprocess
import tempfile

from admin_auth import create_credentials


def local_address(host):
    address = ipaddress.IPv4Address(host)
    if address.is_unspecified or address.is_multicast or not (address.is_private or address.is_loopback):
        raise ValueError('Use a local unicast IPv4 address')
    return str(address)


def initialize(state_directory, certificate_directory, secret_directory, host, uid=None, gid=None):
    """Create NEW private directories; certificate_directory=None skips TLS; caller selects ownership explicitly.

    Existing state is never initialized/reset. This function is usable by Docker,
    native and future plugin adapters, without installing services or packages.
    """
    host = local_address(host)
    state, secrets_dir = Path(state_directory), Path(secret_directory)
    certs = Path(certificate_directory) if certificate_directory is not None else None
    targets = [state, secrets_dir] + ([certs] if certs is not None else [])
    if len({str(p.absolute()) for p in targets}) != len(targets):
        raise ValueError('State, certificates and secrets need separate directories')
    if (uid is None) != (gid is None):
        raise ValueError('Specify both uid and gid, or neither')
    for path in targets:
        if path.exists() or path.is_symlink() or not path.parent.is_dir():
            raise ValueError('Private directory already exists or parent is missing')
    created = []
    try:
        for path in targets:
            path.mkdir(mode=0o700)
            created.append(path)
        for name, document in [('registry.json', {'schema_version': 1, 'bridges': []}),
                               ('admin_auth.json', create_credentials('admin', 'admin'))]:
            path = state / name
            path.write_text(json.dumps(document))
            path.chmod(0o600)
        token = secrets_dir / 'control_token'
        token.write_text(secrets.token_hex(32) + '\n')
        token.chmod(0o400)
        if certs is not None:
            # OpenSSL must never briefly create a world-readable private key.
            with tempfile.TemporaryDirectory(prefix='.certificate-', dir=certs) as directory:
                tmp = Path(directory)
                san = ','.join(dict.fromkeys([f'IP:{host}', 'IP:127.0.0.1', 'DNS:localhost']))
                subprocess.run(['openssl', 'req', '-x509', '-newkey', 'rsa:2048', '-sha256', '-nodes',
                                '-days', '365', '-keyout', str(tmp / 'server.key'),
                                '-out', str(tmp / 'server.crt'), '-subj', '/CN=hue2lox.local',
                                '-addext', 'subjectAltName=' + san, '-addext', 'extendedKeyUsage=serverAuth'],
                               check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                (tmp / 'server.key').chmod(0o600)
                (tmp / 'server.key').replace(certs / 'server.key')
                (tmp / 'server.crt').replace(certs / 'server.crt')
            (certs / 'server.crt').chmod(0o644)
        if uid is not None:
            for directory in targets:
                os.chown(directory, uid, gid)
                for path in directory.iterdir():
                    os.chown(path, uid, gid)
    except BaseException:
        for path in reversed(created):
            shutil.rmtree(path)
        raise
