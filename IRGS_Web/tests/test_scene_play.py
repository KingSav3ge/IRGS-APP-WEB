"""Actual create -> play -> failed attempt -> delivery -> reload, synthetic saves."""
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
from urllib.parse import urlencode
from urllib.request import Request, urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from server import Store, make_server
from gameplay_views import playthrough


class ScenePlayTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1])
        self.addCleanup(self.tmp.cleanup)
        self.store = Store(self.tmp.name)
        self.server = make_server(0, self.tmp.name)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.close)
        self.url = f'http://127.0.0.1:{self.server.server_port}'
        self.token = self.call('/api/campaigns')['token']
        preview = self.call('/api/historical-entry/hyw-1415')
        self.selection = {'profile_id': 'military', 'scenario_id': 'hundred-years-war',
                          'entry_id': 'hyw-1415', 'snapshot_sha256': preview['snapshot_sha256']}
        self.options = self.call('/api/starting-options?' + urlencode(self.selection))

    def close(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()

    def call(self, path, data=None):
        headers = {'Content-Type': 'application/json'}
        if hasattr(self, 'token'):
            headers['X-IRGS-Token'] = self.token
        request = Request(self.url + path,
            data=None if data is None else json.dumps(data).encode(), headers=headers)
        with urlopen(request, timeout=20) as response:
            return json.load(response)

    def create(self, *, opening='quay-delivery-v1', **character_changes):
        character = {'kind': 'new', 'name': 'Synthetic courier', 'species': 'human', 'background': ''}
        if opening is not None:
            character['opening_id'] = opening
        character.update(character_changes)
        result = self.call('/api/create', {**self.selection, 'name': 'Synthetic local delivery',
            'request_id': 'synthetic-create-' + str(len(self.store.listing())),
            'selection_digest': self.options['selection_digest'], 'character': character})
        self.key = result['id']
        return self.view()

    def view(self):
        return self.call('/api/playthrough/' + self.key)

    def body(self, action_id, request_id=None):
        view = self.view()
        choice = next(row for row in view['supported_actions'] if row.get('action_id') == action_id)
        return {'id': self.key, 'revision': view['revision'], 'actor': view['actor_id'],
                'request_id': request_id or 'action-' + str(view['revision']),
                'kind': 'scene_action', 'action_id': action_id, 'text': choice['text']}

    def act(self, action_id, request_id=None):
        return self.call('/api/action', self.body(action_id, request_id))

    def raw(self):
        return self.store.path(self.key).read_bytes()

    def reject(self, body):
        before = self.raw()
        with self.assertRaises(HTTPError) as failure:
            self.call('/api/action', body)
        self.assertEqual(failure.exception.code, 400)
        self.assertEqual(self.raw(), before)

    def test_review_is_explicit_and_default_start_stays_unplaced(self):
        opening = self.options['playable_openings'][0]
        self.assertTrue(opening['fictional'])
        self.assertIn('fiction', opening['review'])
        self.assertIn('seconds', opening['scope'])
        view = self.create(opening=None)
        state = self.store.read(self.key)['state']
        self.assertNotIn('scene_rules', state)
        self.assertEqual(state['stocks'], {})
        self.assertIsNone(view['scene']['location'])
        self.assertEqual(view['supported_actions'], [])

    def test_setup_does_not_assign_historical_actors_scene_or_resources(self):
        view = self.create()
        state = self.store.read(self.key)['state']
        self.assertEqual(state['stocks'][view['actor_id']]['sealed_dispatch'], 1)
        self.assertEqual(state['opening_stock']['sealed_dispatch'], 1)
        for key, actor in state['actors'].items():
            if key != view['actor_id']:
                self.assertEqual(actor['current'], {})
                self.assertNotIn(key, state['stocks'])
        self.assertEqual(state['elapsed_time']['seconds'], 0)
        self.assertFalse(view['capabilities']['action_resolution'])

    def test_actual_play_arc_conserves_dispatch_and_can_continue_after_delivery(self):
        view = self.create()
        actor = view['actor_id']
        original_time = copy.deepcopy(self.store.read(self.key)['state']['campaign_time'])
        look = self.act('look-quay')
        self.assertEqual(look['status'], 'completed_successfully')
        gate = self.act('quay-shortcut')
        self.assertEqual(gate['status'], 'completed_unsuccessfully')
        self.assertEqual(self.view()['scene']['location'], 'quay')
        self.assertEqual(self.store.read(self.key)['state']['elapsed_time']['seconds'], 50)
        self.act('quay-passage')
        self.assertEqual(self.view()['scene']['location'], 'passage')
        self.act('passage-desk')
        self.act('look-desk')
        delivered = self.act('deliver-dispatch')
        self.assertEqual(delivered['status'], 'completed_successfully')
        state = self.store.read(self.key)['state']
        self.assertEqual(state['stocks'][actor]['sealed_dispatch'], 0)
        self.assertEqual(state['stocks']['clerk-tray']['sealed_dispatch'], 1)
        self.assertEqual(sum(stock.get('sealed_dispatch', 0) for stock in state['stocks'].values()), 1)
        self.assertEqual(state['elapsed_time']['seconds'], 170)
        self.assertEqual(state['campaign_time'], original_time)
        self.assertEqual(state['historical_start']['date'], '1415-08-11')
        self.assertEqual(len(self.view()['completed_actions']), 6)
        self.assertIsNone(self.view()['pending_declaration'])
        self.act('desk-passage')
        self.assertEqual(self.view()['scene']['location'], 'passage')

    def test_lost_ack_and_restarted_store_return_original_without_new_observation(self):
        self.create()
        body = self.body('look-quay', 'original-observation')
        result = self.call('/api/action', body)
        before = self.raw()
        restarted = Store(self.tmp.name)
        self.assertEqual(restarted.supported_action(body), result)
        self.assertEqual(self.call('/api/action-result/' + self.key + '/original-observation?actor_id=' + body['actor']), result)
        self.assertEqual(self.raw(), before)
        self.assertEqual(self.store.read(self.key)['state']['elapsed_time']['seconds'], 20)
        self.act('look-quay', 'new-observation')
        self.assertEqual(self.store.read(self.key)['state']['elapsed_time']['seconds'], 40)

    def test_failed_completed_attempt_has_durable_receipt_and_same_retry_no_cost(self):
        self.create()
        body = self.body('quay-shortcut')
        result = self.call('/api/action', body)
        before = self.raw()
        self.assertEqual(self.call('/api/action', body), result)
        self.assertEqual(self.raw(), before)
        self.assertEqual(result['status'], 'completed_unsuccessfully')
        self.assertEqual(result['elapsed_time']['total_seconds'], 30)

    def test_changed_action_text_kind_parameters_or_stale_new_identity_cannot_execute(self):
        self.create()
        body = self.body('look-quay')
        for changes in ({'text': 'Do not look; move instead.'}, {'action_id': 'deliver-dispatch'},
                        {'order_id': 'unrelated'}, {'duration_seconds': 0}, {'kind': 'combat'}):
            with self.subTest(changes=changes):
                self.reject({**body, **changes})
        self.call('/api/action', body)
        self.reject({**body, 'request_id': 'stale-new'})
        self.reject({**body, 'text': 'changed accepted identity'})

    def test_persistence_failure_rolls_back_elapsed_location_and_request_then_retry_works(self):
        self.create()
        body = self.body('quay-passage')
        before = self.raw()
        with patch.object(Store, 'write', side_effect=OSError('synthetic unavailable store')):
            with self.assertRaises(HTTPError) as failure:
                self.call('/api/action', body)
            self.assertEqual(failure.exception.code, 503)
        self.assertEqual(self.raw(), before)
        self.assertEqual(self.call('/api/action', body)['status'], 'completed_successfully')
        self.assertEqual(self.store.read(self.key)['state']['elapsed_time']['seconds'], 45)

    def test_concurrent_duplicate_commits_one_movement(self):
        self.create()
        body = self.body('quay-passage')
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda _: self.call('/api/action', body), range(2)))
        self.assertEqual(results[0], results[1])
        record = self.store.read(self.key)
        self.assertEqual(record['revision'], 1)
        self.assertEqual(record['state']['elapsed_time']['seconds'], 45)

    def test_hidden_gate_condition_does_not_filter_menu_or_leak_to_views(self):
        self.create()
        view = self.view()
        original_options = copy.deepcopy(view['supported_actions'])
        record = self.store.read(self.key)
        record['state']['site_conditions']['quay-gate']['passable'] = True
        self.store.write(record)
        self.assertEqual(self.view()['supported_actions'], original_options)
        public = json.dumps(self.view())
        for hidden in ('site_conditions', 'blocked_by', 'scene_rules', 'validation_reads'):
            self.assertNotIn(hidden, public)
        result = self.act('quay-shortcut')
        self.assertEqual(result['status'], 'completed_successfully')
        self.assertEqual(self.view()['scene']['location'], 'desk')

    def test_current_world_control_is_rechecked_and_rejected_attempt_has_no_elapsed_effect(self):
        view = self.create()
        body = self.body('look-quay')
        record = self.store.read(self.key)
        eligibility = record['state']['entity_registry']['eligibility']['individual:' + view['actor_id']]
        eligibility['versions'][-1]['eligible'] = False
        self.store.write(record)
        self.reject(body)
        self.assertEqual(self.store.read(self.key)['state']['elapsed_time']['seconds'], 0)

    def test_freeform_stays_exact_unresolved_intent_and_blocks_structured_actions(self):
        view = self.create()
        body = self.body('look-quay')
        text = 'I negotiate my fee, then sail for France.'
        result = self.call('/api/declaration', {'id': self.key, 'revision': view['revision'],
            'actor': view['actor_id'], 'request_id': 'own-words', 'declaration': text})
        self.assertEqual(result['status'], 'declared_not_resolved')
        self.assertEqual(self.view()['supported_actions'], [])
        self.reject({**body, 'revision': result['revision']})
        self.assertEqual(self.store.read(self.key)['state']['elapsed_time']['seconds'], 0)

    def test_unavailable_opening_or_nonhuman_does_not_create_campaign(self):
        for changes in ({'opening': 'unselected-pack'}, {'species': 'horse'}):
            with self.subTest(changes=changes), self.assertRaises(HTTPError):
                self.create(**changes)
            self.assertEqual(self.store.listing(), [])

    def test_capitalized_human_starts_the_reviewed_opening(self):
        view = self.create(species='Human')
        self.assertEqual(view['character']['species'], 'Human')
        self.assertEqual(view['scene']['location'], 'quay')
        self.assertTrue(view['capabilities']['playable_opening'])
        self.assertTrue(view['supported_actions'])
        self.assertEqual(len(self.store.listing()), 1)


if __name__ == '__main__':
    unittest.main()
