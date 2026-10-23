"""Cold staging preserves state/identity and refuses live/custom deployments."""
import importlib.util
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from tests.test_install import setup

spec = importlib.util.spec_from_file_location('docker_update', Path(__file__).resolve().parents[1] / 'scripts/prepare-docker-update.py')
update = importlib.util.module_from_spec(spec)
spec.loader.exec_module(update)


class DockerUpdateTests(unittest.TestCase):
    def test_cold_stage_preserves_private_bytes_modes_identity_and_flags(self):
        real_run = subprocess.run
        for source in ('build', 'image'):
            with self.subTest(source=source), tempfile.TemporaryDirectory() as temp:
                old = setup.prepare(Path(temp).resolve()/'old', '127.0.0.1', source='build')
                values = (old/'.env').read_text() + 'LOCAL_OPERATOR_SETTING=retained\n'
                for flag in ('WRITES', 'COLOR', 'WHITE'):
                    values = values.replace(f'HUE_{flag}_ENABLED=1', f'HUE_{flag}_ENABLED=0')
                (old/'.env').write_text(values)
                private = {str(p.relative_to(old)): (p.read_bytes(), p.stat().st_mode & 0o777)
                           for folder in ('data', 'secrets', 'certs') for p in (old/folder).rglob('*') if p.is_file()}
                def run(args, **kwargs):
                    if args[0] == 'docker': return subprocess.CompletedProcess(args, 0, stdout='')
                    return real_run(args, **kwargs)
                candidate = old.with_name('candidate')
                with patch.object(update.os, 'geteuid', return_value=0), patch.object(update.subprocess, 'run', side_effect=run):
                    # avoid changing actual file owners in this portable unit test
                    with patch('os.chown'):
                        update.stage(old, candidate, source, 'ghcr')
                for name, (content, mode) in private.items():
                    self.assertEqual((candidate/name).read_bytes(), content)
                    self.assertEqual((candidate/name).stat().st_mode & 0o777, mode)
                    self.assertEqual((old/name).read_bytes(), content)
                env = dict(line.split('=',1) for line in (candidate/'.env').read_text().splitlines())
                for flag in ('WRITES', 'COLOR', 'WHITE'):
                    self.assertEqual(env[f'HUE_{flag}_ENABLED'], '0')
                self.assertEqual(env['LOCAL_OPERATOR_SETTING'], 'retained')
                old_env = dict(line.split('=',1) for line in values.splitlines())
                self.assertEqual(env['COMPOSE_PROJECT_NAME'], old_env['COMPOSE_PROJECT_NAME'])
                self.assertEqual(env['HUE_PUBLIC_URL'], old_env['HUE_PUBLIC_URL'])
                self.assertEqual(env['HUE2LOX_SOURCE'], source)
                self.assertEqual((old/'.env').read_text(), values)
                self.assertEqual('    build:' in (candidate/'compose.yaml').read_text(), source=='build')

    def test_live_or_custom_installation_is_refused_before_candidate_created(self):
        with tempfile.TemporaryDirectory() as temp:
            old = setup.prepare(Path(temp).resolve()/'old', '127.0.0.1')
            candidate = old.with_name('candidate')
            with patch.object(update.os,'geteuid',return_value=0), patch.object(update.subprocess,'run',return_value=subprocess.CompletedProcess([],0,stdout='container-id')):
                with self.assertRaisesRegex(ValueError,'Stop this Compose'): update.stage(old,candidate,'image')
            self.assertFalse(candidate.exists())
            with (old/'compose.yaml').open('a') as stream: stream.write('# custom operator configuration\n')
            with patch.object(update.os,'geteuid',return_value=0):
                with self.assertRaisesRegex(ValueError,'Custom Compose'): update.stage(old,candidate,'image')
            self.assertFalse(candidate.exists())

    def test_existing_candidate_is_never_removed(self):
        with tempfile.TemporaryDirectory() as temp:
            old=Path(temp)/'old'; candidate=Path(temp)/'candidate'; candidate.mkdir()
            marker=candidate/'keep';marker.write_text('operator data')
            with patch.object(update.os,'geteuid',return_value=0):
                with self.assertRaises(ValueError):update.stage(old,candidate,'build')
            self.assertEqual(marker.read_text(),'operator data')
