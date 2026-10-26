# Coordinator review — shared IRGS starts

26 October 2026. Unified **3.4.2 remains published** at `ba551af`. The next unified
publication is **3.4.3**. This review does not import product source or advance a
version. The three development chats completed their first assigned increments.

| Owner | Received product commit | Review |
| --- | --- | --- |
| Engine | `cc450a6f00a249d2169cdacdfc9c4b1e03f67cc8` | Bounded readiness/context API and optional sourced Henry observation pass Engine review; App/Catalog adoption pending. |
| App | `23184e1e70b6005ad6170edb3843afcaae42e18a` | Preflight and explicit limited-mode consent work at old pins; candidate adoption blocked. Coordinator fixed the import collision. |
| Catalog | `e1778e080385b6ff2bbb93f47f91d0da6e9d6780` | Requirements, availability copy and original baseline diagnostics accepted within scope; new-contract consumer pending. |

## Fixed integration bug

App and Engine both introduced `start_readiness.py`. The host puts Engine runtime
first on `sys.path`; App's imports therefore loaded Engine's different API and
dropped `/api/starting-preview` and `/api/playthrough` requests. Both owners also
introduced `test_start_readiness.py`, preventing full Web unittest discovery.
The coordinator renamed App's files to `start_preview.py` and
`tests/test_start_preview.py`, updated App imports/mock target and refreshed App
hashes. Pins and product behavior otherwise remain unchanged. Keep these names.

## Remaining integration work

1. **App / START-INT-002:** consume Engine's actor-bound existing-person options
   and readiness schema. Henry's published opening currently receives HTTP 400
   from App preflight and cannot be chosen in the wizard. Require explicit choice;
   default Henry and John remain limited modes. No courier fiction for them.
2. **App / START-INT-003:** project actor-received initial civil checkpoint and
   selected elapsed context. A direct synthetic Henry observation commits **20
   seconds**, while App returns `elapsed_time: null` and day zero/unresolved.
   `scene.scope` says `authored_fiction` and the saved opening wrongly asks Henry
   to move/deliver a dispatch. Use actual context and supported capabilities.
   A received initial Julian day is not a running civil clock or known hour.
3. **App / START-INT-004:** adopt the legitimate calendar receipt in the three
   failing Web tests. Assert its exact provenance/status and absence of invented
   operational news. Preserve the privacy checks instead of removing them.
4. **App / START-INT-005:** qualify and commit exact compatible Engine/Catalog
   gitlinks after adoption. Current pins still select the previous product set.
5. **Catalog / START-INT-006:** preserve `player_starts_v1` baseline identities and
   add a separate new-contract consumer selection. Include optional Henry,
   declaration-only Henry/John, new default, authored new character and R00.
   Source uncertainty, actual Core result, civil day precision, local elapsed,
   no fabricated possessions/authority, replay and save/reload are required.

Engine's public contract is already published:
[START_READINESS_API.md](https://github.com/KingSav3ge/IRGS-Engine/blob/cc450a6f00a249d2169cdacdfc9c4b1e03f67cc8/engine/START_READINESS_API.md).
App and Catalog can now adopt it. Engine should support that handoff without
changing the contract silently. John lacks a sourced operational context and
stays held; one Henry observation is not a generally playable historical campaign.

## Checks actually executed for this review

- Engine: **773 run, 772 passed, one absent historical-save skip**.
- App with its committed old pins plus the collision patch: **234 run, 227
  passed, seven native Windows skips**.
- App with delivered Engine/Catalog plus the same patch: **234 run, 224 passed,
  three calendar-contract failures, seven Windows skips**. No import errors remain.
- Interface: **137 checks passed**. Real Chromium starting journeys pass in four
  contexts, including 390px, cancel/change selection, unavailable source,
  lost acknowledgements, original-result retry, reload and withdrawal. Zero
  provider calls, browser errors or external requests. Henry selection is absent.
- Independent HTTP mechanics: **eight passed, zero skips**, against candidate
  owners plus the patch. Direct Henry HTTP creation/observation/retry also works;
  it exposes the App presentation/preflight gaps above.
- Catalog discovery: **209 run, 131 passed, 78 source-selection/reader skips**.
  Seven of those skipped baseline start consumers were then explicitly executed
  at their original Engine `91b2005` / App `00634b1` selections: **seven passed**.
  These counts overlap; remaining historical consumers/readers were not rerun.
- Engine, App at its committed pins, and Catalog integrity checks pass. Catalog
  retains 44 records and the original archive/depot. No user save was used.

Machine-readable scope and source hashes are in
[the review evidence](COORDINATOR_START_REVIEW_2026_10_26.json). Original owner
validation files remain dated at their actual tested sources. This is a review
of component source plus a documented patch, not a clean joined release test.

## Next handoff and publication

Read the updated `CHAT_CONTINUATION.md` and `COORDINATOR_WORK_ORDER.md` in each
owner repository. Repository publication does not resume a chat; direct dispatch
is unavailable. After App adoption and Catalog consumer qualification, the
coordinator reviews the exact compatible set, regenerates current execution
evidence, runs joined/browser/package checks and applies the existing all-three
gate. Only then publish unified 3.4.3 with coordinated versions across four repos.
Keep previous release field 3.3.3 and executable compatibility Core 3.3.
