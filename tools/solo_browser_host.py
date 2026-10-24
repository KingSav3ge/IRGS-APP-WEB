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
    if not SOLO_API or len(sys.argv) != 2:
        raise SystemExit('Select the exact Solo Engine using IRGS_ENGINE_ROOT and supply a temporary metadata path')
    metadata = Path(sys.argv[1])
    host = SoloBridgeTests()
    host.setUp()
    host.stop()
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

    host.config = replace(host.config, transport=offline, deadline_seconds=5)
    host.start()
    metadata.write_text(json.dumps({'port': host.server.server_port, 'save': str(host.store.path(host.key)),
                                    'id': host.key}), encoding='utf-8')
    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        pass
    finally:
        host.doCleanups()
