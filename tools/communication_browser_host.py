"""Canonical host for an explicitly selected temporary communication fixture."""
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'IRGS_Web'),str(ROOT/'IRGS_Web/tests')]
from server import Store,make_server
from app_communication_fixtures import install

if __name__=='__main__':
    folder=Path(sys.argv[1]).resolve()
    if not folder.is_dir() or any(folder.iterdir()):
        raise SystemExit('Supply an empty temporary fixture directory')
    store=Store(folder/'saves')
    contexts=install(store)
    server=make_server(0,store.folder)
    (folder/'host.json').write_text(json.dumps({'port':server.server_port,'contexts':contexts}))
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()
