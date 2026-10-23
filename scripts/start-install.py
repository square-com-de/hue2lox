"""Validate and start a prepared fresh installation, independent of current directory."""
import argparse
import ipaddress
import os
import json
import re
from pathlib import Path
import shutil
import socket
import ssl
import subprocess
import sys
import time
import urllib.request


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
sys.dont_write_bytecode = True
from installer_messages import message, localized_print as print


def preflight(destination):
    dest = Path(destination).resolve()
    required = ('compose.yaml', '.env', 'secrets/control_token', 'data/registry.json',
                'data/admin_auth.json')
    for name in required:
        if not (dest / name).is_file():
            raise ValueError(f'Installation incomplete: {dest / name} is missing. Run preparation first.')
    if 'HUE_LEGACY_ENABLED: "0"' not in (dest / 'compose.yaml').read_text():
        raise ValueError('This is not a prepared fresh-install Compose file. Do not start from the source folder.')
    env = dict(line.split('=', 1) for line in (dest / '.env').read_text().splitlines()
               if '=' in line and not line.lstrip().startswith('#'))
    host = str(ipaddress.IPv4Address(env.get('HUE2LOX_BIND_IP', '')))
    port = int(env.get('HUE2LOX_PORT', '0'))
    if not 1024 <= port <= 65535:
        raise ValueError('Invalid installation port.')
    scheme = env.get('HUE2LOX_SCHEME', 'https')
    if scheme not in ('http', 'https'): raise ValueError('Invalid installation protocol')
    url = f'{scheme}://{host}:{port}'
    if scheme == 'https' and env.get('HUE_PUBLIC_URL') != url:
        raise ValueError('Public URL and bind address disagree. Correct the installation before starting.')
    if not re.fullmatch(r'https?://[A-Za-z0-9.-]+(?::[0-9]+)?', env.get('HUE_PUBLIC_URL', '')):
        raise ValueError('Invalid browser URL; use an HTTP(S) origin without a path')
    from urllib.parse import urlsplit
    public = urlsplit(env['HUE_PUBLIC_URL'])
    if public.port is not None and not 1 <= public.port <= 65535:
        raise ValueError('Invalid browser URL port')
    # Port zero checks address ownership without conflicting with an already running instance.
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.bind((host, 0))
        except OSError as error:
            raise ValueError('Configured IP does not belong to this server or cannot be bound.') from error
    context = None
    if scheme == 'https':
        for name in ('health-test.crt', 'certs/server.crt', 'certs/server.key'):
            if not (dest/name).is_file(): raise ValueError('Installation incomplete: ' + name)
        context = ssl.create_default_context(cafile=str(dest / 'health-test.crt'))
        context.load_cert_chain(dest / 'certs/server.crt', dest / 'certs/server.key')
    elif 'TLS_CERT:' in (dest/'compose.yaml').read_text() or 'TLS_KEY:' in (dest/'compose.yaml').read_text():
        raise ValueError('HTTP installation must omit both TLS variables')
    return dest, url, context


def installation_source(dest):
    values = dict(line.split('=', 1) for line in (dest/'.env').read_text().splitlines()
                  if '=' in line and not line.lstrip().startswith('#'))
    # Old prepared installations remain local-build installations.
    source = values.get('HUE2LOX_SOURCE', 'build')
    compose = (dest/'compose.yaml').read_text()
    if source == 'image':
        image = values.get('HUE2LOX_IMAGE', '')
        if not re.fullmatch(r'(?:docker\.io/dubctrl|ghcr\.io/square-com-de)/hue2lox:'
                            r'(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)(?:-rc\.[1-9]\d*)?', image):
            raise ValueError('Expected a fixed Hue2Lox release image from Docker Hub or GHCR')
        if ('    image: ' + image) not in compose.splitlines() or re.search(r'^\s+build:', compose, re.M):
            raise ValueError('Saved image and Compose file disagree; nothing started')
    elif source == 'build':
        if '    build:' not in compose.splitlines():
            raise ValueError('Saved build mode and Compose file disagree; nothing started')
    else:
        raise ValueError('Invalid saved installation source')
    return source, values.get('HUE2LOX_IMAGE', '')


def print_success(url):
    en = os.environ.get("HUE2LOX_INSTALL_LANG") == "en"
    def text(de, english):
        return english if en else de
    print(r'''
                    .-""""""-.
                  .'  _    _  '.
                 /   (o)  (o)   \
                |       __       |
                 \    \____/    /
            _     '._        _.'     _
           ( \   _   /      \   _   / )
            \ \_/ \_/  /  \  \_/ \_/ /
             \___/\___/ /\ \___/\___/
                _/ / / /  \ \ \ \_
               (__/ (__/  \__) \__)

                 h u e 2 l o x
''')
    print(text('           ACHT ARME. ALLES IM GRIFF.', '           EIGHT ARMS. ALL UNDER CONTROL.'))
    print('=' * 64)
    print(text('             INSTALLATION ERFOLGREICH', '             INSTALLATION SUCCESSFUL'))
    print('=' * 64)
    print('\n  Installation ready: ' + url)
    print(text('  Diese Adresse jetzt im Browser oeffnen.\n', '  Open this address in your browser now.\n'))
    print(text('  ERSTLOGIN', '  FIRST LOGIN'))
    print(text('  Benutzername: admin', '  Username: admin'))
    print(text('  Passwort:     admin\n', '  Password: admin\n'))
    print(text('  Bereits geaendert? Dein eigenes Passwort gilt weiterhin.', '  Already changed it? Your own password still applies.'))
    print(text('  Beim ersten Login bitte das Standardpasswort aendern.\n', '  Please change the default password after your first login.\n'))
    print('=' * 64)
    print()


def project_name(dest):
    values = dict(line.split('=', 1) for line in (dest / '.env').read_text().splitlines()
                  if '=' in line and not line.lstrip().startswith('#'))
    name = values.get('COMPOSE_PROJECT_NAME', 'hue2lox-test')
    if not re.fullmatch(r'hue2lox-[a-z0-9]+', name):
        raise ValueError('Invalid saved Compose project name.')
    return name


def check_project_owner(dest, name):
    # A random word pair can collide. Never take over an unrelated installation.
    result = subprocess.run(['docker', 'ps', '-aq', '--filter',
                             'label=com.docker.compose.project=' + name],
                            check=True, capture_output=True, text=True)
    ids = result.stdout.split()
    if not ids:
        return
    result = subprocess.run(['docker', 'inspect', *ids], check=True, capture_output=True, text=True)
    for container in json.loads(result.stdout):
        labels = container.get('Config', {}).get('Labels') or {}
        owner = labels.get('com.docker.compose.project.working_dir')
        if not owner or Path(owner).resolve() != dest:
            raise ValueError('Installation name already belongs to another directory. Nothing started; choose a different COMPOSE_PROJECT_NAME and HUE2LOX_CONTAINER_NAME in the new installation .env.')


def start(destination):
    if not sys.platform.startswith('linux'):
        raise ValueError('The fresh-install container uses Linux host networking. Run it on the Linux server.')
    if os.geteuid() != 0:
        raise ValueError('Run this command with sudo on Linux.')
    dest, url, context = preflight(destination)
    source, image = installation_source(dest)
    if not shutil.which('docker'):
        raise ValueError('Docker is missing. Complete the Docker installation first.')
    name = project_name(dest)
    command = ['docker', 'compose', '--project-directory', str(dest),
               '--env-file', str(dest / '.env'), '-f', str(dest / 'compose.yaml'),
               '-p', name]
    subprocess.run(command + ['config', '--quiet'], check=True, cwd=dest)
    if name != 'hue2lox-test':
        check_project_owner(dest, name)
    print('Installation: ' + name, flush=True)
    print('Image: ' + image if source == 'image' else 'Source: local build', flush=True)
    build = command + (['up', '-d', '--no-build', '--pull', 'missing'] if source == 'image'
                       else ['up', '-d', '--build'])
    if os.environ.get('HUE2LOX_INSTALL_COMPACT') == '1':
        label = ('Building and starting Hue2Lox' if os.environ.get('HUE2LOX_INSTALL_LANG') == 'en'
                 else 'Hue2Lox bauen und starten')
        if source == 'image':
            label = ('Downloading and starting the Hue2Lox release image'
                     if os.environ.get('HUE2LOX_INSTALL_LANG') == 'en'
                     else 'Hue2Lox Release-Image laden und starten')
        code = subprocess.run([sys.executable, str(Path(__file__).with_name('installer_progress.py')),
                               label, *build], cwd=dest).returncode
        if code:
            raise subprocess.CalledProcessError(code, ['docker', 'compose', 'up'])
        print('HTTP(S) health check …', flush=True)
    else:
        subprocess.run(build, check=True, cwd=dest)
    # Verify the actual configured endpoint; never print configuration/secrets.
    for attempt in range(30):
        try:
            with urllib.request.urlopen(url + '/health', context=context, timeout=3) as response:
                if response.status == 200 and response.read(256) == b'{"status":"ok"}':
                    values = dict(line.split('=', 1) for line in (dest/'.env').read_text().splitlines() if '=' in line)
                    print_success(values['HUE_PUBLIC_URL'])
                    if values['HUE_PUBLIC_URL'] != url:
                        print(('Backend checked: ' if os.environ.get('HUE2LOX_INSTALL_LANG') == 'en' else 'Backend geprüft: ') + url)
                        print('Configure/check your reverse proxy separately.' if os.environ.get('HUE2LOX_INSTALL_LANG') == 'en' else 'Reverse Proxy separat einrichten und prüfen.')
                    return
        except (OSError, ValueError):
            pass
        time.sleep(2)
    raise ValueError('Service did not pass HTTP(S) health check. Inspect logs for this installation; no success confirmed.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--destination', required=True)
    args = parser.parse_args()
    try:
        start(args.destination)
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        parser.exit(1, message('Start stopped: ' + str(error)) + '\n')
