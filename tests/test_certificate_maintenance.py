"""Real certificates on temporary isolated installations, never Docker or bridges."""
import importlib.util
import os
from pathlib import Path
import socket
import ssl
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent

def load(name):
    spec=importlib.util.spec_from_file_location(name, ROOT/'scripts'/f'{name}.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

prepare=load('prepare-install').prepare
maintenance=load('renew-certificate')

class CertificateMaintenanceTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        with socket.socket() as sock:
            sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
        self.dest=prepare(Path(self.temp.name)/'instance','127.0.0.1',port)
        self.original={p:p.read_bytes() for directory in ('data','secrets') for p in (self.dest/directory).rglob('*') if p.is_file()}

    def test_renew_preserves_private_state(self):
        old=(self.dest/'certs/server.crt').read_bytes()
        backup=maintenance.renew(self.dest)
        self.assertEqual((backup/'certs/server.crt').read_bytes(),old)
        self.assertNotEqual((self.dest/'certs/server.crt').read_bytes(),old)
        self.assertEqual((self.dest/'health-test.crt').read_bytes(),(self.dest/'certs/server.crt').read_bytes())
        context=ssl.create_default_context(cafile=str(self.dest/'health-test.crt'))
        context.load_cert_chain(self.dest/'certs/server.crt',self.dest/'certs/server.key')
        certificate=ssl._ssl._test_decode_cert(str(self.dest/'certs/server.crt'))
        self.assertIn(('IP Address','127.0.0.1'),certificate['subjectAltName'])
        self.assertIn('HUE2LOX_BIND_IP=127.0.0.1',(self.dest/'.env').read_text())
        self.assertEqual((self.dest/'certs/server.key').stat().st_mode & 0o777,0o600)
        self.assertEqual((self.dest/'certs').stat().st_mode & 0o777,0o700)
        if os.geteuid()==0:self.assertEqual((self.dest/'certs/server.key').stat().st_uid,10001)
        for path,data in self.original.items():self.assertEqual(path.read_bytes(),data)
        # Restore the saved certificate/environment set into this stopped fixture.
        import shutil
        for name in maintenance.FILES:shutil.copy2(backup/name,self.dest/name)
        self.assertEqual((self.dest/'certs/server.crt').read_bytes(),old)

    def test_active_listener_refused_without_changes(self):
        port=int(dict(l.split('=',1) for l in (self.dest/'.env').read_text().splitlines())['HUE2LOX_PORT'])
        before={n:(self.dest/n).read_bytes() for n in maintenance.FILES}
        with socket.socket() as sock:
            sock.bind(('127.0.0.1',port));sock.listen()
            with self.assertRaises(OSError):maintenance.renew(self.dest)
        for name,data in before.items():self.assertEqual((self.dest/name).read_bytes(),data)

    def test_replace_failure_rolls_back_and_keeps_backup(self):
        before={n:(self.dest/n).read_bytes() for n in maintenance.FILES}
        real=os.replace;calls=0
        def fail_once(src,dst):
            nonlocal calls
            calls+=1
            if calls==3:raise OSError('simulated write failure')
            return real(src,dst)
        with patch.object(maintenance.os,'replace',side_effect=fail_once):
            with self.assertRaises(OSError):maintenance.renew(self.dest)
        for name,data in before.items():self.assertEqual((self.dest/name).read_bytes(),data)

    def test_address_change_updates_url_and_san_without_changing_port(self):
        # Address availability is mocked; no network configuration is changed.
        with patch.object(maintenance.socket, 'socket'):
            maintenance.renew(self.dest, '192.0.2.50')
        self.assertIn('HUE_PUBLIC_URL=https://192.0.2.50:',(self.dest/'.env').read_text())
        cert=ssl._ssl._test_decode_cert(str(self.dest/'certs/server.crt'))
        self.assertIn(('IP Address','192.0.2.50'),cert['subjectAltName'])
        for path,data in self.original.items():self.assertEqual(path.read_bytes(),data)

    def test_renew_after_closed_server_with_time_wait_connections(self):
        port=int(dict(l.split('=',1) for l in (self.dest/'.env').read_text().splitlines())['HUE2LOX_PORT'])
        with socket.socket() as listener:
            listener.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
            listener.bind(('127.0.0.1',port));listener.listen()
            with socket.create_connection(('127.0.0.1',port)) as client:
                conn,_=listener.accept()
                conn.shutdown(socket.SHUT_WR)
                self.assertEqual(client.recv(1),b'')
                conn.close()
        maintenance.renew(self.dest)
        for path,data in self.original.items():self.assertEqual(path.read_bytes(),data)
