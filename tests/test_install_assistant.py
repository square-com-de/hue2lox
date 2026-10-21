"""Installer decisions must not mutate a host when skipped or invalid."""
from pathlib import Path
import subprocess
import tempfile
import unittest

SCRIPT=Path(__file__).resolve().parent.parent/'install-assistant.sh'
class AssistantTests(unittest.TestCase):
    def shell(self, code):
        return subprocess.run(['bash','-c','source "$1"; '+code,'test',str(SCRIPT)],capture_output=True,text=True)
    def test_declining_packages_never_runs_package_manager(self):
        result=self.shell('root_required(){ return 0; }; package_platform(){ return 0; }; confirm(){ return 1; }; run(){ echo UNEXPECTED_MUTATION; return 99; }; base_packages')
        self.assertEqual(result.returncode,0)
        self.assertNotIn('UNEXPECTED_MUTATION',result.stdout)
    def test_apt_failure_stops_before_install(self):
        result=self.shell('root_required(){ return 0; }; package_platform(){ return 0; }; confirm(){ return 0; }; run(){ echo "$*"; return 42; }; base_packages')
        self.assertEqual(result.returncode,42)
        self.assertEqual(result.stdout.strip(),'apt-get update')
    def test_package_index_errors_fail_in_verbose_mode_too(self):
        result=self.shell('HUE2LOX_INSTALL_COMPACT=0; apt-get(){ printf "%s\\n" "$*"; return 42; }; run apt-get update')
        self.assertEqual(result.returncode, 42)
        self.assertIn('APT::Update::Error-Mode=any', result.stdout)

    def test_ready_docker_is_not_reinstalled(self):
        result=self.shell('root_required(){ return 0; }; docker(){ return 0; }; confirm(){ echo UNEXPECTED_CONFIRM; return 99; }; docker_setup')
        self.assertEqual(result.returncode,0)
        self.assertIn('einsatzbereit',result.stdout)
        self.assertNotIn('UNEXPECTED',result.stdout)
    def test_existing_destination_is_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            marker=Path(directory)/'keep';marker.write_text('unchanged')
            result=subprocess.run(['bash','-c','source "$1"; DEST=$2; root_required(){ return 0; }; prepare_setup','test',str(SCRIPT),directory],capture_output=True,text=True)
            self.assertNotEqual(result.returncode,0)
            self.assertEqual(marker.read_text(),'unchanged')
            self.assertIn('existiert bereits',result.stdout)

    def test_confirmation_variants_and_empty_input(self):
        for language in ('de', 'en'):
            for answer in ('j', 'J', 'ja', 'JA', 'Ja', 'y', 'Y', 'yes', 'YES', 'Yes', 'n', 'N', 'nein', 'NEIN', 'no', 'NO', ''):
                with self.subTest(language=language, answer=answer):
                    result=subprocess.run(['bash','-c','source "$1"; HUE2LOX_INSTALL_LANG=$2; confirm Test','test',str(SCRIPT),language],input=answer+'\n',capture_output=True,text=True)
                    self.assertEqual(result.returncode, 0 if answer.lower() in ('','j','ja','y','yes') else 1)

    def test_invalid_confirmation_retries_and_eof_declines(self):
        for value, expected in [('maybe\ny\n',0),('maybe\nn\n',1),('',1)]:
            result=subprocess.run(['bash','-c','source "$1"; HUE2LOX_INSTALL_LANG=en; confirm Test','test',str(SCRIPT)],input=value,capture_output=True,text=True)
            self.assertEqual(result.returncode,expected)
            if value:
                self.assertIn('Please enter yes/y or no/n.',result.stdout)

    def test_language_selection_is_exported_to_child_process(self):
        for value, expected in [('1\n','de'),('2\n','en')]:
            result=subprocess.run(['bash','-c','source "$1"; choose_language; bash -c \'printf "%s" "$HUE2LOX_INSTALL_LANG"\'','test',str(SCRIPT)],input=value,capture_output=True,text=True)
            self.assertEqual(result.returncode,0)
            self.assertEqual(result.stdout,expected)

    def platform_fixture(self, distro, version, codename, arch, *, dietpi=False, raspberry=False, debian=''):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            (root/'etc').mkdir()
            (root/'etc/os-release').write_text(f'ID={distro}\nVERSION_ID="{version}"\nVERSION_CODENAME="{codename}"\n')
            (root/'etc/debian_version').write_text(debian+'\n')
            if dietpi:
                (root/'boot/dietpi').mkdir(parents=True)
                (root/'boot/dietpi/.version').write_text('G_DIETPI_VERSION_CORE=10\n')
            if raspberry:
                (root/'etc/rpi-issue').write_text('Raspberry Pi reference image\n')
            return subprocess.run(['bash','-c','source "$1"; fixture_arch=$3; dpkg(){ printf "%s" "$fixture_arch"; }; detect_package_platform "$2"; printf "%s\\n" "$PLATFORM_LABEL"; docker_source',
                                   'test',str(SCRIPT),directory,arch],capture_output=True,text=True)

    def test_distro_fixtures_select_correct_repository_and_architecture(self):
        cases=[('ubuntu','22.04','jammy','Ubuntu','ubuntu',{}),
               ('ubuntu','24.04','noble','Ubuntu','ubuntu',{}),
               ('ubuntu','26.04','resolute','Ubuntu','ubuntu',{}),
               ('debian','12','bookworm','Debian','debian',{}),
               ('debian','13','trixie','Debian','debian',{}),
               ('debian','12','bookworm','DietPi','debian',{'dietpi':True,'debian':'12.12'}),
               ('debian','13','trixie','DietPi','debian',{'dietpi':True,'debian':'13.1'}),
               ('dietpi','10.7','trixie','DietPi','debian',{'debian':'13.1'})]
        for distro,version,suite,label,family,options in cases:
            for arch in ('amd64','arm64'):
                with self.subTest(distro=distro,version=version,arch=arch,options=options):
                    result=self.platform_fixture(distro,version,suite,arch,**options)
                    self.assertEqual(result.returncode,0,result.stderr)
                    self.assertTrue(result.stdout.startswith(label+'\n'))
                    self.assertIn(f'URIs: https://download.docker.com/linux/{family}\n',result.stdout)
                    self.assertIn(f'Suites: {suite}\n',result.stdout)
                    self.assertIn(f'Architectures: {arch}\n',result.stdout)
        for distro in ('debian','raspbian'):
            for version,suite in [('12','bookworm'),('13','trixie')]:
                result=self.platform_fixture(distro,version,suite,'arm64',raspberry=True)
                self.assertEqual(result.returncode,0,result.stderr)
                self.assertIn('Raspberry Pi OS\n',result.stdout)
                self.assertIn('linux/debian\n',result.stdout)

    def test_unknown_releases_and_32_bit_userspace_rejected(self):
        for distro,version,suite,arch,options in [
            ('ubuntu','28.04','','amd64',{}),('debian','14','forky','amd64',{}),
            ('debian','13','bookworm','amd64',{}),('debian','','trixie','amd64',{}),
            ('linuxmint','22','noble','amd64',{}),('fedora','43','','amd64',{}),
            ('raspbian','12','bookworm','armhf',{'raspberry':True}),
            ('debian','13','trixie','armhf',{'dietpi':True}),
            ('dietpi','10.7','','arm64',{'debian':'testing'}),
            ('debian','11','bullseye','arm64',{'dietpi':True}),
            ('ubuntu','24.04','noble','i386',{})]:
            with self.subTest(distro=distro,version=version,arch=arch):
                result=self.platform_fixture(distro,version,suite,arch,**options)
                self.assertNotEqual(result.returncode,0)
                self.assertNotIn('URIs:',result.stdout)

    def test_unsupported_platform_stops_before_any_package_mutation(self):
        result=self.shell('root_required(){ return 0; }; detect_package_platform(){ return 1; }; run(){ echo UNEXPECTED_MUTATION; }; base_packages')
        self.assertNotEqual(result.returncode,0)
        self.assertNotIn('UNEXPECTED',result.stdout)

    def test_working_docker_skips_even_unsupported_distribution(self):
        result=self.shell('root_required(){ return 0; }; docker(){ return 0; }; package_platform(){ echo UNEXPECTED_PLATFORM_CHECK; return 1; }; run(){ echo UNEXPECTED_MUTATION; }; docker_setup')
        self.assertEqual(result.returncode,0)
        self.assertNotIn('UNEXPECTED',result.stdout)

    def test_broken_existing_docker_is_not_replaced(self):
        result=self.shell('root_required(){ return 0; }; docker(){ return 1; }; package_platform(){ echo UNEXPECTED_PLATFORM_CHECK; }; run(){ echo UNEXPECTED_MUTATION; }; docker_setup')
        self.assertNotEqual(result.returncode,0)
        self.assertNotIn('UNEXPECTED',result.stdout)

    def choose_ip(self, addresses, answer, language='de'):
        return subprocess.run(['bash','-c','source "$1"; fixture_addresses=$2; HUE2LOX_INSTALL_LANG=$3; hostname(){ printf "%s" "$fixture_addresses"; }; choose_server_ip; printf "SELECTED=%s\\n" "$SELECTED_IP"', 'test',str(SCRIPT),addresses,language],input=answer,capture_output=True,text=True)

    def test_ip_number_selection_filters_ipv6_and_duplicates(self):
        result=self.choose_ip('10.200.0.143 fdb8::1 10.200.0.143 10.0.0.8 127.0.0.1 169.254.2.3','2\n')
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn('1  10.200.0.143',result.stdout)
        self.assertIn('2  10.0.0.8',result.stdout)
        self.assertIn('SELECTED=10.0.0.8',result.stdout)
        self.assertNotIn('fdb8',result.stdout)
        self.assertNotIn('127.0.0.1',result.stdout)
        self.assertNotIn('3  ',result.stdout)

    def test_ip_choice_invalid_input_retries_without_default(self):
        result=self.choose_ip('10.200.0.143','\n99\n1+0\n1\n','en')
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(result.stdout.count('Please choose a listed number or q.'),3)
        self.assertIn('SELECTED=10.200.0.143',result.stdout)

    def test_ip_choice_manual_and_no_addresses(self):
        result=self.choose_ip('::1','0\n10.200.0.143\n','en')
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn('No IPv4 address found automatically.',result.stdout)
        self.assertIn('SELECTED=10.200.0.143',result.stdout)

    def test_ip_choice_cancel_and_eof(self):
        for answer in ('q\n',''):
            result=self.choose_ip('10.200.0.143',answer)
            self.assertNotEqual(result.returncode,0)
            self.assertNotIn('SELECTED=',result.stdout)
