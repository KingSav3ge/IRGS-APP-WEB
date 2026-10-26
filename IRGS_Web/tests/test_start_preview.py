"""Current actor capabilities, empty stores and explicitly reviewed creation."""
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


class StartReadinessTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='irgs-readiness-')
        self.store = Store(self.tmp.name)
        self.server = make_server(0, self.tmp.name)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.url = 'http://127.0.0.1:' + str(self.server.server_port)
        self.token = self.call('/api/campaigns')['token']
        entry = self.call('/api/historical-entry/hyw-1415')
        self.base = {'profile_id': 'military', 'scenario_id': 'hundred-years-war',
                     'entry_id': 'hyw-1415', 'snapshot_sha256': entry['snapshot_sha256']}
        self.options = self.call('/api/starting-options?' + urlencode(self.base))
        self.query = {**self.base, 'selection_digest': self.options['selection_digest'],
                      'starting_scenario_id': 'individual', 'character_kind': 'new', 'species': 'human'}

    def tearDown(self):
        self.server.shutdown(); self.server.server_close(); self.thread.join(); self.tmp.cleanup()

    def call(self, path, body=None, *, token=True, headers=None):
        fields = {'Content-Type': 'application/json', **({'X-IRGS-Token': self.token} if token and hasattr(self, 'token') else {})}
        fields.update(headers or {})
        with urlopen(Request(self.url + path, headers=fields,
                            data=None if body is None else json.dumps(body).encode()), timeout=15) as response:
            return json.load(response)

    def preview(self, fields=None, **options):
        return self.call('/api/starting-preview?' + urlencode(fields or self.query), **options)

    def create(self, character, request_id='reviewed-start'):
        return self.call('/api/create', {**self.base, 'name': 'Readiness fixture', 'character': character,
            'starting_scenario_id': 'individual', 'selection_digest': self.options['selection_digest'],
            'request_id': request_id})

    def opening(self):
        return self.options['playable_openings'][0]['id']

    def test_existing_john_is_honest_reference_and_receives_no_courier_setup(self):
        john = next(row for row in self.options['characters'] if row['name'] == 'John of Lancaster')
        query = {key: value for key, value in self.query.items() if key not in ('character_kind', 'species')}
        first = self.preview({**query, 'character_kind': 'existing', 'actor_id': john['id']})
        self.assertEqual(first['status'], 'declaration_only')
        self.assertEqual((first['action_count'], first['process_start_count']), (0, 0))
        self.assertIsNone(first['scene']['location'])
        self.assertEqual(self.store.listing(), [])
        saved = self.create({'kind': 'existing', 'actor_id': john['id']})
        view = self.call('/api/playthrough/' + saved['id'])
        self.assertEqual(view['character']['id'], john['id'])
        self.assertEqual(view['scene'], first['scene'])
        self.assertEqual(view['play_readiness']['status'], 'declaration_only')
        self.assertEqual(view['supported_actions'], [])
        self.assertEqual(view['inventory'], [])
        self.assertNotIn('scene_rules', self.store.read(saved['id'])['state'])
        self.assertNotIn('state', first)
        self.assertNotIn('entity_registry_template', json.dumps(first))

    def test_new_default_retains_unestablished_context_and_explicit_scope(self):
        first = self.preview()
        self.assertEqual(first['status'], 'declaration_only')
        self.assertFalse(first['engine_start_context_contract'])
        self.assertFalse(first['general_freeform_resolution'])
        self.assertIsNone(first['elapsed_time'])
        saved = self.create({'kind': 'new', 'name': 'Explicit reference', 'species': 'human', 'background': ''})
        view = self.call('/api/playthrough/' + saved['id'])
        self.assertEqual(view['scene'], first['scene'])
        self.assertEqual(view['campaign_time'], first['campaign_time'])
        self.assertNotIn('Listed actions remain available', view['assistance']['message'])

    def test_authored_preflight_matches_first_view_and_retained_actual_receipt(self):
        first = self.preview({**self.query, 'opening_id': self.opening()})
        self.assertEqual(first['status'], 'supported_slice')
        self.assertGreater(first['action_count'], 0)
        self.assertGreater(first['process_start_count'], 0)
        self.assertEqual(self.store.listing(), [])
        character = {'kind': 'new', 'name': 'Reviewed human', 'species': 'human',
                     'background': '', 'opening_id': self.opening()}
        saved = self.create(character)
        before = self.store.path(saved['id']).read_bytes()
        self.assertEqual(self.preview({**self.query, 'opening_id': self.opening()}), first)
        self.assertEqual(self.store.path(saved['id']).read_bytes(), before)
        view = self.call('/api/playthrough/' + saved['id'])
        self.assertEqual(view['scene'], first['scene'])
        self.assertEqual(view['campaign_time'], first['campaign_time'])
        self.assertEqual(view['elapsed_time'], first['elapsed_time'])
        self.assertEqual(view['play_readiness']['action_titles'], first['action_titles'])
        self.assertEqual(len(view['process_control']['start_options']), first['process_start_count'])
        action = next(a for a in view['supported_actions'] if a['action_id'] == 'look-quay')
        body = {'id': saved['id'], 'revision': view['revision'], 'actor': view['actor_id'],
                'kind': 'scene_action', 'action_id': action['action_id'], 'text': action['text'],
                'request_id': 'explicit-observation'}
        receipt = self.call('/api/action', body)
        self.assertEqual(receipt['status'], 'completed_successfully')
        self.assertEqual(self.call('/api/action', body), receipt)
        again = self.call('/api/playthrough/' + saved['id'])
        self.assertEqual(again['completed_actions'][-1], receipt)
        self.assertEqual(again['elapsed_time']['seconds'], 20)
        self.assertEqual(self.create(character)['id'], saved['id'])
        self.assertEqual(len(self.store.listing()), 1)

    def test_invalid_choices_and_source_failures_create_no_campaign(self):
        cases = [{**self.query, 'opening_id': self.opening(), 'species': 'elf'},
                 {**self.query, 'opening_id': 'invented'}, {**self.query, 'selection_digest': '0' * 64},
                 {**self.query, 'snapshot_sha256': '0' * 64}, {**self.query, 'world': '{}'},
                 {**{key: value for key, value in self.query.items() if key != 'species'},
                  'character_kind': 'existing', 'actor_id': 'hidden-or-absent'},
                 {**self.query, 'character_kind': 'existing', 'actor_id': 'hidden-or-absent', 'opening_id': self.opening()}]
        for query in cases:
            with self.subTest(query=query), self.assertRaises(HTTPError) as error:
                self.preview(query)
            self.assertIn(error.exception.code, (400, 403))
        with patch('start_preview.initial_campaign', side_effect=OSError('source offline')):
            with self.assertRaises(HTTPError) as error:
                self.preview()
            self.assertEqual(error.exception.code, 503)
        self.assertEqual(self.store.listing(), [])

    def test_preflight_requires_session_origin_and_exact_unique_fields(self):
        for options in ({'token': False}, {'headers': {'Origin': 'https://elsewhere.invalid'}}):
            with self.subTest(options=options), self.assertRaises(HTTPError) as error:
                self.preview(**options)
            self.assertEqual(error.exception.code, 403)
        with self.assertRaises(HTTPError) as error:
            self.call('/api/starting-preview?' + urlencode(self.query) + '&species=elf')
        self.assertEqual(error.exception.code, 400)
        self.assertEqual(self.store.listing(), [])


if __name__ == '__main__':
    unittest.main()
