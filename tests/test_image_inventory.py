import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location('image_inventory', ROOT/'scripts/image-inventory.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class InventoryTests(unittest.TestCase):
    def test_apk_origin_commit_and_license_are_preserved(self):
        data = 'P:libdemo\nV:1.2-r3\nL:MIT AND BSD-2-Clause\no:demo\nc:abc123\nA:aarch64\nF:usr/lib\n\nP:.virtual\nV:1\nL:\n'
        packages = module.apk_packages(data)
        self.assertEqual(len(packages), 2)
        self.assertEqual(packages[1]['source_commit'], 'abc123')
        self.assertEqual(packages[1]['license'], 'MIT AND BSD-2-Clause')
        self.assertEqual(packages[1]['architecture'], 'aarch64')
        self.assertIsNone(packages[0]['origin'])

    def test_non_package_blocks_do_not_create_components(self):
        self.assertEqual(module.apk_packages('F:usr/lib\nR:file.so\n\n'), [])

    def test_publisher_cannot_push_before_materials_are_approved(self):
        workflow = (ROOT/'.github/workflows/publish-image.yml').read_text()
        self.assertIn('push: false', workflow)
        self.assertNotIn('login-action', workflow)
        self.assertNotIn('packages: write', workflow)

    def test_dockerfiles_match_the_inventory_base(self):
        import json
        lock = json.loads((ROOT/'compliance/base-image.json').read_text())
        expected = 'FROM ' + lock['image'] + '@' + lock['index_digest']
        for path in ('Dockerfile', 'docker/Dockerfile.status'):
            self.assertEqual((ROOT/path).read_text().splitlines()[0], expected)
