"""Direct desktop start: no URL/TLS environment and a remapped host port."""
import json
import os
import unittest
from unittest.mock import patch
from tests import test_admin
import admin_auth
import public_address

class DesktopLoginTests(unittest.TestCase):
    request = test_admin.AdminTests.request
    def setUp(self):
        test_admin.AdminTests.setUp(self)
        self.direct_env=patch.dict(os.environ)
        self.direct_env.start()
        for key in ('HUE_PUBLIC_URL','TLS_CERT','TLS_KEY'):os.environ.pop(key,None)
        self.password='admin'
        (self.directory/'auth.json').write_text(json.dumps(admin_auth.create_credentials('admin','admin')))

    def tearDown(self):
        self.direct_env.stop()
        test_admin.AdminTests.tearDown(self)

    def test_default_login_remapped_port_session_and_export_address(self):
        headers={'Host':'localhost:18444','Origin':'http://localhost:18444','Sec-Fetch-Site':'same-origin'}
        code,h,b=self.request('/api/admin/login',{'username':'admin','password':'admin'},headers)
        self.assertEqual(code,200,b)
        self.assertNotIn('Secure',h['Set-Cookie']);self.assertTrue(h['Set-Cookie'].startswith('hue2lox_session='))
        self.cookie=h['Set-Cookie'].split(';')[0];self.csrf=json.loads(b)['csrf']
        self.assertEqual(self.request('/api/admin/session',headers=headers)[0],200)
        code,_,body=self.request('/api/admin/lights',headers=headers)
        self.assertEqual(code,200)
        self.assertIn(b'http://localhost:18444',body)
        self.assertEqual(self.request('/api/admin/logout',{},headers)[0],200)
        self.assertEqual(self.request('/api/admin/session',headers=headers)[0],401)

    def test_default_rejects_cross_origin_and_dns_rebinding(self):
        for headers in [
            {'Host':'localhost:8443','Origin':'http://evil.example'},
            {'Host':'evil.example:8443','Origin':'http://evil.example:8443'},
            {'Host':'localhost:8443','Origin':'http://localhost:8443','Sec-Fetch-Site':'cross-site'},
            {'Host':'localhost:8443','Origin':'https://localhost:8443'},
            {'Host':'127.0.0.1:8443','Origin':'http://localhost:8443'}]:
            code,_,body=self.request('/api/admin/login',{'username':'admin','password':'admin'},headers)
            self.assertEqual(code,403);self.assertEqual(json.loads(body)['error'],'invalid_origin')

    def test_wrong_password_is_401_not_origin_error(self):
        code,_,body=self.request('/api/admin/login',{'username':'admin','password':'wrong'}, {'Host':'127.0.0.1:8443','Origin':'http://127.0.0.1:8443'})
        self.assertEqual(code,401);self.assertNotEqual(json.loads(body)['error'],'invalid_origin')

    def test_direct_lan_and_ipv6_and_context_isolation(self):
        for host in ('192.168.1.50:8443','[::1]:18444','localhost:18444'):
            code,_,body=self.request('/api/admin/login',{'username':'admin','password':'admin'},{'Host':host,'Origin':'http://'+host})
            self.assertEqual(code,200,body)
        self.assertIsNone(public_address.request_url.get())
        for host in ('evil.example','localhost@evil.example','0.0.0.0:8443','224.0.0.1','localhost/path'):
            with self.assertRaises(ValueError):public_address.direct_url(host)
        self.assertEqual(public_address.direct_url('localhost:18444',True),'https://localhost:18444')

