"""Player payload privacy and durable declaration transport over one world."""
import copy
import json
import sys
import tempfile
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from urllib.parse import urlencode

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from server import Store, make_server
from gameplay_views import playthrough


class GameplayTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1])
        self.store=Store(self.tmp.name)
        self.record=self.store.create('Player campaign')
        state=self.record['state']
        state['actors']['private']={'id':'private','name':'HIDDEN_NPC','species':'human',
                                     'current':{'plans':'HIDDEN_CURRENT'}}
        state['campaign_time']['phase']='HIDDEN_GLOBAL_PHASE'
        state['evidence']['secret']={'subject':'private','assertion':'HIDDEN_EVIDENCE',
            'status':'established','recorded_at':0,'source_ref':'HIDDEN_PROVENANCE'}
        state['evidence']['received']={'subject':'AST-08','assertion':'A received report',
            'status':'testimony','recorded_at':0,'source_ref':'HIDDEN_SOURCE_NOT_RECEIVED'}
        state['knowledge']['AST-01']={'received':{'received_at':0,'source_ref':'explicit-receipt'}}
        state['orders']['hidden']={'recipient':'private','content':'HIDDEN_ORDER','received_at':0,
            'executed':False,'source_ref':'secret','authority_ref':'secret'}
        state['orders']['received']={'recipient':'AST-01','content':'A received order','received_at':0,
            'executed':False,'source_ref':'secret','authority_ref':'secret','directives':{'hidden':'HIDDEN_DIRECTIVE'}}
        state['stocks']={'AST-01':{'HIDDEN_STOCK':7}}
        state['opening_stock']={'HIDDEN_STOCK':7}
        state['obligations']['secret-offer']={'subject':'AST-01','description':'HIDDEN_OFFER','status':'offered'}
        state['registry']['private_policy']='HIDDEN_REGISTRY_POLICY'
        state['r9']={'requests':{'private-request':{'status':'unresolved','reason':'HIDDEN_REASON',
            'original':{'id':'private-request','at':0,'op':'record_design','params':{'name':'HIDDEN_REQUEST'}}}},
            'decisions':{},'mandates':{},'frontiers':[]}
        self.store.write(self.record)
        self.server=make_server(0,self.tmp.name)
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True)
        self.thread.start()
        self.url=f'http://127.0.0.1:{self.server.server_port}'
        self.token=self.call('/api/campaigns')['token']

    def tearDown(self):
        self.server.shutdown();self.server.server_close();self.thread.join();self.tmp.cleanup()

    def call(self,path,data=None,*,token=True,headers=None):
        request_headers={'Content-Type':'application/json'}
        if token and hasattr(self,'token'):request_headers['X-IRGS-Token']=self.token
        request_headers.update(headers or {})
        request=Request(self.url+path,data=None if data is None else json.dumps(data).encode(),headers=request_headers)
        with urlopen(request,timeout=15) as response:return json.load(response)

    def declaration(self,request_id='decl-1',**changes):
        return {**{'id':self.record['id'],'revision':self.record['revision'],'request_id':request_id,
                   'actor':'AST-01','declaration':'  I ask a question.\nI wait.  '},**changes}

    def test_default_payload_and_chronicle_contain_no_private_records(self):
        before=self.store.path(self.record['id']).read_bytes()
        projection=self.call('/api/playthrough/'+self.record['id'])
        history=self.call('/api/chronicle/'+self.record['id'])
        for payload in (projection,history):
            self.assertNotIn('HIDDEN_',json.dumps(payload))
            self.assertNotIn('private-request',json.dumps(payload))
        self.assertNotIn('state',projection)
        self.assertNotIn('clock',projection)
        self.assertEqual({a['id'] for a in projection['known_actors']},{'AST-01','AST-08'})
        self.assertEqual(projection['inventory'],[])
        self.assertEqual(len(projection['evidence']),1)
        self.assertEqual(len(projection['orders']),1)
        self.assertFalse(projection['capabilities']['narrator'])
        self.assertFalse(projection['capabilities']['time_advance'])
        self.assertEqual(self.store.path(self.record['id']).read_bytes(),before)
        self.assertNotIn('gameplay_requests',self.store.read(self.record['id']))

    def test_creator_requires_explicit_mode_and_token(self):
        for path,token in (('/api/campaign/'+self.record['id'],True),
                           ('/api/campaign/'+self.record['id']+'?mode=creator',False),
                           ('/api/binding/'+self.record['id'],True),
                           ('/api/playthrough/'+self.record['id']+'?mode=creator',False)):
            with self.subTest(path=path,token=token),self.assertRaises(HTTPError) as err:
                self.call(path,token=token)
            self.assertEqual(err.exception.code,403)
        creator=self.call('/api/playthrough/'+self.record['id']+'?mode=creator')
        self.assertEqual(creator['mode'],'creator')
        self.assertIn('HIDDEN_NPC',json.dumps(creator))
        self.assertIn('state',creator)
        self.assertFalse(creator['capabilities']['action_resolution'])

    def test_actor_impersonation_and_session_boundaries_fail_without_writes(self):
        before=self.store.path(self.record['id']).read_bytes()
        for actor in ('private','AST-08','nonexistent'):
            with self.assertRaises(HTTPError) as err:
                self.call('/api/playthrough/'+self.record['id']+'?actor_id='+actor)
            self.assertEqual(err.exception.code,403)
            with self.assertRaises(HTTPError):self.call('/api/declaration',self.declaration(actor=actor))
        for headers in ({'Host':'attacker.example'},{'Origin':'https://example.com'}):
            with self.assertRaises(HTTPError) as err:
                self.call('/api/playthrough/'+self.record['id'],headers=headers)
            self.assertEqual(err.exception.code,403)
        with self.assertRaises(HTTPError):self.call('/api/playthrough/'+self.record['id'],token=False)
        self.assertEqual(self.store.path(self.record['id']).read_bytes(),before)

    def test_legacy_editor_endpoints_are_not_player_backdoors(self):
        before=self.store.path(self.record['id']).read_bytes()
        for endpoint in ('event','events','frontier','mandate','resolve','fork'):
            with self.assertRaises(HTTPError) as err:self.call('/api/'+endpoint,{'id':self.record['id']})
            self.assertEqual(err.exception.code,403)
        self.assertEqual(self.store.path(self.record['id']).read_bytes(),before)

    def test_new_create_and_restore_default_to_safe_summaries(self):
        entry=self.call('/api/historical-entry/hyw-1415')
        fields={'profile_id':'military','scenario_id':'hundred-years-war','entry_id':'hyw-1415','snapshot_sha256':entry['snapshot_sha256']}
        options=self.call('/api/starting-options?'+urlencode(fields))
        created=self.call('/api/create',{'name':'Safe default',**fields,'selection_digest':options['selection_digest'],
            'character':{'kind':'new','name':'Safe player','species':'human','background':''}})
        self.assertEqual(set(created),{'id','name','revision'})
        self.call('/api/delete',{'id':created['id'],'revision':created['revision']})
        restored=self.call('/api/restore',{'id':created['id'],'revision':created['revision']})
        self.assertEqual(restored,created)

    def test_no_pc_projection_does_not_choose_a_character(self):
        record=copy.deepcopy(self.record)
        record['state']['player_actor_ids']=[]
        self.store.write(record)
        projection=self.call('/api/playthrough/'+record['id'])
        self.assertTrue(projection['requires_character'])
        self.assertIsNone(projection['character'])
        self.assertEqual(projection['known_actors'],[])
        self.assertEqual(projection['chronicle'],[])
        self.assertFalse(projection['capabilities']['can_declare'])
        with self.assertRaises(HTTPError):self.call('/api/declaration',self.declaration())

    def test_only_explicit_current_inventory_rights_expose_quantities(self):
        record=copy.deepcopy(self.record)
        record['state']['gameplay_visibility']={'AST-01':{'inventory':[{
            'location':'AST-01','material':'HIDDEN_STOCK','active':True,'received_at':0,
            'access':'inspect_current','source_ref':'selected-inventory-inspection'}]}}
        self.store.write(record)
        projection=self.call('/api/playthrough/'+record['id'])
        self.assertEqual(projection['inventory'][0]['quantity'],7)
        self.assertEqual(projection['inventory'][0]['ownership'],'not_inferred')
        record['state']['gameplay_visibility']['AST-01']['inventory'][0]['active']=False
        self.store.write(record)
        self.assertEqual(self.call('/api/playthrough/'+record['id'])['inventory'],[])

    def test_lost_ack_replay_is_exact_and_text_preserves_no_outcomes(self):
        request=self.declaration()
        original_state=copy.deepcopy(self.record['state'])
        result=self.call('/api/declaration',request)
        self.assertEqual(result['declaration'],request['declaration'])
        self.assertEqual(result['status'],'declared_not_resolved')
        self.assertIsNone(result['narrative']);self.assertIsNone(result['elapsed_time'])
        raw=self.store.path(self.record['id']).read_bytes()
        self.assertEqual(self.call('/api/action-result/'+self.record['id']+'/decl-1'),result)
        self.assertEqual(self.call('/api/declaration',request),result)
        self.assertEqual(self.store.path(self.record['id']).read_bytes(),raw)
        saved=self.store.read(self.record['id'])
        for field in ('actors','stocks','campaign_time','orders'):
            self.assertEqual(saved['state'][field],original_state[field])
        self.assertEqual(len(saved['state']['player_actions']),1)
        self.assertNotIn('HIDDEN_',json.dumps(result))
        pending=self.call('/api/playthrough/'+self.record['id'])
        self.assertEqual(pending['pending_declaration'],result)
        self.assertFalse(pending['capabilities']['can_declare'])

    def test_changed_payload_stale_revision_and_pending_queue_are_rejected(self):
        result=self.call('/api/declaration',self.declaration())
        raw=self.store.path(self.record['id']).read_bytes()
        for request in (self.declaration(declaration='Different intent'),self.declaration('new-stale'),
                        self.declaration('new-pending',revision=result['revision'])):
            with self.assertRaises(HTTPError):self.call('/api/declaration',request)
        self.assertEqual(self.store.path(self.record['id']).read_bytes(),raw)

    def test_withdrawal_is_durable_idempotent_and_does_not_erase_history(self):
        declared=self.call('/api/declaration',self.declaration())
        state_before=copy.deepcopy(self.store.read(self.record['id'])['state'])
        withdrawal={'id':self.record['id'],'revision':declared['revision'],'request_id':'withdraw-1',
                    'actor':'AST-01','action_request_id':'decl-1'}
        result=self.call('/api/withdraw-declaration',withdrawal)
        self.assertEqual(result['status'],'withdrawn')
        raw=self.store.path(self.record['id']).read_bytes()
        self.assertEqual(self.call('/api/withdraw-declaration',withdrawal),result)
        self.assertEqual(self.call('/api/action-result/'+self.record['id']+'/withdraw-1'),result)
        self.assertEqual(self.call('/api/action-result/'+self.record['id']+'/decl-1')['status'],'withdrawn')
        self.assertEqual(self.store.read(self.record['id'])['state'],state_before)
        self.assertEqual(self.store.path(self.record['id']).read_bytes(),raw)
        projection=self.call('/api/playthrough/'+self.record['id'])
        self.assertIsNone(projection['pending_declaration'])
        self.assertTrue(projection['capabilities']['can_declare'])
        self.assertIn('withdrawn_not_executed',{e['status'] for e in projection['chronicle']})
        newer=self.call('/api/declaration',self.declaration('decl-2',revision=result['revision'],declaration='A revised attempt'))
        self.assertEqual(newer['status'],'declared_not_resolved')

    def test_fork_cannot_replay_or_retrieve_another_campaign_receipt(self):
        self.call('/api/declaration',self.declaration())
        original=self.store.path(self.record['id']).read_bytes()
        branch=self.call('/api/fork',{'id':self.record['id'],'mode':'creator'})
        with self.assertRaises(HTTPError):self.call('/api/action-result/'+branch['id']+'/decl-1')
        with self.assertRaises(HTTPError):self.call('/api/declaration',self.declaration(id=branch['id'],revision=branch['revision']))
        self.assertEqual(self.store.path(self.record['id']).read_bytes(),original)
        self.assertIsNone(self.call('/api/playthrough/'+branch['id'])['pending_declaration'])

    def test_time_advance_and_failed_persistence_have_no_effects(self):
        before=self.store.path(self.record['id']).read_bytes()
        with self.assertRaises(HTTPError) as err:
            self.call('/api/time-advance',{'id':self.record['id'],'actor':'AST-01','duration':'one year'})
        self.assertEqual(err.exception.code,422)
        with patch.object(Store,'write',side_effect=OSError('save unavailable')):
            with self.assertRaises(OSError):self.store.gameplay_request(self.declaration())
        self.assertEqual(self.store.path(self.record['id']).read_bytes(),before)

    def test_simultaneous_retries_commit_one_declaration(self):
        request=self.declaration('concurrent')
        with ThreadPoolExecutor(max_workers=2) as pool:
            results=list(pool.map(lambda _:self.call('/api/declaration',request),range(2)))
        self.assertEqual(results[0],results[1])
        self.assertEqual(len(self.store.read(self.record['id'])['state']['player_actions']),1)


if __name__=='__main__':unittest.main()
