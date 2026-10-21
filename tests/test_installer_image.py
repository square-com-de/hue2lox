"""Release selection, fail-closed startup and legacy compatibility."""
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch
from tests.test_install import setup
from tests.test_start_install import runner
from tests.test_release_image import m as release


class InstallerImageTests(unittest.TestCase):
    def test_image_modes_and_local_build(self):
        with tempfile.TemporaryDirectory() as directory:
            for registry in ('dockerhub', 'ghcr'):
                for scheme in ('http', 'https'):
                    dest = setup.prepare(Path(directory)/(registry+scheme), '127.0.0.1', 18443,
                                         scheme=scheme, registry=registry)
                    compose = (dest/'compose.yaml').read_text()
                    image = setup.release_image(registry)
                    self.assertIn('    image: ' + image, compose)
                    self.assertNotIn('    build:', compose)
                    self.assertIn('network_mode: host', compose)
                    self.assertEqual('TLS_CERT:' in compose, scheme == 'https')
                    self.assertEqual(runner.installation_source(dest), ('image', image))
            dest = setup.prepare(Path(directory)/'dev', '127.0.0.1', source='build')
            self.assertIn('    build:', (dest/'compose.yaml').read_text())
            self.assertEqual(runner.installation_source(dest), ('build', ''))
            # No new metadata in historical installations: keep building, never migrate.
            env = (dest/'.env').read_text().replace('HUE2LOX_SOURCE=build\n', '')
            (dest/'.env').write_text(env)
            self.assertEqual(runner.installation_source(dest), ('build', ''))

    def test_invalid_selection_does_not_create_files(self):
        with tempfile.TemporaryDirectory() as directory:
            for kwargs in ({'source': 'latest'}, {'registry': 'other'}, {'registry': 'ghcr\nBAD=1'}):
                dest = Path(directory)/'invalid'
                with self.assertRaises(ValueError): setup.prepare(dest, '127.0.0.1', **kwargs)
                self.assertFalse(dest.exists())

    def test_start_uses_saved_mode_and_never_builds_release(self):
        with tempfile.TemporaryDirectory() as directory:
            for source, registry in [('image','dockerhub'), ('image','ghcr'), ('build','dockerhub')]:
                dest = setup.prepare(Path(directory)/(source+registry), '127.0.0.1', source=source, registry=registry)
                before = {p: (dest/p).read_bytes() for p in ('.env','compose.yaml','data/admin_auth.json','secrets/control_token')}
                response = Mock(status=200); response.read.return_value = b'{"status":"ok"}'
                context = Mock(); context.__enter__ = Mock(return_value=response); context.__exit__ = Mock(return_value=False)
                with patch.object(runner.sys,'platform','linux'), patch.object(runner.os,'geteuid',return_value=0), \
                     patch.object(runner.shutil,'which',return_value='/usr/bin/docker'), \
                     patch.object(runner.subprocess,'run',return_value=subprocess.CompletedProcess([],0,stdout='')) as run, \
                     patch.object(runner.urllib.request,'urlopen',return_value=context), \
                     patch.dict(runner.os.environ, {'HUE2LOX_INSTALL_COMPACT':'0'}), patch.object(runner,'print_success'):
                    runner.start(dest)
                commands = [c.args[0] for c in run.call_args_list]
                up = next(c for c in commands if 'up' in c)
                self.assertEqual(up[up.index('up'):], ['up','-d','--no-build','--pull','missing'] if source=='image' else ['up','-d','--build'])
                for p, content in before.items(): self.assertEqual((dest/p).read_bytes(), content)

    def test_failed_pull_does_not_build_fallback_or_report_success(self):
        with tempfile.TemporaryDirectory() as directory:
            dest = setup.prepare(Path(directory)/'new', '127.0.0.1')
            def run(command, **kwargs):
                if 'up' in command: raise subprocess.CalledProcessError(1, command)
                return subprocess.CompletedProcess(command,0,stdout='')
            with patch.object(runner.sys,'platform','linux'), patch.object(runner.os,'geteuid',return_value=0), \
                 patch.object(runner.shutil,'which',return_value='/usr/bin/docker'), \
                 patch.object(runner.subprocess,'run',side_effect=run) as calls, \
                 patch.object(runner.urllib.request,'urlopen') as health, patch.object(runner,'print_success') as success, \
                 patch.dict(runner.os.environ, {'HUE2LOX_INSTALL_COMPACT':'0'}):
                with self.assertRaises(subprocess.CalledProcessError): runner.start(dest)
                health.assert_not_called(); success.assert_not_called()
                self.assertFalse(any('--build' in c.args[0] for c in calls.call_args_list))

    def test_tampered_or_floating_image_rejected_before_docker(self):
        with tempfile.TemporaryDirectory() as directory:
            for bad in ('docker.io/dubctrl/hue2lox:latest', 'ghcr.io/other/hue2lox:1.0.0', 'bad'):
                dest = setup.prepare(Path(directory)/str(len(list(Path(directory).iterdir()))), '127.0.0.1')
                (dest/'.env').write_text((dest/'.env').read_text().replace(setup.release_image(),bad))
                with patch.object(runner.sys,'platform','linux'), patch.object(runner.os,'geteuid',return_value=0), \
                     patch.object(runner.subprocess,'run') as run:
                    with self.assertRaises(ValueError): runner.start(dest)
                    run.assert_not_called()
            dest = setup.prepare(Path(directory)/'mismatch', '127.0.0.1')
            (dest/'compose.yaml').write_text((dest/'compose.yaml').read_text().replace(setup.release_image(),setup.release_image('ghcr')))
            with self.assertRaisesRegex(ValueError,'disagree'): runner.installation_source(dest)

    def test_release_tag_must_match_installer_default(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'release-image.json'
            path.write_text(json.dumps({'version':'1.0.0-rc.6'}))
            release.check_installer_version('1.0.0-rc.6',path)
            with self.assertRaisesRegex(ValueError,'before tagging'):
                release.check_installer_version('1.0.0-rc.7',path)

    def test_interactive_choices_in_both_languages(self):
        script = Path(__file__).resolve().parents[1]/'install-assistant.sh'
        for lang in ('de','en'):
            for value, expected in [('\n','image dockerhub'),('2\n','image ghcr'),('3\n','build dockerhub'),('wrong\n2\n','image ghcr')]:
                result = subprocess.run(['bash','-c', 'source "$1"; HUE2LOX_INSTALL_LANG=$2; choose_install_source; printf "RESULT:%s %s" "$INSTALL_SOURCE" "$INSTALL_REGISTRY"',
                                         'test',str(script),lang],input=value,text=True,capture_output=True)
                self.assertEqual(result.returncode,0,result.stderr)
                self.assertIn('RESULT:'+expected,result.stdout)
                self.assertIn(setup.release_image().split(':')[-1],result.stdout)
            result = subprocess.run(['bash','-c','source "$1"; choose_install_source','test',str(script)],input='',text=True,capture_output=True)
            self.assertNotEqual(result.returncode,0)
