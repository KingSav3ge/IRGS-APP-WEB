"""Real Engine multipart reader through App HTTP; all mutable inputs are synthetic."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from server import make_server, Store
from historical_archive import COLLECTIONS, file_hash
from test_historical_archive import fixture_archive


class HistoricalMultipartHTTPTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.source = fixture_archive(self.root, complete=True)
        self.catalog = self.root / 'Catalog/IRGS_Catalog'
        self.details = self.catalog / 'historical_details'
        (self.details / 'parts').mkdir(parents=True)
        self.manifest = self.details / 'manifest.json'
        self.cache = self.root / 'cache'
        self.config = self.root / 'registration.json'
        self.saves = self.root / 'saves'
        data = self.source.read_bytes()
        parts = []
        for offset in range(0, len(data), 512):
            block = data[offset:offset + 512]
            name = f'parts/archive.{len(parts) + 1:04d}'
            (self.details / name).write_bytes(block)
            parts.append({'ordinal': len(parts) + 1, 'path': name, 'bytes': len(block),
                          'sha256': hashlib.sha256(block).hexdigest()})
        self.document = {'schema_version': 1, 'display_name': 'Historical Details',
            'status': 'complete', 'archive': {'name': self.source.name,
                'bytes': len(data), 'sha256': file_hash(self.source)},
            'part_size_bytes': 512, 'parts': parts}
        self.publish_manifest()
        self.catalog_patch = patch('historical_reference.CATALOG_ROOT', self.catalog)
        self.catalog_patch.start()
        self.addCleanup(self.catalog_patch.stop)
        self.server = make_server(0, self.saves, reference_config=self.config,
                                  reference_cache=self.cache)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.stop_server)
        self.url = f'http://127.0.0.1:{self.server.server_port}'
        self.token = self.call('/api/campaigns')['token']

    def stop_server(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()

    def publish_manifest(self):
        self.manifest.write_text(json.dumps(self.document), encoding='utf-8')
        self.pin = file_hash(self.manifest)
        (self.catalog / 'release.json').write_text(json.dumps({'files_sha256': {
            'historical_details/manifest.json': self.pin}}), encoding='utf-8')

    def call(self, path='/api/historical-reference', *, creator=True, token=True):
        if creator:
            path += ('&' if '?' in path else '?') + 'mode=creator'
        headers = {'X-IRGS-Token': self.token} if token and hasattr(self, 'token') else {}
        with urlopen(Request(self.url + path, headers=headers), timeout=10) as response:
            return json.load(response)

    def test_catalog_default_uses_release_pin_and_preserves_original_reference_identity(self):
        before = {p.relative_to(self.details): file_hash(p)
                  for p in self.details.rglob('*') if p.is_file()}
        status = self.call()
        self.assertEqual(status['status'], 'attached_read_only')
        self.assertEqual(status['source_kind'], 'catalog_multipart')
        self.assertEqual(status['manifest_sha256'], self.pin)
        self.assertEqual({row['id'] for row in status['collections']}, set(COLLECTIONS))
        self.assertIn('complete original archive', status['scope'])
        self.assertIn('not browsed', status['scope'])
        self.assertEqual((self.cache / self.document['archive']['sha256'] / 'archive.zip').read_bytes(),
                         self.source.read_bytes())
        first = self.call('/api/historical-reference/search?collection=concepts&limit=1')
        second = self.call('/api/historical-reference/search?collection=concepts&limit=1&offset=1')
        self.assertTrue(first['has_more'])
        self.assertEqual(first['results'][0]['source_id'], second['results'][0]['source_id'])
        self.assertNotEqual(first['results'][0]['row'], second['results'][0]['row'])
        literal = self.call('/api/historical-reference/search?' +
                            urlencode({'collection': 'figures', 'q': '[Henry.*]'}))
        self.assertEqual(literal['results'], [])
        record = self.call('/api/historical-reference/record?collection=research&row=1')
        self.assertEqual(record['reference']['archive_sha256'], self.document['archive']['sha256'])
        self.assertEqual(record['record']['payload']['delivery_status'], 'not_established')
        self.assertEqual(record['sources'][1]['status'], 'unresolved_source_reference')
        self.assertEqual(record['sources'][0]['rights'][0]['disposition'], 'reference_only')
        self.assertFalse(record['campaign_effects'])
        self.assertFalse(record['adoption_performed'])
        self.assertEqual(before, {p.relative_to(self.details): file_hash(p)
                                  for p in self.details.rglob('*') if p.is_file()})
        self.assertEqual(list(self.saves.iterdir()), [])

    def test_unauthorized_requests_cannot_trigger_reconstruction(self):
        for path in ('/api/historical-reference', '/api/historical-reference/search',
                     '/api/historical-reference/record?collection=figures&row=1'):
            for creator, token in ((False, True), (True, False)):
                with self.assertRaises(HTTPError) as caught:
                    self.call(path, creator=creator, token=token)
                self.assertEqual(caught.exception.code, 403)
        self.assertFalse(self.cache.exists())

    def test_missing_part_recovers_on_retry_and_cannot_hide_behind_a_ready_cache(self):
        part = self.details / self.document['parts'][0]['path']
        data = part.read_bytes()
        part.unlink()
        self.assertEqual(self.call()['status'], 'incomplete')
        self.assertFalse(self.cache.exists())
        part.write_bytes(data)
        self.assertEqual(self.call()['status'], 'attached_read_only')
        part.unlink()
        self.assertEqual(self.call()['status'], 'incomplete')
        with self.assertRaises(HTTPError) as caught:
            self.call('/api/historical-reference/search?collection=figures')
        self.assertEqual(caught.exception.code, 400)
        part.write_bytes(data)
        self.assertEqual(self.call()['status'], 'attached_read_only')
        self.assertEqual(list(self.saves.iterdir()), [])

    def test_corruption_and_changed_manifest_fail_closed_without_exposing_owner_paths(self):
        part = self.details / self.document['parts'][0]['path']
        data = part.read_bytes()
        part.write_bytes(bytes([data[0] ^ 1]) + data[1:])
        status = self.call()
        self.assertEqual(status['status'], 'corrupt')
        self.assertNotIn(str(self.root), json.dumps(status))
        self.assertFalse(self.cache.exists() and list(self.cache.iterdir()))
        part.write_bytes(data)
        self.assertEqual(self.call()['status'], 'attached_read_only')
        self.manifest.write_bytes(self.manifest.read_bytes() + b' ')
        self.assertEqual(self.call()['status'], 'corrupt')

    def test_incomplete_manifest_is_never_presented_as_the_archive(self):
        self.document['status'] = 'blocked_missing_source'
        self.publish_manifest()
        status = self.call()
        self.assertEqual(status['status'], 'incomplete')
        self.assertEqual(status['collections'], [])
        self.assertFalse(self.cache.exists())

    def test_explicit_multipart_registration_keeps_correct_storage_label(self):
        self.config.write_text(json.dumps({'schema_version': 1, 'historical_archive': {
            'type': 'catalog_parts', 'manifest_path': str(self.manifest),
            'manifest_sha256': self.pin, 'cache_dir': str(self.cache)}}))
        self.assertEqual(self.call()['source_kind'], 'catalog_multipart')

    def test_reference_reads_leave_an_existing_synthetic_playthrough_and_discovery_unchanged(self):
        record = Store(self.saves).create('Synthetic neighboring campaign', profile_id='ast')
        campaign_path = '/api/playthrough/' + record['id']
        before = self.call(campaign_path, creator=False)
        discovery = self.call('/api/content-library', creator=False)
        saved = {str(p.relative_to(self.saves)): p.read_bytes() for p in self.saves.rglob('*') if p.is_file()}
        self.call()
        self.call('/api/historical-reference/search?collection=figures&q=Henry')
        self.call('/api/historical-reference/record?collection=chronology&row=1')
        after = self.call(campaign_path, creator=False)
        # Presentation refreshes bind a new view identity; campaign facts and
        # deterministic text must remain equal without changing the save.
        self.assertNotEqual(before['local_responses']['scope'].pop('view_id'),
                            after['local_responses']['scope'].pop('view_id'))
        self.assertEqual(before, after)
        self.assertEqual(discovery, self.call('/api/content-library', creator=False))
        self.assertEqual(saved, {str(p.relative_to(self.saves)): p.read_bytes() for p in self.saves.rglob('*') if p.is_file()})


if __name__ == '__main__':
    unittest.main()
