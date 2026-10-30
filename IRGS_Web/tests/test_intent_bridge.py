"""Actor-scoped shared Engine review through the actual local host."""
import copy
from concurrent.futures import ThreadPoolExecutor
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
from test_scene_actions import fixture
from settlement_setup import preview
from rise_campaigns import create as create_rise
from test_settlement import choices


class IntentBridgeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='irgs-intent-http-'); self.addCleanup(self.tmp.cleanup)
        self.store = Store(Path(self.tmp.name) / 'saves')
        world = fixture(); world.s['player_actor_ids'] = ['pc']
        self.scene = uuid.uuid4().hex
        self.store.write({'id': self.scene, 'name': 'Synthetic scene', 'revision': 1, 'state': world.s})
        selected = choices(); review = preview(selected)
        self.rise = create_rise(self.store, {'name': 'Ordinary Rise', 'choices': selected,
            'review_digest': review['review_digest'], 'request_id': uuid.uuid4().hex})['id']
        self.start(); self.addCleanup(self.stop)

    def start(self):
        self.server = make_server(0, self.store.folder)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True); self.thread.start()
        self.url = 'http://127.0.0.1:' + str(self.server.server_port)
        self.token = self.http('/api/campaigns')[1]['token']

    def stop(self):
        self.server.shutdown(); self.server.server_close(); self.thread.join()

    def http(self, path, body=None):
        headers = {'X-IRGS-Token': getattr(self, 'token', '')}
        if body is not None: headers['Content-Type'] = 'application/json'
        request = Request(self.url + path, data=json.dumps(body).encode() if body is not None else None, headers=headers)
        try:
            with urlopen(request, timeout=10) as response: return response.status, json.load(response)
        except HTTPError as error: return error.code, json.load(error)

    def view(self, key, actor):
        code, result = self.http('/api/playthrough/' + key + '?actor_id=' + actor)
        self.assertEqual(code, 200, result); return result

    def prepare(self, key, actor, action_id=None, text='  My exact edited intention.\nNo automatic choice.  '):
        view = self.view(key, actor); packet = view['intent_control']
        cap = next((c for c in packet['capabilities'] if c['action'].get('action_id') == action_id), None) if action_id else None
        if action_id: self.assertIsNotNone(cap)
        body = {'id': key, 'actor': actor, 'revision': view['revision'], 'view_token': packet['view_token'],
                'request_id': uuid.uuid4().hex, 'intention': text, 'capability_id': cap['capability_id'] if cap else None}
        code, prepared = self.http('/api/intent/prepare', body); self.assertEqual(code, 200, prepared)
        return body, prepared

    def accept(self, body, value=True):
        return {'id': body['id'], 'actor': body['actor'], 'request_id': body['request_id'], 'explicitly_accepted': value}

    def test_scene_review_exact_words_atomic_commit_and_original_recovery(self):
        before = self.store.path(self.scene).read_bytes(); body, review = self.prepare(self.scene, 'pc', 'enter-passage')
        self.assertEqual(review['intention'], body['intention']); self.assertEqual(review['capability']['action']['action_id'], 'enter-passage')
        self.assertEqual(self.store.path(self.scene).read_bytes(), before)
        self.assertEqual(self.http('/api/intent/prepare', body), (200, review))
        self.assertEqual(self.http('/api/intent/prepare', {**body, 'intention': 'changed'})[0], 400)
        self.assertEqual(self.http('/api/intent/prepare', {**body, 'source_ref': 'forged'})[0], 400)
        for value in (False, 1, 'true'): self.assertEqual(self.http('/api/intent/execute', self.accept(body, value))[0], 400)
        code, result = self.http('/api/intent/execute', self.accept(body)); self.assertEqual(code, 200, result)
        self.assertEqual(result['status'], 'completed_successfully'); self.assertEqual(result['declaration'], body['intention'])
        self.assertEqual(self.view(self.scene, 'pc')['completed_actions'][-1], result)
        saved = self.store.path(self.scene).read_bytes(); self.stop(); self.start()
        self.assertEqual(self.http('/api/intent/execute', self.accept(body)), (200, result))
        self.assertEqual(self.http('/api/action-result/' + self.scene + '/' + body['request_id'] + '?actor_id=pc'), (200, result))
        self.assertEqual(self.store.path(self.scene).read_bytes(), saved)

    def test_unresolved_declaration_stays_pending_and_can_be_withdrawn(self):
        body, review = self.prepare(self.scene, 'pc', text='I attempt an unsupported conversation.')
        self.assertEqual(review['capability']['operation_id'], 'record_player_action')
        code, result = self.http('/api/intent/execute', self.accept(body)); self.assertEqual(code, 200, result)
        self.assertEqual(result['status'], 'declared_not_resolved')
        view = self.view(self.scene, 'pc'); self.assertEqual(view['pending_declaration']['request_id'], body['request_id'])
        withdrawal = {'id': self.scene, 'actor': 'pc', 'revision': view['revision'],
                      'request_id': uuid.uuid4().hex, 'action_request_id': body['request_id']}
        self.assertEqual(self.http('/api/withdraw-declaration', withdrawal)[0], 200)
        self.assertIsNone(self.view(self.scene, 'pc')['pending_declaration'])

    def test_rise_action_and_stale_review_are_actor_scoped(self):
        body, review = self.prepare(self.rise, 'founder', 'inspect')
        before = copy.deepcopy(self.store.read(self.rise)['state']['stocks'])
        code, result = self.http('/api/intent/execute', self.accept(body)); self.assertEqual(code, 200, result)
        self.assertEqual(result['status'], 'completed_successfully')
        self.assertEqual(self.store.read(self.rise)['state']['stocks'], before)
        self.assertEqual(self.http('/api/intent/status', {'id': self.rise, 'actor': 'oren', 'request_id': body['request_id']})[0], 403)
        stale, _ = self.prepare(self.rise, 'founder', 'inspect'); record = self.store.read(self.rise)
        record['revision'] += 1; self.store.write(record)
        self.assertEqual(self.http('/api/intent/execute', self.accept(stale))[0], 400)

    def test_grant_attempt_view_is_own_read_only_information_without_an_offer_oracle(self):
        before = self.store.path(self.rise).read_bytes()
        grants = self.view(self.rise, 'founder')['intent_control']['grant_prerequisites']
        self.assertEqual(grants['actor_id'], 'founder')
        self.assertEqual(grants['schema_version'], 'irgs-grant-offer-prerequisites-1')
        self.assertEqual({item['action_id'] for item in grants['actions']}, {'request_grant', 'accept_grant'})
        self.assertEqual(grants['offer_status'], 'not_inspected')
        self.assertEqual(grants['consent_status'], 'not_inferred')
        self.assertFalse(grants['committed'])
        self.assertTrue(grants['explicit_acceptance_required'])
        self.assertEqual(self.store.path(self.rise).read_bytes(), before)
        self.assertEqual(self.view(self.scene, 'pc')['intent_control']['grant_prerequisites']['actions'], [])
        self.assertEqual(self.http('/api/playthrough/' + self.rise + '?actor_id=oren')[0], 403)
        record = self.store.read(self.rise)
        # A conserved synthetic alternative; this does not execute a product transfer.
        record['state']['stocks']['oren-home']['grain'] += 1
        record['state']['stocks']['founder-home']['grain'] -= 1
        self.store.write(record)
        self.assertEqual(self.view(self.rise, 'founder')['intent_control']['grant_prerequisites'], grants)

    def test_grant_acceptance_is_separate_rejects_without_offer_and_replays_original_request(self):
        body, _ = self.prepare(self.rise, 'founder', 'accept_grant', 'I accept the terms I received.')
        before = self.store.path(self.rise).read_bytes()
        self.assertEqual(self.http('/api/intent/execute', self.accept(body))[0], 400)
        self.assertEqual(self.store.path(self.rise).read_bytes(), before)
        request, _ = self.prepare(self.rise, 'founder', 'request_grant', 'I request permission for the camp.')
        self.assertFalse(self.store.read(self.rise)['state']['grants'])
        code, offered = self.http('/api/intent/execute', self.accept(request))
        self.assertEqual(code, 200, offered)
        self.assertEqual(self.store.read(self.rise)['state']['grants']['founding']['status'], 'offered')
        acceptance, _ = self.prepare(self.rise, 'founder', 'accept_grant', 'I accept the limited founding grant.')
        self.assertEqual(self.http('/api/intent/execute', self.accept(acceptance, False))[0], 400)
        self.assertEqual(self.store.read(self.rise)['state']['grants']['founding']['status'], 'offered')
        self.assertEqual(self.http('/api/intent/execute', self.accept(acceptance))[0], 200)
        self.assertEqual(self.store.read(self.rise)['state']['grants']['founding']['status'], 'accepted')
        saved = self.store.path(self.rise).read_bytes(); self.stop(); self.start()
        self.assertEqual(self.http('/api/intent/execute', self.accept(request)), (200, offered))
        self.assertEqual(self.store.path(self.rise).read_bytes(), saved)

    def test_restore_invalidates_uncommitted_request_without_changing_save(self):
        body, _ = self.prepare(self.scene, 'pc', 'enter-passage'); before = self.store.path(self.scene).read_bytes()
        self.assertEqual(self.http('/api/delete', {'id': self.scene, 'revision': 1})[0], 200)
        self.assertEqual(self.http('/api/restore', {'id': self.scene, 'revision': 1})[0], 200)
        self.assertEqual(self.store.path(self.scene).read_bytes(), before)
        self.assertEqual(self.http('/api/intent/execute', self.accept(body))[0], 400)
        future, _ = self.prepare(self.scene, 'pc', 'enter-passage')
        self.assertEqual(self.http('/api/intent/execute', self.accept(future))[0], 200)
        self.store.path(self.scene).write_bytes(before)  # Synthetic older checkpoint, never a user save.
        self.assertEqual(self.http('/api/delete', {'id': self.scene, 'revision': 1})[0], 200)
        self.assertEqual(self.http('/api/restore', {'id': self.scene, 'revision': 1})[0], 200)
        self.assertEqual(self.http('/api/intent/execute', self.accept(future))[0], 400)
        self.assertEqual(self.store.path(self.scene).read_bytes(), before)

    def test_failed_save_restart_and_uncertain_sync_recover_original_once(self):
        body, _ = self.prepare(self.scene, 'pc', 'enter-passage'); before = self.store.path(self.scene).read_bytes()
        with patch.object(Store, 'write', side_effect=OSError('synthetic disk failure')):
            self.assertEqual(self.http('/api/intent/execute', self.accept(body))[0], 503)
        self.assertEqual(self.store.path(self.scene).read_bytes(), before)
        self.stop(); self.start()
        status = self.http('/api/intent/status', {'id': self.scene, 'actor': 'pc', 'request_id': body['request_id']})
        self.assertEqual(status[1]['status'], 'save_failed')
        code, result = self.http('/api/intent/execute', self.accept(body)); self.assertEqual(code, 200, result)
        saved = self.store.path(self.scene).read_bytes()
        self.assertEqual(self.http('/api/intent/execute', self.accept(body)), (200, result))
        self.assertEqual(self.store.path(self.scene).read_bytes(), saved)
        second, _ = self.prepare(self.scene, 'pc', 'reach-desk')
        with patch('server.sync_parent', side_effect=OSError('uncertain directory sync')):
            self.assertEqual(self.http('/api/intent/execute', self.accept(second))[0], 503)
        accepted = self.store.read(self.scene)['gameplay_requests'][second['request_id']]['result']
        self.assertEqual(self.http('/api/action-result/' + self.scene + '/' + second['request_id'] + '?actor_id=pc'), (200, accepted))
        self.assertEqual(self.http('/api/intent/execute', self.accept(second)), (200, accepted))

    def test_concurrent_requests_have_one_winner_and_exact_duplicate_result(self):
        first, _ = self.prepare(self.scene, 'pc', 'enter-passage'); second, _ = self.prepare(self.scene, 'pc', 'enter-passage')
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda body: self.http('/api/intent/execute', self.accept(body)), [first, second]))
        self.assertEqual(sorted(code for code, _ in results), [200, 400])
        winner = first if results[0][0] == 200 else second; original = next(result for code, result in results if code == 200)
        with ThreadPoolExecutor(max_workers=2) as pool:
            retries = list(pool.map(lambda _: self.http('/api/intent/execute', self.accept(winner)), range(2)))
        self.assertEqual(retries, [(200, original), (200, original)])
