# Separate grant review controls

The response composer consumes the existing Engine grant-attempt prerequisite
DTO for the controlled actor. It presents separate request and acceptance review
buttons only when those Engine capabilities are selected. It does not inspect
private offer eligibility, issuer stock, consent or hidden feasibility, and adds
no rules. Missing/unselected capabilities remain absent in other contexts.

The player supplies exact editable words. Choosing a control without words only
focuses the composer. Review and cancellation commit no world change; only
explicit confirmation calls the existing shared-intent handler. A request can
produce an offer, never permission by itself. Acceptance is a separate reviewed
attempt and Core rejects it when no valid grant exists. Original request receipts
remain immutable after later acceptance, restart or retry.

The controls remain inside the existing composer below the newest story entry,
without adding a nested story pane. The HTTP tests cover actor privacy, a
conserved synthetic contrast, rejection without an offer, separate acceptance
and original-result recovery. tools/qualify_decision_journeys.js exercises normal
quay and Rise creation, actual refusal and conserved delivery, both grant review
controls, cancellation, empty-word no-op, retained drafts and mobile layout.
Only synthetic temporary stores and local Core operations are used. No provider,
native Windows or functional Alpha qualification is implied.
