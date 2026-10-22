"""Qualify the complete Catalog archive through Creator HTTP, using temporary saves/cache."""
import argparse
import json
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request,urlopen
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'IRGS_Web'))
from server import make_server, Store
from engine_paths import ENGINE_ROOT
from catalog_paths import CATALOG_ROOT
from historical_archive import COLLECTIONS,file_hash


def source_commit(root):
    return subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD'], text=True).strip()


def qualify():
    if not __debug__:
        raise RuntimeError('Qualification requires Python validation; do not use -O.')
    manifest=CATALOG_ROOT/'historical_details/manifest.json'
    document=json.loads(manifest.read_text())
    release=json.loads((CATALOG_ROOT/'release.json').read_text())
    assert file_hash(manifest)==release['files_sha256']['historical_details/manifest.json']
    assert document['archive']['bytes']==533064680
    assert document['archive']['sha256']=='51246eb6898a228f42f0794ed19ce69af275a2a4661c0fb6a1d3baebe3efc773'
    assert len(document['parts'])==32
    def source_stamp(path):
        info=path.stat()
        return info.st_ino,info.st_size,info.st_mtime_ns,info.st_ctime_ns
    inputs={p['path']:source_stamp(manifest.parent/p['path']) for p in document['parts']}
    with tempfile.TemporaryDirectory(prefix='irgs-app-real-') as folder:
        root=Path(folder);saves=root/'saves';cache=root/'cache';config=root/'unattached.json'
        server=make_server(0,saves,reference_config=config,reference_cache=cache)
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        base=f'http://127.0.0.1:{server.server_port}'
        token=None
        def get(path,creator=True,session=True):
            if creator:path+=('&' if '?' in path else '?')+'mode=creator'
            headers={'X-IRGS-Token':token} if session and token else {}
            with urlopen(Request(base+path,headers=headers),timeout=120) as response:return json.load(response)
        try:
            token=get('/api/campaigns',creator=False)['token']
            for path in ('/api/historical-reference','/api/historical-reference/search','/api/historical-reference/record?collection=figures&row=1'):
                for creator,session in ((False,True),(True,False)):
                    try:get(path,creator,session)
                    except HTTPError as error:assert error.code==403
                    else:raise AssertionError('Creator boundary bypassed')
            assert not cache.exists()
            started=time.monotonic();status=get('/api/historical-reference')
            assert status['status']=='attached_read_only',status
            assert status['source_kind']=='catalog_multipart'
            assert status['sha256']==document['archive']['sha256']
            assert {c['id'] for c in status['collections']}==set(COLLECTIONS)
            reconstructed=cache/document['archive']['sha256']/'archive.zip'
            assert reconstructed.stat().st_size==document['archive']['bytes']
            assert file_hash(reconstructed)==document['archive']['sha256']
            initial_cache_stamp=reconstructed.stat().st_mtime_ns
            first_rows={}
            for collection in COLLECTIONS:
                page=get('/api/historical-reference/search?'+urlencode({'collection':collection,'limit':1}))
                assert len(page['results'])==1,collection
                row=page['results'][0]
                record=get('/api/historical-reference/record?'+urlencode({'collection':collection,'row':row['row']}))
                assert record['reference']['archive_sha256']==document['archive']['sha256']
                assert record['reference']['collection']==collection
                assert not record['campaign_effects'] and not record['adoption_performed']
                first_rows[collection]={'row':row['row'],'source_id':row['source_id'],'citations':len(record['sources'])}
            record=Store(saves).create('Synthetic neighboring campaign',profile_id='ast')
            path='/api/playthrough/'+record['id'];before=get(path,creator=False)
            discovery=get('/api/content-library',creator=False)
            saved={p.name:p.read_bytes() for p in saves.iterdir()}
            get('/api/historical-reference');get('/api/historical-reference/search?collection=figures&q=Henry')
            assert get(path,creator=False)==before
            assert get('/api/content-library',creator=False)==discovery
            assert saved=={p.name:p.read_bytes() for p in saves.iterdir()}
            assert reconstructed.stat().st_mtime_ns==initial_cache_stamp
            assert all(source_stamp(manifest.parent/name)==stamp for name,stamp in inputs.items())
            result={'status':'passed', 'engine_commit': source_commit(ENGINE_ROOT.parent),
                    'catalog_commit': source_commit(CATALOG_ROOT.parent),'archive_bytes':document['archive']['bytes'],'archive_sha256':status['sha256'],
                    'app_release_sha256':file_hash(ROOT / 'IRGS_Web/release.json'),
                    'qualifier_sha256':file_hash(Path(__file__)),
                    'manifest_sha256':status['manifest_sha256'],'parts':len(document['parts']),
                    'collections':first_rows,'elapsed_seconds':round(time.monotonic()-started,2),
                    'creator_boundary_denials':6,'campaign_save_bytes_unchanged':True,'source_parts_unchanged':True,
                    'cache_reused':True,'no_reference_POSTs':True,
                    'scope':'Actual complete reconstruction and ten collection search/detail probes; synthetic neighboring campaign only.'}
            return result
        finally:
            server.shutdown();server.server_close();thread.join()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='Optional local JSON evidence path, outside committed source.')
    args = parser.parse_args()
    result = qualify()
    payload = json.dumps(result, indent=2) + '\n'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding='utf-8')
    print(payload, end='')
