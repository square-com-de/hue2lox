"""Exercise relocated runtime staging without Docker or a live installation."""
from pathlib import Path
import json
import os
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent.parent


class RuntimeLayoutTests(unittest.TestCase):
    def test_staging_preserves_state_and_backs_up_runtime(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / 'instance'
            backup = Path(tmp) / 'backup'
            dest.mkdir()
            protected = {
                '.env': 'COMPOSE_PROJECT_NAME=hue2lox-existing\n',
                'data/registry.json': '{"existing":true}',
                'data/admin_auth.json': 'existing password hash',
                'secrets/control_token': 'existing token',
                'certs/server.key': 'existing test key',
                'compose.override.yaml': 'existing overrides',
            }
            for name, value in protected.items():
                p = dest / name
                p.parent.mkdir(exist_ok=True)
                p.write_text(value)
                p.chmod(0o600)
            (dest/'compose.yaml').write_text('previous compose')
            (dest/'registry.json').write_text('{"legacy":true}')
            env = dict(os.environ, src=str(ROOT), dst=str(dest), backup=str(backup))
            subprocess.run(['sh', '-c', '. "$src/scripts/copy-runtime.sh"; copy_runtime'], env=env, check=True, capture_output=True)
            for name, value in protected.items():
                self.assertEqual((dest/name).read_text(), value)
                self.assertEqual((dest/name).stat().st_mode & 0o777, 0o600)
            self.assertEqual((backup/'compose.yaml').read_text(), 'previous compose')
            self.assertEqual(json.loads((dest/'config/registry.json').read_text()), {'legacy': True})
            self.assertEqual((dest/'src/app.py').read_bytes(), (ROOT/'src/app.py').read_bytes())
            self.assertTrue((dest/'docker/Dockerfile.status').is_file())
