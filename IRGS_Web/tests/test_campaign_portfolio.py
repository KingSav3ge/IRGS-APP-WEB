"""Catalogue completeness and the boundary between previews and saved worlds."""
import hashlib
import json
import sys
import tempfile
import threading
import unittest
from collections import Counter
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from campaign_portfolio import PORTFOLIO_PATH, campaign_portfolio
from catalog_paths import CATALOG_ROOT
from server import Store, make_server
from features import content_library

ROOT = Path(__file__).resolve().parents[2]


class CampaignPortfolioTests(unittest.TestCase):
    def test_complete_slate_preserves_source_and_proposal_boundaries(self):
        portfolio = content_library()['portfolio']
        self.assertEqual(portfolio['counts'], {'total': 44, 'launch': 31, 'future': 12,
            'systems': 1, 'free_launch_stories': 18, 'available_slices': 2})
        entries = portfolio['entries']
        self.assertEqual(len({e['catalogue_id'] for e in entries}), 44)
        self.assertEqual(Counter(e['campaign_type'] for e in entries),
            {'short_story': 18, 'curated': 9, 'full': 6, 'major': 6, 'grand': 4, 'simulation_system': 1})
        self.assertEqual(Counter(e['campaign_type'] for e in entries if e['slate'] == 'launch'),
            {'short_story': 18, 'curated': 6, 'full': 4, 'major': 2, 'grand': 1})
        self.assertEqual(hashlib.sha256((CATALOG_ROOT.parent / portfolio['source']['path']).read_bytes()).hexdigest(),
            portfolio['source']['sha256'])
        self.assertEqual([e['catalogue_id'] for e in entries if e['available_slice']], ['MC-01', 'CSS-01'])
        for e in entries:
            for key in ('tagline', 'setting', 'geography', 'period', 'genres', 'synopsis', 'perspectives',
                        'core_experiences', 'featured_systems', 'scope', 'content_dependencies', 'provenance'):
                self.assertTrue(e[key], (e['catalogue_id'], key))
            self.assertFalse(e['availability']['release_approved'])
            self.assertFalse(e['availability']['entitlement_active'])
            self.assertFalse(e['readiness']['full_campaign_ready'])
        self.assertNotIn('The Age of Realms', [e['title'] for e in entries])
        self.assertEqual(next(e for e in entries if e['catalogue_id'] == 'MC-01')['campaign_type'], 'major')
        rise = next(e for e in entries if e['catalogue_id'] == 'CSS-01')
        self.assertEqual(rise['current_display_title'], 'The Rise of... You')
        self.assertEqual(rise['campaign_type'], 'simulation_system')

    def projected_fixture(self, mutate, campaigns):
        data = json.loads(PORTFOLIO_PATH.read_text())
        mutate(data)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'portfolio.json'
            path.write_text(json.dumps(data))
            with patch('campaign_portfolio.PORTFOLIO_PATH', path):
                return campaign_portfolio(campaigns)

    def test_concept_metadata_cannot_create_or_borrow_a_launch_capability(self):
        def forge(data):
            data['entries'][0].update(available_slice=True, current_campaign_id='rise', playable=True,
                launch_capability='reviewed_initialization', development_status='in_development')
        actual = content_library()['campaigns']
        result = self.projected_fixture(forge, actual)['entries'][0]
        self.assertFalse(result['available_slice'])
        self.assertIsNone(result['current_campaign_id'])
        unavailable = self.projected_fixture(forge, [])
        self.assertEqual(unavailable['counts']['available_slices'], 0)
        with self.assertRaises(ValueError):
            self.projected_fixture(lambda d: d['entries'][0]['availability'].update(release_approved=True), actual)

    def test_internal_drafts_are_filtered_before_projection_and_counts(self):
        def internal(data):
            data['entries'][0].update(development_status='concept_draft', title='INTERNAL_DRAFT_SENTINEL')
            data['entries'][0]['availability']['preview'] = True
        result = self.projected_fixture(internal, [])
        self.assertEqual(result['counts']['total'], 43)
        self.assertEqual(result['counts']['launch'], 30)
        self.assertNotIn('INTERNAL_DRAFT_SENTINEL', json.dumps(result))

    def test_a_reference_status_or_missing_initializer_never_becomes_playable(self):
        campaigns = content_library()['campaigns']
        for c in campaigns:
            for p in c.get('periods', []):
                for e in p['entries']:
                    e['ready'] = False
            for t in c.get('templates', []):
                t['ready'] = False
        result = campaign_portfolio(campaigns)
        self.assertEqual(result['counts']['available_slices'], 0)
        self.assertFalse(next(e for e in result['entries'] if e['catalogue_id'] == 'GC-01')['available_slice'])

    def test_http_previews_preserve_an_existing_world_and_forged_concepts_cannot_start(self):
        with tempfile.TemporaryDirectory() as folder:
            store = Store(folder)
            server = make_server(0, folder)
            worker = threading.Thread(target=server.serve_forever, daemon=True)
            worker.start()
            token = None

            def call(path, data=None, *, authenticated=True):
                headers = {'Content-Type': 'application/json'}
                if authenticated and token:
                    headers['X-IRGS-Token'] = token
                request = Request(f'http://127.0.0.1:{server.server_port}' + path,
                    data=None if data is None else json.dumps(data).encode(), headers=headers)
                with urlopen(request, timeout=15) as response:
                    return json.load(response)
            try:
                token = call('/api/campaigns')['token']
                entry = call('/api/historical-entry/hyw-1415')
                fields = {'profile_id': 'military', 'scenario_id': 'hundred-years-war',
                    'entry_id': 'hyw-1415', 'snapshot_sha256': entry['snapshot_sha256']}
                options = call('/api/starting-options?' + urlencode(fields))
                created = call('/api/create', {**fields, 'name': 'Catalogue continuity fixture',
                    'request_id': 'catalogue-continuity', 'selection_digest': options['selection_digest'],
                    'starting_scenario_id': 'individual',
                    'character': {'kind': 'new', 'name': 'Synthetic reader', 'species': 'human'}})
                before = store.path(created['id']).read_bytes()
                for _ in range(2):
                    listing = call('/api/content-library')
                    self.assertEqual(listing['portfolio']['counts']['total'], 44)
                    self.assertEqual([c['id'] for c in listing['campaigns']],
                        ['hundred-years-war', 'world-of-kira', 'rise'])
                for concept in ('SS-01', 'CC-P01', 'GC-01', 'CSS-01'):
                    with self.subTest(concept=concept), self.assertRaises(HTTPError) as error:
                        call('/api/create', {**fields, 'scenario_id': concept,
                            'name': 'Forged concept', 'request_id': 'forged-' + concept,
                            'selection_digest': options['selection_digest'],
                            'character': {'kind': 'new', 'name': 'Synthetic reader', 'species': 'human'}})
                    self.assertEqual(error.exception.code, 403)
                self.assertEqual(store.path(created['id']).read_bytes(), before)
                self.assertEqual(len(store.listing()), 1)
                with self.assertRaises(HTTPError) as error:
                    call('/api/content-library', authenticated=False)
                self.assertEqual(error.exception.code, 403)
            finally:
                server.shutdown()
                server.server_close()
                worker.join()


if __name__ == '__main__':
    unittest.main()
