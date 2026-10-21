"""Device-specific conversion, inventory persistence and legacy upgrade paths."""
import unittest
from unittest.mock import patch

import bridge_admin
import hue_client
from color import GAMUT, gamut_for, light_parameters, kelvin_mirek, rgb_xy
from hue_client import state_payload, write_state


def resource(reference='lamp', red=.64, minimum=200, maximum=400):
    return {'id':reference, 'type':'light',
            'color':{'gamut':{'red':{'x':red,'y':.33},'green':{'x':.30,'y':.60},'blue':{'x':.15,'y':.06}}},
            'color_temperature':{'mirek_schema':{'mirek_minimum':minimum,'mirek_maximum':maximum}}}


class DeviceColorTests(unittest.TestCase):
    def setUp(self):
        hue_client._PARAMETER_CACHE.clear()

    def test_red_uses_target_triangle(self):
        a, b = resource(red=.64), resource(red=.60)
        first = rgb_xy(dict(r=255,g=0,b=0), a)
        second = rgb_xy(dict(r=255,g=0,b=0), b)
        self.assertAlmostEqual(first[0], .64)
        self.assertAlmostEqual(second[0], .60)
        self.assertNotEqual(first, second)
        for field in ('loxone_rgb','loxone_lumitech'):
            payload = state_payload({field:50}, b)
            self.assertAlmostEqual(payload['color']['xy']['x'], .60)
            self.assertEqual(payload['dimming']['brightness'], 50)

    def test_temperature_clamps_without_stretching(self):
        lamp = resource()
        self.assertEqual(kelvin_mirek(2000, lamp),400)
        self.assertEqual(kelvin_mirek(6500, lamp),200)
        self.assertEqual(kelvin_mirek(4000, lamp),250)
        self.assertEqual(kelvin_mirek(1500, resource(maximum=666)),666)
        self.assertEqual(kelvin_mirek(8000, resource(minimum=125)),125)
        payload = state_payload({'loxone_lumitech':200306500}, lamp)
        self.assertEqual(payload['color_temperature']['mirek'],200)
        self.assertEqual(payload['dimming']['brightness'],30)
        self.assertEqual(state_payload({'loxone_lumitech':200006500},lamp),{'on':{'on':False}})

    def test_missing_or_malformed_parameters_have_defined_fallback(self):
        bad = [None, [], {'red':None}, resource()['color']['gamut']]
        bad[-1]['red']['x']=float('nan')
        for gamut in bad:
            self.assertEqual(gamut_for({'color':{'gamut':gamut}}),GAMUT)
        degenerate = {'color':{'gamut':{name:{'x':.3,'y':.3} for name in ('red','green','blue')}}}
        self.assertEqual(gamut_for(degenerate),GAMUT)
        self.assertEqual(kelvin_mirek(2000, {'color_temperature':{'mirek_schema':{'mirek_minimum':500,'mirek_maximum':200}}}),500)
        self.assertEqual(light_parameters({'token':'must-not-retain','color':None}),{})

    def test_inventory_saves_only_valid_conversion_parameters(self):
        item=resource(); item['secret']='must-not-retain'
        saved=bridge_admin.collect_lights([item])[0]
        self.assertEqual(saved['color_parameters'],light_parameters(item))
        self.assertNotIn('secret',str(saved))
        self.assertEqual(bridge_admin.collect_lights([{'id':'plug','type':'light'}])[0]['color_parameters'],{})

    def test_write_uses_persisted_limits_without_extra_get(self):
        bridge={'host':'10.200.0.2','bridge_id':'fixture','lights':[
            {'id':'lamp','color_parameters':light_parameters(resource())}]}
        with patch('hue_client.request_light',return_value=('lamp',{'rid':'lamp','rtype':'light'})) as request:
            write_state({'kelvin':6500},bridge=bridge,light_id='lamp')
            self.assertEqual(request.call_count,1)
            self.assertEqual(request.call_args.args[0],'PUT')
            self.assertEqual(request.call_args.args[1]['color_temperature']['mirek'],200)

    def test_old_inventory_gets_parameters_and_caches_per_light(self):
        bridge={'host':'10.200.0.2','bridge_id':'fixture','lights':[]}
        calls=[]
        def request(method,payload=None,bridge=None,target_light=None):
            calls.append((method,target_light,payload))
            if method=='GET': return target_light,resource(target_light,minimum=200 if target_light=='a' else 250)
            return target_light,{'rid':target_light,'rtype':'light'}
        with patch('hue_client.request_light',side_effect=request):
            for light in ('a','a','b'):
                write_state({'kelvin':6500},bridge=bridge,light_id=light)
        self.assertEqual([c[0] for c in calls],['GET','PUT','PUT','GET','PUT'])
        self.assertEqual(calls[1][2]['color_temperature']['mirek'],200)
        self.assertEqual(calls[-1][2]['color_temperature']['mirek'],250)

    def test_failed_metadata_read_never_sends_write(self):
        with patch('hue_client.request_light',side_effect=OSError('unavailable')) as request:
            with self.assertRaises(OSError):
                write_state({'kelvin':4000},bridge={'host':'10.200.0.2'},light_id='lamp')
            self.assertEqual(request.call_count,1)
            self.assertEqual(request.call_args.args[0],'GET')

    def test_switch_off_does_not_need_parameters(self):
        with patch('hue_client.parameters_for') as parameters, patch('hue_client.request_light',return_value=('lamp',{'rid':'lamp','rtype':'light'})):
            write_state({'loxone_rgb':0},bridge={'host':'10.200.0.2'},light_id='lamp')
            parameters.assert_not_called()


if __name__=='__main__': unittest.main()
