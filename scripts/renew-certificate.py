"""Offline certificate renewal for a stopped prepared installation; never runs Docker."""
import argparse
import errno
import ipaddress
import os
from pathlib import Path
import shutil
import socket
import ssl
import subprocess
import tempfile

FILES = ('.env', 'certs/server.crt', 'certs/server.key', 'health-test.crt')


def renew(destination, host=None):
    dest = Path(destination).resolve()
    for name in FILES + ('compose.yaml', 'data/registry.json', 'data/admin_auth.json', 'secrets/control_token'):
        path = dest / name
        if not path.is_file() or path.is_symlink():
            raise ValueError('Expected regular installation file: ' + name)
    for name in ('certs', 'data', 'secrets'):
        if (dest/name).is_symlink():
            raise ValueError('Symlinked installation directories are not supported')
    if 'HUE_LEGACY_ENABLED: "0"' not in (dest/'compose.yaml').read_text():
        raise ValueError('Only prepared fresh installations are supported')
    lines = (dest/'.env').read_text().splitlines()
    keys = [line.split('=', 1)[0] for line in lines if '=' in line and not line.lstrip().startswith('#')]
    if len(keys) != len(set(keys)):
        raise ValueError('Duplicate environment keys')
    env = dict(line.split('=', 1) for line in lines if '=' in line and not line.lstrip().startswith('#'))
    old = str(ipaddress.IPv4Address(env['HUE2LOX_BIND_IP']))
    address = ipaddress.IPv4Address(host or old)
    if address.is_unspecified or address.is_multicast or not (address.is_private or address.is_loopback):
        raise ValueError('Use a local unicast IPv4 address')
    port = int(env['HUE2LOX_PORT'])
    if not 1024 <= port <= 65535 or env['HUE_PUBLIC_URL'] != f'https://{old}:{port}':
        raise ValueError('Inconsistent installation URL or port')
    # Refuse a listener at either address. Keep reservations until replacements finish.
    # The operator must also stop restart supervisors during maintenance.
    sockets = []
    backup = None
    try:
        for ip in dict.fromkeys((old, str(address))):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sockets.append(sock)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.bind((ip, port))
                sock.listen(1)
            except OSError as error:
                # The previous address may already have been removed by the OS.
                if ip == old and ip != str(address) and error.errno == errno.EADDRNOTAVAIL:
                    continue
                raise
        backup = Path(tempfile.mkdtemp(prefix='.hue2lox-tls-backup-', dir=dest.parent))
        for name in FILES:
            target = backup/name
            target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            shutil.copy2(dest/name, target)
            if os.geteuid() == 0:
                stat = (dest/name).stat()
                os.chown(target, stat.st_uid, stat.st_gid)
        with tempfile.TemporaryDirectory(prefix='.tls-renew-', dir=dest) as temporary:
            work = Path(temporary)
            san = ','.join(dict.fromkeys((f'IP:{address}', 'IP:127.0.0.1', 'DNS:localhost')))
            subprocess.run(['openssl', 'req', '-x509', '-newkey', 'rsa:2048', '-sha256', '-nodes', '-days', '365',
                            '-keyout', str(work/'server.key'), '-out', str(work/'server.crt'),
                            '-subj', '/CN=hue2lox.local', '-addext', 'subjectAltName='+san,
                            '-addext', 'extendedKeyUsage=serverAuth'], check=True,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER).load_cert_chain(work/'server.crt', work/'server.key')
            values = {'HUE2LOX_BIND_IP':str(address), 'HUE_PUBLIC_URL':f'https://{address}:{port}'}
            (work/'.env').write_text('\n'.join(key+'='+values[key] if (key:=line.split('=',1)[0]) in values else line for line in lines)+'\n')
            shutil.copyfile(work/'server.crt', work/'health-test.crt')
            staged = {'.env':work/'.env', 'certs/server.crt':work/'server.crt',
                      'certs/server.key':work/'server.key', 'health-test.crt':work/'health-test.crt'}
            for name, path in staged.items():
                path.chmod(0o600 if name in ('.env','certs/server.key') else 0o644)
                if os.geteuid() == 0:
                    stat = (dest/name).stat()
                    os.chown(path, 10001 if name.startswith('certs/') else stat.st_uid,
                             10001 if name.startswith('certs/') else stat.st_gid)
            try:
                for name, path in staged.items():
                    os.replace(path, dest/name)
                (dest/'certs').chmod(0o700)
                if os.geteuid() == 0:
                    os.chown(dest/'certs', 10001, 10001)
            except BaseException:
                # Process errors roll back. A power loss requires the retained backup.
                for name in FILES:
                    shutil.copy2(backup/name, dest/name)
                    if os.geteuid() == 0:
                        stat = (backup/name).stat()
                        os.chown(dest/name, stat.st_uid, stat.st_gid)
                raise
    except BaseException:
        if backup is not None:
            print('Maintenance failed; retained backup: '+str(backup))
        raise
    finally:
        for sock in sockets:
            sock.close()
    return backup


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--destination', required=True)
    parser.add_argument('--host', help='New local IPv4 address; omit for renewal at the current address')
    args = parser.parse_args()
    if os.geteuid() != 0:
        parser.exit(1, 'Run as root on the Linux server after stopping this installation.\n')
    try:
        backup = renew(args.destination, args.host)
    except (ValueError, KeyError, OSError, subprocess.SubprocessError) as error:
        parser.exit(1, 'Renewal failed: '+str(error)+'\n')
    print('Certificate renewed; service remains stopped. Private rollback backup: '+str(backup))
    print('Restart this installation and verify HTTPS and client trust. No tokens or registry changed.')
