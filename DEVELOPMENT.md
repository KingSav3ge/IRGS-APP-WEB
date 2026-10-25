# IRGS App/Web development guide

Current guide: 25 October 2026. Owner: `KingSav3ge/IRGS-APP-WEB/main`.
Start with [CHAT_CONTINUATION.md](CHAT_CONTINUATION.md).

## Qualified baseline and scope

IRGS **3.4.0 development**, Core compatibility **3.3**. Develop shared systems
across campaigns and themes. Rise R00 and the existing non-Rise authored opening
are actual supported regression contexts. Synthetic theme/profile checks prove
their recorded formatting/declaration behavior, not new campaign mechanics.

The [coordinator integration](https://github.com/KingSav3ge/IRGS/blob/65351ebcfe2538d880f576a3ce4aa2230537e08d/provenance/qa/shared_response_integration_3_4_0_review.json) qualified joined `65351ebcfe2538d880f576a3ce4aa2230537e08d`:

| Component source | Qualified commit |
| --- | --- |
| Engine | `2f9476c6090878257d17cab3ad3a83a7ce18a5dc` |
| App/Web | `aae8a25656c890181e0aa569df2c716968ec3642` |
| Catalog | `27fff8385d1c01fdfe9ad7254b7647e6bc12a01e` |

Recorded integration results: 680 Core tests run (679 passed, one private-fixture
policy skip); 201 Web run (194 passed, seven Windows skips); 105 interface checks;
104 Catalog checks; eight independent HTTP checks. Two-context Chromium and
clean-package qualification passed with zero live inference. These are attributed
prior results, not tests newly executed by this guide update.

Later guide-only commits do not alter this qualified source set. Preserve
independent content/schema versions and historical evidence. See
[shared scope](IRGS_SYSTEMS_SCOPE.md), [continuation](CHAT_CONTINUATION.md) and
[the work order](COORDINATOR_WORK_ORDER.md).

## Source ownership and startup

Own `IRGS_Web/`, the canonical Python host, interface and Catalog viewer. `Engine/`
and `Catalog/` are pinned Git submodules. Preserve their committed pointers;
`git submodule update --init --recursive` checks out the selected revisions.
Commit a new pair only after actual compatibility review. Source fixes belong to
their owners; App must not create another simulator or provider router.

```bash
git status --short
git pull --ff-only origin main
git submodule update --init --recursive
python -B IRGS_Web/server.py --port 8766
```

Use loopback and a separate development port. The Windows root launcher defaults
to 8765 and may reuse another valid installation; tests use temporary saves and
their own ports. Keep operator credentials and detailed accounting server-side.

## Completed foundation

- Common local_responses and saved presentation envelopes in non-Rise and Rise.
- Engine receipt/draft and selected Catalog semantic draft consumption; App-owned
  local UI pack, exact outcomes, non-submitting drafts and literal fallback.
- Lost-acknowledgment/restart/restore protection, themes/reading modes and protected
  usage, including reviewed charge/overrun consistency with Engine admission.
- Coordinator patch: Catalog formatter/code and JSON consume the exact bytes
  verified by their hashes. Retain `CatalogIntakeTests` and both replacement cases.

Read [response contract](IRGS_Web/responses/README.md) and the owning
`Engine/engine/SHARED_SYSTEMS_API.md` / `CONTINUATION_COMMUNICATION_API.md` documents.
The implementation files are under `IRGS_Web/`; avoid a second editable App tree.

## Delivered received-process increment — 25 October 2026

Common Story/HTTP review and explicit continuation now use the pinned Engine's
existing typed process API. Qualified contexts: non-Rise authored observation
and Rise shelter work. Immutable server-owned preparation, actor/scope/revision
checks, received-only progress, atomic candidate/result saves, original receipt
recovery, pause/resume, failure/concurrency/restart and restored-branch handling
are implemented. Routine dispatch remains zero. Process starts are explicitly
unavailable pending the discovery contract described below.

See [process contract](IRGS_Web/PROCESS_BRIDGE.md),
[executed evidence](PROCESS_BRIDGE_VALIDATION.json) and
[current handoff](COORDINATOR_REPORT.md). The existing verified-byte Catalog intake,
response depot, native shared actions and themes are retained. Exact dependency
pins remain Engine `2f9476c6090878257d17cab3ad3a83a7ce18a5dc` and Catalog
`27fff8385d1c01fdfe9ad7254b7647e6bc12a01e`. This App increment needs coordinator
review and fresh joined qualification; it does not reopen the completed baseline.

## Next bounded increment

Add protected operator/launcher configuration for the existing optional Solo
service, keeping credentials and detailed accounting server-side and ordinary
play runnable without a provider. Use existing Engine provider/charge contracts;
validate a concrete configuration without live dispatch, test missing/invalid
configuration and startup/reuse behavior, and preserve local loopback hosting.
Live inference still requires its separately configured authorization.

The process start flow waits on an Engine-owned, actor-safe discovery contract:
sourced kind/action choices bound to actual selected elapsed rules and scope,
with published command/detail semantics and no hidden-feasibility oracle. Do not
infer start controls from private rule dictionaries or theme labels. Continue
independent App work while that exact dependency is pending. Communication/source
controls and additional process contexts require their own qualification.

## Check the App

```bash
python -B tools/verify_components.py --component app
python -B -m unittest discover -s IRGS_Web/tests -v
node IRGS_Web/tests/test_responses.js
node IRGS_Web/tests/test_gameplay_ui.js
node tools/qualify_shared_responses.js /tmp/irgs-shared-browser.json
node tools/qualify_process_bridge.js /tmp/irgs-process-browser.json
```

Real browser qualification requires Playwright and Chromium as development tools;
the product host uses Python's standard library. Report the seven Windows-only
skips on Linux. Browser/HTTP tests must use synthetic state and verify zero
routine dispatch. Check actual effects and recovery, including failed save and
stale navigation; a formatting mock cannot qualify a new handler.

`IRGS_ENGINE_ROOT` and `IRGS_CATALOG_ROOT` can select explicit candidate sources
for isolated checks. Report those sources and actual imported module paths; an
environment override does not update committed submodule pins. Component verifier
checks committed pointers against checked-out submodules. Refresh only App after
source edits: `python -B tools/refresh_component_releases.py --component app`.

## Rules for every increment

Keep one authoritative Core and the nine K-owners; provider work retains the six
existing Director categories. Distinguish intent, authorization, committed effects,
received information and presentation. Only actual actor-legitimate records may
support a response. Testimony and uncertain information retain their status.
Keep storage revision, causal order, elapsed spans, civil dates and information
times distinct. Select real rules/adapters; themes and text create no capability.

Routine responses require no provider, key or model tokens. Preserve exact
receipts, negation, actual zero/absent durations, editable intentions and explicit
submission. Missing text or rules retain a literal/unresolved result and cannot
authorize paid fallback. Keep pinned code/content intake on the exact verified
bytes; retain the component-update regression in App.

Use temporary synthetic saves. Never read/migrate user campaigns or run the
external private-save fixture. Preserve original archives, source records,
rights, adopted canon and 44 previews. Historical Details is fully delivered;
archive reacquisition is complete. Preview/content presence grants no release
or mechanical authority. General freeform/combat, generated dialogue, sustained
institutions, full C2, live model quality and wider hosting retain their open
requirements; Co-op remains deferred.

## Deliver the increment

Keep completed, active and remaining work current. After an actual source edit,
refresh only the owning component release, run relevant behavioral checks and
verify source integrity. Hash refresh and planning alone qualify no feature.
Use Python 3.12+ without `-O`; interface/browser tooling uses Node 20+.

Push only this repository's `main`. Return the full pushed SHA, actual changed
behavior, APIs/adapters, exact dependencies, commands/results/skips and remaining
limits to IRGS Enviroment. Coordinator imports product source only after all
three viable updates, compatible App pins and fresh joined qualification.
Root guide/work-order edits alone need no component release refresh or invented
runtime delivery. Preserve local work before pulling; avoid resets and force pushes.

Previous guide and original owner counts: [dated history](DEVELOPMENT_HISTORY_2026-10-25.md).
