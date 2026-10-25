"""Host authentication/persistence bridge to Engine's optional Solo capability.

Routes, policy, budgets and transport are explicitly supplied by a trusted host.
The default host does not import the optional API or dispatch provider requests.
"""
from dataclasses import asdict, dataclass
import copy
import json
import os
from pathlib import Path
import re
import uuid

from core_world import CoreWorld
from gameplay_views import controlled_actor, pending_declaration, safe_result
from irgs_reference import digest


def sync_parent(path):
    """Persist a replaced directory entry on platforms supporting directory fsync."""
    if os.name != 'nt':
        descriptor = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)


def assistance_status(*, developer=False):
    # Neither an environment key nor a model name establishes a qualified route.
    result = {
        'status': 'unavailable',
        'available': False,
        'message': 'AI assistance is not connected. Listed actions remain available; freeform declarations remain unresolved.',
        'campaign_effects': False,
    }
    if developer:
        result['diagnostics'] = {
            'reason_code': 'explicit_host_configuration_required',
            'dispatch_enabled': False,
            'provider_runtime': 'not_connected',
            'model_evaluations': 'not_run',
        }
    return result


@dataclass(frozen=True)
class SoloConfiguration:
    """Server-only injection. Engine's broker owns eligibility and finite budgets.

    broker_factory(scope_reader) must return the selected Engine's broker, with
    its durable ledger and explicitly approved routes. No implicit live adapter.
    Keep private_dir and the ledger outside save/source/distribution directories.
    """
    broker_factory: object
    transport: object
    route_id: str
    classification: str
    policy_ref: str
    config_version: str
    private_dir: object
    deadline_seconds: float
    max_output_tokens: int


class SoloService:
    def __init__(self, store, configuration=None):
        self.store, self.config, self.closed = store, configuration, False
        if configuration is None:
            return
        # Lazy imports keep the reviewed older Core usable while candidates are
        # explicitly selected for qualification. No alternate executor exists.
        import solo_actions
        import solo_provider
        self.actions, self.api = solo_actions, solo_provider
        self.private = Path(configuration.private_dir).resolve()
        saves = store.folder.resolve()
        source = Path(__file__).resolve().parent.parent
        if (self.private == saves or saves in self.private.parents or
                self.private == source or source in self.private.parents):
            raise ValueError('Solo technical storage must be outside saves and product source')
        self.private.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.metadata_path = self.private / 'host-scope.json'
        self.metadata = (json.loads(self.metadata_path.read_text(encoding='utf-8'))
                         if self.metadata_path.exists() else {'restores': {}, 'cancelled': {}})
        self.broker = configuration.broker_factory(self.scope)
        self.ledger = self.broker.ledger
        store.before_restore = self.rotate_restore

    def status(self, *, developer=False, record=None, actor=None):
        if self.config is None or self.closed:
            return assistance_status(developer=developer)
        available = self.broker.enabled is True
        if record is not None:
            if record['state'].get('binding', {}).get('campaign_profile') == 'rise':
                from settlement_runtime import ACTIONS
                supported = actor == 'founder' and bool(ACTIONS)
            else:
                from scene_actions import scene_options
                supported = bool(actor) and bool(scene_options(record['state'], actor))
            available = available and supported
        result = {'status': 'configured' if available else 'unavailable', 'available': available,
                  'campaign_effects': False, 'message': (
                      'Review an assisted proposal for a listed action. Only your explicit acceptance submits it.'
                      if available else 'Assistance is unavailable for this situation. Listed actions remain available; freeform declarations remain unresolved.')}
        if developer:
            result['diagnostics'] = {'reason_code': 'explicit_host_configuration',
                'dispatch_enabled': self.broker.enabled is True,
                'provider_runtime': 'engine_capability_broker',
                'model_evaluations': 'host_selected_route_requires_engine_eligibility'}
        return result

    def save_metadata(self):
        tmp = self.metadata_path.with_suffix('.tmp')
        with tmp.open('w', encoding='utf-8') as stream:
            json.dump(self.metadata, stream)
            stream.flush()
            os.fsync(stream.fileno())
        tmp.replace(self.metadata_path)
        sync_parent(self.metadata_path)

    def restore_id(self, key):
        if key not in self.metadata['restores']:
            self.metadata['restores'][key] = uuid.uuid4().hex
            self.save_metadata()
        return self.metadata['restores'][key]

    def rotate_restore(self, key):
        # Called under the same Store lock, BEFORE restoring even identical bytes.
        self.metadata['restores'][key] = uuid.uuid4().hex
        self.save_metadata()

    def scope(self, request):
        with self.store.lock:
            if self.closed:
                return None
            try:
                record = self.store.read(request.scope.branch_id)
                controlled_actor(record['state'], request.actor_id, required=True)
                return self.api.WorldScope(record['state']['campaign_id'], record['id'],
                    self.restore_id(record['id']), CoreWorld(state=record['state']).checksum())
            except (FileNotFoundError, PermissionError):
                return None

    def binding(self, data, *, fields):
        if not isinstance(data, dict) or set(data) - fields - {'mode'}:
            raise ValueError('Submit only the selected proposal request fields')
        request_id = data.get('request_id')
        if not isinstance(request_id, str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,128}', request_id):
            raise ValueError('A stable proposal request identity is required')
        record = self.store.read(data['id'])
        if not isinstance(data.get('actor'), str) or not data['actor']:
            raise PermissionError('Explicitly select a player character')
        actor = controlled_actor(record['state'], data['actor'])
        return record, actor, request_id

    def unavailable(self, request_id, code):
        return {'request_id': request_id, 'status': 'unavailable', 'code': code,
                'message': 'No new action was committed. Keep your draft or use a listed action.'}

    def owned_request(self, record, actor, request_id):
        row = self.ledger.lookup(request_id)
        if row is None:
            return None
        request = self.api.ActorRequest.from_json(row['request'])
        if request.scope.branch_id != record['id'] or request.actor_id != actor:
            raise PermissionError('This proposal is not available to the selected character')
        return request

    def public_result(self, result, request, revision):
        public = asdict(result)
        public.update(campaign_id=request.scope.branch_id, actor=request.actor_id, revision=revision)
        if result.proposal is not None and result.status == 'proposal_ready':
            context = json.loads(request.context_json)
            choice = next(item for item in context['options'] if item['action_id'] == result.proposal.action_id)
            public['action'] = {key: copy.deepcopy(choice[key]) for key in
                                ('kind', 'action_id', 'title', 'text', 'description') if key in choice}
        return public

    def propose(self, data, *, lookup=False):
        with self.store.lock:
            record, actor, key = self.binding(data, fields={'id', 'actor', 'request_id', 'revision', 'intention'})
            if self.config is None or self.closed:
                return self.unavailable(key, 'unconfigured')
            request = self.owned_request(record, actor, key)
            if request is not None and not lookup and data.get('intention') != request.intention:
                raise ValueError('Request identity was reused with a different intention')
            if key in record.get('gameplay_requests', {}):
                if request is None:
                    raise ValueError('Request identity is already used by another action')
                return self.store.action_result(record['id'], key, actor)
            if key in self.metadata['cancelled']:
                return self.unavailable(key, 'cancelled')
            if request is None and lookup:
                return self.unavailable(key, 'unknown_request')
            if request is None:
                controlled_actor(record['state'], actor, required=True)
                if type(data.get('revision')) is not int or record['revision'] != data['revision']:
                    return self.unavailable(key, 'stale_state')
                if pending_declaration(record, actor) is not None:
                    return self.unavailable(key, 'pending_declaration')
                try:
                    request = self.actions.prepare_request(CoreWorld(state=record['state']),
                        request_id=key, actor_id=actor, intention=data.get('intention'),
                        branch_id=record['id'], restore_id=self.restore_id(record['id']),
                        allowed_routes=(self.config.route_id,), classification=self.config.classification,
                        policy_ref=self.config.policy_ref, config_version=self.config.config_version,
                        deadline=self.broker.clock() + self.config.deadline_seconds,
                        max_output_tokens=self.config.max_output_tokens)
                except self.api.CapabilityUnavailable as error:
                    return self.unavailable(key, error.code)
            revision = record['revision']
        # Never hold the save-writer lock over provider I/O. Engine checks current
        # scope before dispatch, after output, and before returning cached output.
        result = self.broker.dispatch(request, self.config.route_id, self.config.transport,
            cancelled=lambda: self.closed or key in self.metadata['cancelled'])
        return self.public_result(result, request, revision)

    def cancel(self, data):
        with self.store.lock:
            record, actor, key = self.binding(data, fields={'id', 'actor', 'request_id'})
            if self.config is None:
                return self.unavailable(key, 'unconfigured')
            self.owned_request(record, actor, key)
            # Durable tombstone also fences a cancel arriving just before claim.
            self.metadata['cancelled'][key] = [record['id'], actor]
            self.save_metadata()
            self.ledger.cancel(key)
            return self.unavailable(key, 'cancelled')

    def accept(self, data):
        with self.store.lock:
            record, actor, key = self.binding(data, fields={
                'id', 'actor', 'revision', 'request_id', 'intention', 'proposal_digest', 'explicitly_accepted'})
            if self.config is None or self.closed:
                return self.unavailable(key, 'unconfigured')
            request = self.owned_request(record, actor, key)
            if request is None:
                return self.unavailable(key, 'unknown_request')
            payload = {field: data.get(field) for field in
                       ('id', 'actor', 'request_id', 'intention', 'proposal_digest', 'explicitly_accepted')}
            signature = digest(payload)
            saved = record.get('gameplay_requests', {}).get(key)
            if saved is not None:
                if saved['payload_digest'] != signature:
                    raise ValueError('Request identity was reused with different acceptance')
                return safe_result(saved['result'])
            if key in self.metadata['cancelled']:
                return self.unavailable(key, 'cancelled')
            if type(data.get('revision')) is not int or record['revision'] != data['revision']:
                return self.unavailable(key, 'stale_state')
            if pending_declaration(record, actor) is not None:
                return self.unavailable(key, 'pending_declaration')
            controlled_actor(record['state'], actor, required=True)
            world = CoreWorld(state=record['state'])
            committed = []

            def persist(expected, candidate_save, receipt):
                if self.scope(request) != expected:
                    raise self.api.CapabilityUnavailable('stale_scope_or_state')
                candidate = CoreWorld.load(candidate_save)
                outcome = receipt['outcome']
                settlement = request.operation_id == self.api.RISE_OPERATION
                kind = 'settlement_action' if settlement else 'scene_action'
                if settlement:
                    before = record['state']['elapsed_time']['seconds']
                    after = candidate.s['elapsed_time']['seconds']
                    elapsed = {'axis': candidate.s['elapsed_time']['axis'],
                               'before_seconds': before, 'after_seconds': after, 'seconds': after - before}
                else:
                    elapsed = {'axis': 'authored-opening-seconds',
                               'duration_seconds': outcome['elapsed_seconds'],
                               'total_seconds': outcome['elapsed_total']}
                result = safe_result({'request_id': key, 'campaign_id': record['id'], 'actor': actor,
                    'kind': kind, 'declaration': request.intention, 'status': receipt['status'],
                    'revision': record['revision'] + 1, 'recorded_sequence': candidate.s['clock'],
                    'elapsed_time': elapsed,
                    'narrative': None, 'outcome': outcome, 'receipt': receipt['receipt']})
                from local_presentation import receipt_presentation
                result['presentation'] = receipt_presentation(candidate, result,
                    engine_presentation=receipt.get('presentation'))
                record.setdefault('gameplay_requests', {})[key] = {
                    'campaign_id': record['id'], 'actor': actor, 'kind': kind,
                    'payload': payload, 'payload_digest': signature,
                    'result': copy.deepcopy(result), 'status': receipt['status']}
                self.store.commit(record, candidate, {'action_request_id': key})
                committed.append(result)

            try:
                self.actions.accept_proposal(world, self.ledger, request_id=key,
                    proposal_digest=data.get('proposal_digest'), actor_id=actor,
                    intention=data.get('intention'), branch_id=record['id'],
                    restore_id=self.restore_id(record['id']),
                    explicitly_accepted=data.get('explicitly_accepted'), persist=persist,
                    clock=self.broker.clock)
            except self.api.CapabilityUnavailable as error:
                return self.unavailable(key, error.code)
            # On normal acceptance persist writes receipt+world together. Recovery
            # reads the authoritative save first, even if ledger ack was lost.
            return committed[0] if committed else self.store.action_result(record['id'], key, actor)

    def close(self):
        self.closed = True
