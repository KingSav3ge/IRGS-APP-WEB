# App routine responses 1.0.0

App-owned presentation content: **171 variants in 55 families**, comprising
139 system variants and 32 editable draft starters, with eight composition
recipes. Content lives in `static/responses.data.js`; `static/responses.js`
validates and freezes it once at browser intake and formats plain text locally.
`static/routine.js` binds it to the existing actor-filtered App projection and
current UI/recovery state. There is no provider request, model prompt, inference
router, simulator or editable duplicate of Catalog content in this layer.

Ordinary App labels/status messages already used local strings. This change
formalizes and expands that path; it does not claim measured production token
savings over a paid-message baseline. Only an explicit request for assisted
interpretation uses the existing Engine provider capability. A missing template,
missing fact or unsupported mechanic cannot authorize an automatic paid fallback.
Existing literal interface labels are also local and require no model tokens.
The complete response library is never included in a provider prompt.

## Active mappings

- Composer readiness, pending/unresolved intent, missing/unavailable actor and draft status.
- Listed-action/proposal review, edited intent, pending/unknown/unavailable review.
- Accepted-result notices and Story outcomes, withdrawal, uncertain delivery and saved-result recovery.
- Campaign loading, creation, branch, Trash and restore acknowledgements.
- Protected usage inspection and read-only/unknown-charge explanations.
- Eight generic draft families: clarification, options, observation, explanation,
  help, preparation, consideration and declining for now. Each has four authored
  starting texts. Existing Engine-authored contextual suggestions remain available.

Draft starters require a current available player character. Opening one reviews
its words without changing an independent composer draft. The player may edit,
cancel or explicitly keep the exact words in the composer. Keeping submits
nothing; the existing declaration/acceptance procedure is still required.
No starter grants permission, guarantees feasibility, creates an NPC response,
advances elapsed time or resolves freeform mechanics. Stale actor/campaign,
revision, navigation and request generation prevent copying the old review.

## Formatting and composition

Every frame supplies `actor_id`, `snapshot_id`, `source_ref`, `source_kind`,
`state` and `values`. The App constructs these from the already authorized public
projection, actual result or its own public UI state. No browser/provider context
is accepted as server authorization. The formatter is a presentation validator;
Core and existing host authentication remain authoritative.

Source kinds and public states must match the family. Only declared named scalar
slots are allowed: bounded text/labels or nonnegative safe integers. Expressions,
attribute/index lookup, format conversions, missing fields, extra values and
invalid quantities fail validation. Inserted text is replaced once, so braces
inside received text stay literal. Use `textContent`, textarea `value` or the
existing `esc()` layer; formatted text is never executable HTML.

Recipes combine at most eight complete clauses. All pieces must share the actor
and snapshot, use consistent values for the same source and avoid contradictory
states. System prose and player drafts cannot mix. Two drafts cannot be combined
into a new player decision. Missing required facts fail; optional clauses are
included only when the caller actually has their facts.

Committed-result recipes require `receipt.exact`, whose only variant is the
verbatim public Core `outcome.summary`. Story may append the actual action's
recorded duration when it is present and valid, including zero. Missing duration
is omitted; no fixed time, calendar hour, resource, physical success or project
completion is inferred. Notices retain the exact summary. Actual result objects
and persisted saves are never rewritten. Oversized/unavailable formatting still
preserves the exact receipt as local text rather than replacing it with stock
success prose. Older receipts never append current-world facts.

Variant choice is deterministic by library/language, family, actor and source
identity. Re-render/reload of an event retains its wording. The current UI frame
also binds campaign/revision, a session nonce and request generation; restore or
navigation invalidates an old review. There is no personalized message cache,
cross-actor cache, raw-save context, private state hash or external storage.

## Recipes

| ID | Required clauses | Optional clauses |
| --- | --- | --- |
| `result.exact` | Exact Core summary | None |
| `result.elapsed` | Exact Core summary, recorded action seconds | Neutral next choice |
| `result.next` | Exact Core summary, neutral next choice | Recorded action seconds |
| `request.rejected` | Actual public rejection text, draft-retention notice | Inspection reminder |
| `recovery.uncertain` | Saved-result check guidance | Inspection reminder |
| `review.local` | Explicit listed-action review | Inspection reminder |
| `draft.kept` | Exact draft-copy acknowledgement | Inspection reminder |
| `usage.local` | Unknown-charge explanation, read-only refresh | None |

## Verification

```bash
node IRGS_Web/tests/test_responses.js
node IRGS_Web/tests/test_gameplay_ui.js
node tools/qualify_app_responses.js /tmp/irgs-app-responses-browser.json
python3 -B -m unittest discover -s IRGS_Web/tests -v
```

The 13 formatter checks render all 171 variants and all eight recipes, including
scope/role conflicts, malicious format expressions, bad quantities, immutability,
receipt negation, HTML/braces, line breaks, zero time and missing-template behavior.
Seven new interface checks cover draft review/edit/cancel/keep, stale views,
restoring real-action confirmation, deterministic rerender and local fallback.
Actual Chromium uses a temporary synthetic Core campaign with provider endpoints
blocked. Four real actions include an unsuccessful attempt, an HTML-like quoted
receipt and a deliberately lost acknowledgement. Drafts survive reload; Core's
43 elapsed seconds and original outcomes remain intact. Provider calls: zero.
Playwright/Chromium are test dependencies only. Nothing establishes live model
quality, general dialogue/narration or full C2 completion.


## Reviewed shared-system adapters — 25 October 2026

`local_presentation.py` consumes the selected Engine's offline runtime and the
Catalog `irgs-response-depot-v1` schema-2 source. The App verifies the release-bound
Catalog formatter/library hashes and loads their authored content once; no
editable Catalog copy or personalized render cache is introduced. The App-owned
171-variant pack remains responsible for UI/help/recovery messages.

Every player projection has `local_responses` schema 1:

- `scope`: App campaign ID, authenticated selected actor, current save revision
  and a fresh opaque `view_id`. A refresh/restore/navigation must not reuse an
  old draft review, including restoration of identical save bytes. This identity
  is presentation metadata, not a world hash or a new campaign authority.
- `drafts`: Catalog semantic intents with only legitimately visible labels and
  Engine-associated authored/settlement draft choices. Each has a stable ID,
  title, plain text, source, explicit-submission flag and `automatic_execution: false`.
  Generic Catalog intent tags carry no operation binding. Engine associations
  are informational; copying their words never dispatches that operation.
- Library/runtime identities and zero-call local-render metadata. These details
  are contract fields, not technical routing controls in ordinary gameplay.

Current Catalog mappings are `player.look_around`, `player.wait`, and
`player.observe`/`player.inspect` when a valid public current-location label exists.
They do not manufacture people, destinations, resources or missing facts. Other
Catalog families remain available content, not automatically qualified adapters.
Engine drafts are selected from actual Engine options and matching public controls;
appearance/theme bindings cannot create options. The same review/Keep path handles
App, Catalog and Engine drafts. A changed view scope blocks an old contextual draft.

Native authored-scene, equipment and settlement result writers, and optional
proposal acceptance, now retain a `presentation` beside the original outcome in
the same atomic save. Engine owns complete authorized receipt/observation text;
Catalog's exact-receipt recipe preserves it. Older results without this metadata
keep their existing literal/App rendering and are not migrated or rewritten.
Unsupported receipt adapters and absent text libraries retain the exact public
literal receipt with no inference fallback. Missing Engine executables themselves
are not certified by this presentation fallback.

`presentation` is plain text bound to the actor and actual receipt event ID.
Accepted duplicates, lost acknowledgements, restart and Trash/restore retrieve the
saved original wording without appending current-world facts. The common latest
result panel handles both authored scenes and Rise. It uses the prepared text
without adding a second elapsed clause. Core's original outcome fields remain
unchanged; notices retain their original summary. Engine's settlement adapter
omits a per-action duration when its receipt does not establish one; actual host
zero spans remain zero. No new calendar hour or physical-project completion is inferred.

Reproduce the shared browser qualification with:

```bash
python3 -B -m unittest discover -s IRGS_Web/tests -p test_shared_responses.py -v
node tools/qualify_shared_responses.js /tmp/irgs-shared-responses.json
```

Nine focused HTTP checks cover independent authored-scene and settlement worlds,
real action effects, exact complete receipts, non-submitting drafts, absence/fallback,
actor separation, forged-context rejection, saved replay/concurrent retry, restart,
restore and four-theme label portability. The latter proves content portability
only. Real Chromium uses ordinary play without provider configuration: four
non-Rise actions (43 seconds, including an unsuccessful attempt) and five settlement
actions (3,900 seconds, including actual zero spans and shelter work completion).
Both use the same response schema and latest-result UI, deliberately lose an
acknowledgement, retain drafts over reload and close stale reviews on navigation.
Inference calls and browser errors are zero. No new fantasy/space/modern mechanics,
general narrator, unsupported freeform/combat rules or universal C2 completion is claimed.
