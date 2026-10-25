"""Real typed Core phases through the common HTTP host, synthetic saves only."""
from concurrent.futures import ThreadPoolExecutor
import copy
import json
import uuid
from unittest.mock import patch

import test_solo_bridge as bridge
from core_world import CoreWorld
from process_runtime import prepare, execute
from server import Store


def install_process(store, key, actor, kind, action_id):
    """Trusted fixture setup, not a browser start/capability implementation."""
    record = store.read(key)
    world = CoreWorld(state=record['state'])
    request = prepare(world, phase_id='fixture-start', process_id='selected-process', actor=actor,
        command='start', details={'kind': kind, 'action_id': action_id},
        intention='Explicit synthetic ' + kind, source_ref='synthetic-selected-process',
        branch_id=key, restore_id='fixture-initialization')

    def persist(expected, candidate, received):
        assert expected == request.scope
        record['state'] = json.loads(candidate)
        store.write(record)
    execute(world, request, current_scope=request.scope, persist=persist, explicitly_accepted=True)


class ProcessBridgeTests(bridge.unittest.TestCase):
    start = bridge.SoloBridgeTests.start
    stop = bridge.SoloBridgeTests.stop
    http = bridge.SoloBridgeTests.http

    def setUp(self):
        bridge.SoloBridgeTests.setUp(self)
        self.stop()
        self.config = None
        install_process(self.store, self.key, 'pc', 'observation', 'look-quay')
        from settlement_setup import initialize, preview
        from settlement_runtime import execute as act
        from test_settlement import choices
        selected = choices(); selected['permission'] = 'held'
        world = initialize(selected, preview(selected)['review_digest'], 'synthetic-process-http')
        act(world, 'setup-walk', 'founder', 'walk_clearing', 'explicit synthetic setup')
        act(world, 'setup-found', 'founder', 'found', 'explicit synthetic setup')
        self.rise = uuid.uuid4().hex
        self.store.write({'id': self.rise, 'name': 'Process work fixture', 'revision': 1, 'state': world.s})
        install_process(self.store, self.rise, 'founder', 'work', 'build')
        self.start()
        no_provider = patch('solo_provider.CapabilityBroker.dispatch', side_effect=AssertionError('No routine inference'))
        self.dispatch = no_provider.start(); self.addCleanup(no_provider.stop)

    def view(self, key=None, actor='pc'):
        code, packet = self.http('/api/playthrough/' + (key or self.key) + '?actor_id=' + actor)
        self.assertEqual(code, 200, packet)
        return packet

    def prepared(self, command, details=None, *, key=None, actor='pc', **changes):
        key = key or self.key
        view = self.view(key, actor)
        body = {'id': key, 'actor': actor, 'revision': view['revision'],
            'view_token': view['process_control']['view_token'], 'request_id': uuid.uuid4().hex,
            'process_id': 'selected-process', 'command': command, 'details': details or {},
            'intention': '  Explicit ' + command + '\nDo only this.  ', **changes}
        code, result = self.http('/api/process/prepare', body)
        self.assertEqual(code, 200, result)
        return body, result

    def accepted(self, body, **changes):
        return {'id': body['id'], 'actor': body['actor'], 'request_id': body['request_id'],
                'explicitly_accepted': True, **changes}

    def phase(self, command, details=None, **kwargs):
        body, prepared = self.prepared(command, details, **kwargs)
        code, result = self.http('/api/process/execute', self.accepted(body))
        self.assertEqual(code, 200, result)
        self.assertEqual(result['process']['phase_id'], prepared['phase_id'])
        self.assertEqual(result['process']['phase_intention'], body['intention'])
        return body, result

    def test_common_received_projection_has_no_private_state_or_start_discovery(self):
        for key, actor in ((self.key, 'pc'), (self.rise, 'founder')):
            before = self.store.path(key).read_bytes()
            packet = self.view(key, actor)['process_control']
            self.assertFalse(packet['start_available'])
            row = packet['processes'][0]
            self.assertEqual(row['received']['worked_seconds'], 0)
            self.assertEqual(row['received']['actor'], actor)
            self.assertIn('advance', row['commands'])
            self.assertEqual(before, self.store.path(key).read_bytes())
            for secret in ('params_digest', 'state_digest', 'restore_id', 'PRIVATE_EVALUATOR_MARKER'):
                self.assertNotIn(secret, json.dumps(packet))
        self.dispatch.assert_not_called()

    def test_prepare_is_effect_free_stable_and_requires_explicit_acceptance(self):
        before = self.store.path(self.key).read_bytes()
        body, first = self.prepared('advance', {'seconds': 1})
        self.assertEqual(self.http('/api/process/prepare', body), (200, first))
        self.assertEqual(self.http('/api/process/execute', self.accepted(body, explicitly_accepted=False))[0], 400)
        self.assertEqual(before, self.store.path(self.key).read_bytes())
        changed = {**body, 'intention': 'Other exact words'}
        self.assertEqual(self.http('/api/process/prepare', changed)[0], 400)

    def test_non_rise_observation_delivers_knowledge_only_after_completion(self):
        initial = self.store.read(self.key)['state']['evidence']
        _, partial = self.phase('advance', {'seconds': 1})
        self.assertEqual(partial['process']['worked_seconds'], 1)
        self.assertEqual(partial['process']['status'], 'active')
        self.assertEqual(self.store.read(self.key)['state']['evidence'], initial)
        self.phase('pause'); self.phase('resume')
        _, done = self.phase('advance', {'seconds': 999})
        self.assertEqual(done['process']['status'], 'completed')
        self.assertTrue(done['process']['terminal'])
        self.assertEqual(done['process']['worked_seconds'], 3)
        self.assertEqual(self.store.read(self.key)['state']['elapsed_time']['seconds'], 3)
        self.assertNotEqual(self.store.read(self.key)['state']['evidence'], initial)
        self.assertEqual(done['presentation']['render_usage'], {'provider_calls': 0, 'model_tokens': 0})
        self.assertIn(done, self.view()['completed_actions'])

    def test_rise_work_pause_resume_preserves_project_and_finishes_once(self):
        initial = copy.deepcopy(self.store.read(self.rise)['state']['stocks'])
        kwargs = {'key': self.rise, 'actor': 'founder'}
        _, partial = self.phase('advance', {'seconds': 100}, **kwargs)
        self.assertEqual(partial['process']['worked_seconds'], 100)
        self.phase('pause', **kwargs); self.phase('resume', **kwargs)
        body, done = self.phase('advance', {'seconds': 3600}, **kwargs)
        self.assertEqual(done['process']['status'], 'active')  # Existing competing material boundary.
        body, done = self.phase('advance', {'seconds': 3600}, **kwargs)
        saved = self.store.path(self.rise).read_bytes()
        self.assertEqual(done['process']['status'], 'completed')
        self.assertEqual(self.store.read(self.rise)['state']['projects']['shelter']['worked'], 3600)
        self.assertNotEqual(initial, self.store.read(self.rise)['state']['stocks'])
        self.assertEqual(self.http('/api/process/execute', self.accepted(body)), (200, done))
        self.assertEqual(saved, self.store.path(self.rise).read_bytes())

    def test_cancel_keeps_committed_elapsed_and_original_intention(self):
        self.phase('advance', {'seconds': 1})
        _, result = self.phase('cancel')
        self.assertEqual(result['process']['status'], 'cancelled')
        self.assertEqual(result['process']['worked_seconds'], 1)
        self.assertEqual(result['process']['original_intention'], 'Explicit synthetic observation')
        self.assertEqual(self.view()['process_control']['processes'][0]['commands'], [])

    def test_failed_save_retries_identical_typed_phase_without_partial_effect(self):
        body, prepared = self.prepared('advance', {'seconds': 1})
        before = self.store.path(self.key).read_bytes()
        with patch.object(Store, 'write', side_effect=OSError('synthetic disk failure')):
            self.assertEqual(self.http('/api/process/execute', self.accepted(body))[0], 503)
        self.assertEqual(before, self.store.path(self.key).read_bytes())
        status = self.http('/api/process/status', {k: body[k] for k in ('id', 'actor', 'request_id')})[1]
        self.assertEqual(status['status'], 'save_failed')
        self.assertEqual(status['phase_id'], prepared['phase_id'])
        code, result = self.http('/api/process/execute', self.accepted(body))
        self.assertEqual(code, 200, result)
        self.assertEqual(result['process']['worked_seconds'], 1)
        self.assertEqual(result['process']['phase_id'], prepared['phase_id'])

    def test_late_durability_failure_recovers_already_saved_result(self):
        body, _ = self.prepared('advance', {'seconds': 1})
        with patch('server.sync_parent', side_effect=OSError('synthetic directory sync failure')):
            self.assertEqual(self.http('/api/process/execute', self.accepted(body))[0], 503)
        committed = self.store.path(self.key).read_bytes()
        code, result = self.http('/api/process/execute', self.accepted(body))
        self.assertEqual(code, 200)
        self.assertEqual(result['process']['worked_seconds'], 1)
        self.assertEqual(committed, self.store.path(self.key).read_bytes())

    def test_concurrent_duplicate_and_competing_phase_commit_only_once(self):
        body, _ = self.prepared('advance', {'seconds': 1})
        other, _ = self.prepared('advance', {'seconds': 2})
        with ThreadPoolExecutor(max_workers=4) as pool:
            results = list(pool.map(lambda _: self.http('/api/process/execute', self.accepted(body)), range(4)))
        self.assertTrue(all(result == results[0] for result in results))
        self.assertEqual(results[0][0], 200)
        self.assertEqual(self.http('/api/process/execute', self.accepted(other))[0], 400)
        self.assertEqual(self.store.read(self.key)['state']['elapsed_time']['seconds'], 1)

    def test_restart_preserves_prepared_phase_and_accepted_result(self):
        body, prepared = self.prepared('advance', {'seconds': 1})
        self.stop(); self.start()
        code, result = self.http('/api/process/execute', self.accepted(body))
        self.assertEqual(code, 200, result)
        self.assertEqual(result['process']['phase_id'], prepared['phase_id'])
        self.stop(); self.start()
        self.assertEqual(self.http('/api/action-result/' + self.key + '/' + body['request_id'] + '?actor_id=pc'), (200, result))
        self.assertEqual(self.http('/api/process/execute', self.accepted(body)), (200, result))

    def test_identical_restore_invalidates_pending_phase_but_retains_original_result(self):
        accepted, result = self.phase('advance', {'seconds': 1})
        pending, _ = self.prepared('pause')
        revision = self.store.read(self.key)['revision']
        self.assertEqual(self.http('/api/delete', {'id': self.key, 'revision': revision})[0], 200)
        self.assertEqual(self.http('/api/restore', {'id': self.key, 'revision': revision})[0], 200)
        self.assertEqual(self.http('/api/process/execute', self.accepted(pending))[0], 400)
        self.assertEqual(self.http('/api/process/execute', self.accepted(accepted)), (200, result))
        self.phase('pause')

    def test_branch_cannot_accept_parent_prepared_command_or_replay_parent_result(self):
        body, _ = self.prepared('advance', {'seconds': 1})
        code, branch = self.http('/api/fork', {'id': self.key, 'mode': 'creator'})
        self.assertEqual(code, 200, branch)
        self.assertEqual(self.http('/api/process/execute', self.accepted(body, id=branch['id']))[0], 403)
        self.assertEqual(self.store.read(branch['id'])['state']['elapsed_time']['seconds'], 0)

    def test_forged_fields_actor_source_and_start_are_rejected(self):
        body, _ = self.prepared('pause')
        for change in ({'actor': 'gatekeeper'}, {'scope': {}}, {'source_ref': 'browser'},
                       {'command': 'start'}, {'view_token': 'invented'}, {'revision': True},
                       {'command': 'advance', 'details': {'seconds': True}}):
            candidate = {**body, 'request_id': uuid.uuid4().hex, **change}
            self.assertIn(self.http('/api/process/prepare', candidate)[0], (400, 403))
        self.assertEqual(self.http('/api/process/status', {'id': self.key, 'actor': 'gatekeeper', 'request_id': body['request_id']})[0], 403)

    def test_engine_rejection_is_atomic_sanitized_and_durable(self):
        body, _ = self.prepared('advance', {'seconds': 9007199254740991}, key=self.rise, actor='founder')
        before = self.store.path(self.rise).read_bytes()
        code, result = self.http('/api/process/execute', self.accepted(body))
        self.assertEqual(code, 400, result)
        self.assertEqual(before, self.store.path(self.rise).read_bytes())
        self.assertNotIn('dependencies', json.dumps(result))
        status = self.http('/api/process/status', {k: body[k] for k in ('id', 'actor', 'request_id')})[1]
        self.assertEqual(status['status'], 'rejected')
        self.stop(); self.start()
        self.assertEqual(self.http('/api/process/execute', self.accepted(body))[0], 400)

    def test_status_does_not_reveal_unreceived_live_work_progress(self):
        before = self.view(self.rise, 'founder')['process_control']['processes'][0]['received']
        code, result = self.http('/api/rise/action', {'id': self.rise, 'actor': 'founder',
            'revision': self.store.read(self.rise)['revision'], 'request_id': uuid.uuid4().hex, 'action': 'wait_hour'})
        self.assertEqual(code, 200, result)
        self.assertGreater(self.store.read(self.rise)['state']['projects']['shelter']['worked'], 0)
        after = self.view(self.rise, 'founder')['process_control']['processes'][0]['received']
        self.assertEqual(before, after)
        _, inspected = self.phase('inspect', key=self.rise, actor='founder')
        self.assertGreater(inspected['process']['worked_seconds'], 0)
        self.assertEqual(inspected['process']['elapsed_seconds'], 0)

    def test_restore_of_earlier_bytes_does_not_reexecute_a_previously_accepted_phase(self):
        original = self.store.path(self.key).read_bytes()
        body, result = self.phase('advance', {'seconds': 1})
        revision = self.store.read(self.key)['revision']
        self.assertEqual(self.http('/api/delete', {'id': self.key, 'revision': revision})[0], 200)
        self.store.trash_path(self.key).write_bytes(original)  # Synthetic earlier snapshot only.
        old_revision = json.loads(original)['revision']
        self.assertEqual(self.http('/api/restore', {'id': self.key, 'revision': old_revision})[0], 200)
        self.assertEqual(self.http('/api/process/execute', self.accepted(body))[0], 400)
        self.assertEqual(self.store.path(self.key).read_bytes(), original)
        self.assertEqual(self.http('/api/action-result/' + self.key + '/' + body['request_id'] + '?actor_id=pc')[0], 404)

    def test_session_and_origin_authentication_guard_both_process_endpoints(self):
        body, _ = self.prepared('pause')
        token = self.token
        self.token = 'wrong-token'
        try:
            self.assertEqual(self.http('/api/process/prepare', body)[0], 403)
            self.assertEqual(self.http('/api/process/execute', self.accepted(body))[0], 403)
        finally:
            self.token = token

    def test_result_recovery_does_not_acknowledge_while_directory_sync_is_unavailable(self):
        body, result = self.phase('advance', {'seconds': 1})
        before = self.store.path(self.key).read_bytes()
        endpoint = '/api/action-result/' + self.key + '/' + body['request_id'] + '?actor_id=pc'
        with patch('server.sync_parent', side_effect=OSError('synthetic sync failure')):
            self.assertEqual(self.http(endpoint)[0], 503)
        with patch('process_bridge.sync_parent', side_effect=OSError('synthetic sync failure')):
            self.assertEqual(self.http('/api/process/execute', self.accepted(body))[0], 503)
            self.assertEqual(self.http('/api/process/status', {k: body[k] for k in ('id', 'actor', 'request_id')})[0], 503)
        self.assertEqual(self.store.path(self.key).read_bytes(), before)
        self.assertEqual(self.http(endpoint), (200, result))
