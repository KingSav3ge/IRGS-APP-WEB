# IRGS App/Website work order — historical-details-01

Assigned by the user through IRGS Enviroment on 2026-10-22. Owner: **IRGS App/Website**. Repository: `KingSav3ge/IRGS-APP-WEB`.

## Current state

The joined baseline selects App `3980e5665814847d3cd02c0f0b86417a231e2be6`. Its Engine and Catalog pins remain the previous qualified set. The Creator Historical Reference browser exists; there is no Catalog multipart payload yet. Catalogue v0.5 has 44 previews, not 44 released campaigns.

## Deliverable

Provide the **Historical Details** reference entry backed by the Catalog's complete manifest and the reviewed Engine reader. Keep technical reference browsing in Creator mode. Explain attached/ready, incomplete, corrupt and unavailable states without claiming that placeholder metadata is the archive. Preserve explicit existing local ZIP attachment support. Do not copy a second editable content tree into App.

Keep campaign discovery and player-known information separate from raw source records. Preserve literal search, paging, original records, citations, uncertainty and safe text/link rendering. New reference controls must not adopt history, initialize a world, submit an event or change a save. Preserve catalogue previews, current Century/Rise launch rules and adopted Kira canon.

## Acceptance

- App pins the exact coordinator-reviewed Engine and Catalog commits; test that combination.
- Creator/session restrictions, escaped source text, stale-request handling and navigation are tested.
- Missing/corrupt part messages and the empty/unattached state are exercised.
- Search/detail/retry remain read-only and work beside current campaign flows.
- Run Web and interface tests; report platform skips accurately.
- Make `DEVELOPMENT.md` reflect completed, active and remaining App work, with valid Catalog paths and separate dependency ownership.

## Delivery and review

Work only in your component repository and push its `main`. Do not publish component source to joined IRGS, change another component, or reset existing work. Read repository instructions and current plans first. Keep completed, active and remaining work explicit. Preserve accurate source attribution and distinguish implemented behavior, design requirements and reference data.

Return the full pushed commit SHA, changed behavior, dependency commits, checks actually executed, skipped/unrun checks, open findings and any missing input to the coordinator chat **IRGS Enviroment**. Update the development plan with that increment. A planning-only commit is not the requested viable component update.

The coordinator reviews exact commits. When Engine, App and Catalog each have an approved viable update for this cycle, and the App pins exactly those Engine and Catalog commits, the coordinator tests an isolated joined candidate and imports it into `KingSav3ge/IRGS/main`. Until then the existing integrated component set remains selected. Changes requested by the user take precedence.
