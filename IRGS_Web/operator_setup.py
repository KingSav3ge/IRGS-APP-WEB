"""Explicit, server-only operator configuration for the reviewed Solo adapter.

The file contains approval references and reservation limits, never credentials.
Validation never calls a provider and rejects unsupported models/workloads.
"""
import json
import math
import os
from pathlib import Path
import re
import stat
from types import SimpleNamespace

from assistance import SoloConfiguration
from openai_proposals import ADAPTER_VERSION, CHECKED_MODEL, OpenAIProposalTransport
from solo_provider import (AttemptLedger, CapabilityBroker, CapabilityUnavailable,
    LOCAL_OPERATION, RISE_OPERATION, Route, SCHEMA_VERSION, SpecialistRegistry, TASK)

FIELDS = {'schema_version', 'enabled', 'model', 'adapter_version', 'workload',
    'proposal_schema', 'classification', 'policy_ref', 'approval_ref', 'config_version',
    'price_revision', 'budget_units', 'reservation_units', 'max_output_tokens',
    'max_inflight', 'deadline_seconds', 'private_dir', 'operations'}


def _fail():
    raise ValueError('Invalid operator configuration')


def _secure_file(path, source, saves):
    path = Path(path).expanduser()
    if not path.is_absolute() or path.is_symlink():
        _fail()
    path = path.resolve()
    if path == source or source in path.parents or path == saves or saves in path.parents:
        _fail()
    # The stdlib cannot reliably inspect a Windows file ACL. Do not infer privacy.
    if os.name == 'nt':
        _fail()
    flags = os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0) | getattr(os, 'O_NONBLOCK', 0)
    try:
        fd = os.open(path, flags)
        with os.fdopen(fd, 'rb') as stream:
            info = os.fstat(stream.fileno())
            if (not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid()
                    or info.st_mode & 0o077 or info.st_size > 16384):
                _fail()
            data = stream.read(16385)
        def unique(pairs):
            result = {}
            for key, value in pairs:
                if key in result: _fail()
                result[key] = value
            return result
        return json.loads(data, object_pairs_hook=unique)
    except (OSError, UnicodeError, ValueError, TypeError):
        _fail()


def _private_directory(value, source, saves):
    if not isinstance(value, str) or not Path(value).is_absolute():
        _fail()
    path = Path(value).expanduser()
    if path.is_symlink(): _fail()
    path = path.resolve()
    if path == source or source in path.parents or path == saves or saves in path.parents:
        _fail()
    if path.exists():
        info = path.stat()
        if (not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o077):
            _fail()
        if any((path / name).is_symlink() for name in ('inference.sqlite', 'host-scope.json')):
            _fail()
    return path


def load_operator_configuration(profile_path, save_folder):
    """Return a validated SoloConfiguration. No provider request is made."""
    source = Path(__file__).resolve().parent.parent
    saves = Path(save_folder).resolve()
    data = _secure_file(profile_path, source, saves)
    if not isinstance(data, dict) or set(data) != FIELDS: _fail()
    if (type(data['schema_version']) is not int or data['schema_version'] != 1 or
        data['enabled'] is not True or data['model'] != CHECKED_MODEL or
        data['adapter_version'] != ADAPTER_VERSION or data['workload'] != TASK or
        data['proposal_schema'] != SCHEMA_VERSION): _fail()
    for key in ('classification', 'policy_ref', 'approval_ref', 'config_version', 'price_revision'):
        if not isinstance(data[key], str) or not re.fullmatch(r'[A-Za-z0-9_.:-]{1,128}', data[key]): _fail()
    for key in ('budget_units', 'reservation_units', 'max_output_tokens', 'max_inflight'):
        if type(data[key]) is not int: _fail()
    if not (1 <= data['reservation_units'] <= data['budget_units'] <= 2**63-1 and
            16 <= data['max_output_tokens'] <= 4096 and 1 <= data['max_inflight'] <= 16): _fail()
    if (type(data['deadline_seconds']) not in (int, float) or
        not math.isfinite(data['deadline_seconds']) or not 0 < data['deadline_seconds'] <= 300): _fail()
    operations = data['operations']
    if (not isinstance(operations, list) or not operations or not all(isinstance(x, str) for x in operations)
            or len(set(operations)) != len(operations)
            or not set(operations) <= {LOCAL_OPERATION, RISE_OPERATION}): _fail()
    private = _private_directory(data['private_dir'], source, saves)
    route = Route('openai-local-v1', 'OpenAI', 'direct', 'api.openai.com', CHECKED_MODEL,
        CHECKED_MODEL, data['config_version'], data['policy_ref'], data['price_revision'],
        data['reservation_units'], classifications=(data['classification'],), workloads=(TASK,),
        max_output_tokens=data['max_output_tokens'], enabled=True, approval_ref=data['approval_ref'],
        lifecycle='qualified', tested_capabilities=(SCHEMA_VERSION,), adapter_version=ADAPTER_VERSION,
        operations=tuple(operations))
    registry = SpecialistRegistry([route])
    # Exercise the Engine's real selection guard without creating a request or ledger.
    for operation in operations:
        candidate = SimpleNamespace(allowed_routes=(route.route_id,), config_version=data['config_version'],
            policy_ref=data['policy_ref'], classification=data['classification'], task=TASK,
            operation_id=operation, max_output_tokens=data['max_output_tokens'], model_input=lambda: {})
        try: registry.eligible(candidate, route.route_id)
        except CapabilityUnavailable: _fail()

    def broker(scope_reader):
        private.mkdir(parents=True, mode=0o700, exist_ok=True)
        # Recheck immediately before technical files are opened.
        _private_directory(str(private), source, saves)
        ledger = AttemptLedger(private / 'inference.sqlite', budget_units=data['budget_units'],
                               max_inflight=data['max_inflight'])
        return CapabilityBroker(registry, ledger, enabled=True, scope_reader=scope_reader)

    return SoloConfiguration(broker, OpenAIProposalTransport(enabled=True), route.route_id,
        data['classification'], data['policy_ref'], data['config_version'], private,
        data['deadline_seconds'], data['max_output_tokens'], operator_route=route)


def credential_available():
    value = os.environ.get('OPENAI_API_KEY')
    return (isinstance(value, str) and bool(value.strip()) and len(value) <= 4096
            and '\r' not in value and '\n' not in value)
