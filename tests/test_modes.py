import os
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET
import loxone_export
from tests import test_bridges
from tests import test_admin

class ModeTests(unittest.TestCase):
    setUp=test_bridges.BridgeTests.setUp
    tearDown=test_bridges.BridgeTests.tearDown
    def test_recommendation_by_capabilities_and_flags(self):
        doc=loxone_export.registry();original=doc['bridges'][0]['lights'][0]
        for caps,expected in [(['on'],'switch'),(['on','brightness'],'dim'),(['on','brightness','rgb'],'rgb'),(['on','brightness','rgb','temperature'],'lumitech'),(['on','brightness','temperature'],'tw')]:
            with self.subTest(caps=caps):
                original['capabilities']=caps
                with patch('loxone_export.registry',return_value=doc):self.assertEqual(loxone_export.lights()[0]['recommended_mode'],expected)
        original['capabilities']=['on','brightness','rgb','temperature']
        with patch('loxone_export.registry',return_value=doc),patch.dict(os.environ,{'HUE_WHITE_ENABLED':'0'}):self.assertEqual(loxone_export.lights()[0]['recommended_mode'],'rgb')
        with patch('loxone_export.registry',return_value=doc),patch.dict(os.environ,{'HUE_COLOR_ENABLED':'0'}):self.assertEqual(loxone_export.lights()[0]['recommended_mode'],'tw')
    def test_one_variant_per_lamp_default_and_explicit(self):
        items=loxone_export.lights();key=items[0]['key']
        for mode in ['switch','dim','rgb','lumitech']:
            root=ET.fromstring(loxone_export.export_xml([key],False,variants={key:mode}));commands=root.findall('VirtualOutCmd');self.assertEqual(len(commands),1)
            cmd=commands[0];self.assertEqual(cmd.get('Analog'),'false' if mode=='switch' else 'true')
            self.assertEqual(bool(cmd.get('CmdOffPost')),mode=='switch')
        root=ET.fromstring(loxone_export.export_xml([key],False));self.assertEqual(len(root.findall('VirtualOutCmd')),1);self.assertIn('lumitech',root.find('VirtualOutCmd').get('CmdOnPost'))
    def test_multi_export_accepts_different_modes_and_validates_all(self):
        doc=loxone_export.registry();bridge=doc['bridges'][0];bridge['lights'].append(dict(bridge['lights'][0],id='plug',name='Plug',capabilities=['on']))
        key=bridge['id']+'/'+bridge['lights'][0]['id'];plug=bridge['id']+'/plug'
        with patch('loxone_export.registry',return_value=doc):
            root=ET.fromstring(loxone_export.export_xml([key,plug],False,variants={key:'rgb',plug:'switch'}));self.assertEqual(len(root.findall('VirtualOutCmd')),2)
            for variants in [{plug:'rgb'},{key:'unknown'},{'not-selected':'switch'},[],{key:None}]:
                with self.assertRaises(ValueError):loxone_export.export_xml([key,plug],False,variants=variants)

class ModeAPITests(unittest.TestCase):
    setUp=test_admin.AdminTests.setUp
    tearDown=test_admin.AdminTests.tearDown
    request=test_admin.AdminTests.request
    login=test_admin.AdminTests.login
    def test_export_selected_mode_and_reject_unsupported(self):
        self.login();key=loxone_export.lights()[0]['key']
        code,_,body=self.request('/api/admin/export',{'lights':[key],'variants':{key:'dim'}});self.assertEqual(code,200)
        root=ET.fromstring(body);self.assertEqual(len(root.findall('VirtualOutCmd')),1);self.assertEqual(root.find('VirtualOutCmd').get('CmdOnPost'),'{"brightness":<v>}')
        self.assertEqual(self.request('/api/admin/export',{'lights':[key],'variants':{key:'bad'}})[0],400)
