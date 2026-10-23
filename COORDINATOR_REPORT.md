# App report to IRGS Enviroment — historical-details-01

Date: 2026-10-22. Repository: `KingSav3ge/IRGS-APP-WEB`, delivered on `main`.
This implemented App candidate connects the complete Catalog archive to the
published Engine reader. The delivery response gives the exact pushed App SHA.
Coordinator source approval and isolated joined qualification remain separate;
this report does not assert either approval or an integrated release.

## Resulting behavior

The Creator's **Historical Details** entry uses the Catalog release's pinned
manifest and Engine's `from_catalog_manifest(..., cache_dir=...)` API. All 32
parts and the exact original ZIP are verified before records become available.
App owns no reconstruction algorithm or second editable source tree. Derived
ZIPs use an ignored installation cache.

The complete original archive is preserved, including books, assets and its
central database. This browser exposes ten structured reference collections;
its scope text now distinguishes browsing coverage from archive preservation.
Explicit multipart registration receives the correct storage label. Explicit
local ZIP registration remains supported and takes precedence, including when
broken. Registration changes and repaired parts can recover without a restart.

Status, literal search, paging, source details and retries remain Creator/session
restricted. Reading does not adopt history, initialize a campaign, submit an event,
change a save or grant player knowledge. Original records, row/archive identity,
uncertainty, citations and rights retain their meanings and safe rendering.

## Exact candidate dependency pins

- Engine: `b3e7d760a2cf3712292b09328566cf1ed0d78c97`.
- Catalog: `58ce55672bdd75076b94882bd8715a1d2a1f383a`.
- Manifest SHA-256: `1543cd65b5c4b3ed6f160565b4e4bf01d09dd44a392d53c7036efcd5c0dcf21f`.
- Original ZIP: 533,064,680 bytes;
  `51246eb6898a228f42f0794ed19ce69af275a2a4661c0fb6a1d3baebe3efc773`.

These are tested candidate selections for coordinator review, not a claim of
coordinator-approved dependency release. The coordinator's published gate still
marks source review/integration approval pending. Catalog's complete delivery
supersedes the older missing-source observation. No missing archive input remains.
Only App source and its two dependency pointers are published by this chat;
no Engine/Catalog product source or joined repository is changed or pushed.

## Executed checks

| Check | Result |
| --- | --- |
| `python3 -B -m unittest discover -s IRGS_Web/tests -v` | 166 run; 159 passed; seven Windows PowerShell launcher skips on Linux |
| `node IRGS_Web/tests/test_gameplay_ui.js` | 72 passed; synthetic DOM/transport, including stale responses and escaped source text |
| `python3 -B -m unittest discover -s tools/tests -v` | One attachment-exclusion test passed |
| `python3 -B -m unittest discover -s Engine/IRGS_3_3/runtime -p 'test_historical*.py' -v` | 65 passed |
| `python3 -B Catalog/IRGS_Catalog/verify_catalog.py` | Catalog integrity, 44 concepts and the complete archive verified |
| `python3 -B Catalog/IRGS_Catalog/historical_details_package.py verify Catalog/IRGS_Catalog/historical_details/manifest.json` | 32 parts; 5,146 files; 5,145 delivery bindings; ten collection bindings verified |
| `python3 -B tools/qualify_historical_details.py` | Actual exact reconstruction plus real search/detail from all ten collections; six authorization denials; cache reuse; unchanged source and synthetic campaign save bytes |
| Chromium/Playwright against the actual full-data App host | Creator navigation, all ten collection options, literal search, details, retry and protected deep-link reload passed; zero reference POSTs, save changes or browser errors |
| App source refresh and component verification | App hashes refreshed; exact App/Engine/Catalog source identities checked |

The Web count includes seven new HTTP tests using real Engine multipart assembly
with synthetic parts. They exercise missing/corrupt parts before and after caching,
repair/retry, release-pinned default selection, explicit multipart registration,
incomplete metadata, authorization before reconstruction and read-only operation
beside an existing synthetic playthrough and current campaign discovery. Earlier
error-normalization tests still use isolated test doubles; they are not the new
multipart assembly evidence.

[HISTORICAL_DETAILS_VALIDATION.json](HISTORICAL_DETAILS_VALIDATION.json) records
structured evidence and exact source identities. The complete member inventory
includes the delivery manifest itself; it is the one file explicitly excluded
from its own delivery bindings. Checksums establish byte identity, not historical
truth, new rights, provider-processing permission or campaign adoption.

## Remaining review and unrun scope

- Coordinator source review/approval of the exact pair and App commit, followed by
  isolated joined assembly/package qualification. Joined integration stays held.
- Windows launcher execution and the complete Engine runtime suite were not run
  for this App increment. The relevant historical family and all Web flows passed.
- App probes search/detail for a first record in each collection; they do not
  adjudicate every historical statement. Catalog's verifier processes the full
  payload, file bindings and collection row counts.
- AI provider work is now a sequenced, unimplemented AIP-01–AIP-09 backlog in
  DEVELOPMENT.md. The 16 model evaluation cases remain unrun. No paid inference,
  provider keys, active Director network or general narrator is enabled.
- This session has no direct chat-send tool. This repository report is the handoff
  to IRGS Enviroment; no direct message is claimed.

## Coordinator dependency selection

The coordinator reviewed the newer Engine and Catalog source and qualified their runtime pair against this App: Engine `7fe99a55bab7d731674f56d8adde2b84ae73a860`, Catalog `3e898acb2179f18a41d7967817bedf429df29d3f`. The dependency pointers now select that pair. `COORDINATOR_PIN_REVIEW.json` records fresh executed checks and their exact source commits; the subsequent Engine edit changes reference wording only. Joined source/package qualification remains the coordinator’s next gate. Validation excerpts record opaque third-party source identifiers by hash; original archive records retain their provenance.
