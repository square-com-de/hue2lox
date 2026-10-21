"""The shipped container health command must follow its configured bind endpoint."""
import json
import os
from pathlib import Path
import ssl
import unittest
import urllib.request
from unittest.mock import Mock, patch

class NetworkHealthTests(unittest.TestCase):
    def test_health_command_uses_configured_ip_and_port(self):
        compose=(Path(__file__).resolve().parent.parent/'docker/compose.install.yaml').read_text()
        line=next(line.strip()[6:] for line in compose.splitlines() if line.strip().startswith('test: '))
        command=json.loads(line)
        response=Mock(status=200)
        response.read.return_value=b'{"status":"ok"}'
        with patch.dict(os.environ, {'BIND_HOST':'10.200.0.138','PORT':'19443'}), patch.object(ssl,'create_default_context') as context, patch.object(urllib.request,'urlopen',return_value=response) as request:
            exec(command[3], {})
            request.assert_called_once_with('https://10.200.0.138:19443/health',context=context.return_value,timeout=3)
            context.assert_called_once_with(cafile='/certs/server.crt')
