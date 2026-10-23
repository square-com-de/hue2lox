import importlib.util
import os
import subprocess
import sys
from pathlib import Path
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location('recover_control', Path(__file__).resolve().parents[1] / 'scripts/recover-control-flags.py')
recovery = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(recovery)


class ControlRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.previous_umask = os.umask(0o077)
        self.addCleanup(os.umask, self.previous_umask)

    def test_cli_requires_explicit_opt_in_and_check_never_discloses_other_settings(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary).resolve() / '.env'
            original = 'PRIVATE_TEST_VALUE=fixture-not-for-output\n' + ''.join(flag + '=0\n' for flag in recovery.FLAGS)
            path.write_text(original)
            command = [sys.executable, str(Path(recovery.__file__)), '--settings', str(path)]
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            result = subprocess.run(command + ['--check'], capture_output=True, text=True, check=True)
            self.assertNotIn('fixture-not-for-output', result.stdout + result.stderr)
            self.assertEqual(path.read_text(), original)
            result = subprocess.run(command + ['--enable-supported-control'], capture_output=True, text=True, check=True)
            self.assertNotIn('fixture-not-for-output', result.stdout + result.stderr)
            self.assertEqual(set(recovery.inspect(path)[4].values()), {'1'})

    def test_explicit_correction_preserves_other_bytes_modes_and_private_backup(self):
        for filename, mode in (('.env', 0o600), ('settings.env', 0o640)):
            with self.subTest(filename=filename), tempfile.TemporaryDirectory() as temporary:
                path = Path(temporary).resolve() / filename
                original = b'# retained\r\nOPERATOR_SETTING=keep\r\n' + b''.join((flag + '=0\r\n').encode() for flag in recovery.FLAGS)
                path.write_bytes(original)
                path.chmod(mode)
                before = path.stat()
                self.assertEqual(set(recovery.inspect(path)[4].values()), {'0'})
                self.assertEqual(path.read_bytes(), original)
                values, backup = recovery.enable(path)
                self.assertEqual(set(values.values()), {'1'})
                self.assertEqual(path.read_bytes(), original.replace(b'_ENABLED=0', b'_ENABLED=1'))
                self.assertEqual(backup.read_bytes(), original)
                self.assertEqual(backup.stat().st_mode & 0o777, 0o600)
                self.assertEqual((path.stat().st_mode & 0o777, path.stat().st_uid, path.stat().st_gid),
                                 (mode, before.st_uid, before.st_gid))
                self.assertIsNone(recovery.enable(path)[1])

    def test_ambiguous_missing_or_symbolic_settings_are_never_changed(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            path = root / '.env'
            valid = ''.join(flag + '=0\n' for flag in recovery.FLAGS)
            for content in (valid + recovery.FLAGS[0] + '=1\n', valid.replace('=0', '="0"'), 'OTHER=retained\n'):
                path.write_text(content)
                with self.assertRaises(ValueError):
                    recovery.enable(path)
                self.assertEqual(path.read_text(), content)
                self.assertEqual(list(root.glob('*.controls-before-*')), [])
            path.unlink()
            target = root / 'original'
            target.write_text(valid)
            path.symlink_to(target)
            with self.assertRaises(ValueError):
                recovery.enable(path)
            self.assertEqual(target.read_text(), valid)
