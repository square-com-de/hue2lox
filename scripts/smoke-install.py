"""Run a disposable fresh-install HTTPS smoke test, without Docker or Hue access."""
import importlib.util
import json
import os
from pathlib import Path
import socket
import ssl
import subprocess
import sys
import tempfile
import time
import urllib.request
import urllib.error

spec=importlib.util.spec_from_file_location('prepare_install',Path(__file__).with_name('prepare-install.py'))
setup=importlib.util.module_from_spec(spec);spec.loader.exec_module(setup)

def main():
    with tempfile.TemporaryDirectory(prefix='hue2lox-fresh-smoke-') as tmp:
        with socket.socket() as s:s.bind(('127.0.0.1',0));port=s.getsockname()[1]
        root=setup.prepare(Path(tmp)/'instance','127.0.0.1',port)
        env=dict(os.environ,PORT=str(port),BIND_HOST='127.0.0.1',TLS_CERT=str(root/'certs/server.crt'),TLS_KEY=str(root/'certs/server.key'),HUE_STATE_DIR=str(root/'data'),HUE_REGISTRY_FILE=str(root/'data/registry.json'),HUE_ADMIN_AUTH_FILE=str(root/'data/admin_auth.json'),HUE_CONTROL_TOKEN_FILE=str(root/'secrets/control_token'),HUE_PUBLIC_URL=f'https://127.0.0.1:{port}',HUE_LEGACY_ENABLED='0',HUE_WRITES_ENABLED='0',HUE_COLOR_ENABLED='0',HUE_WHITE_ENABLED='0')
        base=env['HUE_PUBLIC_URL'];ctx=ssl.create_default_context(cafile=str(root/'certs/server.crt'))
        original_token=(root/'secrets/control_token').read_bytes();original_key=(root/'certs/server.key').read_bytes()
        def request(path,body=None,headers=None):
            headers=dict(headers or {})
            if body is not None:headers['Content-Type']='application/json'
            req=urllib.request.Request(base+path,data=json.dumps(body).encode() if body is not None else None,headers=headers)
            try:
                with urllib.request.urlopen(req,context=ctx,timeout=2) as response:return response.status,response.headers,response.read()
            except urllib.error.HTTPError as response:return response.code,response.headers,response.read()
        for run in range(2):
            proc=subprocess.Popen([sys.executable,'src/app.py'],cwd=root,env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            try:
                for _ in range(60):
                    try:
                        if request('/health')[0]==200:break
                    except (OSError,urllib.error.URLError):pass
                    if proc.poll() is not None:raise AssertionError('Fresh process exited')
                    time.sleep(.1)
                else:raise AssertionError('Fresh process did not become healthy')
                for route,name in [('project-license.txt','LICENSE'),('project-notice.txt','NOTICE'),('third-party-notices.txt','THIRD-PARTY-NOTICES.md')]:
                    status,_,content=request('/assets/'+route)
                    assert status==200 and content==(root/name).read_bytes(),route
                import io, zipfile
                status,_,content=request('/assets/hue-models.zip')
                assert status==200
                with zipfile.ZipFile(io.BytesIO(content)) as archive:
                    assert archive.read('LICENSE.txt')==(root/'catalog/LICENSE-zigbee-herdsman-converters').read_bytes()
                    assert archive.read('Hue-Modelltabelle.csv')==(root/'catalog/hue-models.csv').read_bytes()
                    assert archive.read('SOURCE.md')==(root/'catalog/README.md').read_bytes()
                assert request('/api/admin/lights')[0]==401
                assert request('/hue-go/status')[0]==404
                code,headers,body=request('/api/admin/login',{'username':'admin','password':'admin'})
                assert code==200
                cookie=headers['Set-Cookie'].split(';')[0];csrf=json.loads(body)['csrf']
                auth={'Cookie':cookie,'X-CSRF-Token':csrf,'Origin':base}
                code,_,body=request('/api/overview',headers=auth);assert code==200 and json.loads(body)['bridges']==[]
                for path in ['/','/assets/i18n.js','/assets/locales/en.js','/tutorial/en','/licenses']:
                    assert request(path)[0]==200,path
                assert request('/api/admin/token',{},headers={'Cookie':cookie})[0]==403
                code,_,body=request('/api/admin/token',{},headers=auth);assert code==200
                assert json.loads(body)['token'].encode()==original_token.strip()
                assert (root/'certs/server.key').read_bytes()==original_key
            finally:
                proc.terminate()
                try:proc.wait(timeout=5)
                except subprocess.TimeoutExpired:proc.kill();proc.wait()
        print('PASS: fresh empty installation, verified HTTPS, protected API, admin login, CSRF, DE/EN assets, tutorial, notices and restart persistence. No Docker or Hue requests.')

if __name__=='__main__':main()
