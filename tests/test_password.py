import json
import os
from pathlib import Path
import unittest
from unittest.mock import patch
import admin_auth
from tests import test_admin


class PasswordTests(unittest.TestCase):
    setUp=test_admin.AdminTests.setUp
    tearDown=test_admin.AdminTests.tearDown
    request=test_admin.AdminTests.request
    login=test_admin.AdminTests.login
    def test_admin_default_and_short_password_policy(self):
        data=admin_auth.create_credentials('admin','admin')
        self.assertEqual(data['username'],'admin');self.assertNotEqual(data['hash'],'admin')
        for value in ['', '1234']:
            with self.assertRaises(ValueError):admin_auth.create_credentials('admin',value)
    def test_change_requires_session_csrf_and_current_password(self):
        body={'current_password':self.password,'new_password':'admin'}
        self.assertEqual(self.request('/api/admin/password',body)[0],401)
        self.login()
        path=admin_auth.credential_path();before=path.read_bytes()
        self.assertEqual(self.request('/api/admin/password',body,{'X-CSRF-Token':''})[0],403)
        self.assertEqual(self.request('/api/admin/password',{'current_password':'wrong','new_password':'admin'})[0],403)
        self.assertEqual(self.request('/api/admin/password',{'current_password':self.password,'new_password':'1234'})[0],400)
        self.assertEqual(path.read_bytes(),before)
        self.assertEqual(self.request('/api/admin/session')[0],200)
    def test_password_change_revokes_all_sessions_and_accepts_admin(self):
        self.login();first_cookie=self.cookie;first_csrf=self.csrf
        self.cookie=None;self.csrf=None
        self.login();second_cookie=self.cookie
        code,headers,body=self.request('/api/admin/password',{'current_password':self.password,'new_password':'admin'},{'Cookie':first_cookie,'X-CSRF-Token':first_csrf})
        self.assertEqual(code,200);self.assertIn('Max-Age=0',headers['Set-Cookie'])
        self.assertFalse(admin_auth.SESSIONS)
        for cookie in [first_cookie,second_cookie]:self.assertEqual(self.request('/api/admin/token',{}, {'Cookie':cookie})[0],401)
        self.assertEqual(self.request('/api/admin/login',{'username':'admin','password':self.password})[0],401)
        code,_,_=self.request('/api/admin/login',{'username':'admin','password':'admin'});self.assertEqual(code,200)
        self.assertEqual(admin_auth.credential_path().stat().st_mode & 0o777,0o600)
        stored=json.loads(admin_auth.credential_path().read_text());self.assertEqual(stored['algorithm'],'pbkdf2-sha256-600000');self.assertNotEqual(stored['hash'],'admin')
    def test_failed_write_preserves_password_and_session(self):
        self.login();before=admin_auth.credential_path().read_bytes()
        with patch('admin_auth.save_credentials',side_effect=OSError('secret path')):
            code,_,body=self.request('/api/admin/password',{'current_password':self.password,'new_password':'admin'})
            self.assertEqual(code,503);self.assertNotIn(b'secret path',body)
        self.assertEqual(before,admin_auth.credential_path().read_bytes());self.assertEqual(self.request('/api/admin/session')[0],200)
    def test_password_change_attempts_are_limited(self):
        self.login()
        for _ in range(5):self.assertEqual(self.request('/api/admin/password',{'current_password':'wrong','new_password':'admin'})[0],403)
        self.assertEqual(self.request('/api/admin/password',{'current_password':self.password,'new_password':'admin'})[0],429)

    def test_cli_reset_revokes_active_session_without_restart(self):
        self.login()
        admin_auth.save_credentials(admin_auth.credential_path(),admin_auth.create_credentials('admin','reset-private-password'))
        self.assertEqual(self.request('/api/admin/token',{})[0],401)
        self.assertFalse(admin_auth.SESSIONS)
        code,_,_=self.request('/api/admin/login',{'username':'admin','password':'reset-private-password'})
        self.assertEqual(code,200)

    def test_cli_default_reset_preserves_admin_login_and_revokes_session(self):
        import subprocess
        import sys
        from pathlib import Path
        self.login()
        result=subprocess.run([sys.executable,str(Path(__file__).resolve().parent.parent/'src/admin_auth.py'),
                               str(admin_auth.credential_path()),'--default'],capture_output=True)
        self.assertEqual(result.returncode,0)
        self.assertEqual(self.request('/api/admin/token',{})[0],401)
        self.assertEqual(self.request('/api/admin/login',{'username':'admin','password':'admin'})[0],200)

    def test_missing_credentials_invalidate_session(self):
        self.login()
        admin_auth.credential_path().unlink()
        self.assertEqual(self.request('/api/admin/token',{})[0],401)

if __name__=='__main__':unittest.main()
