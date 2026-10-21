"""Shared initialization stays private and certificate-free for HTTP deployments."""
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import install_state


class HttpStateTests(unittest.TestCase):
    def test_http_initialization_without_openssl_keeps_private_modes_under_umask_077(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            previous = os.umask(0o077)
            try:
                with patch.object(install_state.subprocess, 'run') as run:
                    install_state.initialize(root / 'state', None, root / 'secrets', '127.0.0.1')
                    run.assert_not_called()
            finally:
                os.umask(previous)
            self.assertEqual(json.loads((root / 'state/registry.json').read_text()),
                             {'schema_version': 1, 'bridges': []})
            for name, mode in [('state', 0o700), ('secrets', 0o700),
                               ('state/admin_auth.json', 0o600), ('secrets/control_token', 0o400)]:
                self.assertEqual((root / name).stat().st_mode & 0o777, mode)
            self.assertEqual({p.name for p in root.iterdir()}, {'state', 'secrets'})
            before = (root / 'state/admin_auth.json').read_bytes()
            with self.assertRaises(ValueError):
                install_state.initialize(root / 'state', None, root / 'secrets', '127.0.0.1')
            self.assertEqual((root / 'state/admin_auth.json').read_bytes(), before)

    def test_http_preparation_failure_cleans_its_new_directories(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with patch.object(install_state, 'create_credentials', side_effect=ValueError('preparation failed')):
                with self.assertRaises(ValueError):
                    install_state.initialize(root / 'state', None, root / 'secrets', '127.0.0.1')
            self.assertEqual(list(root.iterdir()), [])
