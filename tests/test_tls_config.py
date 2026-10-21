"""TLS_CERT/TLS_KEY startup configuration: HTTP only when both are absent, HTTPS when both are valid."""
from pathlib import Path
import os
import ssl
import subprocess
import sys
import tempfile
import unittest

import app

ROOT = Path(__file__).resolve().parent.parent


class TlsConfigTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        root = Path(cls.temp.name)
        cls.cert, cls.key = str(root / 'cert.pem'), str(root / 'key.pem')
        subprocess.run(['openssl', 'req', '-x509', '-newkey', 'rsa:2048', '-nodes', '-days', '1',
                        '-subj', '/CN=localhost', '-keyout', cls.key, '-out', cls.cert],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_both_absent_means_plain_http(self):
        self.assertIsNone(app.tls_context({}))

    def test_both_valid_means_https(self):
        self.assertIsInstance(app.tls_context({'TLS_CERT': self.cert, 'TLS_KEY': self.key}), ssl.SSLContext)

    def test_partial_or_empty_configuration_is_rejected(self):
        for env in ({'TLS_CERT': self.cert}, {'TLS_KEY': self.key},
                    {'TLS_CERT': '', 'TLS_KEY': ''},
                    {'TLS_CERT': self.cert, 'TLS_KEY': ''}, {'TLS_CERT': '', 'TLS_KEY': self.key}):
            with self.subTest(env=sorted(env)):
                with self.assertRaises(ValueError):
                    app.tls_context(env)

    def test_invalid_paths_with_both_set_fail(self):
        with self.assertRaises(OSError):
            app.tls_context({'TLS_CERT': '/nonexistent/cert.pem', 'TLS_KEY': '/nonexistent/key.pem'})

    def test_service_refuses_to_start_with_partial_tls(self):
        for env in ({'TLS_CERT': self.cert}, {'TLS_KEY': self.key}, {'TLS_CERT': '', 'TLS_KEY': ''}):
            with self.subTest(env=sorted(env)):
                result = subprocess.run([sys.executable, str(ROOT / 'src/app.py')], capture_output=True, text=True,
                                        timeout=20, env={**{k: v for k, v in os.environ.items() if not k.startswith('TLS_')}, **env,
                                                         'PORT': '0', 'BIND_HOST': '127.0.0.1'})
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('TLS_CERT and TLS_KEY must both be set', result.stderr)
                self.assertNotIn('service ready', result.stdout)


if __name__ == '__main__':
    unittest.main()
