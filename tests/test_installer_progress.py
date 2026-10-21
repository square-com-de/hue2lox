"""Exercise progress with real child processes, including prompts and failures."""
import os
from pathlib import Path
import pty
import select
import subprocess
import sys
import tempfile
import time
import unittest

HELPER = Path(__file__).resolve().parent.parent / 'scripts/installer_progress.py'


class ProgressTests(unittest.TestCase):
    runner = [sys.executable, str(HELPER)]
    success = '✓ Test step'
    def invoke(self, code, input_text=''):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        env = dict(os.environ, TMPDIR=directory.name, HUE2LOX_INSTALL_LANG='en')
        result = subprocess.run(self.runner + ['Test step', sys.executable, '-c', code],
                                input=input_text, text=True, capture_output=True, env=env, timeout=10)
        logs = list(Path(directory.name).rglob('*.log'))
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0].stat().st_mode & 0o777, 0o600)
        return result, logs[0].read_text()

    def test_success_hides_noise_and_filters_credentials(self):
        result, log = self.invoke("print('ordinary progress'); print('Authorization: Bearer test-secret'); print('-----BEGIN PRIVATE KEY-----'); print('private-material'); print('-----END PRIVATE KEY-----')")
        self.assertEqual(result.returncode, 0)
        self.assertNotIn('ordinary progress', result.stdout)
        self.assertIn('ordinary progress', log)
        self.assertNotIn('test-secret', log + result.stdout)
        self.assertNotIn('private-material', log + result.stdout)
        self.assertIn(self.success, result.stdout)
        self.assertNotIn('\x1b', result.stdout)

    def test_failure_retains_status_and_shows_cause(self):
        result, log = self.invoke("print('disk full'); raise SystemExit(42)")
        self.assertEqual(result.returncode, 42)
        self.assertIn('disk full', result.stdout)
        self.assertTrue('Failed:' in result.stdout or '[ERROR]' in result.stdout)
        self.assertNotIn('✓', result.stdout)

    def test_prompt_visible_before_answer_and_animation_uses_terminal(self):
        with tempfile.TemporaryDirectory() as directory:
            master, slave = pty.openpty()
            env = dict(os.environ, TMPDIR=directory, TERM='xterm', HUE2LOX_INSTALL_LANG='en')
            child = subprocess.Popen(self.runner + ['Test step', sys.executable, '-c',
                                      "import time; time.sleep(.3); answer=input('Continue [Y/n]: '); print('answer='+answer)"],
                                     stdin=slave, stdout=slave, stderr=slave, env=env)
            os.close(slave)
            output = b''
            try:
                deadline = time.monotonic() + 7
                while b'Continue [Y/n]:' not in output and time.monotonic() < deadline:
                    if select.select([master], [], [], .2)[0]:
                        output += os.read(master, 65536)
                self.assertIn(b'Continue [Y/n]:', output)
                self.assertIn(b'( o  o )', output)
                os.write(master, b'y\n')
                self.assertEqual(child.wait(timeout=5), 0)
                log = next(Path(directory).rglob('*.log')).read_text()
                self.assertIn('answer=y', log)
            finally:
                if child.poll() is None:
                    child.kill(); child.wait()
                os.close(master)


class BootstrapProgressTests(ProgressTests):
    runner = ['bash', str(HELPER.with_name('installer_bootstrap.sh'))]
    success = '[OK] Test step'
