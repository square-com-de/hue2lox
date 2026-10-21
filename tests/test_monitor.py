import json
import unittest
from unittest.mock import patch
import request_monitor as monitor
from tests import test_admin

class MonitorTests(unittest.TestCase):
    def setUp(self):monitor.stop();monitor.clear()
    def tearDown(self):monitor.stop();monitor.clear()
    def test_off_expiry_and_limit(self):
        self.assertIsNone(monitor.begin('PUT','127.0.0.1','/hue-go/state'))
        with patch('request_monitor.time.monotonic',return_value=100):
            self.assertEqual(monitor.start()['remaining_seconds'],600)
            for i in range(205):monitor.begin('PUT','127.0.0.1','/hue-go/state')
            self.assertEqual(len(monitor.snapshot()['events']),200)
        with patch('request_monitor.time.monotonic',return_value=701):
            self.assertFalse(monitor.snapshot()['active']);self.assertIsNone(monitor.begin('PUT','127.0.0.1','/hue-go/state'))
            self.assertEqual(monitor.snapshot()['events'][0]['result'],'recording_stopped')
    def test_restart_and_clear_prevent_inflight_events_reappearing(self):
        monitor.start();old=monitor.begin('PUT','127.0.0.1','/hue-go/state');monitor.start()
        monitor.update(old,status=200);self.assertEqual(monitor.snapshot()['events'],[])
        handle=monitor.begin('PUT','127.0.0.1','/hue-go/state');monitor.clear();monitor.update(handle,status=200)
        self.assertEqual(monitor.snapshot()['events'],[]);self.assertTrue(monitor.snapshot()['active'])
    def test_allowlist_never_keeps_raw_secret_values(self):
        secret='TEST-ONLY-SECRET-TOKEN-1234567890123456789';monitor.start()
        handle=monitor.begin(secret,'127.0.0.1','/api/lights/'+secret+'/token?key='+secret)
        monitor.update(handle,values={'token':secret,'on':secret,'brightness':secret,'rgb':{'r':secret,'g':0,'b':0}},path='/'+secret,status=401,reason=secret)
        event=monitor.snapshot()['events'][0];self.assertNotIn(secret,json.dumps(event));self.assertEqual(event['values'],{})
        handle=monitor.begin('PUT','127.0.0.1','/hue-go/state');monitor.update(handle,values={'on':True,'brightness':47,'rgb':{'r':1,'g':2,'b':3}},status=200)
        self.assertEqual(monitor.snapshot()['events'][-1]['values']['brightness'],47)
    def test_stop_keeps_events_but_rejects_new_writes(self):
        monitor.start();handle=monitor.begin('PUT','127.0.0.1','/hue-go/state');monitor.stop()
        monitor.update(handle,values={'brightness':47},status=200)
        result=monitor.snapshot();self.assertFalse(result['active']);self.assertEqual(len(result['events']),1);self.assertEqual(result['events'][0]['values'],{})

    def test_rejected_body_numbers_types_and_placeholders(self):
        monitor.start()
        for value in [201004847,100101100,'100100100','<v>',True,None]:
            handle=monitor.begin('PUT','127.0.0.1','/hue-go/state')
            monitor.record_body(handle,json.dumps({'loxone_rgb':value}).encode())
            event=monitor.snapshot()['events'][-1]
            self.assertEqual(json.loads(event['body'])['loxone_rgb'],value)
            self.assertEqual(event['body_detail'],'parsed')
        handle=monitor.begin('PUT','127.0.0.1','/hue-go/state')
        monitor.record_body(handle,b'{"loxone_rgb":<v>}')
        event=monitor.snapshot()['events'][-1];self.assertIn('<v>',event['body']);self.assertRegex(event['body_detail'],r'^invalid_json:\d+:\d+$')
    def test_body_redaction_valid_and_malformed(self):
        monitor.start();secret='PRIVATE-KEY-ABC123456789'
        bodies=[json.dumps({'token':secret,'on':secret,'rgb':{'r':secret,'g':999,'b':0}}),
                '{"token":"'+secret+'","loxone_rgb":<v>}',
                '{"token":123456789,"loxone_rgb":123456789012345678901234567890,',
                '{"brightness":"'+secret,
                '{"loxone_rgb":'+('9'*500)+'}',
                '{"loxone_rgb":NaN}']
        for body in bodies:
            handle=monitor.begin('PUT','127.0.0.1','/hue-go/state');monitor.record_body(handle,body.encode())
            event=monitor.snapshot()['events'][-1]
            self.assertNotIn(secret,json.dumps(event));self.assertNotIn('123456789012345678901234567890',event['body'])
        self.assertNotIn('123456789',monitor.malformed_preview('{"token":123456789,'))

class MonitorAPITests(unittest.TestCase):
    request=test_admin.AdminTests.request
    login=test_admin.AdminTests.login
    def setUp(self):test_admin.AdminTests.setUp(self);monitor.stop();monitor.clear()
    def tearDown(self):monitor.stop();monitor.clear();test_admin.AdminTests.tearDown(self)
    def test_admin_session_origin_and_csrf(self):
        self.assertEqual(self.request('/api/admin/monitor')[0],401)
        for action in ['start','stop','clear']:self.assertEqual(self.request('/api/admin/monitor/'+action,{})[0],401)
        self.login()
        for action in ['start','stop','clear']:
            for headers in [{'X-CSRF-Token':''},{'Origin':'https://evil.test'}]:self.assertEqual(self.request('/api/admin/monitor/'+action,{},headers)[0],403)
        self.assertFalse(monitor.snapshot()['active']);self.assertEqual(self.request('/api/admin/monitor/start',{})[0],200)
        self.assertEqual(self.request('/api/admin/monitor')[0],200)
    def test_success_errors_wrong_method_and_redaction(self):
        self.login();self.request('/api/admin/monitor/start',{})
        auth={'Authorization':'Bearer '+'t'*48};path='/hue-go/state'
        secret='TEST-ONLY-SECRET-123456789012345678901234567'
        with patch('app.write_state',return_value={'status':'accepted'}) as write:
            self.assertEqual(self.request(path,{'brightness':47},auth,method='PUT')[0],200)
            self.assertEqual(self.request(path,{'brightness':secret},auth,method='PUT')[0],400)
            self.assertEqual(self.request(path,{'brightness':47},{'Authorization':'Bearer '+secret},method='PUT')[0],401)
            self.assertEqual(self.request(path,{'on':True},auth,method='POST')[0],405)
            self.assertEqual(self.request(path,method='GET')[0],405)
            self.assertEqual(self.request('/api/lights/'+secret+'/unknown/state?key='+secret,{'on':True},auth,method='PUT')[0],404)
            write.assert_called_once_with({'brightness':47})
        events=monitor.snapshot()['events'];self.assertEqual(len(events),6)
        self.assertEqual(events[0]['values'],{'brightness':47});self.assertEqual(events[0]['result'],'accepted')
        self.assertEqual(events[1]['values'],{});self.assertEqual(events[2]['result'],'unauthorized')
        encoded=json.dumps(events);self.assertNotIn(secret,encoded);self.assertNotIn('t'*48,encoded);self.assertNotIn('Authorization',encoded)
    def test_hue_errors_are_generic_and_monitor_does_not_trigger_writes(self):
        self.login();self.request('/api/admin/monitor/start',{})
        with patch('app.write_state',side_effect=ValueError('PRIVATE_HUE_KEY')):
            self.assertEqual(self.request('/hue-go/state',{'on':True},{'Authorization':'Bearer '+'t'*48},method='PUT')[0],502)
        event=monitor.snapshot()['events'][0];self.assertEqual(event['result'],'bridge_command_failed');self.assertNotIn('PRIVATE',json.dumps(event))
        with patch('app.write_state') as write:
            self.request('/api/admin/monitor');self.request('/api/admin/monitor/stop',{});self.request('/api/admin/monitor/clear',{})
            self.assertEqual(monitor.snapshot()['events'],[]);write.assert_not_called()
    def test_disabled_monitor_and_health_do_not_record(self):
        with patch('app.write_state',return_value={'status':'accepted'}):self.request('/hue-go/state',{'on':True},{'Authorization':'Bearer '+'t'*48},method='PUT')
        self.assertEqual(monitor.snapshot()['events'],[])
        monitor.start();self.request('/health');self.assertEqual(monitor.snapshot()['events'],[])

    def test_invalid_body_visible_before_validation_without_writes(self):
        monitor.start();auth={'Authorization':'Bearer '+'t'*48}
        with patch('app.write_state') as write:
            for body in [{'loxone_rgb':201004847},{'loxone_rgb':'100100100'},{'brightness':101}]:
                self.assertEqual(self.request('/hue-go/state',body,auth,method='PUT')[0],400)
                event=monitor.snapshot()['events'][-1]
                self.assertEqual(json.loads(event['body']),body)
            import http.client
            c=http.client.HTTPConnection('127.0.0.1',self.server.server_port,timeout=5)
            c.request('PUT','/hue-go/state',body='{"loxone_rgb":<v>}',headers={**auth,'Content-Type':'application/json'})
            response=c.getresponse();self.assertEqual(response.status,400);response.read();c.close()
            self.assertTrue(monitor.snapshot()['events'][-1]['body_detail'].startswith('invalid_json:'))
            write.assert_not_called()

    def test_framing_lengths_extra_bytes_and_partial_body(self):
        import http.client
        monitor.start()
        payload=b'{"loxone_rgb":100100100}'
        def send(raw,length,eof=False):
            c=http.client.HTTPConnection('127.0.0.1',self.server.server_port,timeout=6)
            c.request('PUT','/hue-go/state',body=raw,headers={'Authorization':'Bearer '+'t'*48,'Content-Type':'application/json','Content-Length':str(length)})
            if eof:
                import socket
                c.sock.shutdown(socket.SHUT_WR)
            r=c.getresponse();status=r.status;r.read();c.close()
            return status,monitor.snapshot()['events'][-1]
        with patch('app.write_state',return_value={'status':'accepted'}) as write:
            status,event=send(payload,len(payload));self.assertEqual(status,200)
            self.assertEqual(event['framing']['read_bytes'],len(payload));self.assertTrue(event['framing']['json_complete'])
            status,event=send(b'\r\n'+payload,len(payload));self.assertEqual(status,400)
            f=event['framing'];self.assertEqual(f['leading_cr'],1);self.assertEqual(f['leading_lf'],1)
            self.assertEqual(f['extra_bytes'],2);self.assertTrue(f['json_complete_with_extra']);self.assertFalse(f['ends_with_object_close'])
            status,event=send(payload[:-1],len(payload)-1);self.assertEqual(status,400)
            self.assertEqual(event['framing']['extra_bytes'],0);self.assertFalse(event['framing']['json_complete_with_extra'])
            status,event=send(payload[:-3],len(payload),True);self.assertEqual(status,400)
            self.assertEqual(event['framing']['read_bytes'],len(payload)-3);self.assertEqual(event['framing']['read_error'],'eof')
            write.assert_called_once()
        self.assertNotIn('t'*48,json.dumps(monitor.snapshot()))
