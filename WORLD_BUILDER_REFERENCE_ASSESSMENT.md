# World Builder reference assessment — public v0.35.4 source

## Feasibility and exact input

An IRGS-native world builder is feasible using the editor's documented workflows
as a reference. **Decompiling the supplied executable is unnecessary for this
assessment:** the public **v0.35.4** tag retains its Python source.

Source: [public release tag](https://github.com/Pfadfinder-Adam/RTW-M2TW-Campaign-Editor/tree/9567aee8c2066d4c8b3838c734141ad1516a89e3),
commit **9567aee8c2066d4c8b3838c734141ad1516a89e3**, with **270 files**. The retrieved
source archive is 6,241,686 bytes, SHA-256
**b65907f59aa91e48b2c6de7ffd95b5b329eb1d3070f9ccc52a48a0cc38c4c6a7**.

The [tagged LICENSE](https://github.com/Pfadfinder-Adam/RTW-M2TW-Campaign-Editor/blob/9567aee8c2066d4c8b3838c734141ad1516a89e3/LICENSE) is GPL version 3.
The current default branch uses different terms for versions after 0.35.4 and
acknowledges the older GPL releases. Keep this assessment pinned to the tagged
source; it does not approve copying later code or changing third-party licenses.

The public release metadata lists a 37,637,737-byte Windows executable with
SHA-256 a060661f1eb856a486bb01598c5e8167c02fe577a916425663157153a4fe791d.
The uploaded executable could not be transferred through the 32 MiB attachment
tool, so its version, hash and equality to that release are **unverified**.
Neither executable was run, installed, unpacked or decompiled. No external source
module, build workflow or test was executed. This is static source/documentation
and screenshot assessment, not runtime qualification.

## What the source actually provides

| Inspected component | Verified design or workflow | IRGS application |
| --- | --- | --- |
| [plan.py](https://github.com/Pfadfinder-Adam/RTW-M2TW-Campaign-Editor/blob/9567aee8c2066d4c8b3838c734141ad1516a89e3/campaign_editor/plan.py) | In-memory edit plan; changed-file report; validation; explicit apply and backup/restore support. | A world-draft diff and reviewed initialization proposal. Retain Core's own atomic state/result/CAS contracts; file backup is not a substitute for them. |
| [mapdata.py](https://github.com/Pfadfinder-Adam/RTW-M2TW-Campaign-Editor/blob/9567aee8c2066d4c8b3838c734141ad1516a89e3/campaign_editor/mapdata.py), [gui_map.py](https://github.com/Pfadfinder-Adam/RTW-M2TW-Campaign-Editor/blob/9567aee8c2066d4c8b3838c734141ad1516a89e3/campaign_editor/gui_map.py) | Tile map data; terrain/political layers; places/ports; zoom, selection and map interactions. | Geography/topology/layer editing in the existing web App, bound to stable world IDs and explicit coordinate units. |
| [terrain.py](https://github.com/Pfadfinder-Adam/RTW-M2TW-Campaign-Editor/blob/9567aee8c2066d4c8b3838c734141ad1516a89e3/campaign_editor/terrain.py), [gui_terrain.py](https://github.com/Pfadfinder-Adam/RTW-M2TW-Campaign-Editor/blob/9567aee8c2066d4c8b3838c734141ad1516a89e3/campaign_editor/gui_terrain.py) | Ground/features/climate/height tools; draft painting kept until Apply; separate pending/dirty/rebind behavior. | Terrain annotations and optional raster/vector draft layers. Navigation, work, sight and elapsed consequences still require selected Engine rules. |
| [mapedit.py](https://github.com/Pfadfinder-Adam/RTW-M2TW-Campaign-Editor/blob/9567aee8c2066d4c8b3838c734141ad1516a89e3/campaign_editor/mapedit.py), [mapzero.py](https://github.com/Pfadfinder-Adam/RTW-M2TW-Campaign-Editor/blob/9567aee8c2066d4c8b3838c734141ad1516a89e3/campaign_editor/mapzero.py) | Placement checks and map-from-zero generation for the original formats. | A small original fictional-world starter, object placement validation and repeatable export. Rebuild the data/validation contracts for IRGS. |
| [moddata.py](https://github.com/Pfadfinder-Adam/RTW-M2TW-Campaign-Editor/blob/9567aee8c2066d4c8b3838c734141ad1516a89e3/campaign_editor/moddata.py), [strat.py](https://github.com/Pfadfinder-Adam/RTW-M2TW-Campaign-Editor/blob/9567aee8c2066d4c8b3838c734141ad1516a89e3/campaign_editor/strat.py) | Original mod file discovery and parsing of factions, settlements, characters and diplomacy. | Inform a separately scoped import/conversion boundary. These parsers do not load IRGS worlds or establish compatible semantics. |
| [check.py](https://github.com/Pfadfinder-Adam/RTW-M2TW-Campaign-Editor/blob/9567aee8c2066d4c8b3838c734141ad1516a89e3/campaign_editor/check.py) | Read-only file/relationship checking and diagnosis. | Object-level schema/reference/profile validation and actionable errors before any world creation. |
| [modbuilder.py](https://github.com/Pfadfinder-Adam/RTW-M2TW-Campaign-Editor/blob/9567aee8c2066d4c8b3838c734141ad1516a89e3/campaign_editor/modbuilder.py) | WHEN/IF/DO recipe builder generates scripts for the original engines. | Possible later declarative authoring of supported triggers/intents. Do not import arbitrary scripts or invent a second executor; all effects remain Core-owned. |

The source's UI is Python **Tkinter**, with Pillow-based map data/rendering and
optional graphics modules. The tagged release workflow uses **PyInstaller**;
the current branch's third-party notices mention a different compiler/runtime.
Do not infer the uploaded binary's packaging from either description.

A full source audit was not performed. Fifteen selected modules were inventoried
with Python AST, key map/terrain/plan/recipe code and packaging metadata were read,
and the tagged map screenshot was inspected. The code is useful as a reference,
but this assessment does not certify its correctness, security, binary equivalence
or suitability as an IRGS runtime dependency.

## Implementation decision for IRGS

Build the Creator Workshop editor in **IRGS-APP-WEB**, with the same authoring
schema and validation/initialization services used by developers. Keep
**IRGS-Engine** authoritative and keep authored packs/provenance in
**IRGS-Catalog**, respecting existing Engine-owned technical content and Kira canon.

Use the source to understand workflows and formats. The present task adopts
**no third-party code, images, executable, GUI dependency or numeric game rules**
into IRGS. Direct code reuse would require a deliberate applicable-license and
dependency decision; do not silently relicense GPL material. The planned web
editor and world-package model are IRGS-authored work.

The source's coloured pixel conventions, faction identifiers, script APIs and
physical/timing defaults are original-format contracts. They do not become
IRGS geography, authority, resources, knowledge or selected rules by being imported.
Keep faithful source attribution in reference records and IRGS language in the
product's own controls.

## Concrete next delivery

Follow [the shared implementation plan](WORLD_BUILDER_PLAN.md):

1. Engine WB-ENG-01 publishes world-draft/package DTOs, selected profile bindings,
   supported initialization operations and validation errors.
2. App WB-APP-01 builds a Creator-only draft/entity editor; map/topology controls
   follow against that same contract, with draft undo and explicit preview/review.
3. Catalog WB-CAT-01/02 creates original fictional example content, source/asset
   provenance and separate actor/evaluator acceptance.
4. Demonstrate draft → validate → review → ordinary new-world playtest →
   save/continue → export/import using existing Core effects. Include a non-Rise
   context and a second family; do not turn the builder into a Rise-only tool.
5. Expand terrain/3D and optional conversions after the first usable authoring
   loop. Continue the protected AI setup and sustained Alpha gameplay critical path.

The remaining binary-transfer limitation does not block these owner tasks.
A later binary-specific comparison would need an accessible file or its verified
hash/version. No such comparison is required to begin the independent authoring
implementation.

All 3.x work remains Pre-Alpha; source availability and this assessment close
no functional Alpha gate. No runtime implementation or joined build is published
by this guide update.
