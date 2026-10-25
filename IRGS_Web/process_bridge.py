"""Local host of Engine's typed process API, with no inference or new rules.

Only already received processes are offered. Start/capability discovery belongs
to Engine; appearance, private rule scans and browser commands cannot select it.
Technical requests/restore identities live outside the authoritative world.
"""
from contextlib import contextmanager
import copy
import hashlib
import hmac
import json
import re
import secrets
import sqlite3

from assistance import sync_parent
from core_world import CoreWorld
from gameplay_views import controlled_actor, pending_declaration, safe_result
from irgs_reference import digest


PUBLIC_PHASE = ('process_id', 'phase_id', 'phase_index', 'actor', 'kind', 'status',
                'terminal', 'original_intention', 'phase_intention', 'summary',
                'at', 'source_ref', 'elapsed_seconds', 'elapsed_total',
                'worked_seconds', 'remaining_seconds')


def commands(received):
    """Published command candidates, never a promise of current feasibility."""
    state = received['status']
    if state == 'cancelled':
        return []
    result = ['inspect']
    if state == 'active':
        result += ['advance', 'pause']
    elif state == 'paused':
        result += ['resume']
    elif state == 'held' and received['kind'] == 'work':
        result += ['pause']
    if state in ('active', 'paused', 'held') and received['kind'] != 'travel':
        result += ['cancel']
    return result


class ProcessService:
    def __init__(self, store):
        self.store = store
        self.path = store.folder / '.host' / 'processes.sqlite'
        previous = store.before_restore

        def rotate(key):
            # Before rename, including a restore of identical bytes. Failure
            # leaves the campaign in Trash, with old commands invalidated.
            with self.database() as db:
                db.execute('INSERT OR REPLACE INTO restores VALUES (?, ?)',
                           (key, secrets.token_hex(32)))
            if previous is not None:
                previous(key)
        store.before_restore = rotate

    @contextmanager
    def database(self):
        self.path.parent.mkdir(mode=0o700, exist_ok=True)
        self.path.touch(mode=0o600, exist_ok=True)
        try:
            db = sqlite3.connect(self.path)
        except sqlite3.Error:
            raise OSError('Process host storage is unavailable') from None
        try:
            db.execute('PRAGMA synchronous=FULL')
            db.execute('CREATE TABLE IF NOT EXISTS restores (branch TEXT PRIMARY KEY, identity TEXT NOT NULL)')
            db.execute('CREATE TABLE IF NOT EXISTS requests (branch TEXT, id TEXT, actor TEXT, '
                       'signature TEXT, request TEXT, revision INTEGER, token TEXT, status TEXT, '
                       'PRIMARY KEY (branch, id))')
            with db:
                yield db
        except sqlite3.Error:
            raise OSError('Process host storage is unavailable') from None
        finally:
            db.close()

    def scope(self, record):
        from runtime_contracts import WorldScope
        with self.database() as db:
            db.execute('INSERT OR IGNORE INTO restores VALUES (?, ?)',
                       (record['id'], secrets.token_hex(32)))
            restore = db.execute('SELECT identity FROM restores WHERE branch=?', (record['id'],)).fetchone()[0]
        world = CoreWorld(state=record['state'])
        return WorldScope(world.s['campaign_id'], record['id'], restore, world.checksum())

    def token(self, record):
        scope = self.scope(record)
        # Opaque browser guard; neither private world digest nor restore ID is
        # published. Every prepare/commit still authenticates the actual world.
        message = digest([scope.campaign_id, scope.branch_id, scope.state_digest, record['revision']])
        return hmac.new(scope.restore_id.encode(), message.encode(), hashlib.sha256).hexdigest()

    def view(self, record, actor):
        result = {'schema_version': 1, 'start_available': False, 'processes': [], 'view_token': None}
        if not actor:
            return result
        from process_runtime import received_status
        from solo_provider import CapabilityUnavailable
        world = CoreWorld(state=record['state'])
        for key, process in world.s.get('processes', {}).items():
            if process['actor'] != actor:
                continue
            try:
                received = received_status(world, actor, key)
            except CapabilityUnavailable:
                continue
            result['processes'].append({'received': {k: copy.deepcopy(received[k]) for k in PUBLIC_PHASE},
                                        'commands': commands(received)})
        if result['processes']:
            result['view_token'] = self.token(record)
        return result

    def binding(self, data, fields):
        if not isinstance(data, dict) or set(data) != fields:
            raise ValueError('Submit only the selected process command fields')
        if not isinstance(data.get('actor'), str) or not data['actor']:
            raise PermissionError('Explicitly select a player character')
        key = data.get('request_id')
        if not isinstance(key, str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,128}', key):
            raise ValueError('A stable phase request identity is required')
        record = self.store.read(data['id'])
        actor = controlled_actor(record['state'], data['actor'], required=True)
        return record, actor, key

    def row(self, branch, key):
        with self.database() as db:
            db.row_factory = sqlite3.Row
            row = db.execute('SELECT * FROM requests WHERE branch=? AND id=?', (branch, key)).fetchone()
            return dict(row) if row else None

    def public_request(self, row):
        from process_runtime import ProcessRequest
        request = ProcessRequest.from_json(row['request'])
        return {'request_id': row['id'], 'campaign_id': row['branch'], 'actor': request.actor,
                'revision': row['revision'], 'view_token': row['token'], 'status': row['status'],
                'process_id': request.process_id, 'phase_id': request.phase_id,
                'phase_index': request.phase_index, 'command': request.command,
                'details': json.loads(request.details_json), 'intention': request.intention}

    def prepare(self, data):
        fields = {'id', 'actor', 'revision', 'view_token', 'request_id', 'process_id',
                  'command', 'details', 'intention'}
        record, actor, key = self.binding(data, fields)
        signature = digest(data)
        prior = self.row(record['id'], key)
        if prior:
            if prior['actor'] != actor or prior['signature'] != signature:
                raise ValueError('Phase request identity was reused with different choices')
            return self.public_request(prior)
        if key in record.get('gameplay_requests', {}):
            raise ValueError('Request identity is already in use')
        if (type(data['revision']) is not int or data['revision'] != record['revision']
                or not isinstance(data['view_token'], str) or data['view_token'] != self.token(record)):
            raise ValueError('This process view changed. Reload before reviewing another phase.')
        if pending_declaration(record, actor):
            raise ValueError('Withdraw the unresolved declaration before reviewing a process command')
        available = next((p for p in self.view(record, actor)['processes']
                          if p['received']['process_id'] == data['process_id']), None)
        if not available or data['command'] not in available['commands']:
            raise ValueError('This process command is not offered by the received record')
        details = data['details']
        if (not isinstance(details, dict) or
                (data['command'] == 'advance' and (set(details) != {'seconds'} or
                 type(details['seconds']) is not int or not 0 < details['seconds'] <= 9007199254740991)) or
                (data['command'] != 'advance' and details)):
            raise ValueError('Advance requires an explicit positive whole number of seconds; other commands take no details')
        from process_runtime import prepare
        from solo_provider import CapabilityUnavailable
        scope = self.scope(record)
        try:
            request = prepare(CoreWorld(state=record['state']), phase_id='web-' + secrets.token_hex(16),
                process_id=data['process_id'], actor=actor, command=data['command'], details=details,
                intention=data['intention'], source_ref='explicit-player-process:' + record['id'] + ':' + key,
                branch_id=record['id'], restore_id=scope.restore_id)
        except CapabilityUnavailable:
            raise ValueError('This process request could not be prepared') from None
        with self.database() as db:
            db.execute('INSERT INTO requests VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                (record['id'], key, actor, signature, request.to_json(), record['revision'], data['view_token'], 'prepared'))
        return self.public_request(self.row(record['id'], key))

    def status(self, data):
        record, actor, key = self.binding(data, {'id', 'actor', 'request_id'})
        saved = record.get('gameplay_requests', {}).get(key)
        if saved and saved.get('campaign_id') == record['id'] and saved.get('actor') == actor and saved.get('kind') == 'process_phase':
            sync_parent(self.store.path(record['id']))
            return safe_result(saved['result'])
        row = self.row(record['id'], key)
        if not row:
            raise FileNotFoundError('No prepared phase is available')
        if row['actor'] != actor:
            raise PermissionError('This phase belongs to another character')
        result = self.public_request(row)
        if row['revision'] != record['revision'] or row['token'] != self.token(record):
            result['status'] = 'stale'
        return result

    def execute(self, data):
        record, actor, key = self.binding(data, {'id', 'actor', 'request_id', 'explicitly_accepted'})
        if data['explicitly_accepted'] is not True:
            raise ValueError('Explicit acceptance is required')
        saved = record.get('gameplay_requests', {}).get(key)
        if saved:
            if saved.get('campaign_id') != record['id'] or saved.get('actor') != actor or saved.get('kind') != 'process_phase':
                raise ValueError('Request identity is already in use')
            sync_parent(self.store.path(record['id']))
            return safe_result(saved['result'])
        row = self.row(record['id'], key)
        if not row or row['actor'] != actor:
            raise PermissionError('No own prepared phase is available')
        if row['status'] == 'rejected':
            raise ValueError('This phase was rejected. Review a fresh command.')
        if (row['revision'] != record['revision'] or row['token'] != self.token(record)
                or pending_declaration(record, actor)):
            raise ValueError('This prepared phase is stale. Reload and review a fresh command.')
        from process_runtime import ProcessRequest, execute
        from solo_provider import CapabilityUnavailable
        request = ProcessRequest.from_json(row['request'])
        world = CoreWorld(state=record['state'])
        committed = None

        def persist(expected, candidate, received):
            nonlocal committed
            current = self.store.read(record['id'])
            if (current['revision'] != row['revision'] or self.scope(current) != expected):
                raise ValueError('The campaign changed before this phase could be saved')
            candidate_world = CoreWorld(state=json.loads(candidate))
            event = 'process:' + request.phase_id
            result = {'request_id': key, 'campaign_id': record['id'], 'actor': actor,
                'kind': 'process_phase', 'status': 'completed_successfully',
                'revision': current['revision'] + 1, 'recorded_sequence': received['at'],
                'outcome': {'summary': received['summary']}, 'receipt': {'event_id': event},
                'process': {k: copy.deepcopy(received[k]) for k in PUBLIC_PHASE},
                'elapsed_time': {'axis': candidate_world.s['elapsed_time']['axis'],
                    'duration_seconds': received['elapsed_seconds'], 'total_seconds': received['elapsed_total']}}
            from local_presentation import receipt_presentation
            result['presentation'] = receipt_presentation(candidate_world, result,
                                                        engine_presentation=received.get('presentation'))
            current.setdefault('gameplay_requests', {})[key] = {'campaign_id': record['id'], 'actor': actor,
                'kind': 'process_phase', 'status': result['status'], 'payload_digest': row['signature'], 'result': result}
            # The candidate world AND exact received result share one fsynced
            # atomic replacement, before Engine or HTTP can acknowledge it.
            self.store.commit(current, candidate_world, result)
            committed = result

        try:
            execute(world, request, current_scope=self.scope(record), persist=persist, explicitly_accepted=True)
        except CapabilityUnavailable:
            with self.database() as db:
                db.execute('UPDATE requests SET status=? WHERE branch=? AND id=?', ('rejected', record['id'], key))
            raise ValueError('This phase could not be accepted under the current Engine rules. No phase was committed.') from None
        except OSError:
            with self.database() as db:
                db.execute('UPDATE requests SET status=? WHERE branch=? AND id=?', ('save_failed', record['id'], key))
            raise
        if committed is None:
            # Normal replay is recovered from the durable App result above.
            raise ValueError('Reload the durable phase result before retrying')
        return committed
