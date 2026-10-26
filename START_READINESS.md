# App start preflight — 26 October 2026

The selected person and start are checked before the final creation review.
Historical reference readiness and character eligibility no longer imply an
executable situation. A start with no executable actions or process starts needs
an explicit **declaration / reference** choice. Back permits a different character
or an explicitly selected fictional opening; nothing chooses a courier setup for
an actual historical person.

This bounded App delivery addresses the presentation/selection parts of
IRGS-PLAY-001/002/006. It does **not** deliver the missing Engine initializer or
make John/1415 executable. The versioned Engine start-context/readiness contract
and Catalog's independently selected start cases remain dependencies. The current
App preflight will need an explicit adapter/qualification when those are published.

## Current public host contract

Authenticated `GET /api/starting-preview` accepts the existing profile, entry,
snapshot hash, starting scenario and Engine selection digest, plus:

- `character_kind=new`, species, and an optional explicit `opening_id`;
- `character_kind=existing`, and the eligible `actor_id`;
- `character_kind=faction`, and its actual entity/representative IDs.

The same player/Creator campaign access boundary as creation applies. Unknown or
duplicate fields are rejected. Personal names and background testimony stay out
of this URL and are preserved in the original reviewed creation body. They grant
no capability; their additional setup records may change causal sequence numbers,
which are not promised by this preflight.

The host uses the pinned Engine's **current** `initial_campaign` and
`initialize_player` in ephemeral memory, then the existing App actor-filtered
`playthrough` and Engine `phase_contract.actor_view`. It never executes an action,
writes a campaign, calls a provider, reserves a budget or touches a continuing
world. Returned scene fields come from this selected view. No private feasibility
scan or historical template-to-player knowledge copy is added.

App schema version 1 reports `preview_only`,
`engine_start_context_contract=false`, and `basis=current_actor_view`.
`supported_slice` means at least one current executable action choice or process
start; it does not promise success. `declaration_only` means both counts are zero.
Source failures or inconsistent packets cannot open the final review. Changes,
cancel, Back and workspace switches invalidate late preflight replies.

The live playthrough's `play_readiness` uses the same counts, with distinct
`pending_declaration` and `unavailable` states. Story and the Tools sidebar explain
the actual empty state, including the unresolved-intent/withdraw path. Assistance
status no longer promises listed actions when no list exists. Missing assistance
never triggers paid fallback.

The explicit reference checkbox governs the normal UI review; it is not a new
Core permission or a replacement for the existing creation API. Retained creation
requests preserve their exact body and stable identity. A lost acknowledgment is
recovered before different choices can create another campaign. Existing action,
process, save, restore and original-result recovery contracts remain in effect.

## Checks and limits

Fresh results are in [START_READINESS_VALIDATION.json](START_READINESS_VALIDATION.json).
The normal-host browser qualification starts with an empty temporary store and
uses actual Library/character/founding controls. It covers existing John/1415,
deliberate new-character reference use, a new human with the fictional quay and
R00. John remains explicitly unsupported for execution; the positive operation
claims belong to the actual authored and R00 handlers.

```bash
python3 -B -m unittest discover -s IRGS_Web/tests -v
node IRGS_Web/tests/test_gameplay_ui.js
node IRGS_Web/tests/test_responses.js
python3 -B -m unittest discover -s tools/tests -v
node tools/qualify_start_readiness.js /tmp/irgs-start-browser.json /tmp/irgs-start-shots
node tools/qualify_shared_responses.js /tmp/irgs-start-shared.json
node tools/qualify_process_bridge.js /tmp/irgs-start-process.json
node tools/qualify_interface_port.js /tmp/irgs-start-port.json
node tools/qualify_interface_refinement.js /tmp/irgs-start-refinement.json
python3 -B tools/verify_components.py --component app
```

The interface suites now explicitly choose reference use for their historical
new-character fixtures. Their original non-submitting setup, saved-byte, mobile,
focus, contrast and local-asset assertions are retained. Screenshots, raw logs
and temporary host metadata stay outside source. No user save, private fixture,
native Windows launcher, live model, full C2 or general freeform/combat qualification
is claimed. Current edition remains 3.4.2; only the App is published for review.
