"""Reviewed shared Engine intentions with durable, actor-scoped recovery."""
import copy
import json
import re

from assistance import sync_parent
from core_world import CoreWorld
from gameplay_views import controlled_actor, pending_declaration, safe_result
from irgs_reference import digest
from process_bridge import ProcessService
from runtime_contracts import AcceptedIntent
import shared_runtime as engine


class IntentService(ProcessService):
    def __init__(self, store):
        super().__init__(store)
        self.path = store.folder / '.host' / 'intents.sqlite'

    def binding(self, data, fields):
        if not isinstance(data, dict) or set(data) != fields:
            raise ValueError('Submit only the selected response fields')
        if not isinstance(data.get('actor'), str) or not data['actor']:
            raise PermissionError('Explicitly select a player character')
        key = data.get('request_id')
        if not isinstance(key, str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,128}', key):
            raise ValueError('A stable response request identity is required')
        record = self.store.read(data['id'])
        return record, controlled_actor(record['state'], data['actor']), key

    def view(self, record, actor):
        empty = {'schema_version': engine.SCHEMA_VERSION, 'capabilities': [], 'view_token': None}
        if not actor: return empty
        try:
            caps = engine.capabilities(CoreWorld(state=record['state']), actor)
        except engine.SharedActionUnavailable:
            return empty
        return {'schema_version': engine.SCHEMA_VERSION, 'capabilities': [item.public() for item in caps],
                'view_token': self.token(record)}

    def saved(self, record, actor, key):
        row = record.get('gameplay_requests', {}).get(key)
        if row is None: return None
        if row.get('campaign_id') != record['id'] or row.get('actor') != actor or row.get('intent_api') is not True:
            raise PermissionError('This request identity is not an own reviewed intent')
        sync_parent(self.store.path(record['id']))
        return safe_result(row['result'])

    def public_request(self, row):
        request = AcceptedIntent.from_json(row['request'])
        return {'request_id': row['id'], 'campaign_id': row['branch'], 'actor': request.actor_id,
            'revision': row['revision'], 'view_token': row['token'], 'status': row['status'],
            'intention': request.intention, 'capability': json.loads(row['capability'])}

    def prepare(self, data):
        record, actor, key = self.binding(data, {'id', 'actor', 'revision', 'view_token',
                                                  'request_id', 'intention', 'capability_id'})
        signature = digest(data)
        accepted = self.saved(record, actor, key)
        if accepted:
            if record['gameplay_requests'][key]['payload_digest'] != signature:
                raise ValueError('Request identity was reused with different choices')
            return accepted
        prior = self.row(record['id'], key)
        if prior:
            if prior['actor'] != actor or prior['signature'] != signature:
                raise ValueError('Request identity was reused with different choices')
            return self.public_request(prior)
        controlled_actor(record['state'], actor, required=True)
        if (type(data['revision']) is not int or data['revision'] != record['revision'] or
                not isinstance(data['view_token'], str) or data['view_token'] != self.token(record)):
            raise ValueError('This action view changed. Reload and review a fresh request.')
        if pending_declaration(record, actor):
            raise ValueError('Withdraw the unresolved declaration before reviewing another response')
        world = CoreWorld(state=record['state']); scope = self.scope(record)
        try:
            request = engine.prepare_intent(world, request_id=key, actor_id=actor,
                intention=data['intention'], capability_id=data['capability_id'],
                branch_id=scope.branch_id, restore_id=scope.restore_id,
                source_ref='explicit-reviewed-intent:' + record['id'] + ':' + key)
            capability = next(item.public() for item in engine.capabilities(world, actor)
                              if item.capability_id == request.capability_id)
        except (engine.SharedActionUnavailable, StopIteration):
            raise ValueError('This action is not available to the selected character') from None
        with self.database() as db:
            db.execute('INSERT INTO requests (branch,id,actor,signature,request,revision,token,status,capability) '
                'VALUES (?,?,?,?,?,?,?,?,?)', (record['id'],key,actor,signature,request.to_json(),
                    record['revision'],data['view_token'],'prepared',json.dumps(capability)))
        return self.public_request(self.row(record['id'], key))

    def status(self, data):
        record, actor, key = self.binding(data, {'id','actor','request_id'})
        accepted = self.saved(record, actor, key)
        if accepted: return accepted
        controlled_actor(record['state'], actor, required=True)
        row = self.row(record['id'], key)
        if not row: raise FileNotFoundError('No prepared response is available')
        if row['actor'] != actor: raise PermissionError('This response belongs to another character')
        result = self.public_request(row)
        if row['revision'] != record['revision'] or row['token'] != self.token(record): result['status'] = 'stale'
        return result

    def execute(self, data):
        record, actor, key = self.binding(data, {'id','actor','request_id','explicitly_accepted'})
        if data['explicitly_accepted'] is not True: raise ValueError('Explicit acceptance is required')
        accepted = self.saved(record, actor, key)
        if accepted: return accepted
        controlled_actor(record['state'], actor, required=True)
        row = self.row(record['id'], key)
        if not row or row['actor'] != actor: raise PermissionError('No own prepared response is available')
        if row['status'] == 'rejected': raise ValueError('This response was rejected. Review a fresh request.')
        if row['revision'] != record['revision'] or row['token'] != self.token(record) or pending_declaration(record, actor):
            raise ValueError('This reviewed response is stale. Reload and review again.')
        request = AcceptedIntent.from_json(row['request']); committed = None

        def persist(expected, candidate, public):
            nonlocal committed
            current = self.store.read(record['id'])
            if current['revision'] != row['revision'] or self.scope(current) != expected:
                raise ValueError('The campaign changed before this response could be saved')
            world = CoreWorld.load(candidate); receipt = public['receipt']; status = public['status']
            declaration = request.operation_id == engine.DECLARE
            result = {'request_id': key, 'campaign_id': record['id'], 'actor': actor,
                'kind': 'shared_intent', 'declaration': request.intention, 'status': status,
                'revision': current['revision'] + 1, 'recorded_sequence': receipt['committed_at'],
                'elapsed_time': None, 'narrative': None}
            if not declaration:
                result.update(outcome={'summary': receipt['exact_text']}, receipt={'event_id': receipt['event_id']})
                from local_presentation import receipt_presentation
                result['presentation'] = receipt_presentation(world, result,
                    engine_presentation={**public['presentation'], 'actor_id': actor})
                elapsed = receipt.get('elapsed_seconds')
                if elapsed is not None:
                    result['elapsed_time'] = {'axis': world.s['elapsed_time']['axis'], 'seconds': elapsed,
                        'before_seconds': record['state']['elapsed_time']['seconds'],
                        'after_seconds': world.s['elapsed_time']['seconds']}
            current.setdefault('gameplay_requests', {})[key] = {'campaign_id': record['id'],
                'actor': actor, 'kind': 'declaration' if declaration else 'shared_intent',
                'intent_api': True, 'payload_digest': row['signature'], 'result': copy.deepcopy(result),
                'status': 'pending' if declaration else status}
            self.store.commit(current, world, result); committed = result
        try:
            engine.execute_intent(CoreWorld(state=record['state']), request, current_scope=self.scope(record),
                                  persist=persist, explicitly_accepted=True)
        except engine.SharedActionUnavailable:
            with self.database() as db:
                db.execute('UPDATE requests SET status=? WHERE branch=? AND id=?', ('rejected',record['id'],key))
            raise ValueError('This action was not accepted. No response was committed.') from None
        except OSError:
            with self.database() as db:
                db.execute('UPDATE requests SET status=? WHERE branch=? AND id=?', ('save_failed',record['id'],key))
            raise
        if committed is None: raise ValueError('Reload the durable response result before retrying')
        return committed
