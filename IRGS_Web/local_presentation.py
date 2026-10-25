"""Read-only adapters for the reviewed Engine runtime and Catalog response depot.

World authorization/execution stays with Core. No browser-supplied fact packets,
provider calls, personalized caches or extra campaign state live in this module.
"""
from functools import lru_cache
import hashlib
import json
import secrets
from types import ModuleType

from catalog_paths import CATALOG_ROOT


@lru_cache(maxsize=1)
def _catalog():
    # Verify only the release-bound files this adapter actually consumes. The
    # ordinary component/launcher check still verifies the whole pinned release.
    release = json.loads((CATALOG_ROOT / 'release.json').read_text(encoding='utf-8'))
    names = ('scripted_responses.py', 'responses/depot_v1/library.json')
    checked = {}
    for name in names:
        path = CATALOG_ROOT / name
        if any(parent.is_symlink() for parent in (path, *path.parents)):
            raise ValueError('Response depot integrity unavailable')
        raw = path.read_bytes()
        if len(raw) > 1048576 or hashlib.sha256(raw).hexdigest() != release['files_sha256'][name]:
            raise ValueError('Response depot integrity unavailable')
        checked[name] = raw
    # Import loaders and load_library would reopen mutable files after the pin
    # check. Compile and decode only the exact bytes checked above.
    formatter = ModuleType('_irgs_app_catalog_responses')
    formatter.__file__ = str(CATALOG_ROOT / names[0])
    exec(compile(checked[names[0]], formatter.__file__, 'exec'), formatter.__dict__)
    library = json.loads(checked[names[1]], object_pairs_hook=formatter._pairs)
    formatter.validate_library(library)
    if library['library_id'] != 'irgs-response-depot-v1' or library['schema_version'] != 2:
        raise ValueError('Response depot compatibility unavailable')
    return formatter, library


def _variant(*parts, count):
    key = json.dumps(parts, ensure_ascii=False).encode()
    return int(hashlib.sha256(key).hexdigest()[:16], 16) % count


def _frame(actor, snapshot, source, family, values):
    return {'actor_id': actor, 'snapshot_id': snapshot, 'source_ref': source,
            'source_kind': family['source_kind'], 'state': family['state'], 'values': values}


def receipt_presentation(world, result, *, engine_presentation=None):
    """Decorate a real, actor-authorized Core result before the atomic save.

    Replay returns the saved decoration. No current facts are appended to an
    older saved result, and metadata is never another authority over the world.
    """
    actor, event = result['actor'], result['receipt']['event_id']
    summary = result['outcome']['summary']
    exact = '\n'.join([summary, *result['outcome'].get('observations', [])])
    text, mode = exact, 'literal_receipt'
    engine_library = None
    try:
        if engine_presentation is None:
            from offline_responses import render_receipt
            engine_presentation = render_receipt(world, actor, event)
        if (engine_presentation['actor_id'] != actor or engine_presentation['format'] != 'plain_text'
                or not engine_presentation['text'].startswith(exact)
                or engine_presentation['render_usage'] != {'provider_calls': 0, 'model_tokens': 0}):
            raise ValueError('Response runtime compatibility unavailable')
        text, mode = engine_presentation['text'], engine_presentation['mode']
        engine_library = {'id': engine_presentation['library_id'], 'version': engine_presentation['library_version']}
    except (ImportError, ValueError, TypeError, KeyError, OSError):
        pass  # Preserve the exact authorized receipt, never a private reason.
    catalog_library = None
    snapshot = 'result:' + secrets.token_hex(16)
    try:
        formatter, library = _catalog()
        family = next(item for item in library['families'] if item['id'] == 'receipt.exact')
        text = formatter.compose_recipe(library, 'routine.result', {
            'receipt.exact': _frame(actor, snapshot, 'receipt:' + event, family, {'receipt_text': text})})
        catalog_library = {'id': library['library_id'], 'version': library['version']}
    except (ImportError, ValueError, TypeError, KeyError, StopIteration, OSError):
        pass
    return {'format': 'plain_text', 'text': text, 'mode': mode, 'actor_id': actor,
            'source_ref': event, 'snapshot_id': snapshot, 'engine_library': engine_library,
            'catalog_library': catalog_library, 'render_usage': {'provider_calls': 0, 'model_tokens': 0}}


def response_view(record, projection):
    """One public contract for supported campaign adapters; appearance is unused."""
    actor = projection['actor_id']
    scope = {'campaign_id': record['id'], 'actor_id': actor, 'revision': record['revision'],
             'view_id': secrets.token_hex(16)}
    result = {'schema_version': 1, 'scope': scope, 'drafts': [], 'catalog_library': None,
              'engine_runtime': False, 'render_usage': {'provider_calls': 0, 'model_tokens': 0}}
    if not actor or not projection['character_available']:
        return result
    # Generic semantic tags are not operation IDs. Supply only known public
    # labels, never target people/resources inferred from private world state.
    location = projection['scene'].get('location')
    candidates = [('player.look_around', 'Look around', {}), ('player.wait', 'Consider waiting', {})]
    if isinstance(location, str) and 0 < len(location) <= 160:
        candidates += [('player.observe', 'Observe ' + location, {'target_label': location}),
                       ('player.inspect', 'Inspect ' + location, {'target_label': location})]
    try:
        formatter, library = _catalog()
        families = {family['id']: family for family in library['families']}
        catalog_drafts = []
        for key, title, values in candidates:
            family = families[key]
            variant = _variant(record['id'], actor, key, values, count=len(family['variants']))
            text = formatter.render_fragment(library, key,
                _frame(actor, scope['view_id'], 'view:' + key, family, values), variant=variant)
            catalog_drafts.append({'id': 'catalog:' + key, 'title': title, 'text': text,
                'source': 'catalog', 'intent_tag': family['intent_tag'], 'operation_id': None,
                'requires_explicit_submission': True, 'automatic_execution': False})
        result['drafts'].extend(catalog_drafts)
        result['catalog_library'] = {'id': library['library_id'], 'version': library['version']}
    except (ImportError, ValueError, TypeError, KeyError, OSError):
        pass
    try:
        from core_world import CoreWorld
        from offline_responses import player_drafts
        packet = player_drafts(CoreWorld(state=record['state']), actor)
        if (packet['actor_id'] != actor or packet['format'] != 'plain_text'
                or packet['render_usage'] != {'provider_calls': 0, 'model_tokens': 0}):
            raise ValueError('Response scope unavailable')
        groups = {}
        for draft in packet['drafts']:
            groups.setdefault((draft['operation'], draft['action_id']), []).append(draft)
        titles = {item.get('action_id', item.get('order_id')): item.get('title', item.get('text'))
                  for item in projection['supported_actions']}
        titles.update({item['id']: item['title'] for item in projection.get('settlement', {}).get('actions', [])})
        for (operation, action), drafts in groups.items():
            draft = drafts[_variant(record['id'], actor, operation, action, count=len(drafts))]
            if action not in titles or draft['automatic_execution'] is not False:
                continue
            result['drafts'].append({'id': 'engine:' + operation + ':' + action,
                'title': 'Consider: ' + titles[action], 'text': draft['text'], 'source': 'engine',
                'intent_tag': None, 'operation_id': operation,
                'requires_explicit_submission': True, 'automatic_execution': False})
        result['engine_runtime'] = True
    except (ImportError, ValueError, TypeError, KeyError, OSError):
        pass
    return result
