"""Fresh install without Docker: secrets, certificate and overwrite safeguards."""
import importlib.util
import json
import os
from pathlib import Path
import ssl
import tempfile
import unittest
spec=importlib.util.spec_from_file_location('prepare_install',Path(__file__).resolve().parent.parent/'scripts/prepare-install.py')
setup=importlib.util.module_from_spec(spec);spec.loader.exec_module(setup)

class FreshInstallTests(unittest.TestCase):
    def test_clean_independent_instances_and_existing_destination_refused(self):
        with tempfile.TemporaryDirectory() as root:
            a=setup.prepare(Path(root)/'a','127.0.0.1',18443);b=setup.prepare(Path(root)/'b','127.0.0.1',18444)
            self.assertEqual(json.loads((a/'data/registry.json').read_text()),{'schema_version':1,'bridges':[]})
            self.assertNotEqual((a/'secrets/control_token').read_bytes(),(b/'secrets/control_token').read_bytes())
            self.assertNotEqual((a/'certs/server.key').read_bytes(),(b/'certs/server.key').read_bytes())
            for f,mode in [('secrets/control_token',0o400),('certs/server.key',0o600),('data/admin_auth.json',0o600)]:self.assertEqual((a/f).stat().st_mode&0o777,mode)
            self.assertEqual(a.stat().st_mode & 0o777,0o755)
            for directory in ('data','certs','secrets'):
                self.assertEqual((a/directory).stat().st_mode & 0o777,0o700)
            self.assertEqual((a/'.env').stat().st_mode & 0o777,0o600)
            context=ssl.create_default_context(cafile=str(a/'certs/server.crt'));context.load_cert_chain(a/'certs/server.crt',a/'certs/server.key')
            env=(a/'.env').read_text();self.assertIn('HUE_WRITES_ENABLED=0',env);self.assertIn('https://127.0.0.1:18443',env)
            self.assertFalse((a/'secrets/hue_key').exists())
            self.assertIn('HUE_LEGACY_ENABLED: "0"',(a/'compose.yaml').read_text())
            compose=(a/'compose.yaml').read_text()
            self.assertIn('network_mode: host',compose)
            self.assertNotIn('    ports:',compose)
            self.assertIn('PORT: "${HUE2LOX_PORT:-8443}"',compose)
            self.assertIn('BIND_HOST: "${HUE2LOX_BIND_IP:?Run prepare-install first}"',compose)
            self.assertIn("os.environ['BIND_HOST']",compose)
            self.assertIn("os.environ['PORT']",compose)
            self.assertNotIn('127.0.0.1:8443/health',compose)
            for name in ('LICENSE','NOTICE','THIRD-PARTY-NOTICES.md'):
                self.assertEqual((a/name).read_bytes(),(Path(__file__).resolve().parent.parent/name).read_bytes())
            values = dict(line.split('=', 1) for line in env.splitlines())
            self.assertRegex(values['COMPOSE_PROJECT_NAME'], r'^hue2lox-[a-z]+$')
            self.assertEqual(values['HUE2LOX_CONTAINER_NAME'], values['COMPOSE_PROJECT_NAME'] + '-1')
            self.assertIn('HUE2LOX_CONTAINER_NAME', compose)
            saved_env = (a/'.env').read_bytes()
            before=(a/'secrets/control_token').read_bytes()
            with self.assertRaises(ValueError):setup.prepare(a,'127.0.0.1')
            self.assertEqual((a/'secrets/control_token').read_bytes(),before)
            self.assertEqual((a/'.env').read_bytes(), saved_env)
    def test_invalid_host_port_never_creates_destination(self):
        with tempfile.TemporaryDirectory() as root:
            dest=Path(root)/'bad'
            for host,port in [('10.200.0.5\nBAD=1',8443),('0.0.0.0',8443),('224.0.0.1',8443),('127.0.0.1',1)]:
                with self.assertRaises(ValueError):setup.prepare(dest,host,port)
                self.assertFalse(dest.exists())
