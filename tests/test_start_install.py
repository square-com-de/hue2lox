"""Reject incomplete/wrong installs before Docker can mutate anything."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from tests.test_install import setup

spec = importlib.util.spec_from_file_location('start_install', Path(__file__).resolve().parent.parent/'scripts/start-install.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)

class StartInstallTests(unittest.TestCase):
    def test_missing_install_never_invokes_docker(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(runner.sys, 'platform', 'linux'), patch.object(runner.os, 'geteuid', return_value=0), patch.object(runner.subprocess, 'run') as run:
            with self.assertRaisesRegex(ValueError, 'incomplete'):
                runner.start(directory)
            run.assert_not_called()

    def test_wrong_compose_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            dest = setup.prepare(Path(directory)/'test', '127.0.0.1', 18443).resolve()
            (dest/'compose.yaml').write_text('services: {}')
            with self.assertRaisesRegex(ValueError, 'not a prepared'):
                runner.preflight(dest)

    def test_explicit_paths_and_fail_fast(self):
        with tempfile.TemporaryDirectory() as directory:
            dest = setup.prepare(Path(directory)/'test', '127.0.0.1', 18443).resolve()
            with patch.object(runner.sys, 'platform', 'linux'), patch.object(runner.os, 'geteuid', return_value=0), patch.object(runner.shutil, 'which', return_value='/usr/bin/docker'), patch.object(runner.subprocess, 'run', side_effect=runner.subprocess.CalledProcessError(1, 'config')) as run:
                with self.assertRaises(runner.subprocess.CalledProcessError):
                    runner.start(dest)
                self.assertEqual(run.call_count, 1)
                command = run.call_args.args[0]
                self.assertEqual(command[command.index('-f')+1], str(dest/'compose.yaml'))
                self.assertEqual(command[command.index('--env-file')+1], str(dest/'.env'))
                self.assertEqual(run.call_args.kwargs['cwd'], dest)

    def test_success_banner_language_and_login(self):
        import contextlib
        import io
        for language, heading, username in [('de','INSTALLATION ERFOLGREICH','Benutzername: admin'),('en','INSTALLATION SUCCESSFUL','Username: admin')]:
            output=io.StringIO()
            with patch.dict(runner.os.environ, {'HUE2LOX_INSTALL_LANG':language}), contextlib.redirect_stdout(output):
                runner.print_success('https://10.200.0.163:18443')
            self.assertIn(heading,output.getvalue())
            self.assertIn(username,output.getvalue())
            self.assertIn('https://10.200.0.163:18443',output.getvalue())


class InstallationIdentityTests(unittest.TestCase):
    def test_identity_survives_repeated_reads_and_legacy_fallback(self):
        with tempfile.TemporaryDirectory() as directory:
            dest = Path(directory)
            env = dest / '.env'
            env.write_text('COMPOSE_PROJECT_NAME=hue2lox-jollyjumper\nHUE2LOX_CONTAINER_NAME=hue2lox-jollyjumper-1\n')
            before = env.read_bytes()
            self.assertEqual(runner.project_name(dest), 'hue2lox-jollyjumper')
            self.assertEqual(runner.project_name(dest), 'hue2lox-jollyjumper')
            self.assertEqual(env.read_bytes(), before)
            env.write_text('HUE2LOX_PORT=18443\n')
            self.assertEqual(runner.project_name(dest), 'hue2lox-test')
            env.write_text('COMPOSE_PROJECT_NAME=unrelated-project\n')
            with self.assertRaises(ValueError): runner.project_name(dest)

    def test_project_collision_is_rejected_and_own_container_allowed(self):
        import json
        from subprocess import CompletedProcess
        with tempfile.TemporaryDirectory() as directory:
            dest = Path(directory).resolve()
            for owner, allowed in [(str(dest), True), ('/some/other/installation', False), (None, False)]:
                containers = [{'Config': {'Labels': {'com.docker.compose.project.working_dir': owner}}}]
                results = [CompletedProcess([], 0, 'abc123\n'), CompletedProcess([], 0, json.dumps(containers))]
                with patch.object(runner.subprocess, 'run', side_effect=results):
                    if allowed:
                        runner.check_project_owner(dest, 'hue2lox-jollyjumper')
                    else:
                        with self.assertRaisesRegex(ValueError, 'another directory'):
                            runner.check_project_owner(dest, 'hue2lox-jollyjumper')
