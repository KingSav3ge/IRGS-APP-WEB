# Emergent reading and navigation refinement — 26 October 2026

This is the first bounded continuation of `APP_DEVELOPMENT_HANDOFF.md`, pulled at
App `1a0bc65dd25a18dfd075b2d603d0351c2d035001`. The original port/design sources,
local assets, licenses and earlier validation records are preserved. Component
edition remains **3.4.1 development**, previous release **3.3.3**. Engine stays
`aa30bb63a3828cbaeb5ee3d1db57edd388a8dc86`; Catalog stays
`526404128830a99fe8ea5c2bce43b6ea7d45fe6f`.

## Reproduced behavior and fixes

The initial real-browser review found the following in the existing port:

- Changing full Reading settings to 22px/light left the Play toolbar showing
  Medium/18px and Dark. The toolbar now updates from the same normalized local
  preferences as the dialog, without rebuilding the Tools panel. Custom sizes
  display their actual value and do not select an unrelated preset. The reading
  group and surface control announce current values and the next surface.
- Quick reading adjustments replaced the focused button and dialog opener,
  leaving focus on the document body. Controls now update in place, retaining
  keyboard focus and the native settings-dialog return target.
- Navigation could remain open over Character/Tools. Choosing a Tools destination
  then left focus on the body. All three drawers now close each other and retain
  their expanded state correctly. A drawer destination receives content focus;
  primary-tab arrow/Home/End navigation still focuses the selected tab. Existing
  dialog Escape handling and drawer-opener focus restoration remain in use.
- The authored opening's small Story label had 1.36:1 contrast on parchment and
  1.67:1 on light paper. Story labels, links and disclosure summaries now use a
  readable accent derived from the actual reading surface and selected palette.
  Pressed reading presets retain readable accents on the dark toolbar. This does
  not replace the genre/campaign palette or change actor-visible facts.

Implementation is confined to `preview.js`, `preview.css` and the existing
preference/navigation hooks in `app.js`. It adds no API route, campaign write,
elapsed span, model dispatch, health/statistic, possession or simulation rule.
Character creation keeps reviewed selection, declaration/testimony status and
explicit final confirmation. Assistance absence still leaves local play usable.

## Qualification

`tools/qualify_interface_refinement.js` uses the real canonical host, temporary
synthetic saves and local Chromium. It exercises these as separate contexts:

1. The existing non-Rise authored opening.
2. Rise's selected founding/work context.
3. A newly and explicitly reviewed historical character start, including a
   canceled character setup before the confirmed creation.

Each runs at 1568px and 390px with dark/light/parchment reading surfaces. Checks
cover settings-to-toolbar synchronization, custom size, focused keyboard quick
controls, dialog/drawer Escape, exclusive drawers, destination and tab focus,
unsent drafts, reload, exact unchanged save bytes and honest local assistance.
Library, Saves, empty Trash/Story and the explicit Creator/player round trip are
also checked. Reading and navigation perform no POST; the qualifier's sole write
is its explicitly confirmed synthetic campaign creation.

Computed Story text, small labels, notes, links, summaries and reading-toolbar
text meet at least 4.5:1 contrast in the tested views. An additional 21 synthetic
genre/surface combinations qualify color portability only; they create no new
campaign capabilities or mechanics. Screenshots are temporary review artifacts.
This is a scoped contrast/focus improvement, not a complete accessibility audit.

The three original browser suites remain: interface port/character review,
shared non-Rise/Rise actions, and typed observation/work with lost replies and
original-result recovery. See [fresh evidence](INTERFACE_REFINEMENT_VALIDATION.json)
for executed commands, actual results/skips and exact source hashes. Earlier
`EMERGENT_INTERFACE_VALIDATION.json` is attributed to the original port.

Run the existing [port checks](EMERGENT_INTERFACE_PORT.md), including:

```bash
node tools/qualify_interface_refinement.js /tmp/irgs-refinement-browser.json /tmp/irgs-refinement-screenshots
```

## Remaining work

The next independent bounded task is protected operator/launcher configuration
for the existing optional Solo service. Communication/source controls await
Engine's matching actor-safe participant and received-source contract. Additional
interface issues require their own reproduction and qualification. Windows
launcher execution, broader accessibility/device coverage, general freeform/combat
and full C2 retain their existing scope. No live inference or user save is used.
Only App main is published here; the coordinator owns joined review, integration
and any version increase. The deferred App-only unified release remains deferred.
