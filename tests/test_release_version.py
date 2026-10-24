import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import release_version
from tests import test_dashboard


class VersionTests(unittest.TestCase):
    def test_source_and_container_metadata_preserves_release_tag(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'install').mkdir()
            for value in ('1.0.1', '1.0.0-rc.6'):
                (root / 'install/release-image.json').write_text(json.dumps({'version': value}))
                self.assertEqual(release_version.installed_version(root), 'v' + value)

    def test_native_manifest_is_authoritative(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'install').mkdir()
            (root / 'install/release-image.json').write_text('{"version":"1.0.1"}')
            (root / 'manifest.json').write_text('{"version":"1.2.3-rc.1"}')
            self.assertEqual(release_version.installed_version(root), 'v1.2.3-rc.1')
            (root / 'manifest.json').write_text('broken')
            self.assertIsNone(release_version.installed_version(root))

    def test_missing_or_invalid_metadata_never_claims_a_release(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.assertIsNone(release_version.installed_version(root))
            for value in ('<script>alert(1)</script>', '', None, 42):
                (root / 'manifest.json').write_text(json.dumps({'version': value}))
                self.assertIsNone(release_version.installed_version(root))


class VersionPageTests(unittest.TestCase):
    setUp = test_dashboard.WebTests.setUp
    tearDown = test_dashboard.WebTests.tearDown
    get = test_dashboard.WebTests.get

    def test_page_renders_installed_version_without_placeholder_or_old_label(self):
        for value in ('v1.0.1', 'v1.0.0-rc.6', None):
            with patch('release_version.installed_version', return_value=value):
                status, headers, body = self.get('/')
            self.assertEqual(status, 200)
            self.assertIn((value or 'Version unbekannt').encode(), body)
            self.assertNotIn(b'Version 2', body)
            self.assertNotIn(b'__HUE2LOX_RELEASE__', body)
            self.assertEqual(int(headers['Content-Length']), len(body))
            self.assertEqual(headers['Cache-Control'], 'no-store')
