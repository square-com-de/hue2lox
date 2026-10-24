"""Scene/group switches with exact-match defaults. Ownership is command history, never lamp feedback.

One lock orders accepted scene operations; no timers or background reactivation.
Unknown ownership (restart, reconfiguration, uncertain bridge result) rejects OFF.
"""
import hashlib
import json
import threading
from bridge_store import read_registry, update_registry, registry_path
from hue_client import request_document

class OrderedLock:
    """FIFO acquisition: queued final OFF cannot be overtaken by an earlier ON."""
    def __init__(self):
        self.condition=threading.Condition()
        self.issued=0
        self.serving=0

    def __enter__(self):
        with self.condition:
            ticket=self.issued
            self.issued+=1
            self.condition.notify_all()
            self.condition.wait_for(lambda:self.serving==ticket)
        return self

    def __exit__(self, *exception):
        with self.condition:
            self.serving+=1
            self.condition.notify_all()


LOCK = OrderedLock()
_owners = {}


class Conflict(ValueError):
    """A safe refusal, not a successful Hue command."""


def forget(bridge_id):
    _owners.pop((str(registry_path()),bridge_id),None)


def fingerprint(bridge, scene, group):
    return hashlib.sha256(json.dumps([bridge.get('host'),bridge.get('bridge_id'),
        group,scene.get('id'),scene.get('group_id'),scene.get('light_ids',[])],sort_keys=True).encode()).hexdigest()


def describe(bridge, scene):
    groups=bridge.get('scene_groups',[])
    candidates=[g for g in groups if scene.get('light_ids') and
                set(scene['light_ids']).issubset(g['light_ids'])]
    chosen=next((g for g in candidates if g['id']==scene.get('switch_group')),None)
    recall=scene.get('switch_mode')=='recall'
    exact=[g for g in candidates if set(g['light_ids'])==set(scene['light_ids'])]
    enabled=not recall and chosen is not None and scene.get('switch_confirmation')==fingerprint(bridge,scene,chosen)
    lights={l['id']:l for l in bridge.get('lights',[])}
    return {'enabled':enabled,'mode':'recall' if recall else 'switch',
            'automatic':scene.get('switch_mode')=='auto',
            'exact_group_id':exact[0]['id'] if len(exact)==1 else '',
            'needs_group':not recall and not enabled,
            'configured':bool(scene.get('switch_group')),
            'group_id':scene.get('switch_group',''),
            'groups':[{**g,'extra_light_ids':sorted(set(g['light_ids'])-set(scene.get('light_ids',[]))),'confirmation':fingerprint(bridge,scene,g),'lamps':[{'id':i,'name':lights.get(i,{}).get('name',i),
                        'hidden':bool(lights.get(i,{}).get('ignored') or lights.get(i,{}).get('removed'))}
                        for i in g['light_ids']],
                       'overlaps':[other['name'] for other in groups if other['id']!=g['id'] and
                                   set(g['light_ids']).intersection(other['light_ids'])]}
                      for g in candidates]}


def apply_defaults(bridge):
    """Bind a unique exact match once; never silently replace a saved assignment."""
    changed=False
    for scene in bridge.get('scenes',[]):
        if scene.get('switch_mode')=='recall' or scene.get('switch_group'):continue
        state=describe(bridge,scene)
        group=next((g for g in bridge.get('scene_groups',[]) if g['id']==state['exact_group_id']),None)
        if group is not None:
            scene.update(switch_mode='auto',switch_group=group['id'],
                         switch_confirmation=fingerprint(bridge,scene,group))
            changed=True
    return changed


def initialize_defaults():
    """Upgrade only local metadata at startup; never call Hue or change old XML."""
    with LOCK:
        document=read_registry()
        if not any(apply_defaults(bridge) for bridge in document['bridges']):return
        def change(current):
            for bridge in current['bridges']:apply_defaults(bridge)
        update_registry(change)


def configure(bridge_id, scene_id, group_id, confirmation=None, mode=None):
    if type(group_id) is not str:raise ValueError('invalid scene group')
    if mode is None:mode='group' if group_id else 'recall'
    if mode not in ('auto','group','recall'):raise ValueError('invalid scene mode')
    with LOCK:
        def change(document):
            bridge=next(b for b in document['bridges'] if b['id']==bridge_id)
            scene=next(s for s in bridge.get('scenes',[]) if s['id']==scene_id and
                       s.get('present') is not False and not s.get('removed'))
            state=describe(bridge,scene)
            chosen_id=state['exact_group_id'] if mode=='auto' else group_id
            if mode=='recall' or (mode=='auto' and not chosen_id):
                scene.pop('switch_group',None);scene.pop('switch_confirmation',None)
                scene['switch_mode']=mode
            else:
                group=next((g for g in state['groups'] if g['id']==chosen_id),None)
                if group is None or type(confirmation) is not str or confirmation!=group['confirmation']:
                    raise ValueError('group confirmation changed; reload inventory')
                # Hash inventory data only, not UI-derived names/overlap details.
                raw=next(g for g in bridge['scene_groups'] if g['id']==chosen_id)
                scene['switch_mode']=mode
                scene['switch_group']=chosen_id
                scene['switch_confirmation']=fingerprint(bridge,scene,raw)
        try:update_registry(change)
        except StopIteration:raise ValueError('unknown scene') from None
        forget(bridge_id)


def control(bridge, scene, on):
    if type(on) is not bool:raise ValueError('invalid switch state')
    with LOCK:
        # Resolve again after queuing. Configuration may have changed meanwhile.
        current=next((b for b in read_registry()['bridges'] if b['id']==bridge['id'] and b.get('enabled') is True),None)
        target=next((s for s in (current or {}).get('scenes',[]) if s['id']==scene['id'] and
                     s.get('present') is not False and not s.get('ignored') and not s.get('removed')),None)
        if target is None or not describe(current,target)['enabled']:
            raise Conflict('scene_switch_configuration_changed')
        group=next(g for g in current['scene_groups'] if g['id']==target['switch_group'])
        key=(str(registry_path()),current['id'])
        # Any topology/configuration change invalidates the in-memory command history.
        signature=json.dumps([current.get('host'),current.get('bridge_id'),current.get('key_file'),
                              current.get('scene_groups'),current.get('scenes')],sort_keys=True)
        if key not in _owners or _owners[key][0]!=signature:_owners[key]=(signature,{})
        owners=_owners[key][1]
        previous=owners.get(group['id'])
        if not on:
            if previous is None or previous['scene'] is None:raise Conflict('scene_switch_ownership_unknown')
            if previous['scene']!=target['id'] or not previous['active']:
                return {'status':'ok','accepted':False,'ignored':True,'reason':'superseded_scene_off'}
        else:
            for gid,owner in owners.items():
                if gid!=group['id'] and owner['active'] and set(owner['members']).intersection(group['light_ids']):
                    raise Conflict('scene_switch_overlapping_group_active')
        # Mark ownership uncertain BEFORE I/O. A timeout can mean the Hue write happened.
        owners[group['id']]={'scene':None,'active':True,'members':group['light_ids']}
        try:
            if on:
                from scenes import _recall
                result=_recall(current,target)
            else:
                rid=group['grouped_light_id']
                document=request_document('PUT','/clip/v2/resource/grouped_light/'+rid,
                                          payload={'on':{'on':False}},bridge=current)
                if (type(document) is not dict or document.get('errors')!=[] or
                        document.get('data')!=[{'rid':rid,'rtype':'grouped_light'}]):
                    raise ValueError('group off rejected')
                result={'status':'ok','accepted':True,'tls_verified':True}
        except Exception:
            # Unknown differs from superseded: it must return a conflict on subsequent OFF.
            # Keep an uncertain active marker to block writes to overlapping groups.
            # A fresh ON on this same group can establish ownership again.
            raise
        owners[group['id']]={'scene':target['id'],'active':on,'members':group['light_ids']}
        return result
