"""Ephemeral App preflight over the current Engine's actor-visible capabilities.

Not the pending Engine start-context contract or a continuing-world migration.
No action execution, persistence, provider use or private feasibility probes.
"""
from campaign_library import initial_campaign
from gameplay_views import playthrough
from starting_selection import initialize_player
from phase_contract import actor_view


def capability_summary(projection, starts):
    pending = projection.get('pending_declaration') is not None
    actions = (projection.get('settlement') or {}).get('actions', projection.get('supported_actions', []))
    actions = [] if pending else actions
    starts = [] if pending else starts
    available = projection.get('character_available') is True and bool(projection.get('actor_id'))
    actions, starts = (actions, starts) if available else ([], [])
    status = ('unavailable' if not available else 'pending_declaration' if pending else
              'supported_slice' if actions or starts else 'declaration_only')
    return {'schema_version': 1, 'basis': 'current_actor_view', 'status': status,
            'action_count': len(actions), 'process_start_count': len(starts),
            'action_titles': [item.get('title', 'Received action') for item in actions],
            'process_titles': [item['title'] for item in starts],
            'general_freeform_resolution': False}


def preview_start(fields):
    allowed = {'profile_id', 'scenario_id', 'entry_id', 'snapshot_sha256',
               'starting_scenario_id', 'selection_digest', 'character_kind',
               'actor_id', 'entity_id', 'species', 'opening_id', 'mode'}
    if set(fields) - allowed:
        raise ValueError('Unknown starting preview field')
    base = {key: fields[key] for key in ('profile_id', 'scenario_id', 'entry_id', 'snapshot_sha256') if key in fields}
    character = {'kind': fields.get('character_kind')}
    if character['kind'] == 'new':
        if fields.get('actor_id') or fields.get('entity_id'):
            raise ValueError('New-character preview cannot select an existing actor')
        # Testimony and names grant no capability. Keep them out of URLs/logs;
        # real creation retains the exact user-supplied fields as before.
        character.update(name='Preview character', species=fields.get('species', 'human'), background='')
        if fields.get('opening_id'):
            character['opening_id'] = fields['opening_id']
    else:
        if fields.get('opening_id') or fields.get('species'):
            raise ValueError('Existing characters cannot receive a new-character fictional opening')
        character.update({key: fields[key] for key in ('actor_id', 'entity_id') if key in fields})
    world = initial_campaign(campaign_id='APP-START-PREVIEW', **base)
    world = initialize_player(world, character=character,
        starting_scenario_id=fields.get('starting_scenario_id', 'individual'),
        selection_digest=fields.get('selection_digest'), request_ref='explicit-app-start-preview')
    actor = world.s['gameplay_started']['actor_id']
    projection = playthrough({'id': 'preview', 'name': 'Starting preview', 'revision': 0,
                              'state': world.s}, actor)
    phases = actor_view(world, actor, branch_id='app-start-preview', restore_id='app-start-preview')
    return {**capability_summary(projection, phases['start_options']),
            'preview_only': True, 'engine_start_context_contract': False,
            'character_kind': character['kind'], 'opening_id': character.get('opening_id'),
            'scene': projection['scene'], 'campaign_time': projection['campaign_time'],
            'elapsed_time': projection['elapsed_time']}
