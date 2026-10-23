"""Offline release binding and complete runtime notice delivery checks."""
import hashlib
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parent.parent


class ReleaseReadinessTests(unittest.TestCase):
    def test_candidate_guides_and_compose_match_installer_version(self):
        version = json.loads((ROOT / 'install/release-image.json').read_text())['version']
        self.assertIn('ghcr.io/square-com-de/hue2lox:' + version,
                      (ROOT / 'docker/compose.image.yaml').read_text())
        for name in ('INSTALL.md', 'INSTALL.de.md', 'docs/AI-INSTALL.md', 'docs/AI-INSTALL.de.md', 'docs/DOWNLOADS.md'):
            with self.subTest(name=name):
                self.assertIn('hue2lox-v' + version + '.zip', (ROOT / name).read_text())
        for name in ('docs/INSTALL-NATIVE.md', 'docs/INSTALL-NATIVE.en.md'):
            self.assertIn('hue2lox-' + version + '-native.tar.gz', (ROOT / name).read_text())

    def test_original_ca_and_complete_upstream_notice_reach_all_deployments(self):
        self.assertEqual(hashlib.sha256((ROOT / 'trust/huebridge-ca.pem').read_bytes()).hexdigest(),
                         '2ff54626fc51de587cce0f3f0339552f89da781b5d5949fa0c90ec30ddf8acfa')
        notice = (ROOT / 'trust/LICENSE-raycast.txt').read_bytes()
        self.assertEqual(hashlib.sha256(notice).hexdigest(),
                         '7f727f8b20cdd0e65f84e70b9cac2fce337dcecee4dc88955eb012ea27f02755')
        self.assertIn(notice.decode().strip(), (ROOT / 'THIRD-PARTY-NOTICES.md').read_text())
        self.assertIn('THIRD-PARTY-NOTICES.md /app/', (ROOT / 'Dockerfile').read_text())
        self.assertIn("'trust'", (ROOT / 'scripts/build-native-package.py').read_text())

    def test_license_page_describes_actual_container_and_native_runtimes(self):
        image = json.loads((ROOT / 'compliance/base-image.json').read_text())['image']
        python = image.split(':')[1].split('-')[0]
        page = (ROOT / 'web/licenses.html').read_text()
        self.assertIn('Python ' + python, page)
        self.assertNotIn('Python 3.12', page)
        self.assertIn('3.11', page)
