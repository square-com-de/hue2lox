"""Atomic local topology storage. New bridge keys live only in the state mount."""
import copy
import hashlib
import re
import unicodedata
import json
import os
from pathlib import Path
import tempfile
import threading

LOCK = threading.RLock()


def registry_path():
    return Path(os.environ.get('HUE_REGISTRY_FILE', str((Path(__file__).resolve().parent.parent/'config/registry.json'))))


def state_dir():
    return Path(os.environ.get('HUE_STATE_DIR', '/data'))


def short_slug(name):
    name=str(name).lower().replace('ä','ae').replace('ö','oe').replace('ü','ue').replace('ß','ss')
    name=unicodedata.normalize('NFKD',name).encode('ascii','ignore').decode()
    return re.sub(r'[^a-z0-9]+','-',name).strip('-')[:8].rstrip('-') or 'licht'


def ensure_short_names(document):
    changed=False
    def assign(items,reserved=()):
        nonlocal changed
        used=set(reserved)
        # Reserve existing aliases first, even for absent, removed or ignored lamps.
        for item in items:
            alias=item.get('short_name')
            if type(alias) is str and re.fullmatch(r'[a-z0-9][a-z0-9-]{0,7}',alias) and alias not in used:
                used.add(alias)
            else:
                item.pop('short_name',None)
        for item in sorted(items,key=lambda item:item['id']):
            if 'short_name' in item:continue
            base=short_slug(item.get('name',''))
            alias=base;attempt=0
            while alias in used:
                suffix=hashlib.sha256((item['id']+':'+str(attempt)).encode()).hexdigest()[:4]
                alias=base[:3]+'-'+suffix;attempt+=1
            item['short_name']=alias;used.add(alias);changed=True
    assign(document['bridges'],{'api'})
    for bridge in document['bridges']:assign(bridge.get('lights',[]))
    return changed


def read_registry():
    with LOCK:
        path=registry_path()
        document=json.loads(path.read_text())
        if document.get('schema_version') != 1 or type(document.get('bridges')) is not list:
            raise ValueError('invalid registry')
        previous=copy.deepcopy(document)
        if ensure_short_names(document) and path.parent.resolve()==state_dir().resolve():
            atomic_write(path.with_name('registry.previous.json'),json.dumps(previous,ensure_ascii=False).encode())
            atomic_write(path,json.dumps(document,ensure_ascii=False,indent=2,allow_nan=False).encode())
        return document


def atomic_write(path, content, mode=0o600):
    path = Path(path)
    descriptor, temporary = tempfile.mkstemp(prefix='.' + path.name + '-', dir=str(path.parent))
    try:
        os.fchmod(descriptor, mode)
        with os.fdopen(descriptor, 'wb') as file:
            file.write(content)
            file.flush()
            os.fsync(file.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def update_registry(change):
    with LOCK:
        current = read_registry()
        updated = copy.deepcopy(current)
        result = change(updated)
        ensure_short_names(updated)
        path = registry_path()
        # Never fall back to writing the code/image directory.
        if path.parent.resolve() != state_dir().resolve():
            raise OSError('writable registry is not configured')
        encoded = json.dumps(updated, ensure_ascii=False, indent=2, allow_nan=False).encode()
        atomic_write(path.with_name('registry.previous.json'), json.dumps(current, ensure_ascii=False).encode())
        atomic_write(path, encoded)
        return result


def save_bridge_key(bridge_id, value):
    import re
    if not re.fullmatch(r'[A-Za-z0-9_-]{1,64}', bridge_id):
        raise ValueError('invalid bridge reference')
    if not isinstance(value, str) or not 16 <= len(value) <= 512 or not value.isascii() or any(ord(c) < 33 or ord(c) > 126 for c in value):
        raise ValueError('invalid bridge key')
    directory = state_dir() / 'bridge-keys'
    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    path = directory / (bridge_id + '.key')
    atomic_write(path, value.encode())
    return str(path)
