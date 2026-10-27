# IRGS development target: functional Alpha 4.0

## Direction and release classification

The user classifies the entire **3.x.x series as Pre-Alpha** and sets a functional
**4.0.0 Alpha** as the development goal. Current published IRGS is **3.4.3
Pre-Alpha**; the recorded previous release remains **3.3.3**. This is a development
assignment, not a 4.0 implementation, release, or passed acceptance report.

Work on shared IRGS systems across campaigns. A polished library, a large
reference archive, an AI connection, or a single scripted opening does not
complete Alpha. Preserve the usable 3.4.3 foundation while completing the
ordinary player loop.

## What functional Alpha means

A new Solo player can install and launch IRGS, configure an optional supported AI
provider through protected operator setup, choose an honestly labelled playable
campaign and character, understand their legitimate circumstances, make a
supported decision, review the exact intended attempt, explicitly commit it,
receive the actual consequences, respond to an evolving world, and continue
after saving, closing, restarting and restoring.

The supported loop must include movement and perception, conversation and
negotiation, material constraints and commitments, selected work/needs/recovery,
a bounded consequential risk or conflict procedure, and NPC/local institutional
responses. These systems must affect the same persistent world. Failure,
refusal, scarcity, interruption and changed circumstances must create further
decisions. A sequence of unrelated canned successes or unresolved declarations
is insufficient. Wider warfare, complete national economies and every historical
institution are outside the minimum; their underlying shared owners remain intact.

The Alpha qualification set must contain **at least two independently initialized
ordinary playable contexts from distinct campaign families**, including **a
non-Rise personal/adventure context**. Their actual roles, constraints and
decisions must differ; theme substitutions alone do not count. Preserve R00 as
a regression whether or not a developed Rise context is selected for Alpha.
An existing fictional courier or R00 example can qualify only after it supports
sustained play through normal product creation. Henry's bounded observation alone
does not qualify. A fictional character in a sourced historical setting is
acceptable when fictional circumstances and historical uncertainty remain explicit.

One supported AI provider must demonstrate a grounded playable cycle before the
AI-enabled Alpha claim is qualified. Routine local operations and rendering
remain usable with no provider and zero routine inference. A provider outage
must preserve the campaign, player intent and recovery path. Model output alone
cannot resolve unsupported gameplay.

## Starting point: reviewed 3.4.3, not fresh Alpha evidence

| Repository | Reviewed source revision |
| --- | --- |
| Unified IRGS | 9dc27f82f7f49e6f8b1de66573b991b22e68cb2a |
| Engine | efc84364b86e640f5028bfac2dfd5ae3021695a9 |
| App/Web | de4e6926f6236f720365d552c69e02756ce18605 |
| Catalog | 6f927b00e12a3339861ac353bc38d03c68279662 |

The coordinator has already integrated start-context adoption, App communication
controls and compatible dependency pins in 3.4.3. Earlier reports of three
unadopted App expectations or a pending 3.4.3 publication are historical; do not
repeat that completed adoption as the new task.

Existing foundations include actor-filtered views, reviewed starts, selected
equipment/observation/work operations, process and communication contracts,
original-result recovery, local response drafts, the 44-record catalogue and
preserved Historical Details archive. General freeform declarations, broad
combat, autonomous continuing play and live AI quality are not thereby complete.
John/default unsupported starts remain limited; Kira remains a reference guide
until actual gameplay is implemented and independently qualified.

The prior joined review records 772 Core passes plus one private-fixture policy
skip, 249 Web passes plus seven Windows skips, 150 interface checks, 32 tooling
checks, eight independent HTTP checks, six browser suites and clean-package
qualification. These are attributed 3.4.3 results, not execution of this plan.
See the [published review](https://github.com/KingSav3ge/IRGS/blob/9dc27f82f7f49e6f8b1de66573b991b22e68cb2a/provenance/qa/start_readiness_3_4_3_review.json).
No Alpha gate is qualified by this instruction update.

## Mandatory Alpha gates

All gates below must be independently qualified against the same compatible
release candidate. The companion [acceptance register](ALPHA_4_0_ACCEPTANCE.json)
records planned requirements and starts with every gate not qualified.
Implementation evidence may be partial without implying product acceptance.

| Gate | Required observable behavior | Primary owners |
| --- | --- | --- |
| A4-G01 | Clean install and normal launch identify the running build and dependencies; setup, missing configuration and offline operation are understandable. No developer-only world seeding. | App, coordinator |
| A4-G02 | Each Alpha start has sourced or explicitly fictional context, actual controlled actor, location, legitimate knowledge, supported actions and reviewed atomic creation. Unsupported references stay honestly limited. | Engine, Catalog, App |
| A4-G03 | Suggested and editable own responses map to versioned supported intents, disclose the exact attempt for review, commit only after explicit acceptance and show the actual result. Ambiguous or unsupported intent remains editable and unresolved. | Engine, App |
| A4-G04 | Local movement/perception, work, inventory/resources, needs and recovery use selected rules and real commitments. Time-dependent consequences and interruptions persist; rejection/retry creates no stock, work or elapsed time. | Engine, App |
| A4-G05 | Ordinary starts expose legitimate participants/channels. Dialogue, testimony, offers, consent, refusal and fulfillment have distinct effects and information status; NPC speech is neither automatic consent nor world truth. | Engine, App, Catalog |
| A4-G06 | At least one NPC and one local institution make continuing decisions from scoped knowledge, authority and shared resources. Their accepted actions change later choices; plans survive continuation and compete with player commitments. | Engine, App |
| A4-G07 | At least one supported risk/conflict procedure produces consequential success, failure or withdrawal and recovery using an adopted, versioned profile. Relevant injury/loss/commitments persist; arbitrary narrator adjudication and decorative combat are insufficient. | Engine, Catalog, App |
| A4-G08 | One protected provider configuration completes a bounded live synthetic intent/dialogue/narration cycle grounded in Core receipts and legitimate information. Cancellation, timeout, invalid output, exhausted budget and outage preserve state and intent. Costs/usage are accounted; ordinary local work makes zero calls. | Engine, App, Catalog |
| A4-G09 | Multi-session play, lost replies, duplicate/concurrent submissions, interrupted work, save failure, restart, restore and stale navigation preserve atomic state and immutable original results. No duplicated effects or future receipts replayed onto a restored branch. | Engine, App |
| A4-G10 | The two ordinary Alpha contexts sustain evolving multi-session decisions through the shared systems; independent consumers check failure and recovery as well as happy paths. R00 and existing supported starts retain their actual guarantees. | Catalog, Engine, App |
| A4-G11 | Real browser and native Windows launch/package checks pass on a clean extraction; responsive controls, keyboard use, pending actions, honest status/time, Chronicle, save/continue and actionable errors support actual play. | App, coordinator |
| A4-G12 | Exact Engine/App/Catalog SHAs and App pins form one verified candidate; scoped DEV/C2 coverage, source integrity, preserved archives, secret-free packaging, regressions and all gates have reviewed evidence. No blocking correctness, privacy, data-loss or ordinary-play defect remains. | Coordinator, all owners |

Do not defer a mandatory gate by silently reducing its definition. Propose a
specific scope change to the coordinator with its effect on functional play.
Bugs that block ordinary play, violate authority/knowledge, lose or duplicate
effects, or expose credentials block Alpha. Smaller known issues must have
documented reproduction, impact and disposition.

## Acceptance journeys and evidence

Catalog owns independent actor instructions and evaluator-only expectations.
Engine owns execution contracts; App owns real product interaction; the
coordinator reproduces the compatible set. For each selected context, capture:

1. Clean normal start and review with no test-only operator injecting state.
2. Consecutive perception/movement, interaction and material decisions whose
   later options depend on prior committed consequences.
3. A refusal, unsupported attempt or failed prerequisite that preserves intent
   and has no invented effects; followed by a legitimate alternate decision.
4. NPC/institution reaction, an obligation or resource conflict, and supported
   time-dependent work or recovery that changes a later decision.
5. The selected risk/conflict path and its recovery wherever that profile applies.
6. Close/restart, save/continue, duplicate or lost-reply retry and a restore branch,
   then further play proving the world was not reset.
7. A separate bounded live-provider journey plus offline/provider-failure paths.
   UI text, effects, knowledge, requests and accounting must agree.

Record exact commits/pins, imported module paths, selected rules/content versions,
commands, assertions, real HTTP/browser interactions, outcomes, failures/skips,
evidence paths, user-visible limits and reviewer. A mock response, refreshed
manifest, unit count, prose transcript or generated plan alone qualifies no
end-to-end gate. Linux Windows skips remain skips until a native run is captured.
Fake provider transports prove protocol behavior, not live model quality.

## Work sequence and interfaces

| Stage | Engine | App/Web | Catalog | Exit |
| --- | --- | --- | --- | --- |
| 1: usable foundations | Ordinary-start participant/channel contract; selected native travel and intent DTOs | Protected setup/build identity; preserve existing review/recovery | Qualify published communication bridge at exact revisions; select Alpha contexts and source/rule gaps | Ordinary-start contracts published with examples, honest limitations and reproducible consumers |
| 2: continuing shared play | Supported intents, resources/time, social execution, bounded NPC/institution decisions and selected conflict/recovery | Normal controls for those capabilities; editable response mapping and truthful continuing state | Independent multi-step requirements/fixtures and readiness copy for both contexts | Sustained offline product journeys work without manual world repair |
| 3: AI-assisted play | Existing provider validation/routing, scoped proposals and grounded narration | Operator configuration, budget/error/review UX and protected dispatch | Grounding/privacy/quality rubric and independent provider-path evaluation | Bounded configured-provider journey plus offline/outage/rejection evidence |
| 4: Alpha qualification | Resolve correctness/recovery defects; map Alpha DEV/C2 coverage | Browser, Windows, accessibility, packaging and recovery fixes | Execute final exact-set consumers; verify archives and release claims | Coordinator reviews all gates and publishes only the qualified candidate |

Start independent work immediately: App setup and Catalog independent assessment
do not wait for the entire Engine. Publish small versioned interface handoffs
early, including DTOs, errors/statuses, examples, recovery expectations and actual
execution scope. Consumers may implement against a documented contract while
labelling not-yet-executable paths pending. Contract publication is not completion.
When a dependency blocks one task, report the exact contract/revision needed and
continue independent work. Do not add a second backend or edit another owner's
source to conceal an upstream gap.

## Architectural and source boundaries

Keep one authoritative Core and the existing nine K-owners. The six Director
categories remain **Game Master, World, National, Regional, Local and Scene**.
Logical AI task assignments do not add Directors, simulation owners or mandatory
calls per turn. Plans, AI and narration propose or describe; Core validates and
commits actual effects.

Keep intention, authorization, effect, outcome, received information and
presentation distinct. Actor views cannot expose raw templates, private saves,
hidden evaluator facts or another actor's private terms. Suggestions cannot
reveal a winning route through hidden truth. Exact testimony remains testimony.
Keep storage revision, causal sequence, selected elapsed work, civil date and
occurrence/recorded/received times separate. Do not invent a universal roll,
duration, stock, rank authority or historical hour.

Use adopted campaign/rule profiles. When required mechanics are unspecified,
write a concrete versioned design proposal with authority, resources, time,
effects, information and tests, then record its explicit adoption under the
existing rule ownership before use. Keep fictional Alpha profile choices distinct
from historical assertions and universal Core defaults. Escalate genuine changes
to agreed mechanics or scope, while continuing independent work. Routine
implementation choices within established contracts do not require new permission.

New historical campaigns use verified dated snapshots; continuing campaigns use
committed history, not a reseeded template or a scheduled historical future.
Preserve original archive bytes, citations and adopted canon. Describe IRGS's
own mechanics without external game or Questner branding; historical source
records retain authentic attribution and content. Keep the 44 preview statuses,
750 system variants, 250 editable drafts, 32 recipes and older fixture identities
unless a separately reviewed change explicitly updates their contract.

Use synthetic temporary stores. Never inspect/copy/migrate user saves for QA.
Do not commit credentials, personal configuration, runtime databases/logs/caches
or generated development artifacts. Live inference is not authorized by this
document: use a protected configured service and an explicitly authorized finite
evaluation budget before the live gate. Missing credentials or budget block that
gate, not offline development. No paid call is needed for this instruction update.

## Release, ownership and reporting

Each chat implements, tests and pushes **only its own component repository**.
App owns its two dependency pins and updates them deliberately after compatibility
checks; environment overrides do not change committed pins. Engine owns technical
initializers/rules and Kira canon; Catalog owns listings, previews, design,
source dossiers and independent evaluations; App owns the viewer and host.

Publish focused viable increments rather than waiting for the whole Alpha.
Report: task/gate and stable DEV/C2 IDs; implementation; full published SHA;
exact tested dependencies and committed pins; executed checks and evidence;
failures/skips; remaining gaps; next task and any specific dependency blocker.
Work orders and reports alone are not viable runtime increments.

The coordinator reviews all three viable compatible updates, assembles and
reproduces joined/browser/package checks, and controls unified publication.
Every push to unified main increments the edition: next is **3.4.4 Pre-Alpha**,
then through 3.4.9, then 3.5.0. Continue 3.x Pre-Alpha work as needed; reaching a
number does not establish Alpha. Only a qualifying functional milestone becomes
a **4.0.0 Alpha** candidate. Align all four edition files at that publication.
Do not change VERSION.json to 4.0 merely for this assignment. Preserve the
user-directed previous_version value 3.3.3, independent content/schema versions,
Core compatibility 3.3 and the current IRGS_3_3 path.

Unified main retains one current distributable; superseded generated installs
need not be kept. Preserve Git history, original supplied archives, source
provenance and accurately dated evidence. Publishing these instructions to
component repos does not publish a joined build or start another chat.
