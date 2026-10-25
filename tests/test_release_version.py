import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import release_version
from tests import test_dashboard


class VersionTests(unittest.TestCase):
    def test_container_release_build_and_development_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'install').mkdir()
            (root / 'install/release-image.json').write_text('{"version":"1.0.1"}')
            # A checked-in declaration is not evidence of a built release.
            self.assertIsNone(release_version.installed_version(root))
            for value in ('1.0.2', '1.0.2-rc.1'):
                data = release_version.build_identity(value, 'a' * 40)
                (root / 'build-info.json').write_text(json.dumps(data))
                self.assertEqual(release_version.installed_version(root), 'Hue2Lox ' + value)
            (root / 'build-info.json').write_text(json.dumps(release_version.build_identity('', 'b' * 40)))
            self.assertEqual(release_version.installed_version(root), 'Hue2Lox · Entwicklungsbuild')
            (root / 'build-info.json').write_text('{"schema_version":1,"version":"1.0.1","kind":"release","revision":null}')
            self.assertIsNone(release_version.installed_version(root))

    def test_release_metadata_requires_revision_and_safe_values(self):
        for version, revision in (('1.0.2', ''), ('<script>', 'a' * 40), ('1.0.2', 'main')):
            with self.subTest(version=version), self.assertRaises(ValueError):
                release_version.build_identity(version, revision)

    def test_malformed_container_metadata_is_not_a_release(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for data in ([], None, {'schema_version': True}, {'schema_version': 1, 'kind': 'release', 'version': '1.0.2', 'revision': 'x'}):
                (root / 'build-info.json').write_text(json.dumps(data))
                self.assertIsNone(release_version.installed_version(root))

    def test_native_manifest_is_authoritative(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'install').mkdir()
            (root / 'install/release-image.json').write_text('{"version":"1.0.1"}')
            (root / 'manifest.json').write_text(json.dumps({'version':'1.2.3-rc.1','commit':'a'*40,'dirty':False}))
            self.assertEqual(release_version.installed_version(root), 'Hue2Lox 1.2.3-rc.1')
            (root / 'manifest.json').write_text(json.dumps({'version':'1.2.3-rc.1','commit':'a'*40,'dirty':True}))
            self.assertEqual(release_version.installed_version(root), 'Hue2Lox · Entwicklungsbuild')
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
        for value in ('Hue2Lox 1.0.2', 'Hue2Lox 1.0.2-rc.1', 'Hue2Lox · Entwicklungsbuild', None):
            with patch('release_version.installed_version', return_value=value):
                status, headers, body = self.get('/')
            self.assertEqual(status, 200)
            self.assertIn((value or 'Version unbekannt').encode(), body)
            self.assertNotIn(b'Version 2', body)
            self.assertNotIn(b'__HUE2LOX_RELEASE__', body)
            self.assertEqual(int(headers['Content-Length']), len(body))
            self.assertEqual(headers['Cache-Control'], 'no-store')
