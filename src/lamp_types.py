"""Detected lamp abilities and local installation choices; never controls lamps."""
from functools import lru_cache
import json
from pathlib import Path
import os

@lru_cache(maxsize=1)
def catalog():
    path=(Path(__file__).resolve().parent.parent/'catalog')/'hue-models.json'
    return json.loads(path.read_text())['models']

def details(light):
    caps=light.get('capabilities',[])
    model=light.get('model','')
    entry=next((row for row in catalog() if model in (row['model_id'],row['product_id'])),None)
    kind='RGB + Tunable White' if 'rgb' in caps and 'temperature' in caps else 'RGB' if 'rgb' in caps else 'Tunable White' if 'temperature' in caps else 'Dimmer' if 'brightness' in caps else 'Ein/Aus'
    return {'lamp_type':kind,'product_name':light.get('product_name') or (entry['name'] if entry else ''),'capabilities':caps,'capability_source':'Hue Bridge','catalog_match':bool(entry)}

def commands(light):
    caps=light.get('capabilities',[])
    items=[{'id':'switch','name':'Ein/Aus','body_on':'{"on":true}','body_off':'{"on":false}','analog':False}]
    if 'brightness' in caps:items.append({'id':'dim','name':'Dimmen','body_on':'{"brightness":<v>}','body_off':'','analog':True})
    if 'temperature' in caps and os.environ.get('HUE_WHITE_ENABLED')=='1':items.append({'id':'tw','name':'Tunable White','body_on':'{"loxone_lumitech":<v>}','body_off':'','analog':True})
    if 'rgb' in caps and os.environ.get('HUE_COLOR_ENABLED')=='1':items.append({'id':'rgb','name':'RGB','body_on':'{"loxone_rgb":<v>}','body_off':'','analog':True})
    if 'rgb' in caps and 'temperature' in caps and os.environ.get('HUE_WHITE_ENABLED')=='1' and os.environ.get('HUE_COLOR_ENABLED')=='1':items.append({'id':'lumitech','name':'Lumitech RGB + Weiß','body_on':'{"loxone_lumitech":<v>}','body_off':'','analog':True})
    return items

def recommended(items):
    return next(mode for mode in ('lumitech','rgb','tw','dim','switch') if any(c['id']==mode for c in items))

def chosen(light,items):
    allowed={c['id'] for c in items}
    modes=[mode for mode in light.get('enabled_modes',[]) if mode in allowed]
    return modes or [recommended(items)]

def save_modes(bridge_id,light_id,modes):
    from bridge_store import update_registry
    if type(modes) is not list or not modes or len(modes)>5 or any(type(mode) is not str for mode in modes) or len(set(modes))!=len(modes):raise ValueError('invalid modes')
    def change(doc):
        bridge=next((b for b in doc['bridges'] if b['id']==bridge_id),None)
        light=next((l for l in bridge.get('lights',[]) if l['id']==light_id),None) if bridge else None
        if not light or any(mode not in {c['id'] for c in commands(light)} for mode in modes):raise ValueError('unsupported mode')
        light['enabled_modes']=modes
    update_registry(change)


def save_icon(bridge_id, light_id, icon):
    """Persist a local visual preference only; never send a Hue command."""
    from bridge_store import update_registry
    choices={'resonate','filament','bollard','garden-spot','lantern-wall','lantern-post','flood','linear','iris','bloom','play-bar','auto','bulb','candle','spot','ceiling','pendant','floor','table','portable','strip','wall'}
    if type(icon) is not str or icon not in choices:
        raise ValueError('invalid icon')
    def change(document):
        bridge=next((b for b in document['bridges'] if b['id']==bridge_id),None)
        light=next((l for l in bridge.get('lights',[]) if l['id']==light_id and not l.get('removed')),None) if bridge else None
        if light is None:
            raise ValueError('unknown light')
        if icon=='auto':
            light.pop('icon_override',None)
        else:
            light['icon_override']=icon
    update_registry(change)
