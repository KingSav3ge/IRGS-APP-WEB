"""App consumer of the published Engine starting contract; synthetic saves only."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from server import Store, make_server

HENRY='HYW-HENRY-V'
JOHN='HYW-JOHN-BEDFORD'
OPENING='henry-1415-embarkation-v1'
SCHEMA='irgs-start-readiness-1'
AXIS='selected-historical-observation-seconds'


class StartContextAdoptionTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='irgs-start-adoption-')
        self.store=Store(self.tmp.name)
        self.server=make_server(0,self.tmp.name)
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start()
        self.url='http://127.0.0.1:'+str(self.server.server_port)
        self.token=self.call('/api/campaigns')['token']
        snapshot=self.call('/api/historical-entry/hyw-1415')
        self.base={'profile_id':'military','scenario_id':'hundred-years-war','entry_id':'hyw-1415',
                   'snapshot_sha256':snapshot['snapshot_sha256']}
        self.options=self.call('/api/starting-options?'+urlencode(self.base))
        self.common={**self.base,'selection_digest':self.options['selection_digest'],'starting_scenario_id':'individual'}

    def tearDown(self):
        self.server.shutdown();self.server.server_close();self.thread.join();self.tmp.cleanup()

    def call(self,path,body=None):
        headers={'Content-Type':'application/json'}
        if hasattr(self,'token'):headers['X-IRGS-Token']=self.token
        request=Request(self.url+path,data=None if body is None else json.dumps(body).encode(),headers=headers)
        with urlopen(request,timeout=15) as response:return json.load(response)

    def preview(self,actor=HENRY,opening=OPENING):
        fields={**self.common,'character_kind':'existing','actor_id':actor}
        if opening:fields['opening_id']=opening
        return self.call('/api/starting-preview?'+urlencode(fields))

    def create(self,actor=HENRY,opening=OPENING,request='explicit-henry'):
        character={'kind':'existing','actor_id':actor}
        if opening:character['opening_id']=opening
        body={**self.common,'name':'Actual selected person','character':character,'request_id':request}
        return self.call('/api/create',body),body

    def view(self,key,actor=None):
        return self.call('/api/playthrough/'+key+('?' + urlencode({'actor_id':actor}) if actor else ''))

    def observe(self,record,request='selected-observation'):
        view=self.view(record['id'])
        choice=next(row for row in view['supported_actions'] if row['action_id']=='observe-embarkation')
        body={'id':record['id'],'actor':HENRY,'revision':view['revision'],'kind':'scene_action',
              'action_id':choice['action_id'],'text':choice['text'],'request_id':request}
        return self.call('/api/action',body),body

    def test_review_is_versioned_explicit_and_bound_to_the_selected_person(self):
        self.assertEqual(self.options['start_readiness']['schema_version'],SCHEMA)
        self.assertEqual([(row['actor_id'],row['id']) for row in self.options['existing_character_openings']],[(HENRY,OPENING)])
        ready=self.preview()
        self.assertEqual(ready['engine_start_context_contract'],SCHEMA)
        self.assertEqual(ready['engine_review']['schema_version'],SCHEMA)
        self.assertEqual(ready['engine_review']['selected_mode']['mode_id'],OPENING)
        self.assertEqual(ready['start_context']['actor_id'],HENRY)
        self.assertEqual(ready['status'],'supported_slice')
        self.assertEqual(ready['action_titles'],['Observe the embarkation setting'])
        self.assertEqual(ready['scene']['scope'],'sourced_setting_with_selected_simulation_observation_rule')
        self.assertEqual(ready['elapsed_time'],{'axis':AXIS,'seconds':0})
        for actor in (HENRY,JOHN):
            default=self.preview(actor,None)
            self.assertEqual(default['status'],'declaration_only')
            self.assertEqual(default['action_count'],0)
            self.assertIsNone(default['scene']['location'])
            self.assertIsNone(default['elapsed_time'])
        self.assertEqual(self.store.listing(),[])

    def test_first_view_has_only_received_context_civil_day_and_one_selected_attempt(self):
        record,body=self.create();view=self.view(record['id'])
        state=self.store.read(record['id'])['state']
        self.assertEqual(state['gameplay_started']['existing_character_opening']['id'],OPENING)
        self.assertFalse(state['gameplay_started']['existing_character_opening']['fictional'])
        self.assertEqual(view['start_context']['schema_version'],SCHEMA)
        self.assertEqual(view['start_context']['selected_start']['selected_mode']['mode_id'],OPENING)
        self.assertEqual(view['scene']['scope'],'sourced_setting_with_selected_simulation_observation_rule')
        self.assertEqual(view['scene']['location'],'portchester-solent-embarkation')
        self.assertIn('exact place',view['scene']['description'])
        self.assertEqual(view['elapsed_time'],{'axis':AXIS,'seconds':0})
        self.assertEqual(view['campaign_time']['day'],0)
        civil=view['campaign_time']['civil']
        self.assertEqual(civil['date'],'1415-08-11');self.assertEqual(civil['calendar'],'julian')
        self.assertEqual(civil['precision'],'day');self.assertIsNone(civil['time']);self.assertIsNone(civil['opening_hour'])
        self.assertEqual(civil['status'],'received_initial_checkpoint');self.assertFalse(civil['current_calendar_binding'])
        self.assertEqual(civil['source_ref'],'historical-opening:'+self.base['snapshot_sha256']+':opening')
        self.assertEqual([a['id'] for a in view['known_actors']],[HENRY])
        self.assertEqual(view['inventory'],[]);self.assertEqual(view['orders'],[])
        for key in ('stocks','capacities','obligations','orders'):self.assertEqual(state[key],{})
        self.assertEqual(set(state['actors'][HENRY]['current']),{'location'})
        prompt=next(block['text'] for block in view['opening']['blocks'] if block['kind']=='first_decision')
        self.assertIn('Observe the embarkation setting',prompt)
        for absent in ('dispatch','deliver','move','travel'):self.assertNotIn(absent,prompt.lower())
        text=json.dumps(view)
        for facts in state['historical_start']['snapshot']['domains'].values():
            for fact in facts:self.assertNotIn(fact['statement'],text)
        for absent in ('entity_registry_template','historical_planning','institutional_mandate_granted'):
            self.assertNotIn(absent,text)

    def test_native_observation_has_actual_axis_and_exact_original_result_after_retry(self):
        record,creation=self.create();initial=self.view(record['id'])
        result,body=self.observe(record)
        self.assertEqual(result['status'],'completed_successfully')
        self.assertEqual(result['elapsed_time'],{'axis':AXIS,'duration_seconds':20,'total_seconds':20})
        raw=self.store.path(record['id']).read_bytes()
        self.assertEqual(self.call('/api/action',body),result)
        self.assertEqual(self.call('/api/action-result/'+record['id']+'/'+body['request_id']+'?actor_id='+HENRY),result)
        self.assertEqual(self.call('/api/create',creation)['id'],record['id'])
        current=self.view(record['id'])
        self.assertEqual(current['elapsed_time'],{'axis':AXIS,'seconds':20})
        self.assertEqual(current['completed_actions'][-1],result)
        self.assertEqual(current['campaign_time'],initial['campaign_time'])
        self.assertEqual(current['inventory'],[])
        self.assertEqual(self.store.path(record['id']).read_bytes(),raw)
        with self.assertRaises(HTTPError) as error:self.call('/api/action',{**body,'text':'Changed intention'})
        self.assertEqual(error.exception.code,400)
        for path in ('/api/playthrough/'+record['id']+'?actor_id='+JOHN,
                     '/api/action-result/'+record['id']+'/'+body['request_id']+'?actor_id='+JOHN):
            with self.subTest(path=path),self.assertRaises(HTTPError) as error:self.call(path)
            self.assertEqual(error.exception.code,403)
        self.assertEqual(self.store.path(record['id']).read_bytes(),raw)

    def test_other_people_and_new_characters_cannot_borrow_a_different_context(self):
        for actor,opening in ((JOHN,OPENING),(HENRY,'quay-delivery-v1'),('absent',OPENING)):
            with self.subTest(actor=actor),self.assertRaises(HTTPError) as error:self.preview(actor,opening)
            self.assertEqual(error.exception.code,400)
        for fields in ({'character_kind':'new','species':'human','opening_id':OPENING},
                       {'character_kind':'existing','actor_id':HENRY,'opening_id':OPENING,'entry_id':'hyw-1360'}):
            with self.subTest(fields=fields),self.assertRaises(HTTPError):
                self.call('/api/starting-preview?'+urlencode({**self.common,**fields}))
        self.assertEqual(self.store.listing(),[])

    def test_absent_pack_blocks_new_review_but_existing_state_and_receipts_remain_readable(self):
        record,_=self.create();receipt,body=self.observe(record)
        raw=self.store.path(record['id']).read_bytes()
        with patch('start_readiness.PACK',Path(self.tmp.name)/'not-present.json'):
            with self.assertRaises(HTTPError) as error:self.preview()
            self.assertEqual(error.exception.code,503)
            self.assertIn('starting source',json.load(error.exception)['error'])
            self.assertEqual(self.view(record['id'])['elapsed_time']['seconds'],20)
            self.assertEqual(self.call('/api/action',body),receipt)
        self.assertEqual(len(self.store.listing()),1)
        self.assertEqual(self.store.path(record['id']).read_bytes(),raw)

    def test_views_reload_and_restore_never_call_initializers_or_change_saved_bytes(self):
        record,_=self.create();receipt,body=self.observe(record)
        raw=self.store.path(record['id']).read_bytes()
        with patch('start_readiness.initialize_context',side_effect=AssertionError('No context reseed')),\
             patch('scene_setup.initialize_opening',side_effect=AssertionError('No opening reseed')),\
             patch('historical_campaigns.prepare_opening',side_effect=AssertionError('No template read')):
            for _ in range(2):self.assertEqual(self.view(record['id'])['completed_actions'][-1],receipt)
            self.assertEqual(self.store.path(record['id']).read_bytes(),raw)
            revision=self.store.read(record['id'])['revision']
            self.call('/api/delete',{'id':record['id'],'revision':revision})
            self.call('/api/restore',{'id':record['id'],'revision':revision})
            self.assertEqual(self.view(record['id'])['elapsed_time']['seconds'],20)
            self.assertEqual(self.call('/api/action',body),receipt)
        self.assertEqual(self.store.path(record['id']).read_bytes(),raw)

    def test_diverged_location_and_calendar_are_not_replaced_from_opening_metadata(self):
        record,_=self.create();saved=self.store.read(record['id']);state=saved['state']
        state['actors'][HENRY]['current']['location']['value']='Changed during this synthetic continuation'
        state['campaign_time']['civil']['date']='1420-01-01'
        self.store.write(saved);before=self.store.path(record['id']).read_bytes()
        view=self.view(record['id'])
        self.assertEqual(view['scene']['location'],'Changed during this synthetic continuation')
        self.assertEqual(view['supported_actions'],[]);self.assertIsNone(view['elapsed_time'])
        self.assertEqual(view['start_context']['current_mode'],'declaration_only')
        self.assertEqual(view['campaign_time']['civil']['date'],'1415-08-11')
        self.assertEqual(self.store.path(record['id']).read_bytes(),before)

    def test_unreceived_initial_date_remains_unknown_despite_template_and_saved_civil_fields(self):
        record,_=self.create();saved=self.store.read(record['id'])
        del saved['state']['knowledge'][HENRY]['setup:civil-date']
        self.store.write(saved);before=self.store.path(record['id']).read_bytes()
        view=self.view(record['id'])
        self.assertIsNone(view['start_context']['civil_time'])
        self.assertNotIn('civil',view['campaign_time'])
        self.assertEqual(self.store.path(record['id']).read_bytes(),before)


if __name__=='__main__':unittest.main()
