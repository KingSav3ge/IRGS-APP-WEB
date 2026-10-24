"""Offline HTTP bridge qualification against an explicitly selected Engine API.

The reviewed dependency predates this API; these checks skip there and run when
IRGS_ENGINE_ROOT selects the exact Solo candidate. Real Core, temporary saves.
"""
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
import json
from pathlib import Path
import sys
import tempfile
import threading
import unittest
import uuid
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from server import Store, make_server
from assistance import SoloConfiguration

try:
    from solo_provider import (AttemptLedger, CapabilityBroker, Route, SCHEMA_VERSION,
                               SpecialistRegistry, TransportReply)
    from test_scene_actions import fixture
    SOLO_API = True
except ModuleNotFoundError:
    SOLO_API = False


class OfflineTransport:
    def __init__(self):
        self.action = 'enter-passage'
        self.inputs = []
        self.error = None
        self.malformed = False
        self.entered, self.release = threading.Event(), threading.Event()
        self.release.set()

    def __call__(self, model_input, route, **limits):
        self.inputs.append(model_input)
        self.entered.set()
        self.release.wait(3)
        body = {'intention': model_input['intention'], 'action_id': self.action,
                'source_refs': model_input['source_refs'][:1]}
        return TransportReply('not-json' if self.malformed else json.dumps(body),
            json.dumps(route.identity()), json.dumps({'input_tokens': 20, 'output_tokens': 12}),
            'offline-attempt', error=self.error)


@unittest.skipUnless(SOLO_API, 'Selected reviewed Engine predates Solo provider API; qualify exact candidate separately')
class SoloBridgeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='irgs-solo-http-')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.store = Store(self.root / 'saves')
        world = fixture()
        world.s['player_actor_ids'] = ['pc']
        world.s['site_conditions']['quay-gate']['evaluator_only'] = 'PRIVATE_EVALUATOR_MARKER'
        self.key = uuid.uuid4().hex
        self.store.write({'id': self.key, 'name': 'Offline opening', 'revision': 1, 'state': world.s})
        self.transport = OfflineTransport()
        private = self.root / 'technical'
        private.mkdir()
        self.route = Route('offline', 'synthetic', 'none', 'in-process', 'fixture-v1', 'v1',
            'config-v1', 'synthetic-transfer-approved-v1', 'synthetic-ceiling-v1', 10,
            enabled=True, approval_ref='offline-tests-only', lifecycle='qualified',
            tested_capabilities=(SCHEMA_VERSION,))
        self.config = SoloConfiguration(lambda scope: CapabilityBroker(SpecialistRegistry([self.route]),
            AttemptLedger(private / 'attempts.sqlite', budget_units=100, max_inflight=2),
            enabled=True, scope_reader=scope), self.transport, 'offline', 'synthetic-approved',
            'synthetic-transfer-approved-v1', 'config-v1', private, 60, 512)
        self.start()
        self.addCleanup(self.stop)

    def start(self):
        self.server = make_server(0, self.store.folder, solo_configuration=self.config)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.url = f'http://127.0.0.1:{self.server.server_port}'
        self.token = self.http('/api/campaigns')[1]['token']

    def stop(self):
        self.transport.release.set()
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()

    def http(self, path, body=None):
        headers = {'X-IRGS-Token': getattr(self, 'token', '')}
        if body is not None:
            headers['Content-Type'] = 'application/json'
        request = Request(self.url + path, data=json.dumps(body).encode() if body is not None else None,
                          headers=headers)
        try:
            with urlopen(request, timeout=10) as reply:
                return reply.status, json.load(reply)
        except HTTPError as error:
            return error.code, json.load(error)

    def proposal(self, **changes):
        return {'id': self.key, 'actor': 'pc', 'revision': self.store.read(self.key)['revision'],
                'request_id': uuid.uuid4().hex, 'intention': '  I take the passage.\nOnward!  ', **changes}

    def accept_body(self, body, result):
        return {**body, 'proposal_digest': result['proposal']['proposal_digest'], 'explicitly_accepted': True}

    def lookup(self, body):
        return self.http('/api/ai/proposal-result/' + self.key + '/' + body['request_id'] + '?actor_id=pc')

    def test_two_consecutive_actions_are_real_core_and_private_context_stays_private(self):
        for action, intention in [('enter-passage', '  Into the passage.\n'), ('reach-desk', 'I approach the desk.')]:
            self.transport.action = action
            body = self.proposal(intention=intention)
            before = self.store.path(self.key).read_bytes()
            code, result = self.http('/api/ai/proposal', body)
            self.assertEqual((code, result['status']), (200, 'proposal_ready'))
            self.assertEqual(before, self.store.path(self.key).read_bytes())
            self.assertEqual(result['proposal']['intention'], intention)
            code, accepted = self.http('/api/ai/accept', self.accept_body(body, result))
            self.assertEqual((code, accepted['status']), (200, 'completed_successfully'))
            self.assertEqual(accepted['declaration'], intention)
            self.assertEqual(accepted['outcome']['summary'], 'Completed ' + action + '.')
            self.assertIsNone(accepted['narrative'])
            for public in (result, accepted, self.http('/api/playthrough/' + self.key)[1], self.transport.inputs):
                self.assertNotIn('PRIVATE_EVALUATOR_MARKER', json.dumps(public))
                self.assertNotIn('state_digest', json.dumps(public))
        saved = self.store.read(self.key)
        self.assertEqual(saved['revision'], 3)
        self.assertEqual(saved['state']['elapsed_time']['seconds'], 35)
        self.assertEqual(saved['state']['actors']['pc']['current']['location']['value'], 'desk')
        self.assertEqual(len(self.transport.inputs), 2)

    def test_lost_ack_restart_and_concurrent_accepts_recover_one_committed_result(self):
        body = self.proposal()
        _, proposal = self.http('/api/ai/proposal', body)
        acceptance = self.accept_body(body, proposal)
        _, original = self.http('/api/ai/accept', acceptance)  # Deliberately discard its ack.
        committed = self.store.path(self.key).read_bytes()
        self.stop()
        self.start()
        with ThreadPoolExecutor(max_workers=2) as pool:
            replies = list(pool.map(lambda _: self.http('/api/ai/accept', acceptance), range(2)))
        self.assertEqual(replies, [(200, original), (200, original)])
        result = self.http('/api/action-result/' + self.key + '/' + body['request_id'] + '?actor_id=pc')[1]
        self.assertEqual(result, original)
        self.assertEqual(self.lookup(body), (200, original))
        self.assertEqual(committed, self.store.path(self.key).read_bytes())
        self.assertEqual(len(self.transport.inputs), 1)

    def test_unknown_lookup_and_repeated_failed_request_never_dispatch_a_fresh_attempt(self):
        body = self.proposal()
        self.assertEqual(self.lookup(body)[1]['code'], 'unknown_request')
        self.assertEqual(self.transport.inputs, [])
        self.transport.error = 'provider_denied'
        before = self.store.path(self.key).read_bytes()
        for _ in range(2):
            self.assertEqual(self.http('/api/ai/proposal', body)[1]['code'], 'provider_denied')
        self.assertEqual(self.lookup(body)[1]['code'], 'provider_denied')
        self.assertEqual(len(self.transport.inputs), 1)
        self.assertEqual(before, self.store.path(self.key).read_bytes())

    def test_malformed_and_unsupported_output_never_commit(self):
        before = self.store.path(self.key).read_bytes()
        self.transport.malformed = True
        result = self.http('/api/ai/proposal', self.proposal())[1]
        self.assertEqual(result['status'], 'unavailable')
        self.transport.malformed = False
        self.transport.action = 'invented-resource-action'
        result = self.http('/api/ai/proposal', self.proposal())[1]
        self.assertEqual(result['status'], 'unavailable')
        self.assertEqual(before, self.store.path(self.key).read_bytes())

    def test_cancel_before_claim_and_during_output_is_durable_and_nonblocking(self):
        body = self.proposal()
        cancel = {k: body[k] for k in ('id', 'actor', 'request_id')}
        self.http('/api/ai/cancel', cancel)
        self.stop()
        self.start()
        self.assertEqual(self.http('/api/ai/proposal', body)[1]['code'], 'cancelled')
        self.assertEqual(self.transport.inputs, [])
        body = self.proposal()
        self.transport.release.clear()
        with ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(self.http, '/api/ai/proposal', body)
            self.assertTrue(self.transport.entered.wait(2))
            result = self.http('/api/ai/cancel', {k: body[k] for k in ('id', 'actor', 'request_id')})[1]
            self.assertEqual(result['code'], 'cancelled')
            self.transport.release.set()
            self.assertEqual(future.result()[1]['code'], 'cancelled')
        self.assertEqual(self.store.read(self.key)['revision'], 1)

    def test_world_write_while_provider_runs_fences_late_output(self):
        body = self.proposal()
        self.transport.release.clear()
        with ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(self.http, '/api/ai/proposal', body)
            self.assertTrue(self.transport.entered.wait(2))
            _, changed = self.http('/api/action', {'id': self.key, 'actor': 'pc', 'revision': 1,
                'request_id': 'parallel-action', 'kind': 'scene_action', 'action_id': 'look-quay',
                'text': 'I attempt look-quay.'})
            self.assertEqual(changed['status'], 'completed_successfully')
            self.transport.release.set()
            self.assertEqual(future.result()[1]['code'], 'stale_scope_or_state')
        self.assertEqual(self.store.read(self.key)['revision'], 2)

    def test_identical_trash_restore_invalidates_old_proposal_without_rewriting_save(self):
        body = self.proposal()
        _, proposal = self.http('/api/ai/proposal', body)
        before = self.store.path(self.key).read_bytes()
        self.http('/api/delete', {'id': self.key, 'revision': 1})
        self.assertEqual(self.lookup(body)[0], 404)
        self.http('/api/restore', {'id': self.key, 'revision': 1})
        self.assertEqual(before, self.store.path(self.key).read_bytes())
        self.assertEqual(self.lookup(body)[1]['code'], 'stale_scope_or_state')
        self.assertEqual(self.http('/api/ai/accept', self.accept_body(body, proposal))[1]['code'], 'stale_scope')
        self.assertEqual(before, self.store.path(self.key).read_bytes())

    def test_explicit_acceptance_exact_intent_and_fields_are_enforced(self):
        body = self.proposal()
        self.assertEqual(self.http('/api/ai/proposal', {**body, 'context': {'raw_world': 'forged'}})[0], 400)
        self.assertEqual(self.http('/api/ai/proposal', {**body, 'actor': 'not-player'})[0], 403)
        _, proposal = self.http('/api/ai/proposal', body)
        acceptance = self.accept_body(body, proposal)
        for changes, code in [({'explicitly_accepted': False}, 'acceptance_required'),
                              ({'intention': 'different'}, 'acceptance_changed'),
                              ({'proposal_digest': 'wrong'}, 'acceptance_changed')]:
            self.assertEqual(self.http('/api/ai/accept', {**acceptance, **changes})[1]['code'], code)
        self.assertEqual(self.store.read(self.key)['revision'], 1)

    def test_save_failure_then_retry_reuses_proposal_and_executes_once(self):
        body = self.proposal()
        _, proposal = self.http('/api/ai/proposal', body)
        acceptance = self.accept_body(body, proposal)
        before = self.store.path(self.key).read_bytes()
        with patch.object(Store, 'write', side_effect=OSError('synthetic disk failure')):
            self.assertEqual(self.http('/api/ai/accept', acceptance)[0], 503)
        self.assertEqual(before, self.store.path(self.key).read_bytes())
        self.assertEqual(self.http('/api/ai/accept', acceptance)[1]['status'], 'completed_successfully')
        self.assertEqual(self.store.read(self.key)['revision'], 2)
        self.assertEqual(len(self.transport.inputs), 1)

    def test_timeout_late_output_and_retry_do_not_create_a_new_attempt(self):
        self.stop()
        self.config = replace(self.config, deadline_seconds=0.04)
        self.start()
        body = self.proposal()
        self.transport.release.clear()
        result = self.http('/api/ai/proposal', body)[1]
        self.assertEqual(result['code'], 'deadline_exceeded')
        self.transport.release.set()
        self.assertEqual(self.http('/api/ai/proposal', body)[1]['code'], 'deadline_exceeded')
        self.assertEqual(len(self.transport.inputs), 1)
        self.assertEqual(self.store.read(self.key)['revision'], 1)


if __name__ == '__main__':
    unittest.main()
