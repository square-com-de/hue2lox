"""Release-only GHCR and Docker Hub publication; never invoked by the installer.

The validate subcommand is offline. prepare and publish require a published
GitHub release, downloaded artifacts from this run, and explicit job tokens.
"""
import argparse
import hashlib
import gzip
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tarfile
import tempfile
import urllib.request

REPO = 'square-com-de/hue2lox'
IMAGE = 'ghcr.io/' + REPO
IMAGES = (IMAGE, 'docker.io/dubctrl/hue2lox')
ARCHES = ('amd64', 'arm64')


def run(*args, **kwargs):
    return subprocess.check_output(args, text=True, **kwargs).strip()


def plan(event, event_name, repository, commit):
    release = event.get('release', {})
    tag = release.get('tag_name', '')
    match = re.fullmatch(r'v(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-rc\.([1-9]\d*))?', tag)
    if event_name != 'release' or event.get('action') != 'published':
        raise ValueError('Only a published release can publish images')
    if repository != REPO or not match or release.get('draft', True):
        raise ValueError('Unexpected repository, draft or unsupported version tag')
    version = tuple(int(n) for n in match.groups()[:3])
    rc = match.group(4)
    if version < (1, 0, 0) or (version == (1, 0, 0) and rc and int(rc) < 6):
        raise ValueError('Historical RC1 through RC5 must remain unchanged')
    if release.get('prerelease') is not bool(rc):
        raise ValueError('RC tags must be prereleases; stable tags must not be prereleases')
    if not re.fullmatch(r'[0-9a-f]{40}', commit):
        raise ValueError('Expected a full source commit')
    if not isinstance(release.get('id'), int):
        raise ValueError('Missing release identity')
    return {'tag': tag, 'version': tag[1:], 'prerelease': bool(rc),
            'commit': commit, 'release_id': release['id'], 'image': IMAGE, 'images': list(IMAGES)}


def check_installer_version(version, path=None):
    path = path or Path(__file__).resolve().parents[1]/'install/release-image.json'
    if json.loads(path.read_text()).get('version') != version:
        raise ValueError('Update install/release-image.json to the release version before tagging')



STABLE_READINESS = Path(__file__).resolve().parents[1]/'compliance/stable-readiness.json'
STABLE_CHECKS = ('documentation_review', 'published_user_flow', 'update_recovery', 'support_scope')


def acceptance_source_digest(commit, cwd=None):
    """Bind approval to all tracked content except the approval record itself."""
    entries = subprocess.check_output(['git', 'ls-tree', '--full-tree', '-rz', commit], cwd=cwd).split(b'\0')
    content = b'\0'.join(entry for entry in entries if entry and
                         entry.split(b'\t', 1)[1] != b'compliance/stable-readiness.json')
    return hashlib.sha256(content).hexdigest()


def check_stable_readiness(info, path=None):
    """Fail closed before publication/promotion; RC preparation is still allowed."""
    if info['prerelease']:
        return
    path = path or STABLE_READINESS
    try:
        record = json.loads(path.read_text())
    except (OSError, ValueError):
        raise ValueError('Stable blocked: missing/invalid stable-readiness.json') from None
    if (type(record) is not dict or record.get('schema_version') != 1 or
            record.get('version') != info['version'] or record.get('approved') is not True):
        raise ValueError('Stable blocked: reviewed version-specific approval is required')
    checks = record.get('checks')
    if type(checks) is not dict:
        raise ValueError('Stable blocked: acceptance evidence is required')
    for name in STABLE_CHECKS:
        check = checks.get(name)
        if (type(check) is not dict or check.get('passed') is not True or
                type(check.get('evidence')) is not list or not check['evidence'] or
                any(type(link) is not str or not link.startswith('https://github.com/'+REPO+'/')
                    for link in check['evidence'])):
            raise ValueError('Stable blocked: incomplete '+name)
    if record.get('source_sha256') != acceptance_source_digest(info['commit']):
        raise ValueError('Stable blocked: source/docs changed since acceptance')


def current_plan():
    event = json.loads(Path(os.environ['GITHUB_EVENT_PATH']).read_text())
    commit = run('git', 'rev-parse', 'HEAD')
    result = plan(event, os.environ['GITHUB_EVENT_NAME'], os.environ['GITHUB_REPOSITORY'], commit)
    check_installer_version(result['version'])
    check_stable_readiness(result)
    if commit != os.environ['GITHUB_SHA']:
        raise ValueError('Checkout does not match the release workflow commit')
    if run('git', 'rev-parse', result['tag'] + '^{commit}') != commit:
        raise ValueError('Release tag does not match checkout')
    subprocess.run(['git', 'merge-base', '--is-ancestor', commit, 'origin/main'], check=True)
    return result


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def verify_inventory(evidence, commit, arch):
    if (evidence / 'source-commit.txt').read_text().strip() != commit:
        raise ValueError('Evidence belongs to another source commit')
    images = json.loads((evidence / 'image.json').read_text())
    if len(images) != 1:
        raise ValueError('Expected exactly one image')
    image = images[0]
    if image['Architecture'] != arch or image['Os'] != 'linux':
        raise ValueError('Wrong platform')
    if image['Config']['Labels'].get('org.opencontainers.image.revision') != commit:
        raise ValueError('Image revision label does not match release')
    return image['Id']


def archive_evidence(destination):
    """Keep retry uploads identical despite artifact extraction timestamps."""
    with destination.open('wb') as raw:
        with gzip.GzipFile(fileobj=raw, mode='wb', filename='', mtime=0) as compressed:
            with tarfile.open(fileobj=compressed, mode='w') as archive:
                paths = [Path('evidence'), *sorted(Path('evidence').rglob('*'))]
                for path in paths:
                    if path.is_symlink():
                        raise ValueError('Evidence must not contain symbolic links')
                    entry = archive.gettarinfo(str(path), arcname=path.as_posix())
                    entry.mtime = entry.uid = entry.gid = 0
                    entry.uname = entry.gname = ''
                    entry.mode = 0o755 if path.is_dir() else 0o644
                    if path.is_file():
                        with path.open('rb') as stream:
                            archive.addfile(entry, stream)
                    elif path.is_dir():
                        archive.addfile(entry)
                    else:
                        raise ValueError('Evidence must contain regular files/directories')


def prepare_source_packages(info, assets):
    """Offline source/native assets from one immutable commit, never workspace state."""
    if (not re.fullmatch(r'[0-9a-f]{40}', info['commit'])
            or not re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+(?:-rc\.[1-9][0-9]*)?', info['version'])
            or info['tag'] != 'v' + info['version']):
        raise ValueError('Expected matching release version, tag and full commit')
    source = run('git', '-c', 'safe.directory=' + str(Path.cwd().resolve()), 'rev-parse', '--show-toplevel')
    assets = assets.resolve()
    source_name = 'hue2lox-' + info['tag']
    subprocess.run(['git', '-c', 'safe.directory=' + source, 'archive', '--format=zip', '--prefix=' + source_name + '/',
                    '--output=' + str(assets / (source_name + '.zip')), info['commit']],
                   check=True, env={**os.environ, 'TZ': 'UTC'})
    # A clean local clone excludes dirty/untracked files and artifact downloads.
    # Do not mutate the release checkout or manufacture a commit for a ZIP tree.
    with tempfile.TemporaryDirectory(prefix='hue2lox-release-native-') as temporary:
        checkout, output = Path(temporary) / 'source', Path(temporary) / 'packages'
        subprocess.run(['git', '-c', 'safe.directory=' + source,
                        '-c', 'safe.directory=' + str(Path(source) / '.git'),
                        'clone', '--quiet', '--no-hardlinks', '--no-checkout',
                        '--', source, str(checkout)], check=True)
        subprocess.run(['git', 'checkout', '--quiet', '--detach', info['commit']], cwd=checkout, check=True)
        subprocess.run([sys.executable, '-B', str(checkout / 'scripts/build-native-package.py'),
                        '--version', info['version'], '--output', str(output)], cwd=checkout, check=True)
        package = output / ('hue2lox-' + info['version'] + '-native.tar.gz')
        with tarfile.open(package) as archive:
            members = archive.getmembers()
            if any(not entry.isfile() or not entry.name.startswith('hue2lox-native/')
                   or '..' in Path(entry.name).parts for entry in members):
                raise ValueError('Unexpected native package entry')
            manifest = json.load(archive.extractfile('hue2lox-native/manifest.json'))
            if (manifest['commit'] != info['commit'] or manifest['version'] != info['version']
                    or manifest['dirty'] is not False):
                raise ValueError('Native package source/version identity mismatch')
            expected = {'hue2lox-native/' + name for name in manifest['files']} | {'hue2lox-native/manifest.json'}
            if len(members) != len(expected) or {entry.name for entry in members} != expected:
                raise ValueError('Native manifest does not cover the exact archive')
            for name, expected_hash in manifest['files'].items():
                if hashlib.sha256(archive.extractfile('hue2lox-native/' + name).read()).hexdigest() != expected_hash:
                    raise ValueError('Native package file hash mismatch')
        (assets / package.name).write_bytes(package.read_bytes())


def prepare(info):
    """Build recipient assets after all quality and material jobs succeeded."""
    assets = Path('release-assets')
    assets.mkdir()
    prepare_source_packages(info, assets)
    bundle = Path('materials/hue2lox-base-sources.tar.gz')
    subprocess.run(['sha256sum', '--check', 'hue2lox-base-sources.tar.gz.sha256'], cwd='materials', check=True)
    (assets / bundle.name).write_bytes(bundle.read_bytes())
    records = {}
    for arch in ARCHES:
        evidence = Path('evidence') / arch
        subprocess.run(['sha256sum', '--check', 'SHA256SUMS.txt'], cwd=evidence, check=True)
        records[arch] = verify_inventory(evidence, info['commit'], arch)
    archive_evidence(assets / 'container-evidence.tar.gz')
    info['platform_image_ids'] = records
    (assets / 'container-release.json').write_text(json.dumps(info, indent=2) + '\n')
    paths = sorted(assets.iterdir())
    (assets / 'SHA256SUMS.txt').write_text(''.join(digest(p) + '  ' + p.name + '\n' for p in paths))
    return assets


def ensure_asset(info, path):
    """Never replace an existing release asset, including on workflow retries."""
    release = json.loads(run('gh', 'api', f'repos/{REPO}/releases/{info["release_id"]}'))
    if (release['tag_name'] != info['tag'] or release['draft']
            or release['prerelease'] != info['prerelease']):
        raise ValueError('Release changed during publication')
    matching = [a for a in release['assets'] if a['name'] == path.name]
    if not matching:
        subprocess.run(['gh', 'release', 'upload', info['tag'], str(path), '--repo', REPO], check=True)
        release = json.loads(run('gh', 'api', f'repos/{REPO}/releases/{info["release_id"]}'))
        matching = [a for a in release['assets'] if a['name'] == path.name]
    if len(matching) != 1:
        raise ValueError('Release asset missing or ambiguous')
    # No Authorization header: prove recipients can retrieve the exact bytes.
    with urllib.request.urlopen(matching[0]['browser_download_url'], timeout=120) as response:
        remote = hashlib.file_digest(response, 'sha256').hexdigest()
    if remote != digest(path):
        raise ValueError('Existing release asset differs; refusing to overwrite ' + path.name)


def remote_manifest(reference):
    # Distinguish a missing tag from authentication/network errors: fail closed.
    result = subprocess.run(['docker', 'manifest', 'inspect', reference], text=True, capture_output=True)
    if result.returncode:
        if any(message in result.stderr.lower() for message in ('manifest unknown', 'no such manifest', 'name unknown')):
            return None
        raise RuntimeError('Cannot inspect registry tag: ' + result.stderr.strip())
    return json.loads(result.stdout)


def publish(info):
    assets = Path('release-assets')
    for path in sorted(assets.iterdir()):
        ensure_asset(info, path)
    for image in IMAGES:
        publish_registry(info, image)


def publish_registry(info, image):
    references = []
    for arch in ARCHES:
        folder = Path('images') / arch
        subprocess.run(['sha256sum', '--check', 'image.tar.gz.sha256'], cwd=folder, check=True)
        subprocess.run(['docker', 'load', '--input', str(folder / 'image.tar.gz')], check=True)
        expected = verify_inventory(Path('evidence') / arch, info['commit'], arch)
        actual = run('docker', 'image', 'inspect', '--format', '{{.Id}}', 'hue2lox-candidate:inventory')
        if actual != expected:
            raise ValueError('Loaded image does not match the inventoried and scanned image')
        reference = image + ':' + info['version'] + '-' + arch
        existing = remote_manifest(reference)
        if existing is not None and existing.get('config', {}).get('digest') != expected:
            raise ValueError('Refusing to replace a different published platform image')
        subprocess.run(['docker', 'tag', actual, reference], check=True)
        subprocess.run(['docker', 'push', reference], check=True)
        references.append(reference)
    reference = image + ':' + info['version']
    existing = remote_manifest(reference)
    if existing is not None:
        # Compare registry platform manifests before touching an immutable version.
        existing_ids = {m['digest'] for m in existing.get('manifests', [])}
        expected_ids = set()
        for ref in references:
            verbose = json.loads(run('docker', 'manifest', 'inspect', '--verbose', ref))
            expected_ids.add(verbose['Descriptor']['digest'])
        if existing_ids != expected_ids:
            raise ValueError('Refusing to replace a different published version')
    else:
        subprocess.run(['docker', 'manifest', 'create', reference, *references], check=True)
        subprocess.run(['docker', 'manifest', 'push', reference], check=True)
    # The package may default to private on first publication. A separate job
    # checks public pulls before promoting a stable release to latest.


def verify_registry(info, image):
    reference = image + ':' + info['version']
    digests = {}
    # Empty Docker configuration: no stored registry credentials.
    with tempfile.TemporaryDirectory() as config:
        env = dict(os.environ, DOCKER_CONFIG=config)
        manifest = json.loads(run('docker', 'manifest', 'inspect', '--verbose', reference, env=env))
        for arch in ARCHES:
            entry = next(m for m in manifest if m['Descriptor']['platform']['architecture'] == arch)
            immutable = image + '@' + entry['Descriptor']['digest']
            subprocess.run(['docker', 'pull', '--platform=linux/' + arch, immutable], env=env, check=True)
            expected = verify_inventory(Path('evidence') / arch, info['commit'], arch)
            actual = run('docker', 'image', 'inspect', '--format', '{{.Id}}', immutable, env=env)
            if actual != expected:
                raise ValueError('Public image differs from tested candidate')
            digests[arch] = immutable
    return digests


def verify_public(info):
    check_stable_readiness(info)
    # Verify BOTH registries before recording completion or moving ANY latest tag.
    registries = {image: verify_registry(info, image) for image in IMAGES}
    path = Path('container-digests.json')
    path.write_text(json.dumps({'tag': info['tag'], 'commit': info['commit'], 'platforms': registries[IMAGE], 'registries': registries}, indent=2) + '\n')
    ensure_asset(info, path)
    checksum = Path('container-digests.json.sha256')
    checksum.write_text(digest(path) + '  ' + path.name + '\n')
    ensure_asset(info, checksum)
    if not info['prerelease']:
        latest = json.loads(run('gh', 'api', f'repos/{REPO}/releases/latest'))
        if latest['tag_name'] == info['tag']:
            for image, digests in registries.items():
                subprocess.run(['docker', 'manifest', 'create', '--amend', image + ':latest', *digests.values()], check=True)
                subprocess.run(['docker', 'manifest', 'push', image + ':latest'], check=True)
        else:
            print('Stable release is not GitHub latest; leaving the latest image unchanged.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('validate', 'prepare', 'publish', 'verify-public', 'source-packages', 'check-readiness', 'source-fingerprint'))
    parser.add_argument('--version', help='Offline source-packages/check-readiness; does not create a release')
    parser.add_argument('--commit', help='Offline source-packages only; defaults to HEAD')
    parser.add_argument('--output', type=Path, help='New local directory for offline packages')
    args = parser.parse_args()
    command = args.command
    if command == 'source-fingerprint':
        if args.version or args.commit or args.output:
            parser.error('source-fingerprint accepts no extra options')
        commit=run('git','rev-parse','HEAD')
        print(json.dumps({'commit':commit,'source_sha256':acceptance_source_digest(commit),
                          'dirty':bool(run('git','status','--porcelain'))},indent=2))
        return
    if command == 'check-readiness':
        if args.commit or args.output:
            parser.error('check-readiness accepts only --version')
        version=args.version or json.loads((Path(__file__).resolve().parents[1]/'install/release-image.json').read_text())['version']
        if not re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+(?:-rc\.[1-9][0-9]*)?',version):
            parser.error('Expected a version such as 1.0.2 or 1.0.2-rc.1')
        try:
            check_stable_readiness({'version':version,'prerelease':'-rc.' in version,'commit':run('git','rev-parse','HEAD')})
        except ValueError as error:
            parser.exit(1,str(error)+'\n')
        print('Readiness check passed; no release, registry or installation changed.')
        return
    if command == 'source-packages':
        if not args.version or not args.output:
            parser.error('source-packages requires --version and --output')
        info = {'version': args.version, 'tag': 'v' + args.version,
                'commit': args.commit or run('git', '-c', 'safe.directory=' + str(Path.cwd().resolve()),
                                             'rev-parse', 'HEAD')}
        args.output.mkdir(parents=True, exist_ok=False)
        prepare_source_packages(info, args.output)
        paths = sorted(args.output.iterdir())
        (args.output / 'SHA256SUMS.txt').write_text(''.join(digest(p) + '  ' + p.name + '\n' for p in paths))
        print('Prepared local source/native packages only; no publication.')
        return
    if args.version or args.commit or args.output:
        parser.error('Package options are restricted to offline source-packages')
    info = current_plan()
    if command == 'prepare':
        prepare(info)
    elif command == 'publish':
        publish(info)
    elif command == 'verify-public':
        verify_public(info)
    else:
        print(json.dumps(info, indent=2))


if __name__ == '__main__':
    main()
