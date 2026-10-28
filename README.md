# IRGS App / Web — 3.4.4 Pre-Alpha

## Coordinated 3.4.4 Pre-Alpha continuation

Current coordinated edition: **3.4.4 Pre-Alpha**; previous release field: **3.3.3**.
The selected travel and ordinary communication increment preserves one Core,
explicit acceptance, actor filtering, conserved stock/time and original-result
recovery. No Alpha gate is closed and live/provider/Windows qualification remains open.

The recipient/version harness fixes are delivered. Next: A4-APP-01 protected operator setup, then A4-APP-03 supported-intent review. Consume published authoring contracts for WB-APP-01; use the existing phase API for selected travel.

This current ordering supersedes earlier review and pending-3.4.3/3.4.4 notes below.
Original tested source identities and older evidence remain unchanged.
The coordinator owns the exact all-three integration and final package review.
Every later unified main push increments the edition; next is 3.4.5 Pre-Alpha.
Continue toward the shared Alpha 4.0 functional gates and World Builder plan.

Current stage: **3.4.3 Pre-Alpha**. Development target: **functional 4.0.0 Alpha**.
Start with [the Alpha plan](ALPHA_4_0_PLAN.md),
[owner work order](COORDINATOR_WORK_ORDER.md) and
[continuation](CHAT_CONTINUATION.md). All 3.x editions are Pre-Alpha.
The reviewed start/communication set is already integrated in unified 3.4.3;
older pending-adoption claims below are dated history, not the current task.
The new plan does not claim Alpha is implemented or qualified.

Current coordinated edition: **3.4.3**; previous release: **3.3.3**.
See [version policy](VERSION_POLICY.md). Earlier baseline tables and execution
records below retain their original tested development identities.

Current development: [guide](DEVELOPMENT.md) · [chat continuation](CHAT_CONTINUATION.md).

Independent App development for IRGS. Campaign catalogue data and designs belong to [IRGS-Catalog](https://github.com/KingSav3ge/IRGS-Catalog), pinned in `Catalog/`. The viewer stays in this repository. This repository owns `IRGS_Web/`; simulation stays in [IRGS-Engine](https://github.com/KingSav3ge/IRGS-Engine). [IRGS/main](https://github.com/KingSav3ge/IRGS) joins all three components.

```bash
git clone --recurse-submodules https://github.com/KingSav3ge/IRGS-APP-WEB.git
cd IRGS-APP-WEB
python -B tools/verify_components.py --component app
python -B IRGS_Web/server.py --port 8766
```

After an ordinary clone, run `git submodule update --init --recursive`. Python 3.12+ is required. The standard-library host binds only to loopback. `Start-IRGS.cmd` is the Windows launcher. Existing user campaigns remain in their original installation; no saves are included or migrated.

Run `python -B -m unittest discover -s IRGS_Web/tests -v` and `node IRGS_Web/tests/test_gameplay_ui.js`. Refresh only App pins after intentional edits with `python -B tools/refresh_component_releases.py --component app`. This changes no Engine commit or release pin.

`Catalog/` is also a pinned dependency: initialize both with `git submodule update --init --recursive`. Select and test an exact Catalog commit before committing a new pointer; this needs no Engine source change. `IRGS_CATALOG_ROOT` can select an explicit `IRGS_Catalog/` directory. Catalogue integrity is verified at host startup.

`Engine/` is a pinned dependency, not a second App-owned simulation. Engine work belongs in its own repository. To test a newer Engine, check out its explicit commit in the submodule, verify the pair, then commit the pointer update. `IRGS_ENGINE_ROOT` can select an explicit Core directory for qualification; joined IRGS uses sibling `IRGS_3_3/`.

The library offers 44 expanded v0.5 concept previews with filters, 37 supported Century dates, the limited fictional Rise founding slice and the adopted Kira v0.5 world guide. Proposed campaigns remain unreleased. Kira has no playable snapshot. The full C2 resolver, general freeform/combat resolution and the complete institutional cycle remain work.

See [catalogue implementation](Catalog/IRGS_Catalog/design/campaign_catalogue/README.md), [App details](IRGS_Web/README.md), and [joined integration instructions](https://github.com/KingSav3ge/IRGS/blob/main/COMPONENT_REPOSITORIES.md).

[Development status](DEVELOPMENT.md) tracks completed, active, blocked and remaining
App work. The Creator's **Historical Details** entry preserves explicit local ZIP
browsing and the complete Catalog multipart archive. Candidate qualification and review are recorded
in the [coordinator report](COORDINATOR_REPORT.md).
