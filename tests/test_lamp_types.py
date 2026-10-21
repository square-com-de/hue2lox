import json
import os
from pathlib import Path
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET
import lamp_types
import loxone_export
import bridge_store
from tests import test_bridges
from tests import test_admin

class LampTypeTests(unittest.TestCase):
    setUp=test_bridges.BridgeTests.setUp
    tearDown=test_bridges.BridgeTests.tearDown
    def test_catalog_and_detected_type_precedence(self):
        rows=lamp_types.catalog();self.assertGreater(len(rows),800)
        self.assertTrue(all(row['model_id'] and row['name'] for row in rows))
        self.assertEqual(lamp_types.details({'model':'LLC020','capabilities':['on']})['lamp_type'],'Ein/Aus')
        for caps,kind in [(['on'],'Ein/Aus'),(['on','brightness'],'Dimmer'),(['on','brightness','temperature'],'Tunable White'),(['on','brightness','rgb'],'RGB'),(['on','brightness','rgb','temperature'],'RGB + Tunable White')]:
            self.assertEqual(lamp_types.details({'capabilities':caps})['lamp_type'],kind)
    def test_tunable_white_default_and_checkbox_export_persistence(self):
        bridge_store.update_registry(lambda d:d['bridges'][0]['lights'][0].update(capabilities=['on','brightness','temperature']))
        light=loxone_export.lights()[0];self.assertEqual(light['recommended_mode'],'tw');self.assertEqual(light['enabled_modes'],['tw'])
        with patch.dict(os.environ,{'HUE_COLOR_ENABLED':'0'}):self.assertIn('tw',[c['id'] for c in loxone_export.lights()[0]['commands']])
        bridge_id,light_id=light['key'].split('/')
        lamp_types.save_modes(bridge_id,light_id,['switch','tw'])
        self.assertEqual(loxone_export.lights()[0]['enabled_modes'],['switch','tw'])
        self.assertEqual(json.loads(self.registry.read_text())['bridges'][0]['lights'][0]['enabled_modes'],['switch','tw'])
        root=ET.fromstring(loxone_export.export_xml([light['key']],False));self.assertEqual(len(root.findall('VirtualOutCmd')),2)
        self.assertIn('loxone_lumitech',root.findall('VirtualOutCmd')[1].get('CmdOnPost'))
        for modes in [[],['rgb'],['tw','tw'],['unknown'],'tw']:
            with self.assertRaises(ValueError):lamp_types.save_modes(bridge_id,light_id,modes)
        # Inventory merges existing choices instead of erasing them.
        import bridge_admin
        discovered=bridge_admin.collect_lights(test_bridges.resources())
        bridge_admin.apply_inventory(bridge_admin.bridge_record(bridge_id),discovered)
        self.assertEqual(next(l for l in loxone_export.lights() if l['key']==light['key'])['enabled_modes'],['switch','tw'])
    def test_list_variants_selected_only_and_single_string_compatibility(self):
        light=loxone_export.lights()[0];key=light['key']
        root=ET.fromstring(loxone_export.export_xml([key],False,variants={key:['switch','dim']}));self.assertEqual(len(root.findall('VirtualOutCmd')),2)
        for modes in [[],['dim','dim'],['bad'],[None]]:
            with self.assertRaises(ValueError):loxone_export.export_xml([key],False,variants={key:modes})
        self.assertEqual(len(ET.fromstring(loxone_export.export_xml([key],False,variants={key:'dim'})).findall('VirtualOutCmd')),1)

class LampUsageAPITests(unittest.TestCase):
    # Use plain admin session fixture plus a private, writable topology.
    def setUp(self):
        test_admin.AdminTests.setUp(self)
        self.registry=self.directory/'registry.json'
        self.registry.write_text((Path(__file__).resolve().parent.parent/'tests/fixtures/registry.json').read_text())
        self.registry_env=patch.dict(os.environ,{'HUE_REGISTRY_FILE':str(self.registry),'HUE_STATE_DIR':str(self.directory)})
        self.registry_env.start()
    def tearDown(self):self.registry_env.stop();test_admin.AdminTests.tearDown(self)
    request=test_admin.AdminTests.request
    login=test_admin.AdminTests.login
    def test_usage_protected_and_no_lamp_writes(self):
        light=loxone_export.lights()[0];bridge_id,light_id=light['key'].split('/')
        body={'bridge_id':bridge_id,'light_id':light_id,'modes':['switch','dim']}
        self.assertEqual(self.request('/api/admin/lights/usage',body)[0],401)
        self.login()
        self.assertEqual(self.request('/api/admin/lights/usage',body,{'X-CSRF-Token':''})[0],403)
        with patch('app.write_state') as write:
            self.assertEqual(self.request('/api/admin/lights/usage',body)[0],200)
            self.assertEqual(loxone_export.lights()[0]['enabled_modes'],['switch','dim'])
            write.assert_not_called()
    def test_icon_preference_protected_persistent_and_rescan_safe(self):
        import bridge_admin
        light=loxone_export.lights()[0];bridge_id,light_id=light['key'].split('/')
        path='/api/admin/lights/icon'
        body={'bridge_id':bridge_id,'light_id':light_id,'icon':'wall'}
        before=loxone_export.export_xml([light['key']],False)
        self.assertEqual(self.request(path,body)[0],401)
        self.login()
        self.assertEqual(self.request(path,body,{'X-CSRF-Token':''})[0],403)
        with patch('app.write_state') as write:
            self.assertEqual(self.request(path,body)[0],200)
            for invalid in ('<svg>',None,{},'constructor'):
                self.assertEqual(self.request(path,{**body,'icon':invalid})[0],400)
            write.assert_not_called()
        def stored():
            doc=json.loads(self.registry.read_text())
            return next(l for b in doc['bridges'] if b['id']==bridge_id for l in b['lights'] if l['id']==light_id)
        self.assertEqual(stored()['icon_override'],'wall')
        for icon in ('resonate','filament','bollard','garden-spot','lantern-wall','lantern-post','flood','linear','iris','bloom','play-bar'):
            self.assertEqual(self.request(path,{**body,'icon':icon})[0],200)
            self.assertEqual(stored()['icon_override'],icon)
        self.assertEqual(self.request(path,body)[0],200)
        self.assertEqual(before,loxone_export.export_xml([light['key']],False))
        discovered=bridge_admin.collect_lights(test_bridges.resources())
        for item in discovered:item['icon_override']='table'
        bridge_admin.apply_inventory(bridge_admin.bridge_record(bridge_id),discovered)
        self.assertEqual(stored()['icon_override'],'wall')
        self.assertEqual(self.request(path,{**body,'icon':'auto'})[0],200)
        self.assertNotIn('icon_override',stored())
        # Visual metadata is never included in Loxone commands.
        self.assertNotIn(b'icon_override',loxone_export.export_xml([light['key']],False))
    def test_white_off_without_rgb_feature(self):
        self.login()
        with patch.dict(os.environ,{'HUE_COLOR_ENABLED':'0'}),patch('app.write_state',return_value={'status':'accepted'}) as write:
            self.assertEqual(self.request('/hue-go/state',{'loxone_lumitech':0},{'Authorization':'Bearer '+'t'*48},method='PUT')[0],200)
            write.assert_called_once()
    def test_catalog_zip_includes_exact_data_license_and_provenance(self):
        import io
        import zipfile
        code,headers,body=self.request('/assets/hue-models.zip')
        self.assertEqual(code,200)
        self.assertEqual(headers['Content-Type'],'application/zip')
        self.assertEqual(headers['Content-Disposition'],'attachment; filename="Hue-Modelltabelle.zip"')
        self.assertEqual(int(headers['Content-Length']),len(body))
        with zipfile.ZipFile(io.BytesIO(body)) as archive:
            expected={'Hue-Modelltabelle.csv':'hue-models.csv','LICENSE.txt':'LICENSE-zigbee-herdsman-converters','SOURCE.md':'README.md'}
            self.assertEqual(set(archive.namelist()),set(expected))
            for name,source in expected.items():
                self.assertEqual(archive.read(name),(Path(__file__).resolve().parent.parent/'catalog'/source).read_bytes())
            self.assertIn(b'499535e092401a6c21e8c3b5e3aeca8062c11841',archive.read('SOURCE.md'))
        code,headers,_=self.request('/assets/hue-models.csv')
        self.assertEqual(code,302)
        self.assertEqual(headers['Location'],'/assets/hue-models.zip')
