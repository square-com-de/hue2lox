"""Loxone editor values must preserve escape sequences, not physical newlines."""
import json
import re
import shutil
import subprocess
import unittest
from pathlib import Path
import xml.etree.ElementTree as ET
import loxone_export
from tests import test_bridges

class HeaderFormatTests(unittest.TestCase):
    setUp=test_bridges.BridgeTests.setUp
    tearDown=test_bridges.BridgeTests.tearDown
    def test_gui_copy_and_xml_share_one_line_escaped_format(self):
        token='fixture-token-no-real-secret-123456789'
        expected='Authorization: Bearer '+token+r'\r\nContent-Type: application/json'
        light=loxone_export.lights()[0]
        for mode in ('switch','dim','rgb','lumitech'):
            root=ET.fromstring(loxone_export.export_xml([light['key']],True,token,variants={light['key']:mode}))
            cmd=root.find('VirtualOutCmd');self.assertEqual(cmd.get('CmdOnHTTP'),expected)
            self.assertEqual(cmd.get('CmdOffHTTP'),expected if mode=='switch' else '')
        self.assertNotIn('\r',expected);self.assertNotIn('\n',expected)
        source=(Path(__file__).resolve().parent.parent/'web/admin.js').read_text()
        helper=re.search(r'function loxoneHTTPHeader\(token\)\{[^\n]+',source).group(0)
        self.assertIsNotNone(shutil.which('node'),'Node required to test actual clipboard helper')
        result=subprocess.check_output(['node','-e',helper+';process.stdout.write(JSON.stringify(loxoneHTTPHeader('+json.dumps(token)+')));'],text=True)
        self.assertEqual(json.loads(result),expected)
        self.assertEqual(source.count('clipboard.writeText(loxoneHTTPHeader('),2)
        self.assertEqual(source.count("loxoneHTTPHeader('DEIN_HUE2LOX_TOKEN')"),2)
