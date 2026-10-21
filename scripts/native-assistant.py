#!/usr/bin/env python3
"""Local package preparation and read-only native checks for the shared installer.

Never downloads source, installs OS packages, initializes private state or calls
Hue/Loxone. Lifecycle mutations remain in deployment/native/manage.py.
"""
import argparse
import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def manager(root=ROOT):
    return load('assistant_native_manager', root / 'deployment/native/manage.py')


def git(root, *args):
    return subprocess.check_output(['git', '-c', 'safe.directory=' + str(root), *args], cwd=root, text=True, stderr=subprocess.PIPE).strip()


def build_source(output, root=ROOT):
    root, output = Path(root).resolve(), Path(output).resolve()
    if Path(git(root, 'rev-parse', '--show-toplevel')).resolve() != root:
        raise ValueError('Native preparation needs the selected repository root')
    if git(root, 'status', '--porcelain', '--untracked-files=all'):
        raise ValueError('Use a clean, reviewed Git checkout; local changes were not packaged')
    commit = git(root, 'rev-parse', 'HEAD')
    version = '0.0.0-dev.' + commit[:12]
    builder = load('assistant_native_builder', root / 'scripts/build-native-package.py')
    with contextlib.redirect_stdout(io.StringIO()):
        builder.build(version, output)
    archive = output / ('hue2lox-' + version + '-native.tar.gz')
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    with tempfile.TemporaryDirectory(prefix='hue2lox-inspect-') as temporary:
        manifest = manager(root).verify_package(archive, digest, Path(temporary) / 'runtime')
    if manifest['commit'] != commit or manifest['dirty'] or git(root, 'status', '--porcelain', '--untracked-files=all'):
        raise ValueError('Source identity changed during preparation; nothing installed')
    metadata = {'package': str(archive), 'sha256': digest, 'version': version, 'commit': commit}
    (output / 'package.json').write_text(json.dumps(metadata) + '\n')
    (output / 'package.json').chmod(0o600)
    print('Development package prepared locally: ' + version + '\nCommit: ' + commit)
    return metadata


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='action', required=True)
    build = commands.add_parser('build')
    build.add_argument('--output', required=True, type=Path)
    inspect = commands.add_parser('inspect')
    inspect.add_argument('--package', required=True, type=Path)
    inspect.add_argument('--sha256', required=True)
    commands.add_parser('health')
    commands.add_parser('endpoint')
    args = parser.parse_args()
    try:
        if args.action == 'build':
            build_source(args.output)
        elif args.action == 'inspect':
            with tempfile.TemporaryDirectory(prefix='hue2lox-inspect-') as temporary:
                manifest = manager().verify_package(args.package, args.sha256, Path(temporary) / 'runtime')
            print('Verified native package: ' + manifest['version'] + '\nCommit: ' + manifest['commit'] + '\nDirty: ' + str(manifest['dirty']))
        else:
            native = manager()
            native.platform_check()
            layout = native.Layout()
            if args.action == 'endpoint':
                values = native.settings(layout)
                print(values['BIND_HOST'] + ' ' + values['PORT'])
            else:
                native.managed(layout)
                native.health(layout)
                print('Verified native HTTPS healthcheck passed.')
    except (ValueError, OSError, subprocess.SubprocessError, tarfile.TarError, KeyError) as error:
        parser.exit(1, 'Native assistant stopped: ' + str(error) + '\n')


if __name__ == '__main__':
    main()
