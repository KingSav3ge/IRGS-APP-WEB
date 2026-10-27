"""Public, non-secret fingerprint of the components selected by this host."""
import hashlib
import json
import re
from pathlib import Path

from catalog_paths import CATALOG_ROOT
from engine_paths import ENGINE_ROOT


def fingerprint(path):
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return None


def running_build():
    app = Path(__file__).resolve().parent
    try:
        version = json.loads((app.parent / 'VERSION.json').read_text(encoding='utf-8'))['version']
        if not isinstance(version, str) or not re.fullmatch(r'\d+\.\d+\.\d+', version):
            version = None
    except (OSError, ValueError, KeyError, TypeError):
        version = None
    return {'schema_version': 1, 'edition': version, 'classification': 'pre_alpha' if version and version.startswith('3.') else 'unclassified',
            'app_manifest_sha256': fingerprint(app / 'release.json'),
            'host_source_sha256': fingerprint(app / 'server.py'),
            'engine_manifest_sha256': fingerprint(ENGINE_ROOT / 'release.json'),
            'engine_core_sha256': fingerprint(ENGINE_ROOT / 'runtime' / 'core_world.py'),
            'catalog_manifest_sha256': fingerprint(CATALOG_ROOT / 'release.json'),
            'catalog_portfolio_sha256': fingerprint(CATALOG_ROOT / 'data' / 'campaign_portfolio.json')}
