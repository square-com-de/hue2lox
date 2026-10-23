#!/usr/bin/env python3
"""Native deployment lifecycle. CLI operates only on the local Debian 13 host.

No application state is migrated from Docker. Packages must be explicitly
selected and independently checksummed; no downloads or package upgrades occur.
"""
import argparse
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
import fcntl
import hashlib
import importlib.util
import ipaddress
import json
import os
from pathlib import Path, PurePosixPath
import platform
import pwd
import grp
import re
import secrets
import shutil
import socket
import ssl
import subprocess
import sys
import tarfile
import tempfile
import time
import urllib.request

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'src'))
sys.dont_write_bytecode = True
from installer_messages import message, localized_print as print

SERVICE = 'hue2lox.service'
USER = 'hue2lox'
VERSION = re.compile(r'[0-9]+\.[0-9]+\.[0-9]+(?:-[A-Za-z0-9][A-Za-z0-9.-]*)?\Z')
REQUIRED = {'LICENSE', 'NOTICE', 'THIRD-PARTY-NOTICES.md', 'src/app.py',
            'src/admin_auth.py', 'src/install_state.py', 'src/bridge_store.py',
            'src/bridge_admin.py', 'src/color.py', 'src/dashboard.py', 'src/discovery.py',
            'src/hue_client.py', 'src/lamp_types.py', 'src/loxone_export.py',
            'src/request_monitor.py', 'src/scenes.py', 'web/index.html',
            'catalog/hue-models.json', 'trust/huebridge-ca.pem',
            'deployment/native/hue2lox.service', 'deployment/native/manage.py',
            'deployment/native/install.sh', 'deployment/native/update.sh',
            'deployment/native/uninstall.sh', 'config/registry.json',
            'scripts/prepare-state.py'}
MAX_PACKAGE = 128 * 1024 * 1024


@dataclass(frozen=True)
class Layout:
    root: Path = Path('/')

    @property
    def app(self): return self.root / 'opt/hue2lox'
    @property
    def config(self): return self.root / 'etc/hue2lox'
    @property
    def state(self): return self.root / 'var/lib/hue2lox'
    @property
    def backups(self): return self.root / 'var/backups/hue2lox'
    @property
    def unit(self): return self.root / 'etc/systemd/system/hue2lox.service'
    @property
    def current(self): return self.app / 'current'


def strict_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('Duplicate JSON key')
            result[key] = value
        return result
    try:
        return json.loads(raw, object_pairs_hook=pairs)
    except RecursionError:
        raise ValueError('JSON nesting limit exceeded') from None


def safe_relative(name):
    path = PurePosixPath(name)
    return (bool(name) and not path.is_absolute() and '\\' not in name and
            all(part not in ('', '.', '..') for part in name.split('/')) and
            not any(ord(c) < 32 or ord(c) == 127 for c in name))


def verify_package(package, sha256, destination):
    """Verify before extracting any bytes; never use tar's path/link extraction."""
    package, destination = Path(package), Path(destination)
    if not re.fullmatch(r'[0-9a-fA-F]{64}', sha256):
        raise ValueError('Expected an independently obtained SHA256 (64 hex characters)')
    if package.stat().st_size > MAX_PACKAGE:
        raise ValueError('Package too large')
    # Read one immutable snapshot, eliminating checksum/extraction TOCTOU.
    import io
    blob = package.read_bytes()
    if hashlib.sha256(blob).hexdigest() != sha256.lower():
        raise ValueError('Package SHA256 mismatch; nothing installed')
    content = {}
    total = 0
    with tarfile.open(fileobj=io.BytesIO(blob), mode='r:gz') as archive:
        for index, member in enumerate(archive):
            if index >= 2000 or not member.isfile() or not member.name.startswith('hue2lox-native/'):
                raise ValueError('Invalid package entry type, prefix or count')
            name = member.name[len('hue2lox-native/'):]
            if not safe_relative(name) or name in content:
                raise ValueError('Invalid or duplicate package path')
            total += member.size
            if not 0 <= member.size <= 32 * 1024 * 1024 or total > MAX_PACKAGE:
                raise ValueError('Expanded package too large')
            with archive.extractfile(member) as source:
                data = source.read(member.size + 1)
            if len(data) != member.size:
                raise ValueError('Truncated package')
            content[name] = data
    if 'manifest.json' not in content:
        raise ValueError('Missing package manifest')
    manifest_bytes = content.pop('manifest.json')
    if len(manifest_bytes) > 1024 * 1024:
        raise ValueError('Package manifest too large')
    manifest = strict_json(manifest_bytes)
    if (type(manifest) is not dict or type(manifest.get('schema_version')) is not int or manifest['schema_version'] != 1 or
            type(manifest.get('version')) is not str or len(manifest['version']) > 64 or not VERSION.fullmatch(manifest['version']) or
            type(manifest.get('commit')) is not str or not re.fullmatch(r'[0-9a-f]{40}', manifest['commit']) or
            type(manifest.get('dirty')) is not bool or type(manifest.get('files')) is not dict):
        raise ValueError('Invalid package identity or schema')
    if set(content) != set(manifest['files']) or not REQUIRED <= set(content):
        raise ValueError('Package manifest does not match complete runtime')
    for name, data in content.items():
        if manifest['files'][name] != hashlib.sha256(data).hexdigest():
            raise ValueError('Packaged file checksum mismatch')
    if destination.exists() or destination.is_symlink():
        raise ValueError('Extraction destination already exists')
    destination.mkdir(mode=0o755)
    destination.chmod(0o755)
    for name, data in content.items():
        path = destination / name
        path.parent.mkdir(parents=True, exist_ok=True, mode=0o755)
        path.write_bytes(data)
        path.chmod(0o755 if name.startswith('deployment/native/') and name.endswith('.sh') else 0o644)
    for directory in destination.rglob('*'):
        if directory.is_dir(): directory.chmod(0o755)
    (destination / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    (destination / 'manifest.json').chmod(0o644)
    return manifest


def native_os_target(release, machine, bits, *, dietpi=False, debian_version='', raspberry=False):
    """Explicit experimental targets; no ID_LIKE guesses or CPU-only 64-bit checks."""
    if machine != 'x86_64' or bits <= 32 or raspberry:
        raise ValueError('Native experimental targets currently require amd64 and a 64-bit OS')
    distro = release.get('ID', '').strip('"')
    version = release.get('VERSION_ID', '').strip('"')
    if distro == 'ubuntu' and not dietpi and version in ('24.04', '26.04'):
        return 'Ubuntu ' + version + ' amd64'
    if distro in ('debian', 'dietpi'):
        base = debian_version.split('.')[0] if distro == 'dietpi' else version.split('.')[0]
        if base in ('12', '13'):
            return ('DietPi (Debian ' + base + ')' if dietpi or distro == 'dietpi' else 'Debian ' + base) + ' amd64'
    raise ValueError('Native experimental targets: Debian 12/13, Ubuntu 24.04/26.04, DietPi on Debian 12/13; amd64 only')


def platform_check():
    if sys.platform != 'linux' or os.geteuid() != 0:
        raise ValueError('Run as root on the local Linux test server (su - or sudo -i)')
    release = dict(line.split('=', 1) for line in Path('/etc/os-release').read_text().splitlines() if '=' in line)
    native_os_target(release, platform.machine(), 64 if sys.maxsize > 2**32 else 32,
                     dietpi=Path('/boot/dietpi/.version').is_file(),
                     debian_version=Path('/etc/debian_version').read_text().strip() if Path('/etc/debian_version').is_file() else '',
                     raspberry=Path('/etc/rpi-issue').exists())
    if sys.version_info < (3, 11) or not ssl.create_default_context().hostname_checks_common_name:
        raise ValueError('Python >=3.11 and required OpenSSL/TLS capabilities are needed')
    for command in ('openssl', 'systemctl', 'useradd', 'groupadd'):
        if not shutil.which(command):
            raise ValueError('Missing prerequisite: ' + command + '. Install prerequisites explicitly first.')
    subprocess.run(['/usr/bin/python3', '-c',
                    'import sys,ssl; assert sys.version_info >= (3,11); '
                    'assert ssl.create_default_context().hostname_checks_common_name'], check=True)
    if not Path('/run/systemd/system').is_dir():
        raise ValueError('A booted systemd system is required')


def ensure_account():
    try:
        account = pwd.getpwnam(USER)
    except KeyError:
        try:
            grp.getgrnam(USER)
        except KeyError:
            subprocess.run(['groupadd', '--system', USER], check=True)
        subprocess.run(['useradd', '--system', '--gid', USER, '--home-dir', '/nonexistent',
                        '--no-create-home', '--shell', '/usr/sbin/nologin', USER], check=True)
        account = pwd.getpwnam(USER)
    if account.pw_uid == 0 or account.pw_shell not in ('/usr/sbin/nologin', '/sbin/nologin', '/bin/false'):
        raise ValueError('Existing hue2lox account is not a dedicated non-login service account')
    if grp.getgrgid(account.pw_gid).gr_name != USER:
        raise ValueError('Service account needs its own hue2lox primary group')
    return account.pw_uid, account.pw_gid


def run_systemctl(*args):
    subprocess.run(['systemctl', *args], check=True, stdout=subprocess.DEVNULL)


def reset_failure():
    # A disabled, stopped unit can be unloaded after daemon-reload. Only reset
    # an actual failed unit; resetting an unloaded one is an error in systemd.
    result = subprocess.run(['systemctl', 'is-failed', '--quiet', SERVICE],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if result.returncode == 0:
        run_systemctl('reset-failed', SERVICE)
    elif result.returncode not in (1, 3, 4):
        raise subprocess.CalledProcessError(result.returncode, result.args)


def reject_links(path):
    path = Path(path)
    for parent in [path, *path.parents]:
        if parent.is_symlink():
            raise ValueError('Refuse a symbolic installation directory: ' + str(parent))
    if path.exists() and any(p.is_symlink() for p in path.rglob('*')):
        raise ValueError('Refuse links in private state/configuration')


def atomic_text(path, text, mode=0o600):
    descriptor, name = tempfile.mkstemp(prefix='.' + path.name + '-', dir=path.parent)
    try:
        with os.fdopen(descriptor, 'w') as output:
            os.fchmod(output.fileno(), mode)
            output.write(text)
            output.flush()
            os.fsync(output.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name): os.unlink(name)


def settings(layout):
    values = {}
    for line in (layout.config / 'settings.env').read_text().splitlines():
        if not line or line.startswith('#'): continue
        key, separator, value = line.partition('=')
        if not separator or key in values or not re.fullmatch(r'[A-Z][A-Z0-9_]*', key) or any(c.isspace() or ord(c) < 32 for c in value):
            raise ValueError('Settings require unique KEY=value entries without shell syntax')
        values[key] = value
    host = str(ipaddress.IPv4Address(values.get('BIND_HOST', '')))
    port = int(values.get('PORT', '0'))
    if not 1024 <= port <= 65535 or values.get('HUE_PUBLIC_URL') != f'https://{host}:{port}':
        raise ValueError('Bind endpoint and HUE_PUBLIC_URL disagree')
    expected = {'HUE_STATE_DIR': str(layout.state), 'HUE_REGISTRY_FILE': str(layout.state / 'registry.json'),
                'HUE_ADMIN_AUTH_FILE': str(layout.state / 'admin_auth.json'),
                'HUE_CONTROL_TOKEN_FILE': str(layout.config / 'secrets/control_token'),
                'TLS_CERT': str(layout.config / 'certs/server.crt'),
                'TLS_KEY': str(layout.config / 'certs/server.key')}
    if any(values.get(key) != value for key, value in expected.items()):
        raise ValueError('Managed private paths changed; explicit migration required')
    return values


def health(layout):
    values = settings(layout)
    context = ssl.create_default_context(cafile=values['TLS_CERT'])
    # Never follow redirects, use environment proxy settings or contact a bridge.
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *args, **kwargs): return None
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}),
                                        urllib.request.HTTPSHandler(context=context), NoRedirect())
    deadline = time.monotonic() + 20
    while time.monotonic() < deadline:
        try:
            with opener.open(values['HUE_PUBLIC_URL'] + '/health', timeout=2) as response:
                if response.status == 200 and response.read(257) == b'{"status":"ok"}':
                    return
        except (OSError, ValueError):
            pass
        time.sleep(.25)
    raise ValueError('Native service failed verified HTTPS healthcheck; no success confirmed')


def initialize_private(layout, runtime, host, uid, gid):
    command = [sys.executable, str(runtime / 'scripts/prepare-state.py'),
               '--state-directory', str(layout.state),
               '--certificate-directory', str(layout.config / 'certs'),
               '--secret-directory', str(layout.config / 'secrets'), '--host', host,
               '--uid', str(uid), '--gid', str(gid)]
    subprocess.run(command, check=True, stdout=subprocess.DEVNULL)
    private_permissions(layout, uid, gid)


def private_permissions(layout, uid, gid):
    for directory in (layout.config, layout.config / 'certs', layout.config / 'secrets'):
        if directory.exists():
            os.chown(directory, 0, gid)
            directory.chmod(0o750)
    for path in layout.config.rglob('*'):
        if path.is_file():
            os.chown(path, 0, gid)
            path.chmod(0o640)
    if layout.state.exists():
        os.chown(layout.state, uid, gid)
        layout.state.chmod(0o700)
        for path in layout.state.rglob('*'):
            os.chown(path, uid, gid)
            path.chmod(0o700 if path.is_dir() else 0o600)


def activate(layout, runtime):
    link = layout.app / ('.current-' + secrets.token_hex(6))
    link.symlink_to(runtime)
    os.replace(link, layout.current)


def install_unit(layout, runtime):
    text = (runtime / 'deployment/native/hue2lox.service').read_text()
    # Exact paths are fixed for the CLI. Layout rebasing is for isolated tests only.
    if layout.root != Path('/'):
        text = text.replace('/opt/hue2lox', str(layout.app)).replace('/etc/hue2lox', str(layout.config)).replace('/var/lib/hue2lox', str(layout.state))
    layout.unit.parent.mkdir(parents=True, exist_ok=True)
    atomic_text(layout.unit, text, 0o644)


def install_record(layout, manifest, installed=True):
    record = {'schema_version': 1, 'deployment': 'hue2lox-native', 'version': manifest['version'],
              'commit': manifest['commit'], 'dirty': manifest['dirty'], 'installed': installed,
              'unit_sha256': hashlib.sha256(layout.unit.read_bytes()).hexdigest() if layout.unit.exists() else None}
    atomic_text(layout.config / 'install.json', json.dumps(record, indent=2) + '\n', 0o640)


def managed(layout, require_installed=True):
    reject_links(layout.config)
    reject_links(layout.state)
    record = strict_json((layout.config / 'install.json').read_text())
    if record.get('deployment') != 'hue2lox-native' or record.get('schema_version') != 1:
        raise ValueError('Not a managed native installation; nothing changed')
    if require_installed:
        if record.get('installed') is not True or not layout.current.is_symlink():
            raise ValueError('Native application is not installed')
        active = layout.current.resolve(strict=True)
        releases = (layout.app / 'releases').resolve()
        if active.parent != releases or not active.is_dir():
            raise ValueError('Active version is outside managed releases')
        if layout.unit.is_symlink() or not layout.unit.is_file() or hashlib.sha256(layout.unit.read_bytes()).hexdigest() != record['unit_sha256']:
            raise ValueError('Managed service file changed; review it before updating/uninstalling')
        return record, active
    return record, None


def validate_runtime(runtime):
    for file in (runtime / 'src').glob('*.py'):
        compile(file.read_bytes(), str(file), 'exec')
    for file in ('catalog/hue-models.json', 'config/registry.json'):
        strict_json((runtime / file).read_text())
    # Import runtime without writing bytecode or executing application startup.
    subprocess.run([sys.executable, '-B', '-c', 'import app, install_state'],
                   cwd=runtime / 'src', check=True, stdout=subprocess.DEVNULL)


def staged_release(args, layout):
    manifest = verify_package(args.package, args.sha256, layout / 'candidate')
    runtime = layout / 'candidate'
    validate_runtime(runtime)
    return manifest, runtime


def install(args, layout):
    platform_check()
    if getattr(args, 'keep_data', False):
        return reinstall(args, layout)
    for path in (layout.app, layout.config, layout.state, layout.backups, layout.unit):
        reject_links(path)
    if any(p.exists() for p in (layout.app, layout.config, layout.state, layout.unit)):
        raise ValueError('Native destination exists. Use update; no existing credentials were reset.')
    host = str(ipaddress.IPv4Address(args.host))
    address = ipaddress.ip_address(host)
    if not (address.is_private or address.is_loopback) or address.is_unspecified or address.is_multicast:
        raise ValueError('Use a local unicast IPv4 address')
    if not 1024 <= args.port <= 65535:
        raise ValueError('Port must be 1024–65535')
    with socket.socket() as probe:
        probe.bind((host, args.port))
    with tempfile.TemporaryDirectory(prefix='hue2lox-native-') as directory:
        manifest, runtime = staged_release(args, Path(directory))
        uid, gid = ensure_account()
        destination = layout.app / 'releases' / (manifest['version'] + '-' + manifest['commit'][:12] + '-' + secrets.token_hex(4))
        created = []
        try:
            layout.app.mkdir(parents=True, mode=0o755)
            created.append(layout.app)
            layout.app.chmod(0o755)
            (layout.app / 'releases').mkdir(mode=0o755)
            (layout.app / 'releases').chmod(0o755)
            layout.config.mkdir(parents=True, mode=0o750)
            created.append(layout.config)
            layout.state.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(runtime, destination)
            initialize_private(layout, destination, host, uid, gid)
            values = {'BIND_HOST': host, 'PORT': str(args.port), 'HUE_PUBLIC_URL': f'https://{host}:{args.port}',
                      'HUE_STATE_DIR': str(layout.state), 'HUE_REGISTRY_FILE': str(layout.state / 'registry.json'),
                      'HUE_ADMIN_AUTH_FILE': str(layout.state / 'admin_auth.json'),
                      'HUE_CONTROL_TOKEN_FILE': str(layout.config / 'secrets/control_token'),
                      'HUE_CA_FILE': str(layout.current / 'trust/huebridge-ca.pem'),
                      'TLS_CERT': str(layout.config / 'certs/server.crt'), 'TLS_KEY': str(layout.config / 'certs/server.key'),
                      'HUE_LEGACY_ENABLED': '0', 'HUE_WRITES_ENABLED': '0', 'HUE_COLOR_ENABLED': '0',
                      'HUE_WHITE_ENABLED': '0', 'PYTHONDONTWRITEBYTECODE': '1'}
            atomic_text(layout.config / 'settings.env', ''.join(f'{k}={v}\n' for k, v in values.items()), 0o640)
            activate(layout, destination)
            install_unit(layout, destination)
            install_record(layout, manifest)
            private_permissions(layout, uid, gid)
            run_systemctl('daemon-reload')
            run_systemctl('enable', '--now', SERVICE)
            health(layout)
        except BaseException:
            # Leave private state available for diagnosis, with a managed record
            # allowing explicit uninstall. Never claim a failed start succeeded.
            if (layout.config / 'install.json').exists():
                try: run_systemctl('disable', '--now', SERVICE)
                except subprocess.CalledProcessError: pass
            else:
                # Before a managed service exists, undo only our own new files.
                # initialize() removes its three private dirs on preparation errors.
                if layout.unit.exists(): layout.unit.unlink()
                if layout.state.exists(): shutil.rmtree(layout.state)
                for path in reversed(created):
                    if path.exists(): shutil.rmtree(path)
            raise
    print(f'Native installation ready: https://{host}:{args.port}\nInitial login: admin / admin. Change it after login. Control remains disabled.')


def reinstall(args, layout):
    """Resume only an explicitly retained installation of the same code identity."""
    record, _ = managed(layout, require_installed=False)
    if record.get('installed') is not False or record.get('uninstalling'):
        raise ValueError('Finish uninstall before reinstalling retained data')
    values = settings(layout)
    if values['BIND_HOST'] != args.host or int(values['PORT']) != args.port:
        raise ValueError('Retained endpoint must be preserved')
    for path in (layout.app, layout.unit):
        reject_links(path)
        if path.exists(): raise ValueError('Application destination already exists')
    with tempfile.TemporaryDirectory(prefix='hue2lox-reinstall-') as directory:
        manifest, runtime = staged_release(args, Path(directory))
        if any(manifest[key] != record[key] for key in ('version', 'commit', 'dirty')):
            raise ValueError('Reinstall requires the retained package identity; update afterwards')
        uid, gid = ensure_account()
        layout.app.mkdir(parents=True, mode=0o755)
        # mkdir modes are filtered by the caller's umask, including root's 077.
        layout.app.chmod(0o755)
        (layout.app / 'releases').mkdir(mode=0o755)
        (layout.app / 'releases').chmod(0o755)
        destination = layout.app / 'releases' / ('restored-' + secrets.token_hex(8))
        try:
            shutil.copytree(runtime, destination)
            activate(layout, destination)
            install_unit(layout, destination)
            install_record(layout, manifest)
            private_permissions(layout, uid, gid)
            run_systemctl('daemon-reload')
            run_systemctl('enable', '--now', SERVICE)
            health(layout)
        except BaseException:
            if strict_json((layout.config / 'install.json').read_text()).get('installed') is False:
                if layout.unit.exists(): layout.unit.unlink()
                shutil.rmtree(layout.app)
                raise
            # Keep a managed installation for diagnosis/retry via update/uninstall.
            if layout.unit.exists():
                try: run_systemctl('disable', '--now', SERVICE)
                except subprocess.CalledProcessError: pass
            raise
    print('Native application reinstalled; existing private data preserved.')


def snapshot_hashes(directory):
    reject_links(directory)
    return {p.relative_to(directory).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in directory.rglob('*') if p.is_file() and p.relative_to(directory).as_posix() != 'snapshot.json'}


def checked_backup(layout, directory):
    directory = Path(directory).absolute()
    reject_links(layout.backups)
    if directory.parent != layout.backups.absolute() or not directory.is_dir():
        raise ValueError('Select a direct backup directory under the managed backup root')
    manifest = strict_json((directory / 'snapshot.json').read_text())
    if manifest.get('schema_version') != 1 or manifest.get('files') != snapshot_hashes(directory):
        raise ValueError('Backup checksum mismatch or incomplete backup')
    for name in ('config/install.json', 'config/settings.env', 'state/registry.json',
                 'hue2lox.service', 'runtime/manifest.json', 'state/admin_auth.json',
                 'config/certs/server.key', 'config/certs/server.crt', 'config/secrets/control_token'):
        if name not in manifest['files']: raise ValueError('Incomplete native backup')
    validate_runtime(directory / 'runtime')
    return directory


def restore_snapshot(layout, saved, uid, gid, previous=None):
    # Prepare complete replacements before removing any live private directory.
    checked_backup(layout, saved)
    reject_links(layout.config)
    reject_links(layout.state)
    destination = layout.app / 'releases' / ('rollback-' + secrets.token_hex(8))
    if previous is not None and snapshot_hashes(previous) == snapshot_hashes(saved / 'runtime'):
        destination = previous
    else:
        shutil.copytree(saved / 'runtime', destination)
    with tempfile.TemporaryDirectory(prefix='.restore-', dir=layout.config.parent) as directory:
        staged_config = Path(directory) / 'config'
        shutil.copytree(saved / 'config', staged_config)
        with tempfile.TemporaryDirectory(prefix='.restore-', dir=layout.state.parent) as state_directory:
            staged_state = Path(state_directory) / 'state'
            shutil.copytree(saved / 'state', staged_state)
            for source, target in ((staged_config, layout.config), (staged_state, layout.state)):
                if target.exists(): shutil.rmtree(target)
                source.rename(target)
    activate(layout, destination)
    shutil.copy2(saved / 'hue2lox.service', layout.unit)
    private_permissions(layout, uid, gid)
    run_systemctl('daemon-reload')
    reset_failure()
    run_systemctl('enable', '--now', SERVICE)
    health(layout)


def rollback(args, layout):
    platform_check()
    _, active = managed(layout)
    settings(layout)
    reject_links(layout.app / 'releases')
    saved = checked_backup(layout, args.backup)
    uid, gid = ensure_account()
    run_systemctl('stop', SERVICE)
    try:
        recovery = backup(layout, active)
    except BaseException:
        run_systemctl('start', SERVICE)
        raise
    try:
        restore_snapshot(layout, saved, uid, gid)
    except BaseException as failure:
        try:
            run_systemctl('stop', SERVICE)
            restore_snapshot(layout, recovery, uid, gid)
        except BaseException as error:
            raise ValueError(f'Rollback and recovery failed; protected backup: {recovery}') from error
        raise ValueError(f'Rollback failed; original installation restored. Backup: {recovery}') from failure
    print(f'Rollback passed HTTPS check. Pre-rollback recovery backup: {recovery}')


def backup(layout, active):
    layout.backups.mkdir(parents=True, exist_ok=True, mode=0o700)
    layout.backups.chmod(0o700)
    target = layout.backups / (datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + secrets.token_hex(6))
    target.mkdir(mode=0o700)
    shutil.copytree(layout.config, target / 'config', symlinks=True)
    shutil.copytree(layout.state, target / 'state', symlinks=True)
    shutil.copy2(layout.unit, target / 'hue2lox.service')
    shutil.copytree(active, target / 'runtime')
    atomic_text(target / 'previous.json', json.dumps({'active': str(active)}))
    atomic_text(target / 'snapshot.json', json.dumps({'schema_version': 1, 'files': snapshot_hashes(target)}))
    return target


def update(args, layout):
    platform_check()
    record, previous = managed(layout)
    settings(layout)
    # Reject external aliases before any root-level archive copy or replacement.
    reject_links(layout.app / 'releases')
    reject_links(layout.backups)
    uid, gid = ensure_account()
    with tempfile.TemporaryDirectory(prefix='hue2lox-native-') as directory:
        manifest, runtime = staged_release(args, Path(directory))
        # This release has registry schema 1 and NO migration implementation.
        if strict_json((layout.state / 'registry.json').read_text()).get('schema_version') != 1:
            raise ValueError('Unsupported state schema; explicit migration required')
        destination = layout.app / 'releases' / (manifest['version'] + '-' + manifest['commit'][:12] + '-' + secrets.token_hex(4))
        shutil.copytree(runtime, destination)
        run_systemctl('stop', SERVICE)
        try:
            saved = backup(layout, previous)
        except BaseException:
            run_systemctl('start', SERVICE)
            raise
        try:
            activate(layout, destination)
            install_unit(layout, destination)
            install_record(layout, manifest)
            private_permissions(layout, uid, gid)
            run_systemctl('daemon-reload')
            reset_failure()
            run_systemctl('enable', '--now', SERVICE)
            health(layout)
        except BaseException as failure:
            try:
                run_systemctl('stop', SERVICE)
                restore_snapshot(layout, saved, uid, gid, previous=previous)
            except BaseException as rollback:
                raise ValueError(f'Update AND rollback failed. Service needs attention. Protected backup: {saved}') from rollback
            raise ValueError(f'Update failed; previous application and private state restored. Backup: {saved}') from failure
    print(f'Native update passed HTTPS healthcheck. Protected backup: {saved}')


def uninstall(args, layout):
    platform_check()
    record, _ = managed(layout, require_installed=False)
    # Finish every safety check before changing service or installation metadata.
    reject_links(layout.app / 'releases')
    if record.get('installed'):
        if not record.get('uninstalling'):
            managed(layout)
        elif layout.unit.exists() or layout.unit.is_symlink():
            if layout.unit.is_symlink() or hashlib.sha256(layout.unit.read_bytes()).hexdigest() != record['unit_sha256']:
                raise ValueError('Managed service file changed during uninstall')
        if layout.current.exists() or layout.current.is_symlink():
            if not layout.current.is_symlink() or layout.current.resolve().parent != (layout.app / 'releases').resolve():
                raise ValueError('Invalid current application reference')
        record['uninstalling'] = True
        atomic_text(layout.config / 'install.json', json.dumps(record), 0o640)
        if layout.unit.exists():
            run_systemctl('disable', '--now', SERVICE)
            layout.unit.unlink()
        run_systemctl('daemon-reload')
        if layout.current.is_symlink(): layout.current.unlink()
        if layout.app.exists(): shutil.rmtree(layout.app)
    if args.purge_data:
        for directory in (layout.state, layout.config):
            reject_links(directory)
            if directory.exists(): shutil.rmtree(directory)
        print('Native application and private configuration/state removed. Backups retained.')
    else:
        record.pop('uninstalling', None)
        record['installed'] = False
        record['unit_sha256'] = None
        atomic_text(layout.config / 'install.json', json.dumps(record, indent=2) + '\n', 0o640)
        print('Native application removed. Private configuration, state and backups retained.')
    # Keep account to preserve ownership of retained private files/backups.


@contextmanager
def operation_lock():
    path = Path('/run/lock/hue2lox-native.lock')
    descriptor = os.open(path, os.O_CREAT | os.O_RDWR | getattr(os, 'O_NOFOLLOW', 0), 0o600)
    try:
        fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield
    except BlockingIOError:
        raise ValueError('Another native installation operation is running') from None
    finally:
        os.close(descriptor)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='action', required=True)
    for action in ('install', 'update'):
        sub = commands.add_parser(action)
        sub.add_argument('--package', required=True, type=Path)
        sub.add_argument('--sha256', required=True)
        if action == 'install':
            sub.add_argument('--keep-data', action='store_true', help='Reinstall the same package using retained private data')
            sub.add_argument('--host', required=True)
            sub.add_argument('--port', type=int, default=18443)
    commands.add_parser('check', help='Read-only native platform and prerequisite check')
    sub = commands.add_parser('rollback')
    sub.add_argument('--backup', required=True, type=Path, help='Complete managed backup; restores its code AND private data')
    sub = commands.add_parser('uninstall')
    sub.add_argument('--purge-data', action='store_true', help='Explicitly remove native config/state; retain backups')
    args = parser.parse_args()
    try:
        platform_check()
        if args.action == 'check':
            print('Native experimental platform and prerequisites ready; no installation changed.')
            return
        with operation_lock():
            {'install': install, 'update': update, 'uninstall': uninstall, 'rollback': rollback}[args.action](args, Layout())
    except (ValueError, OSError, subprocess.SubprocessError, tarfile.TarError, KeyError) as error:
        parser.exit(1, message('Native operation stopped: ' + str(error)) + '\n')


if __name__ == '__main__':
    main()
