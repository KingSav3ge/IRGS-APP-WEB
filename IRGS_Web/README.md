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

AI assistance currently reports unavailable. Listed actions remain usable and
freeform declarations remain unresolved. Creator workspace → AI Network →
Providers & Models shows protected availability, not an active Director graph or
model benchmark. `/api/ai/status` requires the local session; diagnostic fields
require explicit Creator mode. No credentials, provider route or budget is
configured through the browser, and status checks make no provider calls.

Engine owns the forthcoming interpretation/proposal/validation/ledger API. This
App increment contains no replacement simulator or provider router. Qualification
uses the published Catalog scenario through temporary synthetic saves:

```bash
python3 -B tools/qualify_solo_review.py --catalog-commit 2e4f389882df0807fc8064c1a0b533aaa3b1bcd3 --output /tmp/irgs-solo-qualification.json
```

Fetch that Catalog commit into the dependency before running the command. It
selects the exact fixture files from Git into a temporary directory without
moving the committed dependency or installing content. Only evaluator code reads
the oracle. The host receives setup choices and explicit structured requests;
no fixture oracle, raw save or archive is sent to a provider. The selected Core
remains 3.3; 3.4.0 identifies this development iteration, not a new rules version.
