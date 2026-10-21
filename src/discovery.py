"""Bounded local discovery. Advertisements are hints, not device authentication."""
from concurrent.futures import ThreadPoolExecutor
import ipaddress
import re
import socket
import struct
import threading
import time
from urllib.parse import urlsplit
from bridge_store import read_registry, update_registry

LOCK=threading.Lock()
PRIVATE=tuple(ipaddress.ip_network(n) for n in ('10.0.0.0/8','172.16.0.0/12','192.168.0.0/16'))


def local_ip(value):
    address=ipaddress.ip_address(value)
    if address.version!=4 or not any(address in n for n in PRIVATE):
        raise ValueError('local IPv4 required')
    return str(address)


def clean_name(value):
    return ''.join(c for c in value if c.isprintable())[:128].strip() or 'Miniserver'


def miniserver_url(value):
    if not isinstance(value,str) or len(value)>512 or any(c.isspace() or ord(c)<32 for c in value):
        raise ValueError('invalid URL')
    parsed=urlsplit(value)
    if (parsed.scheme not in ('http','https') or parsed.username is not None or parsed.password is not None or
            parsed.query or parsed.fragment or parsed.path not in ('','/') or not parsed.hostname):
        raise ValueError('invalid local URL')
    host=parsed.hostname
    try:host=local_ip(host)
    except ValueError:
        if not re.fullmatch(r'[a-zA-Z0-9](?:[a-zA-Z0-9.-]{0,248}[a-zA-Z0-9])?\.local',host) or '..' in host:
            raise ValueError('local IPv4 or .local hostname required') from None
    port=parsed.port
    if port is not None and not 1<=port<=65535:
        raise ValueError('invalid port')
    return parsed.scheme+'://'+host+((':'+str(port)) if port is not None else '')


def saved_miniserver():
    stored=read_registry().get('miniserver')
    if type(stored) is not dict:return None
    try:return {'name':clean_name(str(stored.get('name','Miniserver'))),'url':miniserver_url(stored.get('url'))}
    except ValueError:return None


def save_miniserver(name,url):
    if not isinstance(name,str) or not 1<=len(name.strip())<=80:raise ValueError('invalid name')
    if url=='':result=None
    else:result={'name':clean_name(name),'url':miniserver_url(url)}
    def change(document):document['miniserver']=result
    update_registry(change)
    return result


def parse_lox(data, sender):
    text=data.decode('utf-8','replace').strip('[]\x00\r\n ')
    match=re.fullmatch(r'LoxLIVE:\s*(.*?)\s+(\d+\.\d+\.\d+\.\d+):(\d+)\s+([0-9a-fA-F]{12})\s+.*',text)
    if not match:return None
    host=local_ip(match[2]);port=int(match[3])
    if host!=sender or not 1<=port<=65535:return None
    return {'name':clean_name(match[1]),'host':host,'url':('https' if port==443 else 'http')+'://'+host+':'+str(port),'source':'udp','serial':match[4].upper()}


def parse_ssdp(data,sender):
    text=data.decode('utf-8','replace')
    if not text.startswith('HTTP/1.1 200'):return None
    headers={}
    for line in text.splitlines()[1:]:
        if ':' in line:
            key,value=line.split(':',1);headers[key.lower().strip()]=value.strip()
    if 'loxone miniserver' not in headers.get('server','').lower():return None
    location=urlsplit(headers.get('location',''))
    if location.username or location.password or location.scheme not in ('http','https'):return None
    host=local_ip(location.hostname)
    if host!=sender:return None
    url=miniserver_url(location.scheme+'://'+location.netloc)
    return {'name':'Loxone Miniserver','host':host,'url':url,'source':'ssdp'}


def receive(sock,parser,seconds=2.5):
    result=[];deadline=time.monotonic()+seconds
    for _ in range(256):
        remaining=deadline-time.monotonic()
        if remaining<=0:break
        sock.settimeout(remaining)
        try:data,address=sock.recvfrom(9001)
        except socket.timeout:break
        if len(data)>9000:continue
        try:item=parser(data,address[0])
        except (ValueError,TypeError,UnicodeError):continue
        if item:result.append(item)
    return result


def lox_udp():
    with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET,socket.SO_BROADCAST,1)
        sock.bind(('',7071))
        sock.sendto(b'\0',('255.255.255.255',7070))
        return receive(sock,parse_lox)


def lox_ssdp():
    with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.IPPROTO_IP,socket.IP_MULTICAST_TTL,2)
        sock.bind(('',0))
        sock.sendto(b'M-SEARCH * HTTP/1.1\r\nHOST: 239.255.255.250:1900\r\nMAN: "ssdp:discover"\r\nMX: 1\r\nST: upnp:rootdevice\r\n\r\n',('239.255.255.250',1900))
        return receive(sock,parse_ssdp)


def dns_name(data,offset,seen=None):
    seen=set() if seen is None else seen
    if len(seen)>128:raise ValueError('long DNS pointer chain')
    labels=[];end=None
    for _ in range(128):
        if offset>=len(data) or offset in seen:raise ValueError('invalid DNS name')
        seen.add(offset);size=data[offset];offset+=1
        if size==0:return '.'.join(labels).lower(),end or offset
        if size&0xc0==0xc0:
            if offset>=len(data):raise ValueError('short DNS pointer')
            pointer=((size&63)<<8)|data[offset];end=end or offset+1
            tail,_=dns_name(data,pointer,seen);labels.append(tail)
            return '.'.join(labels).lower(),end
        if size>63 or offset+size>len(data):raise ValueError('short DNS label')
        labels.append(data[offset:offset+size].decode('utf-8'));offset+=size
    raise ValueError('long DNS name')


def dns_records(data):
    if len(data)<12:raise ValueError('short DNS packet')
    _,flags,questions,answers,authority,additional=struct.unpack('!6H',data[:12])
    if not flags&0x8000 or questions+answers+authority+additional>256:raise ValueError('invalid DNS response')
    offset=12;result=[]
    for _ in range(questions):
        _,offset=dns_name(data,offset);offset+=4
    for _ in range(answers+authority+additional):
        name,offset=dns_name(data,offset)
        if offset+10>len(data):raise ValueError('short DNS record')
        kind,cls,ttl,length=struct.unpack('!HHIH',data[offset:offset+10]);offset+=10;end=offset+length
        if end>len(data):raise ValueError('short DNS data')
        value=None
        if kind==1 and length==4:value=socket.inet_ntoa(data[offset:end])
        elif kind==12:value,_=dns_name(data,offset)
        elif kind==33 and length>=7:
            port=struct.unpack('!H',data[offset+4:offset+6])[0];target,_=dns_name(data,offset+6);value=(target,port)
        if value is not None and ttl and cls&0x7fff==1:result.append((name,kind,value))
        offset=end
    return result


def dns_query(name,kind):
    labels=b''.join(bytes([len(label.encode('utf-8'))])+label.encode('utf-8') for label in name.split('.'))+b'\0'
    return struct.pack('!6H',0,0,1,0,0,0)+labels+struct.pack('!HH',kind,0x8001)


def hue_mdns():
    records=set();asked=set();destination=('224.0.0.251',5353)
    with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.IPPROTO_IP,socket.IP_MULTICAST_TTL,255);sock.bind(('',0))
        def ask(name,kind):
            if (name,kind) not in asked and len(asked)<128:
                asked.add((name,kind));sock.sendto(dns_query(name,kind),destination)
        ask('_hue._tcp.local',12)
        def parse(data,sender):
            for name,kind,value in dns_records(data):
                records.add((name,kind,value))
                if kind==12 and name=='_hue._tcp.local':ask(value,33)
                if kind==33 and name.endswith('._hue._tcp.local'):ask(value[0],1)
            return None
        receive(sock,parse)
    instances={value for name,kind,value in records if name=='_hue._tcp.local' and kind==12}
    result=[]
    for name,kind,value in records:
        if kind!=33 or name not in instances:continue
        target,port=value
        for owner,record_kind,host in records:
            if owner==target and record_kind==1:
                try:host=local_ip(host)
                except ValueError:continue
                result.append({'name':clean_name(name.removesuffix('._hue._tcp.local')),'host':host,'source':'mdns'})
    return result


def search(kind):
    if kind not in ('hue','miniserver'):raise ValueError('invalid search kind')
    if not LOCK.acquire(blocking=False):return {'devices':[],'warning':'search_busy'}
    try:
        methods=[hue_mdns] if kind=='hue' else [lox_udp,lox_ssdp]
        devices={};warnings=[]
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures=[pool.submit(method) for method in methods]
            for future in futures:
                try:
                    for item in future.result():
                        # Deduplicate different discovery methods by address.
                        devices.setdefault(item['host'],item)
                except OSError:warnings.append('network_search_unavailable')
        return {'devices':list(devices.values())[:64], 'warning':warnings[0] if warnings else (None if devices else 'no_devices')}
    finally:LOCK.release()
