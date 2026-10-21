"""Offline native package integrity and allowlist checks; no installers execute."""
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tarfile
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location('native_package', Path(__file__).resolve().parents[1] / 'scripts/build-native-package.py')
package = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(package)


class NativePackageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'source'
        self.output = Path(self.temp.name) / 'output'
        for name in package.TREES:
            directory = self.root / name
            directory.mkdir(parents=True, exist_ok=True)
            (directory / 'example.txt').write_text('public runtime asset\n')
        for name in package.FILES:
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('runtime helper or license\n')
        (self.root / '.env').write_text('DO_NOT_PACKAGE=secret')
        (self.root / 'secrets').mkdir()
        (self.root / 'secrets/private.key').write_text('not a real key')
        (self.root / 'src/__pycache__').mkdir()
        (self.root / 'src/__pycache__/cache.pyc').write_bytes(b'cache')
        self.root_patch = patch.object(package, 'ROOT', self.root)
        self.root_patch.start()
        self.addCleanup(self.root_patch.stop)
        self.git_patch = patch.object(package.subprocess, 'check_output', side_effect=self.git_output)
        self.git_patch.start()
        self.addCleanup(self.git_patch.stop)

    @staticmethod
    def git_output(command, **kwargs):
        return ('a' * 40 + '\n') if 'rev-parse' in command else b' M src/example.txt\n'

    def build(self):
        with patch('sys.stdout', new=io.StringIO()):
            package.build('1.2.3-rc.1', self.output)
        return self.output / 'hue2lox-1.2.3-rc.1-native.tar.gz'

    def test_manifest_covers_exact_allowlist_and_archive_is_reproducible(self):
        archive = self.build()
        original = archive.read_bytes()
        with tarfile.open(archive) as tar:
            names = {entry.name for entry in tar.getmembers()}
            prefix = 'hue2lox-native/'
            manifest = json.load(tar.extractfile(prefix + 'manifest.json'))
            self.assertEqual(manifest['schema_version'], 1)
            self.assertEqual(manifest['version'], '1.2.3-rc.1')
            self.assertEqual(manifest['commit'], 'a' * 40)
            self.assertTrue(manifest['dirty'])
            self.assertEqual(names, {prefix + name for name in manifest['files']} | {prefix + 'manifest.json'})
            for name, sha in manifest['files'].items():
                self.assertEqual(hashlib.sha256(tar.extractfile(prefix + name).read()).hexdigest(), sha)
                self.assertNotIn('__pycache__', name)
                self.assertNotIn('secrets/', name)
                self.assertNotEqual(name, '.env')
        self.assertEqual(self.build().read_bytes(), original)
        self.assertEqual((self.output / 'SHA256SUMS').read_text(), hashlib.sha256(original).hexdigest() + '  ' + archive.name + '\n')

    def test_rejects_unsafe_versions_and_symlinks(self):
        for version in ('../main', '1.0.0/x', '1.0.0\n', 'main', ''):
            with self.subTest(version=version), self.assertRaises(ValueError):
                package.build(version, self.output)
        (self.root / 'src/link').symlink_to(self.root / 'secrets/private.key')
        with self.assertRaisesRegex(ValueError, 'Symbolic'):
            self.build()
