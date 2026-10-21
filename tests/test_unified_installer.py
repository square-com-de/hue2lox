"""Common installer routing: no package managers, services or hardware are used."""
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'install-assistant.sh'


def shell(code, answer='', language='de'):
    return subprocess.run(['bash', '-c', 'source "$1"; HUE2LOX_INSTALL_LANG=$2; ' + code,
                           'installer-test', str(SCRIPT), language], input=answer,
                          text=True, capture_output=True, timeout=10)


class UnifiedInstallerTests(unittest.TestCase):
    def test_deployment_choice_in_both_languages_rejects_invalid_input_and_eof(self):
        for language in ('de', 'en'):
            for choice, backend in [('1', 'docker'), ('2', 'native')]:
                result = shell('choose_deployment; printf "BACKEND:%s" "$DEPLOYMENT"', 'invalid\n' + choice + '\n', language)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn('BACKEND:' + backend, result.stdout)
                self.assertIn('Docker', result.stdout)
                self.assertIn('experiment', result.stdout.lower())
        self.assertNotEqual(shell('choose_deployment', '').returncode, 0)

    def test_check_mode_routes_without_a_terminal_or_mutations(self):
        result = shell('native_status(){ echo NATIVE_READ_ONLY; }; docker(){ echo BAD_DOCKER; }; main --deployment native --check')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('NATIVE_READ_ONLY', result.stdout)
        self.assertNotIn('BAD_DOCKER', result.stdout)

    def test_interactive_main_selects_backend_and_exits_without_installing(self):
        import os
        import pty
        import select
        import time
        for language, choice, label in [('1', '2', 'NATIV'), ('2', '1', 'Docker')]:
            with self.subTest(language=language, backend=choice):
                master, slave = pty.openpty()
                process = subprocess.Popen(['bash', str(SCRIPT)], stdin=slave, stdout=slave,
                                           stderr=slave, env={**os.environ, 'TERM': 'dumb', 'NO_COLOR': '1'})
                os.close(slave)
                output = b''
                try:
                    os.write(master, (language + '\n' + choice + '\n0\n').encode())
                    deadline = time.monotonic() + 8
                    while time.monotonic() < deadline:
                        if select.select([master], [], [], .1)[0]:
                            try:
                                chunk = os.read(master, 65536)
                            except OSError:
                                break
                            if not chunk: break
                            output += chunk
                        elif process.poll() is not None:
                            break
                    self.assertEqual(process.wait(timeout=2), 0, output.decode(errors='replace'))
                    self.assertIn(label, output.decode())
                finally:
                    if process.poll() is None: process.kill(); process.wait()
                    os.close(master)

    def test_native_install_uses_native_adapter_and_retains_quoted_paths(self):
        result = shell('''DEPLOYMENT=native
native_prerequisites(){ return 0; }
native_require_package(){ NATIVE_PACKAGE='/tmp/reviewed package.tar.gz'; NATIVE_SHA256=expected; }
choose_server_ip(){ SELECTED_IP=127.0.0.1; }
confirm(){ return 0; }
run(){ printf '<%s>\\n' "$@"; }
docker(){ echo BAD_DOCKER; return 99; }
prepare_setup''', '18443\n')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('<install>', result.stdout)
        self.assertIn('</tmp/reviewed package.tar.gz>', result.stdout)
        self.assertIn('<127.0.0.1>', result.stdout)
        self.assertNotIn('BAD_DOCKER', result.stdout)

    def test_declined_native_install_never_runs_lifecycle(self):
        result = shell('''DEPLOYMENT=native
native_prerequisites(){ return 0; }
native_require_package(){ NATIVE_PACKAGE=/tmp/test; NATIVE_SHA256=expected; }
choose_server_ip(){ SELECTED_IP=127.0.0.1; }
confirm(){ return 1; }
run(){ echo BAD_MUTATION; }
prepare_setup''', '18443\n')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn('BAD_MUTATION', result.stdout)

    def test_native_base_packages_fail_before_apt_on_unsupported_platform(self):
        result = shell('DEPLOYMENT=native; root_required(){ return 0; }; native_package_platform(){ return 1; }; run(){ echo BAD_APT; }; base_packages')
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn('BAD_APT', result.stdout)

    def test_native_maintenance_routes_update_rollback_and_preserving_uninstall(self):
        for choice, expected, extra in [('1', '<update>', ''), ('3', '<rollback>', '/var/backups/hue2lox/test\n'), ('4', '<uninstall>', '')]:
            result = shell('''DEPLOYMENT=native
native_prerequisites(){ return 0; }
native_require_package(){ NATIVE_PACKAGE=/tmp/test; NATIVE_SHA256=expected; }
confirm(){ return 0; }
run(){ printf '<%s>\\n' "$@"; }
native_maintenance''', choice + '\n' + extra, 'en')
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn(expected, result.stdout)
            self.assertNotIn('--purge-data', result.stdout)
            self.assertNotIn('\\n2', result.stdout)  # menu has real newlines

    def test_cli_rejects_unpaired_native_package_parameters(self):
        self.assertNotEqual(shell('main --check --native-package /tmp/archive').returncode, 0)
        self.assertNotEqual(shell('main --check --deployment unknown').returncode, 0)

    def test_native_package_preparation_decline_does_not_create_artifacts(self):
        result = shell('native_prerequisites(){ return 0; }; confirm(){ return 1; }; run(){ echo BAD_BUILD; }; native_require_package')
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn('BAD_BUILD', result.stdout)
