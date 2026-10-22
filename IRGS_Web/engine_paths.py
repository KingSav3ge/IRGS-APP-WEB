"""Locate the shared Engine in a joined checkout or the app's pinned dependency."""
import os
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parent


def engine_root():
    configured = os.environ.get('IRGS_ENGINE_ROOT')
    candidates = [Path(configured)] if configured else [
        APP_ROOT.parent / 'IRGS_3_3', APP_ROOT.parent / 'Engine' / 'IRGS_3_3']
    for path in candidates:
        path = path.expanduser().resolve()
        if (path / 'runtime/core_world.py').is_file() and (path / 'release.json').is_file():
            return path
    raise RuntimeError('IRGS Engine is unavailable. Run git submodule update --init --recursive '
        'in the app repository, or set IRGS_ENGINE_ROOT to an Engine IRGS_3_3 directory.')


ENGINE_ROOT = engine_root()
