"""Configured lights and Loxone VirtualOut XML; never queries or writes a lamp."""
import scenes
import lamp_types
import io
import json
import os
from pathlib import Path
import re
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET
from bridge_store import read_registry, ensure_short_names


def public_url():
    url = os.environ.get('HUE_PUBLIC_URL', 'https://localhost:8443').rstrip('/')
    parsed = urlsplit(url)
    if parsed.scheme not in ('http', 'https') or not parsed.hostname or parsed.username or parsed.password or parsed.path or parsed.query or parsed.fragment:
        raise ValueError('invalid public URL')
    parsed.port
    return url


def registry():
    return read_registry()

def lights():
    result = []
    document=registry()
    ensure_short_names(document)
    for bridge in document['bridges']:
        for light in bridge.get('lights', []):
            if light.get('ignored') or light.get('removed'):
                continue
            key = bridge['id'] + '/' + light['id']
            if not re.fullmatch(r'[A-Za-z0-9_-]+/[A-Za-z0-9_-]+', key):
                continue
            path = '/' + bridge['short_name'] + '/' + light['short_name'] + '/state'
            capabilities = light.get('capabilities', [])
            available = bridge.get('enabled') is True and light.get('present') is not False
            commands=lamp_types.commands(light)
            result.append({'key': key, 'name': light['name'], 'bridge': bridge['name'],
                           'room': light.get('room',''), 'path': path, 'commands': commands,
                           'recommended_mode':lamp_types.recommended(commands),'enabled_modes':lamp_types.chosen(light,commands),**lamp_types.details(light),
                           'available': available, 'writes_enabled': os.environ.get('HUE_WRITES_ENABLED') == '1'})
    return result


def resolve_path(path):
    match=re.fullmatch(r'/api/lights/([A-Za-z0-9_-]+)/([A-Za-z0-9_-]+)/state',path)
    short=re.fullmatch(r'/([a-z0-9][a-z0-9-]{0,7})/([a-z0-9][a-z0-9-]{0,7})/state',path)
    if not match and not short:return None
    document=registry()
    ensure_short_names(document)
    for bridge in document['bridges']:
        if bridge.get('enabled') is not True:continue
        for light in bridge.get('lights',[]):
            matches=(match and bridge['id']==match[1] and light['id']==match[2]) or (short and bridge['short_name']==short[1] and light['short_name']==short[2])
            if matches and light.get('present') is not False and not light.get('ignored') and not light.get('removed'):
                return bridge,light
    return None


def export_xml(keys, include_token, token=None, kind='lights', variants=None, language='de'):
    if language not in ('de','en'):raise ValueError('unsupported language')
    translated_names={'Ein/Aus':'On/off','Dimmen':'Dimming','Lumitech RGB + Weiß':'Lumitech RGB + White','Szene aktivieren':'Recall scene'} if language=='en' else {}
    if type(keys) is not list or not keys or len(keys) > 500 or any(type(key) is not str for key in keys) or len(set(keys)) != len(keys):
        raise ValueError('invalid selection')
    if kind not in ('lights','scenes'):
        raise ValueError('invalid export kind')
    source = lights() if kind == 'lights' else scenes.available_scenes()
    candidates = {item['key']: item for item in source if item['available']}
    if any(key not in candidates for key in keys):
        raise ValueError('unknown or disabled lamp')
    if type(include_token) is not bool or (include_token and not token):
        raise ValueError('invalid token option')
    if variants is None:
        variants={}
    if type(variants) is not dict or any(type(k) is not str or not (type(v) is str or (type(v) is list and v and all(type(m) is str for m in v) and len(set(v))==len(v))) for k,v in variants.items()) or any(key not in keys for key in variants) or (kind != 'lights' and variants):
        raise ValueError('invalid command variants')
    auth = token if include_token else 'DEIN_HUE2LOX_TOKEN'
    header = 'Authorization: Bearer ' + auth + r'\r\nContent-Type: application/json'
    selected = [dict(candidates[key]) for key in keys]
    if kind == 'lights':
        for light in selected:
            modes=variants.get(light['key'],light['enabled_modes'])
            if type(modes) is str:modes=[modes]
            selected_commands=[next((c for c in light['commands'] if c['id']==mode),None) for mode in modes]
            if any(command is None for command in selected_commands):raise ValueError('unsupported command variant')
            light['commands']=selected_commands
    title = 'Hue2Lox · ' + (selected[0]['name'] if len(selected) == 1 else str(len(selected)) + ((' scenes' if kind == 'scenes' else ' lights') if language=='en' else (' Szenen' if kind == 'scenes' else ' Lampen')))
    root = ET.Element('VirtualOut', {'HintText': '', 'Title': title, 'Comment': 'Hue2Lox HTTPS',
        'Address': public_url(), 'CmdInit': '', 'CloseAfterSend': 'true', 'CmdSep': ';'})
    ET.SubElement(root, 'Info', {'templateType': '3', 'minVersion': '17000331'})
    for light in selected:
        for command in light['commands']:
            ET.SubElement(root, 'VirtualOutCmd', {'Title': light['name'] + ' · ' + translated_names.get(command['name'],command['name']),
                'Comment': light['bridge'] + ' · ' + light['room'],
                'CmdOnMethod': 'PUT', 'CmdOffMethod': 'PUT', 'CmdOn': light['path'],
                'CmdOnHTTP': header, 'CmdOnPost': command['body_on'],
                'CmdOff': light['path'] if command['body_off'] else '',
                'CmdOffHTTP': header if command['body_off'] else '', 'CmdOffPost': command['body_off'],
                'CmdAnswer': '', 'Analog': str(command['analog']).lower(), 'Repeat': '0', 'RepeatRate': '0', 'HintText': ''})
    stream = io.BytesIO()
    ET.ElementTree(root).write(stream, encoding='utf-8', xml_declaration=True)
    return stream.getvalue()
