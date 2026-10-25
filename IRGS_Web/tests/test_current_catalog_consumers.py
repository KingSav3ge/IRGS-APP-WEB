"""Current App-side qualification; historical Catalog consumer IDs stay intact."""
import copy
import hashlib
import importlib.util
import json
import unittest
import uuid
from unittest.mock import patch

import test_solo_bridge as bridge
from catalog_paths import CATALOG_ROOT
from local_presentation import _catalog


def reader(name):
    spec = importlib.util.spec_from_file_location('_app_current_' + name, CATALOG_ROOT / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CurrentCatalogConsumerTests(unittest.TestCase):
    start = bridge.SoloBridgeTests.start
    stop = bridge.SoloBridgeTests.stop
    http = bridge.SoloBridgeTests.http

    def setUp(self):
        bridge.SoloBridgeTests.setUp(self)
        self.stop()
        self.config = None
        compatibility = reader('response_depot_compatibility')
        self.contract = compatibility.load_fixture()
        self.inputs = {key: compatibility.export_actor_input(key) for key in ('rise', 'quay')}
        self.oracle = compatibility.load_evaluator_data()  # Test-only oracle; never a render packet.
        from settlement_setup import preview
        from rise_campaigns import create
        choices = reader('solo_evaluation').load_evaluator_data()['setup']['choices']
        rise = create(self.store, {'name': 'Current Catalog Rise', 'choices': choices,
            'review_digest': preview(choices)['review_digest'], 'request_id': 'current-catalog-rise'})
        from historical_campaigns import historical_entry
        from starting_selection import starting_options
        selection = copy.deepcopy(self.contract['contexts']['quay']['selection'])
        opening = selection.pop('opening_id')
        selection['snapshot_sha256'] = historical_entry(selection['entry_id'])['snapshot_sha256']
        options = starting_options(**selection)
        quay = self.store.create('Current Catalog quay', **selection, selection_digest=options['selection_digest'],
            request_id='current-catalog-quay', creator=False,
            character={'kind': 'new', 'name': 'Current fixture courier', 'species': 'human',
                       'background': '', 'opening_id': opening})
        self.keys = {'rise': rise['id'], 'quay': quay['id']}
        for key in self.keys.values():
            record = self.store.read(key)
            record['state'].setdefault('site_conditions', {})['evaluator_only'] = {'marker': self.oracle['hidden_marker']}
            self.store.write(record)
        self.start()
        for target in ('solo_provider.CapabilityBroker.dispatch', 'openai_proposals.OpenAIProposalTransport.__call__'):
            guard = patch(target, side_effect=AssertionError('Current component integration must stay offline'))
            self.addCleanup(guard.stop)
            guard.start()

    def view(self, context):
        code, packet = self.http('/api/playthrough/' + self.keys[context])
        self.assertEqual(code, 200, packet)
        self.assertNotIn(self.oracle['hidden_marker'], json.dumps(packet))
        return packet

    def test_current_depot_and_followup_preserve_original_fixture_and_consumer_ids(self):
        contract = json.loads((CATALOG_ROOT / 'evaluation/integrated_responses_v1/compatibility.json').read_text())
        source = CATALOG_ROOT / contract['source_fixture']['manifest']
        self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), contract['source_fixture']['sha256'])
        self.assertEqual(contract['consumers']['app_commit'], 'aae8a25656c890181e0aa569df2c716968ec3642')
        from response_depot import DEPOT
        self.assertEqual(DEPOT.read_bytes(), (CATALOG_ROOT / 'responses/depot_v1/library.json').read_bytes())
        _, library = _catalog()
        self.assertEqual(library['library_id'], 'irgs-response-depot-v1')

    def test_all_nine_catalog_cases_execute_through_current_app_and_keep_exact_receipts(self):
        from core_world import CoreWorld
        from offline_responses import receipt_facts
        for context, key in self.keys.items():
            older = []
            for case in self.inputs[context]['cases']:
                view = self.view(context)
                body = {'id': key, 'actor': view['actor_id'], 'revision': view['revision'], 'request_id': case['request_id']}
                if context == 'rise':
                    body['action'] = case['action_id']; endpoint = '/api/rise/action'
                else:
                    option = next(row for row in view['supported_actions'] if row.get('action_id') == case['action_id'])
                    body.update(kind='scene_action', action_id=case['action_id'], text=option['text']); endpoint = '/api/action'
                code, result = self.http(endpoint, body)
                self.assertEqual(code, 200, result)
                expected = self.oracle['cases'][case['case_id']]
                self.assertEqual(result['status'], expected['status'])
                self.assertEqual(result['elapsed_time']['seconds' if context == 'rise' else 'duration_seconds'], expected['duration_seconds'])
                self.assertEqual(self.store.read(key)['state']['elapsed_time']['seconds'], expected['total_seconds'])
                world = CoreWorld(state=self.store.read(key)['state'])
                exact = receipt_facts(world, result['actor'], result['receipt']['event_id'])['literal_text']
                self.assertTrue(result['presentation']['text'].startswith(exact))
                self.assertEqual(result['presentation']['catalog_library']['id'], 'irgs-response-depot-v1')
                self.assertEqual(result['presentation']['render_usage'], {'provider_calls': 0, 'model_tokens': 0})
                self.assertNotIn(self.oracle['hidden_marker'], json.dumps(result))
                older.append((body, result))
            before = self.store.path(key).read_bytes()
            for body, result in older:
                self.assertEqual(self.http('/api/action-result/' + key + '/' + body['request_id'] + '?actor_id=' + body['actor']), (200, result))
            self.assertEqual(before, self.store.path(key).read_bytes())

    def test_catalog_starters_are_non_submitting_and_actor_scoped_in_both_contexts(self):
        for context, key in self.keys.items():
            before = self.store.path(key).read_bytes()
            view = self.view(context)
            packet = view['local_responses']
            self.assertEqual(packet['scope']['actor_id'], view['actor_id'])
            self.assertTrue(any(row['source'] == 'catalog' for row in packet['drafts']))
            self.assertTrue(all(row['requires_explicit_submission'] and not row['automatic_execution'] for row in packet['drafts']))
            self.assertEqual(view['process_control']['engine_schema'], 'irgs-phase-capabilities-1')
            self.assertEqual(before, self.store.path(key).read_bytes())

    def test_catalog_authored_start_reaches_real_engine_phase_and_local_presentation(self):
        key = self.keys['quay']; view = self.view('quay')
        option = next(row for row in view['process_control']['start_options'] if row['action_id'] == 'look-quay')
        body = {'id': key, 'actor': view['actor_id'], 'revision': view['revision'],
            'view_token': view['process_control']['view_token'], 'request_id': uuid.uuid4().hex,
            'command': 'start', 'capability_id': option['capability_id'], 'intention': 'I observe this received quay scene.'}
        code, prepared = self.http('/api/process/prepare', body)
        self.assertEqual(code, 200, prepared)
        accepted = {'id': key, 'actor': body['actor'], 'request_id': body['request_id'], 'explicitly_accepted': True}
        self.assertEqual(self.http('/api/process/execute', accepted)[0], 200)
        view = self.view('quay')
        continuation = {**body, 'revision': view['revision'], 'view_token': view['process_control']['view_token'],
            'command': 'advance', 'request_id': uuid.uuid4().hex, 'process_id': prepared['process_id'], 'details': {'seconds': 20}}
        del continuation['capability_id']
        self.assertEqual(self.http('/api/process/prepare', continuation)[0], 200)
        code, result = self.http('/api/process/execute', {**accepted, 'request_id': continuation['request_id']})
        self.assertEqual(code, 200, result)
        self.assertEqual(result['process']['status'], 'completed')
        self.assertEqual(result['process']['worked_seconds'], 20)  # This selected authored opening's actual rule.
        self.assertEqual(result['presentation']['engine_library']['id'], 'irgs-response-depot-v1')
        self.assertEqual(result['presentation']['catalog_library']['id'], 'irgs-response-depot-v1')
