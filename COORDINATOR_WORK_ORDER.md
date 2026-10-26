# Coordinator work order — IRGS App/Website

Active cycle: shared start-context adoption, candidate next unified **3.4.3**.
Current published unified edition remains **3.4.2**. Previous release: **3.3.3**.

Read [the coordinator review](COORDINATOR_START_REVIEW_2026_10_26.md) and
[the exact evidence](COORDINATOR_START_REVIEW_2026_10_26.json). These instructions replace older
next-task ordering; historical delivery records retain their tested scope.

Adopt the already published Engine `cc450a6` API, documented in
`engine/START_READINESS_API.md` in IRGS-Engine. Engine is no longer the missing
contract dependency. The coordinator fixed module/discovery collisions by
renaming App preflight to `start_preview.py` and its test to
`tests/test_start_preview.py`; retain those separate names.

Close START-INT-002 through 005 in order:

1. Consume Engine's versioned readiness review and actor-bound existing opening
   options. Offer the optional Henry start explicitly and include its opening ID
   in actual review/creation/retry payloads. The old blanket App rejection of
   existing-person opening IDs must be replaced by Engine validation. A changed
   actor/mode clears the old choice/consent and forces review. Henry default and
   John remain declaration-only; no arbitrary/courier context can be borrowed.
2. Project Engine's actor-received `start_context`, initial Julian civil day and
   selected elapsed axis. Preserve unknown hour and `current_calendar_binding:
   false`; do not present local 20-second progress as a running civil clock. Use
   the real context classification and available operations in scene/opening
   guidance. Henry has no dispatch and no supported courier travel. Read-only
   views must not initialize, migrate, repair or reseed continuing saves.
3. Update the three exact Web failures listed in the review with positive checks
   for the legitimate calendar receipt and negative checks for unsourced scene,
   stock, authority, personal contacts and historical future. Do not remove the
   privacy assertions or suppress the received date to obtain a green suite.
4. Run full Web/interface checks and actual browser journeys for explicit Henry,
   default Henry, John, default new, authored new and R00; 390px, source absence,
   changed selection, lost creation/action reply, exact retry, reload, restore
   and actor boundaries. No live provider is needed. Then commit exact compatible
   published Engine/Catalog gitlinks and report the clean tested source set.

Publish adoption early for Catalog's separate consumer. Communication UI/HTTP,
protected operator configuration, supported-intent mapping and build diagnostics
remain subsequent work; cosmetic refinements do not replace the blocked start.

## Completion and ownership

Read `CHAT_CONTINUATION.md` for source selections, rules and checks. Publish only
this component. A work-order/plan change does not complete implementation or
qualify the new contract. Report exact published code and compatible dependencies,
actual passes/failures/skips and remaining work. Coordinator owns joined import,
fresh execution capture, joined/browser/package qualification and versioned
publication after all three viable updates are approved. No dispatch is implied.

## App adoption delivery

START-INT-002/003/004 and compatible pins for 005 are implemented. The exact
executed source, results and limits are recorded in
[START_CONTEXT_ADOPTION_VALIDATION.json](START_CONTEXT_ADOPTION_VALIDATION.json)
and [the delivery scope](START_CONTEXT_ADOPTION.md). Engine is consumed through
its published contract; Catalog's separate consumer qualification and coordinator
exact-set review remain pending. Earlier work-order acceptance above remains
available for review; this delivery creates no new unified release.


## Subsequent App communication delivery

The next communication/source/offer increment named in `CHAT_CONTINUATION.md`
is implemented over Engine `cc450a6` with Catalog `e1778e0` unchanged. It adds
actor-scoped preparation/review/acceptance, exact speech, received terms and
sources, conserved Engine transfers and durable original-result recovery.
Legacy receipt privacy remains preserved. See [scope](COMMUNICATION_BRIDGE.md)
and [fresh executed evidence](COMMUNICATION_BRIDGE_VALIDATION.json).

Qualification uses explicitly selected synthetic non-Rise/R00 channels. Product
initializers still need owned Engine/content channel and introduction selections;
App does not fabricate them or migrate saves. Protected operator configuration
is the next bounded App task. The START-INT-006 Catalog consumer and coordinator
exact-set/joined/browser/package gate remain pending. No unified import, new
release or edition increase is part of this component delivery.
