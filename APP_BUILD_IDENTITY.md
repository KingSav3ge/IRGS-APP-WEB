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

## Executed checks

- Full Web suite: 258 run, 251 passed and seven Windows-only skips. It completed
  before the final client-only older-host fallback and its new interface test;
  Python/backend source did not change afterward.
- Final-source interface: 151 checks passed, including the older-host fallback.
  Formatter: 13 passed; tooling: one passed.
- Seven final-source Chromium journeys passed: interface port, selected starts,
  communication, process, shared responses, interface refinement and offline
  Solo review. The Solo journey used six synthetic transport calls and no live
  provider calls; the other six made zero provider calls. All had zero browser
  errors. The port journey verifies that the actual host identity is visible.
- App component verification passed: 86 App files, 200 Catalog files and the
  exact selected Engine and Catalog pins. Whitespace and JavaScript syntax checks
  passed. Native Windows launch/extraction and live-provider qualification remain
  untested; no Alpha gate is qualified by these results.

The initial publication attempt was interrupted when automatic review hit an
account usage limit. The final-source checks above were rerun after access
returned. See [machine-readable evidence](APP_BUILD_IDENTITY_VALIDATION.json).
