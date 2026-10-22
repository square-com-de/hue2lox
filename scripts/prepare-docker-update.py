#!/usr/bin/env python3
"""Stage a Docker update beside a stopped installer deployment; never start it."""
import argparse
import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from installer_messages import message, localized_print as print


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def stage(destination, candidate, source, registry='dockerhub'):
    if os.geteuid() != 0:
        raise ValueError('Run this command with sudo on Linux.')
    original = Path(destination).absolute()
    candidate = Path(candidate).absolute()
    if original.is_symlink() or candidate.is_symlink() or original.resolve() != original or candidate.parent.resolve() != candidate.parent:
        raise ValueError('Refuse links in private state/configuration')
    if candidate.exists() or candidate.parent != original.parent or candidate == original:
        raise ValueError('Candidate must be a new sibling of the existing installation')
    runner = load('docker_update_start', 'start-install.py')
    prepare = load('docker_update_prepare', 'prepare-install.py')
    old, _, _ = runner.preflight(original)
    old_source, old_image = runner.installation_source(old)
    template = (old / 'docker/compose.install.yaml').read_text()
    if old_source == 'image':
        start, end = template.index('    build:\n'), template.index('    restart:')
        template = template[:start] + '    image: ' + old_image + '\n' + template[end:]
    if dict(line.split('=', 1) for line in (old / '.env').read_text().splitlines() if '=' in line).get('HUE2LOX_SCHEME', 'https') == 'http':
        template = '\n'.join(line for line in template.split('\n') if not any(
            marker in line for marker in ('      TLS_CERT:', '      TLS_KEY:', '      - ./certs:')))
    if (old / 'compose.yaml').read_text() != template:
        raise ValueError('Custom Compose file; review and migrate it manually before updating')
    command = ['docker', 'compose', '--project-directory', str(old), '--env-file', str(old / '.env'),
               '-f', str(old / 'compose.yaml'), '-p', runner.project_name(old)]
    result = subprocess.run(command + ['ps', '--status', 'running', '-q'], check=True,
                            text=True, stdout=subprocess.PIPE)
    if result.stdout.strip():
        raise ValueError('Stop this Compose installation before staging its private data')
    values = dict(line.split('=', 1) for line in (old / '.env').read_text().splitlines()
                  if line and not line.startswith('#') and '=' in line)
    if any(p.is_symlink() for name in ('data', 'certs', 'secrets') for p in (old / name).rglob('*')):
        raise ValueError('Refuse links in private state/configuration')
    for name in ('data', 'secrets', 'certs'):
        if (old / name).is_symlink():
            raise ValueError('Refuse links in private state/configuration')
    scheme = values.get('HUE2LOX_SCHEME', 'https')
    owned = False
    try:
        prepare.prepare(candidate, values['HUE2LOX_BIND_IP'], int(values['HUE2LOX_PORT']),
                        scheme, values['HUE_PUBLIC_URL'], source, registry)
        owned = True
        target = dict(line.split('=', 1) for line in (candidate / '.env').read_text().splitlines() if '=' in line)
        # Preserve identity, endpoint, private paths and all feature settings. Only the
        # explicitly selected deployment source changes. Never evaluate .env as shell.
        values.pop('HUE2LOX_IMAGE', None)
        values['HUE2LOX_SOURCE'] = target['HUE2LOX_SOURCE']
        if 'HUE2LOX_IMAGE' in target:
            values['HUE2LOX_IMAGE'] = target['HUE2LOX_IMAGE']
        (candidate / '.env').write_text(''.join(f'{key}={value}\n' for key, value in values.items()))
        (candidate / '.env').chmod(0o600)
        for name in ('data', 'secrets', 'certs', 'health-test.crt'):
            src, dst = old / name, candidate / name
            if dst.is_dir(): shutil.rmtree(dst)
            elif dst.exists(): dst.unlink()
            if src.exists():
                subprocess.run(['cp', '-a', str(src), str(dst)], check=True)
        runner.preflight(candidate)
        runner.installation_source(candidate)
    except BaseException:
        # Only this newly created staging directory is cleaned; never the original.
        if owned and candidate.exists(): shutil.rmtree(candidate)
        raise
    print('Docker update candidate prepared: ' + str(candidate))
    print('Original installation unchanged. Build/pull, switch directories and verify health as documented.')
    return candidate


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--destination', required=True, type=Path)
    parser.add_argument('--candidate', required=True, type=Path)
    parser.add_argument('--source', required=True, choices=('build', 'image'))
    parser.add_argument('--registry', default='dockerhub', choices=('dockerhub', 'ghcr'))
    args = parser.parse_args()
    try:
        stage(args.destination, args.candidate, args.source, args.registry)
    except (ValueError, OSError, KeyError, subprocess.SubprocessError) as error:
        parser.exit(1, message('Docker update preparation stopped: ' + str(error)) + '\n')
