# Coordinator review — 28 October 2026

Edition **3.4.3 Pre-Alpha**. Next unified iteration: **3.4.4 Pre-Alpha**.
Functional Alpha 4.0 gates remain open. This review publishes no joined build.

## Findings requiring correction

1. **P2 — Select the intended offer recipient explicitly.** In App
   tools/qualify_communication_bridge.js:26, the browser helper supplies transfer
   terms for Oren but leaves the selected participant at its default. The latest
   Engine's legitimate introductions make Elin the first participant. Core
   correctly rejects an Elin offer targeting oren-home; the helper then waits
   30 seconds for an impossible revision increase. The committed qualifier fails
   with the latest roots. A diagnostic copy selecting oren explicitly passes
   all six commands, conserved transfers, lost acknowledgements, recovery,
   privacy and mobile behavior. Fix the helper and make rejection diagnosable;
   do not remove valid introductions or relax Core recipient validation.

2. **P2 — Derive the expected build edition.** App
   IRGS_Web/tests/test_build_identity.py:22 asserts literal 3.4.3, and
   tools/qualify_interface_port.js:21 waits for literal IRGS 3.4.3 Pre-Alpha.
   Simulating only VERSION.json=3.4.4 in memory reproduces the unit failure
   while the actual build function correctly returns 3.4.4/pre_alpha. Derive the
   expectation from the selected metadata and verify UI against the host response.
   Keep missing/invalid metadata and 3.x classification checks.

These are integration-test defects. No production simulation defect was
reproduced in the reviewed bounded operations. The diagnostic browser change is
outside source; the committed qualifier has not been fixed by this review.

## Reviewed scope and evidence

| Component | Reviewed exact source | Assessment |
| --- | --- | --- |
| Engine | 0a50694ae1defcbd85143e3de4de3ae5157ea29c | Reviewed ordinary fictional quay and R00 speech. No autonomous NPC reply, consent, offer selection or broad dialogue completion. Continue selected travel and supported-intent contracts. |
| App | 41ca38473dd7ad30f201c7104f26e51d3df85df2 | Non-secret running-build fingerprints work. Protected operator setup remains unfinished. Correct the two harness findings before latest dependency adoption. |
| Catalog | 476f459aed4903bdacbe4c37041d5ed8308d94a4 | Independent context/journey evaluation keeps source selections, private oracle separation and unmet requirements explicit. Add a separate latest adopted-set qualification rather than rewriting old identities. |

Fresh review execution passed 102 focused Engine tests, five Catalog contract
tests, two App identity tests, 151 interface checks, both ordinary-start HTTP
journeys, and interface/start Chromium suites against explicit latest roots.
The original communication browser qualifier failed as described above; the
diagnostic recipient correction passed. Catalog's five baseline and six journey
HTTP consumers also pass at their exact declared historical selections.

The previous automatic report for these exact latest component heads records
781/782 Core passes with one private-fixture policy skip, 251/258 Web passes
with seven Windows skips, 32 tooling passes and eight independent HTTP passes.
Those attributed earlier results are not fresh full-suite execution here.
Its sole failing regression check is stale operation/dependency evidence after
Engine code/tests changed. A manifest refresh cannot replace execution capture.

See [the structured review](COORDINATOR_REVIEW_2026_10_28.json) for exact
scope, commands, findings and evidence digests. Zero live provider calls and
no user saves were used. No native Windows or new package qualification is claimed.

## Release disposition and next work

Hold unified publication until App publishes the two harness fixes and exact
compatible dependency pins, Catalog supplies separately selected current
acceptance, and the coordinator captures fresh operation evidence and qualifies
the joined/browser/clean-package candidate. App currently commits Engine
efc84364b86e640f5028bfac2dfd5ae3021695a9 and Catalog
6f927b00e12a3339861ac353bc38d03c68279662. Testing an explicit root override
does not update those pins.

Continue offline Alpha work immediately. Engine owns ordinary authority,
resources/time and supported operations; App owns protected setup and reviewed
player controls; Catalog owns independent current-context acceptance. Wider
NPC/institution decisions, selected conflict/recovery, live quality and the
functional Alpha gates remain unfinished.

The user also directs a shared development/Creator Workshop world builder.
Read [the world-builder plan](WORLD_BUILDER_PLAN.md). Its first draft/validation/
playtest slice should support the Alpha contexts; full editor breadth does not
replace the Alpha gameplay gates. Repository guide publication does not dispatch
or resume another chat.
