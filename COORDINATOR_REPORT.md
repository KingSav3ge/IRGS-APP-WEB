# App report to IRGS Enviroment — historical-details-01

Date: 2026-10-22. Repository: `KingSav3ge/IRGS-APP-WEB`, delivered on `main`.
This is an implemented App increment; full cross-component work-order acceptance
remains blocked. The delivery response provides its exact pushed commit SHA.

## Changed behavior

Historical Details is the Creator reference entry, retaining its existing route
and API bookmarks. Unattached, incomplete, corrupt and unavailable sources have
separate messages and a read-only retry. Search and detail retries retain literal
query, collection and source-row identity. Source prose, original records,
uncertainty, citations and rights remain escaped reference data.

Explicit ZIP registration can be added or repaired without restarting the host.
An invalid explicit source is never silently replaced by another archive. Status,
search, detail and retry require Creator mode, the local session and valid origin.
Navigation and inspector-close guards discard older responses. These operations
receive no campaign store and create no events, worlds, knowledge or save changes.

Catalog source selection uses the manifest pin from its release record and an
ignored App installation cache. The adapter targets the Engine's proposed
`from_catalog_manifest(manifest_path, manifest_sha256, cache_dir=...)` API. The
currently pinned Engine has no such API, and the pinned Catalog has no multipart
payload. The optional path fails closed; it does not expose placeholder metadata
as an archive. Failure-code mapping/retry is tested with a test double, not actual
multipart assembly. The complete/missing/corrupt multipart combination still
requires the delivered Engine and Catalog commits.

## Dependency commits

- Engine: `2c5590bcb2d7ee7e02f597526c3cb341841bd2dd`.
- Catalog: `c70dc16d4e48493b833dba5a0f68f43a972bdcb5`.
- Both existing qualified pins are preserved. No Engine/Catalog source, other
  component repository or joined IRGS was changed or pushed.

## Checks executed

| Check | Result |
| --- | --- |
| `python3 -B -m unittest discover -s IRGS_Web/tests -v` | 159 run; 152 passed; seven Windows PowerShell launcher skips on Linux |
| `node IRGS_Web/tests/test_gameplay_ui.js` | 72 passed; synthetic DOM/transport |
| `python3 -B -m unittest discover -s tools/tests -v` | One passed; local attachments excluded from release pins |
| `python3 -B -m unittest discover -s Engine/IRGS_3_3/runtime -p test_historical_archive.py -v` | Six passed; existing explicit ZIP interface |
| Headless Chromium/Playwright against a temporary synthetic host | Passed Player/Creator boundary, attachment/retry, literal search, escaped detail, protected deep-link reload and return to Player; zero POSTs, save files or browser errors |
| `python3 -B tools/refresh_component_releases.py --component app` | Only App source hashes refreshed |
| `python3 -B tools/verify_components.py --component app` | App, pinned Engine and pinned Catalog integrity verified |

The ten historical-reference HTTP cases are included in the Web count. They
cover session/origin denial, local ZIP recovery, unchanged source/save data,
literal lookup, metadata-only rejection and the isolated multipart error contract.

## Open findings and missing input

1. No exact coordinator-approved final Engine/Catalog SHAs were supplied or
   published in the work order. The Engine chat stopped at its usage limit before
   publishing its multipart reader. Do not move dependency pins based on an
   unpublished implementation or infer coordinator approval from a branch head.
2. The actual 533,064,680-byte Grand Archive and complete Catalog parts are absent.
   Actual reassembly, full-data collection coverage and missing/corrupt real part
   checks remain unrun. Synthetic tests establish only their stated scope.
3. Windows launcher execution, the complete Engine runtime suite and joined
   assembly/package qualification were not run for this App increment.
4. This session can inspect chat status but has no tool to message IRGS Enviroment
   directly. This repository report is the handoff; no direct message is claimed.

Next: coordinator selects reviewed Engine/Catalog commits after delivery, App
pins and tests exactly that pair, then coordinator reviews the App commit and
qualifies the isolated joined assembly. No unified source integration is requested
or performed by this App chat.
