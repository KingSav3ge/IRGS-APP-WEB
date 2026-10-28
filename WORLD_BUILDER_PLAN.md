# IRGS World Builder — development and Creator Workshop

## Direction and input status

The user proposes rebuilding a supplied campaign editor as an IRGS world builder,
usable both by IRGS developers and in Creator Workshop. Build **one shared
authoring system** over the authoritative Engine, with role-appropriate screens.
This is a development direction and implementation plan, not a delivered editor.

The supplied Windows executable has **not been inspected**: the attachment
download tool rejects it because it exceeds its 32 MiB transfer limit. Its
language, recoverable source, assets, supported formats and actual editing
features are therefore unknown. The workflows below are IRGS requirements,
not claims about the executable. Do not claim decompilation or compatibility.

When the source project, a smaller archive, or complete split parts are available,
first record hash/size and inspect PE architecture, runtime metadata, version
information, resources, strings and file-format references without launching or
installing it. Managed code may permit useful decompilation; native code may
permit only partial reconstruction. Recoverability must be measured. Record
observed workflows/formats separately from proposed IRGS behavior. Preserve the
original input and attribution independently of IRGS-authored code and data.

## Shared user workflow

1. Create or clone a versioned world draft, select its supported Engine profile,
   and label it historical, fictional or mixed with explicit source uncertainty.
2. Edit geography and topology: named places, regions, terrain annotations,
   connections, access and explicit coordinate units. Add optional map/height
   layers where supported.
3. Edit people, households, institutions, items, finite resources/custody,
   relationships, initial commitments and legitimate initial knowledge.
4. Define dated campaign entry points, controlled roles and selected opening
   rules. Keep civil dates/calendars/unknown hours separate from elapsed work.
5. Validate references, source status, units, selected rule dependencies, actual
   control/capacity and supported initialization operations. Show unresolved
   requirements at their affected objects.
6. Review the initialization diff and create an isolated playtest with the normal
   Engine and App. Inspect actual consequences and repeat after editing the draft.
7. Export a portable versioned world pack with schema/content versions,
   dependency identities, source/asset manifest and checksums. Reviewed content
   may then enter Catalog; ordinary player launch still requires its own review.

Developers and creators use the same schemas, validators and initialization
contracts. Developer conveniences cannot create a second simulation. Workshop
drafts live in their own workspace/store; editing a draft does not mutate a
published Catalog record or an existing campaign.

## Ownership and contracts

| Repository | Owns |
| --- | --- |
| IRGS-Engine | World-draft/package contracts, supported profile bindings, semantic validation, normalization, proposed initialization operations and atomic reviewed creation through the existing Core owners. |
| IRGS-APP-WEB | Creator-only editor, map/layer and entity controls, draft persistence, undo/redo, validation display, diff/review, import/export and isolated playtest host/UI. |
| IRGS-Catalog | Canonical authored world/campaign packs, geography/source dossiers, approved assets/references, metadata/previews, content versions and independent authoring/playtest acceptance fixtures. Technical initializers stay in Engine. |
| Unified IRGS | Compatible assembled editor/runtime/content, clean distribution, integration review and versioned publication. |

Existing Engine-owned technical libraries, initializers and Kira canon stay
in Engine. Catalog authoring does not relocate or replace that adopted canon.

Engine publishes a versioned API before App writes an importer around guessed
fields. The initial data-only package proposal should include:

- Package identity/schema/content version, title, genre/campaign family and
  fictional/historical/mixed classification.
- Exact compatible Engine/profile/content dependencies and selected rule IDs.
- Geography with stable IDs, topology and explicit coordinate/unit system.
  Visual distance does not establish travel time, passability or a route.
- Entity definitions with references, roles/control, actual initial inventories,
  custody/rights and commitments using supported Core procedures.
- Source assertions and their status, time precision, provenance and separately
  selected initial actor receipts. A reference is not automatically actor knowledge.
- Entry points and reviewed initial circumstances, distinct from later goals,
  planned events and possible outcomes. History after the cutoff is not forced.
- Asset/source manifests and file checksums, with bounded data-only payloads.
  No executable scripts, credentials, runtime databases or private save content.

Names above describe a contract to implement, not an already accepted JSON schema.
Engine must publish actual DTO fields, errors, limits and initialization behavior.
Catalog owns authored values; App consumes the contract.

A terrain mark, resource annotation or institution label is draft data. It takes
an explicit adopted profile and reviewed Core initialization to establish
physical stock, control, capabilities and legitimate information. Unsupported
mechanics remain unresolved rather than receiving invented defaults.

## First useful increment and acceptance

Deliver a complete small authoring path before broad terrain/tool expansion:

- Create/save/reload a fictional non-Rise draft with at least two linked places,
  a player and an independently identified contact, a finite conserved item,
  explicitly selected initial knowledge and supported local actions.
- Use the same contract for a second selected campaign family, retaining R00 as
  a regression without making the editor a Rise-specific implementation.
- Validate, preview the exact proposed initialization, explicitly review and
  create an ordinary playtest. Exercise movement/perception, legitimate speech,
  a material consequence, a failed prerequisite and saved continuation wherever
  the selected profile supports them.
- Export/import the world pack, repeat normal reviewed creation in a clean host,
  and demonstrate consistent selected state/rules without a developer repairing it.
- Prove that draft editing, validation and previews commit no campaign effects.
  Reject broken references, missing rules, duplicate IDs, incompatible versions,
  invalid units and unbounded/unsafe package paths with actionable errors.
- Keep creator-only source/editor data out of the player's received view. Test
  cancelled creation, duplicate acceptance, failed save and restored playtests
  against the existing atomicity/recovery contracts.

These are future acceptance requirements. A schema, imported picture, static map
or editable JSON pane alone does not qualify a world builder. Authoring supports
A4-G02/G10/G12; it does not close the remaining Alpha gameplay gates.

## Owner tasks and sequencing

| Task | Deliverable and dependency |
| --- | --- |
| WB-ENG-01 | Inventory existing Creator/Core initialization operations and publish the versioned world draft/package proposal, selected rule bindings, semantic validator DTOs and explicit unsupported areas. Begin alongside selected travel/intent work. |
| WB-ENG-02 | Implement draft validation and initialization preview that produce proposed operations and actor-receipt boundaries without state mutation; apply only through reviewed atomic new-world creation. |
| WB-ENG-03 | Prove both selected contexts, finite resources, units/control, broken dependencies, duplicate creation, failed save and continuation. Keep one Core and existing nine K-owners. |
| WB-APP-01 | After the current integration harness fixes, build a Creator-only draft/list/entity editor against the published contract. Reuse existing Workshop and map-authoring navigation; keep planned pages honest until connected. |
| WB-APP-02 | Add map/topology/layer controls, undo/redo, draft import/export and object-level validation. Use the same draft store/contracts for development and Creator Workshop. |
| WB-APP-03 | Connect exact diff/review and isolated playtest creation to existing host/Engine APIs. Verify reload, cancellation, known-view filtering and ordinary player launch. |
| WB-CAT-01 | Specify original synthetic reference packs and independently authored actor/evaluator instructions for the two selected contexts. Separate world content from technical initialization. |
| WB-CAT-02 | Prepare geography/source/asset provenance and content metadata; preserve original records and qualify proposed conversions before adopting them into working packs. |
| WB-CAT-03 | Independently qualify exported/imported packs and ordinary reviewed playtests against exact Engine/App revisions; require actual effects, failure/recovery and source/privacy separation. |

The coordinator's executable inspection remains blocked on accessible input.
Owner contract/design work can proceed now. First fix the review's reproduced
App harness issues, continue protected operator setup and shared gameplay, and
publish small useful authoring increments alongside that work. Do not pause the
Alpha critical path for a speculative complete editor rewrite.

Keep full terrain sculpting, broad format conversion, unrestricted scripting,
public content hosting/marketplace and complex modification of existing live
campaigns as separately scoped later work. The first release authors new worlds
and isolated playtests. Existing campaign changes need their own reviewed patch
contract, revision/recovery behavior and compatibility evidence.

## Evidence and release policy

Use synthetic temporary stores and declare actual imported sources and pins.
Source references or screenshot-like layouts do not prove functionality.
No live AI is required for ordinary authoring or validation. Preserve user saves,
personal configuration, original source records and accurately dated evidence.
IRGS-authored mechanics and interface use IRGS terms; original input records retain
their authentic attribution.

All 3.x editions remain Pre-Alpha. This plan changes no VERSION.json, Engine
compatibility or selected mechanics. A world builder is qualified only when its
actual editing/validation/creation/playtest/export loop works; Alpha 4.0 still
requires every mandatory shared gate.
