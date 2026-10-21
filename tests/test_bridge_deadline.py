"""Loopback TLS peer trickles bytes faster than inactivity timeout; no Hue access."""
import socket
import ssl
import threading
import time
import unittest
from unittest.mock import patch
import hue_client
from tests import test_https

class BridgeDeadlineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):test_https.HTTPSTests.setUpClass()
    @classmethod
    def tearDownClass(cls):test_https.HTTPSTests.temp.cleanup()

    def exchange(self,mode):
        listener=socket.socket();listener.bind(('127.0.0.1',0));listener.listen()
        port=listener.getsockname()[1];finished=threading.Event()
        def serve():
            try:
                raw,_=listener.accept();raw.settimeout(2)
                with test_https.HTTPSTests.context.wrap_socket(raw,server_side=True) as conn:
                    conn.recv(8192)
                    if mode=='body':
                        conn.sendall(b'HTTP/1.1 200 OK\r\nConnection: close\r\nContent-Length: 100\r\n\r\n')
                    elif mode=='success':
                        conn.sendall(b'HTTP/1.1 200 OK\r\nContent-Length: 2\r\n\r\n{}');return
                    for _ in range(30):
                        conn.sendall(b' ' if mode=='body' else b'X')
                        time.sleep(.04)
            except OSError:pass
            finally:finished.set()
        worker=threading.Thread(target=serve,daemon=True);worker.start()
        started=time.monotonic()
        try:
            # Explicit loopback port, real certificate validation, real deadline logic.
            original=hue_client.BridgeConnection
            def local(host,**kwargs):return original('127.0.0.1',port=port,**kwargs)
            with patch('hue_client.BridgeConnection',side_effect=local),patch('hue_client.tls_context',return_value=test_https.HTTPSTests.client_context),patch('hue_client.BRIDGE_DEADLINE_SECONDS',.25):
                if mode=='success':
                    self.assertEqual(hue_client.request_document('GET','/',bridge={'host':'127.0.0.1','bridge_id':'127.0.0.1'},authenticated=False),{})
                else:
                    with self.assertRaises(hue_client.BridgeRequestError) as error:
                        hue_client.request_document('GET','/',bridge={'host':'127.0.0.1','bridge_id':'127.0.0.1'},authenticated=False)
                    self.assertEqual(str(error.exception),'bridge request failed')
                    self.assertLess(time.monotonic()-started,.9)
        finally:
            listener.close();worker.join(2)
        self.assertTrue(finished.is_set())

    def test_trickled_headers_hit_total_deadline(self):self.exchange('headers')
    def test_trickled_close_delimited_transport_body_hits_deadline(self):self.exchange('body')
    def test_fast_response_still_succeeds(self):self.exchange('success')
