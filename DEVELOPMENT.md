# App / Website development

This repository owns `IRGS_Web/`, the local Solo host, interface and catalogue
viewer. Push App work to `KingSav3ge/IRGS-APP-WEB/main`. Follow
[the current work order](COORDINATOR_WORK_ORDER.md); IRGS Enviroment reviews exact
component commits and performs joined integration separately.

## Ownership and setup

- `Engine/` pins IRGS-Engine. Simulation, world rules and historical archive
  parsing/verification belong there.
- `Catalog/` pins IRGS-Catalog. Campaign data, designs and the preserved Historical
  Details payload belong there. App provides no second editable content tree.
- Catalogue design: [campaign catalogue](Catalog/IRGS_Catalog/design/campaign_catalogue/README.md)
  and [expanded v0.5](Catalog/IRGS_Catalog/design/catalogue_v0_5/README.md).

Python 3.12+ and Node.js are required; no package installation is needed.

```bash
git submodule update --init --recursive
python3 -B tools/verify_components.py --component app
python3 -B IRGS_Web/server.py --port 8766
```

The host binds to loopback. Use a separate unused development port; keep existing
user campaigns in their original installation. Tests use synthetic records and
temporary saves, never private playthroughs.

## Completed foundations

- [x] Player-filtered Story, World and Chronicle; explicit Creator inspection.
- [x] Reviewed character creation, stable request recovery, campaign Trash and
  restoration, reading preferences and the local launcher.
- [x] Viewer for 44 expanded v0.5 concept previews, 37 scoped Century starts,
  the bounded fictional Rise slice and adopted Kira reference canon. Previews
  remain unreleased; Kira has no playable snapshot.
- [x] Bounded equipment actions, contextual draft suggestions and the optional
  authored opening. General freeform/combat declarations remain unresolved.
- [x] Creator-only historical source search, paging, original records, uncertainty,
  citations and rights; safe text and HTTP(S) links; no source adoption or save
  changes. Existing reference routes and bookmarks remain supported.

## historical-details-01

### Completed App work

- [x] Name the Creator reference entry **Historical Details**.
- [x] Explain unattached, incomplete, corrupt and unavailable sources separately;
  metadata alone never represents an available archive.
- [x] Retry archive checks, searches and source records without creating a save,
  event, world or player knowledge. Keep literal query and source-row identity.
- [x] Refresh explicit local ZIP registration without restarting the host; a
  broken explicit attachment never silently falls back to another source.
- [x] Reject stale responses after navigation, newer requests or inspector close.

### Active / blocked

- [ ] Bind the Catalog multipart source to the delivered Engine reader contract
  and exercise complete, missing and corrupt parts through the HTTP interface.
  The App adapter is prepared for `from_catalog_manifest(path, sha256,
  cache_dir=...)`; the currently selected Engine does not publish this API.
  Metadata without a compatible reader/payload remains unavailable. Failure-code
  tests use a test double and do not qualify multipart reconstruction.
- [ ] Pin and qualify the exact coordinator-reviewed Engine and Catalog commits.
  The work order names no approved final SHAs; these are required for final
  cross-component acceptance.
- [ ] Actual full-archive qualification requires the accessible original ZIP or
  the complete Catalog parts. The 533,064,680-byte source is absent from this
  installation; synthetic fixtures do not establish full-data coverage.

### Remaining work outside this increment

- [ ] Follow Engine capability delivery with truthful Solo interface states for
  requirements, active work, interruptions and outcomes (shared DEV-25).
- [ ] General freeform/combat adjudication, calendar advancement and the complete
  institutional cycle depend on Engine delivery; C2's 121 requirements are not
  claimed as implemented or passed.
- [ ] Hosted accounts, public hosting, Co-op, the AI network, Workshop and
  Marketplace remain planned or deferred.
- [ ] Coordinator review and isolated joined qualification precede integration
  into IRGS. Only the coordinator publishes joined component updates.

## Verification

After intentional source changes, refresh only App's integrity record:

```bash
python3 -B tools/refresh_component_releases.py --component app
python3 -B tools/verify_components.py --component app
python3 -B -m unittest discover -s IRGS_Web/tests -v
node IRGS_Web/tests/test_gameplay_ui.js
python3 -B -m unittest discover -s tools/tests -v
```

Component verification requires committed dependency pointers to match the
checked-out submodules. Hash refresh establishes source identity, not behavior.
Report test counts and platform skips explicitly. Synthetic DOM checks and
browser checks are separate evidence; neither establishes full archive content
verification or coordinator approval.

### This increment's executed checks (2026-10-22)

- Web: 159 run, 152 passed, seven Windows PowerShell launcher skips on Linux.
- Interface: 72 checks passed using the synthetic DOM and delayed transport.
- App tooling: one attachment-exclusion test passed.
- Existing pinned Engine ZIP reader: six tests passed.
- Chromium: Player boundary, Creator navigation, attachment/retry, literal
  search, escaped source detail, protected deep-link reload and return to Player
  passed with synthetic source and temporary saves; zero POST requests or saves.
- Refreshed only App hashes and passed App/Engine/Catalog component integrity.

Qualified here with existing pins: Engine
`2c5590bcb2d7ee7e02f597526c3cb341841bd2dd`, Catalog
`c70dc16d4e48493b833dba5a0f68f43a972bdcb5`.
Final multipart pins, actual full-archive verification, Windows execution and
joined integration are not claimed. See [coordinator report](COORDINATOR_REPORT.md).
