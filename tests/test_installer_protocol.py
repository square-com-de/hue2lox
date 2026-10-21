"""Fresh HTTP and HTTPS configurations, including proxy origin separation."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from tests.test_install import setup
from tests.test_start_install import runner


class InstallerProtocolTests(unittest.TestCase):
    def test_http_has_no_certificates_or_empty_tls_variables(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(setup.subprocess, 'run') as run:
            dest = setup.prepare(Path(tmp)/'http', '127.0.0.1', 18444, 'http', 'https://hue.example.org')
            run.assert_not_called()
            self.assertFalse((dest/'certs').exists())
            self.assertFalse((dest/'health-test.crt').exists())
            compose = (dest/'compose.yaml').read_text()
            self.assertNotIn('TLS_CERT:', compose)
            self.assertNotIn('TLS_KEY:', compose)
            self.assertNotIn('./certs:', compose)
            self.assertIn('HUE_PUBLIC_URL=https://hue.example.org', (dest/'.env').read_text())
            _, endpoint, context = runner.preflight(dest)
            self.assertEqual(endpoint, 'http://127.0.0.1:18444')
            self.assertIsNone(context)
            with self.assertRaises(ValueError):
                setup.prepare(dest, '127.0.0.1', 18444, 'https')
            (dest/'compose.yaml').write_text(compose+'\n      TLS_CERT: ""\n')
            with self.assertRaisesRegex(ValueError, 'omit both'):
                runner.preflight(dest)

    def test_https_default_and_legacy_settings_still_validate(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = setup.prepare(Path(tmp)/'https', '127.0.0.1', 18443)
            self.assertTrue((dest/'certs/server.key').is_file())
            _, url, context = runner.preflight(dest)
            self.assertEqual(url, 'https://127.0.0.1:18443')
            self.assertIsNotNone(context)
            env = dest/'.env'
            env.write_text(env.read_text().replace('HUE2LOX_SCHEME=https\n',''))
            self.assertIsNotNone(runner.preflight(dest)[2])

    def test_invalid_origin_or_scheme_creates_no_installation(self):
        for scheme, url in [('ftp', None), ('http', 'https://x/a'), ('http', 'https://user:pass@x'),
                            ('http', 'https://x\nBAD=1'), ('http', 'https://x:99999'),
                            ('http', 'https://$HOST'), ('https', 'https://other.example')]:
            with self.subTest(scheme=scheme,url=url), tempfile.TemporaryDirectory() as tmp:
                dest=Path(tmp)/'new'
                with self.assertRaises(ValueError): setup.prepare(dest,'127.0.0.1',18443,scheme,url)
                self.assertFalse(dest.exists())

    def test_interactive_selection_in_both_languages(self):
        import subprocess
        import os
        import socket
        script = Path(__file__).resolve().parents[1]/'install-assistant.sh'
        for lang in ('de', 'en'):
            for mode, scheme in [('1', 'https'), ('2', 'http')]:
                with self.subTest(lang=lang,mode=mode), tempfile.TemporaryDirectory() as tmp:
                    with socket.socket() as sock:
                        sock.bind(('127.0.0.1',0)); port=sock.getsockname()[1]
                    shell = '''source "$1"
DEST=$2
root_required(){ return 0; }
choose_server_ip(){ SELECTED_IP=127.0.0.1; }
confirm(){ return 0; }
run(){ printf 'ARG:%s\\n' "$@"; }
prepare_setup
'''
                    result=subprocess.run(['bash','-c',shell,'test',str(script),str(Path(tmp)/'new')],
                        input=mode+'\n'+str(port)+'\n'+('https://hue.example.org\n' if mode=='2' else ''),
                        text=True,capture_output=True,env={**os.environ,'HUE2LOX_INSTALL_LANG':lang},timeout=10)
                    self.assertEqual(result.returncode,0,result.stderr)
                    self.assertIn('ARG:--scheme\nARG:'+scheme,result.stdout)
                    if mode=='2': self.assertIn('ARG:--public-url\nARG:https://hue.example.org',result.stdout)
