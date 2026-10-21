"""Saved Hue scenes: read-only inventory and explicit static recall only."""
import re
from bridge_store import read_registry
from hue_client import request_document

REFERENCE = re.compile(r'[A-Za-z0-9_-]{1,128}')


def collect(resources):
    if type(resources) is not list or any(type(resource) is not dict for resource in resources):
        raise ValueError('invalid scene resources')
    groups = {}
    for resource in resources:
        if resource.get('type') in ('room','zone'):
            if not isinstance(resource.get('id'),str) or type(resource.get('metadata',{})) is not dict:
                raise ValueError('invalid scene group')
            groups[resource.get('id')] = str(resource.get('metadata',{}).get('name',''))[:256]
    result, seen = [], set()
    for resource in resources:
        if resource.get('type') != 'scene':
            continue
        reference = resource.get('id')
        group, metadata, actions = resource.get('group',{}), resource.get('metadata',{}), resource.get('actions',[])
        if (not isinstance(reference,str) or not REFERENCE.fullmatch(reference) or reference in seen or
                type(group) is not dict or type(metadata) is not dict or type(actions) is not list):
            raise ValueError('invalid scene inventory')
        if not isinstance(group.get('rid'),str) or not REFERENCE.fullmatch(group['rid']) or group.get('rtype') not in ('room','zone'):
            raise ValueError('invalid scene group')
        members = set()
        for action in actions:
            if type(action) is not dict or type(action.get('target')) is not dict:
                raise ValueError('invalid scene target')
            target = action['target']
            if target.get('rtype') == 'light':
                light = target.get('rid')
                if not isinstance(light,str) or not REFERENCE.fullmatch(light):
                    raise ValueError('invalid scene light')
                members.add(light)
        seen.add(reference)
        result.append({'id':reference,'name':str(metadata.get('name',reference))[:256],
                       'room':groups.get(group.get('rid'),''),'group_type':group.get('rtype',''),
                       'light_ids':sorted(members),'present':True})
    if len(result)>2000:
        raise ValueError('too many scenes')
    return sorted(result,key=lambda scene:(scene['room'].casefold(),scene['name'].casefold(),scene['id']))


def available_scenes():
    result=[]
    for bridge in read_registry()['bridges']:
        hidden={light['id'] for light in bridge.get('lights',[]) if light.get('ignored') or light.get('removed')}
        for scene in bridge.get('scenes',[]):
            if scene.get('removed') or scene.get('present') is False:
                continue
            reference=scene.get('id')
            if not isinstance(reference,str) or not REFERENCE.fullmatch(reference):
                continue
            key=bridge['id']+'/'+reference
            result.append({'key':key,'name':scene['name'],'bridge':bridge['name'],'bridge_id':bridge['id'],
                           'room':scene.get('room',''),'path':'/api/scenes/'+key+'/recall',
                           'ignored':bool(scene.get('ignored')),
                           'available':bridge.get('enabled') is True and not scene.get('ignored'),
                           'light_count':len(scene.get('light_ids',[])),
                           'hidden_light_count':len(hidden.intersection(scene.get('light_ids',[]))),
                           'commands':[{'id':'recall','name':'Szene aktivieren','body_on':'{"recall":true}',
                                        'body_off':'','analog':False}]})
    return result


def resolve_path(path):
    match=re.fullmatch(r'/api/scenes/([A-Za-z0-9_-]+)/([A-Za-z0-9_-]+)/recall',path)
    if not match:
        return None
    for bridge in read_registry()['bridges']:
        if bridge['id']==match[1] and bridge.get('enabled') is True:
            for scene in bridge.get('scenes',[]):
                if scene['id']==match[2] and scene.get('present') is not False and not scene.get('ignored') and not scene.get('removed'):
                    return bridge,scene
    return None


def recall(bridge, scene):
    document=request_document('PUT','/clip/v2/resource/scene/'+scene['id'],
                              payload={'recall':{'action':'active'}},bridge=bridge)
    if (type(document) is not dict or document.get('errors') != [] or
            type(document.get('data')) is not list or len(document['data']) != 1 or not any(
                type(item) is dict and item.get('rid')==scene['id'] and item.get('rtype')=='scene'
                for item in document['data'])):
        raise ValueError('scene recall rejected')
    # The bridge accepted the command; no claim about an observed lamp state.
    return {'status':'ok','scene_id':scene['id'],'accepted':True,'tls_verified':True}
