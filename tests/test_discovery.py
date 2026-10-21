import json
import os
import socket
import struct
import unittest
from unittest.mock import patch
import discovery
import dashboard
import bridge_store
from tests import test_admin
from tests import test_bridges


def name(value):return b''.join(bytes([len(part)])+part.encode() for part in value.split('.'))+b'\0'
def record(owner,kind,value):return name(owner)+struct.pack('!HHIH',kind,1,120,len(value))+value
def hue_packet():
    service='_hue._tcp.local';instance='Hue Bridge._hue._tcp.local';host='hue-test.local'
    return struct.pack('!6H',0,0x8400,0,3,0,0)+record(service,12,name(instance))+record(instance,33,struct.pack('!HHH',0,0,443)+name(host))+record(host,1,socket.inet_aton('10.200.0.253'))

class DiscoveryTests(unittest.TestCase):
    setUp=test_bridges.BridgeTests.setUp
    tearDown=test_bridges.BridgeTests.tearDown
    def test_local_links_persist_and_clear_without_network(self):
        with patch('discovery.socket.socket') as network:
            self.assertEqual(discovery.save_miniserver('Zuhause','https://10.200.0.50:8443/')['url'],'https://10.200.0.50:8443')
            self.assertEqual(discovery.saved_miniserver()['name'],'Zuhause')
            self.assertEqual(bridge_store.read_registry()['miniserver']['url'],'https://10.200.0.50:8443')
            self.assertEqual(discovery.miniserver_url('http://miniserver.local'),'http://miniserver.local')
            self.assertIsNone(discovery.save_miniserver('Zuhause',''));self.assertIsNone(discovery.saved_miniserver());network.assert_not_called()
    def test_dashboard_counts_active_scenes_and_saved_link(self):
        def change(doc):
            doc['bridges'][0]['scenes']=[{'id':'active'},{'id':'ignored','ignored':True},{'id':'removed','removed':True},{'id':'deleted','present':False}]
            doc['bridges'][1]['scenes']=[{'id':'disabled-bridge'}]
        bridge_store.update_registry(change);discovery.save_miniserver('Zuhause','https://10.200.0.50')
        with patch('dashboard.read_bridge_statuses',return_value={}):
            result=dashboard.overview();self.assertEqual(result['scene_count'],1)
            self.assertEqual(result['miniserver']['url'],'https://10.200.0.50')
    def test_bad_urls_leave_registry_unchanged(self):
        before=self.registry.read_bytes()
        for url in ['javascript:alert(1)','https://user:pass@10.200.0.50','https://example.com','http://127.0.0.1','http://169.254.169.254','http://10.200.0.1:0','http://10.200.0.1/path','http://10.200.0.1?token=secret','http://10.200.0.1#fragment','http://10.200.0.1\n',None]:
            with self.subTest(url=url),self.assertRaises((ValueError,TypeError)):discovery.save_miniserver('test',url)
            self.assertEqual(before,self.registry.read_bytes())
    def test_lox_reply_parsing_checks_sender_port_and_private_ip(self):
        data=b'[LoxLIVE: Mein Zuhause 10.200.0.50:80 504F11223344 17.2.8.28 Prog:2026]'
        self.assertEqual(discovery.parse_lox(data,'10.200.0.50')['name'],'Mein Zuhause')
        self.assertEqual(discovery.parse_lox(data.replace(b':80 ',b':443 '),'10.200.0.50')['url'],'https://10.200.0.50:443')
        self.assertIsNone(discovery.parse_lox(data,'10.200.0.51'))
        self.assertIsNone(discovery.parse_lox(data.replace(b':80 ',b':99999 '),'10.200.0.50'))
        self.assertIsNone(discovery.parse_lox(b'unrelated','10.200.0.50'))
    def test_ssdp_requires_loxone_and_matching_location(self):
        data=b'HTTP/1.1 200 OK\r\nSERVER: Loxone Miniserver UPnP/1.0\r\nLOCATION: http://10.200.0.50:80/upnp.xml\r\n\r\n'
        self.assertEqual(discovery.parse_ssdp(data,'10.200.0.50')['url'],'http://10.200.0.50:80')
        self.assertIsNone(discovery.parse_ssdp(data,'10.200.0.51'))
        self.assertIsNone(discovery.parse_ssdp(data.replace(b'Loxone Miniserver',b'Other device'),'10.200.0.50'))
    def test_dns_records_and_malformed_compression(self):
        records=discovery.dns_records(hue_packet());self.assertIn(('hue-test.local',1,'10.200.0.253'),records)
        self.assertEqual(discovery.dns_name(b'\x03hue\0\xc0\0',5),('hue',7))
        for packet in [b'',b'\xc0\0',b'\x3ffoo']:
            with self.assertRaises(ValueError):discovery.dns_name(packet,0)
        with self.assertRaises(ValueError):discovery.dns_records(hue_packet()[:-1])
    def test_hue_mdns_collects_only_matching_service(self):
        def fake_receive(sock,parser):parser(hue_packet(),'10.200.0.253');return []
        with patch('discovery.socket.socket') as factory,patch('discovery.receive',side_effect=fake_receive):
            result=discovery.hue_mdns();self.assertEqual(result[0]['host'],'10.200.0.253')
            self.assertEqual(result[0]['source'],'mdns')
    def test_search_deduplicates_busy_and_failed_transport(self):
        device={'name':'test','host':'10.200.0.50','url':'http://10.200.0.50'}
        with patch('discovery.lox_udp',return_value=[device]),patch('discovery.lox_ssdp',return_value=[device]):
            self.assertEqual(len(discovery.search('miniserver')['devices']),1)
        with patch('discovery.hue_mdns',side_effect=OSError('no network')):
            self.assertEqual(discovery.search('hue')['warning'],'network_search_unavailable')
        discovery.LOCK.acquire()
        try:self.assertEqual(discovery.search('hue')['warning'],'search_busy')
        finally:discovery.LOCK.release()

class DiscoveryAPITests(unittest.TestCase):
    setUp=test_admin.AdminTests.setUp
    tearDown=test_admin.AdminTests.tearDown
    request=test_admin.AdminTests.request
    login=test_admin.AdminTests.login
    def test_discovery_requires_session_origin_csrf_and_valid_kind(self):
        path='/api/admin/discovery'
        self.assertEqual(self.request(path,{'kind':'hue'})[0],401);self.login()
        with patch('discovery.search',return_value={'devices':[],'warning':'no_devices'}) as search:
            for headers in [{'X-CSRF-Token':''},{'Origin':'https://evil.test'}]:self.assertEqual(self.request(path,{'kind':'hue'},headers)[0],403)
            search.assert_not_called();self.assertEqual(self.request(path,{'kind':'hue'})[0],200);search.assert_called_once_with('hue')
        self.assertEqual(self.request(path,{'kind':'arbitrary'})[0],400)
    def test_save_link_requires_csrf_and_does_not_fetch_target(self):
        self.assertEqual(self.request('/api/admin/miniserver')[0],401);self.login()
        registry=self.directory/'registry.json';registry.write_text(json.dumps({'schema_version':1,'bridges':[]}))
        with patch.dict(os.environ,{'HUE_STATE_DIR':str(self.directory),'HUE_REGISTRY_FILE':str(registry)}),patch('discovery.search') as network:
            body={'name':'Loxone','url':'https://10.200.0.50'}
            self.assertEqual(self.request('/api/admin/miniserver',body,{'X-CSRF-Token':''})[0],403)
            self.assertEqual(self.request('/api/admin/miniserver',body)[0],200)
            code,_,raw=self.request('/api/admin/miniserver');self.assertEqual(code,200);self.assertEqual(json.loads(raw)['miniserver']['url'],body['url']);network.assert_not_called()
