# Published Engine start-context adoption — 26 October 2026

The App consumes Engine `cc450a6f00a249d2169cdacdfc9c4b1e03f67cc8` and
Catalog `e1778e080385b6ff2bbb93f47f91d0da6e9d6780`. This implements
START-INT-002/003/004 and selects the compatible pins for START-INT-005.
The coordinator's import/discovery fix is retained: App modules are
`start_preview.py` and `tests/test_start_preview.py`, distinct from Engine's
`start_readiness.py` and test module.

## Explicit person and mode

`starting_selection.starting_options` supplies the Engine
`irgs-start-readiness-1` metadata and person-bound `existing_character_openings`.
The optional `henry-1415-embarkation-v1` option is offered only for Henry V at its
matching snapshot. Its public description, requirements and review state the
broad setting, citations, uncertainty, exclusions and selected observation rule.
An unselected existing context stays unselected. Changing person/perspective or
closing the wizard clears the old opening and consent.

Authenticated `GET /api/starting-preview` calls Engine `review_start`, then its
actual new-world initializer in ephemeral memory. The result retains App schema
1 counts and adds `engine_start_context_contract=irgs-start-readiness-1`,
`engine_review` and the resulting `start_context`. Unknown Engine schemas and
unavailable/held sources cannot authorize a final UI review. Creation validates
the complete options digest again through Core; the preview grants no authority.
Names and background testimony stay out of preview URLs and remain unchanged in
the original actual creation body. Existing-person opening IDs are passed to
Engine validation instead of receiving the old blanket App rejection.

The selected `opening_id` is present in preflight, review, creation and retained
retry bodies. John, default Henry and a new character without an opening still
require deliberate declaration/reference consent. Neither an eligible identity
nor a verified snapshot implicitly installs a situation. A changed actor cannot
borrow Henry's context or the fictional courier setup.

## Received context and separate clocks

`playthrough.start_context` comes from Engine's read-only actor view over saved
state. The App display snapshot uses the save's branch ID and a display-only
scope marker; it is never an action acceptance/recovery token. Existing execution
and process APIs retain their private restore scope and persistence checks.
No current view calls an initializer or loads historical templates to repair a
world. Diverged locations, missing receipts and legacy unknowns remain as saved.

`campaign_time.civil` is projected only from that actor's legitimate received
calendar record, with its source, Julian date, day precision, unknown hour,
`received_initial_checkpoint` status and `current_calendar_binding=false`.
Raw `campaign_time.civil` or a historical template cannot substitute for the
receipt. The UI labels the date **Received initial checkpoint**, explicitly
separating local elapsed seconds from a running civil clock. Original relative
campaign-day fields remain separate in the export.

Henry's scene uses the Engine's sourced-setting classification and received map
text. His actual operation is `observe-embarkation`: one selected local
observation. The known view and new opening guidance do not supply a dispatch,
courier travel, exact berth/vessel occupancy, hour, health, stock, troops,
institutional mandate, private contacts or historical future. Opening guidance
lists actual offered actions. New-character fiction retains its separate pack.

The elapsed projection requires the currently received/controlled selected scene
and its actual selected axis. New accepted action receipts use Core's saved
elapsed axis, including `selected-historical-observation-seconds`, rather than
the old hard-coded fiction axis. Henry's twenty local seconds do not advance the
civil checkpoint. Retrieval/replay returns the originally persisted receipt
before testing current revision or re-executing work. Older saved receipts and
opening presentations are not rewritten during a read.

## Qualification and remaining work

[START_CONTEXT_ADOPTION_VALIDATION.json](START_CONTEXT_ADOPTION_VALIDATION.json)
records fresh execution and exact sources. The three earlier Web failures now
assert the exact legitimate calendar receipt and preserve exclusion of unsourced
scene, resources, authority, personal contacts and historical future. The new
HTTP cases also test lost-source behavior, actor denial, changed replay rejection,
diverged state, unreceived date, and byte-preserving reads/restores.

The normal-host browser suite starts from an empty temporary store. It covers
explicit Henry, default Henry, John, default new, authored new and R00, with
390px layout, source failure, changed choices, cancelled review, lost creation
and action replies, exact original results, reload, Trash/restore and actor
boundaries. The four existing interface/shared/process suites remain in use.

```bash
python3 -B -m unittest discover -s IRGS_Web/tests -v
node IRGS_Web/tests/test_gameplay_ui.js
node IRGS_Web/tests/test_responses.js
python3 -B -m unittest discover -s tools/tests -v
node tools/qualify_start_readiness.js /tmp/irgs-adopt-browser.json /tmp/irgs-adopt-shots
node tools/qualify_shared_responses.js /tmp/irgs-adopt-shared.json
node tools/qualify_process_bridge.js /tmp/irgs-adopt-process.json
node tools/qualify_interface_port.js /tmp/irgs-adopt-port.json
node tools/qualify_interface_refinement.js /tmp/irgs-adopt-refinement.json
python3 -B tools/verify_components.py --component app
```

Catalog's separate new-contract consumer and coordinator exact-set/joined/package
review remain pending. Henry's one observation is a bounded start, not general
historical campaign resolution; John and other held contexts remain held.
Communication UI/HTTP, protected operator setup, supported-intent mapping and
non-secret build diagnostics remain later App work. No user save, live inference,
Windows launcher execution, general freeform/combat or full C2 completion is
claimed. App remains 3.4.2, previous release 3.3.3; the coordinator owns the next
unified 3.4.3 publication.
