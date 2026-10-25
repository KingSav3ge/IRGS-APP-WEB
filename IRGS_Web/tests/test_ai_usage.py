"""Protected read-only accounting over the real Engine ledger, offline only."""
import json
import sqlite3
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from unittest.mock import patch

import test_solo_bridge as bridge


@unittest.skipUnless(bridge.SOLO_API, 'Selected Engine predates Solo ledger API')
class AIUsageTests(unittest.TestCase):
    setUp = bridge.SoloBridgeTests.setUp
    start = bridge.SoloBridgeTests.start
    stop = bridge.SoloBridgeTests.stop
    http = bridge.SoloBridgeTests.http
    proposal = bridge.SoloBridgeTests.proposal

    def usage(self, suffix=''):
        return self.http('/api/ai/usage?mode=creator' + suffix)

    def test_authorization_precedes_ledger_access_and_diagnostics_are_absent_from_player(self):
        self.assertEqual(self.http('/api/ai/usage')[0], 403)
        for headers in ({}, {'X-IRGS-Token': self.token, 'Origin': 'https://invalid.example'}):
            with self.assertRaises(HTTPError) as caught:
                urlopen(Request(self.url + '/api/ai/usage?mode=creator', headers=headers), timeout=5)
            self.assertEqual(caught.exception.code, 403)
        player = self.http('/api/playthrough/' + self.key)[1]
        self.assertNotIn('diagnostics', player['assistance'])
        self.assertNotIn('budget_units', json.dumps(player))
        self.assertEqual(self.transport.inputs, [])

    def test_inspection_reports_reserved_and_reported_units_without_dispatch_or_save_write(self):
        body = self.proposal(intention='PRIVATE_INTENTION_MUST_NOT_APPEAR')
        self.http('/api/ai/proposal', body)
        before = self.store.path(self.key).read_bytes()
        for _ in range(2):
            code, report = self.usage()
            self.assertEqual(code, 200)
            self.assertEqual(report['summary']['reserved_units'], 10)
            self.assertEqual(report['summary']['remaining_units'], 90)
            self.assertEqual(report['summary']['attempts_total'], 1)
            row = report['attempts'][0]
            self.assertEqual(row['requested_identity']['model'], 'fixture-v1')
            self.assertEqual(row['reported_identity']['model'], 'fixture-v1')
            self.assertEqual(row['reported_tokens']['input_tokens'], 20)
            self.assertIsNone(row['reported_tokens']['cached_input_tokens'])
            self.assertEqual(row['billing_status'], 'unknown')
            for hidden in ('PRIVATE_INTENTION_MUST_NOT_APPEAR', 'PRIVATE_EVALUATOR_MARKER',
                           'state_digest', 'dependencies', 'context_json', str(self.root)):
                self.assertNotIn(hidden, json.dumps(report))
        self.assertEqual(len(self.transport.inputs), 1)
        self.assertEqual(before, self.store.path(self.key).read_bytes())

    def test_unknown_usage_and_in_doubt_attempt_keep_reservation_without_retry(self):
        body = self.proposal()
        self.http('/api/ai/proposal', body)
        with sqlite3.connect(self.root / 'technical/attempts.sqlite') as db:
            db.execute("UPDATE attempts SET usage=NULL,status='processing',finished=0,result=NULL,"
                       "transport_state='unknown',reported_identity=NULL")
        code, report = self.usage()
        self.assertEqual(code, 200)
        self.assertEqual(report['summary']['reserved_units'], 10)
        self.assertEqual(report['summary']['active_transport_slots'], 1)
        self.assertEqual(report['summary']['unfinished_or_in_doubt'], 1)
        attempt = report['attempts'][0]
        self.assertEqual(attempt['usage_status'], 'unknown')
        self.assertEqual(attempt['billing_status'], 'unknown')
        self.assertTrue(all(value is None for value in attempt['reported_tokens'].values()))
        self.assertTrue(all(value is None for value in attempt['reported_identity'].values()))
        self.assertEqual(attempt['transport_state'], 'unknown')
        self.assertEqual(len(self.transport.inputs), 1)

    def test_failed_and_cancelled_attempts_keep_full_reservations_after_restart(self):
        self.transport.error = 'provider_denied'
        body = self.proposal()
        self.http('/api/ai/proposal', body)
        self.transport.error = None
        cancelled = self.proposal()
        self.http('/api/ai/proposal', cancelled)
        self.http('/api/ai/cancel', {key: cancelled[key] for key in ('id', 'actor', 'request_id')})
        self.stop()
        self.start()
        report = self.usage()[1]
        self.assertEqual(report['summary']['reserved_units'], 20)
        self.assertEqual(report['summary']['remaining_units'], 80)
        self.assertEqual({row['code'] for row in report['attempts']}, {'provider_denied', 'cancelled'})
        self.assertEqual(len(self.transport.inputs), 2)

    def test_limits_bound_rows_but_totals_cover_the_whole_ledger_and_extra_fields_are_omitted(self):
        for _ in range(2):
            self.http('/api/ai/proposal', self.proposal())
        with sqlite3.connect(self.root / 'technical/attempts.sqlite') as db:
            db.execute('UPDATE attempts SET reported_identity=?', (json.dumps({
                'developer': 'Synthetic', 'api_key': 'SECRET', 'context': 'PRIVATE'}),))
        report = self.usage('&limit=1')[1]
        self.assertEqual(len(report['attempts']), 1)
        self.assertTrue(report['has_more'])
        self.assertEqual(report['summary']['attempts_total'], 2)
        self.assertEqual(report['summary']['reserved_units'], 20)
        self.assertNotIn('SECRET', json.dumps(report))
        self.assertNotIn('PRIVATE', json.dumps(report))
        for invalid in ('0', '51', 'abc'):
            self.assertEqual(self.usage('&limit=' + invalid)[0], 400)

    def test_unconfigured_host_reads_no_ledger_and_enables_no_dispatch(self):
        self.stop()
        original = self.config
        self.config = None
        self.start()
        code, report = self.usage()
        self.assertEqual((code, report['status']), (200, 'unconfigured'))
        self.assertIsNone(report['summary'])
        self.assertEqual(report['attempts'], [])
        self.assertEqual(self.transport.inputs, [])
        self.config = original

    def test_reviewed_charges_match_engine_admission_after_restart_without_mutation(self):
        from inference_accounting import FinalCharge, budget_status, reconcile
        from solo_provider import AttemptLedger
        ledger = AttemptLedger(self.root / 'technical/attempts.sqlite', budget_units=100, max_inflight=2)
        original_save = self.store.path(self.key).read_bytes()
        for index, charge in enumerate((3, 140)):
            body = self.proposal()
            self.assertEqual(self.http('/api/ai/proposal', body)[0], 200)
            reconcile(ledger, FinalCharge(body['request_id'], 'review-' + str(index), charge,
                self.route.price_revision, 'PRIVATE_BILLING_EVIDENCE', 'a' * 64,
                'PRIVATE_OPERATOR_AUTHORITY', final=True), authorize=lambda value: True)
            self.stop()
            self.start()
            expected = budget_status(ledger, authorize=lambda: True)
            with ledger.connection() as db:
                before = tuple(db.iterdump())
            report = self.usage()[1]
            self.assertEqual(report['summary']['remaining_units'], expected['available_units'])
            self.assertEqual(report['summary']['held_units'], expected['held_units'])
            self.assertEqual(report['summary']['known_charged_units'], expected['known_charged_units'])
            self.assertEqual(report['summary']['overrun_units'], expected['overrun_units'])
            self.assertTrue(all(row['billing_status'] == 'operator_reconciled' for row in report['attempts']))
            self.assertNotIn('PRIVATE_BILLING_EVIDENCE', json.dumps(report))
            self.assertNotIn('PRIVATE_OPERATOR_AUTHORITY', json.dumps(report))
            with ledger.connection() as db:
                self.assertEqual(tuple(db.iterdump()), before)
            self.assertEqual(self.store.path(self.key).read_bytes(), original_save)
            self.assertEqual(len(self.transport.inputs), index + 1)

    def test_ledger_read_failure_is_retryable_without_exposing_private_error_text(self):
        with patch('ai_usage.usage_snapshot', side_effect=sqlite3.OperationalError('PRIVATE_STORAGE_FAILURE')):
            code, result = self.usage()
        self.assertEqual(code, 503)
        self.assertNotIn('PRIVATE_STORAGE_FAILURE', json.dumps(result))
        self.assertEqual(self.usage()[0], 200)
        self.assertEqual(self.transport.inputs, [])
