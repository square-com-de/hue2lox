"""Isolated scene-switch replays; no clocks, delays, Hue connections or hardware."""
import copy
import json
import threading
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET
import bridge_store
import bridge_admin
import scenes
import scene_switch
import loxone_export
from tests import test_bridges, test_scenes


def configure(bridge_id,scene_id,group_id):
    bridge=next(b for b in bridge_store.read_registry()['bridges'] if b['id']==bridge_id)
    scene=next(s for s in bridge['scenes'] if s['id']==scene_id)
    group=next((g for g in scene_switch.describe(bridge,scene)['groups'] if g['id']==group_id),{})
    scene_switch.configure(bridge_id,scene_id,group_id,group.get('confirmation'))


def inventory():
    result=test_scenes.resources()
    room=next(r for r in result if r['id']=='room1')
    room['services']=[{'rid':'group1','rtype':'grouped_light'}]
    zone=next(r for r in result if r['id']=='zone1')
    zone.update(services=[{'rid':'group2','rtype':'grouped_light'}],children=[{'rid':'light2','rtype':'light'}])
    result.extend([{'id':'group1','type':'grouped_light','owner':{'rid':'room1','rtype':'room'}},{'id':'group2','type':'grouped_light','owner':{'rid':'zone1','rtype':'zone'}}])
    base=next(r for r in result if r.get('type')=='scene')
    for reference in ('sceneB','sceneC'):
        result.append({**copy.deepcopy(base),'id':reference})
    return result


class SwitchTests(unittest.TestCase):
    setUpBase=test_bridges.BridgeTests.setUp
    tearDownBase=test_bridges.BridgeTests.tearDown
    def setUp(self):
        self.setUpBase();scene_switch._owners.clear()
        with patch('bridge_admin.request_resources',return_value=inventory()):bridge_admin.scan_bridge('eg1')
        for sid in ('scene1','sceneB','sceneC'):configure('eg1',sid,'room1')
        configure('eg1','scene2','zone1')
        self.calls=[]
        def response(method,path,**kwargs):
            self.calls.append((path,kwargs['payload']))
            rid=path.rsplit('/',1)[1];kind=path.split('/')[-2]
            return {'errors':[],'data':[{'rid':rid,'rtype':kind}]}
        self.transport=patch('scene_switch.request_document',side_effect=response);self.transport.start()
        self.recall=patch('scenes.request_document',side_effect=response);self.recall.start()
    def tearDown(self):
        self.recall.stop();self.transport.stop();scene_switch._owners.clear();self.tearDownBase()
    def command(self,sid,on):
        bridge,scene=scenes.resolve_path('/api/scenes/eg1/'+sid+'/state')
        return scene_switch.control(bridge,scene,on)
    def test_both_scene_change_orders_and_final_off(self):
        for off_first in (True,False):
            scene_switch._owners.clear();self.calls.clear();self.command('scene1',True)
            if off_first:self.command('scene1',False)
            self.command('sceneB',True)
            if not off_first:self.assertTrue(self.command('scene1',False)['ignored'])
            self.assertEqual(self.calls[-1][0],'/clip/v2/resource/scene/sceneB')
            self.command('sceneB',False)
            self.assertEqual(self.calls[-1],('/clip/v2/resource/grouped_light/group1',{'on':{'on':False}}))
    def test_rapid_switches_repeated_on_and_duplicate_off(self):
        for sid in ('scene1','sceneB','sceneC','sceneC'):self.command(sid,True)
        count=len(self.calls)
        for sid in ('scene1','sceneB'):self.assertFalse(self.command(sid,False)['accepted'])
        self.assertEqual(len(self.calls),count)
        self.command('sceneC',False);count=len(self.calls)
        self.assertTrue(self.command('sceneC',False)['ignored']);self.assertEqual(len(self.calls),count)
    def test_overlapping_groups_block_on_then_old_duplicate_off_is_safe(self):
        self.command('scene1',True)
        with self.assertRaisesRegex(scene_switch.Conflict,'overlapping'):self.command('scene2',True)
        self.command('scene1',False);self.command('scene2',True);count=len(self.calls)
        self.assertTrue(self.command('scene1',False)['ignored']);self.assertEqual(len(self.calls),count)
        self.command('scene2',False)
        self.assertEqual(self.calls[-1][0],'/clip/v2/resource/grouped_light/group2')
    def test_disjoint_groups_are_independent(self):
        def change(doc):
            bridge=doc['bridges'][0]
            bridge['scene_groups'][0]['light_ids']=[test_bridges.LEGACY,'light3']
        bridge_store.update_registry(change)
        for sid in ('scene1','sceneB','sceneC'):configure('eg1',sid,'room1')
        self.command('scene1',True);self.command('scene2',True);self.command('scene1',False)
        self.command('scene2',False)
        self.assertEqual([p for p,_ in self.calls[-2:]],['/clip/v2/resource/grouped_light/group1','/clip/v2/resource/grouped_light/group2'])
    def test_restart_unknown_off_fails_closed_without_delayed_reactivation(self):
        self.command('scene1',True);scene_switch._owners.clear();count=len(self.calls)
        with self.assertRaisesRegex(scene_switch.Conflict,'unknown'):self.command('scene1',False)
        self.assertEqual(count,len(self.calls));self.command('scene1',True);self.command('scene1',False)
    def test_timeout_partial_error_and_retry(self):
        for failure in (TimeoutError(),{'errors':[{'description':'private'}],'data':[]},{'errors':[],'data':[]}):
            self.command('scene1',True)
            context=patch('scene_switch.request_document',side_effect=failure) if isinstance(failure,Exception) else patch('scene_switch.request_document',return_value=failure)
            with context,self.assertRaises((TimeoutError,ValueError)):self.command('scene1',False)
            with self.assertRaisesRegex(scene_switch.Conflict,'unknown'):self.command('scene1',False)
            self.command('scene1',True);self.command('scene1',False)
    def test_stale_confirmation_cannot_approve_changed_membership(self):
        bridge,scene=scenes.resolve_path('/api/scenes/eg1/scene1/recall')
        confirmation=next(g for g in scene_switch.describe(bridge,scene)['groups'] if g['id']=='room1')['confirmation']
        def change(doc):doc['bridges'][0]['scene_groups'][0]['light_ids'].append('new')
        bridge_store.update_registry(change)
        with self.assertRaisesRegex(ValueError,'confirmation changed'):
            scene_switch.configure('eg1','scene1','room1',confirmation)

    def test_failed_on_does_not_confirm_ownership(self):
        with patch('scenes.request_document',side_effect=TimeoutError()),self.assertRaises(TimeoutError):self.command('scene1',True)
        with self.assertRaisesRegex(scene_switch.Conflict,'unknown'):self.command('scene1',False)
        with self.assertRaisesRegex(scene_switch.Conflict,'overlapping'):self.command('scene2',True)
    def test_config_change_membership_and_legacy_recall_invalidate(self):
        self.command('scene1',True)
        bridge,scene=scenes.resolve_path('/api/scenes/eg1/sceneB/recall');scenes.recall(bridge,scene)
        with self.assertRaisesRegex(scene_switch.Conflict,'unknown'):self.command('scene1',False)
        def change(doc):doc['bridges'][0]['scene_groups'][0]['light_ids'].append('new-light')
        bridge_store.update_registry(change)
        self.assertIsNone(scenes.resolve_path('/api/scenes/eg1/scene1/state'))
        self.assertIsNotNone(scenes.resolve_path('/api/scenes/eg1/scene1/recall'))
    def test_no_automatic_migration_and_digital_export(self):
        configure('eg1','scene1','')
        self.assertIsNone(scenes.resolve_path('/api/scenes/eg1/scene1/state'))
        root=ET.fromstring(loxone_export.export_xml(['eg1/scene1','eg1/sceneB'],False,kind='scenes',language='en'))
        legacy,switch=root.findall('VirtualOutCmd')
        self.assertEqual(legacy.get('CmdOff'),'');self.assertEqual(legacy.get('CmdOnPost'),'{"recall":true}')
        self.assertEqual(switch.get('CmdOnPost'),'{"on":true}');self.assertEqual(switch.get('CmdOffPost'),'{"on":false}')
        self.assertEqual(switch.get('CmdOn'),switch.get('CmdOff'));self.assertEqual(switch.get('Analog'),'false')
        self.assertIn('Scene on/off',switch.get('Title'))
    def test_confirmation_lists_full_group_and_overlaps_and_hidden_lights(self):
        bridge_admin.manage_light('eg1','light2','ignore')
        item=next(s for s in scenes.available_scenes() if s['key']=='eg1/scene1')
        group=next(g for g in item['switch']['groups'] if g['id']=='room1')
        self.assertEqual(len(group['lamps']),3);self.assertTrue(any(l['hidden'] for l in group['lamps']))
        self.assertIn('Ganzes Haus',group['overlaps'])
        with self.assertRaises(ValueError):configure('eg1','scene1','zone1')
    def test_concurrent_arrivals_cannot_overtake_inflight_bridge_call(self):
        entered=threading.Event();release=threading.Event();errors=[]
        def blocked(*args,**kwargs):
            entered.set();self.assertTrue(release.wait(3))
            return {'errors':[],'data':[{'rid':'scene1','rtype':'scene'}]}
        def run(sid,on):
            try:self.command(sid,on)
            except Exception as exc:errors.append(exc)
        with patch('scenes.request_document',side_effect=blocked):
            first=threading.Thread(target=run,args=('scene1',True));first.start();self.assertTrue(entered.wait(3))
            second=threading.Thread(target=run,args=('scene1',False));second.start();self.assertFalse(self.calls)
            release.set();first.join(3);second.join(3)
        self.assertFalse(first.is_alive());self.assertFalse(second.is_alive());self.assertEqual(errors,[])
        self.assertEqual(self.calls[-1][0],'/clip/v2/resource/grouped_light/group1')
    def test_queued_final_off_stays_after_earlier_on(self):
        errors=[]
        def run(sid,on):
            try:self.command(sid,on)
            except Exception as exc:errors.append(exc)
        with scene_switch.LOCK:
            with scene_switch.LOCK.condition:start=scene_switch.LOCK.issued
            first=threading.Thread(target=run,args=('sceneB',True));first.start()
            with scene_switch.LOCK.condition:
                self.assertTrue(scene_switch.LOCK.condition.wait_for(lambda:scene_switch.LOCK.issued==start+1,3))
            final=threading.Thread(target=run,args=('sceneB',False));final.start()
            with scene_switch.LOCK.condition:
                self.assertTrue(scene_switch.LOCK.condition.wait_for(lambda:scene_switch.LOCK.issued==start+2,3))
        first.join(3);final.join(3)
        self.assertFalse(first.is_alive());self.assertFalse(final.is_alive());self.assertEqual(errors,[])
        self.assertEqual(self.calls[-1][0],'/clip/v2/resource/grouped_light/group1')

    def test_unversioned_a_b_a_off_is_current_a_off_documented_limit(self):
        for sid in ('scene1','sceneB','scene1'):self.command(sid,True)
        self.command('scene1',False)
        self.assertEqual(self.calls[-1][0],'/clip/v2/resource/grouped_light/group1')


class SwitchAPITests(test_scenes.SceneAPITests):
    def setUp(self):
        super().setUp();scene_switch._owners.clear()
        def change(doc):doc['bridges'][0]['scene_groups']=scenes.collect_groups(inventory())
        bridge_store.update_registry(change)
    def test_switch_configuration_csrf_control_auth_and_payload(self):
        bridge=bridge_store.read_registry()['bridges'][0]
        scene=next(s for s in bridge['scenes'] if s['id']=='scene1')
        group=next(g for g in scene_switch.describe(bridge,scene)['groups'] if g['id']=='room1')
        body={'bridge_id':'eg1','scene_id':'scene1','group_id':'room1','confirmation':group['confirmation']}
        path='/api/admin/scenes/switch';control='/api/scenes/eg1/scene1/state'
        self.assertEqual(self.request(path,body)[0],401);self.login()
        self.assertEqual(self.request(path,body,{'X-CSRF-Token':''})[0],403)
        self.assertEqual(self.request(path,body,{'Origin':'https://evil.test'})[0],403)
        with patch('scenes.request_document') as write:
            self.assertEqual(self.request(path,body)[0],200);write.assert_not_called()
        auth={'Authorization':'Bearer '+'t'*48}
        with patch('scene_switch.control',return_value={'status':'ok','accepted':True}) as command:
            self.assertEqual(self.request(control,{'on':True},method='PUT')[0],401)
            for value in ({'on':1},{'on':0},{'on':True,'recall':True},{'recall':True}):
                self.assertEqual(self.request(control,value,auth,method='PUT')[0],400)
            command.assert_not_called()
            self.assertEqual(self.request(control,{'on':True},auth,method='PUT')[0],200)
        with patch('scene_switch.control',side_effect=scene_switch.Conflict('scene_switch_ownership_unknown')):
            self.assertEqual(self.request(control,{'on':False},auth,method='PUT')[0],409)


class SwitchUITests(unittest.TestCase):
    def test_actual_ui_requires_explicit_confirmation_and_posts_snapshot_in_both_languages(self):
        from pathlib import Path
        import subprocess
        root=Path(__file__).resolve().parent.parent
        for language in ('de','en'):
            script="""const assert=require('node:assert/strict');global.window={};
            global.navigator={languages:['LANG']};global.localStorage={getItem:()=>null};
            class Element{constructor(tag,text){this.tag=tag;this.textContent=text||'';this.children=[];this.value='';}append(...items){this.children.push(...items);}addEventListener(){}setAttribute(){}replaceChildren(...items){this.children=items;}}
            const message=new Element('p');global.document={documentElement:{},createTreeWalker:()=>({nextNode:()=>false}),querySelectorAll:()=>[],querySelector:()=>message};global.NodeFilter={SHOW_TEXT:4};
            global.node=(tag,text)=>new Element(tag,text);global.adminSession='fixture';
            """.replace('LANG',language)
            for f in ('locales/de.js','locales/en.js','i18n.js','scenes.js'):
                script+=(root/'web'/f).read_text()+'\n'
            script+='''
            loadScenes=async()=>{};renderScenes=()=>{};const calls=[];
            global.adminRequest=async(path,body)=>{calls.push([path,body]);return {ok:true};};
            const scene={key:'b/s',bridge_id:'b',switch:{enabled:true,configured:true,group_id:'room',groups:[{id:'room',name:'Living',confirmation:'snapshot-hash',lamps:[{name:'L1',hidden:true},{name:'L2',hidden:false}],overlaps:['Zone']}]}};
            const box=sceneSwitchOptions(scene);const [title,select,warning,label,save]=box.children;
            assert.equal(save.disabled,true);assert.ok(warning.textContent.includes('L1'));assert.ok(warning.textContent.includes('L2'));assert.ok(warning.textContent.includes('Zone'));
            const check=label.children[0];check.checked=true;check.onchange();assert.equal(save.disabled,false);
            (async()=>{await save.onclick();assert.equal(calls.length,1);assert.equal(calls[0][0],'/api/admin/scenes/switch');assert.equal(calls[0][1].confirmation,'snapshot-hash');assert.equal(calls[0][1].group_id,'room');assert.ok(message.textContent.includes(t('Nutzungsart gespeichert. XML neu exportieren; bestehende Loxone-Konfiguration bleibt unverändert.')));})().catch(e=>{console.error(e);process.exitCode=1;});
            '''
            subprocess.run(['node','-e',script],check=True)
