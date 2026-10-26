"""Real Engine communication through authenticated HTTP and atomic App saves."""
from concurrent.futures import ThreadPoolExecutor
import copy
import json
from pathlib import Path
import sys
import tempfile
import threading
import unittest
import uuid
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request,urlopen

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from server import Store,make_server
from core_world import CoreWorld
from app_communication_fixtures import install,introduce
from test_scene_actions import apply


class CommunicationBridgeTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='irgs-communication-http-')
        self.addCleanup(self.tmp.cleanup)
        self.store=Store(Path(self.tmp.name)/'saves')
        contexts=install(self.store);self.quay=contexts['quay'];self.rise=contexts['rise']
        self.start();self.addCleanup(self.stop)
        guard=patch('solo_provider.CapabilityBroker.dispatch',side_effect=AssertionError('No routine inference'))
        self.dispatch=guard.start();self.addCleanup(guard.stop)

    def start(self):
        self.server=make_server(0,self.store.folder)
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start()
        self.url='http://127.0.0.1:'+str(self.server.server_port)
        self.token=self.http('/api/campaigns',token=False)[1]['token']

    def stop(self):
        self.server.shutdown();self.server.server_close();self.thread.join()

    def http(self,path,body=None,*,token=True,headers=None):
        fields={'X-IRGS-Token':self.token} if token else {}
        fields.update(headers or {})
        if body is not None:fields['Content-Type']='application/json'
        request=Request(self.url+path,data=None if body is None else json.dumps(body).encode(),headers=fields)
        try:
            with urlopen(request,timeout=15) as response:return response.status,json.load(response)
        except HTTPError as error:return error.code,json.load(error)

    def view(self,key=None,actor='pc'):
        code,view=self.http('/api/playthrough/'+(key or self.quay)+'?actor_id='+actor)
        self.assertEqual(code,200,view);return view

    def prepared(self,command='speak',details=None,*,key=None,actor='pc',recipient='witness',text='  Exact words.\nNo silent rewrite.  '):
        key=key or self.quay;view=self.view(key,actor)
        body={'id':key,'actor':actor,'revision':view['revision'],'view_token':view['communication_control']['view_token'],
              'request_id':uuid.uuid4().hex,'channel_id':'quay' if key==self.quay else 'local',
              'recipient':recipient,'command':command,'details':details or {},'intention':text}
        code,packet=self.http('/api/communication/prepare',body)
        self.assertEqual(code,200,packet);return body,packet

    def accepted(self,body,**changes):
        return {'id':body['id'],'actor':body['actor'],'request_id':body['request_id'],'explicitly_accepted':True,**changes}

    def commit(self,*args,**kwargs):
        body,packet=self.prepared(*args,**kwargs)
        code,result=self.http('/api/communication/execute',self.accepted(body))
        self.assertEqual(code,200,result);return body,result

    def terms(self,actor='founder',quantity=2):
        return {'from':actor+'-home','to':'oren-home' if actor=='founder' else 'founder-home',
                'material':'grain','quantity':quantity,'authority_id':actor+'-custody'}

    def offer(self,**changes):
        return self.commit('offer',{'terms':self.terms(**changes)},key=self.rise,actor='founder',recipient='oren')

    def close(self,command,offered,actor='oren'):
        return self.commit(command,{'offer_id':offered['communication']['offer_id'],
            'terms_digest':offered['communication']['terms_digest']},key=self.rise,actor=actor,
            recipient='founder' if actor=='oren' else 'oren',text='Exact '+command+' words.')

    def test_received_view_has_no_hidden_roster_names_feasibility_or_private_pending_data(self):
        before=self.store.path(self.quay).read_bytes();packet=self.view()['communication_control']
        self.assertEqual(packet['schema_version'],'irgs-communication-capabilities-1')
        self.assertEqual([p['actor_id'] for p in packet['channels'][0]['participants']],['witness'])
        source=next(r for r in packet['received_sources']['records'] if r['originator']=='witness')
        self.assertEqual(source['status'],'testimony');self.assertEqual(source['time_axis'],'causal_sequence')
        self.assertEqual(source['text'],'Received attribution from witness. Current presence is not certified.')
        self.assertEqual(source['source_ref'],'synthetic-opening-selection')
        self.assertLess(source['recorded_at'],source['received_at'])
        for private in ('PRIVATE_CHANNEL_ROSTER','PRIVATE_LOCATION','UNRECEIVED_WITNESS_NAME','state_digest','restore_id','params_digest'):
            self.assertNotIn(private,json.dumps(packet))
        self.assertEqual(self.store.path(self.quay).read_bytes(),before)
        self.dispatch.assert_not_called()

    def test_legacy_unattributed_receipt_retains_private_original_provenance(self):
        record=self.store.read(self.quay)
        record['state']['evidence']['legacy']={'subject':'pc','assertion':'Received legacy words',
            'status':'testimony','recorded_at':0,'source_ref':'PRIVATE_ORIGINAL_PROVENANCE',
            'occurrence_time':{'private':'PRIVATE_OCCURRENCE'}}
        record['state']['knowledge']['pc']['legacy']={'received_at':0,'source_ref':'received-copy'}
        self.store.write(record);before=self.store.path(self.quay).read_bytes()
        packet=self.view()['communication_control']
        self.assertEqual(packet['source_projection'],'app-receipt-compatibility-1')
        source=next(row for row in packet['received_sources']['records'] if row['record_id']=='legacy')
        self.assertEqual(source['text'],'Received legacy words')
        self.assertEqual(source['receipt_source_ref'],'received-copy')
        self.assertIsNone(source['source_ref']);self.assertIsNone(source['occurrence_time'])
        self.assertNotIn('PRIVATE_',json.dumps(packet))
        self.assertEqual(self.store.path(self.quay).read_bytes(),before)

    def test_preparation_is_effect_free_immutable_and_needs_boolean_acceptance(self):
        before=self.store.path(self.quay).read_bytes();body,packet=self.prepared()
        self.assertEqual(packet['intention'],body['intention'])
        self.assertEqual(self.http('/api/communication/prepare',body),(200,packet))
        for acceptance in (False,'true',1):self.assertEqual(self.http('/api/communication/execute',self.accepted(body,explicitly_accepted=acceptance))[0],400)
        for changes in ({'intention':'Different words'},{'source_ref':'forged'},{'scope':{}},{'details':{'terms':{}}}):
            self.assertEqual(self.http('/api/communication/prepare',{**body,**changes})[0],400)
        self.assertEqual(self.store.path(self.quay).read_bytes(),before)
        for private in ('state_digest','restore_id','source_ref','params_digest'):
            self.assertNotIn(private,json.dumps(packet))

    def test_non_rise_exact_speech_is_testimony_not_acceptance_or_elapsed_work(self):
        before=copy.deepcopy(self.store.read(self.quay)['state']);words='  I accept.\n<img src=x onerror="window.bad=true"> {literal}  '
        body,result=self.commit(text=words);message=result['communication']
        after=self.store.read(self.quay)['state']
        self.assertEqual(message['utterance'],words);self.assertEqual(message['truth_status'],'testimony')
        self.assertEqual(message['status'],'testimony_received');self.assertEqual(message['elapsed_status'],'not_resolved')
        self.assertIsNone(result['elapsed_time']);self.assertIn(words,result['outcome']['summary'])
        for key in ('stocks','elapsed_time','campaign_time','obligations'):self.assertEqual(after[key],before[key])
        self.assertEqual(after['evidence'][message['evidence_id']]['assertion'],words)
        self.assertEqual(self.view()['completed_actions'][-1],result)
        self.assertEqual(result['presentation']['render_usage'],{'provider_calls':0,'model_tokens':0})

    def test_offer_and_fulfillment_are_distinct_conserved_and_original_proposal_stays_offered(self):
        before=copy.deepcopy(self.store.read(self.rise)['state']['stocks'])
        body,proposal=self.offer()
        self.assertEqual(proposal['communication']['status'],'offered')
        recipient_view=self.view(self.rise,'oren')
        self.assertNotIn('settlement',recipient_view)
        self.assertEqual(recipient_view['inventory'],[])
        self.assertFalse(recipient_view['local_responses']['engine_runtime'])
        self.assertEqual(self.store.read(self.rise)['state']['stocks'],before)
        _,fulfilled=self.close('accept',proposal)
        self.assertEqual(fulfilled['communication']['status'],'fulfilled')
        after=self.store.read(self.rise)['state']['stocks']
        self.assertEqual(after['founder-home']['grain'],before['founder-home']['grain']-2)
        self.assertEqual(after['oren-home']['grain'],before['oren-home']['grain']+2)
        self.assertEqual(self.http('/api/action-result/'+self.rise+'/'+body['request_id']+'?actor_id=founder'),(200,proposal))
        original=self.http('/api/communication/received/'+self.rise+'/'+body['request_id']+'?actor_id=oren')[1]
        self.assertEqual(original['status'],'offered');self.assertEqual(original['terms'],proposal['communication']['terms'])
        status=self.view(self.rise,'oren')['communication_control']['offers'][0]
        self.assertEqual(status['status'],'fulfilled');self.assertEqual(status['supported_commands'],[])

    def test_decline_withdraw_and_counteroffer_preserve_their_separate_terminal_meanings(self):
        initial=copy.deepcopy(self.store.read(self.rise)['state']['stocks'])
        _,first=self.offer();_,declined=self.close('decline',first)
        _,second=self.offer();_,withdrawn=self.close('withdraw',second,'founder')
        _,third=self.offer()
        _,counter=self.commit('counteroffer',{'terms':self.terms('oren',1),'counter_to':third['communication']['offer_id']},
            key=self.rise,actor='oren',recipient='founder',text='I propose different terms, not acceptance.')
        self.assertEqual(declined['communication']['status'],'declined');self.assertEqual(withdrawn['communication']['status'],'withdrawn')
        self.assertEqual(counter['communication']['status'],'offered')
        self.assertEqual(counter['communication']['supersedes'],third['communication']['offer_id'])
        rows=self.view(self.rise,'founder')['communication_control']['offers']
        statuses={r['offer_id']:r for r in rows}
        self.assertEqual(statuses[third['communication']['offer_id']]['status'],'superseded')
        self.assertEqual(statuses[third['communication']['offer_id']]['supported_commands'],[])
        self.assertEqual(self.store.read(self.rise)['state']['stocks'],initial)

    def test_hidden_presence_and_stock_do_not_select_a_winning_menu_and_reject_without_leak(self):
        before=self.view()['communication_control'];body,_=self.prepared()
        record=self.store.read(self.quay);record['state']['actors']['witness']['current']['location']='PRIVATE_REMOTE'
        self.store.write(record)
        visible=self.view()['communication_control']
        self.assertEqual({k:v for k,v in before.items() if k!='view_token'},{k:v for k,v in visible.items() if k!='view_token'})
        self.assertEqual(self.http('/api/communication/execute',self.accepted(body))[0],400)
        fresh,_=self.prepared();raw=self.store.path(self.quay).read_bytes()
        code,error=self.http('/api/communication/execute',self.accepted(fresh))
        self.assertEqual(code,400);self.assertNotIn('PRIVATE_REMOTE',json.dumps(error))
        self.assertEqual(self.store.path(self.quay).read_bytes(),raw)

    def test_failed_save_then_restart_recovery_executes_once_with_original_native_request(self):
        body,prepared=self.prepared();before=self.store.path(self.quay).read_bytes()
        with patch.object(Store,'write',side_effect=OSError('synthetic disk failure')):
            self.assertEqual(self.http('/api/communication/execute',self.accepted(body))[0],503)
        self.assertEqual(self.store.path(self.quay).read_bytes(),before)
        self.stop();self.start()
        code,pending=self.http('/api/communication/status',{'id':self.quay,'actor':'pc','request_id':body['request_id']})
        self.assertEqual(code,200);self.assertEqual(pending['intention'],prepared['intention']);self.assertEqual(pending['status'],'save_failed')
        code,result=self.http('/api/communication/execute',self.accepted(body));self.assertEqual(code,200,result)
        committed=self.store.path(self.quay).read_bytes()
        self.assertEqual(self.http('/api/communication/execute',self.accepted(body)),(200,result))
        self.assertEqual(self.http('/api/communication/status',{'id':self.quay,'actor':'pc','request_id':body['request_id']}),(200,result))
        self.assertEqual(self.store.path(self.quay).read_bytes(),committed)

    def test_directory_sync_uncertainty_is_finished_before_original_result_acknowledgment(self):
        body,_=self.prepared()
        with patch('server.sync_parent',side_effect=OSError('uncertain directory sync')):
            self.assertEqual(self.http('/api/communication/execute',self.accepted(body))[0],503)
        accepted=self.store.read(self.quay)['gameplay_requests'][body['request_id']]['result']
        self.assertEqual(self.http('/api/action-result/'+self.quay+'/'+body['request_id']+'?actor_id=pc'),(200,accepted))
        self.assertEqual(self.http('/api/communication/execute',self.accepted(body)),(200,accepted))

    def test_concurrent_requests_have_one_cas_winner_and_duplicate_retries_one_result(self):
        first,_=self.prepared();second,_=self.prepared()
        with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(lambda body:self.http('/api/communication/execute',self.accepted(body)),[first,second]))
        self.assertEqual(sorted(code for code,_ in results),[200,400])
        winner=first if results[0][0]==200 else second;receipt=next(result for code,result in results if code==200)
        with ThreadPoolExecutor(max_workers=2) as pool:duplicates=list(pool.map(lambda _:self.http('/api/communication/execute',self.accepted(winner)),range(2)))
        self.assertEqual(duplicates,[(200,receipt),(200,receipt)])

    def test_identical_restore_and_older_restore_fence_uncommitted_and_future_requests(self):
        body,_=self.prepared();saved=self.store.path(self.quay).read_bytes()
        revision=self.store.read(self.quay)['revision']
        self.assertEqual(self.http('/api/delete',{'id':self.quay,'revision':revision})[0],200)
        self.assertEqual(self.http('/api/restore',{'id':self.quay,'revision':revision})[0],200)
        self.assertEqual(self.store.path(self.quay).read_bytes(),saved)
        self.assertEqual(self.http('/api/communication/execute',self.accepted(body))[0],400)
        fresh,result=self.commit();future=self.store.path(self.quay).read_bytes()
        self.store.path(self.quay).write_bytes(saved)
        self.http('/api/delete',{'id':self.quay,'revision':revision});self.http('/api/restore',{'id':self.quay,'revision':revision})
        self.assertEqual(self.http('/api/communication/execute',self.accepted(fresh))[0],400)
        self.assertEqual(self.store.path(self.quay).read_bytes(),saved)
        self.assertNotEqual(future,saved)

    def test_actor_authentication_exact_fields_and_received_result_boundary(self):
        body,_=self.prepared()
        self.assertEqual(self.http('/api/communication/prepare',body,token=False)[0],403)
        self.assertEqual(self.http('/api/communication/prepare',body,headers={'Origin':'https://other.invalid'})[0],403)
        for changes in ({'actor':'witness'},{'recipient':'hidden'},{'details':{'source_ref':'private'}}):
            code,_=self.http('/api/communication/prepare',{**body,'request_id':uuid.uuid4().hex,**changes})
            self.assertIn(code,(400,403))
        _,result=self.offer()
        self.assertEqual(self.http('/api/action-result/'+self.rise+'/'+result['request_id']+'?actor_id=oren')[0],403)
        self.assertEqual(self.http('/api/communication/received/'+self.rise+'/'+result['request_id']+'?actor_id=elin')[0],403)

    def test_forwarding_words_does_not_forward_private_terms_original_audience_or_rights(self):
        body,result=self.offer();record=self.store.read(self.rise);world=CoreWorld(state=record['state'])
        apply(world,'forwarded-words','receive_evidence',evidence_id=result['communication']['evidence_id'],recipient='elin')
        introduce(world,'elin','founder')
        record['state']=world.s;record['revision']+=1;self.store.write(record)
        packet=self.view(self.rise,'elin')['communication_control']
        forwarded=next(r for r in packet['received_sources']['records'] if r['record_id']==result['communication']['evidence_id'])
        self.assertEqual(forwarded['text'],body['intention']);self.assertEqual(forwarded['status'],'testimony')
        self.assertEqual(packet['offers'],[])
        for field in ('terms_digest','founder-custody','oren-home'):
            self.assertNotIn(field,json.dumps(packet))
        self.assertEqual(self.http('/api/communication/received/'+self.rise+'/'+body['request_id']+'?actor_id=elin')[0],403)

    def test_no_selected_channel_is_an_honest_empty_view_and_received_sources_stay_read_only(self):
        record=self.store.read(self.quay);del record['state']['communication_rules'];self.store.write(record)
        before=self.store.path(self.quay).read_bytes();packet=self.view()['communication_control']
        self.assertEqual(packet['channels'],[]);self.assertEqual(packet['offers'],[])
        self.assertTrue(packet['received_sources']['records']);self.assertEqual(self.store.path(self.quay).read_bytes(),before)


if __name__=='__main__':unittest.main()
