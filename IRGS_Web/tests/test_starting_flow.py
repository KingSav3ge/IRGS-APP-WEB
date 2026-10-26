"""A reviewed player selection is complete before the first game save exists."""
import json
import sys
import tempfile
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from start_context_assertions import assert_initial_calendar
from server import Store, make_server
from campaign_library import initial_campaign


class StartingFlowTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1])
        self.store = Store(self.tmp.name)
        self.server = make_server(0, self.tmp.name)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.url = f'http://127.0.0.1:{self.server.server_port}'
        self.token = self.call('/api/campaigns')['token']

    def tearDown(self):
        self.server.shutdown(); self.server.server_close(); self.thread.join(); self.tmp.cleanup()

    def call(self, path, data=None, *, token=True, creator=False, headers=None):
        # Generic profiles in these fixtures are internal Creator templates.
        if path == '/api/create' and data is not None and not data.get('scenario_id'):
            creator = True
        if creator:
            if data is None: path += ('&' if '?' in path else '?') + 'mode=creator'
            else: data = {**data, 'mode': 'creator'}
        request_headers = {'Content-Type': 'application/json'}
        if token and hasattr(self, 'token'): request_headers['X-IRGS-Token'] = self.token
        request_headers.update(headers or {})
        request = Request(self.url + path, data=None if data is None else json.dumps(data).encode(), headers=request_headers)
        with urlopen(request, timeout=15) as response: return json.load(response)

    def options(self, **fields):
        return self.call('/api/starting-options?' + urlencode(fields))

    def request(self, *, profile_id='military', character=None, **fields):
        preview_fields = {key: fields[key] for key in ('scenario_id', 'entry_id', 'snapshot_sha256', 'starting_scenario_id') if key in fields}
        options = self.options(profile_id=profile_id, **preview_fields)
        return {'name': 'Reviewed game', 'profile_id': profile_id,
                'character': character or {'kind': 'new', 'name': 'Test player', 'species': 'human', 'background': ''},
                'selection_digest': options['selection_digest'], **fields}

    def historical(self):
        preview = self.call('/api/historical-entry/hyw-1415')
        return {'profile_id': 'military', 'scenario_id': 'hundred-years-war', 'entry_id': 'hyw-1415',
                'snapshot_sha256': preview['snapshot_sha256']}

    def event(self, record, op, **params):
        return self.call('/api/event', {'id': record['id'], 'revision': record['revision'], 'op': op,
            'params': {'source_ref': 'explicit-test-event', **params}}, creator=True)

    def test_missing_or_invalid_character_leaves_no_save(self):
        for payload in ({'name': 'Missing PC', 'profile_id': 'military'},
                        self.request(character={'kind': 'existing', 'actor_id': 'not-present'}),
                        self.request(character={'kind': 'new', 'name': '', 'species': 'human'})):
            with self.subTest(payload=payload), self.assertRaises(HTTPError): self.call('/api/create', payload)
            self.assertEqual(self.store.listing(), [])
            self.assertEqual(list(Path(self.tmp.name).glob('*.tmp')), [])

    def test_exact_background_is_own_testimony_without_invented_assets(self):
        text = '  I say I own a castle.\nThis is my account, not an inventory.  '
        request = self.request(character={'kind': 'new', 'name': 'Mara', 'species': 'human', 'background': text})
        result = self.call('/api/create', request)
        record = self.store.read(result['id']); state = record['state']; pc = state['player_actor_ids'][0]
        self.assertEqual(len(state['actors']), 1)
        self.assertEqual(state['actors'][pc]['name'], 'Mara')
        self.assertEqual(state['evidence']['setup:background']['assertion'], text)
        self.assertEqual(state['evidence']['setup:background']['status'], 'testimony')
        self.assertEqual(set(state['knowledge']), {pc})
        self.assertEqual(set(state['knowledge'][pc]), {'setup:background'})
        for key in ('stocks', 'capacities', 'activities', 'orders'): self.assertEqual(state[key], {})
        self.assertEqual(state['campaign_time']['day'], 0)
        self.assertEqual(state['starting_control']['powers'], ['declare_own_intent'])
        self.assertFalse(state['starting_control']['institutional_mandate_granted'])
        projection = self.call('/api/playthrough/' + result['id'])
        self.assertEqual(projection['evidence'][0]['assertion'], text)
        self.assertEqual(projection['inventory'], [])
        self.assertNotIn('entity_registry', projection)

    def test_review_digest_and_scenario_are_validated_before_writing(self):
        request = self.request()
        for changes in ({'selection_digest': 'stale'}, {'starting_scenario_id': 'national'},
                        {'profile_id': 'fantasy'}, {'selection_digest': None}):
            with self.subTest(changes=changes), self.assertRaises(HTTPError):
                self.call('/api/create', {**request, **changes})
            self.assertEqual(self.store.listing(), [])

    def test_canonical_ast_default_is_existing_ian_and_reads_do_not_migrate(self):
        created = self.call('/api/create', {'name': 'Canonical AST'})
        state = self.store.read(created['id'])['state']
        self.assertEqual(state['player_actor_ids'], ['AST-01'])
        self.assertEqual(state['gameplay_started']['actor_id'], 'AST-01')
        self.assertEqual(state['campaign_time'], initial_campaign('ast', 'TIME-REFERENCE').s['campaign_time'])
        before = self.store.path(created['id']).read_bytes()
        self.call('/api/availability/' + created['id'])
        self.call('/api/starting-options')
        self.assertEqual(self.store.path(created['id']).read_bytes(), before)

    def test_historical_review_has_only_five_configured_existing_characters(self):
        fields = self.historical(); options = self.options(**fields)
        self.assertEqual(len(options['characters']), 5)
        self.assertEqual(len(options['factions']), 5)
        self.assertEqual(sum(row['eligible'] for row in options['characters']), 5)
        chosen = options['characters'][0]['id']
        request = self.request(**fields, character={'kind': 'existing', 'actor_id': chosen})
        created = self.call('/api/create', request)
        record = self.store.read(created['id'])
        self.assertEqual(record['state']['player_actor_ids'], [chosen])
        self.assertEqual(len(record['state']['actors']), 5)
        assert_initial_calendar(self,record['state'],chosen,snapshot_sha256=fields['snapshot_sha256'])
        for key in ('stocks','orders','capacities','obligations'):
            self.assertEqual(record['state'][key],{})
        player = self.call('/api/playthrough/' + created['id'])
        self.assertEqual([actor['id'] for actor in player['known_actors']], [chosen])
        self.assertNotIn('historical_start', json.dumps(player))
        self.assertEqual(len(self.call('/api/availability/' + created['id'])['characters']), 1)
        newer = self.call('/api/create', self.request(**fields))
        newer_state = self.store.read(newer['id'])['state']
        self.assertEqual(len(newer_state['actors']), 6)
        self.assertEqual(len(newer_state['player_actor_ids']), 1)

    def test_custom_date_no_matching_snapshot_is_unavailable_without_fallback(self):
        fields = self.historical()
        result = self.options(**fields, custom_year=1416)
        self.assertFalse(result['available'])
        self.assertNotIn('selection_digest', result)
        result = self.options(profile_id='military', custom_year=1415)
        self.assertFalse(result['available'])
        self.assertEqual(self.store.listing(), [])

    def test_starting_and_live_availability_require_session_and_preserve_bytes(self):
        created = self.call('/api/create', self.request())
        before = self.store.path(created['id']).read_bytes()
        for path in ('/api/starting-options', '/api/availability/' + created['id']):
            for options in ({'token': False}, {'headers': {'Origin': 'https://example.com'}},
                            {'headers': {'Host': 'attacker.example'}}):
                with self.subTest(path=path, options=options), self.assertRaises(HTTPError) as err:
                    self.call(path, **options)
                self.assertEqual(err.exception.code, 403)
        self.assertEqual(self.store.path(created['id']).read_bytes(), before)

    def test_legacy_registry_absence_remains_unavailable_and_never_hydrates(self):
        created = self.call('/api/create', {'name': 'Legacy AST'})
        record = self.store.read(created['id']); record['state'].pop('entity_registry')
        self.store.write(record); before = self.store.path(created['id']).read_bytes()
        result = self.call('/api/availability/' + created['id'])
        self.assertFalse(result['available']); self.assertEqual(result['characters'], [])
        self.assertEqual(self.store.path(created['id']).read_bytes(), before)
        self.assertTrue(self.call('/api/playthrough/' + created['id'])['capabilities']['can_declare'])

    def test_live_player_availability_omits_internal_identity_and_policy_prose(self):
        created = self.call('/api/create', self.request()); record = self.store.read(created['id'])
        registry = record['state']['entity_registry']; pc = record['state']['player_actor_ids'][0]
        registry['entities'][pc]['versions'][-1]['identity']['private_note'] = 'HIDDEN_IDENTITY_NOTE'
        registry['eligibility']['individual:' + pc]['versions'][-1]['reason'] = 'HIDDEN_POLICY_REASON'
        self.store.write(record); raw = self.store.path(created['id']).read_bytes()
        player = self.call('/api/availability/' + created['id'])
        creator = self.call('/api/availability/' + created['id'], creator=True)
        self.assertNotIn('HIDDEN_', json.dumps(player))
        self.assertIn('HIDDEN_POLICY_REASON', json.dumps(creator))
        self.assertEqual(self.store.path(created['id']).read_bytes(), raw)

    def test_divergent_live_registry_uses_committed_records_not_historical_template(self):
        fields = self.historical(); created = self.call('/api/create', self.request(**fields))
        record = self.store.read(created['id']); point = record['state']['entity_registry']['as_of']
        before = self.call('/api/availability/' + created['id'], creator=True)
        dissolved = before['factions'][0]['id']
        record = self.event(record, 'transition_entity', entity_id=dissolved, exists=False, effective_at=point)
        record = self.event(record, 'register_actor', actor_id='LIVE-NEW', name='Live arrival', species='human')
        current = self.call('/api/availability/' + created['id'], creator=True)
        self.assertEqual(current['as_of'], point)
        self.assertNotIn(dissolved, {row['id'] for row in current['factions']})
        self.assertIn('LIVE-NEW', {row['id'] for row in current['characters']})
        player = self.call('/api/availability/' + created['id'])
        self.assertNotIn('LIVE-NEW', json.dumps(player)); self.assertEqual(player['factions'], [])
        self.assertNotIn('control', json.dumps(player)); self.assertNotIn('total', player)
        raw = self.store.path(created['id']).read_bytes()
        with self.assertRaises(HTTPError): self.call('/api/availability/' + created['id'] + '?at=' + str(point))
        self.assertEqual(self.store.path(created['id']).read_bytes(), raw)

    def test_character_death_retains_history_without_automatic_successor(self):
        created = self.call('/api/create', self.request()); record = self.store.read(created['id'])
        pc = record['state']['player_actor_ids'][0]
        request = {'id': record['id'], 'revision': record['revision'], 'request_id': 'prior-intent', 'actor': pc,
                   'declaration': 'I wait here.'}
        receipt = self.call('/api/declaration', request)
        record = self.store.read(created['id']); point = record['state']['entity_registry']['as_of']
        record = self.event(record, 'transition_entity', entity_id=pc, exists=False, effective_at=point)
        raw = self.store.path(created['id']).read_bytes()
        projection = self.call('/api/playthrough/' + created['id'])
        self.assertEqual(projection['actor_id'], pc); self.assertEqual(projection['character']['id'], pc)
        self.assertFalse(projection['character_available']); self.assertFalse(projection['capabilities']['can_declare'])
        self.assertEqual(record['state']['player_actor_ids'], [pc])
        self.assertEqual(self.call('/api/declaration', request), receipt)
        self.assertEqual(self.call('/api/action-result/' + created['id'] + '/prior-intent'), receipt)
        with self.assertRaises(HTTPError) as err:
            self.call('/api/declaration', {**request, 'request_id': 'after-death', 'revision': record['revision']})
        self.assertEqual(err.exception.code, 403)
        self.assertEqual(self.store.path(created['id']).read_bytes(), raw)

    def test_creation_lost_ack_replays_before_source_validation_and_rejects_changed_choice(self):
        request = self.request(request_id='stable-start-request')
        created = self.call('/api/create', request); raw = self.store.path(created['id']).read_bytes()
        with patch('server.initial_campaign', side_effect=AssertionError('must not rebuild accepted game')):
            replay = self.call('/api/create', request)
        self.assertEqual(replay['id'], created['id']); self.assertTrue(replay['creation_replayed'])
        self.assertEqual(replay['status'], 'active')
        self.assertEqual(len(self.store.listing()), 1)
        with self.assertRaises(HTTPError): self.call('/api/create', {**request, 'name': 'Different exact choice'})
        self.assertEqual(self.store.path(created['id']).read_bytes(), raw)
        self.assertNotIn('state', replay)

    def test_creation_retry_does_not_resurrect_trashed_game(self):
        request = self.request(request_id='stable-trash-request'); created = self.call('/api/create', request)
        raw = self.store.path(created['id']).read_bytes()
        self.call('/api/delete', {'id': created['id'], 'revision': created['revision']})
        replay = self.call('/api/create', request)
        self.assertEqual(replay['status'], 'trashed'); self.assertTrue(replay['creation_replayed'])
        self.assertFalse(self.store.path(created['id']).exists())
        self.assertEqual(self.store.trash_path(created['id']).read_bytes(), raw)
        self.assertEqual(self.store.listing(), [])

    def test_simultaneous_create_retries_persist_one_complete_game(self):
        request = self.request(request_id='simultaneous-final-review')
        with ThreadPoolExecutor(max_workers=2) as pool:
            responses = list(pool.map(lambda _: self.call('/api/create', request), range(2)))
        self.assertEqual(responses[0]['id'], responses[1]['id'])
        self.assertEqual(len(self.store.listing()), 1)
        record = self.store.read(responses[0]['id'])
        self.assertEqual(len(record['state']['player_actor_ids']), 1)
        self.assertTrue(record['state']['gameplay_started'])
        self.assertEqual(sum(response.get('creation_replayed') is True for response in responses), 1)

    def test_unacknowledged_creation_write_failure_can_retry_without_empty_game(self):
        request = self.request(request_id='retry-failed-persistence')
        with patch('server.Store.write', side_effect=OSError('fixture persistence unavailable')):
            with self.assertRaises(HTTPError) as err: self.call('/api/create', request)
        self.assertEqual(err.exception.code, 503); self.assertEqual(self.store.listing(), [])
        created = self.call('/api/create', request)
        self.assertEqual(len(self.store.listing()), 1)
        self.assertTrue(self.store.read(created['id'])['state']['player_actor_ids'])


if __name__ == '__main__': unittest.main()
