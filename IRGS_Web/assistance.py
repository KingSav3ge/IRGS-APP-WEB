"""Public availability and protected diagnostics; no inference or routing here."""


def assistance_status(*, developer=False):
    # The selected Engine has no provider/action API yet. Do not infer readiness
    # from an environment variable, a research model name, or a local UI flag.
    result = {
        'status': 'unavailable',
        'available': False,
        'message': 'AI assistance is not connected. Listed actions remain available; freeform declarations remain unresolved.',
        'campaign_effects': False,
    }
    if developer:
        result['diagnostics'] = {
            'reason_code': 'engine_contract_not_available',
            'dispatch_enabled': False,
            'provider_runtime': 'not_connected',
            'model_evaluations': 'not_run',
        }
    return result
