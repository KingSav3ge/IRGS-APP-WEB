"""Verify App-owned sources independently of the Engine release pins."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def verify_app():
    release = json.loads((ROOT / 'release.json').read_text(encoding='utf-8'))
    if release.get('component') != 'IRGS-APP-WEB' or release.get('selected_core') != '3.3':
        raise RuntimeError('No selected IRGS App binding')
    for name, expected in release['files_sha256'].items():
        path = (ROOT / name).resolve()
        if not path.is_relative_to(ROOT):
            raise RuntimeError('Invalid App release path')
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise RuntimeError('App hash mismatch: ' + name)
    return {'status': 'verified', 'component': release['component'], 'files': len(release['files_sha256'])}


if __name__ == '__main__':
    print(json.dumps(verify_app()))
