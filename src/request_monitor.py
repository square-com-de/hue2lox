"""Opt-in, bounded, memory-only diagnostics; never retains raw requests."""
from collections import deque
from datetime import datetime, timezone
import copy
import ipaddress
import json
import math
import re
import threading
import time

DURATION=600
LIMIT=200
LOCK=threading.RLock()
EVENTS=deque(maxlen=LIMIT)
DEADLINE=0
GENERATION=0
NEXT_ID=0
REASONS={'unauthorized','writes_disabled','control_not_configured','invalid_length','expected_json',
         'invalid_state','white_disabled','color_disabled','bridge_command_failed','configuration_unavailable'}


def control_path(path):
    return path.split('?',1)[0]=='/hue-go/state' or path.startswith(('/api/lights/','/api/scenes/')) or bool(re.fullmatch(r'/[a-z0-9][a-z0-9-]{0,7}/[a-z0-9][a-z0-9-]{0,7}/state',path.split('?',1)[0]))


def safe_path(path):
    if path=='/hue-go/state':return path
    if path.startswith('/api/scenes/'):return '/api/scenes/[Bridge]/[Szene]/recall'
    if path.startswith('/api/lights/'):return '/api/lights/[Bridge]/[Lampe]/state'
    if control_path(path):return '/[Bridge]/[Lampe]/state'
    return '[Unbekannter Steuerungspfad]'


def snapshot():
    with LOCK:
        remaining=max(0,math.ceil(DEADLINE-time.monotonic()))
        if not remaining:
            for event in EVENTS:
                if event['result']=='pending':event['result']='recording_stopped'
        return {'active':remaining>0,'remaining_seconds':remaining,'duration_seconds':DURATION,
                'limit':LIMIT,'events':copy.deepcopy(list(EVENTS))}


def start():
    global DEADLINE,GENERATION
    with LOCK:
        GENERATION+=1;EVENTS.clear();DEADLINE=time.monotonic()+DURATION
        return snapshot()


def stop():
    global DEADLINE
    with LOCK:
        DEADLINE=0
        return snapshot()


def clear():
    with LOCK:
        EVENTS.clear()
        return snapshot()


def begin(method,source,path):
    global NEXT_ID
    with LOCK:
        if time.monotonic()>=DEADLINE:return None
        try:source=str(ipaddress.ip_address(source))
        except ValueError:source='unbekannt'
        NEXT_ID+=1
        event={'id':NEXT_ID,'time':datetime.now(timezone.utc).isoformat(),'method':method if method in ('PUT','GET','POST','PATCH','DELETE','HEAD') else 'OTHER',
               'source':source,'path':safe_path(path),'values':{},'http_status':None,'result':'pending'}
        EVENTS.append(event)
        return (GENERATION,NEXT_ID,time.monotonic())


def update(handle,values=None,path=None,status=None,reason=None):
    if handle is None:return
    with LOCK:
        if handle[0]!=GENERATION or time.monotonic()>=DEADLINE:return
        event=next((e for e in EVENTS if e['id']==handle[1]),None)
        if event is None:return
        # Only a previously resolved, registered resource path may be expanded.
        if path and (re.fullmatch(r'/api/(?:lights|scenes)/[A-Za-z0-9_-]{1,24}/[0-9a-fA-F-]{36}/(?:state|recall)',path) or re.fullmatch(r'/[a-z0-9][a-z0-9-]{0,7}/[a-z0-9][a-z0-9-]{0,7}/state',path)):event['path']=path
        if type(values) is dict:
            safe={}
            for key,value in values.items():
                if key in ('on','recall') and type(value) is bool:safe[key]=value
                elif key in ('brightness','kelvin','loxone_rgb','loxone_lumitech') and type(value) in (int,float) and math.isfinite(value) and abs(value)<=1e10:safe[key]=value
                elif key=='rgb' and type(value) is dict and set(value)=={'r','g','b'} and all(type(v) in (int,float) and math.isfinite(v) and 0<=v<=255 for v in value.values()):safe[key]=dict(value)
            event['values']=safe
        if status is not None:
            event['http_status']=int(status)
            event['duration_ms']=round((time.monotonic()-handle[2])*1000)
            event['result']=reason if reason in REASONS else ('accepted' if 200<=status<300 else 'not_found' if status==404 else 'method_not_allowed' if status==405 else 'request_rejected')


FIELDS={'on','recall','brightness','kelvin','loxone_rgb','loxone_lumitech','rgb','r','g','b'}
NUMBER=re.compile(r'-?(?:0|[1-9][0-9]{0,10})(?:\.[0-9]{1,12})?(?:[eE][+-]?[0-9]{1,3})?\Z')


def diagnostic_scalar(value):
    if value is None or type(value) is bool:return value
    if type(value) in (int,float):
        return value if abs(value)<=1e10 and math.isfinite(value) else '[number_out_of_range]'
    if type(value) is str:
        if value=='<v>':return value
        if NUMBER.fullmatch(value) and math.isfinite(float(value)) and abs(float(value))<=1e10:return value
        return '[redacted_text]'
    return '[invalid_type]'


def diagnostic_object(value,depth=0):
    if type(value) is not dict:return diagnostic_scalar(value)
    if depth>1:return '[redacted_nesting]'
    result={key:diagnostic_object(item,depth+1) if key=='rgb' else diagnostic_scalar(item)
            for key,item in value.items() if key in FIELDS}
    if any(key not in FIELDS for key in value):result['[other_fields]']='[redacted]'
    return result


def malformed_preview(text):
    # Tokenize the complete input. Never copy arbitrary substrings or exception text.
    tokens=re.findall(r'"(?:[^"\\]|\\.)*(?:"|$)|<v>|[{}\[\]:,]|[^\s{}\[\]:,]+',text)
    safe=[]
    allowed=False
    for index,token in enumerate(tokens):
        if token in '{}[]:,':
            safe.append(token)
            if token!=':':allowed=False
            continue
        try:value=json.loads(token) if token.startswith('"') else None
        except ValueError:value=None
        if index+1<len(tokens) and tokens[index+1]==':':
            allowed=type(value) is str and value in FIELDS
            safe.append(json.dumps(value if allowed else '[redacted_field]'))
        elif not allowed:safe.append('[redacted]')
        elif token.startswith('"'):safe.append(json.dumps(diagnostic_scalar(value) if value is not None else '[redacted_text]'))
        elif token in ('true','false','null','<v>'):safe.append(token)
        elif NUMBER.fullmatch(token) and abs(float(token))<=1e10:safe.append(token)
        else:safe.append('[redacted]')
    return ' '.join(safe)[:2048]


def record_body(handle,raw):
    if handle is None:return
    text=raw.decode('utf-8',errors='replace')
    try:
        value=json.loads(text)
        body=json.dumps(diagnostic_object(value),ensure_ascii=False,allow_nan=False)
        detail='parsed'
    except json.JSONDecodeError as error:
        body=malformed_preview(text)
        detail='invalid_json:'+str(error.lineno)+':'+str(error.colno)
    with LOCK:
        if handle[0]!=GENERATION or time.monotonic()>=DEADLINE:return
        event=next((e for e in EVENTS if e['id']==handle[1]),None)
        if event is not None:
            event['body']=body
            event['body_detail']=detail



def framing(handle,declared,raw,extra=b'',read_error=None):
    if handle is None:return
    leading=len(raw)-len(raw.lstrip(b' \t\r\n'))
    trailing=len(raw)-len(raw.rstrip(b' \t\r\n'))
    stats={'declared_bytes':declared,'read_bytes':len(raw),
           'leading_whitespace_bytes':leading,'trailing_whitespace_bytes':trailing,
           'leading_cr':raw[:leading].count(b'\r'),'leading_lf':raw[:leading].count(b'\n'),
           'trailing_cr':raw[len(raw)-trailing:].count(b'\r') if trailing else 0,
           'trailing_lf':raw[len(raw)-trailing:].count(b'\n') if trailing else 0,
           'ends_with_object_close':raw.rstrip().endswith(b'}'),
           'extra_bytes':len(extra),'read_error':read_error if read_error in ('timeout','eof','io_error') else None}
    try:json.loads(raw);stats['json_complete']=True
    except (ValueError,UnicodeError):stats['json_complete']=False
    stats['json_complete_with_extra']=False
    if extra:
        try:json.loads(raw+extra);stats['json_complete_with_extra']=True
        except (ValueError,UnicodeError):pass
    with LOCK:
        if handle[0]!=GENERATION or time.monotonic()>=DEADLINE:return
        event=next((e for e in EVENTS if e['id']==handle[1]),None)
        if event is not None:event['framing']=stats
