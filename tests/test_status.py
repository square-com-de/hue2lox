import http.client
from http.server import ThreadingHTTPServer
import json
import threading
import unittest
from unittest.mock import patch
import app


class EndpointTests(unittest.TestCase):
    def setUp(self):
        self.server = ThreadingHTTPServer(('127.0.0.1', 0), app.Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
    def tearDown(self):
        self.server.shutdown(); self.server.server_close(); self.thread.join()
    def request(self, method, path):
        conn = http.client.HTTPConnection('127.0.0.1', self.server.server_port)
        conn.request(method, path)
        r = conn.getresponse(); result = (r.status, r.read()); conn.close()
        return result
    def test_health_is_independent_of_bridge(self):
        with patch('app.read_status', side_effect=RuntimeError('secret')) as read:
            self.assertEqual(self.request('GET', '/health'), (200, b'{"status":"ok"}'))
            read.assert_not_called()
    def test_status_and_sanitized_failure(self):
        with patch('app.read_status', return_value={'on': True, 'brightness': 47.04}):
            status, body = self.request('GET', '/hue-go/status')
            self.assertEqual(status, 200)
            self.assertEqual(json.loads(body)['brightness'], 47.04)
        with patch('app.read_status', side_effect=RuntimeError('DO_NOT_EXPOSE')):
            status, body = self.request('GET', '/hue-go/status')
            self.assertEqual(status, 502)
            self.assertNotIn(b'DO_NOT_EXPOSE', body)
    def test_writes_and_unknown_routes_rejected(self):
        with patch('app.read_status') as read:
            self.assertEqual(self.request('GET', '/unknown')[0], 404)
            self.assertEqual(self.request('PUT', '/hue-go/status')[0], 404)
            read.assert_not_called()

if __name__ == '__main__': unittest.main()
