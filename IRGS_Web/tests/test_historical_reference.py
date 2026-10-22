"""Creator-only HTTP reference browsing cannot write a campaign."""
import json
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from server import make_server
from features import feature_registry, content_library
from historical_archive import HistoricalArchive, file_hash
from test_historical_archive import fixture_archive
from unittest.mock import patch


class HistoricalReferenceHTTPTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.source = fixture_archive(self.tmp.name)
        self.saves = Path(self.tmp.name) / 'saves'
        self.server = make_server(0, self.saves, reference_library=HistoricalArchive(self.source, file_hash(self.source)))
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True); self.thread.start()
        self.url = f'http://127.0.0.1:{self.server.server_port}'
        self.token = self.call('/api/campaigns')['token']

    def tearDown(self):
        self.server.shutdown(); self.server.server_close(); self.thread.join(); self.tmp.cleanup()

    def call(self, path, *, creator=False, token=True, method='GET'):
        if creator: path += ('&' if '?' in path else '?') + 'mode=creator'
        headers = {'X-IRGS-Token': self.token} if token and hasattr(self, 'token') else {}
        with urlopen(Request(self.url + path, headers=headers, method=method), timeout=10) as response:
            return json.load(response)

    def test_all_reference_routes_require_creator_and_session(self):
        for path in ('/api/historical-reference', '/api/historical-reference/search',
                     '/api/historical-reference/record?collection=figures&row=1'):
            for creator, token in ((False, True), (True, False)):
                with self.assertRaises(HTTPError) as caught: self.call(path, creator=creator, token=token)
                self.assertEqual(caught.exception.code, 403)

    def test_search_detail_and_retry_preserve_archive_and_empty_campaign_store(self):
        before = file_hash(self.source)
        self.assertEqual(self.call('/api/historical-reference', creator=True)['status'], 'attached_read_only')
        for _ in range(2):
            result = self.call('/api/historical-reference/search?collection=figures&q=Henry', creator=True)
            self.assertEqual(len(result['results']), 1)
            record = self.call('/api/historical-reference/record?collection=research&row=1', creator=True)
            self.assertFalse(record['campaign_effects']); self.assertFalse(record['adoption_performed'])
        self.assertEqual(before, file_hash(self.source)); self.assertEqual(list(self.saves.iterdir()), [])

    def test_invalid_lookup_cannot_read_arbitrary_paths_or_publish_actions(self):
        for path in ('/api/historical-reference/search?collection=../server.py',
                     '/api/historical-reference/record?collection=figures&row=0'):
            with self.assertRaises(HTTPError) as caught: self.call(path, creator=True)
            self.assertEqual(caught.exception.code, 400)
            self.assertNotIn(self.tmp.name, caught.exception.read().decode())
        with self.assertRaises(HTTPError) as caught: self.call('/api/historical-reference', creator=True, method='POST')
        self.assertEqual(caught.exception.code, 400)
        self.assertEqual(list(self.saves.iterdir()), [])

    def test_library_is_creator_reference_and_never_a_playable_campaign(self):
        creator = feature_registry('release', mode='creator')['features']
        player = feature_registry('release', mode='player')['features']
        self.assertIn('historical-reference-library', [f['id'] for f in creator])
        self.assertNotIn('historical-reference-library', [f['id'] for f in player])
        self.assertNotIn('historical-grand-archive', [c['id'] for c in content_library()['campaigns']])


class HistoricalReferenceSelectionHTTPTests(unittest.TestCase):
    call = HistoricalReferenceHTTPTests.call
    tearDown = HistoricalReferenceHTTPTests.tearDown

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.source = fixture_archive(self.tmp.name)
        self.original = self.source.read_bytes()
        self.config = Path(self.tmp.name) / 'registration.json'
        self.manifest = Path(self.tmp.name) / 'catalog/manifest.json'
        self.saves = Path(self.tmp.name) / 'saves'
        self.server = make_server(0, self.saves, reference_config=self.config,
            reference_manifest=self.manifest, reference_manifest_pin='a' * 64,
            reference_cache=Path(self.tmp.name) / 'cache')
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.url = f'http://127.0.0.1:{self.server.server_port}'
        self.token = self.call('/api/campaigns')['token']

    def attach(self):
        self.config.write_text(json.dumps({'schema_version': 1, 'historical_archive':
            {'path': str(self.source), 'sha256': file_hash(self.source)}}))

    def test_empty_installation_can_attach_and_retry_without_restart_or_save_changes(self):
        empty = self.call('/api/historical-reference', creator=True)
        self.assertEqual(empty['status'], 'not_attached')
        self.assertEqual(empty['collections'], [])
        self.attach()
        ready = self.call('/api/historical-reference', creator=True)
        self.assertEqual(ready['status'], 'attached_read_only')
        self.assertEqual(ready['source_kind'], 'local_zip')
        self.assertEqual(len(self.call('/api/historical-reference/search?collection=figures&q=Henry',
                                      creator=True)['results']), 1)
        self.assertEqual(list(self.saves.iterdir()), [])
        self.assertEqual(self.source.read_bytes(), self.original)

    def test_bad_local_registration_is_not_replaced_by_catalog_or_exposed_as_a_path(self):
        self.attach()
        self.config.write_text('{invalid private registration')
        self.manifest.parent.mkdir()
        self.manifest.write_text('{}')
        with patch('historical_reference.catalog_library') as catalog:
            result = self.call('/api/historical-reference', creator=True)
            self.assertEqual(result['status'], 'corrupt')
            catalog.assert_not_called()
        self.assertNotIn(self.tmp.name, json.dumps(result))
        self.attach()
        self.assertEqual(self.call('/api/historical-reference', creator=True)['status'], 'attached_read_only')

    def test_changed_or_missing_zip_is_unreadable_until_repaired(self):
        self.attach()
        self.call('/api/historical-reference', creator=True)
        self.source.write_bytes(self.original + b'changed')
        self.assertEqual(self.call('/api/historical-reference', creator=True)['status'], 'corrupt')
        with self.assertRaises(HTTPError) as caught:
            self.call('/api/historical-reference/search?collection=figures', creator=True)
        self.assertNotIn(self.tmp.name, caught.exception.read().decode())
        self.source.unlink()
        self.assertEqual(self.call('/api/historical-reference', creator=True)['status'], 'unavailable')
        self.source.write_bytes(self.original)
        self.assertEqual(self.call('/api/historical-reference', creator=True)['status'], 'attached_read_only')
        self.assertEqual(list(self.saves.iterdir()), [])

    def test_denied_session_and_origin_never_open_an_archive(self):
        self.attach()
        with patch('historical_reference.from_registration') as open_source:
            for creator, token in ((False, True), (True, False)):
                with self.assertRaises(HTTPError) as caught:
                    self.call('/api/historical-reference', creator=creator, token=token)
                self.assertEqual(caught.exception.code, 403)
            request = Request(self.url + '/api/historical-reference?mode=creator', headers={
                'X-IRGS-Token': self.token, 'Origin': 'https://example.invalid'})
            with self.assertRaises(HTTPError) as caught:
                urlopen(request, timeout=10)
            self.assertEqual(caught.exception.code, 403)
            open_source.assert_not_called()

    def test_engine_multipart_failure_codes_are_safe_and_retriable(self):
        # Boundary contract only: actual multipart bytes require the new Engine
        # commit. These exceptions deliberately include a private source path.
        class PartFailure(ValueError):
            def __init__(self, code):
                self.code = code
                super().__init__('/private/part')

        self.manifest.parent.mkdir()
        self.manifest.write_text('{}')
        with patch('historical_reference.catalog_library') as open_source:
            for code, expected in (('incomplete', 'incomplete'), ('corrupt', 'corrupt'),
                                   ('invalid_manifest', 'corrupt'), ('unavailable', 'unavailable')):
                open_source.side_effect = PartFailure(code)
                status = self.call('/api/historical-reference', creator=True)
                self.assertEqual(status['status'], expected)
                self.assertEqual(status['collections'], [])
                self.assertNotIn('/private', json.dumps(status))
                self.assertFalse(status['campaign_effects'])
            # The same manifest can recover on retry, without restarting or
            # bypassing the selected pin. Use the existing ZIP API as a test double.
            open_source.side_effect = None
            open_source.return_value = HistoricalArchive(self.source, file_hash(self.source))
            ready = self.call('/api/historical-reference', creator=True)
            self.assertEqual(ready['status'], 'attached_read_only')
            self.assertEqual(ready['source_kind'], 'catalog_multipart')
            self.assertEqual(open_source.call_args.args[1], 'a' * 64)
        self.assertEqual(list(self.saves.iterdir()), [])

    def test_catalog_metadata_alone_never_exposes_an_archive(self):
        self.manifest.parent.mkdir()
        self.manifest.write_text('{}')
        result = self.call('/api/historical-reference', creator=True)
        self.assertIn(result['status'], ('unavailable', 'corrupt', 'incomplete'))
        self.assertEqual(result['collections'], [])
        self.assertFalse(result['campaign_effects'])
        self.assertEqual(list(self.saves.iterdir()), [])


if __name__ == '__main__': unittest.main()
