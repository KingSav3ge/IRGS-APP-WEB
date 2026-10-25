"""App consumes current Engine phase capabilities; Catalog renders real receipts."""
import json
import sqlite3
import unittest
import uuid
from unittest.mock import patch

import test_process_bridge as bridge
from core_world import CoreWorld
from server import Store


class PhaseStartTests(unittest.TestCase):
    setUp = bridge.ProcessBridgeTests.setUp
    start = bridge.ProcessBridgeTests.start
    stop = bridge.ProcessBridgeTests.stop
    http = bridge.ProcessBridgeTests.http
    view = bridge.ProcessBridgeTests.view
    prepared = bridge.ProcessBridgeTests.prepared
    accepted = bridge.ProcessBridgeTests.accepted
    phase = bridge.ProcessBridgeTests.phase

    def fresh(self, key):
        if key == self.key:
            from test_scene_actions import fixture
            world = fixture()
            world.s['player_actor_ids'] = ['pc']
        else:
            from settlement_setup import initialize, preview
            from settlement_runtime import execute
            from test_settlement import choices
            selected = choices(); selected['permission'] = 'held'
            world = initialize(selected, preview(selected)['review_digest'], 'synthetic-start-http')
            execute(world, 'setup-walk', 'founder', 'walk_clearing', 'explicit synthetic setup')
            execute(world, 'setup-found', 'founder', 'found', 'explicit synthetic setup')
        record = self.store.read(key)
        record['state'] = world.s
        self.store.write(record)

    def start_body(self, key=None, actor='pc', action='look-quay'):
        key = key or self.key
        view = self.view(key, actor)
        option = next(row for row in view['process_control']['start_options'] if row['action_id'] == action)
        return {'id': key, 'actor': actor, 'revision': view['revision'], 'view_token': view['process_control']['view_token'],
            'request_id': uuid.uuid4().hex, 'command': 'start', 'capability_id': option['capability_id'],
            'intention': '  My exact requested ' + option['title'] + '\nOnly the selected action.  '}

    def test_start_options_are_effect_free_and_match_actual_engine_contract(self):
        import phase_contract
        from process_bridge import ProcessService
        for key, actor in ((self.key, 'pc'), (self.rise, 'founder')):
            self.fresh(key)
            record = self.store.read(key); before = self.store.path(key).read_bytes()
            scope = ProcessService(self.store).scope(record)
            expected = phase_contract.actor_view(CoreWorld(state=record['state']), actor,
                branch_id=scope.branch_id, restore_id=scope.restore_id)
            packet = self.view(key, actor)['process_control']
            self.assertEqual(packet['start_options'], expected['start_options'])
            self.assertEqual(packet['processes'], [])
            self.assertEqual(before, self.store.path(key).read_bytes())
            self.assertNotIn('state_digest', json.dumps(packet))

    def test_both_real_start_handlers_schedule_once_without_elapsed_work_or_stock_consumption(self):
        for key, actor, action in ((self.key, 'pc', 'look-quay'), (self.rise, 'founder', 'build')):
            self.fresh(key)
            before = self.store.read(key)
            body = self.start_body(key, actor, action)
            code, prepared = self.http('/api/process/prepare', body)
            self.assertEqual(code, 200, prepared)
            self.assertEqual(before, self.store.read(key))
            self.assertEqual(prepared['capability_id'], body['capability_id'])
            self.assertEqual(self.http('/api/process/prepare', body), (200, prepared))
            code, result = self.http('/api/process/execute', self.accepted(body))
            self.assertEqual(code, 200, result)
            self.assertFalse(result['process']['terminal'])
            self.assertEqual(result['process']['worked_seconds'], 0)
            self.assertEqual(result['process']['elapsed_seconds'], 0)
            self.assertEqual(result['process']['phase_id'], prepared['phase_id'])
            self.assertEqual(result['process']['original_intention'], body['intention'])
            self.assertEqual(before['state']['stocks'], self.store.read(key)['state']['stocks'])
            self.assertEqual(result['presentation']['engine_library']['id'], 'irgs-response-depot-v1')
            self.assertEqual(result['presentation']['catalog_library']['id'], 'irgs-response-depot-v1')
            self.assertEqual(result['presentation']['render_usage'], {'provider_calls': 0, 'model_tokens': 0})
            committed = self.store.path(key).read_bytes()
            self.assertEqual(self.http('/api/process/execute', self.accepted(body)), (200, result))
            self.assertEqual(committed, self.store.path(key).read_bytes())
        self.dispatch.assert_not_called()

    def test_hidden_permission_does_not_filter_menu_and_failed_start_is_atomic(self):
        self.fresh(self.rise)
        original = self.view(self.rise, 'founder')['process_control']['start_options']
        record = self.store.read(self.rise)
        record['state']['grants']['founding']['active'] = False
        self.store.write(record)
        self.assertEqual(original, self.view(self.rise, 'founder')['process_control']['start_options'])
        body = self.start_body(self.rise, 'founder', 'build')
        code, prepared = self.http('/api/process/prepare', body)
        self.assertEqual(code, 200, prepared)  # Attemptable is distinct from feasible.
        before = self.store.path(self.rise).read_bytes()
        code, result = self.http('/api/process/execute', self.accepted(body))
        self.assertEqual(code, 400, result)
        self.assertEqual(before, self.store.path(self.rise).read_bytes())
        self.assertNotIn('dependencies', json.dumps(result))

    def test_failed_start_save_and_restart_keep_capability_parent_and_phase(self):
        self.fresh(self.key)
        body = self.start_body()
        code, prepared = self.http('/api/process/prepare', body)
        self.assertEqual(code, 200)
        before = self.store.path(self.key).read_bytes()
        with patch.object(Store, 'write', side_effect=OSError('synthetic disk failure')):
            self.assertEqual(self.http('/api/process/execute', self.accepted(body))[0], 503)
        self.assertEqual(before, self.store.path(self.key).read_bytes())
        self.stop(); self.start()
        status = self.http('/api/process/status', {key: body[key] for key in ('id', 'actor', 'request_id')})[1]
        for key in ('capability_id', 'phase_id', 'process_id'):
            self.assertEqual(status[key], prepared[key])
        code, result = self.http('/api/process/execute', self.accepted(body))
        self.assertEqual(code, 200, result)
        self.assertEqual(result['process']['phase_id'], prepared['phase_id'])

    def test_client_cannot_select_kind_action_parent_source_or_foreign_capability(self):
        self.fresh(self.key)
        body = self.start_body()
        before = self.store.path(self.key).read_bytes()
        for changes in ({'capability_id': 'player.observe'}, {'details': {'kind': 'work', 'action_id': 'build'}},
                        {'process_id': 'browser-parent'}, {'source_ref': 'browser-source'}, {'actor': 'founder'},
                        {'view_token': 'pre-restore'}, {'capability_id': self.start_body(self.rise, 'founder', 'build')['capability_id']}):
            code, result = self.http('/api/process/prepare', {**body, **changes})
            self.assertIn(code, (400, 403), result)
        self.assertEqual(before, self.store.path(self.key).read_bytes())

    def test_completed_observation_preserves_full_engine_and_catalog_text(self):
        self.fresh(self.key)
        body = self.start_body()
        code, prepared = self.http('/api/process/prepare', body)
        self.assertEqual(code, 200)
        self.assertEqual(self.http('/api/process/execute', self.accepted(body))[0], 200)
        _, result = self.phase('advance', {'seconds': 3}, process_id=prepared['process_id'])
        from offline_responses import receipt_facts
        world = CoreWorld(state=self.store.read(self.key)['state'])
        exact = receipt_facts(world, 'pc', result['receipt']['event_id'])['literal_text']
        self.assertTrue(result['presentation']['text'].startswith(exact))
        self.assertEqual(result['process']['status'], 'completed')
        self.assertEqual(result['process']['worked_seconds'], 3)

    def test_old_private_pending_schema_upgrades_without_rewriting_typed_request(self):
        body, prepared = self.prepared('advance', {'seconds': 1})
        path = self.store.folder / '.host' / 'processes.sqlite'
        self.stop()
        with sqlite3.connect(path) as db:
            original = db.execute('SELECT request FROM requests WHERE id=?', (body['request_id'],)).fetchone()[0]
            db.execute('ALTER TABLE requests DROP COLUMN capability')
        self.start()
        code, result = self.http('/api/process/execute', self.accepted(body))
        self.assertEqual(code, 200, result)
        self.assertEqual(result['process']['phase_id'], prepared['phase_id'])
        with sqlite3.connect(path) as db:
            self.assertEqual(original, db.execute('SELECT request FROM requests WHERE id=?', (body['request_id'],)).fetchone()[0])
