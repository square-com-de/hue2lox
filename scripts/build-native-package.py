#!/usr/bin/env python3
"""Build an allowlisted native source package; never publishes or includes state."""
import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import tarfile

ROOT = Path(__file__).resolve().parent.parent
TREES = ('src', 'web', 'catalog', 'trust', 'config', 'deployment/native')
FILES = ('LICENSE', 'NOTICE', 'THIRD-PARTY-NOTICES.md', 'scripts/prepare-state.py',
         'docs/INSTALL-NATIVE.md', 'docs/INSTALL-NATIVE.en.md', 'docs/NATIVE-VM-ACCEPTANCE.md', 'install-assistant.sh',
         'scripts/native-assistant.py', 'scripts/native-menu.sh', 'scripts/installer_progress.py', 'scripts/installer_bootstrap.sh')


def build(version, output):
    if not re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+(?:-[A-Za-z0-9][A-Za-z0-9.-]*)?', version):
        raise ValueError('Version must be a safe version such as 1.2.3 or 1.2.3-rc.1')
    commit = subprocess.check_output(['git', '-c', 'safe.directory=' + str(ROOT), 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    dirty = bool(subprocess.check_output(['git', '-c', 'safe.directory=' + str(ROOT), 'status', '--porcelain', '--untracked-files=all'], cwd=ROOT))
    paths = []
    for name in TREES:
        base = ROOT / name
        if not base.is_dir() or base.is_symlink():
            raise ValueError(f'Missing or symbolic package directory: {name}')
        for path in sorted(base.rglob('*')):
            if path.is_symlink():
                raise ValueError(f'Symbolic links are forbidden: {path.relative_to(ROOT)}')
            if '__pycache__' in path.parts or path.suffix in ('.pyc', '.pyo'):
                continue
            if path.is_file():
                paths.append(path)
            elif not path.is_dir():
                raise ValueError(f'Unsupported package entry: {path.relative_to(ROOT)}')
    paths.extend(ROOT / name for name in FILES)
    content = {}
    for path in sorted(paths):
        if not path.is_file() or path.is_symlink():
            raise ValueError(f'Missing or symbolic package file: {path.relative_to(ROOT)}')
        content[path.relative_to(ROOT).as_posix()] = path.read_bytes()
    manifest = {'schema_version': 1, 'version': version, 'commit': commit, 'dirty': dirty,
                'files': {name: hashlib.sha256(data).hexdigest() for name, data in content.items()}}
    content['manifest.json'] = (json.dumps(manifest, indent=2, sort_keys=True) + '\n').encode()
    output.mkdir(parents=True, exist_ok=True)
    archive = output / f'hue2lox-{version}-native.tar.gz'
    with archive.open('wb') as raw, gzip.GzipFile(filename='', mode='wb', fileobj=raw, mtime=0) as compressed:
        with tarfile.open(fileobj=compressed, mode='w') as tar:
            for name, data in sorted(content.items()):
                info = tarfile.TarInfo('hue2lox-native/' + name)
                info.size = len(data)
                info.mode = 0o755 if name.startswith('deployment/native/') and name.endswith('.sh') else 0o644
                tar.addfile(info, io.BytesIO(data))
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    checksums = ''.join(f'{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}\n'
                        for path in sorted(output.glob('hue2lox-*-native.tar.gz')) if path.is_file() and not path.is_symlink())
    (output / 'SHA256SUMS').write_text(checksums)
    print(f'{archive}\nSHA256 {digest}\nCommit {commit}; dirty={dirty}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--version', required=True)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    try:
        build(args.version, args.output.resolve())
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        parser.exit(1, f'Package build failed: {error}\n')
