"""Preview-only product records; launch authority stays with verified initializers."""
import copy
import json
import re
from collections import Counter
from pathlib import Path

PORTFOLIO_PATH = Path(__file__).resolve().parent / 'data/campaign_portfolio.json'
TYPES = {'SS': 'short_story', 'CC': 'curated', 'FC': 'full', 'MC': 'major',
         'GC': 'grand', 'CSS': 'simulation_system'}
# These connect existing discovery records, never a supplied concept's launch flag.
CURRENT_CAMPAIGNS = {'MC-01': 'hundred-years-war', 'GC-01': 'world-of-kira', 'CSS-01': 'rise'}


def campaign_portfolio(campaigns):
    source = json.loads(PORTFOLIO_PATH.read_text(encoding='utf-8'))
    if source.get('schema_version') != 1 or not isinstance(source.get('entries'), list):
        raise ValueError('Invalid campaign portfolio')
    seen, entries = set(), []
    for original in source['entries']:
        record = copy.deepcopy(original)
        identity = record.get('catalogue_id')
        match = re.fullmatch(r'(SS|CC|FC|MC|GC|CSS)-(P)?[0-9]{2}', identity or '')
        if (not match or identity in seen or record.get('campaign_type') != TYPES[match[1]]
                or record.get('slate') != ('system' if match[1] == 'CSS' else 'future' if match[2] else 'launch')
                or record.get('development_status') not in ('concept_draft', 'planned', 'in_development')
                or record.get('availability', {}).get('release_approved') is not False
                or record.get('readiness', {}).get('full_campaign_ready') is not False):
            raise ValueError('Invalid campaign concept: ' + str(identity))
        seen.add(identity)
        # Concept Draft is internal. A metadata edit cannot publish it by toggling
        # its preview flag, and cannot promote a product to a playable release.
        if record['development_status'] == 'concept_draft' or record['availability'].get('preview') is not True:
            continue
        current_id = CURRENT_CAMPAIGNS.get(identity)
        current = next((c for c in campaigns if c['id'] == current_id), {})
        if identity == 'MC-01':
            available = any(e.get('ready') is True and e.get('playable') is True
                and re.fullmatch(r'[a-f0-9]{64}', e.get('snapshot_sha256') or '')
                for p in current.get('periods', []) for e in p.get('entries', []))
        elif identity == 'CSS-01':
            available = any(t.get('id') == 'R00' and t.get('ready') is True for t in current.get('templates', []))
        else:
            available = False
        record['current_campaign_id'] = current.get('id')
        record['available_slice'] = bool(available)
        entries.append(record)
    counts = Counter(e['slate'] for e in entries)
    return {'schema_version': 1, 'version': source['version'], 'scope': source['scope'],
        'approval_policy': source['approval_policy'], 'source': copy.deepcopy(source['source']),
        'counts': {'total': len(entries), 'launch': counts['launch'], 'future': counts['future'],
            'systems': counts['system'], 'free_launch_stories': sum(e['campaign_type'] == 'short_story'
                and e['slate'] == 'launch' and e['availability']['launch_target_access'] == 'free' for e in entries),
            'available_slices': sum(e['available_slice'] for e in entries)},
        'entries': entries}
