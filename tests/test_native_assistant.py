"""Offline source identity and local automatic package preparation."""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('native_assistant_test', ROOT / 'scripts/native-assistant.py')
assistant = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(assistant)


class NativeAssistantTests(unittest.TestCase):
    def test_clean_checkout_builds_verified_package_and_dirty_source_is_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'source'
            output = Path(directory) / 'packages'
            root.mkdir()
            builder = assistant.load('test_assistant_builder', ROOT / 'scripts/build-native-package.py')
            for name in builder.TREES:
                shutil.copytree(ROOT / name, root / name, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
            for name in (*builder.FILES, 'scripts/build-native-package.py'):
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / name, target)
            for command in (['git', 'init'], ['git', 'add', '.'], ['git', '-c', 'user.name=Test', '-c', 'user.email=test@example.invalid', 'commit', '-m', 'offline fixture']):
                subprocess.run(command, cwd=root, check=True, capture_output=True)
            metadata = assistant.build_source(output, root)
            self.assertEqual(json.loads((output / 'package.json').read_text()), metadata)
            self.assertTrue(Path(metadata['package']).is_file())
            self.assertEqual(metadata['version'], '0.0.0-dev.' + metadata['commit'][:12])
            (root / 'src/app.py').write_text('unreviewed working-tree change')
            with self.assertRaisesRegex(ValueError, 'clean'):
                assistant.build_source(output, root)

    def test_directory_without_git_identity_is_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaises((ValueError, subprocess.CalledProcessError)):
                assistant.build_source(root / 'packages', root)
