"""Prepare an isolated fresh installation; never start Docker or contact a bridge."""
import argparse
import importlib.util
import ipaddress
import json
import os
from pathlib import Path
import secrets
import shutil
import subprocess
import tempfile

SOURCE=Path(__file__).resolve().parent.parent
CODE=('.dockerignore','LICENSE','NOTICE','THIRD-PARTY-NOTICES.md','INSTALL.md','RELEASE.md')


def installation_name():
    adjectives = 'jolly happy clever sunny brave gentle merry lucky cosmic nifty calm bright speedy friendly playful curious dancing flying glowing magic smiling tiny mighty quiet silver golden bold cozy lively fancy swift purple'.split()
    animals = 'jumper octopus otter dolphin penguin puffin turtle panda fox badger beaver koala gecko owl raven robin seal whale squid crab lobster manta falcon finch tiger lion lynx rabbit squirrel wombat yak zebra'.split()
    return 'hue2lox-' + secrets.choice(adjectives) + secrets.choice(animals)


def prepare(destination,host,port=8443):
    address=ipaddress.IPv4Address(host)
    if address.is_unspecified or address.is_multicast or not (address.is_private or address.is_loopback):
        raise ValueError('Use a local unicast IPv4 address')
    if type(port) is not int or not 1024<=port<=65535:raise ValueError('Port must be 1024–65535')
    dest=Path(destination).absolute()
    if dest.exists() or dest.is_symlink():raise ValueError('Destination already exists; nothing changed')
    if not dest.parent.is_dir():raise ValueError('Destination parent must exist')
    if not shutil.which('openssl'):raise ValueError('OpenSSL is required')
    spec=importlib.util.spec_from_file_location('fresh_admin',SOURCE/'src/admin_auth.py')
    auth=importlib.util.module_from_spec(spec);spec.loader.exec_module(auth)
    work=Path(tempfile.mkdtemp(prefix='.hue2lox-setup-',dir=dest.parent))
    try:
        for file in CODE:shutil.copyfile(SOURCE/file,work/file);(work/file).chmod(0o644)
        for directory in ('src','docker','config','web','catalog','trust','install','docs'):
            shutil.copytree(SOURCE/directory,work/directory)
            for path in (work/directory).rglob('*'):path.chmod(0o755 if path.is_dir() else 0o644)
            (work/directory).chmod(0o755)
        shutil.copyfile(SOURCE/'docker/compose.install.yaml',work/'compose.yaml')
        for directory in ('data','certs','secrets'):(work/directory).mkdir(mode=0o700)
        for path,value in [('data/registry.json',{'schema_version':1,'bridges':[]}),('data/admin_auth.json',auth.create_credentials('admin','admin'))]:
            (work/path).write_text(json.dumps(value));(work/path).chmod(0o600)
        (work/'secrets/control_token').write_text(secrets.token_hex(32)+'\n');(work/'secrets/control_token').chmod(0o400)
        name = installation_name()
        (work/'.env').write_text(f'COMPOSE_PROJECT_NAME={name}\nHUE2LOX_CONTAINER_NAME={name}-1\nHUE2LOX_BIND_IP={address}\nHUE2LOX_PORT={port}\nHUE_PUBLIC_URL=https://{address}:{port}\nHUE_WRITES_ENABLED=0\nHUE_COLOR_ENABLED=0\nHUE_WHITE_ENABLED=0\n');(work/'.env').chmod(0o600)
        san=','.join(dict.fromkeys([f'IP:{address}','IP:127.0.0.1','DNS:localhost']))
        subprocess.run(['openssl','req','-x509','-newkey','rsa:2048','-sha256','-nodes','-days','365',
            '-keyout',str(work/'certs/server.key'),'-out',str(work/'certs/server.crt'),
            '-subj','/CN=hue2lox.local','-addext','subjectAltName='+san,'-addext','extendedKeyUsage=serverAuth'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        (work/'certs/server.key').chmod(0o600);(work/'certs/server.crt').chmod(0o644)
        shutil.copyfile(work/'certs/server.crt',work/'health-test.crt')
        if os.geteuid()==0:
            for directory in ('data','certs','secrets'):
                os.chown(work/directory,10001,10001)
                for path in (work/directory).rglob('*'):os.chown(path,10001,10001)
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
    parser.add_argument('--port',type=int,default=8443);args=parser.parse_args()
    try:dest=prepare(args.destination,args.host,args.port)
    except (ValueError,OSError,subprocess.SubprocessError) as error:parser.exit(1,'Setup failed: '+str(error)+'\n')
    print('Fresh installation prepared at '+str(dest))
    print('No container started; no Hue requests sent. Control is disabled by default.')
