# WorldWard: protected operator setup and reviewed intentions

This App increment follows the 3.4.5 Pre-Alpha baseline. It keeps the selected
Engine and Catalog gitlinks and the chronological Story surface. The player-facing
working brand is **WorldWard**, developed by **T!DEMARCH Studios** and powered by
**Fulcrum Engine**; IRGS remains the internal project/repository name. The user
has made this the leading naming direction subject to commercial clearance.

## A4-APP-01: explicit local setup

A trusted operator can select a server-only profile using `--operator-config` or
the non-secret `IRGS_OPERATOR_CONFIG` path. [Setup instructions](IRGS_Web/OPERATOR_SETUP.md)
describe the exact required fields. The profile is a private, owner-controlled
regular file outside the source tree and campaign saves; its separate private
technical directory holds the existing Engine reservation ledger and scope data.
On POSIX, ownership and permissions are checked. Windows fails closed to offline
mode until native ACL handling is implemented and qualified.

Validation uses the pinned Engine's `SpecialistRegistry` and the reviewed direct
OpenAI adapter: exact model snapshot, adapter, proposal schema, workload,
operator-approved classification and selected operations; finite input/output,
concurrency, deadline, reservation and lifetime budget; and explicit policy,
approval, configuration and price-ceiling references. A CLI check validates
without starting a host, dispatching, reading a credential or making a ledger.
An invalid profile or unavailable ledger leaves the host usable offline. A missing
or malformed server credential, exhausted reservation budget or full concurrency
prevents a new proposal. The secret is read server-side from `OPENAI_API_KEY` and
never placed in the profile, browser, response, URL, save, logs or ledger.

The player sees a non-secret readiness message, including that a requested proposal
sends their words and received context to the provider and uses a reservation.
Creator status displays only the fixed selected model, workload, operations and
bounded readiness code; inspecting it does not dispatch. The existing Engine
broker still performs per-request route eligibility, context filtering, durable
reservation, identity/output validation and no-retry recovery. The operator's
ceiling units are not verified provider prices or an automatically enforced
currency bill. A running/reused host keeps its startup configuration until it is
restarted. Creator is a local-owner workspace, not multi-account authentication.

## A4-APP-03: explicit supported-intent review

The App consumes `irgs-shared-runtime-1` Engine capabilities for the selected
actor. The response composer lets the player explicitly choose one supplied
capability, including the unresolved declaration capability, independently of the
editable words. Selecting a draft or capability does not submit or infer an action.
Review shows exact words, actor/known place, actual operation and selected action,
received source references and any supplied action requirements/time description.
Editing the reviewed text retains it as a draft and requires fresh review.

The authenticated host prepares Engine `AcceptedIntent` using its own branch,
restore scope and current world. The immutable request lives in a private host
journal; browser-supplied scope or source is rejected. Explicit boolean acceptance
calls the Engine's shared execution and atomic host CAS, saving the actual world
and public original result together. Lost prepare/execute acknowledgements,
restart, duplicate requests, rejected or stale attempts and restore are fenced or
recover the original result. A selected unresolved declaration remains pending
and withdrawable; it never becomes a resolved outcome. The existing direct
response and action paths remain available. This is explicit selection, not a
natural-language intent classifier or a mapping from arbitrary prose to actions.

The implementation uses one Core and the Engine's existing scene, settlement and
declaration adapters. It does not infer hidden stock, presence, source facts or
NPC decisions. Continuous oldest-to-newest Story, received status and source gaps,
inline choices, draft retention and existing phase/communication recovery remain.
The ordinary browser journeys start from an empty temporary store, create a
non-Rise fictional opening and a Rise campaign through normal reviewed UI, and
perform an actual reviewed action in each without a provider. Separate selected
fixture journeys exercise lost preparation/commit acknowledgements and reload.

## Remaining scope

A4-APP-01 has a working POSIX profile and bounded offline-synthetic transport
path. Native Windows profile ACLs, account/model availability and live-provider
quality require separate qualification and an explicitly authorized finite live
budget. A4-APP-03's explicit selected-capability path does not implement automatic
text-to-intent interpretation, arbitrary freeform/combat resolution, autonomous
NPC decisions or the wider Alpha gameplay gates. The Engine and coordinator own
future supported-intent contracts and joined exact-set/package review. User saves,
credentials, personal configuration, live inference and native Windows were not
used in these checks. No version increase or Alpha qualification is implied.

See [validation evidence](A4_OPERATOR_INTENT_VALIDATION.json) for exact source,
pins, executed checks, skips and test boundaries.
