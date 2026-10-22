"""Refresh explicit Engine/App/Catalog integrity pins after intentional source edits."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXCLUDED = {'__pycache__', 'saves', 'trash', 'live', '.git', '.pytest_cache', 'tmp', 'temp'}


def source_files(root):
    return (p for p in root.rglob('*') if p.is_file()
        and not set(p.relative_to(root).parts).intersection(EXCLUDED)
        and not any(part.startswith('tmp') for part in p.relative_to(root).parts)
        and p.suffix not in ('.pyc', '.log', '.tmp', '.bak'))


def refresh(component):
    if component == 'engine':
        base = ROOT / 'IRGS_3_3'
        release = json.loads((base / 'release.json').read_text())
        paths = {base / name for name in release['files_sha256'] if (base / name).is_file()}
        for directory in ('runtime', 'catalog', 'Core', 'data'):
            paths.update(source_files(base / directory))
        release.pop('host_sha256', None)
        release['component'] = 'IRGS-Engine'
    elif component == 'catalog':
        base = ROOT / 'IRGS_Catalog'
        release = {'schema_version': 1, 'component': 'IRGS-Catalog',
            'scope': 'Campaign discovery and design source; no runtime or release authorization.'}
        paths = set(source_files(base)) - {base / 'release.json'}
    else:
        base = ROOT / 'IRGS_Web'
        release = {'schema_version': 1, 'component': 'IRGS-APP-WEB', 'selected_core': '3.3',
            'engine_dependency': 'Pinned Engine submodule in the standalone app; sibling IRGS_3_3 in joined IRGS.'}
        paths = set(source_files(base)) - {base / 'release.json'}
    release['files_sha256'] = {p.relative_to(base).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(paths)}
    (base / 'release.json').write_text(json.dumps(release, indent=2, ensure_ascii=False) + '\n')
    return {'component': component, 'files': len(paths)}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--component', choices=('engine', 'app', 'catalog', 'both', 'all'), default='both')
    args = parser.parse_args()
    print(json.dumps([refresh(c) for c in ('engine', 'app', 'catalog') if args.component == c or args.component == 'all' or (args.component == 'both' and c != 'catalog')]))
