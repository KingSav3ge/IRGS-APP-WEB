"""Actor-known opening presentation, never a new world event or knowledge grant."""
import copy

VERSION = 2
PROMPT = ('Choose what your character says or attempts. Your exact words are recorded as intent. '
          'General action resolution and narration are unavailable; no outcome or elapsed time is assumed.')


def build_opening(state, actor_id):
    if not state.get('historical_start') or actor_id not in state.get('player_actor_ids', []):
        return None
    # Reuse the same permission boundary as ordinary player reads. This does
    # not read historical setup facts or turn an author's briefing into news.
    from gameplay_views import playthrough
    projection = playthrough({'id': state['campaign_id'], 'name': 'Opening preview', 'revision': 0, 'state': state}, actor_id)
    actor = projection['character']
    blocks = [{'kind': 'character', 'text': 'You are ' + actor['name'] + '.', 'source_ids': []}]
    scene = projection['scene']
    if scene.get('location'):
        blocks.append({'kind': 'scene', 'text': 'Your recorded location: ' + str(scene.get('title') or scene['location']), 'source_ids': []})
    else:
        blocks.append({'kind': 'scene', 'text': 'Your current location and nearby people have not been established.', 'source_ids': []})
    evidence = [item for item in projection['evidence'] if item['id'] != 'setup:background-details']
    if evidence:
        received = max(evidence, key=lambda item: item['received_at'])
        own_background = received['id'] == 'setup:background'
        heading = ('Your declared background (' + received['status'] + ')' if own_background
                   else 'Received ' + received['status'])
        blocks.append({'kind': 'received_record', 'text': heading + ':\n' + received['assertion'],
                       'assertion': received['assertion'], 'status': received['status'],
                       'source_kind': 'declared_background' if own_background else 'received_evidence',
                       'record_id': received['id'], 'source_ids': [received['receipt_ref']]})
    elif projection['orders']:
        received = max(projection['orders'], key=lambda item: item['received_at'])
        blocks.append({'kind': 'received_record', 'text': 'Received order:\n' + received['content'],
                       'content': received['content'], 'status': 'received', 'source_kind': 'received_order',
                       'record_id': received['id'], 'source_ids': []})
    prompt = ('Use a listed action to move, observe or deliver the dispatch in your selected fictional opening. '
              'The actual result and stated local duration will be saved; an attempt can fail. '
              'Your own written response remains available as unresolved intent.'
              if projection['capabilities'].get('playable_opening') else PROMPT)
    blocks.append({'kind': 'first_decision', 'text': prompt, 'source_ids': []})
    return {'id': 'opening:' + state['campaign_id'], 'version': VERSION,
        'scope_campaign_id': state['campaign_id'], 'actor_id': actor_id, 'title': 'Your opening', 'blocks': blocks,
        'presented_at_sequence': state['clock'], 'effects_applied': False,
        'narration': 'actor_known_presentation', 'presentation_only': True}


def opening_view(state, actor_id, *, requests=None, save_id=None):
    opening = state.get('opening_scene')
    if (not isinstance(opening, dict) or opening.get('version') != VERSION
            or opening.get('scope_campaign_id') != state['campaign_id'] or opening.get('actor_id') != actor_id):
        return None
    result = {key: copy.deepcopy(opening[key]) for key in
        ('id', 'version', 'title', 'blocks', 'presented_at_sequence', 'effects_applied', 'narration', 'presentation_only')}
    statuses = []
    for event in state.get('journal', []):
        if (event['op'] in ('execute_player_scene_action', 'execute_player_equipment_issue')
                and event.get('params', {}).get('actor') == actor_id
                and event['at'] >= opening['presented_at_sequence']):
            statuses.append('completed')
            continue
        if (event['op'].removeprefix('ast_') != 'record_player_action' or event.get('params', {}).get('actor') != actor_id
                or event['at'] < opening['presented_at_sequence']):
            continue
        request_id = event['id'].removeprefix('gameplay:')
        request = (requests or {}).get(request_id)
        withdrawn = (request and request.get('campaign_id') == save_id and request.get('actor') == actor_id
                     and request.get('kind') == 'declaration' and request.get('status') == 'withdrawn')
        statuses.append('withdrawn' if withdrawn else 'declared')
    result['status'] = ('first_action_declared' if 'declared' in statuses else
                        'interaction_started' if 'completed' in statuses else
                        'first_attempt_withdrawn' if statuses else 'awaiting_first_action')
    return result
