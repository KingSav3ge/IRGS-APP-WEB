"""Find separately maintained campaign data in joined or pinned source."""
import json
import os
from pathlib import Path
import subprocess
import sys

APP_ROOT = Path(__file__).resolve().parent


def catalog_root():
    configured = os.environ.get('IRGS_CATALOG_ROOT')
    candidates = [Path(configured)] if configured else [
        APP_ROOT.parent / 'IRGS_Catalog',
        APP_ROOT.parent / 'Catalog' / 'IRGS_Catalog']
    for path in candidates:
        path = path.expanduser().resolve()
        if (path / 'data/campaign_portfolio.json').is_file() and (path / 'release.json').is_file():
            return path
    raise RuntimeError('IRGS Catalog is unavailable. Run git submodule update --init --recursive '
        'in the app repository, or set IRGS_CATALOG_ROOT to an IRGS_Catalog directory.')


CATALOG_ROOT = catalog_root()


def verify_catalog():
    return json.loads(subprocess.check_output(
        [sys.executable, '-B', str(CATALOG_ROOT / 'verify_catalog.py')], text=True))
