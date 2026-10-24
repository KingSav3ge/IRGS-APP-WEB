# App theme and usage delivery — 24 October 2026

This increment restores the intended base presentation and connects Genre/Campaign
themes. The preferred warm charcoal/brown base and bronze/coral accents replace
legacy global green overrides. Seven genre palettes use only public campaign
bindings. Century of Conflict, A Scot's Tale and Rise supply explicit campaign
accents. Application pages keep the base; unknown bindings fall back to it.
Reading mode remains independent, and stale campaign responses cannot repaint a
newer selection. No campaign save, rule or dependency source changes.

The next App backlog item also ships: Creator → AI Network → Usage & Budgets,
backed by session/Origin/Creator-protected `GET /api/ai/usage`. This is an allowlisted
read-only projection of Engine's existing ledger, not a second accounting authority.
Lifetime budget/reservations and occupied slots are shown alongside at most 50
recent attempt identities, reported tokens, failures and uncertain states. Missing
reports and actual charges remain unknown. Request text, context, raw result,
private certificates, credentials and storage paths are omitted. Reads cannot
retry inference, refund reservations or reset Engine's budget. Read failures
return a bounded retryable error without private database details.

Validation: 190 Web tests run, 183 passed, seven Windows PowerShell skips;
93 interface checks; seven new real-ledger HTTP tests included in Web; one packaging
tooling test. Real Chromium passed seven genres, three campaign overrides,
Dark-to-Parchment/reload behavior, body text and visible Story surfaces/controls contrast at least 4.5:1 across
Dark, Light and Parchment modes, protected accounting and 390px layout. Browser POSTs and
errors: zero. Synthetic saves stayed byte-identical. Only one offline fixture
attempt seeded accounting before browser launch; no live provider call was made.
App hashes and both exact committed dependencies verified.

Exact dependency pointers stay Engine `8234044c089131314019ecaf6799a2f08028a3f8`
and Catalog `401df26a1f16be864dd15d7c5250da5d75f8ccca`. App began from coordinator
version commit `277554aac21a092b8a55562309da274bbe74a3af`. Delivery response supplies
the full pushed App SHA. Only `KingSav3ge/IRGS-APP-WEB/main` is pushed here.

Reproduce: `python3 -B -m unittest discover -s IRGS_Web/tests -v`,
`node IRGS_Web/tests/test_gameplay_ui.js`,
`node tools/qualify_presentation.js /tmp/irgs-presentation.json`, and
`python3 -B tools/verify_components.py --component app`.
Playwright and Chromium are required only for browser qualification. The qualifier
owns temporary synthetic campaigns and removes its host; no private user save is
opened. Structured evidence: [THEME_USAGE_VALIDATION.json](THEME_USAGE_VALIDATION.json).

Next: operator-controlled direct-adapter startup through the existing host/launcher,
then conditional live qualification when an approved route, finite budget and
credentials are supplied. Live quality, semantic/voice review, billing reconciliation,
general narration/dialogue and wider rules remain unfinished. Joined integration
belongs to the coordinator. The previous reviewed Solo foundation evidence follows.

---

# App primary-update review — IRGS 3.4.0 development

The App now connects the delivered Engine proposal API to explicit player review and the existing authored-scene and Rise action handlers. The coordinator closed a Rise integration gap: settlement proposals are recognized in status and review, and committed results use their actual action kind and settlement elapsed spans. No new simulation rules are introduced.

Selected dependencies:

- Engine: `8234044c089131314019ecaf6799a2f08028a3f8`.
- Catalog: `401df26a1f16be864dd15d7c5250da5d75f8ccca`.

Fresh qualification passed 176 of 183 Web tests, with seven Windows-only skips, all 86 interface checks, and 13 focused authored-scene/Rise HTTP bridge tests. Chromium exercised five consecutive Rise proposals and explicit acceptances through real Core work completion, with a deliberately lost acknowledgement, saved-result recovery and reload. Total elapsed work was 3,900 seconds; no private oracle appeared and there were no page errors. Offline provider calls: five; live calls: zero.

Keys and routing are server-only explicit configuration. Default local hosting keeps assistance unavailable. The direct adapter exists in Engine, but no credentials, eligible workload/budget or live model-quality result are supplied by this update. General narration/dialogue, freeform/combat resolution and wider C2 remain unfinished. This is a viable bounded offline foundation update; it is not a completed live AI release.

[Machine-readable review](COORDINATOR_PRIMARY_REVIEW.json) records inputs and source hashes. Original component evidence remains in `SOLO_RUNTIME_VALIDATION.json`; the earlier pending Rise limitation is superseded by this qualified adapter. Joined import still requires the coordinator's exact three-component approval and isolated candidate tests.
