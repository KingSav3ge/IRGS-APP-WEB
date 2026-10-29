# IRGS-APP-WEB development guide

Current edition: **3.4.5 Pre-Alpha**. Previous release field: **3.3.3**. Target: functional **4.0.0 Alpha** under ALPHA_4_0_PLAN.md and ALPHA_4_0_ACCEPTANCE.json. All Alpha gates remain open. Next unified edition: **3.4.6**.

This release adopts the user-requested chronological story UI: one reading surface, oldest available entries first, then current choices and the retained response form. Drafts, received statuses, exact result text, source gaps and original request recovery remain. App UI implementation: `7d687616b588b2fda3c4f58d445f82d5a13111e9`; exact release pins are recorded by the coordinator in joined COMPONENTS.json. Engine/Catalog product behavior is the qualified 3.4.4 baseline; their current release changes align guides and edition metadata. This is not a new Alpha or gameplay-resolution claim.

Develop IRGS across campaigns and themes, retaining one authoritative Core, nine K owners and the existing six Director categories. Rise R00 is one fictional regression slice. Ordinary speech remains received testimony; an offer is not consent or fulfillment. Storage revision, causal sequence, elapsed work and civil time remain distinct. Full C2, wider autonomous NPC/institution decisions, needs/recovery, selected conflict and sustained AI play remain unfinished. Historical Details is complete; preserve original archive records and canon.

Read AGENTS.md, CHAT_CONTINUATION.md and COORDINATOR_WORK_ORDER.md. The continuation and work order are the current implementation instructions; dated evidence retains its original source selection.

## Current task

**A4-APP-01: protected operator/provider setup, then A4-APP-03 supported-intent review.**

Implement server-side operator configuration with validation, exact eligible model/capability selection, finite budget and non-secret readiness feedback. Preserve local offline play. Then consume Engine’s supported-intent DTOs so a player can review supported execution or retain an explicitly unresolved declaration. Preserve the continuous chronological tale, inline response form, editable drafts, explicit review/cancel/confirm, source status and lost-response recovery. Do not rebuild the former nested history/dashboard layout.

## Verification

Use Python 3.12+ without -O and Node 20+. Start with:

```bash
python -B tools/verify_components.py --component app
node IRGS_Web/tests/test_gameplay_ui.js
```

Run relevant runtime/Web tests and real browser/HTTP journeys for changed behavior. The external historical save fixture is excluded; native Windows checks remain unqualified on Linux. No live-provider quality claim follows from synthetic transport. Keep QA logs and packages outside source. Inspect any integrity failure; refreshing hashes is not a test.

App pins Engine/ and Catalog/ explicitly. Initialize absent dependencies and move only clean dependencies to the committed pins, preserving local work. A new pin needs its own compatibility checks. The coordinator imports one exact approved set through the integration gate, captures fresh execution evidence, runs joined and clean-package qualification, and increments every unified main push.

The canonical runtime remains IRGS_3_3/ and the canonical App IRGS_Web/. Preserve saves, personal configuration, Git history, original archives and accurate evidence; superseded generated distributions can be removed after replacement qualification.
