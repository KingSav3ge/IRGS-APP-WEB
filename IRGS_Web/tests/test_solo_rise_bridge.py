"""Actual Rise effects and persistence through the opt-in proposal HTTP bridge."""
from dataclasses import replace
import json
import unittest
from unittest.mock import patch

import test_solo_bridge as bridge


@unittest.skipUnless(bridge.SOLO_API, 'Selected Engine predates the Solo API')
class RiseSoloBridgeTests(unittest.TestCase):
    start = bridge.SoloBridgeTests.start
    stop = bridge.SoloBridgeTests.stop
    http = bridge.SoloBridgeTests.http
    proposal = bridge.SoloBridgeTests.proposal
    accept_body = bridge.SoloBridgeTests.accept_body

    def lookup(self, body):
        return self.http('/api/ai/proposal-result/' + self.key + '/' + body['request_id']
                         + '?actor_id=' + body['actor'])

    def setUp(self):
        bridge.SoloBridgeTests.setUp(self)
        self.stop()
        from settlement_setup import initialize, preview
        from test_settlement import choices
        from solo_provider import RISE_OPERATION
        selected = choices()
        selected['permission'] = 'held'
        world = initialize(selected, preview(selected)['review_digest'], 'synthetic-rise-bridge')
        self.store.write({'id': self.key, 'name': 'Synthetic Rise bridge',
                          'revision': 0, 'state': world.s})
        self.route = replace(self.route, operations=(RISE_OPERATION,))
        self.start()

    def proposed(self, action):
        self.transport.action = action
        body = self.proposal(actor='founder', intention='  I attempt ' + action + '.\n')
        before = self.store.path(self.key).read_bytes()
        code, result = self.http('/api/ai/proposal', body)
        self.assertEqual((code, result['status']), (200, 'proposal_ready'), result)
        self.assertEqual(before, self.store.path(self.key).read_bytes())
        return body, result

    def test_rise_status_and_continuing_work_use_actual_elapsed_spans_and_conserved_stock(self):
        view = self.http('/api/playthrough/' + self.key + '?actor_id=founder')[1]
        self.assertTrue(view['assistance']['available'])
        durations = []
        for action in ('walk_clearing', 'found', 'build', 'wait_hour', 'wait_hour'):
            body, proposal = self.proposed(action)
            acceptance = self.accept_body(body, proposal)
            code, result = self.http('/api/ai/accept', acceptance)
            self.assertEqual((code, result['status']), (200, 'completed_successfully'), result)
            self.assertEqual(result['kind'], 'settlement_action')
            self.assertEqual(result['elapsed_time']['axis'], 'settlement-seconds')
            self.assertEqual(result['declaration'], body['intention'])
            durations.append(result['elapsed_time']['seconds'])
            saved = self.store.path(self.key).read_bytes()
            self.stop()
            self.start()
            self.assertEqual(self.http('/api/ai/accept', acceptance), (200, result))
            self.assertEqual(self.lookup(body), (200, result))
            self.assertEqual(saved, self.store.path(self.key).read_bytes())
        self.assertEqual(durations, [300, 0, 0, 1500, 2100])
        record = self.store.read(self.key)
        self.assertEqual(record['revision'], 5)
        self.assertEqual(record['state']['elapsed_time']['seconds'], 3900)
        self.assertEqual(record['state']['projects']['shelter']['worked'], 3600)
        self.assertEqual(record['state']['stocks']['founder-home']['timber'], 3)
        for material, opening in record['state']['opening_stock'].items():
            consumed = sum(flow['quantity'] for flow in record['state']['material_flows'].values()
                           if flow['material'] == material)
            self.assertEqual(sum(stock.get(material, 0) for stock in record['state']['stocks'].values())
                             + consumed, opening)
        for public in [self.transport.inputs, view, result]:
            self.assertNotIn('oren-home', json.dumps(public))
            self.assertNotIn('opening_npc_inventory', json.dumps(public))
        self.assertEqual(len(self.transport.inputs), 5)

    def test_denied_and_unsupported_rise_proposals_have_no_effects(self):
        body, proposal = self.proposed('build')
        before = self.store.path(self.key).read_bytes()
        code, result = self.http('/api/ai/accept', self.accept_body(body, proposal))
        self.assertEqual((code, result['code']), (422, 'action_unavailable'))
        self.transport.action = 'invent_grain'
        result = self.http('/api/ai/proposal', self.proposal(actor='founder'))[1]
        self.assertEqual(result['code'], 'unsupported_action')
        self.assertEqual(before, self.store.path(self.key).read_bytes())

    def test_failed_rise_persistence_retries_the_same_proposal_without_another_dispatch(self):
        from server import Store
        body, proposal = self.proposed('walk_clearing')
        acceptance = self.accept_body(body, proposal)
        before = self.store.path(self.key).read_bytes()
        with patch.object(Store, 'write', side_effect=OSError('synthetic failed write')):
            self.assertEqual(self.http('/api/ai/accept', acceptance)[0], 503)
        self.assertEqual(before, self.store.path(self.key).read_bytes())
        self.assertEqual(self.http('/api/ai/accept', acceptance)[1]['status'], 'completed_successfully')
        self.assertEqual(self.store.read(self.key)['revision'], 1)
        self.assertEqual(len(self.transport.inputs), 1)
