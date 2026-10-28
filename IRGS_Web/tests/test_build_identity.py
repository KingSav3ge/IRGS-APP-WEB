"""Running host identity uses selected component files, never configuration."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch
from urllib.request import urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from build_identity import running_build
from catalog_paths import CATALOG_ROOT
from engine_paths import ENGINE_ROOT
from server import make_server


class BuildIdentityTests(unittest.TestCase):
    def test_selected_files_and_missing_edition_are_reported_without_private_paths(self):
        identity = running_build()
        edition = json.loads((Path(__file__).resolve().parents[2] / 'VERSION.json').read_text())['version']
        self.assertEqual(identity['edition'], edition)
        self.assertEqual(identity['classification'], 'pre_alpha' if edition.startswith('3.') else 'unclassified')
        for field, path in [('engine_manifest_sha256', ENGINE_ROOT / 'release.json'),
                            ('catalog_manifest_sha256', CATALOG_ROOT / 'release.json')]:
            self.assertEqual(identity[field], hashlib.sha256(path.read_bytes()).hexdigest())
        self.assertNotIn(str(ENGINE_ROOT), json.dumps(identity))
        self.assertNotIn(str(CATALOG_ROOT), json.dumps(identity))
        with patch('build_identity.json.loads', side_effect=ValueError):
            self.assertIsNone(running_build()['edition'])
        with patch('build_identity.json.loads', return_value={'version': '3.4.4'}):
            future = running_build()
            self.assertEqual(future['edition'], '3.4.4')
            self.assertEqual(future['classification'], 'pre_alpha')
        with patch('build_identity.json.loads', return_value={'version': 'not-a-version'}):
            self.assertIsNone(running_build()['edition'])

    def test_running_host_identity_is_stable_until_restart_and_never_exposes_configuration(self):
        with tempfile.TemporaryDirectory() as folder, patch.dict('os.environ', {'IRGS_TEST_SECRET': 'PRIVATE_SYNTHETIC_SECRET'}):
            servers = []
            def start(build):
                with patch('build_identity.running_build', return_value=build):
                    server = make_server(0, Path(folder) / 'saves')
                thread = threading.Thread(target=server.serve_forever, daemon=True)
                thread.start(); servers.append((server, thread))
                return 'http://127.0.0.1:' + str(server.server_port) + '/api/campaigns'
            try:
                first = {'schema_version': 1, 'edition': '3.4.3', 'app_manifest_sha256': 'a'*64}
                url = start(first)
                with urlopen(url, timeout=5) as response: data = json.load(response)
                self.assertEqual(data['build'], first)
                self.assertNotIn('PRIVATE_SYNTHETIC_SECRET', json.dumps(data))
                with patch('build_identity.running_build', return_value={'edition': 'changed'}):
                    with urlopen(url, timeout=5) as response: self.assertEqual(json.load(response)['build'], first)
                second = {'schema_version': 1, 'edition': '3.4.3', 'app_manifest_sha256': 'b'*64}
                with urlopen(start(second), timeout=5) as response: self.assertEqual(json.load(response)['build'], second)
            finally:
                for server, thread in servers:
                    server.shutdown(); server.server_close(); thread.join()
