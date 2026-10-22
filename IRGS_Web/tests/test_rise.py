"""Synthetic Rise HTTP, persistence, information and retry qualification."""
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

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from server import Store, make_server
from rise_campaigns import create, action
from settlement_setup import preview


class RiseTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.store = Store(self.tmp.name)
        self.server = make_server(0, self.tmp.name)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True); self.thread.start()
        self.url = f'http://127.0.0.1:{self.server.server_port}'
        self.token = self.call('/api/campaigns')['token']

    def tearDown(self):
        self.server.shutdown(); self.server.server_close(); self.thread.join(); self.tmp.cleanup()

    def call(self, path, data=None, *, token=True, origin=None):
        headers = {'Content-Type': 'application/json'}
        if token and hasattr(self, 'token'): headers['X-IRGS-Token'] = self.token
        if origin: headers['Origin'] = origin
        request = Request(self.url + path, data=None if data is None else json.dumps(data).encode(), headers=headers)
        with urlopen(request, timeout=15) as response: return json.load(response)

    def setup_payload(self, request='rise-create', **overrides):
        choices = {'template_id': 'R00', 'founder_name': 'Ari', 'household_name': 'Ari household',
            'settlement_name': 'Willow Camp', 'region_name': 'Greywater Reach', 'date_label': 'Spring, Year 1',
            'company': 'solo', 'permission': 'seek', 'supplies': 'basic'}
        choices.update(overrides)
        review = self.call('/api/rise/preview', {'choices': choices})
        return {'name': 'Rise fixture', 'choices': review['choices'], 'review_digest': review['review_digest'], 'request_id': request}

    def begin(self, **choices): return self.call('/api/rise/create', self.setup_payload(**choices))

    def act(self, saved, selected, request=None):
        result = self.call('/api/rise/action', {'id': saved['id'], 'revision': saved['revision'], 'actor': 'founder',
            'action': selected, 'request_id': request or f'action-{saved["revision"]}'})
        saved['revision'] = result['revision']
        return result

    def camp(self, saved):
        self.act(saved, 'walk_clearing'); self.act(saved, 'found')

    def creator_event(self, saved, operation, **parameters):
        result = self.call('/api/event', {'id': saved['id'], 'revision': saved['revision'],
            'mode': 'creator', 'op': operation, 'params': {'source_ref': 'synthetic Core/Rise regression', **parameters}})
        saved['revision'] = result['revision']
        return result

    def test_new_material_remains_inspectable_with_explicit_unknown_unit(self):
        saved = self.begin()
        self.creator_event(saved, 'establish_stock', location='founder-home', material='water',
            quantity=2, inventory_evidence_ref='synthetic measured inventory')
        before = self.store.path(saved['id']).read_bytes()
        inventory = self.call('/api/playthrough/'+saved['id'])['settlement']['inventory']
        water = next(item for item in inventory if item['material'] == 'water')
        self.assertEqual(water['quantity'], 2)
        self.assertIsNone(water['unit'])
        self.assertEqual(water['unit_status'], 'unconfigured')
        self.assertTrue(next(item for item in inventory if item['material'] == 'grain')['unit'])
        self.assertEqual(self.store.path(saved['id']).read_bytes(), before)
        self.act(saved, 'inspect')

    def test_core_location_confirmation_keeps_inventory_and_movement_usable(self):
        saved = self.begin()
        self.creator_event(saved, 'record_evidence', evidence_id='where', subject='founder',
            status='established', assertion='Founder is at commons.')
        self.creator_event(saved, 'receive_evidence', evidence_id='where', recipient='founder')
        self.creator_event(saved, 'confirm_character_field', subject='founder', field='location',
            value='commons', evidence_id='where', authority_ref='synthetic observation',
            instruction_ref='explicit synthetic confirmation')
        projected = self.call('/api/playthrough/'+saved['id'])['settlement']
        self.assertEqual(projected['location'], 'commons')
        self.assertIsNotNone(projected['inventory'])
        self.act(saved, 'walk_clearing')
        self.assertEqual(self.call('/api/playthrough/'+saved['id'])['settlement']['location'], 'clearing')

    def test_discovery_and_review_are_read_only_and_session_guarded(self):
        families = self.call('/api/rise/templates')['templates']
        self.assertEqual(len(families), 9)
        self.assertEqual([f['id'] for f in families if f['ready']], ['R00'])
        self.assertEqual(self.call('/api/content-library')['campaigns'][-1]['kind'], 'settlement_system')
        with self.assertRaises(HTTPError) as err:
            self.call('/api/create', {'name': 'Forged unreviewed Rise', 'profile_id': 'rise', 'scenario_id': 'rise', 'entry_id': 'R00'})
        self.assertEqual(err.exception.code, 403)
        self.setup_payload(); self.assertEqual(self.store.listing(), [])
        for path, payload in [('/api/rise/templates', None), ('/api/rise/preview', {'choices': {}})]:
            with self.assertRaises(HTTPError) as err: self.call(path, payload, token=False)
            self.assertEqual(err.exception.code, 403)
        with self.assertRaises(HTTPError) as err: self.call('/api/rise/preview', {'choices': {}}, origin='https://outside.invalid')
        self.assertEqual(err.exception.code, 403)

    def test_review_digest_rejects_changed_or_held_family_before_initial_save(self):
        payload = self.setup_payload(); payload['choices']['company'] = 'sibling'
        with self.assertRaises(HTTPError): self.call('/api/rise/create', payload)
        payload['choices']['template_id'] = 'H01'
        with self.assertRaises(HTTPError): self.call('/api/rise/create', payload)
        self.assertEqual(self.store.listing(), [])

    def test_creation_retries_preserve_bytes_and_recover_from_trash(self):
        payload = self.setup_payload(); saved = self.call('/api/rise/create', payload)
        original = self.store.path(saved['id']).read_bytes()
        replay = self.call('/api/rise/create', payload)
        self.assertTrue(replay['creation_replayed']); self.assertEqual(replay['id'], saved['id'])
        self.assertEqual(self.store.path(saved['id']).read_bytes(), original)
        changed = copy.deepcopy(payload); changed['choices']['supplies'] = 'stocked'
        with self.assertRaises(HTTPError): self.call('/api/rise/create', changed)
        self.assertEqual(self.store.path(saved['id']).read_bytes(), original)
        self.call('/api/delete', {'id': saved['id'], 'revision': 0})
        self.assertEqual(self.call('/api/rise/create', payload)['status'], 'trashed')
        self.assertEqual(self.store.listing(), [])
        self.call('/api/restore', {'id': saved['id'], 'revision': 0})
        self.assertEqual(self.store.path(saved['id']).read_bytes(), original)

    def test_action_replay_before_stale_revision_and_result_lookup_after_restart(self):
        saved = self.begin()
        body = {'id': saved['id'], 'revision': 0, 'actor': 'founder', 'action': 'request_grant', 'request_id': 'offer'}
        result = self.call('/api/rise/action', body); original = self.store.path(saved['id']).read_bytes()
        self.assertEqual(self.call('/api/rise/action', body), result)
        self.assertEqual(self.store.path(saved['id']).read_bytes(), original)
        self.assertEqual(Store(self.tmp.name).action_result(saved['id'], 'offer', 'founder'), result)
        lookup = self.call(f'/api/action-result/{saved["id"]}/offer?actor_id=founder')
        self.assertEqual(lookup, result); self.assertNotIn('certificate', json.dumps(lookup))
        chronicle = self.call(f'/api/chronicle/{saved["id"]}')
        self.assertTrue(any('Elin offers' in row['text'] for row in chronicle['entries']))
        with self.assertRaises(HTTPError): self.call('/api/rise/action', {**body, 'action': 'accept_grant'})
        with self.assertRaises(HTTPError): self.call('/api/rise/action', {**body, 'request_id': 'new-stale'})
        self.assertEqual(self.store.path(saved['id']).read_bytes(), original)

    def test_failed_persistence_does_not_accept_identity_or_repeat_effects(self):
        payload = self.setup_payload()
        with patch.object(self.store, 'write', side_effect=OSError('synthetic disk failure')):
            with self.assertRaises(OSError): create(self.store, payload)
        self.assertEqual(self.store.listing(), [])
        saved = create(self.store, payload)
        body = {'id': saved['id'], 'revision': 0, 'actor': 'founder', 'action': 'request_grant', 'request_id': 'disk-action'}
        original = self.store.path(saved['id']).read_bytes()
        with patch.object(self.store, 'write', side_effect=OSError('synthetic disk failure')):
            with self.assertRaises(OSError): action(self.store, body)
        self.assertEqual(self.store.path(saved['id']).read_bytes(), original)
        result = action(self.store, body)
        self.assertEqual(action(Store(self.tmp.name), body), result)
        self.assertEqual(self.store.read(saved['id'])['revision'], 1)

    def test_concurrent_retries_commit_only_one_creation_and_one_action(self):
        payload = self.setup_payload()
        with ThreadPoolExecutor(max_workers=2) as pool: results = list(pool.map(lambda _: create(self.store, payload), range(2)))
        self.assertEqual(results[0]['id'], results[1]['id']); self.assertEqual(len(self.store.listing()), 1)
        body = {'id': results[0]['id'], 'revision': 0, 'actor': 'founder', 'action': 'wait_hour', 'request_id': 'parallel-action'}
        with ThreadPoolExecutor(max_workers=2) as pool: actions = list(pool.map(lambda _: action(self.store, body), range(2)))
        self.assertEqual(actions[0], actions[1])
        raw = self.store.read(results[0]['id'])
        self.assertEqual(raw['revision'], 1); self.assertEqual(raw['state']['elapsed_time']['seconds'], 1800)

    def test_remote_stocks_private_policies_and_distant_work_are_absent_from_player_view(self):
        saved = self.begin(company='sibling', permission='held'); self.camp(saved)
        self.act(saved, 'delegate'); self.act(saved, 'walk_commons')
        raw = self.store.read(saved['id']); raw['state']['private_policy'] = 'hidden-policy-marker'
        # Preserve stock conservation while making private quantities distinctive.
        raw['state']['stocks']['oren-home']['grain'] += 9876
        raw['state']['opening_stock']['grain'] += 9876
        self.store.write(raw)
        for _ in range(2): self.act(saved, 'wait_hour')
        projected = self.call('/api/playthrough/' + saved['id'])
        s = projected['settlement']; serialized = json.dumps(projected)
        self.assertIsNone(s['inventory']); self.assertNotIn('hidden-policy-marker', serialized)
        self.assertNotIn('9880', serialized); self.assertNotIn('state', projected)
        self.assertTrue(all(p['worker'] != 'Rowan' for p in s['projects']))
        self.assertFalse(any('shelter project is complete' in r['text'] for r in s['receipts']))
        self.act(saved, 'walk_clearing')
        current = self.call('/api/playthrough/' + saved['id'])['settlement']
        self.assertEqual(next(p['status'] for p in current['projects'] if p['worker'] == 'Rowan'), 'complete')
        self.assertEqual(next(q['quantity'] for q in current['inventory'] if q['material'] == 'timber'), 3)

    def test_unauthorized_or_infeasible_action_leaves_save_unchanged_without_private_reason(self):
        saved = self.begin(); original = self.store.path(saved['id']).read_bytes()
        body = {'id': saved['id'], 'revision': 0, 'actor': 'founder', 'action': 'build', 'request_id': 'bad-build'}
        with self.assertRaises(HTTPError) as err: self.call('/api/rise/action', body)
        message = json.load(err.exception)['error']
        self.assertIn('No effects or elapsed work', message); self.assertNotIn('AssertionError', message)
        for changes in ({'actor': 'oren'}, {'seconds': 999}, {'action': 'invent_grain'}):
            with self.assertRaises(HTTPError): self.call('/api/rise/action', {**body, **changes})
        self.assertEqual(self.store.path(saved['id']).read_bytes(), original)

    def test_pending_freeform_intent_blocks_automatic_settlement_actions(self):
        saved = self.begin()
        result = self.call('/api/declaration', {'id': saved['id'], 'revision': 0, 'actor': 'founder',
            'request_id': 'own-response', 'declaration': 'I consider another approach.'})
        self.assertEqual(result['status'], 'declared_not_resolved')
        with self.assertRaises(HTTPError): self.call('/api/rise/action', {'id': saved['id'], 'revision': 1,
            'actor': 'founder', 'action': 'wait_hour', 'request_id': 'wait-with-pending'})
        self.assertEqual(self.store.read(saved['id'])['state']['elapsed_time']['seconds'], 0)


if __name__ == '__main__': unittest.main()
