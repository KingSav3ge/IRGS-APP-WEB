"""Temporary offline host for qualify_solo_browser.js; never a product launcher."""
from dataclasses import replace
import json
from pathlib import Path
import sys
import threading
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'IRGS_Web/tests'))
from test_solo_bridge import SOLO_API, SoloBridgeTests

if __name__ == '__main__':
    if not SOLO_API or len(sys.argv) not in (2, 3):
        raise SystemExit('Select the exact Solo Engine using IRGS_ENGINE_ROOT and supply a temporary metadata path')
    metadata = Path(sys.argv[1])
    host = SoloBridgeTests()
    host.setUp()
    host.stop()
    if len(sys.argv) == 3 and sys.argv[2] == 'routine':
        record = host.store.read(host.key)
        record['state']['scene_rules']['actions']['look-quay']['success_text'] = (
            'No supplies were moved.\n<img src=x onerror="window.receiptExecuted=true"> {source_text}')
        host.store.write(record)
    transport = host.transport

    def offline(model_input, route, **limits):
        transport.action = next((action for action in ('enter-passage', 'reach-desk', 'look-desk')
                                 if action in model_input['allowed_actions']), model_input['allowed_actions'][0])
        transport.error = 'provider_denied' if model_input['intention'] == 'PROVIDER_DENIED' else None
        if model_input['intention'] == 'WAIT_FOR_NAVIGATION':
            time.sleep(1)
        result = transport(model_input, route, **limits)
        metadata.with_suffix('.inputs.json').write_text(json.dumps(transport.inputs), encoding='utf-8')
        return result

    host.config = (None if len(sys.argv) == 3 and sys.argv[2] in ('shared', 'processes')
                   else replace(host.config, transport=offline, deadline_seconds=5))
    host.start()
    details = {'port': host.server.server_port, 'save': str(host.store.path(host.key)), 'id': host.key}
    if len(sys.argv) == 3 and sys.argv[2] == 'presentation':
        from campaign_library import initial_campaign
        from starting_selection import options_for_world
        from historical_campaigns import historical_entry
        from settlement_setup import initialize, preview
        from test_settlement import choices
        import uuid
        campaigns = {}
        for profile in ('military', 'roman', 'fantasy', 'paf', 'shinobi', 'space'):
            world = initial_campaign(profile)
            reviewed = options_for_world(world)
            saved = host.store.create('Synthetic ' + profile, profile,
                character={'kind': 'new', 'name': 'Theme reader', 'species': 'human', 'background': ''},
                selection_digest=reviewed['selection_digest'])
            campaigns[profile] = saved['id']
        entry = historical_entry('hyw-1415')
        fields = {'scenario_id': 'hundred-years-war', 'entry_id': 'hyw-1415',
                  'snapshot_sha256': entry['snapshot_sha256']}
        world = initial_campaign('military', **fields)
        reviewed = options_for_world(world)
        saved = host.store.create('Synthetic Century', 'military', **fields,
            character={'kind': 'new', 'name': 'Theme reader', 'species': 'human', 'background': ''},
            selection_digest=reviewed['selection_digest'])
        campaigns['hundred-years-war'] = saved['id']
        campaigns['ast'] = host.store.create('Synthetic AST')['id']
        selected = choices()
        world = initialize(selected, preview(selected)['review_digest'], 'synthetic-presentation')
        key = uuid.uuid4().hex
        host.store.write({'id': key, 'name': 'Synthetic Rise', 'revision': 0, 'state': world.s})
        campaigns['rise'] = key
        host.http('/api/ai/proposal', host.proposal(intention='PRIVATE_BROWSER_INTENTION'))
        details['campaigns'] = campaigns
        details['save_folder'] = str(host.store.folder)
    if len(sys.argv) == 3 and sys.argv[2] == 'shared':
        from settlement_setup import initialize, preview
        from test_settlement import choices
        import uuid
        selected = choices()
        selected['permission'] = 'held'
        world = initialize(selected, preview(selected)['review_digest'], 'synthetic-shared-browser')
        key = uuid.uuid4().hex
        host.store.write({'id': key, 'name': 'Shared settlement fixture', 'revision': 0, 'state': world.s})
        details['contexts'] = [
            {'name': 'authored_scene', 'id': host.key, 'actor': 'pc',
             'save': str(host.store.path(host.key)), 'revision': 1,
             'actions': ['look-quay', 'try-gate', 'enter-passage', 'reach-desk'], 'elapsed': 43},
            {'name': 'settlement', 'id': key, 'actor': 'founder',
             'save': str(host.store.path(key)), 'revision': 0,
             'actions': ['walk_clearing', 'found', 'build', 'wait_hour', 'wait_hour'], 'elapsed': 3900}]
    if len(sys.argv) == 3 and sys.argv[2] == 'processes':
        from test_process_bridge import install_process
        from settlement_setup import initialize, preview
        from settlement_runtime import execute as act
        from test_settlement import choices
        import uuid
        install_process(host.store, host.key, 'pc', 'observation', 'look-quay')
        selected = choices(); selected['permission'] = 'held'
        world = initialize(selected, preview(selected)['review_digest'], 'synthetic-process-browser')
        act(world, 'setup-walk', 'founder', 'walk_clearing', 'explicit synthetic setup')
        act(world, 'setup-found', 'founder', 'found', 'explicit synthetic setup')
        key = uuid.uuid4().hex
        host.store.write({'id': key, 'name': 'Continuing work fixture', 'revision': 1, 'state': world.s})
        install_process(host.store, key, 'founder', 'work', 'build')
        details['contexts'] = [
            {'name': 'observation', 'id': host.key, 'actor': 'pc', 'save': str(host.store.path(host.key)),
             'revision': 1, 'commands': [['pause', None], ['resume', None], ['advance', 1], ['advance', 99]], 'elapsed': 3},
            {'name': 'work', 'id': key, 'actor': 'founder', 'save': str(host.store.path(key)),
             'revision': 1, 'commands': [['pause', None], ['resume', None], ['advance', 100], ['advance', 3600], ['advance', 3600]], 'elapsed': 3900}]
    metadata.write_text(json.dumps(details), encoding='utf-8')
    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        pass
    finally:
        host.doCleanups()
