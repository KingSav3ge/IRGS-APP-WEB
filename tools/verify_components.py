"""Verify independent Engine/App/Catalog pins and an App's checked-out dependencies."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent


def run(command):
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError((result.stdout + result.stderr)[-4000:])
    return result.stdout


def verify(component):
    if component == 'catalog':
        return json.loads(run([sys.executable, '-B', str(ROOT / 'IRGS_Catalog/verify_catalog.py')]))
    if component == 'engine':
        core = ROOT / 'IRGS_3_3'
    else:
        sys.path.insert(0, str(ROOT / 'IRGS_Web'))
        from engine_paths import ENGINE_ROOT
        core = ENGINE_ROOT
    checks = {'engine': json.loads(run([sys.executable, '-B', str(core / 'runtime/irgs.py'), 'verify']))}
    if component == 'app':
        checks['app'] = json.loads(run([sys.executable, '-B', str(ROOT / 'IRGS_Web/app_integrity.py')]))
        from catalog_paths import CATALOG_ROOT, verify_catalog
        checks['catalog'] = verify_catalog()
        if (ROOT / '.gitmodules').exists():
            expected_catalog = run(['git', 'rev-parse', 'HEAD:Catalog']).strip()
            actual_catalog = run(['git', '-C', str(ROOT / 'Catalog'), 'rev-parse', 'HEAD']).strip()
            if expected_catalog != actual_catalog:
                raise RuntimeError('Catalog checkout differs from the App commit pin')
            checks['catalog_commit'] = actual_catalog
            expected = run(['git', 'rev-parse', 'HEAD:Engine']).strip()
            actual = run(['git', '-C', str(ROOT / 'Engine'), 'rev-parse', 'HEAD']).strip()
            if expected != actual:
                raise RuntimeError('Engine checkout differs from the App commit pin; qualify and commit the dependency update')
            checks['engine_commit'] = actual
    return {'status': 'verified', 'component': component, 'checks': checks, 'behavioral_tests_executed': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--component', choices=('engine', 'app', 'catalog'), required=True)
    print(json.dumps(verify(parser.parse_args().component)))
