"""Exercise generated install settings against real routing; all Hue writes mocked."""
import http.client
from http.server import ThreadingHTTPServer
import json
import os
from pathlib import Path
import tempfile
import threading
from unittest.mock import patch
import xml.etree.ElementTree as ET

import app
import loxone_export


def assert_ready(test, values):
    for flag in ('WRITES', 'COLOR', 'WHITE'):
        test.assertEqual(values[f'HUE_{flag}_ENABLED'], '1')
    with tempfile.TemporaryDirectory() as directory:
        registry = Path(directory) / 'registry.json'
        registry.write_bytes((Path(__file__).parent / 'fixtures/registry.json').read_bytes())
        token = Path(directory) / 'token'
        token.write_text('test-only-' + 'x' * 48)
        settings = dict(values, HUE_REGISTRY_FILE=str(registry), HUE_STATE_DIR=directory,
                        HUE_CONTROL_TOKEN_FILE=str(token))
        with patch.dict(os.environ, settings, clear=True), patch('app.write_state', return_value={'status': 'accepted'}) as write:
            light = loxone_export.lights()[0]
            test.assertTrue(light['writes_enabled'])
            test.assertEqual(light['recommended_mode'], 'lumitech')
            test.assertTrue({'switch', 'dim', 'rgb', 'tw', 'lumitech'} <= {c['id'] for c in light['commands']})
            for mode in ('rgb', 'lumitech'):
                xml = ET.fromstring(loxone_export.export_xml([light['key']], False, variants={light['key']: mode}))
                test.assertIn('loxone_' + mode, xml.find('VirtualOutCmd').get('CmdOnPost'))
            write.assert_not_called()
            server = ThreadingHTTPServer(('127.0.0.1', 0), app.Handler)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            def request(body, authorized):
                connection = http.client.HTTPConnection('127.0.0.1', server.server_port, timeout=5)
                headers = {'Content-Type': 'application/json'}
                if authorized:
                    headers['Authorization'] = 'Bearer ' + token.read_text()
                connection.request('PUT', light['path'], json.dumps(body), headers)
                response = connection.getresponse()
                status = response.status
                response.read()
                connection.close()
                return status
            try:
                test.assertEqual(request({'on': True}, False), 401)
                write.assert_not_called()
                for body in ({'on': True}, {'brightness': 30}, {'loxone_rgb': 100},
                             {'loxone_lumitech': 100}, {'loxone_lumitech': 200302700}):
                    with test.subTest(body=body):
                        test.assertEqual(request(body, True), 200)
                test.assertEqual(write.call_count, 5)
            finally:
                server.shutdown()
                server.server_close()
                thread.join()
