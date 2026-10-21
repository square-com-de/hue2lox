"""Regression checks for complete, hash-checked source collection."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('source_bundle', ROOT / 'scripts/build-source-bundle.py')
bundle = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bundle)


class SourceBundleTests(unittest.TestCase):
    def test_every_runtime_origin_has_complete_recipe(self):
        recipes = {r['origin']: r for r in bundle.read('recipes.json')}
        for arch in ('amd64', 'arm64'):
            for p in bundle.read(arch + '-base-packages.json'):
                if p['name'] != '.python-rundeps':
                    self.assertTrue(recipes[p['origin']]['directory_complete'])
        self.assertTrue(any('libverto-0.3.2.tar.gz' in j[0] for j in bundle.source_jobs()))

    def test_inline_apkbuild_input_cannot_be_skipped(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            recipe = root / 'recipes/example/APKBUILD'
            recipe.parent.mkdir(parents=True)
            recipe.write_text('sha512sums="' + 'a' * 128 + '  example.tar.gz"\n')
            with patch.object(bundle, 'read', return_value=[]):
                with self.assertRaisesRegex(ValueError, 'Missing/mismatched'):
                    bundle.check_recipe_inputs(root)

    def test_corrupt_cache_is_rejected_without_download(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'bad').write_bytes(b'changed source')
            with patch.object(bundle.urllib.request, 'urlopen') as network:
                with self.assertRaisesRegex(ValueError, 'Checksum mismatch'):
                    bundle.fetch(('bad', 'https://example.invalid/source', 'sha256', '0' * 64), root / 'out', root)
                network.assert_not_called()
            self.assertFalse((root / 'out/bad').exists())

    def test_archive_paths_cannot_escape(self):
        for value in ('../LICENSE', '/LICENSE', 'a/../../LICENSE', 'a\\LICENSE'):
            with self.assertRaises(ValueError):
                bundle.safe_path(value)

    def test_vendor_manifest_includes_indented_dependencies(self):
        manifest = 'requests==2.32.3\n    certifi==2024.8.30\n    idna==3.10\n'
        matches = bundle.parse_vendors(manifest)
        self.assertEqual([name for name, version in matches], ['requests', 'certifi', 'idna'])

    def test_changed_runtime_package_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'APK inventory differs'):
            bundle.verify_inventory([], {'apk_packages': [{'name': 'new-library', 'version': '1'}]}, 'amd64')
