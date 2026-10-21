import http.client
import json
import unittest
from unittest.mock import MagicMock, patch

import hue_client
import bridge_admin
from tests import test_admin


class BridgeTransportTests(unittest.TestCase):
    def request(self, connection):
        with patch('hue_client.tls_context'), patch('hue_client.BridgeConnection',return_value=connection):
            return hue_client.request_document('GET','/api/config',bridge={'host':'192.0.2.1','bridge_id':'fixture'},authenticated=False)

    def test_transport_and_protocol_errors_are_sanitized(self):
        for failure in [TimeoutError('SECRET'), OSError('SECRET'),
                        http.client.RemoteDisconnected('SECRET'),
                        http.client.BadStatusLine('SECRET'),
                        http.client.IncompleteRead(b'SECRET',20)]:
            with self.subTest(kind=type(failure).__name__):
                conn=MagicMock();conn.getresponse.side_effect=failure
                with self.assertRaises(hue_client.BridgeRequestError) as error:self.request(conn)
                self.assertEqual(str(error.exception),'bridge request failed')
                conn.close.assert_called_once()

    def test_response_read_and_json_errors_are_sanitized(self):
        for body in [b'SECRET', b'\xff', b'x'*4194305]:
            conn=MagicMock();response=conn.getresponse.return_value
            response.status=200;response.read.return_value=body
            with self.assertRaises(hue_client.BridgeRequestError):self.request(conn)
            conn.close.assert_called_once()
        conn=MagicMock();conn.getresponse.return_value.status=200
        conn.getresponse.return_value.read.side_effect=http.client.IncompleteRead(b'SECRET',5)
        with self.assertRaises(hue_client.BridgeRequestError):self.request(conn)

    def test_unexpected_resource_shapes_are_sanitized(self):
        for document in [None, [], {'errors':[], 'data':None}, {'errors':[], 'data':[None]}]:
            with patch('hue_client.request_document',return_value=document):
                with self.assertRaises(hue_client.BridgeRequestError):
                    hue_client.request_light('GET',bridge={},target_light='fixture')
                with self.assertRaises(hue_client.BridgeRequestError):hue_client.request_resources({})

    def test_unconfigured_legacy_never_uses_a_private_default(self):
        with patch.dict('os.environ',{},clear=True):
            with self.assertRaises(ValueError):hue_client.default_bridge()


class BridgeErrorAPITests(unittest.TestCase):
    setUp=test_admin.AdminTests.setUp
    tearDown=test_admin.AdminTests.tearDown
    request=test_admin.AdminTests.request
    login=test_admin.AdminTests.login

    def test_scan_failure_returns_json_and_releases_operation_lock(self):
        self.login()
        bridge={'id':'fixture','host':'192.0.2.1','key_file':str(self.directory/'auth.json')}
        with patch('bridge_admin.bridge_record',return_value=bridge), patch('bridge_admin.request_resources',side_effect=hue_client.BridgeRequestError('bridge request failed')):
            for _ in range(2):
                code,headers,body=self.request('/api/admin/bridges/scan',{'id':'fixture'},headers={'Origin':'https://hue2lox.test:8443','X-CSRF-Token':self.csrf})
                self.assertEqual(code,502)
                self.assertEqual(json.loads(body)['error'],'inventory_unavailable')
                self.assertIn('application/json',headers['Content-Type'])


if __name__=='__main__':unittest.main()
