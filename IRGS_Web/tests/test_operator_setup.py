"""Explicit protected configuration and synthetic transport through the real host."""
import json
import os
from pathlib import Path
import sys
import subprocess
import tempfile
import threading
import unittest
import uuid
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from server import Store, make_server
from test_scene_actions import fixture
from openai_proposals import ADAPTER_VERSION, CHECKED_MODEL, HTTPReply
from operator_setup import load_operator_configuration
from solo_provider import LOCAL_OPERATION, RISE_OPERATION, SCHEMA_VERSION, TASK


@unittest.skipIf(os.name == 'nt', 'POSIX protected-file checks require a separate Windows ACL implementation')
class OperatorSetupTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='irgs-operator-')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.profile = self.root / 'operator.json'
        self.data = {'schema_version': 1, 'enabled': True, 'model': CHECKED_MODEL,
            'adapter_version': ADAPTER_VERSION, 'workload': TASK, 'proposal_schema': SCHEMA_VERSION,
            'classification': 'synthetic-approved', 'policy_ref': 'synthetic-policy',
            'approval_ref': 'synthetic-approval', 'config_version': 'v1', 'price_revision': 'synthetic-price',
            'budget_units': 10, 'reservation_units': 10, 'max_output_tokens': 512, 'max_inflight': 1,
            'deadline_seconds': 30, 'private_dir': str(self.root / 'technical'),
            'operations': [LOCAL_OPERATION, RISE_OPERATION]}
        self.write(self.data)
        self.calls = []
        self.env = patch.dict(os.environ, {'OPENAI_API_KEY': 'SYNTHETIC-SECRET-NEVER-DISPLAY'})
        self.env.start(); self.addCleanup(self.env.stop)
        self.mock = patch('openai_proposals._http_post', side_effect=self.fake_post)
        self.mock.start(); self.addCleanup(self.mock.stop)
        self.store = Store(self.root / 'saves')
        world = fixture(); world.s['player_actor_ids'] = ['pc']
        self.key = uuid.uuid4().hex
        self.store.write({'id': self.key, 'name': 'Selected test context', 'revision': 1, 'state': world.s})
        self.server = None
        self.addCleanup(self.stop)

    def write(self, value):
        self.profile.write_text(json.dumps(value)); self.profile.chmod(0o600)

    def fake_post(self, request, *, timeout):
        self.calls.append(request)
        payload = json.loads(request.data)
        received = json.loads(payload['input'][0]['content'][0]['text'])
        action = next(item for item in ('enter-passage', 'inspect') if item in received['allowed_actions'])
        proposal = {'intention': received['intention'], 'action_id': action,
                    'source_refs': received['source_refs'][:1]}
        response = {'id': 'resp_synthetic', 'model': CHECKED_MODEL, 'status': 'completed', 'error': None,
            'usage': {'input_tokens': 5, 'output_tokens': 5}, 'output': [{'type': 'message',
            'role': 'assistant', 'status': 'completed', 'content': [{'type': 'output_text',
            'text': json.dumps(proposal)}]}]}
        return HTTPReply(200, json.dumps(response).encode(), 'req_synthetic')

    def start(self, profile=True):
        self.server = make_server(0, self.store.folder, operator_config_path=self.profile if profile else None)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True); self.thread.start()
        self.url = 'http://127.0.0.1:' + str(self.server.server_port)
        self.token = self.http('/api/campaigns')[1]['token']

    def stop(self):
        if self.server:
            self.server.shutdown(); self.server.server_close(); self.thread.join(); self.server = None

    def http(self, path, body=None, token=True):
        headers = {'X-IRGS-Token': getattr(self, 'token', '')} if token else {}
        if body is not None: headers['Content-Type'] = 'application/json'
        request = Request(self.url + path, data=json.dumps(body).encode() if body is not None else None, headers=headers)
        try:
            with urlopen(request, timeout=10) as response: return response.status, json.load(response)
        except HTTPError as error: return error.code, json.load(error)

    def test_exact_configuration_validated_without_provider_calls_or_secret_output(self):
        self.start()
        public = self.http('/api/ai/status')[1]
        creator = self.http('/api/ai/status?mode=creator')[1]
        self.assertTrue(public['available']); self.assertNotIn('diagnostics', public)
        self.assertIn('received context', public['message'])
        self.assertIn('budget reservation', public['message'])
        self.assertEqual(creator['diagnostics']['reason_code'], 'ready')
        self.assertEqual(creator['diagnostics']['model'], CHECKED_MODEL)
        self.assertEqual(creator['diagnostics']['workload'], TASK)
        self.assertEqual(self.http('/api/ai/status?mode=creator', token=False)[0], 403)
        self.assertNotIn('SYNTHETIC-SECRET', json.dumps([public, creator]))
        self.assertNotIn(str(self.root), json.dumps([public, creator]))
        self.assertEqual(self.calls, [])
        with patch.dict(os.environ, {'OPENAI_API_KEY': ''}):
            self.assertFalse(self.http('/api/ai/status')[1]['available'])
            self.assertEqual(self.http('/api/ai/status?mode=creator')[1]['diagnostics']['reason_code'], 'credential_unavailable')
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'synthetic\nheader'}):
            self.assertFalse(self.http('/api/ai/status')[1]['available'])
        self.assertEqual(self.calls, [])

    def test_non_regular_profile_is_rejected_without_waiting_for_a_writer(self):
        self.profile.unlink(); os.mkfifo(self.profile, 0o600)
        with self.assertRaises(ValueError): load_operator_configuration(self.profile, self.store.folder)
        self.assertEqual(self.calls, [])

    def test_running_host_keeps_its_configuration_until_restart(self):
        self.start()
        self.assertEqual(self.http('/api/ai/status?mode=creator')[1]['diagnostics']['reason_code'], 'ready')
        self.write({**self.data, 'model': 'changed-unreviewed-model'})
        self.assertEqual(self.http('/api/ai/status?mode=creator')[1]['diagnostics']['reason_code'], 'ready')
        self.stop(); self.start()
        self.assertEqual(self.http('/api/ai/status?mode=creator')[1]['diagnostics']['reason_code'], 'invalid_operator_configuration')
        self.assertEqual(self.calls, [])

    def test_command_line_validation_never_starts_host_or_creates_ledger(self):
        command = [sys.executable, '-B', str(Path(__file__).resolve().parents[1] / 'server.py'),
                   '--operator-config', str(self.profile), '--check-operator-config']
        result = subprocess.run(command, capture_output=True, text=True, timeout=20, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('No provider request was made', result.stdout)
        self.assertNotIn('SYNTHETIC-SECRET', result.stdout + result.stderr)
        self.assertNotIn(str(self.profile), result.stdout + result.stderr)
        self.assertFalse((self.root / 'technical').exists()); self.assertEqual(self.calls, [])
        self.write({**self.data, 'model': 'unreviewed'})
        result = subprocess.run(command, capture_output=True, text=True, timeout=20, check=False)
        self.assertNotEqual(result.returncode, 0); self.assertNotIn(str(self.profile), result.stderr)
        self.assertFalse((self.root / 'technical').exists())

    def test_bad_model_workload_limits_keys_and_permissions_fail_closed_offline(self):
        bad = [{'model': 'unreviewed-alias'}, {'workload': 'narration'}, {'enabled': False},
               {'budget_units': 0}, {'reservation_units': 11}, {'max_output_tokens': True},
               {'operations': [LOCAL_OPERATION, 'arbitrary']}, {'proposal_schema': 'unreviewed'},
               {'api_key': 'PRIVATE-LEAK-ATTEMPT'}, {'private_dir': str(self.store.folder)}]
        for change in bad:
            with self.subTest(change=change):
                self.write({**self.data, **change})
                with self.assertRaises(ValueError): load_operator_configuration(self.profile, self.store.folder)
        self.write(self.data); self.profile.chmod(0o644)
        self.start(); self.assertFalse(self.http('/api/ai/status')[1]['available'])
        status = self.http('/api/ai/status?mode=creator')[1]
        self.assertEqual(status['diagnostics']['reason_code'], 'invalid_operator_configuration')
        self.assertNotIn('PRIVATE-LEAK-ATTEMPT', json.dumps(status)); self.assertEqual(self.calls, [])
        view = self.http('/api/playthrough/' + self.key + '?actor_id=pc')[1]
        action = next(row for row in view['supported_actions'] if row['action_id'] == 'enter-passage')
        code, result = self.http('/api/action', {'id': self.key, 'actor': 'pc', 'revision': view['revision'],
            'request_id': uuid.uuid4().hex, 'kind': 'scene_action', 'action_id': action['action_id'], 'text': action['text']})
        self.assertEqual((code, result['status']), (200, 'completed_successfully'))
        self.assertEqual(self.calls, [])

    def test_operation_selection_does_not_advertise_an_unapproved_rise_workload(self):
        from rise_campaigns import create
        from settlement_setup import preview
        from test_settlement import choices
        selected = choices(); reviewed = preview(selected)
        rise = create(self.store, {'name': 'Ordinary Rise', 'choices': selected,
            'review_digest': reviewed['review_digest'], 'request_id': uuid.uuid4().hex})['id']
        self.write({**self.data, 'operations': [LOCAL_OPERATION]}); self.start()
        self.assertTrue(self.http('/api/playthrough/' + self.key + '?actor_id=pc')[1]['assistance']['available'])
        self.assertFalse(self.http('/api/playthrough/' + rise + '?actor_id=founder')[1]['assistance']['available'])
        self.assertEqual(self.calls, [])

    def test_approved_rise_workload_uses_review_and_real_core_once(self):
        from rise_campaigns import create
        from settlement_setup import preview
        from test_settlement import choices
        selected = choices(); reviewed = preview(selected)
        rise = create(self.store, {'name': 'Ordinary Rise', 'choices': selected,
            'review_digest': reviewed['review_digest'], 'request_id': uuid.uuid4().hex})['id']
        self.start(); view = self.http('/api/playthrough/' + rise + '?actor_id=founder')[1]
        before = self.store.path(rise).read_bytes()
        body = {'id': rise, 'actor': 'founder', 'revision': view['revision'],
                'request_id': uuid.uuid4().hex, 'intention': 'I inspect my surroundings.'}
        code, proposal = self.http('/api/ai/proposal', body)
        self.assertEqual((code, proposal['status']), (200, 'proposal_ready'))
        self.assertEqual(proposal['proposal']['action_id'], 'inspect')
        self.assertEqual(before, self.store.path(rise).read_bytes())
        accept = {**body, 'proposal_digest': proposal['proposal']['proposal_digest'], 'explicitly_accepted': True}
        code, result = self.http('/api/ai/accept', accept)
        self.assertEqual((code, result['status']), (200, 'completed_successfully'))
        saved = self.store.path(rise).read_bytes()
        self.assertEqual(self.http('/api/ai/accept', accept), (200, result))
        self.assertEqual(self.store.path(rise).read_bytes(), saved); self.assertEqual(len(self.calls), 1)

    def test_review_explicit_acceptance_budget_and_restart_recover_once(self):
        self.start(); before = self.store.path(self.key).read_bytes()
        body = {'id': self.key, 'actor': 'pc', 'revision': 1, 'request_id': uuid.uuid4().hex,
                'intention': '  I take the passage.\nCarefully.  '}
        code, proposal = self.http('/api/ai/proposal', body)
        self.assertEqual((code, proposal['status']), (200, 'proposal_ready'))
        self.assertEqual(before, self.store.path(self.key).read_bytes()); self.assertEqual(len(self.calls), 1)
        self.assertNotIn('SYNTHETIC-SECRET', self.calls[0].data.decode())
        self.assertNotIn('SYNTHETIC-SECRET', json.dumps(proposal))
        self.assertEqual(self.http('/api/ai/status?mode=creator')[1]['diagnostics']['reason_code'], 'budget_exhausted')
        accept = {**body, 'proposal_digest': proposal['proposal']['proposal_digest'], 'explicitly_accepted': True}
        code, result = self.http('/api/ai/accept', accept)
        self.assertEqual((code, result['status']), (200, 'completed_successfully'))
        self.assertEqual(result['declaration'], body['intention']); committed = self.store.path(self.key).read_bytes()
        self.stop(); self.start()
        self.assertEqual(self.http('/api/ai/accept', accept), (200, result))
        self.assertEqual(self.store.path(self.key).read_bytes(), committed); self.assertEqual(len(self.calls), 1)
        self.assertEqual(self.http('/api/ai/status?mode=creator')[1]['diagnostics']['reason_code'], 'budget_exhausted')
        self.assertEqual(self.http('/api/ai/proposal', {**body, 'request_id': uuid.uuid4().hex, 'revision': 2})[1]['code'], 'budget_exhausted')
        self.assertEqual(self.calls[0].get_header('Authorization'), 'Bearer SYNTHETIC-SECRET-NEVER-DISPLAY')
        self.assertNotIn('SYNTHETIC-SECRET', (self.root / 'technical' / 'inference.sqlite').read_bytes().decode('latin-1'))
