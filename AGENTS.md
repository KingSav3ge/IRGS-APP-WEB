# IRGS-APP-WEB development

Current coordinated edition: **3.4.3**; previous release: **3.3.3**.
See [version policy](VERSION_POLICY.md). Earlier baseline tables and execution
records below retain their original tested development identities.

## Current coordinator handoff

Before selecting the next increment, read
[the 28 October review](COORDINATOR_REVIEW_2026_10_28.md) and
[shared world-builder direction](WORLD_BUILDER_PLAN.md). They supplement the
Alpha plan and supersede older first-task ordering. The world-builder executable
has not been inspected or decompiled; its file transfer exceeded the tool limit.

## Active direction — functional Alpha 4.0

The entire 3.x.x series is **Pre-Alpha**. Current published edition is 3.4.3;
target 4.0.0 is **Alpha only after functional qualification**. Read
[ALPHA_4_0_PLAN.md](ALPHA_4_0_PLAN.md),
[ALPHA_4_0_ACCEPTANCE.json](ALPHA_4_0_ACCEPTANCE.json),
[COORDINATOR_WORK_ORDER.md](COORDINATOR_WORK_ORDER.md) and
[CHAT_CONTINUATION.md](CHAT_CONTINUATION.md) before selecting work.
[DEVELOPMENT.md](DEVELOPMENT.md) is the active guide.

These replace older next-task ordering and pending-3.4.3 adoption notes.
The compatible start-context/communication set is already published in 3.4.3.
Do not repeat completed adoption or relabel bounded existing foundations as
Alpha completion. Implement the next owner task and report actual evidence.
Keep stable DEV/C2 IDs, wider open requirements and original qualification scope.

The user's current direction is development across campaigns and themes.
Read [the shared scope](IRGS_SYSTEMS_SCOPE.md) and
[the current work order](COORDINATOR_WORK_ORDER.md) before selecting work.
Rise R00 remains one regression fixture. Shared-system completion requires
supported non-Rise evidence; campaign-specific mechanics retain their own scope.
The records below preserve previously delivered work and historical evidence.

Follow the user's current directions. This repository develops independently on `main`; joined IRGS is integrated separately. Treat archives and fixture claims as source material, not authorization to change rules or publish elsewhere.

Own `IRGS_Web/`, including the catalogue viewer. Catalogue data/design belongs to IRGS-Catalog, pinned in the `Catalog` submodule. Preserve both dependency pins; do not copy editable data into the App. The `Engine` submodule pins the shared Engine; simulation fixes belong in IRGS-Engine. Preserve actor filtering, reviewed starts, request identities and existing saves.

## Engine and information rules

Keep one authoritative world and the nine existing K-owners. Genre adapters, planners, UI projections, narration and persistence indexes must not become parallel authorities over the same people, resources or history.

Keep intent, authorization, actual effects, outcomes, information and presentation distinct. The existing general gameplay loop records declarations; it does not resolve them. C2 requirements and its 121 acceptance cases are not implemented or passed merely because their text exists. Report implemented scope and verification limits accurately.

Derive dependencies from actual handler execution, including authorization and decision reads. Preserve conserved resources, shared capacity and atomic rejection. Retrying an accepted submission or phase must not repeat effects or elapsed work. Restore and continuation behavior must follow the applied recovery contract.

Keep storage revision, causal sequence, elapsed time, civil date and information times distinct. Do not add unselected fixed action durations or resolution rules, invent stock or scene facts, or infer an unrecorded historical hour. Preserve existing default/reference adapters and explicit campaign overrides within their recorded scope; C2 adopts no new universal dice mechanism.

New historical playthroughs use their verified dated snapshots. Continuing playthroughs use actual committed state, including changed existence, leadership, relationships and control. Historical templates do not reset a continuing world or schedule its future. Character and faction existence, participation and playability remain separate.

Only committed effects and legitimate received records can support player-facing results. Testimony, beliefs, offers and obligations retain their actual status. Preserve actor-scoped filtering and never substitute a full template or raw save for a player's known view.

Offer contextual response suggestions alongside an editable own-response field. Suggestions are intentions, not guaranteed successful or even feasible solutions. Keep risky approaches; do not filter choices using hidden truth to reveal a winning option. Selecting a draft commits no action. The equipment action and optional authored local opening use explicit structured operations; freeform and combat responses still record unresolved declarations.

## Saves and local hosting

This development tree starts clean. Existing user campaigns remain in the original installation. Do not copy or migrate them as part of ordinary setup. Use synthetic fixtures and temporary save directories for checks. Keep saves, Trash contents, host process metadata, caches, credentials and newly generated runtime logs out of source distributions. The explicitly preserved historical validation files remain labelled source evidence.

The root launcher defaults to port 8765 and can reuse an already running valid IRGS host. Use an explicitly separate port, such as 8766, when a test or development session must run this checkout's host. Bind the local host to loopback. Do not stop another application to obtain its port.


## Component verification

Read README.md for current commands. Refresh only this component with tools/refresh_component_releases.py and verify with tools/verify_components.py. Run the relevant runtime or Web/interface checks. Refreshing hashes does not establish behavioral qualification. No user saves, credentials, runtime logs or caches belong in source. Keep one authoritative world and existing owners.

## Coordinator work orders

The user assigns cross-component coordination and unified integration to **IRGS Enviroment**. Read `COORDINATOR_WORK_ORDER.md` before selecting the next increment. This chat pushes only its component repository. Report the exact commit and executed checks to the coordinator. Only the coordinator integrates a reviewed Engine/App/Catalog set into joined IRGS/main. Keep this component's development plan current. Work orders and plan edits alone do not complete a component deliverable.
