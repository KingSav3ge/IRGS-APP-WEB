# WorldWard operator setup

WorldWard runs offline by default. The optional assisted proposal path can be
explicitly configured for the pinned Fulcrum Engine's `openai-responses-local-1`
adapter and its exact reviewed `gpt-5.4-mini-2026-03-17` model. This is a local
configuration and protocol check, not proof that an account can access the
model, a measured model-quality result or authorization to spend funds.

The operator creates a JSON profile **outside the application source and campaign
saves**, with an absolute path. On POSIX the profile must be a regular file owned
by the operator with no group/other permissions (for example, `chmod 600`). Its
technical directory must also be outside source and saves, owned by the operator
and private (`chmod 700` if it already exists). The host creates that directory
when needed. It contains the Engine's persistent reservation ledger and host
scope metadata; preserve it across restarts. Do not share it with another host.

A profile must contain exactly these fields; replace the placeholder references,
limits and absolute private path with the operator's explicitly reviewed values:

```json
{
  "schema_version": 1,
  "enabled": true,
  "model": "gpt-5.4-mini-2026-03-17",
  "adapter_version": "openai-responses-local-1",
  "workload": "propose_local_action",
  "proposal_schema": "solo-proposal-1",
  "classification": "operator-approved-classification",
  "policy_ref": "operator-reviewed-transfer-policy",
  "approval_ref": "operator-route-approval",
  "config_version": "operator-config-v1",
  "price_revision": "operator-reviewed-price-ceiling-v1",
  "budget_units": 1000,
  "reservation_units": 100,
  "max_output_tokens": 512,
  "max_inflight": 1,
  "deadline_seconds": 30,
  "private_dir": "/absolute/path/outside/worldward-and-saves/private",
  "operations": ["execute_player_scene_action", "execute_settlement_action"]
}
```

These example numbers are **not** a price quote or recommended spending limit.
The operator must choose a finite budget and conservative per-attempt reservation
covering the bounded input, output and applicable fees in their chosen units.
The ledger enforces those units; it cannot verify actual provider pricing, bills,
model availability, retention terms or account entitlements. An unresolved
charge retains its reservation. Reopening the same ledger preserves its ceiling;
changing the configured ceiling on that ledger is rejected rather than silently
resetting accounting. Select only workloads and operations the operator approves.

The secret is supplied to the server process through its `OPENAI_API_KEY`
environment variable, not the JSON file, command arguments, website, browser
storage or a campaign save. Do not paste a credential into a shell command that
will be recorded in history. No credential is read when no profile is selected.
The adapter reads it only when an explicitly requested proposal is dispatched;
the status check only establishes whether a suitably formatted value is present.
Never commit the profile, key or private technical directory.

Before launch, check the profile without dispatch or creating a ledger:

```bash
python3 -B IRGS_Web/server.py --operator-config /absolute/path/to/operator.json --check-operator-config
```

This verifies the selected local route, schema and bounds. It does not check the
credential, ledger, provider account, model access, current price or network.
To start a new local host with the profile, supply `--operator-config` to
`server.py`, or set the non-secret `IRGS_OPERATOR_CONFIG` path in the launcher
process environment before starting it. An existing reused host retains the
configuration it started with; inspect its status and start the intended host on
a separate port if needed. No settings are changed through the player API.

In Creator workspace → AI Network → Providers & Models, readiness reports only
safe local status, the selected model, workload and allowed operations. A missing
credential, invalid profile, exhausted reservation budget or full concurrency
leaves assistance unavailable. Ordinary local actions and unresolved declarations
remain usable. Looking at status or a draft makes no provider request. An actual
proposal is opt-in; the player reviews the exact words and selected action, and
only explicit acceptance may commit the Engine result. No automatic paid retry,
provider fallback or fabricated model output is performed.

The current protected-profile reader requires POSIX ownership/mode checks. On
Windows it fails closed to offline mode until native ACL validation is implemented
and qualified. Creator mode is an explicit local-owner workspace, not a multi-user
security boundary. Live provider qualification requires a separately approved
finite budget and synthetic evaluation; the automated tests use a fake HTTP sender.
