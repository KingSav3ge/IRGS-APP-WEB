"""Durable, explicitly reviewed App host for Engine communication capabilities.

Only the existing Engine chooses received participants/terms and commits effects.
The process host's private journal/scope plumbing is reused in a separate file;
neither journal owns game facts. Native requests and scope digests stay private.
"""
import copy
import json
import re
import secrets

import communication_contract as engine
import supported_intent as intents
from communication_runtime import CommunicationRequest
from core_world import CoreWorld
from gameplay_views import controlled_actor, pending_declaration, safe_result
from irgs_reference import digest
from process_bridge import ProcessService
from assistance import sync_parent
from shared_runtime import SharedActionUnavailable


class CommunicationService(ProcessService):
    def __init__(self, store):
        super().__init__(store)
        self.path = store.folder / '.host' / 'communications.sqlite'

    def binding(self, data, fields):
        if not isinstance(data, dict) or set(data) != fields:
            raise ValueError('Submit only the selected communication fields')
        if not isinstance(data.get('actor'), str) or not data['actor']:
            raise PermissionError('Explicitly select a player character')
        key = data.get('request_id')
        if not isinstance(key, str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,128}', key):
            raise ValueError('A stable communication request identity is required')
        record = self.store.read(data['id'])
        actor = controlled_actor(record['state'], data['actor'])
        return record, actor, key

    def view(self, record, actor):
        if not actor:
            return {'schema_version': engine.SCHEMA_VERSION, 'channels': [], 'offers': [],
                    'received_sources': {'records': [], 'total': 0, 'truncated': False}, 'view_token': None}
        scope = self.scope(record)
        try:
            packet = engine.actor_view(CoreWorld(state=record['state']), actor,
                branch_id=scope.branch_id, restore_id=scope.restore_id)
        except engine.CommunicationUnavailable:
            return {'schema_version': engine.SCHEMA_VERSION, 'channels': [], 'offers': [],
                    'received_sources': {'records': [], 'total': 0, 'truncated': False}, 'view_token': None}
        # Pre-contract, unattributed evidence was exposed through its receipt,
        # without the original private provenance or occurrence metadata. Keep
        # that established App boundary. Explicitly attributed native sources
        # retain both Engine references; no evidence or receipt is rewritten.
        for source in packet['received_sources']['records']:
            if not source.get('originator'):
                if source['source_ref'] != source['receipt_source_ref']:
                    source['source_ref'] = None
                source['occurrence_time'] = None
        packet['source_projection'] = 'app-receipt-compatibility-1'
        return {**packet, 'view_token': self.token(record), 'intent_schema_version': intents.SCHEMA_VERSION}

    def received(self, record, actor, request_id):
        actor = controlled_actor(record['state'], actor, required=True)
        scope = self.scope(record)
        try:
            return engine.received_communication(CoreWorld(state=record['state']), actor, request_id,
                branch_id=scope.branch_id, restore_id=scope.restore_id)
        except engine.CommunicationUnavailable:
            raise PermissionError('This communication record is not available to the selected character') from None

    def public_request(self, row):
        request = CommunicationRequest.from_json(row['request'])
        packet = {'request_id': row['id'], 'campaign_id': row['branch'], 'actor': request.actor,
                'revision': row['revision'], 'view_token': row['token'], 'status': row['status'],
                'recipient': request.recipient, 'channel_id': request.channel_id, 'command': request.command,
                'details': json.loads(request.details_json), 'intention': request.intention}
        if row.get('capability') is not None:
            packet['intent_review'] = json.loads(row['capability'])
        return packet

    def saved(self, record, actor, key):
        saved = record.get('gameplay_requests', {}).get(key)
        if saved is None:
            return None
        if saved.get('campaign_id') != record['id'] or saved.get('actor') != actor or saved.get('kind') != 'communication':
            raise PermissionError('This request identity is not an own communication result')
        sync_parent(self.store.path(record['id']))
        return safe_result(saved['result'])

    def prepare(self, data):
        return self._prepare(data, supported=False)

    def prepare_supported(self, data):
        return self._prepare(data, supported=True)

    def _prepare(self, data, *, supported):
        fields = {'id', 'actor', 'revision', 'view_token', 'request_id', 'recipient',
                  'channel_id', 'command', 'details', 'intention'}
        record, actor, key = self.binding(data, fields)
        signature = digest([intents.SCHEMA_VERSION, data]) if supported else digest(data)
        accepted = self.saved(record, actor, key)
        if accepted:
            if record['gameplay_requests'][key]['payload_digest'] != signature:
                raise ValueError('Communication request identity was reused with different choices')
            return accepted
        prior = self.row(record['id'], key)
        if prior:
            if prior['actor'] != actor or prior['signature'] != signature:
                raise ValueError('Communication request identity was reused with different choices')
            return self.public_request(prior)
        controlled_actor(record['state'], actor, required=True)
        if (type(data['revision']) is not int or data['revision'] != record['revision']
                or not isinstance(data['view_token'], str) or data['view_token'] != self.token(record)):
            raise ValueError('This communication view changed. Reload and review a fresh request.')
        if pending_declaration(record, actor):
            raise ValueError('Withdraw the unresolved declaration before reviewing a communication')
        details = copy.deepcopy(data['details'])
        if data['command'] in ('offer', 'counteroffer'):
            expected = {'terms'} if data['command'] == 'offer' else {'terms', 'counter_to'}
            if not isinstance(details, dict) or set(details) != expected:
                raise ValueError('Supply only the explicit proposed terms and received counteroffer reference')
            details['offer_id'] = 'web-offer-' + secrets.token_hex(16)
        scope = self.scope(record)
        review = None
        try:
            world = CoreWorld(state=record['state'])
            arguments = dict(recipient=data['recipient'], channel_id=data['channel_id'], command=data['command'],
                details=details, intention=data['intention'], branch_id=scope.branch_id, restore_id=scope.restore_id)
            source = 'explicit-player-communication:' + record['id'] + ':' + key
            if supported:
                review = intents.review_communication(world, actor_id=actor, **arguments)
                if review['status'] != 'supported':
                    return {'request_id': key, 'campaign_id': record['id'], 'actor': actor,
                        'revision': record['revision'], 'view_token': data['view_token'],
                        'status': review['status'], 'intention': data['intention'], 'intent_review': review}
                request = intents.prepare_communication(world, request_id=key, actor_id=actor,
                    review_id=review['review_id'], source_ref=source, **arguments)
            else:
                request = engine.prepare(world, request_id=key, actor=actor, source_ref=source, **arguments)
        except (engine.CommunicationUnavailable, SharedActionUnavailable):
            raise ValueError('This communication cannot be reviewed under the selected received capabilities') from None
        with self.database() as db:
            db.execute('INSERT INTO requests (branch,id,actor,signature,request,revision,token,status,capability) '
                       'VALUES (?,?,?,?,?,?,?,?,?)',
                (record['id'], key, actor, signature, request.to_json(), record['revision'], data['view_token'],
                 'prepared', json.dumps(review) if review is not None else None))
        return self.public_request(self.row(record['id'], key))

    def status(self, data):
        record, actor, key = self.binding(data, {'id', 'actor', 'request_id'})
        accepted = self.saved(record, actor, key)
        if accepted:
            return accepted
        row = self.row(record['id'], key)
        if not row:
            raise FileNotFoundError('No prepared communication is available')
        if row['actor'] != actor:
            raise PermissionError('This communication belongs to another character')
        result = self.public_request(row)
        if row['revision'] != record['revision'] or row['token'] != self.token(record):
            result['status'] = 'stale'
        return result

    def execute(self, data):
        record, actor, key = self.binding(data, {'id', 'actor', 'request_id', 'explicitly_accepted'})
        if data['explicitly_accepted'] is not True:
            raise ValueError('Explicit acceptance is required')
        accepted = self.saved(record, actor, key)
        if accepted:
            return accepted
        controlled_actor(record['state'], actor, required=True)
        row = self.row(record['id'], key)
        if not row or row['actor'] != actor:
            raise PermissionError('No own prepared communication is available')
        if row['status'] == 'rejected':
            raise ValueError('This communication was rejected. Review a fresh request.')
        if (row['revision'] != record['revision'] or row['token'] != self.token(record)
                or pending_declaration(record, actor)):
            raise ValueError('This prepared communication is stale. Reload and review a fresh request.')
        request = CommunicationRequest.from_json(row['request'])
        committed = None

        def persist(expected, candidate, public):
            nonlocal committed
            supported = row.get('capability') is not None
            if supported:
                if (public.get('schema_version') != intents.SCHEMA_VERSION or public.get('request_id') != key
                        or public.get('actor_id') != actor or public.get('intention') != request.intention
                        or public.get('operation_id') != 'execute_local_communication'
                        or public.get('status') != public.get('communication', {}).get('status')):
                    raise ValueError('The Engine communication result does not match this reviewed request')
                received = public['communication']
            else:
                received = public
            current = self.store.read(record['id'])
            if current['revision'] != row['revision'] or self.scope(current) != expected:
                raise ValueError('The campaign changed before this communication could be saved')
            world = CoreWorld.load(candidate)
            receipt = received['receipt']
            event = 'communication:' + key
            if received['actor'] != actor or receipt['actor_id'] != actor or receipt['event_id'] != event:
                raise ValueError('The Engine communication receipt does not match this actor and request')
            result = {'request_id': key, 'campaign_id': record['id'], 'actor': actor,
                'kind': 'communication', 'status': 'completed_successfully',
                'revision': current['revision'] + 1, 'recorded_sequence': received['at'],
                'declaration': request.intention, 'outcome': {'summary': receipt['exact_text']},
                'receipt': {'event_id': event}, 'communication': copy.deepcopy(received), 'elapsed_time': None}
            if supported:
                result['intent_result'] = copy.deepcopy(public)
            from local_presentation import receipt_presentation
            text = {**received['presentation'], 'actor_id': receipt['actor_id']}
            result['presentation'] = receipt_presentation(world, result, engine_presentation=text)
            current.setdefault('gameplay_requests', {})[key] = {'campaign_id': record['id'], 'actor': actor,
                'kind': 'communication', 'status': result['status'], 'payload_digest': row['signature'], 'result': result}
            self.store.commit(current, world, result)
            committed = result

        try:
            execute = intents.execute_communication if row.get('capability') is not None else engine.execute
            execute(CoreWorld(state=record['state']), request, current_scope=self.scope(record),
                    persist=persist, explicitly_accepted=True)
        except (engine.CommunicationUnavailable, SharedActionUnavailable):
            with self.database() as db:
                db.execute('UPDATE requests SET status=? WHERE branch=? AND id=?', ('rejected', record['id'], key))
            raise ValueError('This communication was not accepted under current Core rules. No communication was committed.') from None
        except OSError:
            with self.database() as db:
                db.execute('UPDATE requests SET status=? WHERE branch=? AND id=?', ('save_failed', record['id'], key))
            raise
        if committed is None:
            raise ValueError('Reload the durable communication result before retrying')
        return committed
