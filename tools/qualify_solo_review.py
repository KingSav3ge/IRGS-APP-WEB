"""Qualify App HTTP/recovery against an exact Catalog synthetic fixture snapshot.

This never connects a provider. Only evaluator code reads the private oracle;
the host receives reviewed setup choices and explicit structured player actions.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import threading
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'IRGS_Web'))
from server import Store, make_server
from engine_paths import ENGINE_ROOT
from rise_campaigns import create
from settlement_setup import preview
from settlement_runtime import location
from historical_archive import file_hash


def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT / 'Catalog'), *args])


def qualify(commit):
    if not __debug__ or re.fullmatch(r'[0-9a-f]{40}', commit) is None:
        raise ValueError('Use Python validation and an exact 40-character Catalog commit SHA.')
    if git('cat-file', '-t', commit).strip() != b'commit':
        raise ValueError('Catalog snapshot is not a commit')
    with tempfile.TemporaryDirectory(prefix='irgs-solo-qualification-') as folder:
        root = Path(folder)
        prefix = 'IRGS_Catalog/evaluation/solo_r00_v1/'
        module_name = 'IRGS_Catalog/solo_evaluation.py'
        files = git('ls-tree', '-r', '--name-only', commit, '--', prefix, module_name).decode().splitlines()
        for name in files:
            if (not name.startswith(prefix) and name != module_name) or '..' in Path(name).parts:
                raise ValueError('Unexpected fixture source path')
            target = root / 'fixture' / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(git('show', commit + ':' + name))
        module_path = root / 'fixture' / module_name
        spec = importlib.util.spec_from_file_location('qualified_catalog_solo', module_path)
        evaluation = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(evaluation)
        evaluation.validate_fixture()
        evaluator = evaluation.load_evaluator_data()
        oracle = evaluator['oracle']
        excluded = [*oracle['hidden_markers'], 'oren-home', 'oren-repair', 'opening_npc_inventory']
        store = Store(root / 'saves')
        choices = evaluator['setup']['choices']
        review = preview(choices)
        campaign = create(store, {'name': 'Synthetic Catalog Solo qualification', 'choices': choices,
            'review_digest': review['review_digest'], 'request_id': 'solo-qualification-create'})['id']
        server, thread, token, base = None, None, None, None

        def call(path, body=None):
            request = Request(base + '/api/' + path,
                data=None if body is None else json.dumps(body).encode(),
                headers={'X-IRGS-Token': token or '', 'Content-Type': 'application/json'})
            with urlopen(request, timeout=10) as response:
                return json.load(response)

        def start():
            nonlocal server, thread, token, base
            server = make_server(0, store.folder)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            base = f'http://127.0.0.1:{server.server_port}'
            token = call('campaigns')['token']

        def stop():
            server.shutdown()
            server.server_close()
            thread.join()

        def check_no_oracle(value):
            assert all(marker not in json.dumps(value) for marker in excluded)

        results, accepted, rejected = {}, 0, 0
        start()
        try:
            for case in oracle['cases']:
                actor_input = evaluation.export_actor_input(case['case_id'])
                view = call('playthrough/' + campaign + '?actor_id=founder')
                check_no_oracle(actor_input)
                check_no_oracle(view)
                context = actor_input['context']
                assert context['revision'] == view['revision']
                assert context['location'] == view['settlement']['location']
                assert context['elapsed_seconds'] == view['settlement']['elapsed_seconds']
                body = {'id': campaign, 'actor': 'founder', 'request_id': case['request_id'],
                        'revision': case['request_revision'], 'action': case['action_id']}
                check_no_oracle(body)
                before = store.path(campaign).read_bytes()
                try:
                    result = call('rise/action', body)
                except HTTPError as error:
                    assert error.code == 400 and case['kind'] in ('denied', 'unsupported', 'stale', 'changed_replay')
                    assert store.path(campaign).read_bytes() == before
                    rejected += 1
                else:
                    assert case['kind'] in ('legitimate', 'replay')
                    check_no_oracle(result)
                    if case['kind'] == 'replay':
                        assert result == results[case['replay_of']]
                        assert store.path(campaign).read_bytes() == before
                    else:
                        results[case['case_id']] = result
                        accepted += 1
                        # Lose the acknowledgement, restart the host, then look up
                        # the saved result without submitting a fresh action.
                        stop()
                        start()
                        recovered = call(f'action-result/{campaign}/{case["request_id"]}?actor_id=founder')
                        assert recovered == result
                        saved = store.path(campaign).read_bytes()
                        with ThreadPoolExecutor(max_workers=2) as pool:
                            repeated = list(pool.map(lambda _: call('rise/action', body), range(2)))
                        assert repeated == [result, result]
                        assert store.path(campaign).read_bytes() == saved
                record = store.read(campaign)
                state, expected = record['state'], case['expected']
                assert record['revision'] == expected['revision']
                assert state['clock'] == expected['clock']
                assert state['elapsed_time']['seconds'] == expected['elapsed_seconds']
                assert location(state, 'founder') == expected['location']
                assert ('camp' in state['settlements']) == expected['camp_established']
                assert state['stocks']['founder-home']['timber'] == expected['founder_timber']
                assert state['stocks']['oren-home']['timber'] == expected['npc_timber']
                for material, quantity in state['opening_stock'].items():
                    remaining = sum(account.get(material, 0) for account in state['stocks'].values())
                    used = sum(flow['quantity'] for flow in state['material_flows'].values()
                               if flow['material'] == material and flow['kind'] == 'consumption')
                    assert remaining + used == quantity
            record = store.read(campaign)
            assert len(record['gameplay_requests']) == accepted == 5
            saved = store.path(campaign).read_bytes()
            call('delete', {'id': campaign, 'revision': record['revision']})
            call('restore', {'id': campaign, 'revision': record['revision']})
            assert store.path(campaign).read_bytes() == saved
            status = call('ai/status')
            assert not status['available'] and 'diagnostics' not in status
            return {'status': 'passed', 'fixture_id': evaluation.FIXTURE_ID,
                'fixture_catalog_commit': commit,
                'fixture_manifest_sha256': file_hash(module_path.parent / 'evaluation/solo_r00_v1/manifest.json'),
                'runtime_engine_commit': subprocess.check_output(['git', '-C', str(ENGINE_ROOT.parent), 'rev-parse', 'HEAD'], text=True).strip(),
                'runtime_catalog_commit': git('rev-parse', 'HEAD').decode().strip(),
                'cases': len(oracle['cases']), 'accepted_Core_actions': accepted,
                'atomic_rejections': rejected, 'host_restarts': accepted,
                'concurrent_retries_per_accepted_action': 2,
                'lost_acknowledgements_recovered': accepted,
                'Trash_restore_preserves_exact_save_bytes': True,
                'oracle_absent_from_actor_inputs_HTTP_requests_and_player_views': True,
                'provider_calls': 0, 'provider_action_contract_qualified': False}
        finally:
            stop()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--catalog-commit', required=True)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = qualify(args.catalog_commit)
    payload = json.dumps(result, indent=2) + '\n'
    if args.output:
        args.output.write_text(payload, encoding='utf-8')
    print(payload, end='')
