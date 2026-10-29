import json
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from urllib.parse import urlencode
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from start_context_assertions import assert_initial_calendar
from server import make_server, Store
from ast_runtime import initial_ast


class HostTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1])
        self.server = make_server(0, self.tmp.name)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.url = f'http://127.0.0.1:{self.server.server_port}'
        self.token = self.call('/api/campaigns')['token']

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()
        self.tmp.cleanup()

    def call(self, path, data=None, token=None, *, creator=True):
        if creator:
            if data is not None:data={**data,'mode':'creator'}
            elif path.startswith(('/api/campaign/','/api/binding/')):
                path+=('&' if '?' in path else '?')+'mode=creator'
        headers = {'Content-Type': 'application/json', 'X-IRGS-Token': token or getattr(self, 'token', '')}
        req = Request(self.url+path, data=json.dumps(data).encode() if data is not None else None, headers=headers)
        with urlopen(req) as response:
            return json.load(response)

    def create(self):
        return self.call('/api/create', {'name': 'Test campaign'})

    def test_campaign_artwork_is_static_and_creates_no_campaign(self):
        with urlopen(self.url + '/voyage.svg') as response:
            self.assertEqual(response.headers.get_content_type(), 'image/svg+xml')
            artwork = response.read().decode('utf-8')
        self.assertIn('Illustrative voyage artwork', artwork)
        self.assertNotIn('<script', artwork)
        self.assertEqual(self.call('/api/campaigns')['campaigns'], [])
        with self.assertRaises(HTTPError) as missing:
            urlopen(self.url + '/unlisted-artwork.svg')
        self.assertEqual(missing.exception.code, 404)

    def create_player(self,payload):
        fields={k:payload[k] for k in ('profile_id','scenario_id','entry_id','snapshot_sha256') if payload.get(k) is not None}
        options=self.call('/api/starting-options?'+urlencode(fields))
        return self.call('/api/create',{**payload,'selection_digest':options['selection_digest'],
            'character':{'kind':'new','name':'Test player','species':'human','background':''}})

    def event(self, r, **overrides):
        return self.call('/api/event', {**{'id': r['id'], 'revision': r['revision'], 'op': 'ast_record_player_action',
            'params': {'actor':'AST-01','instruction_ref':'test player','source_ref':'test source','declaration':'Inspect the gate'}}, **overrides})

    def test_event_persists_and_does_not_resolve_outcome(self):
        r = self.create()
        changed = self.event(r)
        saved = Store(self.tmp.name).read(r['id'])
        self.assertEqual(changed, saved)
        self.assertEqual(saved['state']['player_actions'][0]['status'], 'declared_not_resolved')
        self.assertEqual(saved['state']['stocks'], {})
        self.assertEqual(saved['revision'], 1)
        self.assertEqual(self.call('/api/campaign/'+r['id']), saved)
        request = next(iter(saved['state']['r9']['requests'].values()))
        self.assertEqual(request['status'], 'committed')
        self.assertTrue(request['certificate']['reads'])
        self.assertTrue(request['certificate']['writes'])
        self.assertEqual(saved['last_result']['committed'], [request['original']['id']])

    def test_rejected_and_stale_events_preserve_save(self):
        r = self.create()
        with self.assertRaises(HTTPError):
            self.event(r, params={'actor':'AST-01','declaration':'bad'})
        self.assertEqual(Store(self.tmp.name).read(r['id']), r)
        changed = self.event(r)
        with self.assertRaises(HTTPError): self.event(r)
        self.assertEqual(Store(self.tmp.name).read(r['id']), changed)

    def test_branch_is_independent(self):
        original = self.create()
        branch = self.call('/api/fork', {'id': original['id']})
        self.event(branch)
        self.assertEqual(Store(self.tmp.name).read(original['id']), original)
        self.assertNotEqual(original['id'], branch['id'])
        self.assertNotEqual(original['state']['campaign_id'],branch['state']['campaign_id'])
    def test_new_ast_campaigns_have_distinct_scope_before_replay(self):
        first=self.create();second=self.create()
        self.assertNotEqual(first['state']['campaign_id'],second['state']['campaign_id'])
        with self.assertRaises(HTTPError):
            self.event(second,params={'actor':'AST-01','instruction_ref':'test','source_ref':'test','declaration':'A declaration','campaign_id':first['state']['campaign_id']})
        self.assertEqual(Store(self.tmp.name).read(second['id']),second)

    def test_token_origin_host_and_paths(self):
        with self.assertRaises(HTTPError) as err:
            self.call('/api/create', {'name':'bad'}, token='invalid')
        self.assertEqual(err.exception.code, 403)
        for headers in ({'Origin':'https://example.com','X-IRGS-Token':self.token}, {'Host':'attacker.example','X-IRGS-Token':self.token}):
            with self.assertRaises(HTTPError) as err:
                urlopen(Request(self.url+'/api/create',data=b'{"name":"bad"}',headers=headers))
            self.assertEqual(err.exception.code, 403)
        with self.assertRaises(ValueError): Store(self.tmp.name).read('../outside')

    def test_inventory_runs_actual_engine_and_conserves(self):
        r=self.create()
        r=self.event(r,op='ast_establish_stock',params={'source_ref':'test','location':'store','material':'grain','quantity':10,'inventory_evidence_ref':'count'})
        r=self.event(r,op='ast_transfer_stock',params={'source_ref':'test','from':'store','to':'camp','material':'grain','quantity':3,'authority_ref':'host'})
        self.assertEqual(r['state']['stocks'], {'store':{'grain':7},'camp':{'grain':3}})
        with self.assertRaises(HTTPError):
            self.event(r,op='ast_transfer_stock',params={'source_ref':'test','from':'store','to':'camp','material':'grain','quantity':99,'authority_ref':'host'})
        self.assertEqual(Store(self.tmp.name).read(r['id']),r)

    def test_static_entrypoint(self):
        with urlopen(self.url) as r:
            self.assertIn(b'WorldWard',r.read())
            self.assertIn("frame-ancestors 'none'",r.headers['Content-Security-Policy'])

    def test_catalog_separates_core_genres_libraries_and_campaign_profiles(self):
        catalog = self.call('/api/catalog?mode=creator')
        self.assertEqual(str(catalog['core']['version']), '3.3')
        self.assertEqual({p['id'] for p in catalog['campaign_profiles']},
                         {'ast','military','roman','fantasy','paf','shinobi','space'})
        self.assertNotIn('ast', {g['id'] for g in catalog['genre_engines']})
        self.assertIn('ast', {lib['id'] for lib in catalog['content_libraries']})

    def test_player_catalog_contains_core_health_without_technical_engine_choices(self):
        catalog = self.call('/api/catalog', creator=False)
        self.assertEqual(set(catalog), {'core'})
        self.assertEqual(str(catalog['core']['version']), '3.3')
        self.assertTrue(catalog['core']['single_world_per_campaign'])
        self.assertTrue(self.call('/api/content-library', creator=False)['campaigns'])
        with self.assertRaises(HTTPError) as denied:
            self.call('/api/catalog?mode=creator', token='invalid-session')
        self.assertEqual(denied.exception.code, 403)

    def test_content_lookup_preserves_campaign_and_source_status(self):
        r=self.create()
        before=Store(self.tmp.name).path(r['id']).read_bytes()
        result=self.call('/api/content?library=ast&q=Abel&limit=5')
        self.assertFalse(result['lookup_creates_state'])
        self.assertFalse(result['numerical_models_adopted'])
        self.assertTrue(result['source_status'])
        self.assertTrue(result['results'])
        self.assertEqual(Store(self.tmp.name).path(r['id']).read_bytes(),before)
        with self.assertRaises(HTTPError):self.call('/api/content?library=unknown')
        with self.assertRaises(HTTPError):self.call('/api/content?library=ast&limit=1000')

    def test_non_ast_profile_uses_core_world_and_actual_campaign_scope(self):
        r = self.create_player({'name':'Fantasy test','profile_id':'fantasy'})
        self.assertEqual(r['state']['profile'], 'IRGS-CORE-3.3')
        self.assertEqual(r['state']['binding']['campaign_profile'], 'fantasy')
        self.assertEqual(len(r['state']['actors']),1)
        self.assertEqual(len(r['state']['player_actor_ids']),1)
        self.assertNotEqual(r['state']['campaign_id'], 'AST')
        r = self.event(r, op='record_design', params={'design_id':'d','name':'A sourced draft','source_ref':'test'})
        self.assertEqual(r['state']['journal'][-1]['params']['campaign_id'], r['state']['campaign_id'])
        self.assertIn('d',r['state']['designs'])
        with self.assertRaises(HTTPError):
            self.event(r,op='record_design',params={'campaign_id':'AST','design_id':'cross','name':'Bad scope','source_ref':'test'})
        self.assertEqual(Store(self.tmp.name).read(r['id']), r)

    def test_legacy_ast_reads_preserve_exact_file_bytes(self):
        key = 'a'*32
        record = {'id':key,'name':'Existing AST','revision':7,'state':initial_ast().s}
        record['state']['profile']='AST-CORE-3.3'
        for field in ('binding','player_actor_ids','capacities','activities'):
            record['state'].pop(field,None)
        self.assertEqual(record['state']['profile'],'AST-CORE-3.3')
        raw = ('\n' + json.dumps(record,ensure_ascii=False,separators=(',',':')) + '\n\n').encode('utf-8')
        path = Path(self.tmp.name) / (key+'.json')
        path.write_bytes(raw)
        self.assertEqual(self.call('/api/campaign/'+key),record)
        self.assertIn(key,{c['id'] for c in self.call('/api/campaigns')['campaigns']})
        binding=self.call('/api/binding/'+key)
        self.assertEqual(binding['campaign_profile'],'ast')
        self.assertTrue(binding['legacy_profile_alias'])
        self.assertEqual(path.read_bytes(),raw)

    def test_generic_actor_capacity_and_activity_use_shared_records(self):
        r=self.create_player({'name':'Military test','profile_id':'military'})
        r=self.event(r,op='register_actor',params={'actor_id':'worker','name':'Sourced worker','species':'human','source_ref':'test'})
        r=self.event(r,op='record_capacity',params={'capacity_id':'yard','site':'yard','quantity':1,'unit':'concurrent_people','source_ref':'test'})
        start=r['state']['clock']+1
        r=self.event(r,op='commit_activity',params={'activity_id':'task','actors':['worker'],'site':'yard','capacity_id':'yard','start':start,'end':start+3,'role':'guard','authority_ref':'fixture','source_ref':'test'})
        self.assertEqual(r['state']['activities']['task']['actors'],['worker'])
        self.assertEqual(r['state']['actors']['worker']['name'],'Sourced worker')
        self.assertEqual(r['state']['capacities']['yard']['quantity'],1)

    def test_frontier_persists_contention_and_resolves_later_without_duplicate_effects(self):
        r=self.create()
        r=self.event(r,op='establish_stock',params={'source_ref':'count','location':'store','material':'grain','quantity':10,'inventory_evidence_ref':'count'})
        operations=[{'op':'transfer_stock','params':{'source_ref':'fixture','from':'store','to':dst,'material':'grain','quantity':8,'authority_ref':'fixture'}} for dst in ('household','military')]
        r=self.call('/api/frontier',{'id':r['id'],'revision':r['revision'],'events':operations})
        deferred=r['last_result']['deferred']
        self.assertEqual(len(deferred),2)
        self.assertEqual(r['state']['stocks'],{'store':{'grain':10}})
        self.assertEqual(len(r['state']['r9']['requests']),3)
        self.assertTrue(r['last_result']['edges'])
        stale=r
        r=self.call('/api/mandate',{'id':r['id'],'revision':r['revision'],'mandate_id':'m','actor':'AST-07','operations':['transfer_stock'],'source_ref':'explicit fixture authority'})
        with self.assertRaises(HTTPError):
            self.call('/api/resolve',{'id':stale['id'],'revision':stale['revision'],'decision_id':'stale','request_id':deferred[0],'mandate_id':'m','actor':'AST-07','approve':True})
        with self.assertRaises(HTTPError):
            self.call('/api/resolve',{'id':r['id'],'revision':r['revision'],'decision_id':'bad','request_id':deferred[0],'mandate_id':'m','actor':'other','approve':True})
        approved=self.call('/api/resolve',{'id':r['id'],'revision':r['revision'],'decision_id':'approved','request_id':deferred[0],'mandate_id':'m','actor':'AST-07','approve':True})
        self.assertEqual(approved['state']['stocks']['store']['grain'],2)
        self.assertEqual(approved['state']['r9']['requests'][deferred[0]]['status'],'approved_executed')
        at=approved['state']['r9']['decisions']['approved']['payload']['at']
        replay=self.call('/api/resolve',{'id':approved['id'],'revision':approved['revision'],'decision_id':'approved','request_id':deferred[0],'mandate_id':'m','actor':'AST-07','approve':True,'at':at})
        self.assertEqual(replay,approved)
        denied=self.call('/api/resolve',{'id':approved['id'],'revision':approved['revision'],'decision_id':'denied','request_id':deferred[1],'mandate_id':'m','actor':'AST-07','approve':False})
        self.assertEqual(denied['state']['stocks']['store']['grain'],2)
        self.assertEqual(denied['state']['r9']['requests'][deferred[1]]['status'],'denied')
        self.assertEqual(Store(self.tmp.name).read(r['id']),denied)

    def test_invalid_batch_request_is_durable_but_invalid_single_event_is_rejected(self):
        r=self.create()
        params={'source_ref':'fixture','from':'missing','to':'household','material':'grain','quantity':1,'authority_ref':'fixture'}
        with self.assertRaises(HTTPError):self.event(r,op='transfer_stock',params=params)
        self.assertEqual(Store(self.tmp.name).read(r['id']),r)
        pending=self.call('/api/frontier',{'id':r['id'],'revision':r['revision'],'events':[{'op':'transfer_stock','params':params}]})
        self.assertEqual(pending['revision'],1)
        self.assertEqual(len(pending['last_result']['deferred']),1)
        self.assertEqual(pending['state']['stocks'],{})
        request=next(iter(pending['state']['r9']['requests'].values()))
        self.assertEqual(request['status'],'unresolved')
        self.assertEqual(request['original']['params']['from'],'missing')

    def test_delete_and_restore_preserve_exact_save_bytes(self):
        original=self.create()
        branch=self.call('/api/fork',{'id':original['id']})
        branch=self.event(branch)
        store=Store(self.tmp.name)
        path=store.path(branch['id'])
        raw=('\n'+json.dumps(branch,ensure_ascii=False,separators=(',',':'))+'\n\n').encode('utf-8')
        path.write_bytes(raw)
        original_raw=store.path(original['id']).read_bytes()
        deleted=self.call('/api/delete',{'id':branch['id'],'revision':branch['revision']})
        self.assertEqual(deleted['status'],'trashed')
        self.assertFalse(path.exists())
        self.assertEqual(store.trash_path(branch['id']).read_bytes(),raw)
        self.assertNotIn(branch['id'],{r['id'] for r in self.call('/api/campaigns')['campaigns']})
        self.assertEqual(self.call('/api/trash')['campaigns'],[{k:branch[k] for k in ('id','name','revision')}])
        with self.assertRaises(HTTPError) as err:self.call('/api/campaign/'+branch['id'])
        self.assertEqual(err.exception.code,404)
        restored=self.call('/api/restore',{'id':branch['id'],'revision':branch['revision']})
        self.assertEqual(restored,branch)
        self.assertEqual(path.read_bytes(),raw)
        self.assertFalse(store.trash_path(branch['id']).exists())
        self.assertEqual(self.call('/api/trash')['campaigns'],[])
        self.assertIn(branch['id'],{r['id'] for r in self.call('/api/campaigns')['campaigns']})
        self.assertEqual(store.path(original['id']).read_bytes(),original_raw)

    def test_campaign_trash_survives_http_server_restart(self):
        campaign=self.create()
        store=Store(self.tmp.name)
        raw=store.path(campaign['id']).read_bytes()
        self.call('/api/delete',{'id':campaign['id'],'revision':campaign['revision']})
        self.server.shutdown();self.server.server_close();self.thread.join()
        self.server=make_server(0,self.tmp.name)
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True)
        self.thread.start()
        self.url=f'http://127.0.0.1:{self.server.server_port}'
        self.token=self.call('/api/campaigns')['token']
        self.assertEqual(self.call('/api/campaigns')['campaigns'],[])
        self.assertEqual(self.call('/api/trash')['campaigns'][0]['id'],campaign['id'])
        self.call('/api/restore',{'id':campaign['id'],'revision':campaign['revision']})
        self.assertEqual(store.path(campaign['id']).read_bytes(),raw)

    def test_stale_missing_and_invalid_trash_requests_preserve_saves(self):
        campaign=self.create()
        updated=self.event(campaign)
        store=Store(self.tmp.name)
        raw=store.path(campaign['id']).read_bytes()
        with self.assertRaises(HTTPError):
            self.call('/api/delete',{'id':campaign['id'],'revision':campaign['revision']})
        self.assertEqual(store.path(campaign['id']).read_bytes(),raw)
        self.assertEqual(self.call('/api/trash')['campaigns'],[])
        self.call('/api/delete',{'id':updated['id'],'revision':updated['revision']})
        for endpoint,request in (
            ('delete',{'id':updated['id'],'revision':updated['revision']}),
            ('restore',{'id':updated['id'],'revision':0}),
            ('delete',{'id':'b'*32,'revision':0}),
            ('restore',{'id':'b'*32,'revision':0}),
            ('delete',{'id':'../outside','revision':0}),
            ('restore',{'id':'../outside','revision':0})):
            with self.assertRaises(HTTPError):self.call('/api/'+endpoint,request)
        self.assertEqual(store.trash_path(updated['id']).read_bytes(),raw)
        self.assertFalse(store.path(updated['id']).exists())

    def test_restore_collision_preserves_active_and_trashed_campaigns(self):
        campaign=self.create()
        store=Store(self.tmp.name)
        original_raw=store.path(campaign['id']).read_bytes()
        self.call('/api/delete',{'id':campaign['id'],'revision':campaign['revision']})
        collision={**campaign,'name':'Active campaign with the same ID'}
        store.write(collision)
        active_raw=store.path(campaign['id']).read_bytes()
        with self.assertRaises(HTTPError):
            self.call('/api/restore',{'id':campaign['id'],'revision':campaign['revision']})
        self.assertEqual(store.path(campaign['id']).read_bytes(),active_raw)
        self.assertEqual(store.trash_path(campaign['id']).read_bytes(),original_raw)
        with self.assertRaises(HTTPError):
            self.call('/api/delete',{'id':collision['id'],'revision':collision['revision']})
        self.assertEqual(store.path(campaign['id']).read_bytes(),active_raw)
        self.assertEqual(store.trash_path(campaign['id']).read_bytes(),original_raw)

    def test_delete_and_restore_require_local_token_host_and_origin(self):
        campaign=self.create()
        store=Store(self.tmp.name)
        raw=store.path(campaign['id']).read_bytes()
        for endpoint in ('delete','restore'):
            payload={'id':campaign['id'],'revision':campaign['revision']}
            with self.assertRaises(HTTPError) as err:
                self.call('/api/'+endpoint,payload,token='wrong')
            self.assertEqual(err.exception.code,403)
            for headers in ({'Origin':'https://example.com','X-IRGS-Token':self.token},
                            {'Host':'attacker.example','X-IRGS-Token':self.token}):
                with self.assertRaises(HTTPError) as err:
                    urlopen(Request(self.url+'/api/'+endpoint,data=json.dumps(payload).encode(),headers=headers))
                self.assertEqual(err.exception.code,403)
            if endpoint=='delete':
                self.assertEqual(store.path(campaign['id']).read_bytes(),raw)
                self.call('/api/delete',payload)
            else:self.assertEqual(store.trash_path(campaign['id']).read_bytes(),raw)
        with self.assertRaises(HTTPError) as err:
            urlopen(Request(self.url+'/api/trash',headers={'Host':'attacker.example'}))
        self.assertEqual(err.exception.code,403)

    def test_historical_catalogue_and_preview_are_read_only(self):
        existing=self.create()
        store=Store(self.tmp.name)
        raw=store.path(existing['id']).read_bytes()
        catalogue=self.call('/api/historical-campaigns')
        self.assertEqual(len(catalogue['entries']),37)
        self.assertEqual(len(catalogue['featured_years']),10)
        preview=self.call('/api/historical-entry/hyw-1415')
        self.assertTrue(preview['ready'])
        self.assertEqual(preview['snapshot']['opening']['date'],'1415-08-11')
        self.assertTrue(self.call('/api/historical-entry/hyw-1360')['ready'])
        self.assertEqual(store.path(existing['id']).read_bytes(),raw)
        self.assertEqual(len(self.call('/api/campaigns')['campaigns']),1)
        for endpoint in ('/api/historical-campaigns','/api/historical-entry/hyw-1415'):
            with self.assertRaises(HTTPError) as err:
                urlopen(Request(self.url+endpoint,headers={'Host':'attacker.example'}))
            self.assertEqual(err.exception.code,403)

    def test_historical_create_requires_exact_ready_scope_and_preview_hash(self):
        preview=self.call('/api/historical-entry/hyw-1415')
        valid={'name':'Historical opening','profile_id':'military','scenario_id':'hundred-years-war',
               'entry_id':'hyw-1415','snapshot_sha256':preview['snapshot_sha256']}
        options=self.call('/api/starting-options?'+urlencode({k:v for k,v in valid.items() if k!='name'}))
        valid.update(character={'kind':'new','name':'Test player','species':'human','background':''},
                     selection_digest=options['selection_digest'])
        for changes in ({'profile_id':'ast'},{'scenario_id':'other'},{'entry_id':'missing'},
                        {'entry_id':'hyw-1360'},{'snapshot_sha256':'0'*64},{'snapshot_sha256':None},
                        {'entry_id':None}):
            with self.subTest(changes=changes), self.assertRaises(HTTPError):
                self.call('/api/create',{**valid,**changes})
            self.assertEqual(self.call('/api/campaigns')['campaigns'],[])
        campaign=self.call('/api/create',valid)
        state=campaign['state']
        self.assertEqual(state['binding']['campaign_profile'],'military')
        self.assertEqual(state['binding']['snapshot_sha256'],preview['snapshot_sha256'])
        self.assertEqual(state['historical_start']['snapshot'],preview['snapshot'])
        self.assertEqual(state['historical_start']['calendar'],'julian')
        self.assertEqual(len(state['player_actor_ids']),1)
        self.assertEqual(state['campaign_time']['day'],0)
        assert_initial_calendar(self,state,state['player_actor_ids'][0],snapshot_sha256=preview['snapshot_sha256'])
        for field in ('pending','stocks','capacities','player_actions'):
            self.assertFalse(state[field])

    def test_historical_fork_and_scene_preserve_opening_and_original_save(self):
        preview=self.call('/api/historical-entry/hyw-1415')
        original=self.create_player({'name':'Historical original','profile_id':'military',
            'scenario_id':'hundred-years-war','entry_id':'hyw-1415','snapshot_sha256':preview['snapshot_sha256']})
        store=Store(self.tmp.name)
        raw=store.path(original['id']).read_bytes()
        branch=self.call('/api/fork',{'id':original['id']})
        self.assertNotEqual(branch['state']['campaign_id'],original['state']['campaign_id'])
        self.assertEqual(branch['state']['historical_start'],original['state']['historical_start'])
        branch=self.event(branch,op='set_scene',params={'day':1,'time':None,'precision':'unresolved',
            'description':'An explicitly selected scene','source_ref':'test source','instruction_ref':'host request'})
        self.assertEqual(branch['state']['historical_start'],original['state']['historical_start'])
        self.assertEqual(store.path(original['id']).read_bytes(),raw)
        self.assertEqual(branch['state']['player_actor_ids'],original['state']['player_actor_ids'])
        self.assertEqual(self.call('/api/binding/'+branch['id'])['entry_id'],'hyw-1415')


if __name__ == '__main__': unittest.main()
