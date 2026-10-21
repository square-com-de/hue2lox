"""Original icon metadata mapping and shipped asset regression checks."""
from pathlib import Path
import subprocess
import unittest
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parent.parent
class IconTests(unittest.TestCase):
    def test_mapping_and_untrusted_metadata(self):
        script=(ROOT/'web/lamp-icons.js').read_text()+'''
const assert=require('node:assert/strict');
for(const [light,expected] of [
 [{model:'1746430P7',archetype:'wall_lantern'},'resonate'],[{model:'929003553001',archetype:'wall_lantern'},'resonate'],[{model:'LTO001',archetype:'vintage_bulb'},'filament'],[{model:'LTO001',icon_override:'table'},'table'],[{model:'LLC020'},'portable'],[{archetype:'hue_go'},'portable'],
 [{archetype:'classic_bulb'},'bulb'],[{archetype:'ceiling_round'},'ceiling'],
 [{archetype:'wall_lantern'},'lantern-wall'],[{archetype:'hue_lightstrip'},'strip'],
 [{icon_override:'candle',model:'LLC020'},'candle'],[{icon:'go'},'portable'],
 [{icon:'not-known',archetype:'table_shade'},'table'],
 [{archetype:'plug'},'generic'],[{},'bulb'],
 [{icon:'constructor',model:'__proto__',archetype:'toString'},'bulb'],
 [{icon:'<img onerror=alert(1)>'},'bulb'],[{model:'LCW004'},'wall'],[{model:'LCF001'},'bollard'],[{model:'LCS001'},'garden-spot'],[{model:'LCT024'},'play-bar'],[{model:'LLC006'},'iris'],[{model:'LLC011'},'bloom'],[{model:'LCL003'},'bulb'],[{model:'LCF001',icon_override:'wall'},'wall'],[{model:'LCW004',icon_override:'table'},'table'],[{model:'LCW004',icon_override:'auto'},'wall']]) {
 assert.equal(lampIconKey(light),expected);
 assert.equal(typeof LAMP_ICONS[lampIconKey(light)],'string');
}
assert.equal(Object.keys(LAMP_ICONS).length,22);
'''
        subprocess.run(['node','-e',script],check=True)
    def test_original_sources_and_removed_bundle(self):
        sources=list((ROOT/'web/lamp-icons').glob('*.svg'))
        self.assertEqual(len(sources),22)
        for path in sources:
            root=ET.parse(path).getroot()
            self.assertEqual(root.attrib['viewBox'],'0 0 64 64')
            for element in root.iter():
                self.assertIn(element.tag.split('}')[-1],('svg','path','ellipse','circle','rect'))
        for name in ('hue-icons.js','hue-icons-license.txt'):
            self.assertFalse((ROOT/'web'/name).exists())
            self.assertNotIn('/assets/'+name,(ROOT/'web/index.html').read_text())
            self.assertNotIn('/assets/'+name,(ROOT/'src/app.py').read_text())
