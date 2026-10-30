# WB-APP-01: bounded Creator draft and playtest handoff

Status: Proposed. Evidence: source inspected through the GitHub connection on
30 October 2026. No runtime code, tests, dependency pins or release metadata are
changed by this handoff. The execution environment failed to start; no new
Python, browser, filesystem-durability or gameplay qualification was run.

## Current selection and reconciliation

- App: `75ccc9aa7b746f23e1d2c86dc0464c48858469e5`.
- Engine gitlink: `7f4ef150e2049c7718ac600680cb9c3633353a6a`.
- Catalog gitlink: `fae1ab8709049d3f76a0121bfd15731a29c203b5`.
- Current coordinated edition: 3.4.7 Pre-Alpha. The coordinator owns the next
  qualified joined edition, 3.4.8. Functional Alpha gates remain open.

The current App work order supersedes the earlier grant-control task: optional
offer setup, versioned communication with legacy recovery and separate grant
request/acceptance controls are delivered within their recorded scope. The next
task is disposable Creator draft preview and explicit durable playtest creation.
This handoff does not repeat those completed deliveries.

The Design Studio supplies design context and handoffs. Its separate
Deus-Lo-Vult repository workflow does not relocate WorldWard runtime work.
Implementation belongs in WORLDWARD-APP-WEB; Core initialization stays in the
pinned Engine and canonical content stays in Catalog. Dated Studio catalogue
decisions are not fresh campaign qualification.

## First implementation slice: preview only

Use existing Creator navigation `workshop`, `campaign-builder` and
`playtest-validation`. Keep unsupported map, entity, package, marketplace and
commercial controls planned. Basic ordinary character creation remains outside
this feature.

Offer only the profiles supported by the inspected Engine:

- `rise-r00` with `classification: fictional` and actual
  `settlement_setup.preview` choices, including an independently selected
  optional offer profile.
- `historical-quay` with `classification: mixed`, the exact selected
  `snapshot_sha256`, and a new human choosing `quay-contact-v1` or
  `quay-contact-decision-v1`. Historical setting and fictional actor/context
  remain separately labelled; the unknown historical hour remains unknown.

Consume the exact `irgs-world-draft-1` fields:
`schema_version`, `draft_id`, `classification`, `profile_id`, `choices`.
Do not add guessed map, resource, actor, script or time fields.

Proposed App routes, not published APIs:

| Route | Required behavior |
| --- | --- |
| Creator draft load/save | Owner-scoped independent drafts with an expected revision; a conflict preserves both the current server record and the editor's unsaved words. Draft storage is separate from campaign state. |
| `POST /api/creator/drafts/preview` | Authenticate existing session/Host/Origin and explicit Creator access; bound and validate data; call `world_draft.preview_initialization`; return its actor-filtered preview. |
| Future create/status routes | Remain unavailable until the creation boundary and acceptance gates below are implemented and tested. |

Display field-level validation, actual classification/source, selected rules and
known initial actor view. Show **Preview only — no campaign saved**. Preview
identities, snapshots and capabilities cannot authorize actual creation or later
actions. Refreshing or cancelling preview publishes no campaign or receipt and
does not alter any ongoing world.

The current source has no draft routes. Creator authorization is the existing
`local_owner_creator_opt_in` model; it is not multi-account authentication.
A new endpoint must explicitly call the Creator guard as well as the common
session/Host/Origin checks. Neither a request ID nor a review digest grants access.

## Durable creation: design requirements before enabling the button

Use the Engine's DRAFT_HOST_ATOMIC_CONTRACT.md as the implementation obligation.
Publish a concrete App DTO before wiring a create control.

1. Bind a stable request ID to the server-derived authorized owner, exact draft,
   draft/review digests, explicit boolean acceptance, intended campaign and
   host-assigned branch/restore identities. Never accept owner identity, sources
   or authority from browser input. IDs must never become filesystem paths.
2. On a genuinely new request, recheck authorization, source/rule digests and
   campaign absence before calling `world_draft.initialize`. Do not reuse the
   preview candidate. A retained matching receipt is recovered before trying a
   new initializer or substituting a later world's view.
3. Publish initialized Core state, ownership/access, stable request fingerprint,
   initial scope metadata and the original actor-scoped result as one coherent
   durable creation. No second simulation or resource authority is introduced.
4. Prefer evaluating a complete single campaign-record envelope against the
   existing atomic Store pattern. Do not scatter ownership, creation receipt and
   publication state across independently committed files/databases. This is a
   proposed storage strategy; current Store.write alone does not prove that the
   full contract, principal binding or restore integration is satisfied.
5. Record the original public creation result once. After lost reply, restart or
   later play, retry the identical bound payload and return that same receipt
   without another initializer, effect or write. Changed fields under the same
   prepared/accepted request are a safe conflict.
6. Preserve receipts, authorization and deletion/tombstone policy through backup
   and restore. A retry must not recreate a trashed/deleted campaign or reopen a
   discarded future. Fresh gameplay uses current scopes and its existing
   action/communication identities, not historical creation identities.

Keep the player's exact Story and communication drafts independent of Creator
drafts. Only after confirmed creation should **Open playtest** obtain the actual
controlled actor's current projection and enter the existing chronological Story.
Choices and the retained response stay below the latest entry.

## Two issues requiring Engine/coordinator reconciliation

**Durability uncertainty.** Store.write flushes/fsyncs a temporary file, replaces
the active path, then syncs its parent directory. An error at the last step can
occur after the complete record is already visible. Do not report guaranteed
rollback or invite a new creation ID in that case. Define a distinct
confirmation-pending outcome and same-request durability recovery, or implement
an alternative publication mechanism that demonstrably meets the stricter
no-visible-campaign-on-failure wording. The Engine host contract needs this case
clarified before durable playtest support is claimed.

**Public versus private restore identity.** The host contract asks for a creation
result identifying the initial branch/restore scope. Existing bridges keep their
restore identity private and derive browser guards from it. A public creation
receipt must not expose that internal secret. Specify a separate opaque
historical public handle, keep the real guard private, and rebind current action
scope after restore. The historical receipt must never masquerade as current
submission authority. Obtain contract-level agreement on this representation.

Neither proposal changes the Engine contract or constitutes accepted new policy.
Keep durable create disabled until these boundaries are resolved and qualified.

## Observable acceptance gates

1. Both selected profiles validate and preview through the real authenticated
   host and ordinary Creator controls. Unsupported profiles, scripts, excess
   fields and stale snapshot/rule digests reject with actionable errors.
2. Draft edit/save/reload, conflict, back and cancel preserve unsaved words and
   create no campaign effects. Ordinary player requests cannot use Creator routes.
3. Preview contains only controlled-actor information, actual receipt/source
   status and supplied time precision; no raw world or hidden records escape.
4. Preview IDs cannot be used as real campaign/action authorization.
5. Explicit create publishes one complete tuple and a fresh independent Core
   world. Concurrent identical requests yield one campaign and identical result;
   altered payloads, collisions and unauthorized lookup fail without disclosure.
6. Inject failures before and after each durability boundary, including parent
   sync and process interruption. Prove definite rejection versus uncertain
   confirmation and original-result recovery; no half-published tuple.
7. Exact retry after lost response, restart and later actual play returns the
   original initial actor view, not a recomputed current view.
8. Trash, delete, backup and restore preserve the stated retention/ownership
   policy. Discarded-future submissions are fenced; no implicit re-creation.
9. Play each created profile using actual supported actions, speech or selected
   refusal, finite resources where selected, a failed prerequisite, save and
   reload. No privileged fixture repair enters ordinary instructions.
10. Preserve legacy saves, communication requests/results, independent drafts,
    actor filtering, source statuses, chronological Story and mobile layout.
    Run component integrity and independent Catalog consumers against exact pins.

Test execution, Windows ACL work, live-provider quality, arbitrary world
authoring and Alpha qualification remain open. No provider belongs in preview
or the atomic creation transaction.

## Inspected sources

- https://github.com/KingSav3ge/WORLDWARD-APP-WEB/blob/75ccc9aa7b746f23e1d2c86dc0464c48858469e5/CHAT_CONTINUATION.md
- https://github.com/KingSav3ge/WORLDWARD-APP-WEB/blob/75ccc9aa7b746f23e1d2c86dc0464c48858469e5/COORDINATOR_WORK_ORDER.md
- https://github.com/KingSav3ge/WORLDWARD-APP-WEB/blob/75ccc9aa7b746f23e1d2c86dc0464c48858469e5/IRGS_Web/server.py
- https://github.com/KingSav3ge/WORLDWARD-APP-WEB/blob/75ccc9aa7b746f23e1d2c86dc0464c48858469e5/IRGS_Web/features.py
- https://github.com/KingSav3ge/WORLDWARD-APP-WEB/blob/75ccc9aa7b746f23e1d2c86dc0464c48858469e5/WORLD_BUILDER_PLAN.md
- https://github.com/KingSav3ge/Fulcrum-Engine/blob/7f4ef150e2049c7718ac600680cb9c3633353a6a/engine/DRAFT_HOST_ATOMIC_CONTRACT.md
- https://github.com/KingSav3ge/Fulcrum-Engine/blob/7f4ef150e2049c7718ac600680cb9c3633353a6a/IRGS_3_3/runtime/world_draft.py
