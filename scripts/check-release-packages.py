#!/usr/bin/env python3
"""Test unpublished source/native assets from one commit on isolated empty state."""
import argparse
import hashlib
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parent.parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--version', default='1.0.0')
    parser.add_argument('--docker', action='store_true', help='Disposable CI runner/root only')
    args = parser.parse_args()
    if args.docker and (os.environ.get('CI') != 'true' or os.getuid() != 0):
        parser.error('--docker requires root on a disposable CI runner')
    with tempfile.TemporaryDirectory(prefix='hue2lox-package-check-') as temporary:
        work = Path(temporary)
        packages = work / 'packages'
        subprocess.run([sys.executable, '-B', str(ROOT / 'scripts/release-image.py'), 'source-packages',
                        '--version', args.version, '--output', str(packages)], cwd=ROOT, check=True)
        for line in (packages / 'SHA256SUMS.txt').read_text().splitlines():
            expected, name = line.split('  ')
            assert hashlib.sha256((packages / name).read_bytes()).hexdigest() == expected
        with zipfile.ZipFile(packages / f'hue2lox-v{args.version}.zip') as archive:
            prefix = f'hue2lox-v{args.version}/'
            assert archive.testzip() is None
            assert all(name.startswith(prefix) and '..' not in Path(name).parts for name in archive.namelist())
            archive.extractall(work / 'source')
        source = work / 'source' / f'hue2lox-v{args.version}'
        subprocess.run([sys.executable, '-B', str(source / 'scripts/smoke-install.py')], cwd=source, check=True)
        native = packages / f'hue2lox-{args.version}-native.tar.gz'
        checksum = hashlib.sha256(native.read_bytes()).hexdigest()
        subprocess.run([sys.executable, '-B', str(ROOT / 'scripts/smoke-native.py'),
                        '--package', str(native), '--sha256', checksum], check=True)
        # The source ZIP has no Git identity. It must accept the supplied native
        # archive, not synthesize a commit or fetch mutable main.
        subprocess.run([sys.executable, '-B', str(source / 'scripts/native-assistant.py'), 'inspect',
                        '--package', str(native), '--sha256', checksum], cwd=source, check=True)
        print('PASS: source ZIP and native archive, checksum, ZIP-based native handoff and actual HTTPS/password/restart tests.')
        if args.docker:
            subprocess.run(['sh', str(source / 'scripts/ci-container.sh')], cwd=source, check=True)
            print('PASS: Docker built and exercised from the release source ZIP; no registry publication or hardware access.')


if __name__ == '__main__':
    main()
