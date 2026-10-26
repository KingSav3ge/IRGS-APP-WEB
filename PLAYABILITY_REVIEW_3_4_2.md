# IRGS 3.4.2 playability assessment — 26 October 2026

The coordinator ran unified `ba551af285a6e1eb0766a9d06f83cbc0e5335b35` through
the normal canonical host with an initially empty temporary campaign store, actual
Chromium UI and public HTTP requests. This assessment implements the user's request
to run IRGS, evaluate necessary work and update the three development chats.
It changes no game rules and imports no user save. The supplied known-view export
was a diagnostic reference; its contents are not republished or treated as a save.
See [executed evidence](PLAYABILITY_EVIDENCE_3_4_2.json).

## Findings

| ID | Priority | Reproduced behavior | Required work / owner |
| --- | --- | --- | --- |
| IRGS-PLAY-001 | P0 | John of Lancaster at 1415 starts with no received scene/location and no executable actions or process starts. One eligible existing character tested at each of all 37 historical entries has zero such controls. | Engine: reviewed start context and explicit playability contract. App: consume it before creation. Catalog: source requirements and independent cases. |
| IRGS-PLAY-002 | P0 | A new character using the default no-authored-opening choice also enters a declaration-only campaign. Final review does warn about unresolved intent, but selection does not distinguish the readiness of the chosen actor/mode. | App: explicit playable-slice versus declaration/reference choice. Engine publishes capabilities; content titles or snapshot readiness cannot supply them. |
| IRGS-PLAY-003 | P1 | A submitted own response becomes `declared_not_resolved`; it survives reload and can be withdrawn. In a working authored campaign it suppresses three listed actions until withdrawal, with no outcome or elapsed-time effect. | Engine/App: extend actual selected handlers and reviewed intent mapping. General freeform resolution and NPC decisions remain open. Preserve honest unsupported results. |
| IRGS-PLAY-004 | P1 | Even the working authored historical opening displays campaign day 0 with unresolved civil time; its local elapsed seconds work. | Engine/App: a sourced initial civil-date/precision contract and separate elapsed/calendar presentation. Do not invent an hour or a universal action duration. |
| IRGS-PLAY-005 | P1 | Engine communication/source/offer capability tests pass, but the normal App has no corresponding communication bridge/controls. | App: authenticated actor-scoped prepare/review/accept/recovery over the delivered Engine contract, then Catalog consumer qualification. |
| IRGS-PLAY-006 | P1 | Normal hosting has no configured assistance. The generic “listed actions remain available” message also appears when the actual list is empty. | App: capability-specific empty-state messages and protected operator configuration using existing routing/budget contracts. An API key alone is not completion of playability. |
| IRGS-PLAY-007 | P2 | Public Core identity reports 3.3 and known-view exports provide no App/coordinated build identity. Core 3.3 is correct for this edition. | App: non-secret process/build identity in diagnostics/exports so stale hosts or installations can be distinguished. Preserve existing Core compatibility fields. |

The survey covers **one eligible existing actor per entry**, not every actor/date
combination. Missing items in a player view are unestablished knowledge, not proof
that the authoritative world has no corresponding people, assets or resources.

## Working behavior observed

- Normal UI: a newly created human with the explicitly selected fictional quay
  opening completed observation, failed shortcut, movement and delivery: five
  committed actions, 150 local elapsed seconds and dispatch quantity 1 to 0.
  Reload retained the revision; the 390px layout fit.
- Normal UI: reviewed R00 founding supported walk/found/build/two wait requests,
  completing 3,600 shelter-work seconds at 3,900 elapsed seconds, with timber 6 to 3.
- In the working authored campaign, typing “I look around” saved an unresolved
  declaration and changed the executable action list from three to zero. Reload
  retained it; withdrawal restored all three actions without changing elapsed time
  or inventory. The missing intent-to-supported-operation path affects playable
  contexts too. This observation is not a desired behavior to freeze into tests.
- The Kira guide opened as reference with no start button. All 44 concept cards
  remained previews; content presence did not create a campaign capability.
- Separate synthetic browser regressions passed nine shared actions and eleven
  observation/work phases, including zero spans, failed outcomes, explicit review,
  saved results, lost replies, reload, stale navigation and pause/resume.
- Eight independent HTTP mechanics checks and 32 Engine communication capability
  cases passed. All evaluated browser flows had zero page errors and zero provider
  calls. The three-second observation fixture is separate from the normal quay's
  20-second observation rule; neither becomes a universal duration.

Earlier full-suite results (740 Core, 229 Web, 128 interface) belong to the 3.4.2
release review. They were not rerun or relabelled as new execution here. No native
Windows, live AI/model-quality, faction-start or full C2 qualification is claimed.

## First coordinated delivery

Prioritize a complete supported path from reviewed character selection to a
legitimate starting view, explicitly confirmed operation, received result and
save/reload continuation. Existing historical characters and new characters need
distinct reviewed setup; the fictional courier setup cannot be silently attached
to an actual historical person. If evidence or mechanics are missing, classify
that selected start honestly and offer reference/declaration mode explicitly.

Engine publishes the versioned readiness/start-context contract and a bounded
implemented start. App consumes it and prevents an unlabeled dead end. Catalog
adds sourced requirements and separately versioned positive/negative consumer
cases. Freeze the contract before final App pins and qualification. Keep the
working authored opening and R00 as regressions; demonstrate the new existing-
character path as a third distinct case. Do not narrow IRGS development to Rise.

Opening prose must remain presentation. Do not fix initialization by inventing
facts in `opening_scene.py`, copying the entire historical template into player
knowledge, adding NPC decisions or granting rank-based resources automatically.
Only actual source-backed initialization and authoritative Core operations create
state. Preserve testimony, uncertainty, actor access, authority, conservation,
separate time axes and atomic persistence. Continuing games must not be reseeded
or reset; any future repair requires a separately reviewed continuation contract.

## Reproduce the critical path

Run the actual host against an empty temporary store. In Library choose Century
of Conflict, 1415, review the historical start and select existing John of Lancaster.
Confirm creation; inspect scene, received records and supported actions. Submit
“I look around and ask where I am”, reload, then withdraw. Separately create a new
human with no authored opening, then another with the explicit quay opening and
execute its listed actions. A successful supported action must retain its exact
receipt and actual duration; an unsupported declaration must not invent either.
Repeat with independent actor inputs/evaluator expectations and fresh source pins.

## Publication scope

These are work orders and evaluation evidence at current edition **3.4.2**,
previous release **3.3.3**. They are not implemented fixes or a new unified release.
Only the three component instruction repositories are updated by this assessment.
Unified source and its qualified pins remain at the published baseline. The next
unified main publication must increase the version and qualify a viable all-three
product set. Do not repin old fixture manifests, refresh product hashes for prose,
publish user campaign data or claim that a repository push started another chat.
