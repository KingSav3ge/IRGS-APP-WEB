# App communication and received-source bridge — 26 October 2026

The App consumes Engine `irgs-communication-capabilities-1` at
`cc450a6f00a249d2169cdacdfc9c4b1e03f67cc8`, retaining Catalog
`e1778e080385b6ff2bbb93f47f91d0da6e9d6780`. Edition remains **3.4.2**,
previous release **3.3.3**, Core compatibility **3.3**. This is the bounded
communication increment following the delivered start-context adoption.

## Player flow and information boundary

Story has an expandable **Communication & received sources** section in both
the generic and Rise interfaces. Channels, participants, attributed sources,
received offers, structured terms and role-dependent commands come from the
Engine actor view. Actor names require an existing received identity; otherwise
the received actor reference is shown. The App does not scan a raw roster or
current private presence, stock, mandates or obligations to choose a menu.

The editable exact words and structured command are independent. Speak records
testimony; saying “I accept” under Speak accepts nothing. Offer/counteroffer
terms require explicit account, material, positive whole quantity and authority
references. They are proposed terms, not stock reservations or authorization.
Counteroffer reverses the received account references for editing and leaves the
new authority reference blank. Each preparation shows its exact command, words
and terms in the existing review dialog. Editing retains a communication draft
and requires a fresh review; the independent own-response draft is preserved.

Accept attempts Engine's actual conserved transfer. Offer, fulfilled, declined,
withdrawn and superseded retain their distinct received meanings. A committed
App command has `status=completed_successfully`; its nested `communication.status`
is the actual Engine result. The interface labels that nested status. The
original proposal result stays offered after a later acceptance; the latest
received offer view and message describe the subsequent closure.

Exact source text is escaped and rendered as text, including literal HTML.
Sources retain testimony status, attribution, separate original/reception
references and causal coordinates. Native explicitly attributed records use the
Engine DTO. The App's `source_projection=app-receipt-compatibility-1` conservatively
preserves its older boundary for unattributed legacy receipts: a different
original source and occurrence metadata are withheld, while the received copy's
reference, words and recorded/received coordinates remain available. A shared
original/receipt reference can still be shown. No source or save is rewritten.
Forwarded words do not reveal the original audience, structured terms, digest or
rights. Private typed communication records require an actual participant.

## Host, acceptance and recovery

`GET /api/playthrough/<save>?actor_id=<actor>` includes `communication_control`
and an actual command count in live readiness. The existing authenticated host,
Host/Origin checks and shared store writer lock protect all endpoints:

| Endpoint | Purpose |
| --- | --- |
| `POST /api/communication/prepare` | Effect-free immutable preparation |
| `POST /api/communication/status` | Recover own preparation or original result |
| `POST /api/communication/execute` | Explicitly accept that exact preparation |
| `GET /api/communication/received/<save>/<request>?actor_id=<actor>` | Read own received native message |
| `GET /api/action-result/<save>/<request>?actor_id=<actor>` | Retrieve the durable original App result |

Preparation binds the explicit actor, save, storage revision, opaque view token,
stable request identity, channel, recipient, command, exact words and typed
details. The host supplies new offer identities and source references; browser
scope/native requests are rejected. Only boolean `true` is acceptance. Pending
unresolved declarations block new commands. Changed actors, navigation, changed
received capabilities and stale preparation tokens cannot confirm old reviews.

`CommunicationService` reuses the process host's private scope/journal plumbing
in its own `.host/communications.sqlite`; it owns no Core facts. Engine executes
against a detached candidate and requires a persistence callback. The callback
checks the current revision/scope and atomically saves the candidate world and
exact App result together, with file/directory synchronization before acknowledgment.
Original results are returned before stale-state/re-execution checks. Uncertain
directory synchronization is completed before result recovery acknowledges it.

The browser retains the original preparation body before sending it, allowing
lost preparation acknowledgments, reload and effect-free same-identity retries.
Accepted transport uses existing original-result recovery. Restart, concurrent
requests, failed saves and identical/older Trash restores retain their fences.
Restore rotates private scope even when campaign bytes are identical. The
shared Process and optional Solo restore callbacks remain chained.

## Tested scope and content dependency

[Fresh attributed evidence](COMMUNICATION_BRIDGE_VALIDATION.json) records exact
sources, executed results and remaining dependencies. Test-only selections use
a non-Rise quay testimony channel and an R00 free-stock transfer channel. The
R00 fixture explicitly assigns several characters to the human for actor-boundary
checks; it simulates no NPC decision or multiplayer behavior. The published R00
gameplay/draft adapter remains founder-only. Other controlled actors receive
generic known views and their own communication capabilities, without founder
inventory or actions; unavailable Engine draft adapters retain local fallbacks.

Normal pinned initializers do **not** yet select these communication channels
and introductions. Their empty controls remain explicit. Product code adds no
fixture, introduction, authority grant or communication rule to a new/continuing
campaign. Engine/content selection is still required to make communication
available in those ordinary starts. Source reads never initialize or repair saves.

Speech has no selected elapsed rule. Causal sequence, storage revision, local
elapsed seconds and civil time remain separate. Communication adds no duration,
calendar progress, NPC choice, automatic dialogue or model inference. Existing
local Engine/Catalog/App receipt rendering needs no API token. Broader freeform,
combat and historical operational starts remain outside this delivery.

Reproduce with synthetic temporary stores only:

```bash
python3 -B -m unittest discover -s IRGS_Web/tests -v
node IRGS_Web/tests/test_gameplay_ui.js
node IRGS_Web/tests/test_responses.js
python3 -B -m unittest discover -s tools/tests -v
node tools/qualify_communication_bridge.js /tmp/irgs-comm-browser.json /tmp/irgs-comm-shots
node tools/qualify_start_readiness.js /tmp/irgs-comm-starts.json /tmp/irgs-comm-start-shots
node tools/qualify_shared_responses.js /tmp/irgs-comm-shared.json
node tools/qualify_process_bridge.js /tmp/irgs-comm-process.json
node tools/qualify_interface_port.js /tmp/irgs-comm-port.json /tmp/irgs-comm-port-shots
node tools/qualify_interface_refinement.js /tmp/irgs-comm-refinement.json /tmp/irgs-comm-refinement-shots
python3 -B tools/verify_components.py --component app
```

The communication browser starts the canonical loopback host on a free port in
an empty temporary fixture store and shuts down only its own child. It checks
all six commands, exact words, source/actor filtering, lost prepare/execute
acknowledgments, independent drafts, reload, 390px layout and conserved stock.
The existing five browser suites retain start, phase, theme, reading and recovery
coverage. Raw logs/screenshots remain outside source; the attributed JSON is
source evidence. Native Windows and live providers were not exercised.

Next bounded App task: protected operator/launcher configuration for the existing
optional Solo service, keeping credentials/accounting server-side and ordinary
supported play available without a provider. Supported-intent mapping and
non-secret build diagnostics follow. Catalog's separate adopted-App start
consumer and the coordinator's exact-set/joined/browser/package qualification
remain their owners' work. Push only App; do not prepare a unified release or
increase the edition in this increment.
