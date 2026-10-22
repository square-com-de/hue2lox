#!/usr/bin/env python3
"""Actual cold-update/rollback acceptance on a disposable CI runner, loopback only."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import ssl
import subprocess
import tempfile
import urllib.error
import urllib.request

assert os.environ.get('CI') == 'true' and os.geteuid() == 0, 'Disposable root CI only'
ROOT = Path(__file__).resolve().parents[1]


def run(*args, **kwargs):
    return subprocess.run(args, check=True, **kwargs)


def load(name, file):
    spec=importlib.util.spec_from_file_location(name,file)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module


prepare=load('update_ci_prepare',ROOT/'scripts/prepare-install.py')
update=load('update_ci_stage',ROOT/'scripts/prepare-docker-update.py')

with tempfile.TemporaryDirectory(prefix='hue2lox-update-ci-') as temporary:
    work=Path(temporary)
    target=work/'source'
    shutil.copytree(ROOT,target,ignore=shutil.ignore_patterns('.git','__pycache__','*.pyc'))
    (target/'web/index.html').write_text((target/'web/index.html').read_text()+'\n<!-- update-ci-target-code -->\n')
    (target/'install/release-image.json').write_text(json.dumps({'version':'1.0.0-rc.9001'}))
    update.ROOT=target
    base_image=run('docker','image','inspect','hue2lox-default-ci:check','--format','{{.Id}}',capture_output=True,text=True).stdout.strip()
    for index,(source,registry,scheme) in enumerate([('build','ghcr','https'),('image','ghcr','http'),('image','dockerhub','https')]):
        instance=work/('instance-'+str(index));candidate=instance.with_name(instance.name+'-candidate')
        prepare.prepare(instance,'127.0.0.1',18643+index,scheme=scheme,source='image',registry=registry)
        old_reference=prepare.release_image(registry)
        run('docker','tag',base_image,old_reference)
        def compose(*args,override=None,check=True):
            cmd=['docker','compose','--project-directory',str(instance),'-f',str(instance/'compose.yaml')]
            if override:cmd+=['-f',str(override)]
            return subprocess.run(cmd+list(args),check=check)
        def image_id():
            container=subprocess.check_output(['docker','compose','--project-directory',str(instance),'-f',str(instance/'compose.yaml'),'ps','-q','hue2lox'],text=True).strip()
            return subprocess.check_output(['docker','inspect','--format','{{.Image}}',container],text=True).strip()
        context=ssl.create_default_context(cafile=str(instance/'health-test.crt')) if scheme=='https' else None
        base=f'{scheme}://127.0.0.1:{18643+index}'
        opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),urllib.request.HTTPSHandler(context=context))
        def request(path,body=None,headers=None):
            headers=dict(headers or {})
            if body is not None:headers['Content-Type']='application/json'
            req=urllib.request.Request(base+path,data=json.dumps(body).encode() if body is not None else None,headers=headers)
            try:
                with opener.open(req,timeout=5) as response:return response.status,response.headers,response.read()
            except urllib.error.HTTPError as response:return response.code,response.headers,response.read()
        def login(password,expected=200):
            code,headers,body=request('/api/admin/login',{'username':'admin','password':password})
            assert code==expected
            if expected==200:return {'Cookie':headers['Set-Cookie'].split(';')[0],'X-CSRF-Token':json.loads(body)['csrf'],'Origin':base}
        def snapshot():
            return {str(p.relative_to(instance)):(hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None,p.stat().st_mode&0o777,p.stat().st_uid,p.stat().st_gid)
                    for folder in ('data','secrets','certs') if (instance/folder).exists() for p in [instance/folder,*list((instance/folder).rglob('*'))]}
        old_image=None
        try:
            compose('up','-d','--no-build','--pull','never','--wait','--wait-timeout','120')
            a='ci-update-password-A-local';b='ci-update-password-B-local'
            auth=login('admin')
            assert request('/api/admin/password',{'current_password':'admin','new_password':a},auth)[0]==200
            login('admin',401);login(a)
            old_image=image_id()
            compose('down')
            saved=work/('backup-'+str(index));saved.mkdir(mode=0o700)
            run('cp','-a',str(instance),str(saved/'instance'))
            run('docker','image','save','--output',str(saved/'image.tar'),old_image)
            before=snapshot()
            update.stage(instance,candidate,source,registry)
            # Failures during preparation leave the original data and directory intact.
            assert snapshot()==before
            if source=='image':
                new_reference='ghcr.io/square-com-de/hue2lox:1.0.0-rc.9001' if registry=='ghcr' else 'docker.io/dubctrl/hue2lox:1.0.0-rc.9001'
                run('docker','build','-f',str(candidate/'docker/Dockerfile.status'),'--build-arg','REGISTRY_SOURCE=install/registry.empty.json','-t',new_reference,str(candidate))
            else:
                run('docker','compose','--project-directory',str(candidate),'-f',str(candidate/'compose.yaml'),'build')
            previous=work/('previous-'+str(index));instance.rename(previous);candidate.rename(instance)
            compose('up','-d','--no-build','--pull','never','--wait','--wait-timeout','120')
            assert image_id()!=old_image
            assert b'update-ci-target-code' in request('/')[2]
            assert request('/assets/sidebar-icons.svg')[0]==200
            login('admin',401);auth=login(a)
            assert snapshot()==before
            assert request('/api/admin/password',{'current_password':a,'new_password':b},auth)[0]==200
            login(a,401);login(b)
            compose('down')
            if source=='build':
                # A different, deliberately broken application image must fail its healthcheck.
                (instance/'src/app.py').write_text('raise RuntimeError("isolated update failure fixture")\n')
                compose('build')
                result=compose('up','-d','--no-build','--pull','never','--wait','--wait-timeout','15',check=False)
                assert result.returncode!=0
                compose('down')
            failed=work/('failed-'+str(index));instance.rename(failed)
            run('cp','-a',str(saved/'instance'),str(instance))
            run('docker','image','load','--input',str(saved/'image.tar'))
            override=saved/'rollback-image.yaml';override.write_text('services:\n  hue2lox:\n    image: "'+old_image+'"\n')
            compose('up','-d','--no-build','--pull','never','--wait','--wait-timeout','120',override=override)
            assert image_id()==old_image
            assert b'update-ci-target-code' not in request('/')[2]
            assert snapshot()==before
            login(b,401);login(a)
            print('PASS: real Docker code update and exact-image/data/password rollback: '+source+'/'+registry+'/'+scheme,flush=True)
        finally:
            if (instance/'compose.yaml').exists():compose('down',check=False)
