"""Attach an existing local Grand Archive ZIP without copying it into IRGS."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from engine_paths import ENGINE_ROOT
sys.path.insert(0, str(ENGINE_ROOT / 'runtime'))
from historical_archive import HistoricalArchive, file_hash


def register(archive, destination):
    path = Path(archive).resolve(strict=True)
    if not path.is_file() or path.suffix.lower() != '.zip':
        raise ValueError('Select an existing Historical Grand Archive ZIP')
    sha256 = file_hash(path)
    library = HistoricalArchive(path, sha256)
    status = library.verify_collections()
    config = Path(destination)
    config.parent.mkdir(parents=True, exist_ok=True)
    temporary = config.with_suffix('.tmp')
    temporary.write_text(json.dumps({'schema_version': 1, 'historical_archive':
                         {'path': str(path), 'sha256': sha256}}, indent=2) + '\n', encoding='utf-8')
    temporary.replace(config)
    return status


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive')
    parser.add_argument('--config', type=Path, default=ROOT / 'cache/reference_sources.json')
    args = parser.parse_args()
    print(json.dumps(register(args.archive, args.config), ensure_ascii=True))
