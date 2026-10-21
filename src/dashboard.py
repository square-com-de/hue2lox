import lamp_types
"""Read-only public topology projection. Never exposes credential fields."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import threading
import time
from hue_client import read_bridge_statuses
from bridge_store import read_registry
from discovery import saved_miniserver

LOCK = threading.Lock()
CACHE = None
CACHE_AT = 0
GENERATION = 0
FETCH_LOCK = threading.Lock()
REGISTRY = (Path(__file__).resolve().parent.parent/'config/registry.json')


def overview():
    global CACHE, CACHE_AT
    with LOCK:
        if CACHE is not None and time.monotonic() - CACHE_AT < 5:
            return CACHE
    # Serialize refreshes separately. Local mutations only acquire LOCK.
    with FETCH_LOCK:
        with LOCK:
            if CACHE is not None and time.monotonic() - CACHE_AT < 5:
                return CACHE
            generation = GENERATION
        registry = read_registry()
        if registry.get('schema_version') != 1:
            raise ValueError('unknown registry schema')
        bridges = []
        jobs = []
        for bridge in registry['bridges']:
            configured = bridge.get('enabled') is True
            public = {k: bridge.get(k) for k in ('id','name','host')}
            public.update(enabled=configured, status='prepared' if not configured else 'ready', lights=[])
            for light in bridge.get('lights', []):
                if light.get('removed'):
                    continue
                item = {k: light.get(k) for k in ('id','name','room','model','archetype','icon','icon_override','capabilities','control_path')}
                item.update(lamp_types.details(light))
                item.update(status='ignored' if light.get('ignored') else 'prepared', state=None, ignored=bool(light.get('ignored')))
                public['lights'].append(item)
            if configured and any(not item['ignored'] for item in public['lights']):
                jobs.append((bridge, public))
            bridges.append(public)
        def fetch(job):
            bridge, public = job
            try:
                states = read_bridge_statuses(bridge)
            except Exception:
                states = {}
                public['status'] = 'degraded'
            missing = {light['id'] for light in bridge.get('lights',[]) if light.get('present') is False}
            for item in public['lights']:
                if item['ignored']:
                    continue
                state = states.get(item['id']) if item['id'] not in missing else None
                if state is not None:
                    item['state'] = state
                    item['status'] = 'online'
                else:
                    item['status'] = 'unavailable'
                    public['status'] = 'degraded'
                    item['error'] = ('Bei der letzten Inventur nicht gefunden.' if item['id'] in missing else
                                     'Status derzeit nicht verfügbar. Bridge-Verbindung prüfen.')
            if not states and public['lights']:
                public['status'] = 'degraded'
        with ThreadPoolExecutor(max_workers=4) as pool:
            list(pool.map(fetch, jobs))
        result = {'status':'ok','updated_at':datetime.now(timezone.utc).isoformat(),
                  'read_only':True,'bridges':bridges,'miniserver':saved_miniserver(),
                  'scene_count':sum(1 for bridge in registry['bridges'] if bridge.get('enabled') is True
                                    for scene in bridge.get('scenes',[]) if scene.get('present') is not False
                                    and not scene.get('ignored') and not scene.get('removed')),
                  'features':{k: os.environ.get(v) == '1' for k,v in (
                      ('control','HUE_WRITES_ENABLED'),('rgb','HUE_COLOR_ENABLED'),('white','HUE_WHITE_ENABLED'))}}
        with LOCK:
            # A mutation during this fetch wins. Do not republish its old snapshot.
            if generation == GENERATION:
                CACHE=result;CACHE_AT=time.monotonic()
                return result
        # Let the caller retry instead of presenting pre-mutation data as current.
        raise ValueError('overview changed during refresh; retry')


def invalidate():
    global CACHE, CACHE_AT, GENERATION
    with LOCK:
        GENERATION += 1
        CACHE = None
        CACHE_AT = 0
