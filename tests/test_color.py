import math
import os
import unittest
from unittest.mock import patch
from color import GAMUT, clip_xy, rgb_xy, loxone_rgb
from hue_client import state_payload, write_state, read_status
from tests import test_control


class ColorMathTests(unittest.TestCase):
    def test_black_is_off_and_no_division_by_zero(self):
        self.assertIsNone(rgb_xy({'r':0,'g':0,'b':0}))
        self.assertEqual(state_payload({'rgb':{'r':0,'g':0,'b':0}}),{'on':{'on':False}})
        self.assertEqual(state_payload({'loxone_rgb':0}),{'on':{'on':False}})
    def test_primary_colors_and_gamut_projection(self):
        for rgb,vertex in [({'r':255,'g':0,'b':0},GAMUT[0]),({'r':0,'g':255,'b':0},GAMUT[1]),({'r':0,'g':0,'b':255},GAMUT[2])]:
            x,y=rgb_xy(rgb)
            self.assertAlmostEqual(x,vertex[0],places=3)
            self.assertAlmostEqual(y,vertex[1],places=3)
        self.assertEqual(clip_xy(GAMUT[0]),GAMUT[0])
        x,y=clip_xy((1,0));self.assertTrue(0<=x<=1 and 0<=y<=1)
        for r in (0,10,128,255):
            for g in (0,10,128,255):
                for b in (0,10,128,255):
                    xy=rgb_xy(dict(r=r,g=g,b=b))
                    if xy is not None:
                        self.assertEqual(clip_xy(xy),xy)
    def test_gamma_corrected_mixed_color_reference(self):
        # Independently calculated reference for r=128,g=64,b=32.
        x,y=rgb_xy(dict(r=128,g=64,b=32))
        self.assertAlmostEqual(x,0.5737,places=3)
        self.assertAlmostEqual(y,0.3592,places=3)
    def test_classic_loxone_channel_order_and_brightness(self):
        self.assertEqual(loxone_rgb(50),{'rgb':{'r':255.0,'g':0.0,'b':0.0},'brightness':50})
        for packed,channel in [(100,'r'),(100000,'g'),(100000000,'b')]:
            value=loxone_rgb(packed)
            self.assertEqual(value['rgb'][channel],255)
            self.assertEqual(value['brightness'],100)
        p=state_payload({'loxone_rgb':50050050})
        self.assertEqual(p['dimming']['brightness'],50)
        self.assertTrue('color' in p)
    def test_invalid_colors_never_contact_bridge(self):
        bad=[{'rgb':[]},{'rgb':{'r':0,'g':0}}, {'rgb':{'r':True,'g':0,'b':0}},
             {'rgb':{'r':float('nan'),'g':0,'b':0}}, {'rgb':{'r':256,'g':0,'b':0}},
             {'rgb':{'r':255,'g':0,'b':0},'on':False},
             {'rgb':{'r':0,'g':0,'b':0},'brightness':False},
             {'loxone_rgb':True},{'loxone_rgb':101},{'loxone_rgb':1.5},
             {'loxone_rgb':float('inf')},{'loxone_rgb':100100101},
             {'loxone_rgb':100,'brightness':50}]
        with patch('hue_client.request_light') as request:
            for state in bad:
                with self.subTest(state=state),self.assertRaises(ValueError):write_state(state)
            request.assert_not_called()
    def test_payload_preserves_brightness_when_unspecified(self):
        p=state_payload({'rgb':{'r':255,'g':0,'b':0}})
        self.assertNotIn('dimming',p)
        self.assertTrue(p['on']['on'])
        p=state_payload({'rgb':{'r':255,'g':0,'b':0},'brightness':35})
        self.assertEqual(p['dimming']['brightness'],35)
    def test_color_status_is_raw_not_invented_rgb(self):
        light={'id':'lamp','type':'light','metadata':{'name':'Hue Go'},'on':{'on':True},'dimming':{'brightness':47.04},'color':{'xy':{'x':0.4,'y':0.3}},'color_temperature':{'mirek':250,'mirek_valid':False}}
        with patch('hue_client.request_light',return_value=('lamp',light)):
            value=read_status();self.assertEqual(value['xy'],{'x':0.4,'y':0.3});self.assertFalse(value['color_temperature']['mirek_valid'])


class ColorEndpointTests(unittest.TestCase):
    setUp = test_control.ControlEndpointTests.setUp
    tearDown = test_control.ControlEndpointTests.tearDown
    request = test_control.ControlEndpointTests.request
    def test_color_gate_is_independent_of_on_off_gate(self):
        os.environ['HUE_WRITES_ENABLED']='1'
        with patch.dict(os.environ,{'HUE_COLOR_ENABLED':'0'}),patch('app.write_state') as write:
            self.assertEqual(self.request('{"rgb":{"r":255,"g":0,"b":0}}',self.token)[0],403)
            self.assertEqual(self.request('{"loxone_rgb":100}',self.token)[0],403)
            write.assert_not_called()
        with patch.dict(os.environ,{'HUE_COLOR_ENABLED':'1'}),patch('app.write_state',return_value={'status':'accepted'}) as write:
            self.assertEqual(self.request('{"rgb":{"r":255,"g":0,"b":0}}',self.token)[0],200)
            write.assert_called_once()
