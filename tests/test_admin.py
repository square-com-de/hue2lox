import http.client
import json
import os
from pathlib import Path
import tempfile
import threading
import time
import unittest
from unittest.mock import patch
from http.server import ThreadingHTTPServer
import xml.etree.ElementTree as ET
import admin_auth
import app
import loxone_export


class AdminTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.directory=Path(self.temp.name)
        self.password='test-only-long-password'
        auth=self.directory/'auth.json';auth.write_text(json.dumps(admin_auth.create_credentials('admin',self.password)))
        token=self.directory/'token';token.write_text('t'*48)
        admin_auth.SESSIONS.clear();admin_auth.ATTEMPTS.clear()
        self.env=patch.dict(os.environ,{'HUE_REGISTRY_FILE':str(Path(__file__).resolve().parent.parent/'tests/fixtures/registry.json'),'HUE_ADMIN_AUTH_FILE':str(auth),'HUE_CONTROL_TOKEN_FILE':str(token),'HUE_PUBLIC_URL':'https://hue2lox.test:8443','HUE_COLOR_ENABLED':'1','HUE_WHITE_ENABLED':'1','HUE_WRITES_ENABLED':'1'})
        self.env.start();self.server=ThreadingHTTPServer(('127.0.0.1',0),app.Handler)
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start()
        self.cookie=None;self.csrf=None
    def tearDown(self):
        self.server.shutdown();self.server.server_close();self.thread.join();self.env.stop();self.temp.cleanup();admin_auth.SESSIONS.clear();admin_auth.ATTEMPTS.clear()
    def request(self,path,body=None,headers=None,method=None):
        h={'Host':'hue2lox.test:8443'}
        if self.cookie:h['Cookie']=self.cookie
        if self.csrf:h['X-CSRF-Token']=self.csrf
        if body is not None:h['Content-Type']='application/json';body=json.dumps(body)
        h.update(headers or {})
        c=http.client.HTTPConnection('127.0.0.1',self.server.server_port,timeout=5)
        c.request(method or ('POST' if body is not None else 'GET'),path,body=body,headers=h)
        r=c.getresponse();result=(r.status,dict(r.getheaders()),r.read());c.close();return result
    def login(self):
        code,h,b=self.request('/api/admin/login',{'username':'admin','password':self.password})
        self.assertEqual(code,200);self.cookie=h['Set-Cookie'].split(';')[0];self.csrf=json.loads(b)['csrf'];return h
    def test_no_token_or_exports_without_login_or_with_bearer(self):
        for path,body in [('/api/admin/lights',None),('/api/admin/token',{}),('/api/admin/export',{'lights':['eg1/00000000-0000-4000-8000-000000000001'],'include_token':True}),('/api/overview',None)]:
            code,_,b=self.request(path,body,{'Authorization':'Bearer '+'t'*48});self.assertEqual(code,401);self.assertNotIn(b't'*48,b)
    def test_secure_cookie_token_csrf_and_logout(self):
        h=self.login();cookie=h['Set-Cookie']
        for flag in ['HttpOnly','Secure','SameSite=Strict','Path=/']:self.assertIn(flag,cookie)
        self.assertTrue(cookie.startswith('__Host-'))
        for header in [{'X-CSRF-Token':''},{'Origin':'https://evil.test'},{'Host':'evil.test'},{'Sec-Fetch-Site':'cross-site'}]:self.assertEqual(self.request('/api/admin/token',{},header)[0],403)
        code,h,b=self.request('/api/admin/token',{});self.assertEqual(code,200);self.assertEqual(json.loads(b)['token'],'t'*48);self.assertEqual(h['Cache-Control'],'no-store')
        code,_,b=self.request('/api/admin/lights');self.assertEqual(code,200);self.assertNotIn(b't'*48,b);self.assertNotIn(b'key_file',b)
        self.assertEqual(self.request('/api/admin/logout',{})[0],200)
        self.assertEqual(self.request('/api/admin/token',{})[0],401)
    def test_plain_http_public_url_uses_cookie_browsers_accept(self):
        with patch.dict(os.environ,{'HUE_PUBLIC_URL':'http://hue2lox.test:8443'}):
            self.cookie=None
            code,h,_=self.request('/api/admin/login',{'username':'admin','password':self.password})
            self.assertEqual(code,200);cookie=h['Set-Cookie']
            self.assertTrue(cookie.startswith('hue2lox_session='));self.assertNotIn('Secure',cookie)
            for flag in ['HttpOnly','SameSite=Strict','Path=/']:self.assertIn(flag,cookie)
            self.cookie=cookie.split(';')[0];self.csrf=None
            self.assertEqual(self.request('/api/admin/lights')[0],200)
    def test_rate_limit_and_expiration(self):
        for _ in range(5):self.assertEqual(self.request('/api/admin/login',{'username':'admin','password':'incorrect'})[0],401)
        self.assertEqual(self.request('/api/admin/login',{'username':'admin','password':self.password})[0],429)
        admin_auth.ATTEMPTS.clear();self.login()
        for entry in admin_auth.SESSIONS.values():entry['seen']=time.monotonic()-admin_auth.IDLE-1
        self.assertEqual(self.request('/api/admin/token',{})[0],401)
    def test_xml_selection_headers_escaping_and_no_lamp_writes(self):
        data=loxone_export.registry();bridge=data['bridges'][0];original=bridge['lights'][0]
        original['name']='Go & <Wohnen> "Test"';second=dict(original,id='another-light',name='Zweite Lampe',control_path='');bridge['lights'].append(second)
        path=self.directory/'registry.json';path.write_text(json.dumps(data))
        with patch.dict(os.environ,{'HUE_REGISTRY_FILE':str(path)}),patch('app.write_state') as write:
            self.login();keys=[bridge['id']+'/'+l['id'] for l in bridge['lights']]
            code,h,b=self.request('/api/admin/export',{'lights':keys,'include_token':True,'variants':dict(zip(keys,['switch','dim']))})
            self.assertEqual(code,200);root=ET.fromstring(b);self.assertEqual(root.tag,'VirtualOut');commands=root.findall('VirtualOutCmd');self.assertEqual(len(commands),2)
            self.assertEqual(root.get('Address'),'https://hue2lox.test:8443')
            self.assertEqual(commands[0].get('Title'),'Go & <Wohnen> "Test" · Ein/Aus')
            self.assertEqual(commands[0].get('CmdOnHTTP'),'Authorization: Bearer '+'t'*48+r'\r\nContent-Type: application/json')
            self.assertEqual(commands[0].get('CmdOnMethod'),'PUT');self.assertEqual(commands[1].get('CmdOnPost'),'{"brightness":<v>}');self.assertEqual(commands[1].get('CmdOff'),'')
            self.assertIn(loxone_export.lights()[0]['path'],b.decode());self.assertNotIn('/api/lights/',b.decode())
            self.assertEqual(h['Cache-Control'],'no-store');self.assertIn('attachment',h['Content-Disposition'])
            code,_,b=self.request('/api/admin/export',{'lights':[keys[0]],'include_token':False});self.assertEqual(code,200);self.assertNotIn(b't'*48,b);self.assertIn(b'DEIN_HUE2LOX_TOKEN',b)
            for body in [{'lights':[]},{'lights':['unknown']},{'lights':[keys[0],keys[0]]},{'lights':keys,'include_token':'true'}]:self.assertEqual(self.request('/api/admin/export',body)[0],400)
            write.assert_not_called()
    def test_registered_generic_control_route_requires_existing_token(self):
        path='/api/lights/eg1/00000000-0000-4000-8000-000000000001/state'
        with patch('app.write_state',return_value={'status':'accepted'}) as write:
            self.assertEqual(self.request(path,{'on':True},method='PUT')[0],401)
            code,_,_=self.request(path,{'on':True},{'Authorization':'Bearer '+'t'*48},method='PUT');self.assertEqual(code,200)
            self.assertEqual(write.call_args.kwargs['light_id'],'00000000-0000-4000-8000-000000000001')
            self.assertEqual(self.request('/api/lights/og1/unknown/state',{'on':True},method='PUT')[0],404)

if __name__=='__main__':unittest.main()
