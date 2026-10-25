# IRGS local website

IRGS uses Core 3.3 as one campaign-state kernel. Genre engines supply domain rules, content libraries supply references, and campaign profiles select them. Player campaign discovery is separate from installed technical and legacy library assets.

## Start and continue

Double-click `Start-IRGS.cmd` whenever you want to play. It uses the canonical `IRGS_3_3/Start-IRGS-3.3.ps1` launcher to verify the release, start the local host in the background if needed, and open http://127.0.0.1:8765 in your default browser. You can close the launcher window; IRGS keeps running. Opening it again reuses the existing IRGS host without duplicating it. Another application using the port receives a readable error and is left running. A new version is not required to launch the site.

Use `Start-IRGS.ps1 -NoBrowser` for a launch/reuse check without opening a browser, or `-Port` for an explicit alternative port. Startup logs and process metadata are in `IRGS_3_3/live/`, separate from campaign saves. No third-party Python packages are required. Do not use Python's `-O` flag: the engine relies on assertions for validation. In joined IRGS, keep `IRGS_3_3/` beside `IRGS_Web/`. In the standalone App repository, initialize the pinned `Engine` submodule with `git submodule update --init --recursive`; the App loads `Engine/IRGS_3_3/`. `IRGS_ENGINE_ROOT` can explicitly select another Core directory for qualification.

The site starts in **Player view**. Story, World and Chronicle inspect one saved campaign through server-filtered views for the selected controlled character. Searches, inspections, settings and starting-point selections make no world changes. Existing saves are read without automatic migration.

Story preserves exact declarations and received records. Character, Inventory, Relationships, Map, Projects and Institutions show supplied records or explicit unknowns. Possessions, quantities, skills, locations and faction powers are not filled from an illustrative narrative. Known people are not automatically nearby people, and no map is fabricated without an authorized atlas.

The preferred visual design comes from the top-level frontend in `IRGS-3.3.2.Emergent.zip`: warm dark surfaces, cream type, rubricated and bronze accents, framed cards and large campaign headings. The local Solo app uses its top navigation, expandable section drawer and character/context plus reading columns. Smaller screens use compact navigation and a context drawer. This is a visual port onto the existing Core host; the archive's separate Mongo simulation, hosted login, store, AI and voice services are not connected. App/Web and Engine/Core develop in their independent repositories; the selected executable Core remains 3.3.

Reading settings control font, size, line spacing, width, parchment/light/dark surfaces, mechanical detail and reduced motion. Dark is the default for new users; previously chosen reading surfaces remain. Preferences, bookmarks, unsent drafts and view scroll positions stay on this device, without world effects. Enter adds a line; Ctrl/Cmd+Enter submits by default. Optional Enter-to-submit retains Shift+Enter for new lines.

## Create a Solo campaign

**New playthrough** opens the player Content Library, which currently lists only the Hundred Years’ War. Choose a verified entry, then follow Campaign → Starting point → Character → Review. The clicked entry and exact snapshot hash are retained and rechecked; there is no fallback to another profile or date. No campaign file is written until **Start campaign** on the final review. Back and Cancel submit no creation request and advance no time. An earlier unconfirmed Start request may already be saved.

Choose an eligible existing person or create a named character with an explicit species (initially human). A quick name/species start is sufficient. Optional guided fields separately record origin, birthplace, nationality, culture, family, upbringing, education and career intent. Independent, mercenary, retinue, civilian, institutional and undecided arrangements remain separate from control perspective. A dated organization may be mentioned without granting acceptance, recruitment access or control. Reported offers, current positions and membership are unconfirmed testimony, not hiring or contracts. These fields create no relatives, property, skills, money, equipment or authority. Existing characters are not rewritten by new-character fields. Own received background details are shown as testimony in Character inspection.

Review the selected person, starting point, individual control and reference provenance. The final review also explains that this build can create campaigns, inspect records and preserve declarations, but general freeform resolution and calendar advancement remain unavailable. The optional authored opening alone advances its selected local elapsed seconds through listed actions. Equipment-order execution requires actual received orders, control, authority and established stock; setup supplies none of these automatically. A Start request retains one identity and exact choices if its acknowledgement is lost. **Check / retry campaign creation** recovers the same campaign without duplication. A campaign subsequently moved to Trash stays there; retry does not restore it. Unconfirmed requests are retained locally across reloads.

### Historical starting points

**The Hundred Years’ War** uses the Military genre with a dated campaign library. Featured years are 1337, 1360, 1369, 1389, 1415, 1422, 1435, 1444, 1449 and 1453. All 37 catalogue entries can be inspected and searched. All 37 entries now have distinct supported creation snapshots. The preserved 1415 opening keeps its 11 August cutoff; the other 36 use their individually authored 15 December Julian cutoffs. Structural qualification does not authenticate every historical statement. No nearby year is substituted for a missing snapshot.

The developed opening is **11 August 1415, Julian calendar, before departure**, with day precision and unknown hour. Review its detailed “Before you start” guide, political/military/territorial/diplomatic records, actors, unknowns and source links, then choose a character. Creation sends the exact reviewed snapshot hash and availability digest for server validation.

Briefings are out-of-character setup references, not automatic player knowledge or a forced new-character location. A Scot’s Tale is a named 1415 scenario reference, with launch disabled pending reconciliation of its checkpoint civil date. It is not an independent public campaign card or a separately selectable new profile. Existing legacy saves remain resumable without migration or redating. Creator workspace retains an **Opening reference** separately from current campaign facts. Live availability reads the saved current registry, never a historical template or reset year. An unavailable character retains their identity and history; no replacement is automatically chosen.

For newly created historical games, **Your opening** is a separate actor-scoped presentation built only from the selected character and legitimately received records. Testimony keeps its actual status. This presentation does not manufacture a Chronicle event, nearby person, scene location, dialogue, movement or outcome. For an unplaced start the first declaration remains pending intent. New human characters can instead explicitly select **A dispatch before departure** in the optional opening field: a fictional local delivery scene with real movement, observations, blocked attempts, conserved dispatch transfer and saved local elapsed seconds. Listed actions resolve; own freeform words remain intent. The final review explains the authored circumstances and durations. Existing saves and historical figures are untouched.

## Declarations and Chronicle

The freeform composer needs no technical source fields. Submission records exact intent with a stable request identity. A persisted `declared_not_resolved` attempt is not a narrated outcome. The saved-intent message explicitly states that freeform declarations cannot be resolved yet; it is not a processing indicator. While that declaration remains pending, another action cannot be submitted. An unsent draft remains editable. **Withdraw pending attempt** explicitly releases that intent for revision, retaining the original record without changing resources or time.

**Suggested responses and your own answer:** explicitly received contextual prompts can offer draft responses beside **Write your own response**. Selecting a suggestion fills the editable composer without sending it. The player can edit the words or write a different answer. Choices may fail, carry risks or prove unsuitable; the menu does not certify feasibility or reveal hidden odds. Combat suggestions require a received combat prompt and remain unresolved intentions. No encounter, elapsed time or successful action is created by displaying or choosing a draft.

**Equipment orders:** a controlled character can explicitly attempt a received structured issue order. The host rechecks actual control, scoped authority, recipients and conserved stock through Core. Choices are received instructions, not guaranteed successes. A valid action atomically saves real transfers, an outcome and a receipt. Retry/reload retrieves that result without repeating effects. Failed checks leave the save unchanged and expose no private validation reason. A separate unsent draft survives execution, and a completed action permits the next action.

After a lost acknowledgement, the UI checks the saved action result before retrying the identical request. It retains the draft and request identity across reloads. A failed connection does not silently become a fresh action.

Chronicle searches personal, biographical, relationship, institutional, timeline and archive records within the selected access scope. Original text, statuses, sources and supplied occurrence/observation/transmission/receipt/recording times retain their meanings. Missing source text is marked without a reconstructed transcript. Calendar boundaries and summary budgets remain unconfigured until committed. Inspecting history generates no summaries or epochs.

A general narrator, general action resolver and elapsed-time advancement are not connected. Visible time controls explain this and remain disabled. Supplied dates and precision are preserved; a causal event counter is not treated as elapsed time or a year advance.

## Creator workspace and management

Navigation comes from a role-filtered registry after session initialization. Registered child sections have individual deep links and support reload and browser history. Planned, scaffold and deferred pages explain their status without invented records, balances or working controls. Fetch failures show a readable retry. Requesting a development visibility stage does not grant access to Creator or developer sections.

**Creator workspace** explicitly enables full records and sourced host tools. Only this mode fetches raw campaign state, full source-library lookups and full-save exports. Returning to Player view requests a fresh filtered projection. **Export known view** exports that projection alone. Reading library references does not adopt them as campaign facts. Creator technical initialization remains available for non-archived internal profiles; these are not public campaign listings.

Creator-only Historical Comparison / Historical Inspector separates the immutable sourced baseline, read-only prospective assessments and explicit actual occurrence links. Execution, calendar-driven scheduling and outcome resolution remain unbound. A historical date or plan never establishes a campaign occurrence, and no future-plan data is fetched into player Story, context or Chronicle.

Creator tools record sourced characters, capacities, activities, scenes, evidence, inventory, obligations, designs and orders. Every event uses dependency observation. Invalid single events save no revision; simultaneous conflicts retain unresolved intent. Scoped mandates and approve/deny decisions recheck current state. The tools do not supply unsupported automatic physical or narrative outcomes. **Branch** creates an independent persisted copy and requires Creator mode.

Choose **Delete → Move to Trash** to remove an accidental branch or another campaign from the active list. Exact save bytes move into `saves/trash/`. **Campaign Trash → Restore campaign** returns the full history, pending requests and revision. Trash survives host restart. There is no permanent delete or overwrite on restore. Keep separate save backups; no import UI is provided.

## Local hosting and verification

The host binds to 127.0.0.1, checks Host/Origin, uses a per-process token for private views and writes, and checks revisions for mutations. Raw campaign/binding routes and legacy editor writes require explicit Creator mode plus token. Public hosting, accounts and Co-op are not implemented; this release is Solo only.

Player routes include `/api/playthrough/{id}`, `/api/action`, `/api/declaration`, `/api/withdraw-declaration`, `/api/action-result/{campaign}/{request}`, `/api/chronicle/{id}` and `/api/availability/{id}`. Setup uses `/api/starting-options`, `/api/historical-campaigns`, `/api/historical-entry/{id}` and `/api/create`. Existing management envelopes and Creator event/frontier/mandate/resolve/fork/reference routes remain supported.

Run `python -m unittest discover -s tests -v` from `IRGS_Web` for HTTP, gameplay, history and starting-flow tests. Run `node IRGS_Web/tests/test_gameplay_ui.js` from the project root for frontend transport, selection, setup and routing checks. It uses artificial campaign records, mocked transport and the actual read-only feature registry; it never opens a real save or starts a server. A Python runtime is used only to load that registry (override with `IRGS_TEST_PYTHON` when necessary).


## Campaign portfolio and independent development

The App owns the viewer for 44 catalogue concept previews. Catalogue records and discovery configuration belong to the pinned `Catalog/IRGS_Catalog/data/` dependency. All new concepts remain unreleased; existing Century dated starts and the fictional Rise founding slice retain their reviewed workflows. Kira v0.5 is an adopted, searchable world reference without a playable snapshot. See [catalogue scope](../Catalog/IRGS_Catalog/design/campaign_catalogue/README.md).

App source integrity is recorded in `IRGS_Web/release.json`, separately from the Engine. Run `python -B tools/refresh_component_releases.py --component app` after intentional App edits, then `python -B tools/verify_components.py --component app` and the relevant Web/interface tests. Independent development uses `KingSav3ge/IRGS-APP-WEB/main`; joined `KingSav3ge/IRGS/main` retains both components.


## Historical Details — Creator reference

The Creator navigation entry **Historical Details** retains the existing
`#/historical-reference-library` bookmark and `/api/historical-reference` routes.
It is absent from Player navigation. All reference endpoints require the current
local session token and explicit Creator mode, including status and retry.
Browsing, literal search, paging and source-record inspection cannot initialize a
world, adopt history, submit an event or change a campaign save.

An explicit local source attachment remains supported:

```bash
python3 -B IRGS_Web/register_historical_archive.py /absolute/path/to/IRGS_Historical_Grand_Archive_v1_1.zip
```

Run this from the repository root. Registration records the chosen ZIP and its
SHA-256 in ignored `IRGS_Web/cache/reference_sources.json`; it does not copy the
archive into source. The host reloads registration on the next reference request.
An invalid explicit attachment is reported rather than silently substituted.
Empty, unavailable and failed-verification states offer **Check again**. Search
and source-detail failures offer their own retries. Source text, uncertainty,
original row identities, citation and rights records remain reference material.
The default source is the pinned Catalog's
`historical_details/manifest.json`, using its exact SHA-256 from Catalog's release
record. Engine verifies/reconstructs all parts into ignored
`IRGS_Web/cache/historical_details/`; App never copies an editable content tree.
An explicit ZIP registration takes precedence, including when it is broken.
The complete archive includes books, assets and its central database, while the
browser exposes ten structured collections. Preservation and reading establish
no new historical truth, license, campaign fact or player knowledge.

Run `python3 -B tools/qualify_historical_details.py --output /tmp/irgs-app-qualification.json`
from the repository root to repeat actual full-archive HTTP qualification. It
uses temporary synthetic saves/cache and reports exact dependency commits,
source hashes and collection probes. Catalog's own
`historical_details_package.py verify` checks every source member and binding.
See [development status](../DEVELOPMENT.md) for executed evidence, coordinator
review and the sequenced AI provider backlog.


## Solo action review — 3.4.0 development

Listed equipment, opening and Rise choices now open a review before submission.
Canceling or editing changes no world state. **Confirm and submit action** invokes
the same existing Core operation and durable request recovery. Editing the listed
wording disables that structured confirmation; **Keep as editable draft** copies
the exact words into your response without sending them. A separate response
already being drafted survives confirmation or cancellation.

The default host reports unconfigured assistance. Listed actions remain usable and
freeform declarations remain unresolved. Creator workspace → AI Network →
Providers & Models shows protected status. Status checks make no provider calls;
credentials, route approval and budgets are never configured in the browser.

An explicitly configured host can use Engine's optional Solo API. The server-only
`SoloConfiguration` passed to `make_server` supplies a broker factory, transport,
approved route/policy/configuration, finite deadline/output limit and private
technical directory. Engine owns route eligibility, reservations, validation and
execution. Keep its ledger and host scope metadata outside campaign saves and
product source. Use one host writer per save directory. No implicit environment
key discovery, paid retry, route fallback or live adapter is provided here.

**Review with assistance** sends the exact editable intention to the selected
Engine builder. The player sees the proposed structured action and received
source references before accepting. Editing invalidates that proposal; cancellation
and navigation fence late output. Only explicit acceptance invokes Core. The
committed outcome summary/observations come from its handler; provider prose
cannot create world facts. Unknown replies offer lookup of the same identity,
not automatic new inference. Existing action-result recovery handles accepted
responses lost during delivery. Trash/restore rotates a private restore identity
before restoring even identical save bytes.

The reviewed Engine pin predates this API and safely stays unconfigured. Candidate
`500ab4286aed5354719a78006195922316b41023` supports authored opening actions,
not Catalog's R00 settlement actions. Its full offline App regression and real
browser flow can be qualified explicitly without moving dependency pointers:

```bash
# Export that exact Engine commit's IRGS_3_3 directory to /tmp/irgs-engine-500 first.
IRGS_ENGINE_ROOT=/tmp/irgs-engine-500/IRGS_3_3 python3 -B -m unittest discover -s IRGS_Web/tests -v
IRGS_ENGINE_ROOT=/tmp/irgs-engine-500/IRGS_3_3 node tools/qualify_solo_browser.js /tmp/irgs-solo-browser.json
```

The browser qualifier requires Playwright and Chromium (`IRGS_CHROMIUM` may select
its executable). It owns temporary synthetic saves and an offline fake transport;
it performs no live inference and cleans up its own host. The complete Engine
suite, model semantic/voice evaluation and joined package qualification are separate.

The Catalog R00 fixture is separately qualified through its real structured
handlers and temporary evaluator-only oracle:

```bash
python3 -B tools/qualify_solo_review.py --catalog-commit 2e4f389882df0807fc8064c1a0b533aaa3b1bcd3 --output /tmp/irgs-solo-qualification.json
```

Fetch that Catalog commit into the dependency before running the command. Exact
fixture files are selected from Git into a temporary directory without moving the
committed dependency. This does not certify R00 interpretation through the new API.
Core remains 3.3; 3.4.0 identifies this development iteration.


## Application and campaign themes

Application pages use the warm charcoal/brown base with bronze/coral accents.
Campaign pages select a palette from their public genre binding; known campaigns
can override those accents. Seven genres are supported: military, Roman, fantasy,
post-apocalyptic, shinobi, space and settlement. Century of Conflict, A Scot's Tale
and Rise have campaign variants. Unknown bindings use the base. Names and private
world facts do not select styles. Dark, Light and Parchment remain independent
reading preferences and survive switching/reload. Theme selection changes no save.
`static/themes.css` owns palette tokens; `static/themes.js` selects only known
public presentation IDs. Layout lives in `static/style.css`.

## Protected usage and budgets

Creator workspace → AI Network → Usage & Budgets reads Engine's technical ledger.
The view shows total lifetime reservations/remaining operator units and occupied
transport slots, plus recent requested/reported identities, reported token fields
and errors. `GET /api/ai/usage?mode=creator&limit=25` requires the local session,
accepted Origin and explicit Creator mode. `limit` is bounded to 1–50; summary
totals always cover the entire ledger. Request/context text, private dependencies,
credentials and storage paths never appear in this projection. The default host
shows unconfigured status and creates no ledger just to inspect it.

Reservations remain consumed after failures/cancellation. Missing token reports
and actual charges stay unknown; reported tokens are not a verified bill. Refresh
reads saved records and never retries inference, refunds units or resets budgets.
Run `node tools/qualify_presentation.js /tmp/irgs-presentation.json` for real
Chromium theme/accounting qualification with temporary synthetic campaigns.


## Local reusable App responses

The [App routine library](responses/README.md) supplies 171 authored variants in
55 families: 139 system messages and 32 editable draft starters, with eight
composition recipes. It renders locally and uses no provider tokens. Ordinary
App labels were already local; no production token-savings benchmark is claimed.
Requesting assisted interpretation remains an explicit separate action.

In **Write your own response → Editable draft starters**, select starting words,
review/edit them, then explicitly keep the draft. This submits nothing and
preserves your independent response until you choose Keep. Actual supported
actions still require confirmation. Missing facts/templates never authorize a
paid fallback or turn an unsupported declaration into a resolved action.

The result renderer preserves the exact Core summary and uses only an actual
recorded elapsed span. All inserted names/source text use text nodes or existing
escaping. Library data is immutable, source/state/slot checked and selected
with deterministic variants. No raw save, private certificate or entire response
library is sent to a provider. The App owns this UI pack; Catalog and Engine retain
their own response content and execution/information duties.

Run `node IRGS_Web/tests/test_responses.js` for the local formatter contract and
`node tools/qualify_app_responses.js /tmp/irgs-app-routines.json` for the real
browser/Core flow with inference endpoints blocked and temporary synthetic saves.


## Shared response contract

The reviewed Engine offline runtime and Catalog response depot now feed the same
player result/draft layer across supported authored-scene and settlement contexts.
Server-built `local_responses` bind drafts to the selected actor, campaign,
revision and a fresh view identity. Catalog semantic tags do not authorize Engine
operations. Both Catalog and Engine suggestions review before explicit Keep;
copying/editing remains non-submitting, and custom responses remain available.

Accepted results retain a plain-text `presentation` with complete legitimate
Engine receipt/observation text, anchored through Catalog's exact-receipt recipe.
The common latest-result panel handles both adapters without a second elapsed
clause. Saved presentation is replayed unchanged after lost acknowledgements,
restart and Trash/restore. Older results keep their existing literal rendering;
missing text adapters never trigger inference. Public theme names confer no
mechanics. Source ownership and the reviewed dependency pointers stay intact.

Run `node tools/qualify_shared_responses.js /tmp/irgs-shared-responses.json` for a
real Chromium/Core round trip in two independently initialized synthetic contexts
with no provider configured. See the [response contract](responses/README.md)
for current mappings, source boundaries and unimplemented adapters.


## Received process continuation

Story offers a common review/confirmation path for Engine-selected process starts
and already received phases. The qualified contexts are non-Rise authored
observation and Rise shelter work. Enter elapsed seconds explicitly; pause/resume retain actual work,
and an Inspect command obtains a fresh local receipt. Review cancellation sends
no execution. Last received progress is distinct from remote live state, and a
committed phase does not imply a completed parent process.

Prepared commands and accepted results recover across lost replies, reload,
restart, retries and supported Trash/restore operations. Candidate Core state
and the exact received result are persisted atomically before acknowledgment.
These controls use no provider or model tokens. Begin options and continuation
commands come from Engine's published `irgs-phase-capabilities-1` contract. They
remain attempts checked by Core; themes create no operations. See the
[HTTP, persistence and dependency contract](PROCESS_BRIDGE.md).
Run `node tools/qualify_process_bridge.js /tmp/irgs-process-browser.json` in
addition to the ordinary guide checks for actual Chromium process qualification.
