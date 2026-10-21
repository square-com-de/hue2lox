import copy
import importlib.util
import io
import json
import os
import zipfile
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location('release_image', ROOT / 'scripts/release-image.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
SHA = 'a' * 40


def event(tag='v1.0.0-rc.4', prerelease=True):
    return {'action': 'published', 'release': {'id': 42, 'tag_name': tag,
            'draft': False, 'prerelease': prerelease}}


class ReleaseTests(unittest.TestCase):
    def test_rc_and_stable_get_explicit_versions(self):
        for tag, rc in [('v1.0.0-rc.4', True), ('v1.0.0', False), ('v2.1.0-rc.1', True)]:
            with self.subTest(tag=tag):
                result = m.plan(event(tag, rc), 'release', m.REPO, SHA)
                self.assertEqual(result['version'], tag[1:])
                self.assertEqual(result['prerelease'], rc)
                self.assertEqual(result['image'], 'ghcr.io/square-com-de/hue2lox')

    def test_manual_push_pr_draft_and_old_releases_cannot_publish(self):
        for name in ('workflow_dispatch', 'push', 'pull_request'):
            with self.subTest(name=name), self.assertRaises(ValueError):
                m.plan(event(), name, m.REPO, SHA)
        for tag in ('main', 'v1.0.0-rc.1', 'v1.0.0-rc.2', 'v1.0.0-rc.3',
                    'v0.9.0', 'v01.0.0', 'v1.0.0-rc.0', 'v1.0.0; echo bad'):
            with self.subTest(tag=tag), self.assertRaises(ValueError):
                m.plan(event(tag), 'release', m.REPO, SHA)
        for field, value in [('draft', True), ('prerelease', False), ('id', None)]:
            data = event()
            data['release'][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                m.plan(data, 'release', m.REPO, SHA)
        for repo, commit in [('other/repo', SHA), (m.REPO, 'abc')]:
            with self.assertRaises(ValueError):
                m.plan(event(), 'release', repo, commit)
        data = event()
        data['action'] = 'edited'
        with self.assertRaises(ValueError):
            m.plan(data, 'release', m.REPO, SHA)
        with self.assertRaises(ValueError):
            m.plan(event('v1.0.0', True), 'release', m.REPO, SHA)

    def test_evidence_must_match_source_platform_and_label(self):
        image = {'Id': 'sha256:123', 'Architecture': 'arm64', 'Os': 'linux',
                 'Config': {'Labels': {'org.opencontainers.image.revision': SHA}}}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            (path / 'source-commit.txt').write_text(SHA)
            (path / 'image.json').write_text(json.dumps([image]))
            self.assertEqual(m.verify_inventory(path, SHA, 'arm64'), 'sha256:123')
            with self.assertRaises(ValueError):
                m.verify_inventory(path, 'b' * 40, 'arm64')
            with self.assertRaises(ValueError):
                m.verify_inventory(path, SHA, 'amd64')
            altered = copy.deepcopy(image)
            altered['Config']['Labels']['org.opencontainers.image.revision'] = 'b' * 40
            (path / 'image.json').write_text(json.dumps([altered]))
            with self.assertRaises(ValueError):
                m.verify_inventory(path, SHA, 'arm64')

    def test_registry_auth_and_network_errors_do_not_mean_missing_tag(self):
        for error in ('unauthorized', 'denied', 'connection timed out'):
            response = subprocess.CompletedProcess([], 1, '', error)
            with patch.object(m.subprocess, 'run', return_value=response), self.assertRaises(RuntimeError):
                m.remote_manifest('example:tag')
        response = subprocess.CompletedProcess([], 1, '', 'manifest unknown')
        with patch.object(m.subprocess, 'run', return_value=response):
            self.assertIsNone(m.remote_manifest('example:tag'))

    def test_existing_release_asset_is_verified_anonymously_never_replaced(self):
        info = m.plan(event(), 'release', m.REPO, SHA)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'source.zip'
            path.write_bytes(b'expected source')
            release = {'tag_name': info['tag'], 'draft': False, 'prerelease': True, 'assets': [
                {'name': path.name, 'browser_download_url': 'https://example.org/asset'}]}
            with patch.object(m, 'run', return_value=json.dumps(release)), \
                 patch.object(m.subprocess, 'run') as upload, \
                 patch.object(m.urllib.request, 'urlopen', return_value=io.BytesIO(path.read_bytes())) as fetch:
                m.ensure_asset(info, path)
                upload.assert_not_called()
                fetch.assert_called_once_with('https://example.org/asset', timeout=120)
            with patch.object(m, 'run', return_value=json.dumps(release)), \
                 patch.object(m.subprocess, 'run') as upload, \
                 patch.object(m.urllib.request, 'urlopen', return_value=io.BytesIO(b'other')):
                with self.assertRaisesRegex(ValueError, 'refusing to overwrite'):
                    m.ensure_asset(info, path)
                upload.assert_not_called()

    def test_wrong_loaded_candidate_stops_before_registry_push(self):
        info = m.plan(event(), 'release', m.REPO, SHA)
        with patch.object(m.Path, 'iterdir', return_value=iter([])), \
             patch.object(m.subprocess, 'run') as commands, \
             patch.object(m, 'verify_inventory', return_value='expected'), \
             patch.object(m, 'run', return_value='different'), \
             patch.object(m, 'remote_manifest') as registry:
            with self.assertRaisesRegex(ValueError, 'Loaded image'):
                m.publish(info)
            registry.assert_not_called()
            self.assertFalse(any('push' in c.args[0] for c in commands.call_args_list))

    def test_rc_public_verification_never_promotes_latest(self):
        info = m.plan(event(), 'release', m.REPO, SHA)
        manifests = [{'Descriptor': {'platform': {'architecture': a}, 'digest': 'sha256:' + a}}
                     for a in m.ARCHES]
        with tempfile.TemporaryDirectory() as directory, \
             patch.object(m, 'run', side_effect=[json.dumps(manifests), 'image-id', 'image-id']) as reads, \
             patch.object(m.subprocess, 'run') as commands, \
             patch.object(m, 'verify_inventory', return_value='image-id'), \
             patch.object(m, 'ensure_asset') as asset, \
             patch.object(m, 'Path', side_effect=lambda name: Path(directory) / name):
            m.verify_public(info)
            self.assertTrue(asset.called)
            self.assertFalse(any('latest' in str(c) for c in commands.call_args_list))
            self.assertFalse(any('gh' in c.args for c in reads.call_args_list))
            for c in commands.call_args_list:
                self.assertIn('DOCKER_CONFIG', c.kwargs['env'])

    def test_prepare_archives_the_commit_not_untracked_workspace_files(self):
        with tempfile.TemporaryDirectory() as directory:
            previous = Path.cwd()
            os.chdir(directory)
            try:
                subprocess.run(['git', 'init', '-q'], check=True)
                Path('README.md').write_text('committed source')
                subprocess.run(['git', 'add', 'README.md'], check=True)
                subprocess.run(['git', '-c', 'user.name=Test', '-c', 'user.email=test@example.org',
                                '-c', 'commit.gpgsign=false', 'commit', '-qm', 'fixture'], check=True)
                commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
                Path('private-untracked.txt').write_text('not a release file')
                Path('materials').mkdir()
                Path('materials/hue2lox-base-sources.tar.gz').write_bytes(b'checked bundle')
                Path('evidence/amd64').mkdir(parents=True)
                Path('evidence/arm64').mkdir()
                info = m.plan(event(), 'release', m.REPO, commit)
                original_run = subprocess.run

                def command(args, **kwargs):
                    if args[0] == 'sha256sum':
                        return subprocess.CompletedProcess(args, 0)
                    return original_run(args, **kwargs)

                with patch.object(m.subprocess, 'run', side_effect=command), \
                     patch.object(m, 'verify_inventory', return_value='image-id'):
                    assets = m.prepare(info)
                with zipfile.ZipFile(assets / 'hue2lox-v1.0.0-rc.4.zip') as archive:
                    self.assertEqual(archive.read('hue2lox-v1.0.0-rc.4/README.md'), b'committed source')
                    self.assertFalse(any('private-untracked' in name for name in archive.namelist()))
                for line in (assets / 'SHA256SUMS.txt').read_text().splitlines():
                    expected, name = line.split('  ')
                    self.assertEqual(m.digest(assets / name), expected)
            finally:
                os.chdir(previous)

    def test_stable_promotion_requires_github_latest_and_public_verification(self):
        info = m.plan(event('v1.0.0', False), 'release', m.REPO, SHA)
        manifests = [{'Descriptor': {'platform': {'architecture': a}, 'digest': 'sha256:' + a}}
                     for a in m.ARCHES]
        for latest in ('v1.0.0', 'v1.1.0'):
            with self.subTest(latest=latest), tempfile.TemporaryDirectory() as directory, \
                 patch.object(m, 'run', side_effect=[json.dumps(manifests), 'image-id', 'image-id',
                                                    json.dumps({'tag_name': latest})]), \
                 patch.object(m.subprocess, 'run') as commands, \
                 patch.object(m, 'verify_inventory', return_value='image-id'), \
                 patch.object(m, 'ensure_asset'), \
                 patch.object(m, 'Path', side_effect=lambda name: Path(directory) / name):
                m.verify_public(info)
                pushes = [c.args[0] for c in commands.call_args_list if 'push' in c.args[0]]
                self.assertEqual(bool(pushes), latest == 'v1.0.0')
        with patch.object(m, 'run', side_effect=RuntimeError('anonymous access denied')), \
             patch.object(m.subprocess, 'run') as commands:
            with self.assertRaises(RuntimeError):
                m.verify_public(info)
            commands.assert_not_called()

    def test_workflow_has_no_manual_publishing_path(self):
        text = (ROOT / '.github/workflows/release-image.yml').read_text()
        self.assertIn('types: [published]', text)
        self.assertNotIn('workflow_dispatch', text)
        self.assertNotIn('pull_request:', text)
        self.assertIn('needs: [quality, materials]', text)
        self.assertIn('needs: publish', text)
