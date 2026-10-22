"""Campaign discovery, capability metadata and actor-known opening integration."""
import copy
import json
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from server import Store, make_server
from features import FEATURES, content_library, feature_registry
from opening_scene import build_opening


class StageOneTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1])
        self.store = Store(self.tmp.name)
        self.server = make_server(0, self.tmp.name)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True); self.thread.start()
        self.url = f'http://127.0.0.1:{self.server.server_port}'
        self.token = self.call('/api/campaigns')['token']

    def tearDown(self):
        self.server.shutdown(); self.server.server_close(); self.thread.join(); self.tmp.cleanup()

    def call(self, path, data=None, *, creator=False, token=True, headers=None):
        if creator:
            if data is None: path += ('&' if '?' in path else '?') + 'mode=creator'
            else: data = {**data, 'mode': 'creator'}
        request_headers = {'Content-Type': 'application/json'}
        if token and hasattr(self, 'token'): request_headers['X-IRGS-Token'] = self.token
        request_headers.update(headers or {})
        request = Request(self.url + path, data=None if data is None else json.dumps(data).encode(), headers=request_headers)
        with urlopen(request, timeout=15) as response: return json.load(response)

    def reviewed(self, request_id='stage-one-create', background=''):
        entry = self.call('/api/historical-entry/hyw-1415')
        fields = {'profile_id': 'military', 'scenario_id': 'hundred-years-war', 'entry_id': 'hyw-1415',
                  'snapshot_sha256': entry['snapshot_sha256']}
        options = self.call('/api/starting-options?' + urlencode(fields))
        return {'name': 'Stage one fixture', **fields, 'request_id': request_id,
            'selection_digest': options['selection_digest'], 'starting_scenario_id': 'individual',
            'character': {'kind': 'new', 'name': 'Unaffiliated fixture', 'species': 'human', 'background': background}}

    def event(self, record, op, **params):
        return self.call('/api/event', {'id': record['id'], 'revision': record['revision'], 'op': op,
            'params': {'source_ref': 'stage-one-fixture', **params}}, creator=True)

    def test_configured_campaigns_with_exact_verified_entry_and_disabled_references(self):
        library = self.call('/api/content-library')
        self.assertEqual([c['id'] for c in library['campaigns']], ['hundred-years-war', 'world-of-kira', 'rise'])
        campaign = library['campaigns'][0]
        entries = [e for p in campaign['periods'] for e in p['entries']]
        self.assertEqual(len(entries), 37); self.assertEqual(len(campaign['periods']), 3)
        ready = [e for e in entries if e['ready']]
        self.assertEqual(len(ready),37)
        selected=next(e for e in ready if e['id']=='hyw-1415')
        self.assertEqual(selected['snapshot_sha256'], self.call('/api/historical-entry/hyw-1415')['snapshot_sha256'])
        self.assertTrue(all(e['snapshot_sha256'] is None for e in entries if not e['ready']))
        references = [s for s in selected['scenarios'] if s['id'] != 'individual']
        self.assertTrue(all(not s['ready'] and not s['playable'] for s in references))
        self.assertEqual(self.store.listing(), [])

    def test_snapshot_status_alone_does_not_claim_launch_readiness(self):
        with patch('features.historical_entry', return_value={'ready': False, 'snapshot_sha256': None}):
            library = self.call('/api/content-library')
        self.assertEqual(library['campaigns'][0]['playable_entry_count'], 0)
        self.assertTrue(all(not e['ready'] and e['snapshot_sha256'] is None for p in library['campaigns'][0]['periods'] for e in p['entries']))

    def test_every_catalogue_entry_can_start_its_own_reviewed_local_playthrough(self):
        entries=self.call('/api/historical-campaigns')['entries']
        for entry in entries:
            with self.subTest(entry=entry['id']):
                preview=self.call('/api/historical-entry/'+entry['id'])
                origin={'profile_id':'military','scenario_id':'hundred-years-war',
                    'entry_id':entry['id'],'snapshot_sha256':preview['snapshot_sha256']}
                options=self.call('/api/starting-options?'+urlencode(origin))
                character={'kind':'new','name':'Independent local traveller','species':'human',
                    'opening_id':options['playable_openings'][0]['id']}
                payload={**origin,'name':'Synthetic '+entry['id'],'request_id':'all-entries-'+entry['id'],
                    'character':character,'selection_digest':options['selection_digest']}
                created=self.call('/api/create',payload)
                replay=self.call('/api/create',payload)
                self.assertEqual(created['id'],replay['id'])
                saved=self.store.read(created['id'])['state']
                self.assertEqual(saved['historical_start']['entry_id'],entry['id'])
                self.assertEqual(saved['historical_start']['date'],preview['snapshot']['opening']['date'])
                actor=saved['player_actor_ids'][0]
                self.assertEqual(saved['stocks'][actor]['sealed_dispatch'],1)
                self.assertTrue(saved['gameplay_started']['authored_opening']['fictional'])
                self.assertFalse(saved['historical_start']['automatic_future_history'])
                self.assertFalse(saved['historical_planning']['installed_schedule'])
                projection=self.call('/api/playthrough/'+created['id'])
                self.assertEqual(projection['actor_id'],actor)
                self.assertNotIn('historical_start',projection)
        self.assertEqual(len(self.store.listing()),37)

    def test_kira_world_reference_has_map_keys_without_a_launch_or_private_source_dump(self):
        library = self.call('/api/content-library')
        kira = next(c for c in library['campaigns'] if c['id'] == 'world-of-kira')
        self.assertEqual(kira['kind'], 'campaign_world')
        self.assertEqual(kira['periods'], [])
        self.assertEqual(kira['playable_entry_count'], 0)
        self.assertEqual(kira['launch_capability'], 'reference_only')
        world = self.call('/api/campaign-world/world-of-kira')
        self.assertNotIn('records', world)
        self.assertNotIn('continuity_issues', world)
        self.assertNotIn('source_text', world)
        maps = world['guide']['map_catalogues']
        self.assertEqual([len(m['entries']) for m in maps], [66, 32, 11, 0, 0, 0])
        self.assertEqual([e['label'] for e in maps[0]['entries'] if e['printed_number'] == 25], ['Lethar', 'Sarinus'])
        self.assertEqual(self.store.listing(), [])
        self.assertNotIn('200,000', json.dumps(world))

    def test_world_inspection_preserves_saved_playthrough_and_forged_start_cannot_launch(self):
        created = self.call('/api/create', self.reviewed())
        raw = self.store.path(created['id']).read_bytes()
        for _ in range(2):
            self.call('/api/campaign-world/world-of-kira')
            self.call('/api/content-library')
        self.assertEqual(self.store.path(created['id']).read_bytes(), raw)
        with self.assertRaises(HTTPError) as err:
            self.call('/api/create', {**self.reviewed(request_id='forged-kira-start'),
                'profile_id': 'fantasy', 'scenario_id': 'world-of-kira', 'entry_id': 'kira-1342'})
        self.assertEqual(err.exception.code, 403)
        self.assertEqual(len(self.store.listing()), 1)

    def test_unknown_or_malformed_world_reference_is_rejected(self):
        for identity in ('unknown-world', '../source_text.json', 'world-of-kira/../source_text.json'):
            with self.subTest(identity=identity), self.assertRaises(HTTPError) as err:
                self.call('/api/campaign-world/' + identity)
            self.assertEqual(err.exception.code, 400)
        from campaign_worlds import WORLD_FILES
        source = json.loads(WORLD_FILES['world-of-kira'].read_text(encoding='utf-8'))
        source['readiness']['playable'] = True
        invalid = Path(self.tmp.name) / 'invalid-reference.fixture'
        invalid.write_text(json.dumps(source), encoding='utf-8')
        with patch.dict(WORLD_FILES, {'world-of-kira': invalid}), self.assertRaises(HTTPError) as err:
            self.call('/api/campaign-world/world-of-kira')
        self.assertEqual(err.exception.code, 400)
        self.assertEqual(self.store.listing(), [])

    def test_role_scoped_expanded_registry_stage_cannot_grant_privileges(self):
        player = self.call('/api/features?stage=development')
        self.assertTrue(all('player' in f['availableTo'] for f in player['features']))
        ids = {f['id'] for f in player['features']}
        self.assertNotIn('developer', ids); self.assertNotIn('providers-models', ids); self.assertNotIn('workshop', ids)
        creator = self.call('/api/features?stage=development', creator=True)
        self.assertEqual(len(creator['features']), len(FEATURES))
        ids = {f['id'] for f in creator['features']}
        for identity in ('atlas', 'economy', 'politics', 'military', 'settlements', 'institutions', 'civilization',
                         'capability-broker', 'solo-conversion', 'workshop', 'marketplace', 'feature-registry'):
            self.assertIn(identity, ids)
        self.assertEqual(len(ids), len(FEATURES))
        for feature in creator['features']:
            self.assertTrue(feature['parentId'] is None or feature['parentId'] in ids)
            self.assertTrue(set(feature['dependencyIds']) <= ids)
            self.assertEqual(feature['route'], '#/' + feature['id'])
        release = self.call('/api/features?stage=release', creator=True)
        self.assertTrue(all(f['lifecycle'] == 'functional' for f in release['features']))
        self.assertNotIn('solo-conversion', {f['id'] for f in release['features']})
        with self.assertRaises(HTTPError) as err: self.call('/api/features?stage=invalid')
        self.assertEqual(err.exception.code, 400)

    def test_discovery_and_registry_session_host_origin_boundaries(self):
        for path in ('/api/features', '/api/content-library', '/api/campaign-world/world-of-kira'):
            for options in ({'token': False}, {'headers': {'Origin': 'https://example.com'}},
                            {'headers': {'Host': 'attacker.example'}}):
                with self.subTest(path=path, options=options), self.assertRaises(HTTPError) as err: self.call(path, **options)
                self.assertEqual(err.exception.code, 403)
        self.assertEqual(self.store.listing(), [])

    def test_generic_player_create_and_mismatched_entries_rejected_before_save(self):
        valid = self.reviewed()
        for payload in ({'name': 'Unapproved generic', 'profile_id': 'fantasy'},
                        {**valid, 'profile_id': 'roman'}, {**valid, 'entry_id': 'hyw-1360'},
                        {**valid, 'snapshot_sha256': '0'*64}, {**valid, 'scenario_id': None}):
            with self.subTest(payload=payload), self.assertRaises(HTTPError) as err: self.call('/api/create', payload)
            self.assertEqual(err.exception.code, 403)
            self.assertEqual(self.store.listing(), [])
        generic_options = self.call('/api/starting-options?profile_id=fantasy')
        created = self.call('/api/create', {'name': 'Internal template', 'profile_id': 'fantasy',
            'character': valid['character'], 'selection_digest': generic_options['selection_digest']}, creator=True)
        self.assertEqual(created['state']['binding']['campaign_profile'], 'fantasy')

    def test_opening_does_not_disclose_historical_reference_or_fabricate_scene(self):
        created = self.call('/api/create', self.reviewed())
        record = self.store.read(created['id']); state = record['state']
        self.assertEqual(state['knowledge'], {})
        view = self.call('/api/playthrough/' + created['id']); opening = view['opening']
        self.assertEqual(opening['status'], 'awaiting_first_action'); self.assertTrue(opening['presentation_only'])
        self.assertFalse(opening['effects_applied']); self.assertEqual(view['chronicle'], [])
        text = json.dumps(view)
        for facts in state['historical_start']['snapshot']['domains'].values():
            for fact in facts: self.assertNotIn(fact['statement'], text)
        self.assertNotIn('world_hook', text); self.assertNotIn('Known at this date', text)
        self.assertIn('have not been established', opening['blocks'][1]['text'])
        self.assertEqual(state['actors'][view['actor_id']]['current'], {})
        self.assertFalse(view['capabilities']['narrator']); self.assertFalse(view['capabilities']['action_resolution'])
        self.assertNotIn('historical_event_plans', text)

    def test_opening_uses_only_own_received_record_and_never_overrides_later_scene(self):
        created = self.call('/api/create', self.reviewed(background='  My own exact account.  '))
        record = self.store.read(created['id']); pc = record['state']['player_actor_ids'][0]
        opening = self.call('/api/playthrough/' + created['id'])['opening']
        received = next(b for b in opening['blocks'] if b['kind'] == 'received_record')
        self.assertEqual(received['assertion'], '  My own exact account.  ')
        self.assertEqual(received['status'], 'testimony')
        self.assertEqual(received['source_kind'], 'declared_background')
        self.assertTrue(received['text'].startswith('Your declared background (testimony):\n'))
        self.assertFalse(opening['effects_applied'])
        record = self.event(record, 'record_evidence', evidence_id='later-place', subject=pc, status='established', assertion='At the new place')
        record = self.event(record, 'confirm_character_field', subject=pc, field='location', value='A later established place',
                            evidence_id='later-place', authority_ref='actual-fixture', instruction_ref='actual-player')
        record = self.event(record, 'set_scene', day=4, time='09:00', precision='exact', description='HIDDEN_GLOBAL_NOT_OBSERVED', instruction_ref='actual-player')
        view = self.call('/api/playthrough/' + created['id'])
        self.assertEqual(view['scene']['location'], 'A later established place')
        self.assertEqual(view['scene']['title'], 'A later established place')
        self.assertEqual(view['opening'], opening); self.assertNotIn('HIDDEN_GLOBAL_NOT_OBSERVED', json.dumps(view))

    def test_read_reload_create_retry_and_withdrawn_first_attempt_are_exact_once(self):
        request = self.reviewed(); created = self.call('/api/create', request)
        raw = self.store.path(created['id']).read_bytes()
        with patch('server.validate_player_creation', side_effect=PermissionError('changed source or listing')):
            replay = self.call('/api/create', request)
        self.assertTrue(replay['creation_replayed']); self.assertEqual(replay['id'], created['id'])
        view = self.call('/api/playthrough/' + created['id']); self.call('/api/chronicle/' + created['id'])
        self.assertEqual(self.store.path(created['id']).read_bytes(), raw)
        action = {'id': created['id'], 'revision': 0, 'actor': view['actor_id'], 'request_id': 'first', 'declaration': 'I choose to wait.'}
        acknowledgement = self.call('/api/declaration', action)
        self.assertEqual(acknowledgement['status'], 'declared_not_resolved')
        self.assertEqual(self.call('/api/declaration', action), acknowledgement)
        self.call('/api/withdraw-declaration', {'id': created['id'], 'revision': 1, 'actor': view['actor_id'],
            'request_id': 'withdraw-first', 'action_request_id': 'first'})
        after = self.call('/api/playthrough/' + created['id'])
        self.assertEqual(after['opening']['status'], 'first_attempt_withdrawn')
        self.assertTrue(after['capabilities']['can_declare'])
        self.assertEqual(sum(e['kind'] == 'player_declaration' for e in after['chronicle']), 1)

    def test_legacy_reads_do_not_create_opening_or_migrate_and_branch_is_scoped(self):
        record = self.store.create('Existing generic fixture', 'military', character={'kind': 'new', 'name': 'Legacy', 'species': 'human'},
            selection_digest=self.call('/api/starting-options?profile_id=military')['selection_digest'])
        raw = self.store.path(record['id']).read_bytes()
        view = self.call('/api/playthrough/' + record['id']); self.assertIsNone(view['opening'])
        self.assertEqual(self.store.path(record['id']).read_bytes(), raw)
        created = self.call('/api/create', self.reviewed())
        branch = self.call('/api/fork', {'id': created['id']}, creator=True)
        self.assertIsNone(self.call('/api/playthrough/' + branch['id'])['opening'])
        self.assertIsNotNone(self.call('/api/playthrough/' + created['id'])['opening'])

    def test_background_details_require_own_actual_matching_receipt(self):
        created = self.call('/api/create', self.reviewed()); record = self.store.read(created['id']); pc = record['state']['player_actor_ids'][0]
        assertion = json.dumps({'kind': 'character_background', 'schema_version': 1, 'details': {'identity': {'national_origin': 'Declared origin'}}})
        record = self.event(record, 'record_evidence', evidence_id='setup:background-details', subject=pc, status='testimony', assertion=assertion, originator=pc)
        self.assertNotIn('background_details', self.call('/api/playthrough/' + created['id'])['character'])
        record = self.event(record, 'receive_evidence', evidence_id='setup:background-details', recipient=pc)
        view = self.call('/api/playthrough/' + created['id'])
        self.assertEqual(view['character']['background_details']['details']['identity']['national_origin'], 'Declared origin')
        self.assertEqual(view['character']['background_details']['status'], 'testimony')

    def test_historical_comparison_endpoints_are_creator_only_and_read_only(self):
        created = self.call('/api/create', self.reviewed()); raw = self.store.path(created['id']).read_bytes()
        for path in ('/api/historical-baseline', '/api/historical-plans/' + created['id']):
            with self.assertRaises(HTTPError) as err: self.call(path)
            self.assertEqual(err.exception.code, 403)
            self.assertTrue(self.call(path, creator=True))
            with self.assertRaises(HTTPError): self.call(path + '?mode=creator', token=False)
        self.assertEqual(self.store.path(created['id']).read_bytes(), raw)

    def test_fork_rebinds_pinned_historical_reference_without_replaying_history(self):
        from historical_plans import baseline_view, initialize_plans
        created = self.call('/api/create', self.reviewed()); record = self.store.read(created['id'])
        if 'historical_planning' not in record['state']:
            baseline = baseline_view(); plans = initialize_plans(baseline, record['state'])
            plans['baseline_snapshot'] = baseline
            record['state']['historical_planning'] = plans
        collection = record['state']['historical_planning']
        self.assertTrue(collection['plans'])
        collection['plans'][0].update(status='PREVENTED', change_ref='explicit-fixture-review')
        self.store.write(record); raw = self.store.path(record['id']).read_bytes()
        branch = self.call('/api/fork', {'id': record['id']}, creator=True)
        copied = branch['state']['historical_planning']
        self.assertEqual(copied['campaign_id'], branch['state']['campaign_id'])
        self.assertEqual(copied['baseline_snapshot'], collection['baseline_snapshot'])
        self.assertEqual(copied['plans'][0]['status'], 'PREVENTED')
        self.assertTrue(all(p['campaign_id'] == branch['state']['campaign_id'] for p in copied['plans']))
        self.assertEqual(branch['state']['journal'], record['state']['journal'])
        self.assertFalse(self.call('/api/historical-plans/' + branch['id'], creator=True)['execution_available'])
        self.assertNotIn('historical_planning', json.dumps(self.call('/api/playthrough/' + branch['id'])))
        self.assertEqual(self.store.path(record['id']).read_bytes(), raw)


if __name__ == '__main__': unittest.main()
