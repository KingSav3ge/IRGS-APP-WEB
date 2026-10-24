# App report to IRGS Enviroment — solo-runtime-01

24 October 2026. Target: **IRGS 3.4.0 development**, executable Core compatibility
3.3. Delivery repository: `KingSav3ge/IRGS-APP-WEB/main` only. The delivery response
supplies its full pushed SHA. This delivers the bounded offline App proposal flow;
it does not claim a qualified live AI release or complete Solo/C2 coverage.

## Executable behavior

Listed equipment, authored opening and Rise choices require explicit review.
Selection, editing and cancellation commit no world effect. Edited words can be
kept as an unsent draft; an independent response survives action execution.

`SoloService` optionally consumes Engine's server-only builder, capability broker,
ledger and acceptance API. `make_server(..., solo_configuration=...)` takes explicit
trusted configuration; the default host is unconfigured and makes no provider
request. No App router, validator, alternate rules or world store was introduced.
Keys, approval, routes, limits and accounting stay server-side. Creator status is
protected and allowlisted; Player projections contain no developer diagnostics.

The connected flow retains exact editable intention, shows a supported action
and received source references, then requires explicit acceptance. Core's actual
handler commits once. Its outcome summary/observations supply grounded text;
provider prose has no authority. Unsupported freeform/combat remains unresolved.

Proposal lookup cannot create a fresh inference attempt. Stable accepted requests
reuse existing action-result recovery across lost acknowledgements and restart.
World plus public receipt share one atomic, flushed save replacement under the
single host writer lock. Technical cancellation and restore identities live
outside saves/source. Restore rotates identity before identical-byte restoration.
Engine and browser fences reject late output after state change, navigation,
actor/campaign change, edited intent or review closure. Provider I/O holds no save
lock, so cancellation and unrelated actions can proceed.

## Exact dependencies and remaining integration gap

Committed dependency pointers remain the reviewed pair:

- Engine `723627e629231b5e90f38b9d52b65c9a3967b92a`.
- Catalog `3e898acb2179f18a41d7967817bedf429df29d3f`.

Engine candidate **`500ab4286aed5354719a78006195922316b41023`** was exported from
its exact Git objects to temporary storage and selected through `IRGS_ENGINE_ROOT`
for offline HTTP/browser qualification. It currently prepares and accepts only
`scene_actions`. Catalog's synthetic R00 fixture targets `settlement_runtime`;
**its interpreted proposal path remains unsupported**. App does not supply a
second executor to disguise this gap. The full interpreted flow is proven using
Engine's synthetic authored opening, not the R00 scenario.

Catalog fixture **`2e4f389882df0807fc8064c1a0b533aaa3b1bcd3`**, fixture
`irgs-solo-r00-eval-v1`, manifest SHA-256
`2d30e863c4f769f0e2039469807ca0c6eeef3f30edd17d96778cebcba65bdbe5`,
was separately qualified through real existing R00 structured handlers. Its exact
files were read into temporary evaluator storage without changing the runtime
pin. Only evaluator code reads the private oracle; no private campaign or archive
is sent to a model.

## Executed evidence

| Check | Result |
| --- | --- |
| Full Web on reviewed pins | 180 run, 163 passed, 17 skipped: seven Windows PowerShell launchers, ten optional Solo API checks absent from the older Engine |
| Full Web on exact Engine candidate above | 180 run, 173 passed, seven Windows launcher skips |
| App Solo HTTP cases within that candidate suite | Ten passed: two actions, exact intent, privacy, explicit/unchanged acceptance, malformed/unsupported output, denial, timeout, durable cancellation, state/restore fencing, failed save, lost ack/restart and concurrent acceptance retries |
| Selected Engine provider API suite | 22 passed; complete Engine suite not rerun by App |
| Synthetic interface regressions | 85 passed, including new proposal acceptance/edit/cancel/stale/uncertain/reload checks |
| Attachment packaging tooling | One passed |
| Exact R00 HTTP qualification | Ten cases: five actual accepted Core actions, four unchanged-save rejections, one exact result replay; five restarts, two concurrent retries per acceptance; conserved finite stock and oracle exclusion; zero providers |
| Chromium/Playwright offline proposal flow | Two consecutive real Core actions; exact editable intent; cancel/edit and provider denial commit nothing; deliberately aborted accepted response recovers by result lookup; reload and late navigation fenced; six fake transport calls, zero live calls, zero browser errors |
| App/component integrity | Only App hashes refreshed; App and exact committed Engine/Catalog verified |

Reproduce the candidate checks with an exact Engine export selected through
`IRGS_ENGINE_ROOT`, `python3 -B -m unittest discover -s IRGS_Web/tests -v`, and
`node tools/qualify_solo_browser.js /tmp/irgs-solo-browser.json`. The browser
qualifier owns and removes its temporary synthetic host/save; Playwright and
Chromium are required. Reproduce R00 with
`python3 -B tools/qualify_solo_review.py --catalog-commit 2e4f389882df0807fc8064c1a0b533aaa3b1bcd3`.

Structured evidence: [SOLO_RUNTIME_VALIDATION.json](SOLO_RUNTIME_VALIDATION.json).
Historical Details evidence remains in [COORDINATOR_PIN_REVIEW.json](COORDINATOR_PIN_REVIEW.json)
and [HISTORICAL_DETAILS_VALIDATION.json](HISTORICAL_DETAILS_VALIDATION.json).
Adopted catalogue and original Historical archive are unchanged.

## Remaining requirements

Coordinator must review a compatible Engine/App/Catalog set before dependency
pointers move or joined IRGS integrates it. R00 proposal support, Engine direct
adapter, semantic/voice evaluations, general narration/dialogue, detailed developer
usage presentation, Windows execution and joined clean extraction remain open.
Live smoke requires an eligible approved exact route/model, server credentials
and finite budget; no live AI play or model benchmark is claimed. Fake transport
qualification does not establish model interpretation quality.

This repository report is the coordinator handoff. No direct chat message or
unified integration is claimed.
