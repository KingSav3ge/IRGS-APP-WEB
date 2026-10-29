"""Versioned communication review/results over the durable, actor-scoped host."""
import copy
import json
import unittest
import uuid
from unittest.mock import patch

import test_communication_bridge as legacy
from communication_bridge import CommunicationService
from server import Store


class CommunicationIntentTests(unittest.TestCase):
    setUp = legacy.CommunicationBridgeTests.setUp
    start = legacy.CommunicationBridgeTests.start
    stop = legacy.CommunicationBridgeTests.stop
    http = legacy.CommunicationBridgeTests.http
    view = legacy.CommunicationBridgeTests.view
    accepted = legacy.CommunicationBridgeTests.accepted

    def prepare(self, **changes):
        view = self.view(); control = view['communication_control']
        self.assertEqual(control['intent_schema_version'], 'irgs-supported-intent-1')
        body = {'id':self.quay, 'actor':'pc', 'revision':view['revision'], 'view_token':control['view_token'],
            'request_id':uuid.uuid4().hex, 'channel_id':'quay', 'recipient':'witness', 'command':'speak',
            'details':{}, 'intention':'  Exact words.\nNo silent rewrite.  ', **changes}
        code, packet = self.http('/api/communication/intent/prepare', body)
        self.assertEqual(code, 200, packet)
        return body, packet

    def test_exact_review_and_durable_dto_recover_after_restart_and_later_work(self):
        before = self.store.path(self.quay).read_bytes()
        body, packet = self.prepare(); review = packet['intent_review']
        self.assertEqual(review['schema_version'], 'irgs-supported-intent-1')
        self.assertEqual(review['status'], 'supported'); self.assertEqual(review['intention'], body['intention'])
        self.assertEqual(review['selection']['operation_id'], 'execute_local_communication')
        self.assertEqual(self.store.path(self.quay).read_bytes(), before)
        self.assertEqual(self.http('/api/communication/intent/prepare', body), (200, packet))
        for value in (False, 1, 'true'):
            self.assertEqual(self.http('/api/communication/execute', self.accepted(body, explicitly_accepted=value))[0], 400)
        code, result = self.http('/api/communication/execute', self.accepted(body)); self.assertEqual(code, 200, result)
        dto = result['intent_result']
        self.assertEqual(dto['schema_version'], review['schema_version']); self.assertEqual(dto['intention'], body['intention'])
        self.assertEqual(dto['communication'], result['communication']); self.assertEqual(dto['status'], 'testimony_received')
        self.assertEqual(dto['receipt'], result['communication']['receipt'])
        self.assertEqual(self.view()['completed_actions'][-1], result)
        second, _ = self.prepare(intention='A later separate speech.')
        self.assertEqual(self.http('/api/communication/execute', self.accepted(second))[0], 200)
        saved = self.store.path(self.quay).read_bytes(); self.stop(); self.start()
        self.assertEqual(self.http('/api/communication/execute', self.accepted(body)), (200, result))
        self.assertEqual(self.http('/api/action-result/'+self.quay+'/'+body['request_id']+'?actor_id=pc'), (200, result))
        self.assertEqual(self.store.path(self.quay).read_bytes(), saved)
        for private in ('state_digest', 'restore_id', 'params_digest', 'PRIVATE_'):
            self.assertNotIn(private, json.dumps(packet)+json.dumps(result))

    def test_unsupported_and_clarification_do_not_prepare_or_commit(self):
        before = self.store.path(self.quay).read_bytes()
        for changes, status in [({'command':'invented'}, 'unsupported'),
                                ({'recipient':None}, 'clarification_required'),
                                ({'details':{'extra':'not valid speech'}}, 'clarification_required')]:
            body, packet = self.prepare(**changes)
            self.assertEqual(packet['status'], status); self.assertEqual(packet['intent_review']['status'], status)
            self.assertIsNone(CommunicationService(self.store).row(self.quay, body['request_id']))
            self.assertEqual(self.http('/api/communication/execute', self.accepted(body))[0], 403)
        self.assertEqual(self.store.path(self.quay).read_bytes(), before)
        self.dispatch.assert_not_called()

    def test_contract_identity_cannot_be_reinterpreted_and_legacy_pending_recovers(self):
        old_body, old_packet = legacy.CommunicationBridgeTests.prepared(self)
        self.assertNotIn('intent_review', old_packet)
        self.assertEqual(self.http('/api/communication/intent/prepare', old_body)[0], 400)
        self.stop(); self.start()
        code, old_result = self.http('/api/communication/execute', self.accepted(old_body)); self.assertEqual(code, 200)
        self.assertNotIn('intent_result', old_result)
        new_body, _ = self.prepare()
        self.assertEqual(self.http('/api/communication/prepare', new_body)[0], 400)
        self.assertEqual(self.http('/api/communication/intent/prepare', {**new_body,'intention':'Changed words'})[0], 400)
        self.assertEqual(self.http('/api/communication/execute', self.accepted(new_body))[0], 200)
        self.assertEqual(self.http('/api/communication/execute', self.accepted(old_body)), (200, old_result))

    def test_new_route_keeps_authentication_and_server_owned_fields(self):
        body, packet = self.prepare()
        before = self.store.path(self.quay).read_bytes()
        self.assertEqual(self.http('/api/communication/intent/prepare', body, token=False)[0], 403)
        self.assertEqual(self.http('/api/communication/intent/prepare', body, headers={'Origin':'https://outside.invalid'})[0], 403)
        for field, value in [('source_ref','forged'), ('review_id',packet['intent_review']['review_id']), ('scope',{})]:
            self.assertEqual(self.http('/api/communication/intent/prepare', {**body,field:value})[0], 400)
        self.assertEqual(self.http('/api/communication/status', {'id':self.quay,'actor':'witness','request_id':body['request_id']})[0], 403)
        self.assertEqual(self.store.path(self.quay).read_bytes(), before)

    def test_failed_persistence_restore_and_actual_presence_refusal(self):
        body, _ = self.prepare(); before = self.store.path(self.quay).read_bytes()
        with patch.object(Store, 'write', side_effect=OSError('Synthetic disk failure')):
            self.assertEqual(self.http('/api/communication/execute', self.accepted(body))[0], 503)
        self.assertEqual(self.store.path(self.quay).read_bytes(), before)
        self.stop(); self.start()
        code, status = self.http('/api/communication/status', {'id':self.quay,'actor':'pc','request_id':body['request_id']})
        self.assertEqual(code, 200); self.assertEqual(status['status'], 'save_failed'); self.assertEqual(status['intent_review']['status'], 'supported')
        self.assertEqual(self.http('/api/communication/execute', self.accepted(body))[0], 200)
        stale, _ = self.prepare(); revision = self.store.read(self.quay)['revision']
        self.http('/api/delete', {'id':self.quay,'revision':revision}); self.http('/api/restore', {'id':self.quay,'revision':revision})
        self.assertEqual(self.http('/api/communication/execute', self.accepted(stale))[0], 400)
        record = self.store.read(self.quay); record['state']['actors']['witness']['current']['location'] = 'PRIVATE_REMOTE'
        self.store.write(record)
        refused, packet = self.prepare(); self.assertEqual(packet['intent_review']['status'], 'supported')
        before = self.store.path(self.quay).read_bytes()
        code, error = self.http('/api/communication/execute', self.accepted(refused)); self.assertEqual(code, 400)
        self.assertNotIn('PRIVATE_REMOTE', json.dumps(error)); self.assertEqual(self.store.path(self.quay).read_bytes(), before)


if __name__ == '__main__': unittest.main()
