import http.client
import json
import os
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch, MagicMock
from http.server import ThreadingHTTPServer
import app
import hue_client


class MappingTests(unittest.TestCase):
    def test_on_off_and_dimming(self):
        for state, expected in [
            ({'on': True}, {'on': {'on': True}}),
            ({'on': False}, {'on': {'on': False}}),
            ({'brightness': 0}, {'on': {'on': False}}),
            ({'brightness': 25.5}, {'on': {'on': True}, 'dimming': {'brightness': 25.5}}),
            ({'brightness': 100}, {'on': {'on': True}, 'dimming': {'brightness': 100}}),
        ]:
            with self.subTest(state=state):
                self.assertEqual(hue_client.state_payload(state), expected)
    def test_invalid_input_never_reaches_bridge(self):
        bad = [None, [], {}, {'on': 1}, {'on': 'true'}, {'brightness': True},
               {'brightness': -1}, {'brightness': 101}, {'brightness': '50'},
               {'brightness': float('nan')}, {'brightness': float('inf')},
               {'color': 'red'}, {'on': False, 'brightness': 50}, {'on': True, 'brightness': 0}]
        with patch('hue_client.request_light') as request:
            for state in bad:
                with self.subTest(state=state), self.assertRaises(ValueError):
                    hue_client.write_state(state)
            request.assert_not_called()
    def test_put_and_acknowledgement(self):
        light = 'test-light'
        with patch('hue_client.request_light', return_value=(light, {'rid': light, 'rtype': 'light'})) as request:
            result = hue_client.write_state({'brightness': 50})
            request.assert_called_once_with('PUT', {'on': {'on': True}, 'dimming': {'brightness': 50}})
            self.assertEqual(result['status'], 'accepted')
        with patch('hue_client.request_light', return_value=(light, {'rid': 'other', 'rtype': 'light'})):
            with self.assertRaises(ValueError): hue_client.write_state({'on': True})
    def test_api_errors_even_with_http_200(self):
        with tempfile.TemporaryDirectory() as directory:
            key = Path(directory)/'key'; key.write_text('fake-test-key')
            env = {'HUE_BRIDGE_IP':'192.0.2.1','HUE_BRIDGE_ID':'001788FFFE000001','HUE_LIGHT_ID':'fixture-light','HUE_KEY_FILE': str(key), 'HUE_CA_FILE': str(Path(__file__).resolve().parent.parent/'trust/huebridge-ca.pem')}
            with patch.dict(os.environ, env), patch('hue_client.BridgeConnection') as connection:
                response = MagicMock(); response.status = 200
                response.read.return_value = b'{"errors":[{"description":"failed"}],"data":[]}'
                connection.return_value.getresponse.return_value = response
                with self.assertRaises(ValueError): hue_client.write_state({'on': True})
                connection.return_value.close.assert_called_once()
                self.assertEqual(connection.return_value.request.call_args.args[0], 'PUT')


class ControlEndpointTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.token = 'a'*48
        tokenfile = Path(self.temp.name)/'token'; tokenfile.write_text(self.token)
        self.env = patch.dict(os.environ, {'HUE_WRITES_ENABLED': '0', 'HUE_CONTROL_TOKEN_FILE': str(tokenfile)})
        self.env.start()
        self.server = ThreadingHTTPServer(('127.0.0.1', 0), app.Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True); self.thread.start()
    def tearDown(self):
        self.server.shutdown(); self.server.server_close(); self.thread.join()
        self.env.stop(); self.temp.cleanup()
    def request(self, body, token=None, method='PUT'):
        headers = {'Content-Type': 'application/json'}
        if token is not None: headers['Authorization'] = 'Bearer ' + token
        conn = http.client.HTTPConnection('127.0.0.1', self.server.server_port, timeout=5)
        conn.request(method, '/hue-go/state', body=body, headers=headers)
        response = conn.getresponse(); result=(response.status, response.read()); conn.close()
        return result
    def test_default_disabled_and_unauthorized_never_write(self):
        with patch('app.write_state') as write:
            self.assertEqual(self.request('{"on":true}', self.token)[0], 403)
            os.environ['HUE_WRITES_ENABLED'] = '1'
            self.assertEqual(self.request('{"on":true}')[0], 401)
            self.assertEqual(self.request('{"on":true}', 'wrong')[0], 401)
            self.assertEqual(self.request('', method='GET')[0], 405)
            write.assert_not_called()
    def test_bad_input_never_writes(self):
        os.environ['HUE_WRITES_ENABLED'] = '1'
        with patch('app.write_state') as write:
            for body in ['not json', '{"brightness":101}', '{"brightness":NaN}', '{"on":0}', '[]', '{}', 'x'*1025]:
                self.assertEqual(self.request(body,self.token)[0], 400)
            write.assert_not_called()
    def test_authorized_command_and_generic_bridge_error(self):
        os.environ['HUE_WRITES_ENABLED'] = '1'
        with patch('app.write_state', return_value={'status':'accepted'}) as write:
            self.assertEqual(self.request('{"brightness":30}',self.token), (200,b'{"status":"accepted"}'))
            write.assert_called_once_with({'brightness':30})
        with patch('app.write_state', side_effect=RuntimeError('SECRET')):
            status,body=self.request('{"on":false}',self.token)
            self.assertEqual(status,502); self.assertNotIn(b'SECRET',body)

if __name__ == '__main__': unittest.main()
