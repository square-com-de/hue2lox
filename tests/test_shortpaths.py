import copy
import json
import os
from pathlib import Path
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET
import bridge_store
import loxone_export
from tests import test_bridges

class ShortPathTests(unittest.TestCase):
    setUp=test_bridges.BridgeTests.setUp
    tearDown=test_bridges.BridgeTests.tearDown
    def test_persistent_aliases_collisions_rename_and_rescan(self):
        doc=bridge_store.read_registry();bridge=doc['bridges'][0]
        first=bridge['lights'][0];alias=first['short_name'];bridge_alias=bridge['short_name']
        def change(doc):
            b=doc['bridges'][0];b['name']='Anderer Name';b['lights'][0]['name']='Anderes Licht'
            b['lights'].append(dict(b['lights'][0],id='duplicate',short_name='',ignored=True))
            b['lights'].append(dict(b['lights'][0],id='duplicate2',short_name='',removed=True))
        bridge_store.update_registry(change)
        saved=bridge_store.read_registry()['bridges'][0]
        self.assertEqual(saved['short_name'],bridge_alias);self.assertEqual(saved['lights'][0]['short_name'],alias)
        aliases=[l['short_name'] for l in saved['lights']];self.assertEqual(len(aliases),len(set(aliases)))
        self.assertTrue(all(1<=len(a)<=8 for a in aliases+[bridge_alias]))
        self.assertIn('short_name',json.loads(self.registry.read_text())['bridges'][0])
    def test_normalization_routes_and_xml(self):
        self.assertEqual(bridge_store.short_slug('Büro Süd!'),'buero-su')
        lights=loxone_export.lights();light=lights[0];path=light['path']
        self.assertLessEqual(len(path),24);self.assertEqual(path.split('/')[-1],'state')
        target=loxone_export.resolve_path(path);self.assertEqual(target[1]['id'],light['key'].split('/')[1])
        self.assertEqual(loxone_export.resolve_path('/api/lights/'+light['key']+'/state')[1]['id'],target[1]['id'])
        root=ET.fromstring(loxone_export.export_xml([light['key']],False));self.assertEqual(root.find('VirtualOutCmd').get('CmdOn'),path)
        bridge_store.update_registry(lambda d:d['bridges'][0]['lights'][0].update(ignored=True))
        self.assertIsNone(loxone_export.resolve_path(path))
    def test_new_bridge_alias_collision_and_existing_alias_reservation(self):
        doc={'bridges':[{'id':'one','name':'Erdgeschoss','lights':[]},{'id':'two','name':'Erdgeschoss','lights':[]}]}
        bridge_store.ensure_short_names(doc);old=copy.deepcopy(doc)
        doc['bridges'].insert(0,{'id':'zero','name':'Erdgeschoss','lights':[]})
        bridge_store.ensure_short_names(doc)
        self.assertEqual([b['short_name'] for b in doc['bridges'][1:]],[b['short_name'] for b in old['bridges']])
        self.assertEqual(len({b['short_name'] for b in doc['bridges']}),3)
        reserved={'bridges':[{'id':'api-bridge','name':'API','lights':[]}]}
        bridge_store.ensure_short_names(reserved);self.assertNotEqual(reserved['bridges'][0]['short_name'],'api')

class ShortPathAPITests(unittest.TestCase):
    from tests import test_admin
    setUp=test_admin.AdminTests.setUp
    tearDown=test_admin.AdminTests.tearDown
    request=test_admin.AdminTests.request
    def test_short_path_control_auth_and_method(self):
        import request_monitor
        path=loxone_export.lights()[0]['path'];auth={'Authorization':'Bearer '+'t'*48}
        request_monitor.start()
        try:
            with patch('app.write_state',return_value={'status':'accepted'}) as write:
                self.assertEqual(self.request(path,{'brightness':20},auth,method='PUT')[0],200)
                self.assertEqual(request_monitor.snapshot()['events'][-1]['path'],path)
                self.assertEqual(self.request(path,{'brightness':20},method='PUT')[0],401)
                self.assertEqual(self.request(path,method='GET')[0],405)
                write.assert_called_once();self.assertEqual(write.call_args.kwargs['light_id'],loxone_export.lights()[0]['key'].split('/')[1])
        finally:request_monitor.stop();request_monitor.clear()
