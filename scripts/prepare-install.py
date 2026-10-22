"""Prepare an isolated fresh installation; never start Docker or contact a bridge."""
import argparse
import json
import ipaddress
import re
from urllib.parse import urlsplit
import os
from pathlib import Path
import secrets
import shutil
import subprocess
import tempfile
import sys

SOURCE=Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SOURCE / 'src'))
sys.dont_write_bytecode = True
from installer_messages import message, localized_print as print
from install_state import initialize
CODE=('.dockerignore','LICENSE','NOTICE','THIRD-PARTY-NOTICES.md','INSTALL.md','RELEASE.md')


def installation_name():
    adjectives = 'jolly happy clever sunny brave gentle merry lucky cosmic nifty calm bright speedy friendly playful curious dancing flying glowing magic smiling tiny mighty quiet silver golden bold cozy lively fancy swift purple'.split()
    animals = 'jumper octopus otter dolphin penguin puffin turtle panda fox badger beaver koala gecko owl raven robin seal whale squid crab lobster manta falcon finch tiger lion lynx rabbit squirrel wombat yak zebra'.split()
    return 'hue2lox-' + secrets.choice(adjectives) + secrets.choice(animals)


def validate_public_url(value):
    if not re.fullmatch(r'https?://[A-Za-z0-9.-]+(?::[0-9]+)?', value):
        raise ValueError('Use an HTTP(S) origin without credentials, path or trailing slash')
    parsed = urlsplit(value)
    if not parsed.hostname or (parsed.port is not None and not 1 <= parsed.port <= 65535):
        raise ValueError('Invalid public URL')
    return value


def release_image(registry='dockerhub'):
    repositories = {'dockerhub': 'docker.io/dubctrl/hue2lox',
                    'ghcr': 'ghcr.io/square-com-de/hue2lox'}
    if registry not in repositories: raise ValueError('Choose dockerhub or ghcr')
    version = json.loads((SOURCE/'install/release-image.json').read_text()).get('version')
    if not isinstance(version, str) or not re.fullmatch(r'(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-rc\.[1-9]\d*)?', version):
        raise ValueError('Installer image must use a fixed release version')
    return repositories[registry] + ':' + version


def prepare(destination,host,port=8443,scheme='https',public_url=None,source='image',registry='dockerhub'):
    if source not in ('image', 'build'): raise ValueError('Choose image or build')
    image = release_image(registry) if source == 'image' else None
    address=ipaddress.IPv4Address(host)
    if address.is_unspecified or address.is_multicast or not (address.is_private or address.is_loopback):
        raise ValueError('Use a local unicast IPv4 address')
    if type(port) is not int or not 1024<=port<=65535:raise ValueError('Port must be 1024–65535')
    if scheme not in ('http', 'https'): raise ValueError('Choose http or https')
    endpoint = f'{scheme}://{address}:{port}'
    public_url = validate_public_url(public_url or endpoint)
    if scheme == 'https' and public_url != endpoint:
        raise ValueError('Direct HTTPS uses the configured IP and port')
    dest=Path(destination).absolute()
    if dest.exists() or dest.is_symlink():raise ValueError('Destination already exists; nothing changed')
    if not dest.parent.is_dir():raise ValueError('Destination parent must exist')
    if scheme == 'https' and not shutil.which('openssl'):raise ValueError('OpenSSL is required')
    work=Path(tempfile.mkdtemp(prefix='.hue2lox-setup-',dir=dest.parent))
    try:
        for file in CODE:shutil.copyfile(SOURCE/file,work/file);(work/file).chmod(0o644)
        for directory in ('src','docker','config','web','catalog','trust','install','docs'):
            shutil.copytree(SOURCE/directory,work/directory)
            for path in (work/directory).rglob('*'):path.chmod(0o755 if path.is_dir() else 0o644)
            (work/directory).chmod(0o755)
        compose = (SOURCE/'docker/compose.install.yaml').read_text()
        if image:
            start = compose.index('    build:\n')
            end = compose.index('    restart:', start)
            compose = compose[:start] + '    image: ' + image + '\n' + compose[end:]
        (work/'compose.yaml').write_text(compose)
        owner = (10001, 10001) if os.geteuid() == 0 else (None, None)
        initialize(work/'data', work/'certs' if scheme == 'https' else None,
                   work/'secrets', str(address), *owner)
        name = installation_name()
        (work/'.env').write_text(f'COMPOSE_PROJECT_NAME={name}\nHUE2LOX_CONTAINER_NAME={name}-1\nHUE2LOX_BIND_IP={address}\nHUE2LOX_PORT={port}\nHUE2LOX_SCHEME={scheme}\nHUE_PUBLIC_URL={public_url}\nHUE_WRITES_ENABLED=0\nHUE_COLOR_ENABLED=0\nHUE_WHITE_ENABLED=0\n');(work/'.env').chmod(0o600)
        with (work/'.env').open('a') as settings:
            settings.write(f'HUE2LOX_SOURCE={source}\n')
            if image: settings.write(f'HUE2LOX_IMAGE={image}\n')
        if scheme == 'https':
            shutil.copyfile(work/'certs/server.crt',work/'health-test.crt')
        else:
            compose = (work/'compose.yaml').read_text()
            compose = '\n'.join(line for line in compose.split('\n') if not any(
                marker in line for marker in ('      TLS_CERT:', '      TLS_KEY:', '      - ./certs:')))
            (work/'compose.yaml').write_text(compose)
        # Refuse concurrent creation too, rather than replacing another installation.
        if dest.exists() or dest.is_symlink():raise ValueError('Destination appeared during setup')
        # Allow the SSH user to enter the install directory and read public assets.
        # Private subdirectories and .env retain their restrictive permissions.
        work.chmod(0o755)
        work.rename(dest)
    finally:
        if work.exists():shutil.rmtree(work)
    return dest

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--destination',required=True);parser.add_argument('--host',required=True)
    parser.add_argument('--port',type=int,default=8443)
    parser.add_argument('--scheme',choices=('http','https'),default='https')
    parser.add_argument('--public-url')
    parser.add_argument('--source', choices=('image', 'build'), default='image')
    parser.add_argument('--registry', choices=('dockerhub', 'ghcr'), default='dockerhub')
    args=parser.parse_args()
    try:dest=prepare(args.destination,args.host,args.port,args.scheme,args.public_url,args.source,args.registry)
    except (ValueError,OSError,subprocess.SubprocessError) as error:parser.exit(1,message('Setup failed: '+str(error))+'\n')
    print('Fresh installation prepared at '+str(dest))
    print('No container started; no Hue requests sent. Control is disabled by default.')
