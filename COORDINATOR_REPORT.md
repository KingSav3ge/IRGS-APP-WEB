# App report to IRGS Enviroment — solo-runtime-01

23 October 2026. Target: IRGS 3.4.0 development, with executable Core 3.3.
Push destination: `KingSav3ge/IRGS-APP-WEB/main`. This is an executable App review,
availability and recovery increment. It does not complete AI-assisted Solo play.
The delivery response supplies the full pushed commit SHA.

## Implemented behavior

Equipment, authored opening and Rise choices now open an explicit review.
Selection and cancellation send nothing. The player may edit the words or keep
them in the existing response editor without submitting. Different wording
disables confirmation of the original structured action; an unsent independent
response survives review and action execution. Only explicit confirmation calls
the existing selected Core handler. No resource or interpretation logic moves
into App.

Review validity checks the campaign, actor, selected campaign control, revision,
request generation, current view, pending request and character availability.
Navigation/reload/mode changes discard stale reviews. Confirmation reuses the
existing durable request and result recovery, including lost acknowledgements.

Player availability reports that AI assistance is not connected. Supported
existing actions still run, and unsupported freeform remains unresolved. The
session-bound `/api/ai/status` exposes no diagnostic fields to Player mode;
Creator-only Providers & Models reports bounded unavailable diagnostics. Unknown
configuration fields are not rendered, source/status text is escaped, late status
responses are fenced, and checking status makes no inference request. No keys,
provider router, paid dispatch or fictitious benchmark is introduced.

## Exact source selection

Runtime dependency pointers remain the currently reviewed pair:

- Engine: `723627e629231b5e90f38b9d52b65c9a3967b92a`.
- Catalog: `3e898acb2179f18a41d7967817bedf429df29d3f`.

Fixture qualification explicitly reads Catalog commit
`2e4f389882df0807fc8064c1a0b533aaa3b1bcd3`, fixture
`irgs-solo-r00-eval-v1`, manifest SHA-256
`2d30e863c4f769f0e2039469807ca0c6eeef3f30edd17d96778cebcba65bdbe5`.
It reads the exact Git objects into a temporary evaluator directory without
moving the runtime pin or installing another editable content tree. Evaluator
setup/oracle remains outside host request payloads. The host receives reviewed
setup choices and explicit actor/action/request fields, using the real Core.

## Executed checks

| Check | Result |
| --- | --- |
| Full Web regressions | 170 run, 163 passed, seven Windows PowerShell launcher skips on Linux |
| Interface regressions | 80 passed, including explicit review/cancel/edit, two actions, double confirmation, stale reviews, safe status and existing lost-ack/reload checks |
| Attachment packaging tooling | One passed |
| `tools/qualify_solo_review.py --catalog-commit 2e4f389882df0807fc8064c1a0b533aaa3b1bcd3` | Ten actual fixture cases: five accepted Core actions, four unchanged-save rejections, one exact original-result replay |
| Recovery in that HTTP qualification | Five host restarts and saved-result lookups; two concurrent retries for each accepted action; original receipts/save bytes retained; exact Trash/restore bytes |
| Information and conservation | Evaluator markers/private identifiers absent from actor exports, HTTP action requests and Player views; actual finite stocks plus consumption conserved at every fixture step |
| Chromium/Playwright with the Catalog R00 setup | Two consecutive Core actions; cancel/edit sends nothing; denied build leaves save unchanged; deliberately aborted accepted HTTP acknowledgement recovers by result lookup without another effect; draft survives reload; protected status works |
| App source integrity | Only App hashes refreshed; App and the exact pinned Engine/Catalog verified |

Browser and HTTP evidence are distinct from synthetic DOM transport checks.
No private user campaign was opened, migrated or restored. Qualification's
restore is recoverable Campaign Trash restoration; it does not certify a future
provider task's behavior after arbitrary world-snapshot restore.

Structured evidence: [SOLO_RUNTIME_VALIDATION.json](SOLO_RUNTIME_VALIDATION.json).
Previous Historical Details completion remains recorded in
[COORDINATOR_PIN_REVIEW.json](COORDINATOR_PIN_REVIEW.json) and
[HISTORICAL_DETAILS_VALIDATION.json](HISTORICAL_DETAILS_VALIDATION.json).
The complete archive and current catalogue remain unchanged.

## Remaining requirements and prerequisites

Engine has not published the new provider/action API at the reviewed runtime
pin. Its latest fetched commit `e2d7fd3d2c3aef436fda280c45c0e4508c02618a`
adds the 3.4.0 iteration label, not a provider runtime. App therefore returns
unavailable rather than inventing a second contract or a fake successful result.

Next: consume the published scoped Engine API; qualify the Catalog actor export
against it; connect interpreted proposal, explicit acceptance, committed result
and grounded narration. Provider absence/denial/timeout, cancellation, malformed
output, budget/usage and post-restore stale tasks still need that exact contract.
The fixture qualification uses explicit structured operations, not interpreted
natural-language intents. No provider model or semantic quality is certified.

No complete Engine suite, Windows execution, joined clean extraction or live
provider smoke was run for this App increment. Live smoke later requires configured
server credentials, an eligible exact route/model and a finite approved budget;
those credentials are not required for the remaining offline implementation.
Only the coordinator can approve a new dependency/update set and integrate joined
IRGS. This chat publishes only App. Its direct chat-send tool remains unavailable;
this repository report is the handoff, with no direct message claimed.
