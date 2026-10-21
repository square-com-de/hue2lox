"""Real local TLS connections; no Hue devices or production credentials."""
import http.client
from pathlib import Path
import socket
import ssl
import subprocess
import tempfile
import threading
import time
import unittest

import app


class HTTPSTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        root = Path(cls.temp.name)
        cert, key = root / 'cert.pem', root / 'key.pem'
        subprocess.run(['openssl', 'req', '-x509', '-newkey', 'rsa:2048',
                        '-nodes', '-days', '1', '-subj', '/CN=localhost',
                        '-addext', 'subjectAltName=IP:127.0.0.1',
                        '-keyout', str(key), '-out', str(cert)],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        cls.context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        cls.context.load_cert_chain(cert, key)
        cls.client_context = ssl.create_default_context(cafile=str(cert))

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def setUp(self):
        self.server = app.BoundedHTTPSServer(('127.0.0.1', 0), app.Handler, self.context)
        self.server.handshake_timeout = 1
        self.server.request_timeout = .3
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.address = self.server.server_address

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)

    def health(self):
        conn = http.client.HTTPSConnection(*self.address, context=self.client_context, timeout=.7)
        try:
            conn.request('GET', '/health')
            response = conn.getresponse()
            self.assertEqual(response.status, 200)
            self.assertEqual(response.read(), b'{"status":"ok"}')
        finally:
            conn.close()

    def test_silent_handshake_does_not_block_health_and_expires(self):
        with socket.create_connection(self.address, timeout=3) as stalled:
            # Must succeed before the stalled connection's one-second timeout.
            self.health()
            self.assertEqual(stalled.recv(1), b'')
        self.health()

    def test_partial_http_headers_expire_without_blocking_health(self):
        with self.client_context.wrap_socket(socket.create_connection(self.address, timeout=2),
                                             server_hostname='127.0.0.1') as stalled:
            stalled.sendall(b'GET /health HTTP/1.1\r\nHost: localhost\r\n')
            self.health()
            self.assertEqual(stalled.recv(1), b'')
        self.health()

    def test_capacity_rejection_does_not_stop_accept_loop(self):
        # Occupy all slots deterministically without spawning 32 idle clients.
        for _ in range(self.server.max_connections):
            self.assertTrue(self.server.connection_slots.acquire(blocking=False))
        try:
            with socket.create_connection(self.address, timeout=2) as rejected:
                self.assertEqual(rejected.recv(1), b'')
        finally:
            for _ in range(self.server.max_connections):
                self.server.connection_slots.release()
        self.health()

    def test_invalid_handshake_does_not_stop_server(self):
        with socket.create_connection(self.address, timeout=2) as invalid:
            invalid.sendall(b'not a TLS handshake\r\n')
            try:
                self.assertEqual(invalid.recv(1), b'')
            except ConnectionResetError:
                pass
        self.health()

    def test_trickling_headers_cannot_extend_total_deadline(self):
        with self.client_context.wrap_socket(socket.create_connection(self.address, timeout=2),
                                             server_hostname='127.0.0.1') as stalled:
            stalled.sendall(b'GET /health HTTP/1.1\r\nX-Test: ')
            started=time.monotonic()
            for _ in range(6):
                time.sleep(.1)
                try:
                    stalled.sendall(b'x')
                except OSError:
                    break
            self.assertEqual(stalled.recv(1),b'')
            self.assertLess(time.monotonic()-started,1.2)
        self.health()


if __name__ == '__main__':
    unittest.main()
