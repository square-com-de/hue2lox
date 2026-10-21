"""Security boundary regressions; isolated local fixtures, no device access."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import Mock, patch

import app
import hue_client
from tests import test_admin


class StrictJSONTests(unittest.TestCase):
    def test_ambiguous_and_nonstandard_json_rejected(self):
        for body in (b'{"on":true,"on":false}',b'{"brightness":NaN}',
                     b'{"brightness":Infinity}', b'['*2000+b'0'+b']'*2000):
            with self.subTest(body_size=len(body)),self.assertRaises(ValueError):
                app.parse_request_json(body)
        self.assertEqual(app.parse_request_json(b'{"on":false}'),{'on':False})
        text={'name':'escaped " quote, brackets '+'['*100+' and backslash '+chr(92)}
        self.assertEqual(app.parse_request_json(json.dumps(text).encode()),text)

    def test_body_timeout_is_total_not_reset_by_each_byte(self):
        handler=object.__new__(app.Handler)
        handler.server=Mock(request_timeout=1)
        handler.connection=Mock()
        handler.rfile=Mock()
        handler.rfile.read1.return_value=b'x'
        with patch('app.time.monotonic',side_effect=[0,.4,.8,1.2]):
            with self.assertRaisesRegex(ValueError,'deadline'):
                handler.read_body(3)
        self.assertEqual(handler.rfile.read1.call_count,2)

    def test_excessively_nested_bridge_response_is_sanitized(self):
        with patch('hue_client.tls_context'),patch('hue_client.BridgeConnection') as connection:
            response=connection.return_value.getresponse.return_value
            response.status=200;response.read.return_value=b'['*2000+b'0'+b']'*2000
            with self.assertRaises(hue_client.BridgeRequestError):
                hue_client.request_document('GET','/api/config',bridge={'host':'192.0.2.1','bridge_id':'fixture'},authenticated=False)
            connection.return_value.close.assert_called_once()


class LoginInputTests(unittest.TestCase):
    setUp=test_admin.AdminTests.setUp
    tearDown=test_admin.AdminTests.tearDown
    request=test_admin.AdminTests.request

    def test_deep_login_json_returns_json_400_and_service_remains_available(self):
        import http.client
        connection=http.client.HTTPConnection('127.0.0.1',self.server.server_port,timeout=3)
        raw=b'{"username":"admin","password":'+b'['*2000+b'0'+b']'*2000+b'}'
        connection.request('POST','/api/admin/login',raw,{'Host':'hue2lox.test:8443','Content-Type':'application/json'})
        response=connection.getresponse()
        self.assertEqual(response.status,400)
        self.assertEqual(json.loads(response.read())['error'],'invalid_request')
        connection.close()
        self.assertEqual(self.request('/health')[0],200)


class CertificatePermissionsTests(unittest.TestCase):
    def test_private_key_permissions_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/'scripts').mkdir()
            script=root/'scripts/create-cert.sh'
            shutil.copyfile(Path(__file__).resolve().parent.parent/'scripts/create-cert.sh',script)
            env=dict(os.environ,HUE2LOX_BIND_IP='127.0.0.1')
            first=subprocess.run(['sh',str(script)],env=env,capture_output=True)
            self.assertEqual(first.returncode,0)
            key=root/'certs/server.key';before=key.read_bytes()
            self.assertEqual(key.stat().st_mode&0o777,0o600)
            self.assertEqual((root/'certs').stat().st_mode&0o777,0o700)
            second=subprocess.run(['sh',str(script)],env=env,capture_output=True)
            self.assertNotEqual(second.returncode,0)
            self.assertEqual(key.read_bytes(),before)
