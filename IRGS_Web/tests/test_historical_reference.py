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


if __name__ == '__main__': unittest.main()
