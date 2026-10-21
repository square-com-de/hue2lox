"""Exercise the exact copyable commands, offline, using local tool fixtures."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def command(platform, language='en'):
    script = "global.window=global; global.document={getElementById:()=>null};\n"
    script += (ROOT / f'web/locales/{language}.js').read_text()
    script += f"\nfunction t(k){{return window.HUE2LOX_MESSAGES.{language}[k]??k;}}\n"
    script += (ROOT / 'web/discovery-help.js').read_text()
    script += '\nprocess.stdout.write(localDiscoveryCommand(' + json.dumps(platform) + '));'
    return subprocess.check_output(['node', '-e', script], text=True)


class DiscoveryHelpTests(unittest.TestCase):
    def test_generated_asset_current(self):
        before = (ROOT / 'web/discovery-help.js').read_bytes()
        subprocess.run(['python3', str(ROOT / 'tools/build_discovery_help.py')], check=True)
        self.assertEqual(before, (ROOT / 'web/discovery-help.js').read_bytes())

    def test_both_languages_complete_and_shell_valid(self):
        for lang in ('de', 'en'):
            for platform in ('macos', 'linux', 'windows'):
                code = command(platform, lang)
                self.assertNotIn('@@', code)
                self.assertNotIn('discovery.meethue.com', code)
                self.assertNotIn('https://', code)
                if platform != 'windows':
                    subprocess.run(['bash', '-n'], input=code, text=True, check=True)
                self.assertIn('Keine Bridges' if lang == 'de' else 'No bridges', code)

    def run_shell(self, platform, tool, fixture, lang='en'):
        with tempfile.TemporaryDirectory() as work:
            for name, body in [(tool, fixture), ('sleep', 'exit 0')]:
                path = Path(work) / name
                path.write_text('#!/bin/bash\n' + body + '\n')
                path.chmod(0o755)
            # capture uses background processes: wait for a fixture marker instead of a real delay.
            (Path(work) / 'sleep').write_text('#!/bin/bash\nfor i in {1..200}; do [ -e "$FIXTURE_READY" ] && { rm "$FIXTURE_READY"; exit 0; }; /bin/sleep 0.01; done\nexit 1\n')
            env = dict(os.environ, PATH=work + ':' + os.environ['PATH'], FIXTURE_READY=work + '/ready')
            return subprocess.run(['bash'], input=command(platform, lang), env=env, text=True,
                                  capture_output=True, timeout=10)

    def test_macos_resolves_all_and_deduplicates(self):
        fixture = '''case "$1" in
-B) printf '12 Add 3 11 local. _hue._tcp. Hue Bridge - A\n12 Add 3 11 local. _hue._tcp. Hue Bridge - A\n12 Add 2 11 local. _hue._tcp. Hue Bridge - B\n';;
-L) printf '%s can be reached at bridge.local.:443\n' "$2";;
-G) printf '12 Add 2 11 bridge.local. 192.168.2.10 120\n12 Add 2 11 bridge.local. 192.168.2.10 120\n';;
esac
touch "$FIXTURE_READY"'''
        result = self.run_shell('macos', 'dns-sd', fixture)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.count('192.168.2.10'), 2, result.stdout + result.stderr)
        self.assertEqual(result.stdout.count('Hue Bridge - A'), 1)
        self.assertIn('Hue Bridge - B', result.stdout)

    def test_linux_resolved_ipv4_only_and_escaped_name(self):
        fixture = r'''printf '%s\n' '=;eth0;IPv4;Hue\032Bridge\032-\032A;_hue._tcp;local;bridge.local;192.168.2.10;443;' '=;eth0;IPv4;Hue\032Bridge\032-\032A;_hue._tcp;local;bridge.local;192.168.2.10;443;' '=;eth0;IPv6;Hue;_hue._tcp;local;bridge.local;fe80::1;443;'
touch "$FIXTURE_READY"'''
        result = self.run_shell('linux', 'avahi-browse', fixture)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.count('192.168.2.10'), 1)
        self.assertIn('Hue Bridge - A', result.stdout)
        self.assertNotIn('fe80::1', result.stdout)

    def test_no_results_is_explained(self):
        for platform, tool in [('macos', 'dns-sd'), ('linux', 'avahi-browse')]:
            result = self.run_shell(platform, tool, 'touch "$FIXTURE_READY"', 'de')
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('Keine Bridges gefunden', result.stdout)

    def test_copy_secure_http_and_manual_fallback(self):
        js = """
let selected=false, removed=0, copied='', legacy=false;
const code={textContent:'whole command'}, status={textContent:''};
Object.defineProperty(global,'navigator',{value:{clipboard:{writeText:async text=>{copied=text;}}},configurable:true});
global.window={getSelection:()=>({removeAllRanges(){},addRange(){selected=true;}})};
global.document={getElementById:()=>null,body:{append(){}},
 createElement:()=>({style:{},setAttribute(){},select(){},remove(){removed++;}}),
 execCommand:()=>legacy,createRange:()=>({selectNodeContents(){}})};
function t(k){return k;}
""" + (ROOT / 'web/discovery-help.js').read_text() + """
(async()=>{
 await copyDiscoveryCommand(code,status);
 if(copied!=='whole command'||!status.textContent.startsWith('Kopiert'))throw Error('modern');
 navigator.clipboard=undefined;legacy=true;status.textContent='';
 await copyDiscoveryCommand(code,status);
 if(!status.textContent.startsWith('Kopiert')||removed!==1)throw Error('http fallback');
 legacy=false; await copyDiscoveryCommand(code,status);
 if(!selected||removed!==2||!status.textContent.includes('markiert'))throw Error('manual fallback');
})().catch(e=>{console.error(e);process.exitCode=1;});
"""
        subprocess.run(['node', '-e', js], check=True)
