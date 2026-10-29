# Supported communication intent adoption

This A4-APP-03 increment consumes the pinned Fulcrum Engine's
`irgs-supported-intent-1` communication review, prepare and result methods.
The existing communication capabilities still supply actor-received participants,
commands and terms. Words and structured selection remain independent; the App
adds no parser, NPC decision, stock, authority, elapsed duration or civil hour.

## New requests and explicit review

The communication projection advertises `intent_schema_version`. When that
version is available the UI posts its exact words and explicit selection to
`/api/communication/intent/prepare`. The authenticated host rejects browser-supplied
scope, sources, review IDs or new offer IDs. It binds the current revision and
private restore scope, supplies the offer identity when needed, calls Engine
`review_communication`, and retains its actual public review.

`unsupported` and `clarification_required` responses create no native request or
campaign effects. The UI keeps both independent drafts, shows the actual status,
and requires changed selection/terms to be reviewed again. A supported review
is not a promise of success. The host uses `prepare_communication` to bind the
same exact selection and stores the native request privately. The public packet
includes `intent_review`; the UI verifies actor, words and complete selection
against that packet before confirmation. Object key order does not change terms.
The review includes received attribution and the selected channel source.

Explicit boolean confirmation uses the existing `/api/communication/execute`.
For these new rows the host calls `execute_communication`, validates the actual
versioned result against the actor/request, and atomically saves it as
`intent_result` alongside the original communication, App result and Core
candidate. The actual receipt status stays distinct: testimony, offered,
declined, withdrawn, superseded and fulfilled retain their meanings. Engine
control, presence, current authority and resource checks remain authoritative.
Only a controlled recipient may explicitly accept; no NPC consent is inferred.

## Recovery and compatibility

The prepare route is retained with the local unaccepted review. A missing prepare
reply/reload retries the same route, body and identity. A lost execute reply
uses the existing durable original-result lookup. The nested DTO is preserved
in that result and never reconstructed from a newer world. Restart, persistence
failure, directory-sync uncertainty, stale selection and restore continue through
the existing host journal, writer lock, scope rotation and atomic CAS behavior.

`/api/communication/prepare` remains compatible. Old prepared rows have no review
marker and execute through the original Engine communication method. Old accepted
results return unchanged. Request signatures distinguish the two prepare
contracts; a prepared identity cannot be silently reinterpreted across them.
The UI recovers older local review records on the original route. No campaign
migration or private-save inspection occurs.

## Qualification and remaining work

Focused HTTP tests exercise supported/unsupported/clarification, exact wording,
boolean confirmation, result persistence/restart/retry after later work, legacy
pending/committed recovery, contract identity mismatch, origin/token checks,
source/scope rejection, atomic persistence failure, restore and actual presence
refusal. The ordinary browser journey creates a non-Rise quay-contact opening
and an optionally offer-enabled Rise world through normal UI; it submits actual
versioned testimony and an offered proposal, with independent draft reload and
no stock transfer or NPC consent. The selected-fixture browser journey separately
covers all six communication commands, conserved transfers and lost replies.
The Story journey retains chronological entries, choices/composer placement and
mobile layout. These are synthetic temporary campaigns, with no live inference.

Scene/settlement shared-intent execution retains its existing contract. Grant
prerequisites, world-draft preview/editor, general text interpretation, broader
NPC/institution decisions and the functional Alpha gates remain open. Windows
protected setup stays unavailable pending native ACL implementation/testing;
live-provider quality requires a separately authorized eligible route and finite
budget. The App remains 3.4.6 Pre-Alpha; the coordinator owns the next qualified
joined edition, 3.4.7. Engine and Catalog pins are unchanged.

See [validation evidence](COMMUNICATION_INTENT_ADOPTION_VALIDATION.json) for exact
source, dependency identities and executed checks.
