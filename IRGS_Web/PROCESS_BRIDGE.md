# Received process controls

The common Story controls continue **existing** Engine processes. Qualified
contexts are the non-Rise authored observation and Rise shelter work. The host
uses the pinned Engine's `process_runtime.prepare`, `ProcessRequest` JSON,
`execute`, `received_status` and `WorldScope` contracts. It supplies no scheduler,
duration, work rate, stock, knowledge rule or provider dispatch.

## Player behavior

Story shows the selected actor's last received phase, original intention, status,
worked seconds and remaining seconds. This is received progress, not a live feed
of remote work. An explicit local **Inspect** can obtain a fresh Core receipt.
The published command candidates include pause/resume, cancellation where the
kind permits it, and advancement with a player-entered positive whole number of
seconds. Current control, place, commitments, permissions and selected rules are
checked by Engine on execution. Candidates do not certify feasibility.

Choosing a command prepares it without changing the campaign. The review shows
the exact intention and requires confirmation. Editing it disables execution;
the edited words can instead be kept as an ordinary draft. Canceling the review
executes nothing. A phase may commit successfully while its parent process is
still active, paused or held; Story labels the phase and actual process status.
There is no automatic next phase, fixed time button or background clock.

Preparation survives a lost reply and reload through **Recover reviewed process
command**. Confirmation uses the existing saved-result recovery path. The same
phase ID, original result and prepared wording survive duplicate submissions,
concurrent retries and host restart. An unsent composer draft remains separate.
Navigation, actor/campaign selection, revision and restore changes fence reviews.

## HTTP and persistence

All endpoints require the existing loopback Host/Origin/session checks and an
explicit owned actor. They run under the same `Store.lock` as every campaign
writer within the existing single-owning-host contract for a save directory.
Distributed writers are outside this qualification. Browser/provider scope,
source references and serialized typed commands
are rejected. The server owns the source reference, phase ID and typed scope.

- `GET /api/playthrough/{id}?actor_id=...` adds `process_control` schema 1:
  actor-filtered received phases, published command candidates, an opaque
  `view_token` and `start_available: false`. Raw world hashes and restore IDs are
  never sent to the player. No process capability is selected by a theme.
- `POST /api/process/prepare` accepts exactly `id`, `actor`, `revision`,
  `view_token`, `request_id`, `process_id`, `command`, `details`, `intention`.
  Advance takes only `details.seconds`; other commands take empty details.
  The actor, revision and current opaque guard must match. The response contains
  the immutable public command, identity and review status. Retrying identical
  fields returns the original preparation; identity reuse with changed fields
  fails. Preparation does not resolve a phase or update the campaign revision.
- `POST /api/process/execute` accepts exactly `id`, `actor`, `request_id`,
  `explicitly_accepted: true`. It loads the private stored `ProcessRequest`;
  browser-supplied execution details are never trusted.
- `POST /api/process/status` accepts exactly `id`, `actor`, `request_id` and
  returns that actor's prepared/stale/rejected/save-failed status or saved result.
- `GET /api/action-result/{id}/{request_id}?actor_id=...` retrieves the accepted
  original through the common result API without advancing work.

Private requests and restore identities persist in `saves/.host/processes.sqlite`
with SQLite full synchronization and restricted creation permissions. This is
excluded runtime metadata, outside Core world records and nonrecursive campaign
listings; it is not shipped, exported as player context or a second world owner.
It contains no provider credential or inference ledger. Each supported restore
rotates its identity before renaming the save, even for identical bytes. It also
preserves the optional assistance service's separate restore hook. A new branch
gets its own identity. Direct external file replacement/import is not supported.

The Engine persistence callback compares actual campaign/branch/restore digest
and App revision again, then saves the candidate Core world and complete App
result together through the existing fsynced atomic replacement. Failed saves
leave no in-memory Core effects. A failure after replacement is uncertain;
recovery reads the saved original, completes directory synchronization before
acknowledging it, and never repeats the phase. Private bounded failure statuses
do not disclose dependency reads or hidden rejection facts. Older snapshots
without the accepted result cannot reuse a pre-restore pending command.

Each saved result retains the public received `process` fields, exact Core
summary, actual elapsed span/axis/total and complete authorized Engine/Catalog
local presentation. Observation knowledge appears only on actual completion.
Zero elapsed phases remain zero. Physical projects, reservations, stocks and
material boundaries remain in Engine's existing records. Old response records
and the verified-byte Catalog intake are preserved.

## Dependency and qualification boundary

Engine `2f9476c6090878257d17cab3ad3a83a7ce18a5dc` publishes typed process
execution and received status, but no player-safe **start capability discovery**
contract. Before the App can offer starts, Engine must publish actor-authorized,
sourced kind/action choices tied to the actual selected elapsed binding and
scope, with command/detail semantics that do not disclose hidden feasibility.
The App must not infer those choices by scanning private rule dictionaries or
mapping genre/theme names. No start endpoint or button is delivered here.
Tests initialize processes explicitly through the real typed Engine API as
trusted synthetic fixture setup; this does not qualify a player start flow.

Travel retains its published Engine rules (including unavailable cancellation),
but the new App qualification names observation and work only. Communication
controls, broader capability discovery, protected operator/launcher configuration
and fresh coordinator joined qualification remain separate work. The previously
qualified shared-response integration remains completed.

Run the ordinary guide checks plus:

```bash
python3 -B -m unittest discover -s IRGS_Web/tests -p test_process_bridge.py -v
node tools/qualify_process_bridge.js /tmp/irgs-process-browser.json
```

The HTTP cases execute actual Core effects with temporary independent worlds,
including no premature observation, pause/resume, cancellation, competing work
boundaries, failed persistence, concurrency, restart, restored branches, actor
filtering, received versus live progress and durable recovery. Chromium uses both
contexts, lost preparation and execution replies, review cancellation, reload,
stale navigation and a 390px Story viewport. Inference is forbidden throughout.
