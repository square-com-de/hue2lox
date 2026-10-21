import json
import unittest
from unittest.mock import patch
import bridge_admin
import bridge_store
import dashboard
import hue_client
import loxone_export
from tests import test_bridges
from tests.test_bridges import LEGACY, resources
from tests import test_admin

class LampTests(unittest.TestCase):
    setUp=test_bridges.BridgeTests.setUp
    tearDown=test_bridges.BridgeTests.tearDown
    def test_ignore_restore_and_rescan_without_hue_writes(self):
        with patch('bridge_admin.request_document') as write:
            bridge_admin.manage_light('eg1',LEGACY,'ignore')
            bridge_admin.apply_inventory(bridge_admin.bridge_record('eg1'),bridge_admin.collect_lights(resources()))
            light=bridge_store.read_registry()['bridges'][0]['lights'][0]
            self.assertTrue(next(l for l in bridge_admin.bridge_record('eg1')['lights'] if l['id']==LEGACY)['ignored'])
            self.assertNotIn('eg1/'+LEGACY,[l['key'] for l in loxone_export.lights()])
            self.assertIsNone(loxone_export.resolve_path('/api/lights/eg1/'+LEGACY+'/state'))
            with self.assertRaises(ValueError):hue_client.default_bridge()
            with self.assertRaises(ValueError):loxone_export.export_xml(['eg1/'+LEGACY],False)
            bridge_admin.manage_light('eg1',LEGACY,'ignore',False)
            self.assertIsNotNone(loxone_export.resolve_path('/api/lights/eg1/'+LEGACY+'/state'))
            self.assertEqual(hue_client.default_bridge()['id'],'eg1')
            write.assert_not_called()
    def test_remove_rediscovery_preserves_alias(self):
        original_path=next(l for l in loxone_export.lights() if l['key']=='eg1/'+LEGACY)['path']
        bridge_admin.manage_light('eg1',LEGACY,'remove')
        with patch('dashboard.read_bridge_statuses') as request:
            result=dashboard.overview()
            self.assertEqual(result['bridges'][0]['lights'],[]);request.assert_not_called()
        self.assertEqual(loxone_export.lights(),[])
        with self.assertRaises(ValueError):hue_client.default_bridge()
        bridge_admin.apply_inventory(bridge_admin.bridge_record('eg1'),bridge_admin.collect_lights(resources()))
        self.assertEqual(loxone_export.resolve_path(next(l for l in loxone_export.lights() if l['key']=='eg1/'+LEGACY)['path'])[1]['id'],LEGACY)
        self.assertEqual(next(l for l in loxone_export.lights() if l['key']=='eg1/'+LEGACY)['path'],original_path)
        self.assertEqual(next(l for l in bridge_store.read_registry()['bridges'][0]['lights'] if l['id']==LEGACY)['control_path'],'/hue-go/state')
    def test_ignored_not_polled_or_degraded(self):
        bridge_admin.manage_light('eg1',LEGACY,'ignore')
        with patch('dashboard.read_bridge_statuses') as request:
            result=dashboard.overview()['bridges'][0]
            self.assertEqual(result['status'],'ready');self.assertEqual(result['lights'][0]['status'],'ignored');request.assert_not_called()
    def test_validation_and_busy_leave_registry_unchanged(self):
        before=self.registry.read_bytes()
        for ref,light,action,ignored in [('unknown',LEGACY,'ignore',True),('eg1','unknown','remove',True),('eg1',LEGACY,'ignore','true'),('eg1',None,'ignore',True)]:
            with self.assertRaises(bridge_admin.BridgeError):bridge_admin.manage_light(ref,light,action,ignored)
            self.assertEqual(before,self.registry.read_bytes())
        lock=bridge_admin.operation_lock('eg1');lock.acquire()
        try:
            with self.assertRaises(bridge_admin.BridgeError) as error:bridge_admin.manage_light('eg1',LEGACY,'remove')
            self.assertEqual(error.exception.status,409)
        finally:lock.release()

class LampAPITests(unittest.TestCase):
    setUp=test_admin.AdminTests.setUp
    tearDown=test_admin.AdminTests.tearDown
    request=test_admin.AdminTests.request
    login=test_admin.AdminTests.login
    def test_session_csrf_origin_and_dispatch(self):
        body={'bridge_id':'eg1','light_id':LEGACY,'ignored':True}
        for action in ('ignore','remove'):
            path='/api/admin/lights/'+action
            self.assertEqual(self.request(path,body)[0],401)
            self.login()
            with patch('bridge_admin.manage_light',return_value={'id':LEGACY}) as change:
                self.assertEqual(self.request(path,body,{'X-CSRF-Token':''})[0],403)
                self.assertEqual(self.request(path,body,{'Origin':'https://evil.test'})[0],403)
                change.assert_not_called()
                self.assertEqual(self.request(path,body)[0],200)
                change.assert_called_once_with('eg1',LEGACY,action,True)
            self.cookie=None;self.csrf=None
