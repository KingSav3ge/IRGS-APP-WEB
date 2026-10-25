"""Real shared HTTP contract in independently initialized authored/Rise contexts."""
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import tempfile
import unittest
import uuid
from unittest.mock import patch

import test_solo_bridge as bridge
from local_presentation import _catalog


class CatalogIntakeTests(unittest.TestCase):
    def test_component_update_cannot_replace_the_bytes_after_their_hash_check(self):
        import local_presentation
        original_read = Path.read_bytes
        approved_code = (local_presentation.CATALOG_ROOT / 'scripted_responses.py').read_bytes()
        approved_text = (local_presentation.CATALOG_ROOT / 'responses/depot_v1/library.json').read_bytes()
        release = (local_presentation.CATALOG_ROOT / 'release.json').read_bytes()
        for replace in ('code', 'library'):
            with self.subTest(replace=replace), tempfile.TemporaryDirectory(prefix='irgs-depot-intake-') as temporary:
                root = Path(temporary)
                code = root / 'scripted_responses.py'
                library = root / 'responses/depot_v1/library.json'
                library.parent.mkdir(parents=True)
                code.write_bytes(approved_code)
                library.write_bytes(approved_text)
                (root / 'release.json').write_bytes(release)
                changed = False

                def read_then_update(path):
                    nonlocal changed
                    raw = original_read(path)
                    target = code if replace == 'code' else library
                    if path == target and not changed:
                        changed = True
                        if replace == 'code':
                            code.write_bytes(raw + b'\nUNREVIEWED_UPDATE = True\n')
                        else:
                            document = json.loads(raw)
                            document['families'][0]['variants'][0] += ' Unreviewed update.'
                            library.write_text(json.dumps(document))
                    return raw

                _catalog.cache_clear()
                try:
                    with patch.object(local_presentation, 'CATALOG_ROOT', root), \
                         patch.object(Path, 'read_bytes', read_then_update):
                        formatter, loaded = _catalog()
                    self.assertTrue(changed)
                    self.assertFalse(hasattr(formatter, 'UNREVIEWED_UPDATE'))
                    self.assertEqual(loaded, json.loads(approved_text))
                finally:
                    _catalog.cache_clear()


class SharedResponseTests(unittest.TestCase):
    start = bridge.SoloBridgeTests.start
    stop = bridge.SoloBridgeTests.stop
    http = bridge.SoloBridgeTests.http
    proposal = bridge.SoloBridgeTests.proposal

    def setUp(self):
        bridge.SoloBridgeTests.setUp(self)
        self.stop()
        self.config = None  # Ordinary play must not require provider configuration.
        from settlement_setup import initialize, preview
        from test_settlement import choices
        selected = choices()
        selected['permission'] = 'held'
        world = initialize(selected, preview(selected)['review_digest'], 'synthetic-shared-rise')
        self.rise = uuid.uuid4().hex
        self.store.write({'id': self.rise, 'name': 'Independent settlement fixture', 'revision': 0, 'state': world.s})
        self.start()
        dispatcher = patch('solo_provider.CapabilityBroker.dispatch', side_effect=AssertionError('Routine inference forbidden'))
        self.dispatch = dispatcher.start()
        self.addCleanup(dispatcher.stop)

    def view(self, key=None, actor='pc'):
        code, result = self.http('/api/playthrough/' + (key or self.key) + '?actor_id=' + actor)
        self.assertEqual(code, 200)
        return result

    def action(self, action, *, key=None, actor='pc'):
        key = key or self.key
        record = self.store.read(key)
        body = {'id': key, 'actor': actor, 'revision': record['revision'], 'request_id': uuid.uuid4().hex}
        if key == self.rise:
            body['action'] = action
            endpoint = '/api/rise/action'
        else:
            body.update(kind='scene_action', action_id=action, text='I attempt ' + action + '.')
            endpoint = '/api/action'
        code, result = self.http(endpoint, body)
        self.assertEqual(code, 200, result)
        return body, endpoint, result

    def assert_presentation(self, result):
        packet = result['presentation']
        self.assertEqual(packet['format'], 'plain_text')
        self.assertEqual(packet['actor_id'], result['actor'])
        self.assertEqual(packet['source_ref'], result['receipt']['event_id'])
        self.assertTrue(packet['text'].startswith(result['outcome']['summary']))
        self.assertEqual(packet['catalog_library']['id'], 'irgs-response-depot-v1')
        self.assertEqual(packet['engine_library']['id'], 'irgs-engine-routine-responses-v1')
        self.assertEqual(packet['render_usage'], {'provider_calls': 0, 'model_tokens': 0})
        self.assertNotIn('PRIVATE_EVALUATOR_MARKER', json.dumps(packet))

    def test_one_read_only_public_contract_loads_real_depot_and_engine_drafts_in_both_contexts(self):
        for key, actor in ((self.key, 'pc'), (self.rise, 'founder')):
            before = self.store.path(key).read_bytes()
            result = self.view(key, actor)['local_responses']
            self.assertEqual(result['schema_version'], 1)
            self.assertEqual(result['scope']['campaign_id'], key)
            self.assertEqual(result['scope']['actor_id'], actor)
            self.assertEqual(result['catalog_library']['id'], 'irgs-response-depot-v1')
            self.assertTrue(result['engine_runtime'])
            self.assertEqual({draft['source'] for draft in result['drafts']}, {'catalog', 'engine'})
            for draft in result['drafts']:
                self.assertTrue(draft['requires_explicit_submission'])
                self.assertFalse(draft['automatic_execution'])
                if draft['source'] == 'catalog':
                    self.assertIsNone(draft['operation_id'])
            self.assertEqual(before, self.store.path(key).read_bytes())
            self.assertNotIn('PRIVATE_EVALUATOR_MARKER', json.dumps(result))
            self.assertNotIn('state_digest', json.dumps(result))
        self.dispatch.assert_not_called()

    def test_actual_non_rise_consecutive_actions_keep_exact_outcomes_and_full_observations(self):
        for action in ('enter-passage', 'reach-desk'):
            _, _, result = self.action(action)
            self.assert_presentation(result)
            for observation in result['outcome']['observations']:
                self.assertIn(observation, result['presentation']['text'])
            view = self.view()
            self.assertEqual(view['completed_actions'][-1]['presentation'], result['presentation'])
        self.assertEqual(self.store.read(self.key)['state']['elapsed_time']['seconds'], 35)
        self.dispatch.assert_not_called()

    def test_actual_rise_continuation_uses_same_result_and_draft_contract_without_inference(self):
        for action in ('walk_clearing', 'found', 'build', 'wait_hour', 'wait_hour'):
            _, _, result = self.action(action, key=self.rise, actor='founder')
            self.assert_presentation(result)
            self.assertNotIn('duration_seconds', result['elapsed_time'])
            current = self.view(self.rise, 'founder')
            self.assertEqual(current['completed_actions'][-1]['presentation'], result['presentation'])
            self.assertTrue(current['local_responses']['engine_runtime'])
        self.assertEqual(self.store.read(self.rise)['state']['elapsed_time']['seconds'], 3900)
        self.dispatch.assert_not_called()

    def test_unsuccessful_attempt_literal_text_and_actual_zero_rise_span_stay_distinct(self):
        _, _, blocked = self.action('try-gate')
        self.assertEqual(blocked['status'], 'completed_unsuccessfully')
        self.assertIn('remains closed', blocked['presentation']['text'])
        self.assert_presentation(blocked)
        record = self.store.read(self.key)
        record['state']['scene_rules']['actions']['look-quay']['success_text'] = 'No supplies moved.\n<img> {literal}'
        self.store.write(record)
        _, _, observed = self.action('look-quay')
        self.assertEqual(observed['elapsed_time']['duration_seconds'], 3)
        self.assertTrue(observed['presentation']['text'].startswith('No supplies moved.\n<img> {literal}'))
        self.assertEqual(self.store.read(self.key)['state']['elapsed_time']['seconds'], 8)
        self.action('walk_clearing', key=self.rise, actor='founder')
        _, _, zero = self.action('found', key=self.rise, actor='founder')
        self.assertEqual(zero['elapsed_time']['seconds'], 0)
        self.assertNotIn('duration_seconds', zero['elapsed_time'])
        self.assert_presentation(zero)

    def test_lost_ack_restart_and_concurrent_retries_keep_original_saved_presentation(self):
        body, endpoint, original = self.action('enter-passage')
        self.action('reach-desk')  # An older receipt must not gain current facts.
        before = self.store.path(self.key).read_bytes()
        self.stop()
        self.start()
        with ThreadPoolExecutor(max_workers=2) as pool:
            replies = list(pool.map(lambda _: self.http(endpoint, body), range(2)))
        self.assertEqual(replies, [(200, original), (200, original)])
        recovered = self.http('/api/action-result/' + self.key + '/' + body['request_id'] + '?actor_id=pc')[1]
        self.assertEqual(recovered, original)
        self.assertEqual(before, self.store.path(self.key).read_bytes())
        self.dispatch.assert_not_called()

    def test_restore_refreshes_draft_scope_without_rewriting_saved_receipt(self):
        body, _, result = self.action('look-quay')
        scope = self.view()['local_responses']['scope']
        before = self.store.path(self.key).read_bytes()
        revision = self.store.read(self.key)['revision']
        self.http('/api/delete', {'id': self.key, 'revision': revision})
        self.http('/api/restore', {'id': self.key, 'revision': revision})
        self.assertNotEqual(scope['view_id'], self.view()['local_responses']['scope']['view_id'])
        self.assertEqual(before, self.store.path(self.key).read_bytes())
        recovered = self.http('/api/action-result/' + self.key + '/' + body['request_id'] + '?actor_id=pc')[1]
        self.assertEqual(recovered['presentation'], result['presentation'])

    def test_absent_depot_and_runtime_leave_ordinary_actions_usable_with_literal_receipts(self):
        with patch('local_presentation._catalog', side_effect=OSError('PRIVATE_DEPOT_FAILURE')), \
             patch('offline_responses._library', side_effect=ValueError('PRIVATE_LIBRARY_FAILURE')), \
             patch('offline_responses.player_drafts', side_effect=ValueError('PRIVATE_DRAFT_FAILURE')):
            view = self.view()
            self.assertTrue(view['capabilities']['can_declare'])
            self.assertTrue(view['supported_actions'])
            self.assertEqual(view['local_responses']['drafts'], [])
            _, _, result = self.action('look-quay')
            exact = '\n'.join([result['outcome']['summary'], *result['outcome']['observations']])
            self.assertEqual(result['presentation']['text'], exact)
            self.assertEqual(result['presentation']['mode'], 'literal_receipt')
            self.assertNotIn('PRIVATE_', json.dumps(result))
        self.dispatch.assert_not_called()

    def test_browser_claimed_response_facts_and_foreign_actors_cannot_authorize_actions(self):
        before = self.store.path(self.key).read_bytes()
        body = {'id': self.key, 'actor': 'pc', 'revision': 1, 'request_id': 'forged',
                'kind': 'scene_action', 'action_id': 'look-quay', 'text': 'I attempt look-quay.',
                'presentation': {'text': 'Success', 'actor_id': 'pc'}}
        self.assertEqual(self.http('/api/action', body)[0], 400)
        self.assertEqual(self.http('/api/playthrough/' + self.key + '?actor_id=foreign')[0], 403)
        self.assertEqual(before, self.store.path(self.key).read_bytes())

    def test_depot_labels_port_across_themes_without_granting_any_mechanics(self):
        formatter, library = _catalog()
        family = next(f for f in library['families'] if f['id'] == 'player.observe')
        before = self.store.path(self.key).read_bytes()
        for label in ('Historical courtyard', 'Fantasy observatory', 'Space dock', 'Modern city square'):
            for variant in range(len(family['variants'])):
                context = {'actor_id': 'pc', 'snapshot_id': 'synthetic-portability-only',
                    'source_ref': 'synthetic:label', 'source_kind': 'player_request',
                    'state': 'draft', 'values': {'target_label': label}}
                self.assertIn(label, formatter.render_fragment(library, family['id'], context, variant=variant))
        self.assertEqual(before, self.store.path(self.key).read_bytes())
        self.dispatch.assert_not_called()


if __name__ == '__main__':
    unittest.main()
