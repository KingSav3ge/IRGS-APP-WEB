"""Independent expectations for the adopted 1415 calendar receipt."""
import json


def assert_initial_calendar(test, state, actor, *, snapshot_sha256):
    test.assertEqual(set(state['knowledge']), {actor})
    test.assertEqual(set(state['knowledge'][actor]), {'setup:civil-date'})
    evidence = state['evidence']['setup:civil-date']
    receipt = state['knowledge'][actor]['setup:civil-date']
    test.assertEqual(evidence['subject'], actor)
    test.assertEqual(evidence['status'], 'established')
    source = 'historical-opening:' + snapshot_sha256 + ':opening'
    test.assertEqual(evidence['source_ref'], source)
    test.assertLessEqual(evidence['recorded_at'], receipt['received_at'])
    test.assertLessEqual(receipt['received_at'], state['clock'])
    civil = json.loads(evidence['assertion'])
    test.assertEqual(civil, {'kind': 'initial_civil_date', 'schema_version': 1,
        'date': '1415-08-11', 'calendar': 'julian', 'precision': 'day', 'time': None,
        'ordinal': state['historical_start']['snapshot']['entity_registry_template']['as_of'],
        'source_ref': source, 'elapsed_calendar_binding': False})
    return civil
