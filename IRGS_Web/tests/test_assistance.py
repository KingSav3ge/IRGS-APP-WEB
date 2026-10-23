"""Unavailable assistance leaves real supported actions and player drafts alone."""
import json
import os
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from server import Store, make_server


class AssistanceStatusTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.store = Store(self.tmp.name)
        self.record = self.store.create('Synthetic player')
        self.server = make_server(0, self.tmp.name)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.stop_server)
        self.url = f'http://127.0.0.1:{self.server.server_port}'
        self.token = self.get('/api/campaigns')['token']

    def stop_server(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()

    def get(self, path, *, token=True, origin=None):
        headers = {'X-IRGS-Token': self.token} if token and hasattr(self, 'token') else {}
        if origin:
            headers['Origin'] = origin
        with urlopen(Request(self.url + path, headers=headers), timeout=10) as response:
            return json.load(response)

    def test_public_and_developer_status_require_session_and_origin(self):
        for path in ('/api/ai/status', '/api/ai/status?mode=creator'):
            for token, origin in ((False, None), (True, 'https://example.invalid')):
                with self.assertRaises(HTTPError) as caught:
                    self.get(path, token=token, origin=origin)
                self.assertEqual(caught.exception.code, 403)

    def test_player_status_contains_no_diagnostics_or_credentials(self):
        before = self.store.path(self.record['id']).read_bytes()
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'SYNTHETIC_KEY_DO_NOT_EXPOSE'}):
            public = self.get('/api/ai/status')
            developer = self.get('/api/ai/status?mode=creator')
        self.assertEqual(public['status'], 'unavailable')
        self.assertFalse(public['available'])
        self.assertFalse(public['campaign_effects'])
        self.assertNotIn('diagnostics', public)
        self.assertEqual(developer['diagnostics']['provider_runtime'], 'not_connected')
        self.assertFalse(developer['diagnostics']['dispatch_enabled'])
        self.assertNotIn('SYNTHETIC_KEY_DO_NOT_EXPOSE', json.dumps(developer))
        self.assertNotIn('OPENAI_API_KEY', json.dumps(developer))
        self.assertEqual(before, self.store.path(self.record['id']).read_bytes())

    def test_playthrough_has_safe_availability_without_rewriting_current_capabilities(self):
        view = self.get('/api/playthrough/' + self.record['id'])
        self.assertTrue(view['capabilities']['can_declare'])
        self.assertFalse(view['assistance']['available'])
        self.assertNotIn('diagnostics', view['assistance'])
        self.assertNotIn('state', view)

    def test_current_script_is_served_for_the_browser(self):
        with urlopen(self.url + '/solo.js', timeout=10) as response:
            self.assertEqual(response.status, 200)
            self.assertIn('text/javascript', response.headers['Content-Type'])
            self.assertIn(b'confirmReviewedAction', response.read())
