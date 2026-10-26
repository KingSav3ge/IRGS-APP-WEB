"""Atomic host transport and actor-filtered presentation for the Rise compiler."""
import copy
import hashlib
import json
import re
from irgs_reference import digest
from gameplay_views import controlled_actor, pending_declaration, safe_result
from settlement_setup import initialize, templates, preview
from settlement_runtime import ACTIONS, execute, household_of, location, _free


def _identity(value):
    if not isinstance(value, str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,128}', value):
        raise ValueError('A stable request identity is required')
    return value


def create(store, data):
    with store.lock:
        if not isinstance(data, dict) or set(data) - {'name', 'choices', 'review_digest', 'request_id', 'mode'}:
            raise ValueError('Use the reviewed settlement setup')
        request = _identity(data.get('request_id'))
        name = data.get('name')
        if not isinstance(name, str) or not name.strip() or len(name.strip()) > 100:
            raise ValueError('Supply a campaign name using 1–100 characters')
        payload = {k: copy.deepcopy(data.get(k)) for k in ('name', 'choices', 'review_digest')}
        signature = digest(payload)
        key = hashlib.sha256(('IRGS-rise-create:' + request).encode()).hexdigest()[:32]
        active, trashed = store.path(key), store.trash_path(key)
        existing = [p for p in (active, trashed) if p.exists()]
        if len(existing) > 1: raise ValueError('Campaign identity collision; neither save was changed')
        if existing:
            record = json.loads(existing[0].read_text(encoding='utf-8'))
            prior = record.get('creation_request', {})
            if prior.get('id') != request or prior.get('payload_digest') != signature:
                raise ValueError('Creation identity was reused with different starting choices')
            return {**{k: record[k] for k in ('id', 'name', 'revision')}, 'creation_replayed': True,
                    'status': 'active' if existing[0] == active else 'trashed'}
        world = initialize(data.get('choices'), data.get('review_digest'), 'IRGS-' + key)
        record = {'id': key, 'name': name.strip(), 'revision': 0, 'state': world.s,
                  'creation_request': {'id': request, 'payload_digest': signature}}
        store.write(record)
        return {k: record[k] for k in ('id', 'name', 'revision')}


def action(store, data):
    with store.lock:
        allowed = {'id', 'revision', 'actor', 'request_id', 'action', 'mode'}
        if not isinstance(data, dict) or set(data) - allowed:
            raise ValueError('Use the listed settlement action')
        request = _identity(data.get('request_id'))
        if not isinstance(data.get('actor'), str) or not data['actor']:
            raise ValueError('Explicitly select the acting founder')
        record = store.read(data['id'])
        actor = controlled_actor(record['state'], data['actor'])
        payload = {'campaign_id': record['id'], 'actor': actor, 'kind': 'settlement_action', 'action': data.get('action')}
        signature = digest(payload)
        saved = record.get('gameplay_requests', {}).get(request)
        if saved is not None:
            if saved.get('campaign_id') != record['id'] or saved.get('payload_digest') != signature:
                raise ValueError('Request identity was reused with different action choices')
            return safe_result(saved['result'])
        controlled_actor(record['state'], actor, required=True)
        if type(data.get('revision')) is not int or data['revision'] != record['revision']:
            raise ValueError('This campaign changed. Reload before submitting a new request.')
        if pending_declaration(record, actor) is not None:
            raise ValueError('Withdraw your unresolved declaration before another action')
        from core_world import CoreWorld
        world = CoreWorld(state=record['state'])
        before = world.s.get('elapsed_time', {}).get('seconds', 0)
        resolved = execute(world, request, actor, payload['action'], 'explicit-player-request:' + record['id'] + ':' + request)
        after = world.s['elapsed_time']['seconds']
        summary = world.s['settlement_receipts'][actor][request]['text']
        result = {'request_id': request, 'campaign_id': record['id'], 'actor': actor,
            'kind': 'settlement_action', 'status': 'completed_successfully', 'revision': record['revision']+1,
            'recorded_sequence': world.s['clock'],
            'elapsed_time': {'axis': 'settlement-seconds', 'before_seconds': before, 'after_seconds': after, 'seconds': after-before},
            'outcome': {'summary': summary}, 'narrative': summary,
            'receipt': {'event_id': resolved['event_id'], 'request_id': request}}
        from local_presentation import receipt_presentation
        result['presentation'] = receipt_presentation(world, result)
        record.setdefault('gameplay_requests', {})[request] = {
            'campaign_id': record['id'], 'actor': actor, 'kind': 'settlement_action', 'payload': payload,
            'payload_digest': signature, 'status': result['status'], 'result': copy.deepcopy(result),
            'dependencies': resolved['certificate']}
        store.commit(record, world, {'action_request_id': request})
        return result


def view(state, actor):
    """Explicit local inspection, never raw private state or distant truth."""
    if state.get('binding', {}).get('campaign_profile') != 'rise': return None
    # The published R00 gameplay/draft adapter is founder-only. Other selected
    # characters retain their ordinary received view and communication rights;
    # a roster entry does not grant the founder's household inspection/actions.
    if actor != 'founder': return None
    controlled_actor(state, actor, required=True)
    h = household_of(state, actor)
    site = location(state, actor)
    at_stores = state['stock_accounts'][h]['site'] == site
    camp = state['settlements'].get('camp')
    visible_camp = None
    if camp and site == camp['site']:
        members = [a for home in camp['households'] for a in state['households'][home]['members']]
        present = [a for a in members if location(state, a) == site]
        places = sum(a['places'] for a in state['assets'].values() if a['site'] == site)
        visible_camp = {'name': camp['name'], 'residents': len(members), 'present': len(present),
                        'shelter_places': places, 'shelter_shortfall': max(0, len(present)-places)}
    projects = [{'kind': p['kind'], 'worker': state['actors'][p['worker']]['name'], 'status': p['status'],
                 'worked_seconds': p['worked'], 'required_seconds': p['duration']}
                for p in state['projects'].values() if p['site'] == site]
    assessments = [copy.deepcopy(a) for a in state['provision']['assessments'].values() if a['household'] == h] if at_stores else []
    units = state['settlement_model'].get('units', {})
    inventory = [{'material': material, 'quantity': quantity, 'unit': units.get(material),
                  'unit_status': 'configured' if units.get(material) else 'unconfigured',
                  'available': max(0, _free(state, h, material)),
                  'reserved_for_work': sum(p['timber'] if material == 'timber' else 1 if material == 'axe' else 0
                      for p in state['projects'].values() if p['household'] == h and p['status'] == 'active'),
                  'protected_seed': min(quantity, state['households'][h]['seed_reserve']) if material == 'grain' else 0}
                 for material, quantity in state['stocks'][h].items()] if at_stores else None
    return {'version': state['rise']['version'], 'region': state['rise']['choices']['region_name'],
        'opening_date': state['rise']['choices']['date_label'], 'location': site,
        'elapsed_seconds': state['elapsed_time']['seconds'], 'household_name': state['households'][h]['name'],
        'inventory': inventory, 'seed_reserve': (min(state['stocks'][h].get('grain', 0), state['households'][h]['seed_reserve']) if at_stores else None), 'camp': visible_camp,
        'projects': projects, 'provision': assessments[-1] if assessments else None,
        'people': [state['actors'][key]['name'] for key in state['actors'] if location(state, key) == site],
        'receipts': list(copy.deepcopy(state['settlement_receipts'].get(actor, {})).values()),
        'actions': [{'id': key, 'title': title, 'description': description} for key, title, description in ACTIONS],
        'limits': copy.deepcopy(state['settlement_model']['limits'])}


def listing():
    return {'id': 'rise', 'kind': 'settlement_system', 'title': 'The Rise of... You',
        'summary': 'Found a household and settlement in a fictional region. Permission, supplies, work and neighbors share one continuing world.',
        'status': 'Fictional foundation available; eight design families held',
        'templates': templates()['templates']}
