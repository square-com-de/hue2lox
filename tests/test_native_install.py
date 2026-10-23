"""Native package boundaries and lifecycle; only temporary paths and fake services."""
import argparse
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tarfile
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location('native_manage', ROOT / 'deployment/native/manage.py')
native = importlib.util.module_from_spec(SPEC)
# dataclasses consult the module registry when resolving annotations.
import sys
sys.modules[SPEC.name] = native
SPEC.loader.exec_module(native)


def runtime_files():
    files = {}
    for tree in ('src', 'web', 'catalog', 'trust', 'config', 'deployment/native'):
        for path in (ROOT / tree).rglob('*'):
            if path.is_file() and '__pycache__' not in path.parts and path.suffix != '.pyc':
                files[path.relative_to(ROOT).as_posix()] = path.read_bytes()
    for name in ('LICENSE', 'NOTICE', 'THIRD-PARTY-NOTICES.md', 'scripts/prepare-state.py'):
        files[name] = (ROOT / name).read_bytes()
    return files


def package(path, *, version='1.2.3', commit='a' * 40, change=None, extra=()):
    files = runtime_files()
    manifest = {'schema_version': 1, 'version': version, 'commit': commit,
                'dirty': False,
                'files': {key: hashlib.sha256(value).hexdigest() for key, value in files.items()}}
    if change:
        change(files, manifest)
    files['manifest.json'] = json.dumps(manifest).encode()
    with tarfile.open(path, 'w:gz') as archive:
        for name, value in files.items():
            info = tarfile.TarInfo('hue2lox-native/' + name)
            info.mode = 0o644
            info.size = len(value)
            archive.addfile(info, io.BytesIO(value))
        for info, value in extra:
            archive.addfile(info, io.BytesIO(value) if value is not None else None)
    return hashlib.sha256(path.read_bytes()).hexdigest()


class NativePackageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.archive = self.root / 'native.tar.gz'
        self.destination = self.root / 'extract'

    def verify(self, digest):
        return native.verify_package(self.archive, digest, self.destination)

    def test_valid_package_keeps_identity_and_bytes(self):
        digest = package(self.archive)
        self.verify(digest)
        self.assertEqual((self.destination / 'src/app.py').read_bytes(), (ROOT / 'src/app.py').read_bytes())
        manifest = json.loads((self.destination / 'manifest.json').read_text())
        self.assertEqual(manifest['commit'], 'a' * 40)
        self.assertEqual(manifest['version'], '1.2.3')

    def test_outer_checksum_rejected_before_extract(self):
        package(self.archive)
        with self.assertRaises((ValueError, RuntimeError)):
            self.verify('0' * 64)
        self.assertFalse((self.destination / 'src/app.py').exists())

    def test_manifest_checksum_mismatch_rejected(self):
        digest = package(self.archive, change=lambda files, manifest: files.__setitem__('src/app.py', b'altered'))
        with self.assertRaises((ValueError, RuntimeError)):
            self.verify(digest)

    def test_unlisted_file_rejected(self):
        digest = package(self.archive, change=lambda files, manifest: files.__setitem__('extra.py', b'extra'))
        with self.assertRaises((ValueError, RuntimeError)):
            self.verify(digest)

    def test_missing_file_rejected(self):
        digest = package(self.archive, change=lambda files, manifest: files.pop('src/app.py'))
        with self.assertRaises((ValueError, RuntimeError)):
            self.verify(digest)

    def test_incomplete_runtime_even_with_matching_manifest_rejected(self):
        def remove_required(files, manifest):
            files.pop('src/app.py')
            manifest['files'].pop('src/app.py')
        digest = package(self.archive, change=remove_required)
        with self.assertRaises((ValueError, RuntimeError)):
            self.verify(digest)

    def test_expanded_member_limit_checked_before_reading_payload(self):
        info = tarfile.TarInfo('hue2lox-native/oversized')
        info.size = 32 * 1024 * 1024 + 1
        # Intentionally truncated: the size guard must reject this header before
        # reading payload. Python 3.15's TAR writer refuses a missing fileobj.
        import gzip
        with gzip.open(self.archive, 'wb') as archive:
            archive.write(info.tobuf())
            archive.write(b'\0' * 1024)
        digest = hashlib.sha256(self.archive.read_bytes()).hexdigest()
        with self.assertRaisesRegex(ValueError, 'large'):
            self.verify(digest)
        self.assertFalse(self.destination.exists())

    def test_duplicate_manifest_keys_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            native.strict_json('{"version":"1.2.3","version":"2.0.0"}')

    def test_invalid_identity_rejected(self):
        for field, value in (('version', '../../escape'), ('commit', 'main'), ('schema_version', 999), ('schema_version', True)):
            with self.subTest(field=field):
                digest = package(self.archive, change=lambda files, manifest: manifest.__setitem__(field, value))
                with self.assertRaises((ValueError, RuntimeError)):
                    self.verify(digest)

    def test_traversal_absolute_and_wrong_prefix_rejected(self):
        for name in ('hue2lox-native/../../escaped', str(self.root / 'absolute-escaped'), 'other/file'):
            with self.subTest(name=name):
                info = tarfile.TarInfo(name)
                info.size = 1
                digest = package(self.archive, extra=[(info, b'x')])
                with self.assertRaises((ValueError, RuntimeError)):
                    self.verify(digest)
        self.assertFalse((self.root / 'escaped').exists())

    def test_symlink_hardlink_and_special_file_rejected(self):
        for kind in (tarfile.SYMTYPE, tarfile.LNKTYPE, tarfile.FIFOTYPE, tarfile.CHRTYPE):
            with self.subTest(kind=kind):
                info = tarfile.TarInfo('hue2lox-native/link')
                info.type = kind
                info.linkname = '/etc/passwd'
                digest = package(self.archive, extra=[(info, None)])
                with self.assertRaises((ValueError, RuntimeError)):
                    self.verify(digest)

    def test_duplicate_member_rejected(self):
        info = tarfile.TarInfo('hue2lox-native/src/app.py')
        info.size = 1
        digest = package(self.archive, extra=[(info, b'x')])
        with self.assertRaises((ValueError, RuntimeError)):
            self.verify(digest)


class NativeLifecycleTests(unittest.TestCase):
    def setUp(self):
        from contextlib import ExitStack
        import os
        import subprocess
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.layout = native.Layout(self.root / 'target')
        self.archive = self.root / 'native.tar.gz'
        self.args = argparse.Namespace(package=self.archive, sha256=package(self.archive),
                                       host='127.0.0.1', port=18443, purge_data=False)
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        self.stack.enter_context(patch.object(native, 'print', create=True))
        self.stack.enter_context(patch.object(native, 'platform_check'))
        self.stack.enter_context(patch.object(native, 'ensure_account', return_value=(os.getuid(), os.getgid())))
        self.stack.enter_context(patch.object(native.os, 'chown'))
        self.stack.enter_context(patch.object(native.socket, 'socket'))
        self.systemctl = self.stack.enter_context(patch.object(native, 'run_systemctl'))
        self.health = self.stack.enter_context(patch.object(native, 'health'))
        self.stack.enter_context(patch.object(native, 'reset_failure'))
        # Real credential/certificate preparation, but no account changes or chown.
        def initialize(layout, runtime, host, uid, gid):
            subprocess.run([sys.executable, str(runtime / 'scripts/prepare-state.py'),
                            '--state-directory', str(layout.state),
                            '--certificate-directory', str(layout.config / 'certs'),
                            '--secret-directory', str(layout.config / 'secrets'),
                            '--host', host], check=True, capture_output=True)
            native.private_permissions(layout, uid, gid)
        self.stack.enter_context(patch.object(native, 'initialize_private', side_effect=initialize))

    def install(self):
        native.install(self.args, self.layout)

    def protected_snapshot(self):
        return {str(path.relative_to(self.layout.root)): (path.read_bytes(), path.stat().st_mode & 0o777)
                for base in (self.layout.config, self.layout.state)
                for path in base.rglob('*') if path.is_file()}

    def changed_user_state(self):
        (self.layout.state / 'registry.json').write_text('{"schema_version":1,"bridges":[],"user_marker":"preserve"}')
        (self.layout.state / 'admin_auth.json').write_text('user changed credential hash')
        (self.layout.config / 'secrets/control_token').write_text('user changed token')

    def next_package(self):
        self.args.sha256 = package(self.archive, version='1.2.4', commit='b' * 40)

    def test_fresh_install_preserves_disabled_control_and_private_modes(self):
        self.install()
        values = native.settings(self.layout)
        for key in ('HUE_WRITES_ENABLED', 'HUE_COLOR_ENABLED', 'HUE_WHITE_ENABLED'):
            self.assertEqual(values[key], '0')
        self.assertEqual((self.layout.state / 'admin_auth.json').stat().st_mode & 0o777, 0o600)
        self.assertEqual((self.layout.config / 'certs/server.key').stat().st_mode & 0o777, 0o640)
        self.assertEqual(self.layout.state.stat().st_mode & 0o777, 0o700)
        self.assertTrue(self.layout.current.is_symlink())
        self.health.assert_called_once_with(self.layout)
        self.systemctl.assert_any_call('enable', '--now', native.SERVICE)

    def test_early_preparation_failure_cleans_own_files_and_allows_retry(self):
        with patch.object(native, 'initialize_private', side_effect=ValueError('certificate preparation failed')):
            with self.assertRaisesRegex(ValueError, 'certificate preparation failed'):
                self.install()
        for path in (self.layout.app, self.layout.config, self.layout.state, self.layout.unit):
            self.assertFalse(path.exists(), str(path))
        self.systemctl.assert_not_called()
        self.install()
        self.assertTrue(self.layout.current.is_symlink())
        self.assertTrue((self.layout.config / 'install.json').is_file())
        self.health.assert_called_once_with(self.layout)

    def test_repeat_install_refuses_to_reset_existing_state(self):
        self.install()
        self.changed_user_state()
        before = self.protected_snapshot()
        self.systemctl.reset_mock()
        with self.assertRaises(ValueError):
            self.install()
        self.assertEqual(self.protected_snapshot(), before)
        self.systemctl.assert_not_called()

    def test_update_keeps_user_state_and_protected_matching_backup(self):
        self.install()
        self.changed_user_state()
        before = self.protected_snapshot()
        previous = self.layout.current.resolve()
        self.next_package()
        native.update(self.args, self.layout)
        self.assertNotEqual(self.layout.current.resolve(), previous)
        after = self.protected_snapshot()
        for name in before:
            if not name.endswith('/install.json'):
                self.assertEqual(after[name], before[name], name)
        backups = list(self.layout.backups.iterdir())
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].stat().st_mode & 0o777, 0o700)
        self.assertEqual((backups[0] / 'state/admin_auth.json').read_bytes(),
                         (self.layout.state / 'admin_auth.json').read_bytes())
        self.assertEqual(json.loads((backups[0] / 'previous.json').read_text())['active'], str(previous))

    def test_failed_health_restores_code_and_matching_private_snapshot(self):
        self.install()
        self.changed_user_state()
        before = self.protected_snapshot()
        previous = self.layout.current.resolve()
        self.next_package()
        def fail_candidate_then_verify_old(layout):
            if layout.current.resolve() != previous:
                (layout.state / 'admin_auth.json').write_text('candidate mutated state')
                raise ValueError('simulated HTTPS failure')
        self.health.side_effect = fail_candidate_then_verify_old
        with self.assertRaisesRegex(ValueError, 'previous application and private state restored'):
            native.update(self.args, self.layout)
        self.assertEqual(self.layout.current.resolve(), previous)
        self.assertEqual(self.protected_snapshot(), before)

    def test_invalid_update_never_stops_running_service(self):
        self.install()
        self.changed_user_state()
        before = self.protected_snapshot()
        self.args.sha256 = '0' * 64
        self.systemctl.reset_mock()
        with self.assertRaises(ValueError):
            native.update(self.args, self.layout)
        self.systemctl.assert_not_called()
        self.assertEqual(self.protected_snapshot(), before)

    def test_uninstall_retains_private_data_and_explicit_purge_removes_it(self):
        self.install()
        self.changed_user_state()
        marker = self.root / 'unrelated-docker-instance'
        marker.write_text('do not touch')
        native.uninstall(self.args, self.layout)
        self.assertFalse(self.layout.app.exists())
        self.assertFalse(self.layout.unit.exists())
        self.assertEqual((self.layout.state / 'admin_auth.json').read_text(), 'user changed credential hash')
        self.assertEqual(marker.read_text(), 'do not touch')
        self.args.purge_data = True
        native.uninstall(self.args, self.layout)
        self.assertFalse(self.layout.state.exists())
        self.assertFalse(self.layout.config.exists())
        self.assertEqual(marker.read_text(), 'do not touch')

    def test_changed_service_file_blocks_destructive_operations(self):
        self.install()
        self.layout.unit.write_text('another service')
        self.systemctl.reset_mock()
        with self.assertRaisesRegex(ValueError, 'service file changed'):
            native.uninstall(self.args, self.layout)
        self.systemctl.assert_not_called()
        self.assertTrue(self.layout.state.is_dir())

    def test_symlinked_private_state_blocks_update(self):
        self.install()
        outside = self.root / 'external-secret'
        outside.write_text('untouched')
        (self.layout.state / 'alias').symlink_to(outside)
        self.systemctl.reset_mock()
        with self.assertRaisesRegex(ValueError, 'links'):
            native.update(self.args, self.layout)
        self.assertEqual(outside.read_text(), 'untouched')
        self.systemctl.assert_not_called()

    def test_reinstall_retained_data_requires_explicit_matching_package(self):
        self.install()
        self.changed_user_state()
        before = self.protected_snapshot()
        native.uninstall(self.args, self.layout)
        with self.assertRaises(ValueError): self.install()
        self.args.keep_data = True
        self.next_package()
        with self.assertRaisesRegex(ValueError, 'identity'): self.install()
        self.assertFalse(self.layout.app.exists())
        self.args.sha256 = package(self.archive)
        self.install()
        for name, value in before.items():
            if not name.endswith('/install.json'):
                self.assertEqual(self.protected_snapshot()[name], value)
        self.systemctl.assert_any_call('enable', '--now', native.SERVICE)

    def test_uninstall_symlink_preflight_does_not_change_service(self):
        self.install()
        link = self.layout.current.resolve() / 'alias'
        link.symlink_to(self.root / 'outside')
        before = self.protected_snapshot()
        self.systemctl.reset_mock()
        with self.assertRaises(ValueError): native.uninstall(self.args, self.layout)
        self.systemctl.assert_not_called()
        self.assertTrue(self.layout.unit.is_file())
        self.assertEqual(before, self.protected_snapshot())

    def test_interrupted_uninstall_can_resume_after_unit_removal(self):
        self.install()
        with patch.object(native, 'run_systemctl', side_effect=lambda *args: (_ for _ in ()).throw(OSError('interrupted reload')) if args == ('daemon-reload',) else None):
            with self.assertRaises(OSError): native.uninstall(self.args, self.layout)
        self.assertFalse(self.layout.unit.exists())
        native.uninstall(self.args, self.layout)
        self.assertFalse(self.layout.app.exists())
        self.assertFalse(native.strict_json((self.layout.config / 'install.json').read_text())['installed'])

    def test_failed_initial_install_recovery_enables_autostart(self):
        self.health.side_effect = ValueError('startup failed')
        with self.assertRaises(ValueError): self.install()
        self.health.side_effect = None
        self.systemctl.reset_mock()
        self.next_package()
        native.update(self.args, self.layout)
        self.systemctl.assert_any_call('enable', '--now', native.SERVICE)

    def test_later_rollback_restores_self_contained_code_and_private_data(self):
        self.install()
        self.changed_user_state()
        before = self.protected_snapshot()
        old = self.layout.current.resolve()
        self.next_package()
        native.update(self.args, self.layout)
        saved = next(self.layout.backups.iterdir())
        import shutil
        shutil.rmtree(old)
        (self.layout.state / 'registry.json').write_text('{"schema_version":1,"bridges":[],"later":"change"}')
        self.args.backup = saved
        native.rollback(self.args, self.layout)
        for name, value in before.items():
            self.assertEqual(self.protected_snapshot()[name], value)
        self.assertEqual((self.layout.current.resolve() / 'src/app.py').read_bytes(), (ROOT / 'src/app.py').read_bytes())
        self.assertEqual(len(list(self.layout.backups.iterdir())), 2)

    def test_corrupt_manual_rollback_rejected_before_service_stop(self):
        self.install()
        self.next_package()
        native.update(self.args, self.layout)
        self.args.backup = next(self.layout.backups.iterdir())
        (self.args.backup / 'state/admin_auth.json').write_text('corrupted')
        self.systemctl.reset_mock()
        with self.assertRaisesRegex(ValueError, 'checksum'): native.rollback(self.args, self.layout)
        self.systemctl.assert_not_called()

    def test_failed_manual_rollback_recovers_current_installation(self):
        self.install()
        self.next_package()
        native.update(self.args, self.layout)
        self.args.backup = next(self.layout.backups.iterdir())
        before = self.protected_snapshot()
        calls = []
        def fail_once(layout):
            calls.append(True)
            if len(calls) == 1: raise ValueError('restored application failed')
        self.health.side_effect = fail_once
        with self.assertRaisesRegex(ValueError, 'original installation restored'):
            native.rollback(self.args, self.layout)
        self.assertEqual(before, self.protected_snapshot())

    def test_reinstall_with_umask_077_keeps_code_accessible_and_private_state_protected(self):
        import os
        self.install()
        before = self.protected_snapshot()
        native.uninstall(self.args, self.layout)
        self.args.keep_data = True
        previous_umask = os.umask(0o077)
        try:
            self.install()
        finally:
            os.umask(previous_umask)
        active = self.layout.current.resolve()
        for directory in (self.layout.app, self.layout.app / 'releases', active, active / 'src'):
            self.assertEqual(directory.stat().st_mode & 0o777, 0o755, str(directory))
        for name, value in before.items():
            if not name.endswith('/install.json'):
                self.assertEqual(self.protected_snapshot()[name], value)
        self.assertEqual(self.layout.state.stat().st_mode & 0o777, 0o700)
        self.assertEqual(self.layout.config.stat().st_mode & 0o777, 0o750)

    def test_reinstall_failure_before_record_keeps_data_and_allows_retry(self):
        self.install()
        self.changed_user_state()
        native.uninstall(self.args, self.layout)
        before = self.protected_snapshot()
        self.args.keep_data = True
        with patch.object(native, 'install_unit', side_effect=OSError('write failure')):
            with self.assertRaises(OSError): self.install()
        self.assertEqual(before, self.protected_snapshot())
        self.assertFalse(self.layout.app.exists())
        self.install()
        self.assertTrue(self.layout.unit.is_file())

    def test_manual_rollback_recovers_after_private_directory_removal_error(self):
        self.install()
        self.next_package()
        native.update(self.args, self.layout)
        self.args.backup = next(self.layout.backups.iterdir())
        before = self.protected_snapshot()
        remove = native.shutil.rmtree
        failed = []
        def fail_once(path, *args, **kwargs):
            result = remove(path, *args, **kwargs)
            if Path(path) == self.layout.state and not failed:
                failed.append(True)
                raise OSError('interrupted after state removal')
            return result
        with patch.object(native.shutil, 'rmtree', side_effect=fail_once):
            with self.assertRaisesRegex(ValueError, 'original installation restored'):
                native.rollback(self.args, self.layout)
        self.assertEqual(before, self.protected_snapshot())


class SystemdFailureResetTests(unittest.TestCase):
    def test_unloaded_or_healthy_unit_needs_no_reset(self):
        import subprocess
        for code in (1, 3, 4):
            with self.subTest(code=code), patch.object(native.subprocess, 'run', return_value=subprocess.CompletedProcess([], code)), patch.object(native, 'run_systemctl') as systemctl:
                native.reset_failure()
                systemctl.assert_not_called()

    def test_failed_unit_is_reset_before_start(self):
        import subprocess
        with patch.object(native.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0)), patch.object(native, 'run_systemctl') as systemctl:
            native.reset_failure()
            systemctl.assert_called_once_with('reset-failed', native.SERVICE)

    def test_systemctl_query_error_is_not_silenced(self):
        import subprocess
        with patch.object(native.subprocess, 'run', return_value=subprocess.CompletedProcess([], 2)):
            with self.assertRaises(subprocess.CalledProcessError): native.reset_failure()


class NativeTargetTests(unittest.TestCase):
    def test_explicit_linux_test_targets(self):
        for distro, version, options, label in [
            ('debian', '12', {}, 'Debian 12'), ('debian', '13', {}, 'Debian 13'),
            ('ubuntu', '24.04', {}, 'Ubuntu 24.04'), ('ubuntu', '26.04', {}, 'Ubuntu 26.04'),
            ('debian', '13', {'dietpi': True}, 'DietPi'),
            ('dietpi', '10.7', {'debian_version': '12.12'}, 'DietPi')]:
            with self.subTest(distro=distro, version=version):
                self.assertIn(label, native.native_os_target({'ID': distro, 'VERSION_ID': version}, 'x86_64', 64, **options))

    def test_unknown_old_and_non_amd64_systems_are_not_silently_allowed(self):
        for release, machine, bits, options in [
            ({'ID': 'ubuntu', 'VERSION_ID': '22.04'}, 'x86_64', 64, {}),
            ({'ID': 'ubuntu', 'VERSION_ID': '24.10'}, 'x86_64', 64, {}),
            ({'ID': 'debian', 'VERSION_ID': '11'}, 'x86_64', 64, {}),
            ({'ID': 'linuxmint', 'ID_LIKE': 'ubuntu', 'VERSION_ID': '24.04'}, 'x86_64', 64, {}),
            ({'ID': 'dietpi', 'VERSION_ID': '10'}, 'x86_64', 64, {}),
            ({'ID': 'debian', 'VERSION_ID': '13'}, 'aarch64', 64, {}),
            ({'ID': 'debian', 'VERSION_ID': '13'}, 'x86_64', 32, {}),
            ({'ID': 'debian', 'VERSION_ID': '13'}, 'x86_64', 64, {'raspberry': True})]:
            with self.subTest(release=release, machine=machine, bits=bits):
                with self.assertRaises(ValueError): native.native_os_target(release, machine, bits, **options)
