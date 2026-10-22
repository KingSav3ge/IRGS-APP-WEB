"""Out-of-character campaign-world references; never initialize saved state."""
import copy
import json
from pathlib import Path
from engine_paths import ENGINE_ROOT

WORLD_FILES = {
    'world-of-kira': ENGINE_ROOT / 'catalog/campaigns/kira/world.json',
}


def world_reference(world_id):
    if world_id not in WORLD_FILES:
        raise ValueError('Unknown campaign world')
    world = json.loads(WORLD_FILES[world_id].read_text(encoding='utf-8'))
    if (world.get('id') != world_id or world.get('kind') != 'campaign_world'
            or world.get('schema_version') != 1
            or world.get('readiness', {}).get('guide_available') is not True
            or world['readiness'].get('ready') is not False
            or world['readiness'].get('playable') is not False
            or world['readiness'].get('starting_snapshots') != []):
        raise ValueError('Campaign world reference is invalid')
    # Only the authored public guide is projected. Raw character sheets,
    # source quotations and editorial review stay in the source package.
    # No save, actor knowledge, inventory or live authority is consulted.
    return copy.deepcopy({key: world[key] for key in (
        'id', 'title', 'version', 'kind', 'status', 'summary', 'reference_period', 'guide')})


def world_listing(world_id):
    world = world_reference(world_id)
    return {key: world[key] for key in ('id', 'title', 'kind', 'status', 'summary')} | {
        'period': world['reference_period'], 'periods': [], 'entry_count': 0,
        'playable_entry_count': 0, 'reference_id': world['id'],
        'launch_capability': 'reference_only',
        'readiness': 'World guide available. Starting snapshots are in development.',
    }
