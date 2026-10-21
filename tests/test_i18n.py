"""Translation boundary and export regression tests."""
import json
from pathlib import Path
import subprocess
import unittest
import xml.etree.ElementTree as ET
from unittest.mock import patch
import loxone_export
from tests import test_admin
from tests import test_bridges

ROOT=Path(__file__).resolve().parent.parent
class LocaleTests(unittest.TestCase):
    def test_dictionary_parity_fallback_and_language_detection(self):
        de=json.loads((ROOT/'web/locales/de.json').read_text());en=json.loads((ROOT/'web/locales/en.json').read_text())
        self.assertEqual(de.keys(),en.keys());self.assertTrue(all(en.values()))
        # No browser dependencies: exercise the actual choice/fallback implementation.
        script='''const assert=require('node:assert/strict');global.window={};global.navigator={languages:['fr-FR','en-US']};global.localStorage={getItem:()=>null};global.document={documentElement:{},createTreeWalker:()=>({nextNode:()=>false}),querySelectorAll:()=>[]};global.NodeFilter={SHOW_TEXT:4};'''
        for f in ['locales/de.js','locales/en.js','i18n.js']:script+=(ROOT/'web'/f).read_text()+'\n'
        script+='''assert.equal(i18n.language,'en');assert.equal(i18n.choose('de',['en-US']),'de');assert.equal(i18n.choose('invalid',['de-AT']),'de');assert.equal(i18n.choose(null,['fr']),'en');assert.equal(t('Passwort'),'Password');assert.equal(t('My own room'),'My own room');delete window.HUE2LOX_MESSAGES.en.Passwort;assert.equal(t('Passwort'),'Passwort');'''
        subprocess.run(['node','-e',script],check=True)
    def test_static_and_dynamic_catalogs_build_reproducibly(self):
        for lang in ('de','en'):
            data=json.loads((ROOT/f'web/locales/{lang}.json').read_text())
            expected='window.HUE2LOX_MESSAGES=window.HUE2LOX_MESSAGES||{};\nwindow.HUE2LOX_MESSAGES.'+lang+'='+json.dumps(data,ensure_ascii=False)+';\n'
            self.assertEqual((ROOT/f'web/locales/{lang}.js').read_text(),expected)

class LocalizedExportTests(unittest.TestCase):
    setUp=test_bridges.BridgeTests.setUp
    tearDown=test_bridges.BridgeTests.tearDown
    def test_language_only_changes_generated_labels_not_names_or_protocol(self):
        doc=loxone_export.registry();doc['bridges'][0]['lights'][0]['name']='Passwort & Küche'
        with patch('loxone_export.registry',return_value=doc):
            key=loxone_export.lights()[0]['key']
            roots=[ET.fromstring(loxone_export.export_xml([key],False,variants={key:'switch'},language=lang)) for lang in ('de','en')]
            a,b=[r.find('VirtualOutCmd') for r in roots]
            self.assertEqual(a.get('Title'),'Passwort & Küche · Ein/Aus');self.assertEqual(b.get('Title'),'Passwort & Küche · On/off')
            for k in a.attrib:
                if k!='Title':self.assertEqual(a.get(k),b.get(k))
            with self.assertRaises(ValueError):loxone_export.export_xml([key],False,language='xx')

class LocaleAssetsTests(unittest.TestCase):
    setUp=test_admin.AdminTests.setUp
    tearDown=test_admin.AdminTests.tearDown
    request=test_admin.AdminTests.request
    def test_public_local_assets_and_guides(self):
        for path in ['/assets/i18n.js','/assets/locales/en.js','/assets/locales/de.js','/tutorial/en','/licenses','/assets/catalog-license.txt']:
            code,headers,body=self.request(path);self.assertEqual(code,200,path);self.assertEqual(int(headers['Content-Length']),len(body));self.assertNotIn(b't'*48,body)
        self.assertIn(b'lang="en"',self.request('/tutorial/en')[2])
        self.assertEqual(self.request('/assets/locales/../../secrets/control_token')[0],404)

class MonitorLocaleTests(unittest.TestCase):
    def test_actual_monitor_formats_only_redaction_markers(self):
        for language in ('de','en'):
            script="const assert=require('node:assert/strict');global.window={};global.navigator={languages:['"+language+"']};global.localStorage={getItem:()=>null};global.document={documentElement:{},createTreeWalker:()=>({nextNode:()=>false}),querySelectorAll:()=>[],querySelector:()=>({addEventListener:()=>{}})};global.NodeFilter={SHOW_TEXT:4};global.setInterval=()=>{};"
            for file in ('locales/de.js','locales/en.js','i18n.js','monitor.js'):
                script+=(ROOT/'web'/file).read_text()+'\n'
            script+="assert.equal(monitorBody('brightness=42 xy=0.2 Passwort & Küche'), 'brightness=42 xy=0.2 Passwort & Küche');assert.equal(monitorBody('[redacted_text]'),t('[Text ausgeblendet]'));assert.equal(monitorDetail('invalid_json:2:7'),t('JSON ungültig: Zeile ')+'2'+t(', Spalte ')+'7');assert.equal(monitorDetail('parsed'),'parsed');"
            subprocess.run(['node','-e',script],check=True)
