# App primary-update review — IRGS 3.4.0 development

The App now connects the delivered Engine proposal API to explicit player review and the existing authored-scene and Rise action handlers. The coordinator closed a Rise integration gap: settlement proposals are recognized in status and review, and committed results use their actual action kind and settlement elapsed spans. No new simulation rules are introduced.

Selected dependencies:

- Engine: `25e45945f9bb73d041a9d948d577a9240310da90`.
- Catalog: `2e4f389882df0807fc8064c1a0b533aaa3b1bcd3`.

Fresh qualification passed 176 of 183 Web tests, with seven Windows-only skips, all 86 interface checks, and 13 focused authored-scene/Rise HTTP bridge tests. Chromium exercised five consecutive Rise proposals and explicit acceptances through real Core work completion, with a deliberately lost acknowledgement, saved-result recovery and reload. Total elapsed work was 3,900 seconds; no private oracle appeared and there were no page errors. Offline provider calls: five; live calls: zero.

Keys and routing are server-only explicit configuration. Default local hosting keeps assistance unavailable. The direct adapter exists in Engine, but no credentials, eligible workload/budget or live model-quality result are supplied by this update. General narration/dialogue, freeform/combat resolution and wider C2 remain unfinished. This is a viable bounded offline foundation update; it is not a completed live AI release.

[Machine-readable review](COORDINATOR_PRIMARY_REVIEW.json) records inputs and source hashes. Original component evidence remains in `SOLO_RUNTIME_VALIDATION.json`; the earlier pending Rise limitation is superseded by this qualified adapter. Joined import still requires the coordinator's exact three-component approval and isolated candidate tests.
