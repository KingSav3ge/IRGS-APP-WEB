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
