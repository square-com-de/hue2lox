import os
import unittest
from unittest.mock import patch
from tests import test_control
from color import kelvin_mirek,loxone_lumitech
from hue_client import state_payload,write_state


class WhiteTests(unittest.TestCase):
    def test_kelvin_reference_points(self):
        for k,m in [(2000,500),(2700,370),(4000,250),(6500,154)]:
            self.assertEqual(kelvin_mirek(k),m)
    def test_temperature_payload_preserves_brightness(self):
        self.assertEqual(state_payload({'kelvin':2700}),{'on':{'on':True},'color_temperature':{'mirek':370}})
        p=state_payload({'kelvin':6500,'brightness':30})
        self.assertEqual(p['color_temperature'],{'mirek':154});self.assertEqual(p['dimming'],{'brightness':30})
        self.assertNotIn('color',p)
    def test_lumitech_white_decode_and_off(self):
        self.assertEqual(loxone_lumitech(201002700),{'kelvin':2700,'brightness':100})
        self.assertEqual(loxone_lumitech(200306500),{'kelvin':6500,'brightness':30})
        self.assertEqual(state_payload({'loxone_lumitech':200002700}),{'on':{'on':False}})
        p=state_payload({'loxone_lumitech':200306500})
        self.assertEqual(p['color_temperature']['mirek'],154);self.assertEqual(p['dimming']['brightness'],30)
    def test_lumitech_rgb_matches_existing_tested_rgb(self):
        for v in (0,1,100,100000,100000000,50050050,100100100):
            self.assertEqual(state_payload({'loxone_lumitech':v}),state_payload({'loxone_rgb':v}))
    def test_invalid_never_contacts_bridge(self):
        bad=[{'kelvin':0},{'kelvin':999},{'kelvin':20001},{'kelvin':True},{'kelvin':'2700'},
             {'kelvin':float('nan')},{'kelvin':2700,'on':False},{'kelvin':2700,'rgb':{'r':255,'g':0,'b':0}},
             {'loxone_lumitech':True},{'loxone_lumitech':200000999},{'loxone_lumitech':201012700},
             {'loxone_lumitech':200302700.5},{'loxone_lumitech':float('inf')},{'loxone_lumitech':200302700,'on':True}]
        with patch('hue_client.request_light') as request:
            for value in bad:
                with self.subTest(value=value),self.assertRaises(ValueError):write_state(value)
            request.assert_not_called()


class WhiteEndpointTests(unittest.TestCase):
    setUp=test_control.ControlEndpointTests.setUp
    tearDown=test_control.ControlEndpointTests.tearDown
    request=test_control.ControlEndpointTests.request
    def test_white_gate_and_mock_request(self):
        os.environ['HUE_WRITES_ENABLED']='1'
        with patch.dict(os.environ,{'HUE_WHITE_ENABLED':'0','HUE_COLOR_ENABLED':'1'}),patch('app.write_state') as write:
            self.assertEqual(self.request('{"kelvin":2700}',self.token)[0],403)
            self.assertEqual(self.request('{"loxone_lumitech":200302700}',self.token)[0],403)
            write.assert_not_called()
        with patch.dict(os.environ,{'HUE_WHITE_ENABLED':'1','HUE_COLOR_ENABLED':'1'}),patch('app.write_state',return_value={'status':'accepted'}) as write:
            self.assertEqual(self.request('{"loxone_lumitech":200302700}',self.token)[0],200)
            write.assert_called_once_with({'loxone_lumitech':200302700})
    def test_rgb_cannot_bypass_color_gate_through_lumitech(self):
        os.environ['HUE_WRITES_ENABLED']='1'
        with patch.dict(os.environ,{'HUE_WHITE_ENABLED':'1','HUE_COLOR_ENABLED':'0'}),patch('app.write_state') as write:
            self.assertEqual(self.request('{"loxone_lumitech":100}',self.token)[0],403)
            write.assert_not_called()
