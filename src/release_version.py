"""Installed build identity; no network lookups or mutable application state."""
import argparse
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
VERSION = r'[0-9]+\.[0-9]+\.[0-9]+(?:-[A-Za-z0-9][A-Za-z0-9.-]*)?'
REVISION = r'[0-9a-f]{40}'


def build_identity(version='', revision=''):
    if revision and not re.fullmatch(REVISION, revision):
        raise ValueError('Invalid build revision')
    if version and (not re.fullmatch(VERSION, version) or not revision):
        raise ValueError('A release build needs a safe version and exact revision')
    return {'schema_version': 1, 'version': version or None,
            'revision': revision or None, 'kind': 'release' if version else 'development'}


def installed_version(root=None):
    root = ROOT if root is None else Path(root)
    # Native package manifests describe the actual installed package. A dirty
    # package is explicitly a development build, even if its version looks stable.
    native = root / 'manifest.json'
    if native.exists():
        try:
            data = json.loads(native.read_text())
            version, commit, dirty = data['version'], data['commit'], data['dirty']
            if (not isinstance(version, str) or not re.fullmatch(VERSION, version)
                    or not isinstance(commit, str) or not re.fullmatch(REVISION, commit)
                    or type(dirty) is not bool):
                return None
            return 'Hue2Lox ' + version if not dirty else 'Hue2Lox · Entwicklungsbuild'
        except (OSError, ValueError, KeyError, TypeError):
            return None
    try:
        data = json.loads((root / 'build-info.json').read_text())
        if not isinstance(data, dict) or type(data.get('schema_version')) is not int or data['schema_version'] != 1:
            return None
        expected = build_identity(data.get('version') or '', data.get('revision') or '')
        if data != expected:
            return None
        return ('Hue2Lox ' + data['version'] if data['kind'] == 'release'
                else 'Hue2Lox · Entwicklungsbuild')
    except (OSError, ValueError, KeyError, TypeError):
        return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-build', type=Path, required=True)
    parser.add_argument('--version', default='')
    parser.add_argument('--revision', default='')
    args = parser.parse_args()
    data = build_identity(args.version, args.revision)
    if args.version:
        # The publication workflow independently checks tag/commit binding.
        if json.loads((ROOT / 'install/release-image.json').read_text())['version'] != args.version:
            parser.error('Build version does not match release metadata')
    args.write_build.write_text(json.dumps(data, sort_keys=True) + '\n')


if __name__ == '__main__':
    main()
