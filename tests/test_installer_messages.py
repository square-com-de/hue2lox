"""Language selected in the shell reaches helpers and their CLI errors."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import installer_messages

ROOT = Path(__file__).resolve().parents[1]


class InstallerMessageTests(unittest.TestCase):
    def test_native_and_docker_cli_error_language_preserves_exit_status(self):
        for script, args, prefix in [('scripts/native-assistant.py',['inspect','--package','/missing','--sha256','bad'],'Nativer Assistent angehalten'),
                                     ('scripts/prepare-install.py',['--destination','/unused','--host','0.0.0.0'],'Vorbereitung fehlgeschlagen')]:
            for lang in ('de','en'):
                result=subprocess.run([sys.executable,str(ROOT/script),*args],env={**os.environ,'HUE2LOX_INSTALL_LANG':lang},capture_output=True,text=True)
                self.assertNotEqual(result.returncode,0)
                self.assertEqual(prefix in result.stderr,lang=='de',result.stderr)

    def test_language_changes_messages_but_keeps_identifiers_and_values(self):
        text='Native update passed HTTPS healthcheck. Protected backup: /var/backups/hue2lox/20261023T120000Z-abcd'
        with patch.dict(os.environ,{'HUE2LOX_INSTALL_LANG':'de'}):
            result=installer_messages.message(text)
            self.assertIn('Geschützte Sicherung:',result)
            self.assertTrue(result.endswith('/var/backups/hue2lox/20261023T120000Z-abcd'))
        with patch.dict(os.environ,{'HUE2LOX_INSTALL_LANG':'en'}):self.assertEqual(installer_messages.message(text),text)
