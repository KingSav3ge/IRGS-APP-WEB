# A4-APP-01 partial delivery: running build identity

The running host snapshots its edition from `VERSION.json` and SHA-256 hashes
of its selected App, Engine and Catalog release manifests at startup. The same
response also reports hashes of the selected host, Engine Core and Catalog
portfolio source files. No local path, environment variable, operator setting or
credential is returned. The existing local `/api/campaigns` response carries the
snapshot. A reused host reports its own startup snapshot; changing files on disk
requires a host restart to produce a new snapshot.

The interface displays the running edition and abbreviated App, Engine and
Catalog manifest hashes. Full manifest hashes are available in the display's
tooltip and the local response. A missing or invalid edition is reported as
unknown; a missing component file has a null fingerprint. All 3.x editions are
labelled Pre-Alpha. The identity is a fingerprint of selected files, not a Git
commit or a full source-integrity verification. Run `tools/verify_components.py`
for the latter and compare exact commits separately for integration.

This is an independent implementation increment within A4-APP-01 and contributes
toward A4-G01. A4-APP-01 remains in progress: protected operator configuration,
validation and a qualified production provider transport have not been delivered.
Engine's pinned Solo API provides a broker and transport protocol, but this App
has no production adapter. No provider credentials are loaded or exposed and no
live provider call was made. Offline local play remains available. A4-G01 and
A4-G08 remain unqualified; configured AI, native Windows qualification and the
other Alpha gates still need their own evidence.

The following checks use temporary synthetic stores and the actual pinned Engine
and Catalog. The browser checks include ordinary reviewed creation, reload,
responsive layout and the identity displayed from the local host. The host
identity tests check selected file hashes, missing version, secret absence and
restart/reuse behavior. Historical validation records remain attributed to their
original source.

```bash
python3 -B -m unittest discover -s IRGS_Web/tests -v
node IRGS_Web/tests/test_gameplay_ui.js
node IRGS_Web/tests/test_responses.js
node tools/qualify_interface_port.js /tmp/irgs-a4-build-browser.json /tmp/irgs-a4-build-shots
node tools/qualify_start_readiness.js /tmp/irgs-a4-starts.json /tmp/irgs-a4-starts-shots
node tools/qualify_communication_bridge.js /tmp/irgs-a4-communication.json /tmp/irgs-a4-communication-shots
node tools/qualify_process_bridge.js /tmp/irgs-a4-process.json
node tools/qualify_shared_responses.js /tmp/irgs-a4-shared.json
node tools/qualify_interface_refinement.js /tmp/irgs-a4-refinement.json /tmp/irgs-a4-refinement-shots
python3 -B tools/verify_components.py --component app
```

The current component stays 3.4.3 Pre-Alpha, with Engine
`efc84364b86e640f5028bfac2dfd5ae3021695a9` and Catalog
`6f927b00e12a3339861ac353bc38d03c68279662`. Coordinator owns joined review,
release and all Alpha gate qualification. Next continue protected setup, including
configuration validation without dispatch, separate operator/player exposure,
restart/offline behavior and a qualified adapter; then A4-APP-02 and A4-APP-03.

## Executed checks and pending publication

- Full Web suite: 258 run, 251 passed and seven Windows-only skips. It completed
  before the final client-only older-host fallback and its new interface test.
- Interface suite: 150 passed against the preceding client. After the fallback,
  a sandbox-only run passed 150 checks, including the new fallback check; one
  registry enumeration check was omitted because its Python subprocess is denied
  in the sandbox. A full final-source interface rerun remains pending.
- Six Chromium suites passed before the final client-only fallback, including
  the visible identity, normal creation and recovery journeys. Final-source
  browser execution remains pending. These checks made zero provider calls.
- Formatter: 13 passed; tooling: one passed. Final App component verification
  passed for 86 App files, 200 Catalog files and the selected dependency pins.
- JavaScript syntax and CRLF-aware diff checks passed. A final full interface
  and browser rerun, and repository push, need the network-enabled environment.

The automatic review for network-enabled execution failed due to the account
usage limit; it was not a finding about safety. Preserve the local commit and
resume the final checks and publication when review is available. No unified
integration or Alpha qualification is implied.
