"""Stable approval is separate from green technical tests; never touches a registry."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('stable_gate',ROOT/'scripts/release-image.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)


class StableGateTests(unittest.TestCase):
    def record(self):
        return {'schema_version':1,'version':'1.0.2','approved':True,'source_sha256':'b'*64,'checks':{
            name:{'passed':True,'evidence':['https://github.com/square-com-de/hue2lox/issues/1']}
            for name in m.STABLE_CHECKS}}
    def check(self,record,version='1.0.2'):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'gate.json';path.write_text(json.dumps(record))
            with patch.object(m,'acceptance_source_digest',return_value='b'*64):
                return m.check_stable_readiness({'version':version,'prerelease':False,'commit':'a'*40},path)
    def test_stable_needs_exact_version_explicit_boolean_and_every_evidence(self):
        good=self.record();self.check(good)
        for field,value in [('approved',False),('approved','true'),('version','1.0.1'),('schema_version',2),('source_sha256','c'*64)]:
            altered=copy.deepcopy(good);altered[field]=value
            with self.subTest(field=field,value=value),self.assertRaises(ValueError):self.check(altered)
        for name in m.STABLE_CHECKS:
            for evidence in ([],[''],['https://example.org/not-our-acceptance']):
                altered=copy.deepcopy(good);altered['checks'][name]['evidence']=evidence
                with self.subTest(name=name,evidence=evidence),self.assertRaises(ValueError):self.check(altered)
            altered=copy.deepcopy(good);altered['checks'][name]['passed']=False
            with self.assertRaises(ValueError):self.check(altered)
    def test_rc_remains_buildable_without_stable_approval(self):
        m.check_stable_readiness({'version':'1.0.2-rc.1','prerelease':True},Path('/not-present.json'))
    def test_missing_invalid_or_unapproved_record_blocks(self):
        for record in (None,[],{},self.record()|{'approved':False}):
            with self.assertRaises(ValueError):self.check(record)
        with self.assertRaises(ValueError):m.check_stable_readiness({'version':'1.0.2','prerelease':False},Path('/not-present.json'))
    def test_unapproved_gate_prevents_any_registry_operation(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'gate.json';path.write_text(json.dumps(self.record()|{'approved':False}))
            with patch.object(m,'STABLE_READINESS',path),patch.object(m,'verify_registry') as registry,patch.object(m.subprocess,'run') as command:
                with self.assertRaises(ValueError):m.verify_public({'version':'1.0.2','prerelease':False})
                registry.assert_not_called();command.assert_not_called()

    def test_content_binding_ignores_only_gate_and_changes_for_code_or_docs(self):
        import subprocess
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/'compliance').mkdir()
            def git(*args):return subprocess.check_output(['git',*args],cwd=root,text=True).strip()
            git('init','-q');git('config','user.name','Fixture');git('config','user.email','fixture@example.invalid')
            (root/'README.md').write_text('reviewed instructions');(root/'app.py').write_text('print(1)')
            (root/'compliance/stable-readiness.json').write_text('{}');git('add','.');git('commit','-qm','candidate')
            expected=m.acceptance_source_digest('HEAD',root)
            (root/'compliance/stable-readiness.json').write_text('{"approved":true}');git('add','.');git('commit','-qm','approval')
            self.assertEqual(expected,m.acceptance_source_digest('HEAD',root))
            (root/'README.md').write_text('new unreviewed instructions');git('add','.');git('commit','-qm','new docs')
            self.assertNotEqual(expected,m.acceptance_source_digest('HEAD',root))
            changed=m.acceptance_source_digest('HEAD',root)
            (root/'app.py').write_text('print(2)');git('add','.');git('commit','-qm','new code')
            self.assertNotEqual(changed,m.acceptance_source_digest('HEAD',root))
