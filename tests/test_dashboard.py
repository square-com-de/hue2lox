import json
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch
import dashboard
from tests import test_control


class RegistryTests(unittest.TestCase):
    def setUp(self):
        self.env=patch.dict('os.environ', {'HUE_REGISTRY_FILE':str(Path(__file__).resolve().parent.parent/'tests/fixtures/registry.json')});self.env.start()
        dashboard.CACHE=None;dashboard.CACHE_AT=0
    def tearDown(self):
        self.env.stop()
        dashboard.CACHE=None;dashboard.CACHE_AT=0
    def test_topology_secret_redaction_and_disabled_bridges(self):
        state={'on':True,'brightness':47.04,'color_temperature':{'mirek':370,'mirek_valid':True}}
        with patch('dashboard.read_bridge_statuses',return_value={'00000000-0000-4000-8000-000000000001':state}) as read:
            result=dashboard.overview()
            self.assertEqual(len(result['bridges']),3);read.assert_called_once()
            self.assertEqual(result['bridges'][0]['lights'][0]['state'],state)
            text=json.dumps(result)
            self.assertNotIn('key_file',text);self.assertNotIn('/run/secrets',text)
            self.assertEqual(result['bridges'][1]['status'],'prepared')
            dashboard.overview();read.assert_called_once()
    def test_bridge_failure_is_generic(self):
        with patch('dashboard.read_bridge_statuses',side_effect=RuntimeError('PRIVATE TOKEN')):
            result=dashboard.overview()
            self.assertNotIn('PRIVATE TOKEN',json.dumps(result))
            self.assertEqual(result['bridges'][0]['status'],'degraded')
            self.assertIsNone(result['bridges'][0]['lights'][0]['state'])
    def test_multiple_active_bridges_and_lights(self):
        original=json.loads((Path(__file__).resolve().parent.parent/'tests/fixtures/registry.json').read_text())
        bridge=dict(original['bridges'][0]);bridge['id']='second';bridge['host']='192.0.2.2';bridge['lights']=[dict(bridge['lights'][0],id='second-light')]
        original['bridges'].append(bridge)
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'registry.json';p.write_text(json.dumps(original))
            with patch.dict('os.environ',{'HUE_REGISTRY_FILE':str(p)}),patch('dashboard.read_bridge_statuses',side_effect=lambda b: {l['id']:{'on':False,'brightness':20} for l in b['lights']}) as read:
                result=dashboard.overview();self.assertEqual(read.call_count,2)
                self.assertEqual(result['bridges'][-1]['lights'][0]['id'],'second-light')


class WebTests(unittest.TestCase):
    setUp=test_control.ControlEndpointTests.setUp
    tearDown=test_control.ControlEndpointTests.tearDown
    def get(self,path):
        import http.client
        conn=http.client.HTTPConnection('127.0.0.1',self.server.server_port)
        conn.request('GET',path);r=conn.getresponse();value=(r.status,dict(r.getheaders()),r.read());conn.close();return value
    def test_assets_and_csp(self):
        for path in ['/','/assets/app.js','/assets/app.css','/tutorial','/assets/tutorial.css','/assets/tutorial-config.png','/assets/tutorial-commands.png','/assets/tutorial-monitor.png']:
            code,headers,body=self.get(path);self.assertEqual(code,200);self.assertGreater(len(body),100)
            self.assertIn("frame-ancestors 'none'",headers['Content-Security-Policy'])
    def test_allowlist_blocks_sensitive_and_traversal_paths(self):
        for path in ['/secrets/hue_key','/.env','/assets/../registry.json','/registry.json','/web/index.html']:
            self.assertEqual(self.get(path)[0],404)
    def test_overview_and_health_do_not_write(self):
        with patch('app.overview',return_value={'status':'ok','bridges':[]}),patch('app.write_state') as write:
            self.assertEqual(self.get('/api/overview')[0],403)
            self.assertEqual(self.get('/health')[2],b'{"status":"ok"}')
            write.assert_not_called()
