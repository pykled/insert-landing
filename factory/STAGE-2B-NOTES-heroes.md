# Stage 2B notes: heroes (maker 2B-1)

Owner of `factory/templates/heroes/**` only. Everything below that touches another file is a request, not a change.

## What exists

Ten hero pairs (`<id>.j2` + `<id>.css.j2`): `cinematic` (port of `previews/stonehurst/index.html`), `crest-centred`,
`inset-caption`, `panel`, `silent`, `inset-wide`, `landscape-silent`, `arch-split`, `pair-split`, `slideshow`.
Shared helpers, underscore-prefixed so `lib/templates.py` never mistakes them for heroes:

- `heroes/_shared.css.j2`: fact list, the date band under the photo (`.hero-dateband` + `partials/date-inline.j2`
  row styles), reduced-motion branch for `.hero-anim` / `[data-motion-device]`.
- `heroes/_facts.j2`: `year / acres / guests / spaces` from `v.vibe.era` and `v.tagline_facts`, each wrapped in
  `data-fact` (contract 4.1); nulls omitted.
- `heroes/_h1.css.j2`: the headline rule. `display_case == 'caps'` (or a caps-only pairing without a secondary) renders
  tracked caps 26-40 px; otherwise sentence case in the display face or, for caps-/wordmark-only pairings, in
  `pair.secondary`; never below `pair.display.min_px`; 400-weight faces with `min_px >= 36` get a 48 px floor on mobile.
- `heroes/_ornament-slot.j2`: renders `ornaments/<ornament>.j2` with `slot='hero'` (used by `crest-centred` above the
  name and by `panel` inside the deep panel). **`base.html.j2` must not also include the hero slot**, or the crest /
  double-line frame appears twice.

Verification builds: `.factory-check/heroes/build-heroes.sh` (16 builds: every hero through each dialect that allows
it), `.factory-check/heroes/qa-all.sh`, `.factory-check/heroes/shoot.py` (contact sheet at 1440 + 390).

## Judgement calls the checker should know about

1. **Two stacked scrim gradients** on `cinematic` (left 35 -> 0 and bottom 0 -> 35) and `crest-centred` (vertical
   10 -> 35 plus a radial pool 35 -> 0 under the centred copy). No single stop exceeds 35% black (25% in candlelit),
   which is what E9 and the baseline measure; where the layers overlap the effective darkening reaches ~50-58%. The
   mock did the same with much heavier layers (92%). If stage 3 reads the rule as "35% effective", drop the second
   layer; the contrast numbers below get worse.
2. **Cinematic on mobile** no longer puts copy on the photo: the photo stands alone (66svh) and the copy + date card
   sit on paper under it. With a 35% cap the mock's mobile treatment (copy on the upper half of the photo) cannot
   pass 4.5:1 on any daylight lead.
3. **`cinematic` in candlelit** keeps a 25% gradient even on a `light: night` lead (the contract says "none on dark
   photos"). Stonehurst's greenhouse-at-night glows exactly where the copy sits (h1 measured 1.02:1 with no scrim).
4. **Text-on-photo contrast is content-dependent and still fails on Stonehurst's leads** (barn, flower garden): QA
   reports 2.3-4.7:1 on cinematic / crest-centred desktop copy. Every Stonehurst lead is a bright daylight photo; the
   spec's full-bleed rule ("only if the lead shows the building", estate; "golden hour", ranch) assumes a lead that is
   dark in the copy zone. Suggest stage 3 adds a per-photo "dark lower third" signal to `needs` for `cinematic` and
   `crest-centred`, or routes such leads to `frame` / `inset-caption`. Everything else in those heroes passes.
5. **`silent`**: the contract wants "the nav bar at the foot of the hero". The header is rendered by `base.html.j2`
   (sticky, top), which this maker cannot move, so the foot bar carries the headline (h1), the kicker + facts line and
   one outlined Inquire. Duplicating nav links there would count toward E14.
6. **`pair-split` b/w photo**: Stonehurst has no `mono: true` photo. The hero takes the first non-lead photo whose
   `subject` is building / interior / detail (spec 2.8 allows mono for architectural photos) and renders it through
   `filter: grayscale(1) contrast(1.05)`; the lead stays in colour. A `mono: true` photo wins when present.
7. **`slideshow`**: user-advanced only, `data-autoplay="off"`, cross-fade `t.motion_device_ms` (1200 ms default), no
   transition under reduced motion, first frame shown without JS. Counter / arrows / caption sit on paper under the
   photo, so no text sits on the photo and no scrim is needed. The hero uses `data-slide-counter`, not
   `data-counter`, and does not define `window.__slideTo`: those are the `slideshow-counter` moment's (contract 1.3).
8. **Facts in the first screen** on the tall heroes (`silent`, `landscape-silent`, `slideshow`): the photo height is
   `min(100svh - 150..250px, 680..740px)` so a hairline facts strip lands above 900 px at 1440x900.
9. **`arch-split` wash** renders only when `ornament == 'watercolour-wash'` (one device per page), as
   `radial-gradient` of `color-mix(var(--accent) 8%, transparent)`.
10. **Mobile h1 sizes go through the base's `--h1-size`**: `css/responsive.css.j2` (base maker) sets every dialect h1 below
    600 px to `max(var(--h1-floor), var(--h1-size))`, which out-specifies a hero class. The h1 helper and the per-hero
    mobile rules therefore set `--h1-size` as well as `font-size`; the base floor (48/56 px for thin faces) still wins.
    Because of that floor the **crest hero's h1 is the headline**, not the venue name: a 56 px tracked-caps
    "STONEHURST" cannot fit 360 px. The name is a `p.crest-name` (the header carries the name anyway).
11. **Crest-centred on mobile** follows cinematic: photo alone, crest block on paper under it.
12. **Mobile `sizes`** on the full-bleed heroes is `(max-width: 860px) 160-180vw, 100vw` because the cover-cropped box
    is taller than wide; without it QA flags the 1200 px source as soft on a 2x phone.

## Requests outside my paths (stage 2A / base / other makers)

- `tests/test_templates.py::test_real_filesystem_statuses` asserts `not TPL.exists('hero', 'crest-centred')` and
  `test_dialect_build_falls_back_and_records` forces `hero=crest-centred` expecting a fallback: both now fail by design
  because the hero exists. 53/55 pass; stage 2A owns the tests. `lib/templates.py --refresh` was run (statuses in
  `data/dialects.json` now say `exists`; the data diff is left uncommitted for the integrator).
- `moments/crest-reveal`: `h2.mo-crest-name` (15 px, .32em tracking) overflows a 390 px viewport by 15 px on the estate
  builds (the only horizontal overflow QA finds on any hero build), and its SVG "S" measures 1:1 contrast.
- `ornaments/crest-roundel`: the header/footer "S" initials measure 3.7:1 (22 px, below 4.5).

- `build.py` `hero_sizes` (the `<link rel=preload imagesizes>`) only knows `masthead`, `cinematic`, `frame`; every
  other hero gets `(min-width: 861px) 46vw, 100vw`, so Chrome preloads the 1200 px file and then fetches the 1800 px
  one ("preloaded but not used" console warning on inset-caption, slideshow). Suggested map: `100vw` for
  `crest-centred`, `silent`, `landscape-silent`, `slideshow`; `(min-width: 1400px) 1280px, 90vw` for `inset-caption`;
  `(min-width: 1200px) 1120px, 90vw` for `inset-wide`; `(min-width: 861px) 50vw, 100vw` for `panel`;
  `(min-width: 1140px) 520px, (min-width: 861px) 46vw, 100vw` for `arch-split`, `pair-split`.
- Pairing `candlelit-forum`: Forum 400 fails the hairline probe at 40 px (45% of the letterform <= 1 px, desktop and
  mobile) and the caps band tops out at 40 px. Contract 3.2 says drop the pairing rather than loosen the probe.
- Pairing `coastal-engraved`: Josefin Sans 500 caps h1 at 26 px still reports 57% hairline on mobile; `max_px` 30.
- `estate-caslon` / `botanical-cardo`: 400-weight display at 40-48 px warns (23-31% hairline); the helper already
  floors mobile at 48 px.
- Stonehurst content: `terrace`, `reception`, `stonepath` sources are 1600 px, below every bleed hero's 2400 px need;
  the test builds use `barn` / `greenhouse` / `hero` for bleed heroes.
- Not mine, seen in every QA run: `E16 body text 15.5px` (spaces section blurbs), `E16 line length 73` (story
  pullquote), `E5 tracked caps 67 chars` (story cite), `H2 below pairing minimum` on mobile (base h2 clamp),
  `crest-reveal` moment SVG text contrast, `H3 Josefin at 12px` (footer headings), `ornament -> none` fallbacks.
