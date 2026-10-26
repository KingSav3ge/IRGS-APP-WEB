# Emergent interface port — 26 October 2026

The user requested the Emergent preview's interface in IRGS. This delivery adapts
its book-like visual design to the canonical `IRGS_Web` host and its existing
Engine/Catalog contracts. The complete original project remains on
`KingSav3ge/IRGS/Emergent` at `437fa7586385fed14883e3d672ab3e51a9193311`.
That branch has separate Git history; it is a design source, not a merge parent.

The landing page, campaign library, saved-story shelf, reviewed character wizard
and three-column Play view now use local fonts, warm surfaces, compact navigation
and responsive drawers. The 44 concept cards retain their previews and filters.
Historical starts, the fictional founding slice and Kira's reference guide keep
their actual availability. Character fields remain the host's reviewed fields;
appearance supplies no statistics, possessions or simulation capabilities.

The character panel and recent Chronicle use the existing actor-filtered view.
The centre retains explicit action review, editable drafts, unresolved freeform
declarations, typed process controls and original-result recovery. Reading
controls change local preferences. Saved-story cards resume through the filtered
read route and fence navigation after delayed replies. Neither reading nor
opening the character wizard submits a campaign change. The mobile character
and reading drawers close each other and support Escape with focus restoration.

The product still runs with Python's standard library. All new runtime fonts
and artwork are bundled; there are no external asset requests. Font licenses
are in `IRGS_Web/licenses/`, with source/rights references and SHA-256 values in
`IRGS_Web/INTERFACE_ASSETS.json`. Source adaptation is recorded separately in
`IRGS_Web/EMERGENT_INTERFACE_SOURCE.json`. The server serves exact allowlisted
asset names and retains its existing origin, session and content-security policy.

The Emergent project's Mongo backend, hosted accounts, model choices, voice,
payments and alternate simulation are outside this interface delivery. The
canonical host's actual optional assistance and received records determine what
the interface can offer. Wider freeform/combat resolution, full C2 and operator
configuration retain their existing development requirements.

## Exact dependencies and verification

Component edition stays **3.4.1 development**, previous release **3.3.3**, until
a coordinated publication. Engine pin:
`aa30bb63a3828cbaeb5ee3d1db57edd388a8dc86`; Catalog pin:
`526404128830a99fe8ea5c2bce43b6ea7d45fe6f`. Neither component source nor pin changes.

See `EMERGENT_INTERFACE_VALIDATION.json` for this delivery's executed evidence.
Run from the repository root with the pinned submodules available:

```bash
python -B -m unittest discover -s IRGS_Web/tests -v
node IRGS_Web/tests/test_responses.js
node IRGS_Web/tests/test_gameplay_ui.js
python -B -m unittest discover -s tools/tests -v
node tools/qualify_shared_responses.js /tmp/irgs-shared-browser.json
node tools/qualify_process_bridge.js /tmp/irgs-process-browser.json
node tools/qualify_interface_port.js /tmp/irgs-interface-browser.json /tmp/irgs-interface-screenshots
python -B tools/verify_components.py --component app
```

The interface browser check creates one explicitly confirmed historical campaign
inside its temporary synthetic store. It verifies zero writes before confirmation,
unchanged original fixtures, local assets, desktop/390px layout, reference-only
Kira, type filters, reload, drawer focus and zero provider calls. The two existing
browser suites separately verify actual non-Rise/Rise actions and processes,
including lost replies, recovery, explicit acceptance and elapsed work. Windows
PowerShell checks retain their actual Linux skips. No user saves participate.

Unified publication remains a coordinator operation under the repository's
integration and version policy. Publishing the App increment alone does not
claim a new unified release or qualify the separate Emergent backend.
