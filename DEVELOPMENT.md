# App / Website development

## Current priority — shared IRGS systems

The user's current direction is development across campaigns and themes.
Read [the shared scope](IRGS_SYSTEMS_SCOPE.md) and
[the current work order](COORDINATOR_WORK_ORDER.md) before selecting work.
Rise R00 remains one regression fixture. Shared-system completion requires
supported non-Rise evidence; campaign-specific mechanics retain their own scope.
The records below preserve previously delivered work and historical evidence.

## Current priority — App local routine responses, 24 October 2026

### Completed

- [x] App-owned versioned response pack: 171 variants across 55 families, with
  139 system variants, 32 editable draft starters and eight whole-clause recipes.
- [x] Local validated formatting for routine UI, review, recovery, save and usage
  messages. Explicit Engine-assisted interpretation stays separate; missing
  templates/facts cannot trigger paid fallback or resolve unsupported mechanics.
- [x] Strict source/state/slot checks, immutable intake, deterministic event
  variants and actor/snapshot/role-safe composition. No personalized response
  cache and no Catalog content or dependency-pointer change.
- [x] Keep the exact Core outcome summary and only append actual recorded
  action duration, including zero. No invented stock, elapsed hour, success,
  project completion or NPC decision. Render source strings as text.
- [x] Editable generic draft starters review before copying, retain an independent
  draft until explicit Keep, execute nothing, and reject stale selections.
  Composer height is bounded so expanded draft choices do not obscure Story actions.
- [x] Real browser: four actual Core actions, unsuccessful physical attempt,
  exact HTML-like/braced receipt, 43 recorded seconds, lost-ack recovery,
  cancellation/edit/keep/reload; provider calls and browser errors both zero.

Fresh checks: 190 Web run, 183 passed, seven Windows launcher skips; 100 interface
checks; 13 formatter checks render all 171 variants and eight recipes; one packaging
tooling test; real Chromium routine/receipt flow and existing theme/mobile usage
qualification passed. App and exact reviewed dependencies verified. See
[response contract](IRGS_Web/responses/README.md) and
[delivery evidence](APP_RESPONSES_VALIDATION.json).

### Active / next

Maintain routine-first presentation while consuming Engine's and Catalog's owned
response contracts only through reviewed public projections and compatible pins.
The App pack owns UI/help/recovery wording; it does not become a world narrator or
second simulator. The next previously planned App item remains operator-controlled
Engine direct-adapter startup through host/launcher with explicit approvals and
finite limits. Conditional live smoke, semantic/voice evaluation, billing
reconciliation, general dialogue and broader C2 remain unfinished. This increment
uses no live provider and pushes only IRGS-APP-WEB.

## Current delivery — theme recovery and protected usage, 24 October 2026

### Completed

- [x] Restore the preferred warm charcoal/brown base and bronze/coral accents.
  Remove legacy global palette/reading overrides from the layout stylesheet.
- [x] Use one presentation layer: base application → public genre binding → known
  campaign override. Seven genre palettes cover military, Roman, fantasy,
  post-apocalyptic, shinobi, space and settlement. Century of Conflict, A Scot's
  Tale and Rise have explicit campaign accents. Unknown bindings use the base.
- [x] Home, Library, Trash and developer pages keep the base identity. Switching,
  deselecting and loading campaigns reset/apply themes; stale loads cannot repaint
  the current campaign. Display names, hidden state and provider text select no theme.
- [x] Preserve independent Dark/Light/Parchment reading mode, font and sizing across
  campaign switches and reload. Presentation writes no campaign state.
- [x] Creator → AI Network → Usage & Budgets reads Engine's existing ledger. It
  shows lifetime reservations/remaining operator units, occupied slots, recent
  requested/reported identities, reported tokens, errors and uncertain attempts.
  Missing reports and actual charges remain unknown. Inspection never dispatches,
  retries, refunds or resets a budget. Request/context/private certificates stay
  outside the projection; Player mode cannot read it.
- [x] Real Chromium covers all seven genres and three campaign overrides, reading
  reload, protected accounting, unchanged synthetic saves and 390px layout. Body text and
  visible Story panels/controls meet 4.5:1 across Dark, Light and Parchment modes.

### Verification and next goal

190 Web tests run: 183 passed, seven Windows launcher skips. Interface: 93 passed.
Seven new real-ledger HTTP cases cover authorization, privacy, unknown usage,
failed/cancelled reservations after restart, bounded rows, no configured ledger
and retryable storage failure. Packaging tooling: one passed. App and pinned
Engine/Catalog integrity verified. See [current evidence](THEME_USAGE_VALIDATION.json).

Next App goal: consume an operator-supplied Engine direct-adapter configuration
through the launcher/host, with explicit route/workload approval and finite
limits. Keep unconfigured play usable; do not infer approval or budget from an
API key. Conditional live smoke, semantic/voice evaluation, detailed billing
reconciliation and wider narration/rules remain open. This delivery makes no
live provider call and does not claim a model benchmark or completed Solo/C2.
Dependency pins remain the coordinator-reviewed 3.4.0 pair below. Joined publication
belongs to the coordinator; this chat pushes only IRGS-APP-WEB.

## Qualified primary-update candidate — 24 October 2026

The App now consumes Engine `8234044c089131314019ecaf6799a2f08028a3f8` and Catalog `401df26a1f16be864dd15d7c5250da5d75f8ccca` for the 3.4.0 development update. The coordinator fixed the Rise status, proposal review and result adapter to use actual settlement receipts and elapsed spans. Five consecutive proposed/accepted actions complete existing shelter work; retry, restart and a lost acknowledgement retain one effect per request. Authored-scene behavior remains qualified separately. Default AI is unconfigured; offline fake transport is not live AI or a general narrator.

Fresh checks: 183 Web tests run, 176 passed, seven Windows PowerShell skips; 86 interface checks; 13 focused authored-scene/Rise bridge tests; actual Chromium Rise round trip with five accepted actions, 3,900 elapsed seconds, reload and lost-response recovery, zero page errors. See [the coordinator primary review](COORDINATOR_PRIMARY_REVIEW.json). Earlier records below retain their original candidate pins and then-pending limits. Exact joined qualification remains a coordinator step.

Target iteration: **IRGS 3.4.0 — in development**. See the active Solo runtime work order and completion plan. Previously qualified versions and evidence retain their recorded identities.

This repository owns `IRGS_Web/`, the local Solo host, interface and catalogue
viewer. Push App work to `KingSav3ge/IRGS-APP-WEB/main`. Follow
[the current work order](COORDINATOR_WORK_ORDER.md); IRGS Enviroment reviews exact
component commits and performs joined integration separately.

## Active priority — 23 October 2026

Complete the AI-assisted Solo player round trip under [the new work order](COORDINATOR_WORK_ORDER.md): editable intention, supported proposal, explicit submit, actual Core outcome, grounded narration and next action. Consume the Engine API with honest unconfigured/error states and protected diagnostics; reuse current request/recovery identities. Engine owns all resolution and provider routing. Historical Details is integrated at the currently committed Engine/Catalog pins; its old approval blockers are resolved. The explicit action review and offline Engine proposal round trip below are implemented. The reviewed runtime supports authored-scene and Rise proposals with explicit offline host configuration; default hosting remains unconfigured and live qualification remains pending.

## Ownership and setup

- `Engine/` pins IRGS-Engine. Simulation, world rules and historical archive
  parsing/verification belong there.
- `Catalog/` pins IRGS-Catalog. Campaign data, designs and the preserved Historical
  Details payload belong there. App provides no second editable content tree.
- Catalogue design: [campaign catalogue](Catalog/IRGS_Catalog/design/campaign_catalogue/README.md)
  and [expanded v0.5](Catalog/IRGS_Catalog/design/catalogue_v0_5/README.md).

Python 3.12+ and Node.js are required; no package installation is needed.

```bash
git submodule update --init --recursive
python3 -B tools/verify_components.py --component app
python3 -B IRGS_Web/server.py --port 8766
```

The host binds to loopback. Use a separate unused development port; keep existing
user campaigns in their original installation. Tests use synthetic records and
temporary saves, never private playthroughs.

## Completed foundations

- [x] Player-filtered Story, World and Chronicle; explicit Creator inspection.
- [x] Reviewed character creation, stable request recovery, campaign Trash and
  restoration, reading preferences and the local launcher.
- [x] Viewer for 44 expanded v0.5 concept previews, 37 scoped Century starts,
  the bounded fictional Rise slice and adopted Kira reference canon. Previews
  remain unreleased; Kira has no playable snapshot.
- [x] Bounded equipment actions, contextual draft suggestions and the optional
  authored opening. General freeform/combat declarations remain unresolved.
- [x] Creator-only historical source search, paging, original records, uncertainty,
  citations and rights; safe text and HTTP(S) links; no source adoption or save
  changes. Existing reference routes and bookmarks remain supported.

## solo-runtime-01 — App review and offline Engine bridge

Target iteration: **IRGS 3.4.0**. Executable Core compatibility remains 3.3.

### Completed

- [x] Listed equipment, authored opening and Rise choices require explicit review.
  Selection and editing commit no effects. Edited words can become an unsent
  draft; a separate response survives cancellation and action execution.
- [x] Optional server-only `SoloConfiguration` connects the selected Engine's
  scoped request builder, broker, ledger and acceptance API. App implements no
  provider router, proposal validator, rules or alternate world state.
- [x] Actor-known input → supported proposal → explicit acceptance → real Core
  outcome → saved actor-legitimate summary/observations → next decision. Exact
  original intention is retained in the Core instruction and public result.
- [x] Stable proposal lookup does not dispatch a new attempt. Accepted results
  reuse current saved-result recovery, including lost acknowledgement, host
  restart and concurrent retry. Save plus public receipt share one flushed,
  atomic replacement under the host writer lock.
- [x] Durable cancellation and restore identities fence late output. Restore
  rotates identity before even an identical-byte Trash restore. Browser review
  also checks campaign, actor, revision, navigation, current draft and request.
- [x] Default host remains unconfigured and makes no provider call. Existing
  structured actions remain usable, unsupported freeform remains unresolved,
  and unsent drafts survive failures. Protected status never exposes credentials,
  route configuration, budget or detailed usage to Player mode.
- [x] Real Chromium offline round trip passed two consecutive Core actions,
  exact editable intent, cancel/edit, provider denial, intentionally lost HTTP
  acknowledgement, saved-result recovery, reload and late-navigation fencing.
- [x] Exact Catalog R00 fixture qualification passed ten structured-handler cases,
  restart/concurrent retry, finite-stock conservation and oracle exclusion.

### Active / remaining

- [ ] Engine's candidate API currently prepares/accepts authored `scene_actions`.
  Catalog's synthetic R00 fixture targets `settlement_runtime`, so the R00
  **interpreted** proposal path remains unavailable. Its structured path is
  tested; App will not implement another executor to bridge that mismatch.
- [ ] Coordinator review and approval of a compatible dependency pair. Pins stay
  Engine `723627e629231b5e90f38b9d52b65c9a3967b92a` and Catalog
  `3e898acb2179f18a41d7967817bedf429df29d3f`. Candidate Engine
  `500ab4286aed5354719a78006195922316b41023` was selected explicitly through
  `IRGS_ENGINE_ROOT`; fixture Catalog `401df26a1f16be864dd15d7c5250da5d75f8ccca`
  was read from exact Git objects into temporary evaluator storage.
- [ ] Engine direct adapter, live credentials/approved route/finite budget,
  semantic and voice evaluation, general dialogue/narrator and wider continuing
  rules. No live model quality or full Solo/C2 completion is claimed.
- [ ] Detailed developer usage view, Windows execution, coordinator's isolated
  joined clean extraction and conditional live smoke.

### Executed evidence (2026-10-24)

Web on reviewed pins: 180 run, 163 passed, 17 skipped (seven Windows launchers;
ten optional Solo API cases require the explicitly selected candidate).
Web on Engine `500ab4286aed5354719a78006195922316b41023`: 180 run, 173 passed,
seven Windows skips. All ten App Solo bridge HTTP cases pass there. Engine's
selected provider API suite: 22 passed. Interface: 85 passed. App tooling: one
passed. Exact Catalog R00 HTTP fixture: ten cases passed. Chromium offline
proposal flow: passed, six fake transport calls, zero live calls or browser errors.
See [coordinator report](COORDINATOR_REPORT.md) and
[structured validation](SOLO_RUNTIME_VALIDATION.json) for scope and commands.

## historical-details-01

### Completed App work

- [x] Name the Creator reference entry **Historical Details**.
- [x] Explain unattached, incomplete, corrupt and unavailable sources separately;
  metadata alone never represents an available archive.
- [x] Retry archive checks, searches and source records without creating a save,
  event, world or player knowledge. Keep literal query and source-row identity.
- [x] Refresh explicit local ZIP registration without restarting the host; a
  broken explicit attachment never silently falls back to another source.
- [x] Reject stale responses after navigation, newer requests or inspector close.

### Completed multipart qualification

- [x] Connect the actual Engine `from_catalog_manifest(path, sha256, cache_dir=...)`
  contract to the Catalog release's exact manifest pin.
- [x] Reconstruct and verify the actual 533,064,680-byte archive from all 32 parts.
  Catalog verification checked all 5,146 files, 5,145 delivery bindings and ten
  collection bindings. The delivery manifest excludes itself from its inventory.
- [x] Search and inspect a real record from each of the ten collections through
  Creator HTTP, preserving original archive/row identity, citations and rights.
- [x] Test missing/corrupt parts, recovery, incomplete metadata, authorization
  before cache assembly and unchanged synthetic campaign saves with the real
  Engine reader. No multipart test double substitutes for those seven HTTP tests.
- [x] Describe the full preserved archive separately from the ten browsable
  collections. Books, assets and the central database remain preserved.
- [x] Exercise the actual full-data Creator UI in Chromium: navigation,
  search/detail/retry and protected deep-link reload; no POSTs or save changes.

### Historical qualification record — superseded by completed integration

The concrete tested dependency pair is Engine
`b3e7d760a2cf3712292b09328566cf1ed0d78c97` and Catalog
`58ce55672bdd75076b94882bd8715a1d2a1f383a`. Engine's candidate has coordinator
scoped checks; the coordinator's published gate still marks source review and
integration approval pending. The completed Catalog source supersedes the
coordinator's earlier blocked-source observation. Do not label a tested candidate
as a coordinator-approved release. Exact dependency selection and joined
integration were subsequently completed at the current reviewed pins. This paragraph preserves the earlier candidate identities; it is not a current blocker.

### Remaining work outside this increment

- [ ] Follow Engine capability delivery with truthful Solo interface states for
  requirements, active work, interruptions and outcomes (shared DEV-25).
- [ ] General freeform/combat adjudication, calendar advancement and the complete
  institutional cycle depend on Engine delivery; C2's 121 requirements are not
  claimed as implemented or passed.
- [ ] Hosted accounts, public hosting, Co-op, the AI network, Workshop and
  Marketplace remain planned or deferred.
- [ ] Coordinator review and isolated joined qualification precede integration
  into IRGS. Only the coordinator publishes joined component updates.

## Verification

After intentional source changes, refresh only App's integrity record:

```bash
python3 -B tools/refresh_component_releases.py --component app
python3 -B tools/verify_components.py --component app
python3 -B -m unittest discover -s IRGS_Web/tests -v
node IRGS_Web/tests/test_gameplay_ui.js
python3 -B -m unittest discover -s tools/tests -v
```

Component verification requires committed dependency pointers to match the
checked-out submodules. Hash refresh establishes source identity, not behavior.
Report test counts and platform skips explicitly. Synthetic DOM checks and
browser checks are separate evidence; neither establishes full archive content
verification or coordinator approval.

### Current increment's executed checks (2026-10-22)

- Web: 166 run, 159 passed, seven Windows PowerShell launcher skips on Linux.
- Interface: 72 checks passed using the synthetic DOM and delayed transport.
- App tooling: one attachment-exclusion test passed.
- Selected Engine historical archive/parts/plans family: 65 tests passed.
- Complete Catalog integrity and package verification passed: 32 parts, 5,146
  files, 5,145 delivery bindings, ten collection bindings, 44 concept previews.
- `tools/qualify_historical_details.py` passed actual archive reconstruction,
  first-row search/detail for all ten collections, six authorization denials,
  cache reuse, unchanged source parts and unchanged synthetic campaign saves.
- Chromium passed the actual Catalog Creator flow with no POSTs, save changes
  or browser errors. Earlier synthetic escaping/retry checks also remain valid.

The full Engine suite, Windows execution and joined package/integration were not
run for this increment. Byte identity does not authenticate historical claims,
expand licenses or adopt campaign facts. See [coordinator report](COORDINATOR_REPORT.md).

## Sequenced AI provider backlog — offline bridge delivered; live integration pending

Read the coordinator's [master-spec addendum](https://github.com/KingSav3ge/IRGS/blob/main/AI_PROVIDER_STRATEGY.md),
[checked research](https://github.com/KingSav3ge/IRGS/blob/main/AI_PROVIDER_REVIEW.md)
and [16 required evaluation cases](https://github.com/KingSav3ge/IRGS/blob/main/provenance/qa/ai_provider_strategy/EVALUATION_CASES.json).
Historical Details is integrated. `solo-runtime-01` is now the active delivery. The existing supported gameplay
and reviewed Engine provider contract precede player integration. The Python host
and JavaScript UI remain; no gateway or framework rewrite has been selected.

| Requirement | App responsibility after Engine delivery | Status |
| --- | --- | --- |
| AIP-01 registry | Protected server-fed developer status; distinguish developer, gateway, host, model and tested workload. | Planned |
| AIP-02 adapter | Unavailable status, protected diagnostics and offline Engine proposal/error bridge delivered; direct/live adapter pending. | Partial |
| AIP-03 specialists | Display the existing six Director categories and logical responsibilities without a second registry. | Planned |
| AIP-04 routing | Consume Engine decisions; no App router or technical routing in campaign selection. | Planned |
| AIP-05 validation | Explicit listed/proposed action review and stale-output fences delivered; strict validation stays in Engine. | Partial |
| AIP-06 ledger | Protected read-only requested/reported identities, finite reservations, reported tokens, failures and unknown usage/charges. No price/billing reconciliation. | Partial |
| AIP-07 evaluations | Report executed versus unrun cases, disclosed human review and measured evidence; no fabricated winners. | Planned |
| AIP-08 migration | Scope, restore, navigation and cancellation fences plus durable previous receipts tested offline. | Partial |
| AIP-09 access | Enforce developer diagnostics and actor information boundaries; never send source data or credentials through browser controls. | Planned |

AIP-S1 begins with disabled-by-default/offline contracts and protected status.
Connect one already supported player action only after its Engine flow is
qualified. Missing credentials, denial/timeout, unsafe output, stale responses and
duplicate submission need checks against the exact selected Engine. Provider
model evaluation cases remain unrun; existing Web tests are not live model
benchmarks. No paid inference, subscription, active narrator or autonomous
Director network is enabled by these plan entries. No Catalog record selects a
model or authorizes external processing.
