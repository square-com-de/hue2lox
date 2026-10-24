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
    def test_visible_default_without_checkbox_and_immediate_choice_in_both_languages(self):
        from pathlib import Path
        import subprocess
        root=Path(__file__).resolve().parent.parent
        for language in ('de','en'):
            script="""const assert=require('node:assert/strict');global.window={};
            global.navigator={languages:['LANG']};global.localStorage={getItem:()=>null};
            class Element{constructor(tag,text,cls){this.tag=tag;this.textContent=text||'';this.className=cls;this.children=[];this.value='';}append(...items){this.children.push(...items);}addEventListener(){}setAttribute(){}replaceChildren(...items){this.children=items;}}
            const message=new Element('p');global.document={documentElement:{},createTreeWalker:()=>({nextNode:()=>false}),querySelectorAll:()=>[],querySelector:()=>message};global.NodeFilter={SHOW_TEXT:4};
            global.node=(tag,text,cls)=>new Element(tag,text,cls);global.adminSession='fixture';
            """.replace('LANG',language)
            for f in ('locales/de.js','locales/en.js','i18n.js','scenes.js'):
                script+=(root/'web'/f).read_text()+'\n'
            script+='''
            loadScenes=async()=>{};renderScenes=()=>{};const calls=[];
            global.adminRequest=async(path,body)=>{calls.push([path,body]);return {ok:true};};
            const group={id:'room',name:'Living',confirmation:'snapshot-hash',extra_light_ids:['l2'],lamps:[{id:'l1',name:'L1',hidden:true},{id:'l2',name:'L2',hidden:false}],overlaps:['Zone']};
            const scene={available:true,key:'b/s',bridge_id:'b',switch:{mode:'switch',enabled:true,automatic:true,configured:true,exact_group_id:'room',group_id:'room',groups:[group]}};
            const box=sceneSwitchOptions(scene),controls=box.children[0],mode=controls.children[0].children[0],target=controls.children[1].children[0];
            const all=[];function visit(e){all.push(e);e.children.forEach(visit);}visit(box);
            assert.equal(mode.value,'switch');assert.equal(target.value,'room');assert.equal(all.some(e=>e.tag==='input'||e.tag==='button'||e.tag==='details'),false);
            const pending=sceneSwitchOptions({...scene,switch:{...scene.switch,enabled:false,group_id:''}});assert.ok(pending.children.some(e=>e.textContent.includes('L2')));
            assert.ok(all.some(e=>e.textContent.includes('L1')));assert.ok(all.some(e=>e.textContent.includes('L2')));assert.ok(all.some(e=>e.textContent.includes('Zone')));
            (async()=>{target.value='room';await target.onchange();assert.equal(calls.length,1);assert.equal(calls[0][1].mode,'group');assert.equal(calls[0][1].confirmation,'snapshot-hash');assert.equal(calls[0][1].group_id,'room');mode.value='recall';await mode.onchange();assert.equal(calls[1][1].mode,'recall');assert.equal(calls[1][1].group_id,'');})().catch(e=>{console.error(e);process.exitCode=1;});
            '''
            subprocess.run(['node','-e',script],check=True)


class AutomaticDefaultsTests(unittest.TestCase):
    setUp=test_bridges.BridgeTests.setUp
    tearDown=test_bridges.BridgeTests.tearDown
    def scan(self,resources=None):
        with patch('bridge_admin.request_resources',return_value=resources or inventory()):bridge_admin.scan_bridge('eg1')
    def item(self,sid='scene2'):
        return next(s for s in scenes.available_scenes() if s['key']=='eg1/'+sid)
    def test_unique_exact_group_defaults_to_on_off_and_xml_without_choice(self):
        with patch('scene_switch.request_document') as write,patch('scenes.request_document') as recall:
            self.scan();item=self.item();self.assertTrue(item['switch']['enabled']);self.assertTrue(item['switch']['automatic'])
            self.assertEqual(item['path'],'/api/scenes/eg1/scene2/state');write.assert_not_called();recall.assert_not_called()
        command=ET.fromstring(loxone_export.export_xml(['eg1/scene2'],False,kind='scenes')).find('VirtualOutCmd')
        self.assertEqual(command.get('CmdOnPost'),'{"on":true}');self.assertEqual(command.get('CmdOffPost'),'{"on":false}')
    def test_superset_requires_choice_not_silent_recall_or_bigger_group(self):
        self.scan();item=self.item('scene1');self.assertEqual(item['switch']['mode'],'switch');self.assertTrue(item['switch']['needs_group'])
        self.assertEqual(item['switch']['group_id'],'');self.assertEqual(len(item['switch']['groups'][0]['extra_light_ids']),2)
        with self.assertRaises(ValueError):loxone_export.export_xml(['eg1/scene1'],False,kind='scenes')
        self.assertIsNotNone(scenes.resolve_path('/api/scenes/eg1/scene1/recall'))
    def test_ambiguous_exact_groups_do_not_pick_one(self):
        resources=inventory();resources.extend([{'id':'group3','type':'grouped_light','owner':{'rid':'zone3','rtype':'zone'}},{'id':'zone3','type':'zone','metadata':{'name':'Same lamps'},'children':[{'rid':'light2','rtype':'light'}],'services':[{'rid':'group3','rtype':'grouped_light'}]}])
        self.scan(resources);self.assertFalse(self.item()['switch']['enabled']);self.assertEqual(self.item()['switch']['exact_group_id'],'')
    def test_explicit_recall_survives_restart_rescan_and_auto_can_be_reenabled(self):
        self.scan();scene_switch.configure('eg1','scene2','',mode='recall');before=self.registry.read_bytes()
        scene_switch.initialize_defaults();self.assertEqual(before,self.registry.read_bytes());self.scan()
        item=self.item();self.assertEqual(item['switch']['mode'],'recall');self.assertEqual(item['commands'][0]['body_off'],'')
        group=next(g for g in item['switch']['groups'] if g['id']=='zone1')
        scene_switch.configure('eg1','scene2','zone1',group['confirmation'],mode='auto')
        self.assertTrue(self.item()['switch']['enabled'])
    def test_initial_upgrade_persists_once_then_changed_group_is_not_rebound(self):
        self.scan()
        def old(doc):
            for s in doc['bridges'][0]['scenes']:
                for k in ('switch_mode','switch_group','switch_confirmation'):s.pop(k,None)
        bridge_store.update_registry(old);scene_switch.initialize_defaults();first=self.registry.read_bytes()
        scene_switch.initialize_defaults();self.assertEqual(first,self.registry.read_bytes())
        changed=inventory();next(r for r in changed if r['id']=='zone1')['children'].append({'rid':'light3','rtype':'light'})
        self.scan(changed);item=self.item();self.assertFalse(item['switch']['enabled']);self.assertTrue(item['switch']['needs_group'])
        scene_switch.initialize_defaults();self.assertFalse(self.item()['switch']['enabled'])
    def test_existing_manual_group_is_preserved_even_when_default_is_exact(self):
        self.scan();configure('eg1','scene2','room1');scene_switch.initialize_defaults();self.scan()
        item=self.item();self.assertEqual(item['switch']['group_id'],'room1');self.assertFalse(item['switch']['automatic'])
    def test_stale_auto_choice_cannot_enable_new_inventory(self):
        self.scan();item=self.item();group=next(g for g in item['switch']['groups'] if g['id']=='zone1')
        def change(doc):doc['bridges'][0]['scene_groups'][1]['name']='Renamed'
        bridge_store.update_registry(change)
        with self.assertRaisesRegex(ValueError,'confirmation changed'):
            scene_switch.configure('eg1','scene2','zone1',group['confirmation'],mode='auto')
