import copy
import json
import os
from pathlib import Path
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET
import bridge_admin
import bridge_store
import scenes
import loxone_export
from tests import test_admin
from tests import test_bridges


def resources():
    return test_bridges.resources()+[
        {'type':'scene','id':'scene1','metadata':{'name':'Abend & <Ruhe>'},'group':{'rid':'room1','rtype':'room'},'actions':[{'target':{'rid':test_bridges.LEGACY,'rtype':'light'},'action':{'on':{'on':True}}}]},
        {'type':'zone','id':'zone1','metadata':{'name':'Ganzes Haus'}},
        {'type':'scene','id':'scene2','metadata':{'name':'Lesen'},'group':{'rid':'zone1','rtype':'zone'},'actions':[{'target':{'rid':'light2','rtype':'light'},'action':{}}]},
        {'type':'smart_scene','id':'smart1','metadata':{'name':'Natürliches Licht'}}]

class SceneTests(unittest.TestCase):
    setUp=test_bridges.BridgeTests.setUp
    tearDown=test_bridges.BridgeTests.tearDown
    def scan(self):
        with patch('bridge_admin.request_resources',return_value=resources()),patch('bridge_admin.request_document') as write:
            bridge_admin.scan_bridge('eg1');write.assert_not_called()
    def test_inventory_room_zone_and_read_only_rescan(self):
        self.scan();items=scenes.available_scenes();self.assertEqual(len(items),2)
        self.assertEqual({s['room'] for s in items},{'Wohnen & Küche','Ganzes Haus'})
        self.assertEqual(bridge_admin.list_bridges()[0]['scene_count'],2)
        changed=resources();changed=[r for r in changed if r.get('id')!='scene2'];next(r for r in changed if r.get('id')=='scene1')['metadata']['name']='Neu'
        with patch('bridge_admin.request_resources',return_value=changed):bridge_admin.scan_bridge('eg1')
        items={s['key']:s for s in scenes.available_scenes()}
        self.assertEqual(items['eg1/scene1']['name'],'Neu');self.assertNotIn('eg1/scene2',items)
        self.assertIsNone(scenes.resolve_path('/api/scenes/eg1/scene2/recall'))
        with self.assertRaises(ValueError):loxone_export.export_xml(['eg1/scene2'],False,kind='scenes')
    def test_failed_inventory_preserves_previous_scenes_and_lights(self):
        self.scan();before=self.registry.read_bytes();broken=resources();broken.append(copy.deepcopy(next(r for r in broken if r.get('type')=='scene')))
        with patch('bridge_admin.request_resources',return_value=broken):
            with self.assertRaises(bridge_admin.BridgeError):bridge_admin.scan_bridge('eg1')
        self.assertEqual(self.registry.read_bytes(),before)
    def test_bridge_scope_and_hidden_lamp_warning(self):
        self.scan();bridge_admin.manage_light('eg1',test_bridges.LEGACY,'ignore')
        item=next(s for s in scenes.available_scenes() if s['key']=='eg1/scene1');self.assertEqual(item['hidden_light_count'],1);self.assertTrue(item['available'])
        def change(doc):
            second=doc['bridges'][1];second['enabled']=True;second['scenes']=copy.deepcopy(doc['bridges'][0]['scenes'])
        bridge_store.update_registry(change)
        target=scenes.resolve_path('/api/scenes/og1/scene1/recall');self.assertEqual(target[0]['id'],'og1')
        for path in ['/api/scenes/unknown/scene1/recall','/api/scenes/eg1/../../recall','/api/scenes/eg1/scene1/delete']:
            self.assertIsNone(scenes.resolve_path(path))
    def test_export_is_digital_ein_only_and_escapes_names(self):
        self.scan();root=ET.fromstring(loxone_export.export_xml(['eg1/scene1','eg1/scene2'],False,kind='scenes'))
        commands=root.findall('VirtualOutCmd');self.assertEqual(len(commands),2)
        for cmd in commands:
            self.assertEqual(cmd.get('CmdOnMethod'),'PUT');self.assertEqual(cmd.get('CmdOnPost'),'{"recall":true}')
            for field in ['CmdOff','CmdOffHTTP','CmdOffPost']:self.assertEqual(cmd.get(field),'')
            self.assertEqual(cmd.get('Analog'),'false');self.assertEqual(cmd.get('Repeat'),'0')
            self.assertIn('DEIN_HUE2LOX_TOKEN',cmd.get('CmdOnHTTP'))
        self.assertIn('Abend & <Ruhe>',str([c.get('Title') for c in commands]))
        token='fixture-scene-token-not-real'
        self.assertIn(token.encode(),loxone_export.export_xml(['eg1/scene1'],True,token,kind='scenes'))
        with self.assertRaises(ValueError):loxone_export.export_xml(['eg1/scene1'],False)
    def test_ignore_restore_persists_and_blocks_control_export(self):
        self.scan()
        with patch('bridge_admin.request_document') as write:
            bridge_admin.manage_scene('eg1','scene1','ignore')
            self.scan()
            item=next(s for s in scenes.available_scenes() if s['key']=='eg1/scene1')
            self.assertTrue(item['ignored']);self.assertFalse(item['available'])
            self.assertEqual(bridge_admin.list_bridges()[0]['scene_count'],1)
            self.assertIsNone(scenes.resolve_path('/api/scenes/eg1/scene1/recall'))
            with self.assertRaises(ValueError):loxone_export.export_xml(['eg1/scene1'],False,kind='scenes')
            bridge_admin.manage_scene('eg1','scene1','ignore',False)
            self.assertIsNotNone(scenes.resolve_path('/api/scenes/eg1/scene1/recall'))
            write.assert_not_called()
    def test_local_remove_reappears_on_scan_without_hue_delete(self):
        self.scan()
        with patch('bridge_admin.request_document') as write:
            bridge_admin.manage_scene('eg1','scene1','remove')
            self.assertNotIn('eg1/scene1',[s['key'] for s in scenes.available_scenes()])
            self.assertIsNone(scenes.resolve_path('/api/scenes/eg1/scene1/recall'))
            with self.assertRaises(ValueError):loxone_export.export_xml(['eg1/scene1'],False,kind='scenes')
            self.scan();self.assertIsNotNone(scenes.resolve_path('/api/scenes/eg1/scene1/recall'));write.assert_not_called()
    def test_successful_empty_scene_inventory_purges_old_entries(self):
        self.scan();bridge_admin.manage_scene('eg1','scene1','ignore')
        with patch('bridge_admin.request_resources',return_value=test_bridges.resources()):bridge_admin.scan_bridge('eg1')
        self.assertEqual(scenes.available_scenes(),[])
        self.assertEqual(bridge_admin.bridge_record('eg1')['scenes'],[])
    def test_scene_management_validation_and_bridge_lock(self):
        self.scan();before=self.registry.read_bytes()
        for bridge,reference,option in [('eg1','unknown',True),('unknown','scene1',True),('eg1','scene1','true')]:
            with self.assertRaises(bridge_admin.BridgeError):bridge_admin.manage_scene(bridge,reference,'ignore',option)
            self.assertEqual(self.registry.read_bytes(),before)
        lock=bridge_admin.operation_lock('eg1');lock.acquire()
        try:
            with self.assertRaises(bridge_admin.BridgeError) as error:bridge_admin.manage_scene('eg1','scene1','remove')
            self.assertEqual(error.exception.status,409)
        finally:lock.release()
    def test_malformed_scene_inventory_rejected(self):
        for field,value in [('id','../escape'),('group',{'rid':[], 'rtype':'room'}),('actions',[{'target':{'rid':'../escape','rtype':'light'}}]),('metadata',[])]:
            with self.subTest(field=field):
                broken=copy.deepcopy(next(r for r in resources() if r.get('type')=='scene'));broken[field]=value
                with self.assertRaises(ValueError):scenes.collect([broken])
        with self.assertRaises(ValueError):scenes.collect([None])
    def test_recall_exact_payload_and_hue_error(self):
        bridge={'id':'eg1'};scene={'id':'scene1'}
        with patch('scenes.request_document',return_value={'errors':[],'data':[{'rid':'scene1','rtype':'scene'}]}) as request:
            result=scenes.recall(bridge,scene);self.assertTrue(result['accepted'])
            request.assert_called_once_with('PUT','/clip/v2/resource/scene/scene1',payload={'recall':{'action':'active'}},bridge=bridge)
        for document in [{'errors':[{'description':'PRIVATE'}],'data':[]},{'errors':[],'data':[]},{'errors':[],'data':[{'rid':'wrong','rtype':'scene'}]}]:
            with patch('scenes.request_document',return_value=document):
                with self.assertRaises(ValueError):scenes.recall(bridge,scene)

class SceneAPITests(unittest.TestCase):
    request=test_admin.AdminTests.request
    login=test_admin.AdminTests.login
    def setUp(self):
        test_admin.AdminTests.setUp(self)
        self.registry=self.directory/'registry.json'
        doc=json.loads((Path(__file__).resolve().parent.parent/'tests/fixtures/registry.json').read_text())
        doc['bridges'][0]['scenes']=scenes.collect(resources());self.registry.write_text(json.dumps(doc))
        self.registry_env=patch.dict(os.environ,{'HUE_REGISTRY_FILE':str(self.registry),'HUE_STATE_DIR':str(self.directory)});self.registry_env.start()
    def tearDown(self):
        self.registry_env.stop();test_admin.AdminTests.tearDown(self)
    def test_admin_session_export_csrf_and_no_scene_creation(self):
        self.assertEqual(self.request('/api/admin/scenes')[0],401)
        self.assertEqual(self.request('/api/admin/scenes/export',{'scenes':['eg1/scene1']})[0],401)
        self.login();code,_,body=self.request('/api/admin/scenes');self.assertEqual(code,200);self.assertNotIn(b'key_file',body)
        with patch('scenes.request_document') as write:
            self.assertEqual(self.request('/api/admin/scenes/export',{'scenes':['eg1/scene1']},{'X-CSRF-Token':''})[0],403)
            code,_,body=self.request('/api/admin/scenes/export',{'scenes':['eg1/scene1']});self.assertEqual(code,200);self.assertEqual(len(ET.fromstring(body).findall('VirtualOutCmd')),1)
            self.assertEqual(self.request('/api/admin/scenes/add',{})[0],404);write.assert_not_called()
    def test_bearer_flag_and_payload_gate_all_before_hue_request(self):
        path='/api/scenes/eg1/scene1/recall';auth={'Authorization':'Bearer '+'t'*48}
        with patch('scenes.recall',return_value={'status':'ok','accepted':True}) as recall:
            self.assertEqual(self.request(path,{'recall':True},method='PUT')[0],401)
            with patch.dict(os.environ,{'HUE_WRITES_ENABLED':'0'}):self.assertEqual(self.request(path,{'recall':True},auth,method='PUT')[0],403)
            for payload in [{},{'recall':False},{'recall':1},{'recall':True,'on':True},{'recall':{'action':'active'}}]:
                self.assertEqual(self.request(path,payload,auth,method='PUT')[0],400)
            self.assertEqual(self.request('/api/scenes/eg1/unknown/recall',{'recall':True},auth,method='PUT')[0],404)
            recall.assert_not_called()
            self.assertEqual(self.request(path,{'recall':True},auth,method='PUT')[0],200);recall.assert_called_once()
    def test_scene_management_requires_session_csrf_and_blocks_recall(self):
        body={'bridge_id':'eg1','scene_id':'scene1'}
        for action in ('ignore','remove'):
            self.assertEqual(self.request('/api/admin/scenes/'+action,body)[0],401)
        self.login()
        with patch('scenes.recall') as recall:
            for action in ('ignore','remove'):
                path='/api/admin/scenes/'+action
                self.assertEqual(self.request(path,body,{'X-CSRF-Token':''})[0],403)
                self.assertEqual(self.request(path,body,{'Origin':'https://evil.test'})[0],403)
            self.assertEqual(self.request('/api/admin/scenes/ignore',{**body,'ignored':'true'})[0],400)
            self.assertEqual(self.request('/api/admin/scenes/ignore',body)[0],200)
            self.assertEqual(self.request('/api/scenes/eg1/scene1/recall',{'recall':True},{'Authorization':'Bearer '+'t'*48},method='PUT')[0],404)
            self.assertEqual(self.request('/api/admin/scenes/remove',body)[0],200)
            recall.assert_not_called()
    def test_hue_errors_sanitized(self):
        with patch('scenes.recall',side_effect=ValueError('PRIVATE_BRIDGE_SECRET')):
            code,_,body=self.request('/api/scenes/eg1/scene1/recall',{'recall':True},{'Authorization':'Bearer '+'t'*48},method='PUT')
            self.assertEqual(code,502);self.assertNotIn(b'PRIVATE',body)
