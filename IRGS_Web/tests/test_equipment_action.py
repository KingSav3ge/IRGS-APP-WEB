"""A consequential Solo action over the real loopback host and a synthetic world."""
import copy
import json
import sys
import tempfile
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from server import Store, make_server
from campaign_library import initial_campaign
from core_world import CoreWorld
from player_actions import equipment_options
from r9_runtime import grant


class EquipmentActionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1])
        self.addCleanup(self.tmp.cleanup)
        self.store = Store(self.tmp.name)
        self.key = 'a' * 32
        world = initial_campaign('military', campaign_id='synthetic-equipment-campaign')
        for sequence, (actor, controlled) in enumerate((('commander', True), ('other-player', True),
                                                       ('recipient-one', False), ('recipient-two', False)), 1):
            world.apply('fixture:actor:' + actor, sequence, 'register_actor',
                        campaign_id=world.s['campaign_id'], actor_id=actor, name=actor,
                        species='human', player_controlled=controlled,
                        instruction_ref='explicit-synthetic-player-selection', source_ref='synthetic-fixture')
        world.apply('fixture:stock', 5, 'establish_stock', campaign_id=world.s['campaign_id'],
                    location='depot', material='spear', quantity=4,
                    inventory_evidence_ref='synthetic-count', source_ref='synthetic-fixture')
        for sequence, order_id in enumerate(('issue-one', 'issue-two'), 6):
            world.apply('fixture:order:' + order_id, sequence, 'receive_order',
                        campaign_id=world.s['campaign_id'], order_id=order_id,
                        recipient='commander', content='Issue one spear to recipient-one.',
                        authority_ref='issue-authority', source_ref='synthetic-received-order',
                        directives={'operation': 'issue_equipment', 'persons': ['recipient-one'],
                                    'material': 'spear', 'from': 'depot', 'quantity_each': 1, 'deadline': 100})
        grant(world, 'issue-authority', 'commander', ['military_issue_equipment'],
              at=8, source_ref='PRIVATE_AUTHORITY_SOURCE')
        world.s['actors']['private'] = {'id': 'private', 'name': 'PRIVATE_NPC', 'species': 'human',
                                       'current': {'plans': 'PRIVATE_PLANS'}}
        world.s['orders']['private-order'] = {'recipient': 'private', 'content': 'PRIVATE_ORDER',
            'received_at': 0, 'executed': False, 'source_ref': 'PRIVATE_SOURCE', 'authority_ref': 'private-authority'}
        world.s['stocks']['PRIVATE_DEPOT'] = {'PRIVATE_MATERIAL': 41}
        world.s['opening_stock']['PRIVATE_MATERIAL'] = 41
        world._validate(world.s)
        self.record = {'id': self.key, 'name': 'Synthetic equipment action', 'revision': 0, 'state': world.s}
        self.store.write(self.record)
        self.server = make_server(0, self.tmp.name)
        self.addCleanup(self.server.server_close)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.thread.join)
        self.addCleanup(self.server.shutdown)
        self.url = 'http://127.0.0.1:' + str(self.server.server_port)
        self.token = self.call('/api/campaigns')['token']

    def call(self, path, data=None, *, token=True, headers=None):
        request_headers = {'Content-Type': 'application/json'}
        if token and hasattr(self, 'token'):
            request_headers['X-IRGS-Token'] = self.token
        request_headers.update(headers or {})
        request = Request(self.url + path, data=None if data is None else json.dumps(data).encode(),
                          headers=request_headers)
        with urlopen(request, timeout=15) as response:
            return json.load(response)

    def action(self, request_id='equipment-1', **changes):
        order_id = changes.get('order_id', 'issue-one')
        current = self.store.read(self.key)['state']
        options = equipment_options(current, 'commander') + equipment_options(self.record['state'], 'commander')
        option = next((item for item in options if item['order_id'] == order_id), None)
        text = option['text'] if option else 'I attempt to carry out a selected received order.'
        return {**{'id': self.key, 'revision': 0, 'request_id': request_id, 'actor': 'commander',
                   'kind': 'issue_equipment', 'order_id': order_id, 'text': text}, **changes}

    def receive_prompt(self, prompt_id='encounter-one', recipient='commander', **changes):
        params = {**{'prompt_id': prompt_id, 'recipient': recipient, 'title': 'A received encounter',
                     'description': 'A messenger asks how you intend to respond.', 'context_kind': 'dialogue',
                     'choices': [{'id': 'ask', 'label': 'Ask for clarification',
                                  'text': 'I ask for clarification before deciding.'}],
                     'source_ref': 'PRIVATE_PROMPT_PROVENANCE'}, **changes}
        record = self.store.read(self.key)
        return self.call('/api/event', {'id': self.key, 'revision': record['revision'], 'mode': 'creator',
                                       'op': 'receive_response_prompt', 'params': params})

    def raw(self):
        return self.store.path(self.key).read_bytes()

    def projection(self, actor='commander'):
        return self.call('/api/playthrough/' + self.key + '?actor_id=' + actor)

    def mutate(self, change):
        record = self.store.read(self.key)
        change(record['state'])
        CoreWorld(state=record['state'])
        self.store.write(record)

    def rejected(self, request, *, status=None):
        before = self.raw()
        with self.assertRaises(HTTPError) as rejected:
            self.call('/api/action', request)
        if status is not None:
            self.assertEqual(rejected.exception.code, status)
        error = json.loads(rejected.exception.read())
        self.assertNotIn('PRIVATE_', json.dumps(error))
        self.assertEqual(self.raw(), before)
        return error

    def test_received_options_do_not_disclose_current_stock_or_private_authority(self):
        before = self.raw()
        view = self.projection()
        self.assertEqual({option['order_id'] for option in view['supported_actions']}, {'issue-one', 'issue-two'})
        self.assertTrue(view['capabilities']['supported_action_resolution'])
        self.assertFalse(view['capabilities']['action_resolution'])
        self.assertFalse(view['capabilities']['time_advance'])
        self.assertEqual(view['inventory'], [])
        self.assertNotIn('PRIVATE_', json.dumps(view))
        self.assertEqual(self.projection('other-player')['supported_actions'], [])
        self.assertEqual(self.raw(), before)
        # Received choices must not become an oracle for unobserved stock or authority changes.
        self.mutate(lambda state: state['r9']['mandates']['issue-authority'].update(active=False))
        self.assertEqual(self.projection()['supported_actions'], view['supported_actions'])
        self.mutate(lambda state: (state['stocks']['depot'].update(spear=0),
                                   state['opening_stock'].update(spear=0)))
        self.assertEqual(self.projection()['supported_actions'], view['supported_actions'])

    def test_outcome_commits_conserved_stock_and_own_safe_chronicle(self):
        time_before = copy.deepcopy(self.record['state']['campaign_time'])
        request = self.action()
        result = self.call('/api/action', request)
        self.assertEqual(result['status'], 'completed_successfully')
        self.assertEqual(result['declaration'], request['text'])
        self.assertEqual(result['kind'], 'issue_equipment')
        self.assertIsNone(result['elapsed_time'])
        self.assertIsNone(result['narrative'])
        self.assertTrue(result['outcome']['summary'])
        self.assertTrue(result['receipt']['event_id'])
        self.assertNotIn('PRIVATE_', json.dumps(result))
        self.assertNotIn('dependencies', result)
        saved = self.store.read(self.key)
        state = saved['state']
        self.assertEqual(state['stocks']['depot']['spear'], 3)
        self.assertEqual(state['stocks']['recipient-one']['spear'], 1)
        self.assertEqual(state['opening_stock']['spear'], 4)
        self.assertTrue(state['orders']['issue-one']['executed'])
        self.assertEqual(state['campaign_time'], time_before)
        CoreWorld(state=state)
        view = self.projection()
        self.assertIsNone(view['pending_declaration'])
        self.assertTrue(view['capabilities']['can_declare'])
        self.assertEqual(view['completed_actions'], [result])
        self.assertEqual([option['order_id'] for option in view['supported_actions']], ['issue-two'])
        self.assertIn('completed_successfully', {entry['status'] for entry in view['chronicle']})
        self.assertNotIn('PRIVATE_', json.dumps(view))
        self.assertEqual(self.projection('other-player')['completed_actions'], [])

    def test_retry_and_new_store_reload_recover_identical_outcome_without_effects(self):
        request = self.action()
        result = self.call('/api/action', request)
        before = self.raw()
        self.assertEqual(self.call('/api/action', request), result)
        self.assertEqual(self.call('/api/action-result/' + self.key + '/equipment-1?actor_id=commander'), result)
        reloaded = Store(self.tmp.name)
        self.assertEqual(reloaded.supported_action(request), result)
        self.assertEqual(reloaded.action_result(self.key, 'equipment-1', 'commander'), result)
        self.assertEqual(self.raw(), before)

    def test_concurrent_retries_commit_one_effect_and_one_receipt(self):
        request = self.action('concurrent')
        with ThreadPoolExecutor(max_workers=4) as pool:
            outcomes = list(pool.map(lambda _: self.call('/api/action', request), range(4)))
        self.assertTrue(all(outcome == outcomes[0] for outcome in outcomes))
        saved = self.store.read(self.key)
        self.assertEqual(saved['revision'], 1)
        self.assertEqual(saved['state']['stocks']['depot']['spear'], 3)
        self.assertEqual(len(saved['gameplay_requests']), 1)
        self.assertEqual(sum(event['id'] == outcomes[0]['receipt']['event_id']
                             for event in saved['state']['journal']), 1)

    def test_accepted_retry_retrieves_history_after_authority_and_stock_change(self):
        request = self.action()
        original = self.call('/api/action', request)
        def change_world(state):
            state['r9']['mandates']['issue-authority']['active'] = False
            state['stocks']['depot']['spear'] = 0
            state['stocks']['recipient-one']['spear'] = 4
        self.mutate(change_world)
        before = self.raw()
        self.assertEqual(self.call('/api/action', request), original)
        self.assertEqual(self.call('/api/action-result/' + self.key + '/equipment-1?actor_id=commander'), original)
        self.assertEqual(self.raw(), before)
        self.rejected(self.action('new-action', revision=original['revision'], order_id='issue-two'))

    def test_next_action_works_after_a_completed_outcome_and_reload(self):
        first = self.call('/api/action', self.action())
        view = self.projection()
        second = self.call('/api/action', self.action('equipment-2', revision=view['revision'], order_id='issue-two'))
        self.assertEqual(second['status'], 'completed_successfully')
        self.assertNotEqual(first['receipt']['event_id'], second['receipt']['event_id'])
        state = self.store.read(self.key)['state']
        self.assertEqual(state['stocks']['depot']['spear'], 2)
        self.assertEqual(state['stocks']['recipient-one']['spear'], 2)
        view = self.projection()
        self.assertEqual(len(view['completed_actions']), 2)
        self.assertEqual(view['supported_actions'], [])
        self.assertTrue(view['capabilities']['can_declare'])
        self.assertIsNone(view['pending_declaration'])

    def test_changed_payload_and_stale_new_request_cannot_reuse_accepted_identity(self):
        result = self.call('/api/action', self.action())
        for change in ({'text': 'Different words'}, {'order_id': 'issue-two'},
                       {'kind': 'declaration'}, {'actor': 'other-player'}):
            with self.subTest(change=change):
                self.rejected(self.action(**change))
        self.rejected(self.action('stale-new', order_id='issue-two'))
        self.assertEqual(self.call('/api/action', self.action(revision=result['revision'])), result)
        self.rejected(self.action('new-again', revision=result['revision']))

    def test_different_words_cannot_silently_execute_a_listed_equipment_action(self):
        for text in ('Do not issue the equipment.', 'I ask whether the order can be changed.'):
            with self.subTest(text=text):
                result = self.rejected(self.action(text=text))
                self.assertIn('own response', result['error'])
        self.assertFalse(self.store.read(self.key)['state']['orders']['issue-one']['executed'])

    def test_selected_actor_and_local_session_boundaries_prevent_impersonation(self):
        for actor in ('private', 'missing', '', None, 'other-player'):
            with self.subTest(actor=actor):
                self.rejected(self.action(actor=actor))
        for arguments in ({'token': False}, {'headers': {'Origin': 'https://attacker.invalid'}},
                          {'headers': {'Host': 'attacker.invalid'}}):
            before = self.raw()
            with self.assertRaises(HTTPError) as rejected:
                self.call('/api/action', self.action(), **arguments)
            self.assertEqual(rejected.exception.code, 403)
            self.assertEqual(self.raw(), before)

    def test_revoked_future_or_wrong_scope_authority_fails_without_private_details(self):
        original = copy.deepcopy(self.record)
        for changes in ({'active': False}, {'effective_at': 999}, {'actor': 'other-player'},
                        {'operations': ['record_design']}):
            with self.subTest(changes=changes):
                self.store.write(copy.deepcopy(original))
                self.mutate(lambda state: state['r9']['mandates']['issue-authority'].update(changes))
                self.rejected(self.action())

    def test_depletion_during_multi_recipient_issue_has_no_partial_effects(self):
        def deplete(state):
            state['stocks']['depot']['spear'] = 1
            state['opening_stock']['spear'] = 1
            state['orders']['issue-one']['directives']['persons'] = ['recipient-one', 'recipient-two']
        self.mutate(deplete)
        self.rejected(self.action())
        state = self.store.read(self.key)['state']
        self.assertNotIn('recipient-one', state['stocks'])
        self.assertNotIn('recipient-two', state['stocks'])
        self.assertFalse(state['orders']['issue-one']['executed'])

    def test_expired_unreceived_or_other_orders_are_rejected_atomically(self):
        original = copy.deepcopy(self.record)
        for mutate in (lambda state: state['orders']['issue-one']['directives'].update(deadline=1),
                       lambda state: state['orders']['issue-one'].update(received_at=999),
                       lambda state: state['orders']['issue-one'].update(recipient='private'),
                       lambda state: state['orders']['issue-one'].update(revoked=True)):
            self.store.write(copy.deepcopy(original))
            self.mutate(mutate)
            self.rejected(self.action())
        self.store.write(copy.deepcopy(original))
        self.rejected(self.action(order_id='missing-order'))

    def test_pending_declaration_requires_withdrawal_before_a_different_action(self):
        pending = self.call('/api/declaration', {'id': self.key, 'revision': 0, 'request_id': 'pending-intent',
                            'actor': 'commander', 'declaration': 'I consider another action.'})
        view = self.projection()
        self.assertIsNotNone(view['pending_declaration'])
        self.assertEqual(view['supported_actions'], [])
        self.rejected(self.action(revision=pending['revision']))
        withdrawal = self.call('/api/withdraw-declaration', {'id': self.key, 'revision': pending['revision'],
                               'request_id': 'withdraw-pending', 'actor': 'commander',
                               'action_request_id': 'pending-intent'})
        result = self.call('/api/action', self.action(revision=withdrawal['revision']))
        self.assertEqual(result['status'], 'completed_successfully')

    def test_failed_persistence_leaves_the_campaign_and_retry_safe(self):
        before = self.raw()
        with patch.object(Store, 'write', side_effect=OSError('synthetic save unavailable')):
            with self.assertRaises(HTTPError) as rejected:
                self.call('/api/action', self.action())
            self.assertEqual(rejected.exception.code, 503)
        self.assertEqual(self.raw(), before)
        self.assertEqual(self.call('/api/action', self.action())['status'], 'completed_successfully')
        self.assertEqual(self.store.read(self.key)['state']['stocks']['depot']['spear'], 3)

    def test_rejected_action_has_no_receipt_or_pending_state_and_later_play_continues(self):
        self.mutate(lambda state: state['r9']['mandates']['issue-authority'].update(active=False))
        self.rejected(self.action('rejected-action'))
        before = self.raw()
        with self.assertRaises(HTTPError) as missing:
            self.call('/api/action-result/' + self.key + '/rejected-action?actor_id=commander')
        self.assertEqual(missing.exception.code, 404)
        self.assertEqual(self.raw(), before)
        view = self.projection()
        self.assertIsNone(view['pending_declaration'])
        self.assertEqual(view['completed_actions'], [])
        self.assertTrue(view['capabilities']['can_declare'])
        self.mutate(lambda state: state['r9']['mandates']['issue-authority'].update(active=True))
        self.assertEqual(self.call('/api/action', self.action('later-action'))['status'], 'completed_successfully')

    def test_missing_receipt_still_requires_controlled_actor_before_absence_disclosure(self):
        before = self.raw()
        with self.assertRaises(HTTPError) as denied:
            self.call('/api/action-result/' + self.key + '/not-accepted?actor_id=private')
        self.assertEqual(denied.exception.code, 403)
        self.assertEqual(self.raw(), before)

    def test_received_prompt_projection_is_private_and_read_only(self):
        self.receive_prompt()
        self.receive_prompt('other-encounter', 'other-player', title='PRIVATE_OTHER_PROMPT',
                            description='PRIVATE_OTHER_DESCRIPTION', choices=[])
        before = self.raw()
        view = self.projection()
        self.assertEqual(view['response_prompt']['prompt_id'], 'encounter-one')
        self.assertEqual(view['response_prompt']['source_status'], 'received_prompt')
        self.assertEqual(view['response_choices'], [{'id': 'ask', 'label': 'Ask for clarification',
            'text': 'I ask for clarification before deciding.', 'kind': 'declaration'}])
        self.assertNotIn('PRIVATE_', json.dumps(view))
        other = self.projection('other-player')
        self.assertEqual(other['response_prompt']['prompt_id'], 'other-encounter')
        self.assertEqual(other['response_choices'], [])
        self.assertEqual(self.raw(), before)

    def test_explicit_combat_prompt_offers_tentative_drafts_without_resolving_combat(self):
        self.assertIsNone(self.projection()['response_prompt'])
        self.assertEqual(self.projection()['response_choices'], [])
        before = copy.deepcopy(self.store.read(self.key)['state'])
        self.receive_prompt(context_kind='combat', choices=[], title='A received combat situation',
                            description='This situation was explicitly supplied to the character.')
        view = self.projection()
        self.assertEqual(view['response_prompt']['context_kind'], 'combat')
        self.assertEqual(len(view['response_choices']), 5)
        self.assertTrue(all(choice['kind'] == 'declaration' for choice in view['response_choices']))
        current = self.store.read(self.key)['state']
        for field in ('stocks', 'opening_stock', 'actors', 'orders', 'campaign_time', 'player_actions'):
            self.assertEqual(current[field], before[field])

    def test_own_response_preserves_exact_words_as_unresolved_intent_without_combat_effects(self):
        self.receive_prompt(context_kind='combat', choices=[])
        before = copy.deepcopy(self.store.read(self.key)['state'])
        text = '  I try to fall back toward the doorway.\nI do not attack.  '
        result = self.call('/api/declaration', {'id': self.key, 'revision': self.store.read(self.key)['revision'],
                           'request_id': 'own-combat-response', 'actor': 'commander', 'declaration': text})
        self.assertEqual(result['declaration'], text)
        self.assertEqual(result['status'], 'declared_not_resolved')
        self.assertIsNone(result['elapsed_time'])
        self.assertIsNone(result['narrative'])
        current = self.store.read(self.key)['state']
        for field in ('stocks', 'opening_stock', 'actors', 'orders', 'campaign_time', 'response_prompts'):
            self.assertEqual(current[field], before[field])
        self.assertEqual(self.projection()['pending_declaration']['declaration'], text)

    def test_receipt_is_actor_scoped_and_a_fork_cannot_replay_the_original_save(self):
        result = self.call('/api/action', self.action())
        original = self.raw()
        with self.assertRaises(HTTPError) as rejected:
            self.call('/api/action-result/' + self.key + '/equipment-1?actor_id=other-player')
        self.assertEqual(rejected.exception.code, 403)
        branch = self.call('/api/fork', {'id': self.key, 'mode': 'creator'})
        with self.assertRaises(HTTPError):
            self.call('/api/action-result/' + branch['id'] + '/equipment-1?actor_id=commander')
        with self.assertRaises(HTTPError):
            self.call('/api/action', self.action(id=branch['id'], revision=branch['revision']))
        self.assertEqual(self.raw(), original)
        self.assertEqual(self.call('/api/action-result/' + self.key + '/equipment-1?actor_id=commander'), result)


if __name__ == '__main__':
    unittest.main()
