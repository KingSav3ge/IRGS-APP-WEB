"""Read-only, allowlisted projection of Engine's private technical attempt ledger.

Only the Creator HTTP route may call this projection. Request text, context,
acceptance certificates, private paths and dependency reads never leave storage.
Reservations are operator units, never a price estimate or verified bill.
"""
import json
import math

IDENTITY_FIELDS = ('developer', 'gateway', 'host', 'model', 'model_version')
TOKEN_FIELDS = ('input_tokens', 'output_tokens', 'cached_input_tokens', 'reasoning_tokens')


def _object(value):
    try:
        result = json.loads(value or '{}')
        return result if isinstance(result, dict) else {}
    except (ValueError, TypeError):
        return {}


def _text(value, limit=256):
    return value[:limit] if isinstance(value, str) else None


def _time(value):
    return value if type(value) in (int, float) and math.isfinite(value) else None


def usage_snapshot(ledger, *, limit=25):
    if type(limit) is not int or not 1 <= limit <= 50:
        raise ValueError('Choose between 1 and 50 recent attempts')
    if ledger is None:
        return {'status': 'unconfigured', 'attempts': [], 'summary': None,
                'billing_status': 'unknown', 'message': 'No assistance ledger is configured. This check makes no provider request.'}
    with ledger.connection() as db:
        # One read transaction keeps aggregate totals and recent rows consistent.
        db.execute('BEGIN')
        budget, max_inflight = db.execute('SELECT budget,inflight FROM limits WHERE id=1').fetchone()
        totals = db.execute('SELECT a.reserved,a.finished,a.status,r.charged_units FROM attempts a'
            ' LEFT JOIN reconciliations r ON a.id=r.attempt_id').fetchall()
        count = len(totals)
        reserved = sum(row[0] for row in totals)
        held = sum(row[0] for row in totals if row[3] is None)
        charged = sum(row[3] for row in totals if row[3] is not None)
        unknown = sum(row[3] is None for row in totals)
        active = sum(row[1] == 0 for row in totals)
        unfinished = sum(row[2] == 'processing' for row in totals)
        rows = db.execute('SELECT a.id,a.route,a.reserved,a.status,a.finished,a.requested_identity,a.reported_identity,a.usage,'
            'a.started,a.completed,a.accepted IS NOT NULL,json_extract(a.result,\'$.code\'),'
            'a.transport_state,a.dispatch_started,r.charged_units FROM attempts a'
            ' LEFT JOIN reconciliations r ON a.id=r.attempt_id'
            ' ORDER BY a.started DESC,a.id DESC LIMIT ?', (limit,)).fetchall()
    attempts = []
    for row in rows:
        (request_id, route, units, status, finished, requested, reported, usage,
         started, completed, accepted, code, transport_state, dispatch_started, reviewed_charge) = row
        tokens = _object(usage)
        reported_tokens = {key: tokens[key] for key in TOKEN_FIELDS
                           if type(tokens.get(key)) is int and tokens[key] >= 0}
        attempts.append({'request_id': _text(request_id, 128), 'route_id': _text(route),
            'reserved_units': units, 'status': status if status in ('processing', 'proposal_ready', 'unavailable') else 'unknown',
            'code': _text(code), 'acceptance_recorded': bool(accepted), 'transport_finished': bool(finished),
            'transport_state': transport_state if transport_state in ('not_started', 'admitted', 'unknown') else 'unknown',
            'requested_identity': {key: _text(_object(requested).get(key)) for key in IDENTITY_FIELDS},
            'reported_identity': {key: _text(_object(reported).get(key)) for key in IDENTITY_FIELDS},
            'reported_tokens': {key: reported_tokens.get(key) for key in TOKEN_FIELDS},
            'usage_status': 'reported' if reported_tokens else 'unknown',
            'billing_status': 'unknown' if reviewed_charge is None else 'operator_reconciled',
            'reviewed_charge_units': reviewed_charge,
            'started_at': _time(started), 'completed_at': _time(completed),
            'dispatch_admitted_at': _time(dispatch_started)})
    return {'status': 'available', 'billing_status': 'unknown',
        'message': 'Unreconciled attempts retain their reservations, including failures and cancellations. Available units use the Engine admission calculation: unreconciled holds plus operator-reviewed final charges. Missing reports remain unknown; this view does not verify provider bills. Acceptance recorded describes the technical acknowledgement; Core receipts remain authoritative. Inspection never retries or reconciles an attempt.',
        'summary': {'attempts_total': count, 'budget_units': budget, 'reserved_units': reserved,
                    'held_units': held, 'known_charged_units': charged, 'unknown_attempts': unknown,
                    'remaining_units': max(0, budget - held - charged),
                    'overrun_units': max(0, held + charged - budget), 'active_transport_slots': active,
                    'maximum_transport_slots': max_inflight, 'unfinished_or_in_doubt': unfinished},
        'attempts': attempts, 'recent_limit': limit, 'has_more': count > len(attempts)}
