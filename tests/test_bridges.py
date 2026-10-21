import copy
import json
import os
from pathlib import Path
import ssl
import tempfile
import unittest
from unittest.mock import MagicMock, patch

import bridge_admin
import bridge_store
import dashboard
import hue_client
import loxone_export
from tests import test_admin

KEY = 'fixture-bridge-key-not-real-1234567890'
IDENTITY = '001788FFFEABCDEF'
LEGACY = '00000000-0000-4000-8000-000000000001'


def resources():
    return [
        {'id':'dev1','type':'device','product_data':{'model_id':'LLC020','product_archetype':'hue_go'}},
        {'id':'dev2','type':'device','product_data':{'model_id':'LWB001','product_archetype':'classic_bulb'}},
        {'id':'dev3','type':'device','product_data':{'model_id':'LOM001','product_archetype':'plug'}},
        {'id':'room1','type':'room','metadata':{'name':'Wohnen & Küche'},'children':[{'rid':'dev1','rtype':'device'},{'rid':'dev2','rtype':'device'},{'rid':'dev3','rtype':'device'}]},
        {'id':LEGACY,'type':'light','metadata':{'name':'Hue Go'},'owner':{'rid':'dev1','rtype':'device'},'on':{'on':True},'dimming':{'brightness':47.04},'color':{'xy':{'x':.4,'y':.3}},'color_temperature':{'mirek':370}},
        {'id':'light2','type':'light','metadata':{'name':'Deckenlicht'},'owner':{'rid':'dev2'},'on':{'on':False},'dimming':{'brightness':25}},
        {'id':'light3','type':'light','metadata':{'name':'Steckdose'},'owner':{'rid':'dev3'},'on':{'on':False}},
    ]


class BridgeTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.registry=self.root/'registry.json'
        doc=json.loads((Path(__file__).resolve().parent.parent/'tests/fixtures/registry.json').read_text())
        key=self.root/'legacy-key';key.write_text(KEY)
        doc['bridges'][0]['key_file']=str(key)
        self.registry.write_text(json.dumps(doc))
        self.env=patch.dict(os.environ,{'HUE_STATE_DIR':str(self.root),'HUE_REGISTRY_FILE':str(self.registry),'HUE_COLOR_ENABLED':'1','HUE_WHITE_ENABLED':'1'})
        self.env.start();bridge_store.read_registry();dashboard.invalidate()
    def tearDown(self):
        self.env.stop();self.temp.cleanup();dashboard.invalidate()
    def identity(self,host='10.200.0.136',identity=IDENTITY):
        return {'host':host,'bridge_id':identity,'bridge_name':'Bridge','model':'BSB002','firmware':'test','certificate_sha256':'AA:BB','tls_verified':True}
    def add(self):
        with patch('bridge_admin.probe',return_value=self.identity()):
            return bridge_admin.add_bridge('Obergeschoss','10.200.0.136')
    def test_private_ip_validation_and_ca_verified_identity_bootstrap(self):
        for invalid in ['127.0.0.1','169.254.1.1','8.8.8.8','localhost','https://10.200.0.1','10.200.0.1:443','::1',None,'224.0.0.1']:
            with self.subTest(invalid=invalid), self.assertRaises(bridge_admin.BridgeError):bridge_admin.local_host(invalid)
        context=MagicMock();sock=context.wrap_socket.return_value.__enter__.return_value
        sock.getpeercert.side_effect=lambda binary_form=False: b'certificate' if binary_form else {'subject':((('commonName',IDENTITY),),)}
        with patch('bridge_admin.tls_context',return_value=context),patch('bridge_admin.socket.create_connection'),patch('bridge_admin.request_document',return_value={'bridgeid':IDENTITY.lower(),'name':'test'}) as request:
            result=bridge_admin.probe('10.200.0.136')
            self.assertEqual(result['bridge_id'],IDENTITY);self.assertTrue(result['tls_verified'])
            self.assertEqual(context.verify_mode,ssl.CERT_REQUIRED)
            self.assertEqual(request.call_args.kwargs['bridge']['bridge_id'],IDENTITY)
            self.assertFalse(request.call_args.kwargs['authenticated'])
        with patch('bridge_admin.tls_context',return_value=MagicMock()),patch('bridge_admin.socket.create_connection',side_effect=ssl.SSLCertVerificationError('bad')),patch('bridge_admin.request_document') as request:
            with self.assertRaises(bridge_admin.BridgeError) as error:bridge_admin.probe('10.200.0.136')
            self.assertEqual(error.exception.code,'bridge_certificate_invalid');request.assert_not_called()
    def test_add_reuses_prepared_bridge_and_preserves_other_lights(self):
        before=bridge_store.read_registry()['bridges'][0]
        first=self.add();second=self.add()
        self.assertEqual(first['id'],'og1');self.assertEqual(first['bridge_id'],IDENTITY)
        doc=bridge_store.read_registry();self.assertEqual(len(doc['bridges']),3);self.assertEqual(doc['bridges'][0],before)
        self.assertNotIn(KEY,json.dumps(first));self.assertNotIn('key_file',json.dumps(second))
        self.assertEqual(self.registry.stat().st_mode & 0o777,0o600)
        self.assertTrue((self.root/'registry.previous.json').is_file())
    def test_pair_requires_link_button_then_stores_key_and_inventories(self):
        self.add()
        with patch('bridge_admin.probe',return_value=self.identity()),patch('bridge_admin.request_document',return_value=[{'error':{'type':101}}]) as request,patch('bridge_admin.request_resources') as read:
            with self.assertRaises(bridge_admin.BridgeError) as error:bridge_admin.pair_bridge('og1')
            self.assertEqual(error.exception.code,'press_link_button');read.assert_not_called()
            self.assertEqual(request.call_args.args,('POST','/api'))
            self.assertFalse((self.root/'bridge-keys/og1.key').exists())
        with patch('bridge_admin.probe',return_value=self.identity()),patch('bridge_admin.request_document',return_value=[{'success':{'username':KEY}}]) as request,patch('bridge_admin.request_resources',return_value=resources()):
            result=bridge_admin.pair_bridge('og1')
        self.assertTrue(result['inventory_ready']);self.assertEqual(result['bridge']['light_count'],3)
        path=self.root/'bridge-keys/og1.key';self.assertEqual(path.read_text(),KEY);self.assertEqual(path.stat().st_mode & 0o777,0o600)
        self.assertNotIn(KEY,json.dumps(result));self.assertNotIn(KEY,self.registry.read_text())
        doc=bridge_store.read_registry();self.assertTrue(doc['bridges'][1]['enabled']);lights=doc['bridges'][1]['lights']
        hue=next(l for l in lights if l['id']==LEGACY);self.assertEqual(hue['model'],'LLC020');self.assertEqual(hue['archetype'],'hue_go');self.assertEqual(hue['room'],'Wohnen & Küche');self.assertIn('temperature',hue['capabilities'])
        plug=next(l for l in lights if l['id']=='light3');self.assertEqual(plug['capabilities'],['on'])
    def test_pair_retry_does_not_create_second_key_and_existing_key_is_reused(self):
        self.add()
        with patch('bridge_admin.probe',return_value=self.identity()),patch('bridge_admin.request_document',return_value=[{'success':{'username':KEY}}]) as request,patch('bridge_admin.request_resources',side_effect=ValueError('SECRET')):
            result=bridge_admin.pair_bridge('og1');self.assertFalse(result['inventory_ready']);self.assertEqual(request.call_count,1)
        with patch('bridge_admin.probe',return_value=self.identity()),patch('bridge_admin.request_document') as request,patch('bridge_admin.request_resources',return_value=resources()):
            result=bridge_admin.pair_bridge('og1');self.assertTrue(result['inventory_ready']);request.assert_not_called()
        eg=bridge_store.read_registry()['bridges'][0]
        with patch('bridge_admin.probe',return_value=self.identity(eg['host'],eg['bridge_id'])),patch('bridge_admin.request_document') as request,patch('bridge_admin.request_resources',return_value=resources()):
            bridge_admin.pair_bridge('eg1');request.assert_not_called()
    def test_scan_preserves_alias_marks_missing_and_excludes_stale_exports(self):
        with patch('bridge_admin.request_resources',return_value=resources()):bridge_admin.scan_bridge('eg1')
        doc=bridge_store.read_registry();light=next(l for l in doc['bridges'][0]['lights'] if l['id']==LEGACY)
        self.assertEqual(light['control_path'],'/hue-go/state')
        self.assertEqual(loxone_export.resolve_path('/api/lights/eg1/light2/state')[1]['id'],'light2')
        with patch('bridge_admin.request_resources',return_value=resources()[:-2]):bridge_admin.scan_bridge('eg1')
        doc=bridge_store.read_registry();self.assertTrue(next(l for l in doc['bridges'][0]['lights'] if l['id']=='light2')['present'] is False)
        self.assertIsNone(loxone_export.resolve_path('/api/lights/eg1/light2/state'))
        with self.assertRaises(ValueError):loxone_export.export_xml(['eg1/light2'],False)
        self.assertEqual(hue_client.default_bridge()['host'],'10.200.0.253')
    def test_invalid_inventory_never_overwrites_registry_and_bulk_status_one_request(self):
        before=self.registry.read_bytes()
        with patch('bridge_admin.request_resources',return_value=[{'type':'light','id':'../secret'}]):
            with self.assertRaises(bridge_admin.BridgeError):bridge_admin.scan_bridge('eg1')
        self.assertEqual(before,self.registry.read_bytes())
        with patch('hue_client.request_resources',return_value=resources()) as request:
            result=hue_client.read_bridge_statuses(bridge_store.read_registry()['bridges'][0])
            self.assertEqual(request.call_count,1);self.assertIsNone(result['light3']['brightness']);self.assertFalse(result['light3']['on'])
        for value in ['../escape','bad/name']:
            with self.assertRaises(ValueError):bridge_store.save_bridge_key(value,KEY)
    def test_repair_creates_new_key_without_overwriting_legacy_secret(self):
        eg=bridge_store.read_registry()['bridges'][0]
        with patch('bridge_admin.probe',return_value=self.identity(eg['host'],eg['bridge_id'])),patch('bridge_admin.request_document',return_value=[{'success':{'username':KEY+'-new'}}]) as request,patch('bridge_admin.request_resources',return_value=resources()):
            result=bridge_admin.pair_bridge('eg1',replace=True)
            self.assertTrue(result['inventory_ready']);request.assert_called_once()
        self.assertEqual(Path(eg['key_file']).read_text(),KEY)
        self.assertEqual((self.root/'bridge-keys/eg1.key').read_text(),KEY+'-new')
        self.assertEqual(hue_client.default_bridge()['key_file'],str(self.root/'bridge-keys/eg1.key'))

    def test_busy_bridge_is_rejected(self):
        lock=bridge_admin.operation_lock('eg1');lock.acquire()
        try:
            with self.assertRaises(bridge_admin.BridgeError) as error:bridge_admin.scan_bridge('eg1')
            self.assertEqual(error.exception.code,'bridge_busy')
        finally:lock.release()


class BridgeEndpointTests(unittest.TestCase):
    setUp=test_admin.AdminTests.setUp
    tearDown=test_admin.AdminTests.tearDown
    request=test_admin.AdminTests.request
    login=test_admin.AdminTests.login
    def test_bridge_endpoints_require_session_csrf_and_sanitize_errors(self):
        with patch('app.bridge_admin.add_bridge') as add:
            self.assertEqual(self.request('/api/admin/bridges/add',{'name':'Test','host':'10.200.0.136'})[0],401);add.assert_not_called()
            self.login()
            self.assertEqual(self.request('/api/admin/bridges/add',{'name':'Test','host':'10.200.0.136'},{'X-CSRF-Token':''})[0],403);add.assert_not_called()
        with patch('app.bridge_admin.add_bridge',side_effect=bridge_admin.BridgeError('bridge_certificate_invalid',502)):
            code,_,body=self.request('/api/admin/bridges/add',{'name':'Test','host':'10.200.0.136'});self.assertEqual(code,502);self.assertEqual(json.loads(body)['error'],'bridge_certificate_invalid')
        with patch('app.bridge_admin.pair_bridge',return_value={'bridge':{'id':'new','light_count':3},'inventory_ready':True}),patch('app.write_state') as write:
            self.assertEqual(self.request('/api/admin/bridges/pair',{'id':'new'})[0],200);write.assert_not_called()
        code,_,body=self.request('/api/admin/bridges');self.assertEqual(code,200);self.assertNotIn(b'key_file',body)
