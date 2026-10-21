#!/usr/bin/env python3
"""Assemble checked third-party sources and notices; never execute upstream code."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import tarfile
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
LOCKS = ROOT / 'compliance'


def read(name):
    return json.loads((LOCKS / name).read_text())


def safe_path(value):
    p = PurePosixPath(value)
    if p.is_absolute() or '..' in p.parts or not p.parts or '\\' in value:
        raise ValueError(f'Unsafe archive path: {value}')
    return p


def source_jobs():
    jobs = []
    for row in read('recipes.json'):
        if not row.get('directory_complete'):
            raise ValueError('Incomplete recipe: ' + row['origin'])
        for f in row['recipe_files']:
            jobs.append((f"recipes/{row['origin']}/{f['name']}",
                         row['url'].rsplit('/', 1)[0] + '/' + f['name'], 'sha256', f['sha256']))
    for row in read('source-checksums.json'):
        jobs.append((f"sources/{row['origin']}/{row['name']}", row['url'], 'sha512', row['sha512']))
    for row in read('python-sources.json'):
        jobs.append((f"sources/{row['name']}/{row['url'].rsplit('/', 1)[1]}", row['url'], 'sha256', row['sha256']))
    for row in read('supplements.json'):
        jobs.append((row['path'], row['url'], 'sha256', row['sha256']))
    for name, url, algorithm, digest in jobs:
        safe_path(name)
        if not url.startswith('https://') or not re.fullmatch('[0-9a-f]+', digest):
            raise ValueError('Invalid source lock: ' + name)
    if len({j[0] for j in jobs}) != len(jobs):
        raise ValueError('Duplicate source destination')
    return jobs


def fetch(job, output, cache=None):
    name, url, algorithm, expected = job
    candidate = cache / name if cache else None
    if candidate and candidate.is_file():
        data = candidate.read_bytes()
    else:
        with urllib.request.urlopen(url, timeout=120) as response:
            data = response.read()
    if hashlib.new(algorithm, data).hexdigest() != expected:
        raise ValueError('Checksum mismatch: ' + name)
    target = output / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)


def check_recipe_inputs(output):
    """Also match old APKBUILDs with sha512sums=\"hash filename\" on one line."""
    locked = {(r['origin'], r['name']): r['sha512'] for r in read('source-checksums.json')}
    for recipe in (output / 'recipes').glob('*/APKBUILD'):
        for digest, name in re.findall(r'([0-9a-f]{128})\s+([^\s"\x27]+)', recipe.read_text()):
            if locked.get((recipe.parent.name, name)) != digest:
                raise ValueError('Missing/mismatched APKBUILD input: ' + recipe.parent.name + '/' + name)


def extract_notices(output):
    # No extractall, links or special files: copy only regular notice text.
    notices = {}
    for archive in sorted((output / 'sources').glob('*/*')):
        if not tarfile.is_tarfile(archive):
            continue
        origin = archive.parent.name
        with tarfile.open(archive) as tf:
            for member in tf:
                leaf = PurePosixPath(member.name).name.lower()
                include = leaf.startswith(('license', 'licence', 'copying', 'notice', 'copyright')) or leaf == 'authors.txt'
                include |= origin == 'ca-certificates' and leaf in ('certdata.txt', 'c_rehash.c')
                if not member.isfile() or not include:
                    continue
                relative = safe_path(member.name)
                dest = output / 'licenses' / origin / archive.name / relative
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(tf.extractfile(member).read())
                notices.setdefault(origin, []).append(dest.relative_to(output).as_posix())
    return notices


def parse_vendors(text):
    return re.findall(r'^\s*([A-Za-z0-9_-]+)==([^\s#]+)', text, re.M)


def verify_inventory(records, inventory, arch):
    def pairs(rows):
        return {(r['name'].lower().replace('_', '-'), r['version']) for r in rows}
    expected = [r for r in records if r.get('platform') == 'linux/' + arch]
    if pairs(expected) != pairs(inventory['apk_packages']):
        raise ValueError('Runtime APK inventory differs from source bundle: ' + arch)
    expected_vendor = [r for r in records if r.get('kind') == 'pip-vendored']
    if pairs(expected_vendor) != pairs(inventory['vendored_packages']):
        raise ValueError('Runtime vendored inventory differs from source bundle: ' + arch)
    expected_pip = [r for r in records if r['name'] == 'pip']
    if pairs(expected_pip) != pairs(inventory['python_packages']):
        raise ValueError('Runtime Python package inventory differs: ' + arch)
    version = next(r['version'] for r in records if r['name'] == 'python')
    if inventory['python_version'] != version:
        raise ValueError('Runtime Python version differs: ' + arch)


def component_map(output, notices):
    records = []
    generated = {'alpine-base', 'alpine-keys', 'alpine-baselayout', 'krb5-conf'}
    for arch in ('amd64', 'arm64'):
        for package in read(arch + '-base-packages.json'):
            row = dict(package)
            row['platform'] = 'linux/' + arch
            origin = row.get('origin')
            if row['name'] == '.python-rundeps':
                row.update(source_files=[], license_files=[], note='Virtual dependency record; no separate payload.')
            else:
                files = sorted((output / 'sources' / origin).glob('*'))
                recipes = sorted((output / 'recipes' / origin).rglob('*'))
                row['source_files'] = [p.relative_to(output).as_posix() for p in files + recipes if p.is_file()]
                row['license_files'] = list(notices.get(origin, []))
                if origin in generated:
                    row['license_files'].append('supplements/GPL-2.0-only.txt' if origin == 'alpine-baselayout' else 'supplements/MIT.txt')
                    row['note'] = 'License declared in exact APKBUILD. Complete original recipe/data retained; upstream supplies no separate copyright notice. No holder is inferred from maintainer names.'
                if origin == 'ca-certificates':
                    row['license_files'] += ['supplements/MIT.txt', 'supplements/MPL-2.0.txt']
                    row['note'] = 'Full certdata.txt MPL notice and c_rehash.c copyright header retained with complete license texts and original source archive.'
                if not row['source_files'] or not row['license_files']:
                    raise ValueError('Unmapped runtime package: ' + row['name'])
            records.append(row)
    for name, version in (('python', '3.12.15'), ('pip', '25.0.1'), ('typing_extensions', '4.12.2')):
        records.append(dict(name=name, version=version, platforms=['linux/amd64', 'linux/arm64'],
                            source_files=[p.relative_to(output).as_posix() for p in (output / 'sources' / name).glob('*')],
                            license_files=notices[name]))
    pip_archive = next((output / 'sources/pip').glob('*.tar.gz'))
    with tarfile.open(pip_archive) as tf:
        manifest = next(m for m in tf if m.name.endswith('/pip/_vendor/vendor.txt'))
        text = tf.extractfile(manifest).read().decode()
    aliases = {'pyproject-hooks': 'pyproject_hooks', 'setuptools': 'pkg_resources'}
    for name, version in parse_vendors(text):
        directory = aliases.get(name.lower(), name.lower())
        paths = notices['typing_extensions'] if directory == 'typing_extensions' else [p for p in notices['pip'] if '/_vendor/' + directory + '/' in p]
        if not paths:
            raise ValueError('Missing vendored notice: ' + name)
        records.append(dict(name=name, version=version, kind='pip-vendored', source_files=[pip_archive.relative_to(output).as_posix()], license_files=paths))
    for row in records:
        for name in row['source_files'] + row['license_files']:
            if not (output / safe_path(name)).is_file():
                raise ValueError('Missing mapped file: ' + name)
    return records


def assemble(output, cache=None, evidence=None):
    output.mkdir(parents=True, exist_ok=False)
    with ThreadPoolExecutor(max_workers=6) as pool:
        list(pool.map(lambda job: fetch(job, output, cache), source_jobs()))
    check_recipe_inputs(output)
    notices = extract_notices(output)
    records = component_map(output, notices)
    if evidence:
        for arch in ('amd64', 'arm64'):
            inventory = json.loads((evidence / arch / 'inventory.json').read_text())
            verify_inventory(records, inventory, arch)
            shutil.copytree(evidence / arch, output / 'image-evidence' / arch)
    (output / 'component-map.json').write_text(json.dumps(records, indent=2) + '\n')
    shutil.copytree(LOCKS, output / 'provenance')
    shutil.copyfile(ROOT / 'docs/CONTAINER-SOURCES.md', output / 'README.md')
    index = ['# Runtime component and notice index', '', 'Original license/copyright texts are retained at the listed paths. Complete source archives preserve notices in source headers as well.', '']
    for row in records:
        index += [f"## {row['name']} {row['version']} ({row.get('platform', row.get('kind', 'both platforms'))})", '', row.get('note', ''), '', 'Sources/build recipes:']
        index += ['- ' + p for p in row['source_files']]
        index += ['', 'License and copyright texts:'] + ['- ' + p for p in row['license_files']] + ['']
    (output / 'NOTICES.md').write_text('\n'.join(index))
    files = sorted(p for p in output.rglob('*') if p.is_file())
    (output / 'SHA256SUMS.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest() + '  ' + p.relative_to(output).as_posix() + '\n' for p in files))
    archive = output.with_name(output.name + '.tar.gz')
    with tarfile.open(archive, 'w:gz') as tf:
        tf.add(output, arcname=output.name)
    archive.with_name(archive.name + '.sha256').write_text(hashlib.sha256(archive.read_bytes()).hexdigest() + '  ' + archive.name + '\n')
    print(f'PASS: {len(records)} component records; {len(source_jobs())} verified inputs; {archive}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True, help='New directory (must not exist)')
    parser.add_argument('--cache', type=Path, help='Optional local source cache; all hashes are still checked')
    parser.add_argument('--evidence', type=Path, help='Directory with amd64/ and arm64/ built-image inventories to check')
    args = parser.parse_args()
    assemble(args.output, args.cache, args.evidence)
