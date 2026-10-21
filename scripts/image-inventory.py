"""Read an image's package/license metadata without initializing Hue2Lox.

Run inside the exact candidate image with --network none and a read-only filesystem.
The output is evidence for review, not a declaration of license compliance.
"""
import hashlib
import importlib.metadata
import json
import platform
from pathlib import Path
import re
import sys


def apk_packages(text):
    result = []
    for block in text.split('\n\n'):
        fields = {}
        for line in block.splitlines():
            if len(line) > 1 and line[1] == ':':
                fields.setdefault(line[0], line[2:])
        if 'P' not in fields:
            continue
        result.append({key: fields.get(field) for key, field in {
            'name': 'P', 'version': 'V', 'license': 'L', 'origin': 'o',
            'source_commit': 'c', 'architecture': 'A', 'homepage': 'U'}.items()})
    return sorted(result, key=lambda package: package['name'])


def inventory():
    database = Path('/lib/apk/db/installed')
    if not database.is_file():
        raise SystemExit('Expected the Alpine package database in the candidate image')
    files = {}
    roots = [Path('/usr/share/licenses'), Path('/usr/local/lib/python3.12'), Path('/app')]
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob('*'):
            name = path.name.lower()
            if path.is_symlink() or not path.is_file():
                continue
            if not (name.startswith(('license', 'licence', 'copying', 'copyright', 'notice'))
                    or name in ('third-party-notices.md', 'vendor.txt')):
                continue
            data = path.read_bytes()
            files[str(path)] = {'sha256': hashlib.sha256(data).hexdigest(),
                                'text': data.decode('utf-8', errors='replace')}
    python_packages = []
    for dist in importlib.metadata.distributions():
        python_packages.append({'name': dist.metadata['Name'], 'version': dist.version,
                                'license': dist.metadata.get('License-Expression') or dist.metadata.get('License'),
                                'license_files': dist.metadata.get_all('License-File', [])})
    vendored = []
    for vendor in Path('/usr/local/lib/python3.12').rglob('vendor.txt'):
        for line in vendor.read_text().splitlines():
            match = re.match(r'\s*([\w.-]+)==([^\s;#]+)', line)
            if match:
                vendored.append({'name': match[1], 'version': match[2], 'manifest': str(vendor)})
    return {'schema_version': 1, 'review_status': 'not-approved-for-distribution',
            'architecture': platform.machine(), 'python_version': platform.python_version(),
            'alpine_version': Path('/etc/alpine-release').read_text().strip(),
            'apk_packages': apk_packages(database.read_text()), 'python_packages': python_packages,
            'vendored_packages': vendored, 'license_files': files}


if __name__ == '__main__':
    json.dump(inventory(), sys.stdout, indent=2, sort_keys=True)
    print()
