# IRGS App/Website work order — solo-runtime-01

Assigned through IRGS Enviroment on 23 October 2026 following the user's direction to complete the systems needed to run IRGS. Owner: **IRGS App/Website**. Push only to `KingSav3ge/IRGS-APP-WEB/main`.

## Baseline and priority

Reviewed integrated App: `d8dc35ed653e516ccd0cacf91ee9693258491032`. Its reviewed dependency pins are Engine `723627e629231b5e90f38b9d52b65c9a3967b92a` and Catalog `3e898acb2179f18a41d7967817bedf429df29d3f`. Historical Details is integrated; the previous work order is preserved in `COORDINATOR_WORK_ORDER_HISTORICAL_DETAILS_01.md`. No archive payload or coordinator pin input is missing for that completed work.

Read the coordinator's [Solo completion plan](https://github.com/KingSav3ge/IRGS/blob/main/SOLO_COMPLETION_PLAN.md). Complete the player round trip against the Engine-owned provider/action contract. Keep the existing Python host and JavaScript interface and current reviewed campaign behavior.

## Implementation

1. Preserve the player's editable exact intention and existing submission/recovery identities. Display unconfigured, pending, denied, failed, unresolved and committed outcomes honestly. Missing AI configuration must leave supported existing actions usable and retain unsent drafts.
2. Consume Engine's scoped provider/action API. Build truthful unavailable/error handling and protected developer diagnostics while Engine implements its API; do not invent a second provider router or simulator. For candidate qualification, select exact Engine/Catalog snapshots explicitly; commit dependency pointers only for a reviewed compatible pair.
3. Wire actor-known input → interpreted supported proposal → explicit player acceptance → Core execution → durable outcome → grounded narration → next action. Choosing or editing a suggestion commits no effect. Show the accepted action and its actual status separately from provider prose. An unsupported freeform/combat declaration must remain unresolved.
4. Keys, provider configuration, budgets and detailed usage stay server-side behind existing Creator/developer permissions. Keep ordinary campaign controls focused on player decisions. Escape provider text and reject stale responses after navigation, state change, restore, newer requests and inspector closure. Source text is display data, never executable instructions.
5. Reuse current lost-acknowledgement, reload, Trash/restore and duplicate-submit recovery. A provider error cannot trigger an implicit fresh paid attempt or repeat an accepted Core effect. Preserve current player/Creator information boundaries and actor-scoped views.

## Required evidence

Use the reviewed synthetic scenario from Catalog and the real selected Engine handlers. Execute two consecutive supported actions, editable intent and cancellation before submit, denied/unsupported actions, provider absence/denial/timeout, a lost acknowledgement, concurrent retry, restart/restore and stale output/navigation. Verify actor-hidden evaluator data never reaches player rendering or request payloads. Run Web/interface regressions and a real browser round trip; report Windows/platform skips accurately.

The full flow may use fake provider transport for offline integration, with that scope explicit. Live AI play is a separate conditional check requiring configured server credentials, an eligible exact model and finite budget. No live credentials are required to implement and test the App flow. Hosted accounts, purchases, Co-op, Marketplace and extra viewer sections are queued behind this runtime delivery.

## Delivery and coordinator review

Work in your own component repository on `main`. Preserve existing work and adopted content. Return the exact pushed commit, changed executable behavior or validated test content, tested dependencies, executed checks, skips, remaining requirements and live prerequisites to **IRGS Enviroment**. Update completed, active and remaining work. Documentation and hash-only changes are not a viable runtime delivery.

The coordinator reviews an actual Engine/App/Catalog update set, checks exact App pins and tests an isolated joined candidate before integrating product source. No previous-cycle approval applies to a new commit. Test with temporary synthetic saves only. The original Historical Grand Archive remains exact, and no private campaign or reference payload is sent to a provider by this work order.

The coordinator can read these chats and publish repository work orders but has no direct chat-start/send tool. This file is the assignment; publication does not claim that your chat was resumed. The QA monitor tests pushed source, not development activity.
