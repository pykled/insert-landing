# Stage 2B notes: ornaments + base template / css (maker 2B-4, 2026-10-21)

Owned paths: `templates/ornaments/**`, `templates/base.html.j2`, `templates/css/**`. Everything else below is a request
to whoever owns the file. Builds + QA logs used here: `.factory-check/ornaments/<id>/`, `.factory-check/qa-<id>.log`,
`.factory-check/b-<id>.log`; tools in `.factory-check/tools/` (`build-ornaments.sh`, `qa-ornaments.sh`, `shots.py`
contact sheets, `probe.py` hairline share per face/size).

## What base.html.j2 / css now do (dialect builds only; `--dialect none` renders byte-for-byte as before, verified a/b/c)

- `<body data-dialect data-ornament data-motion data-paper data-paper-tone data-photo-edge ...>`.
- Ornament css included once after the section css; the ornament `.j2` is included by base at these slots, all with
  `from_base=true`: `header` (after `</header>`), `hero` (after the hero), `story` and `tour` (before that section, with
  `section_label`, `section_index`, `section_total`), `facts` (after `#facts-strip` / `#glance`), `footer` (before `<footer>`).
- Placement gate (`ornaments/_lib.j2` `place(slot, want)`): a shared namespace `orn` caps placed instances at 3 and renders
  each slot name once. A hero/section that includes the partial itself (`{% with slot='hero' %}` etc.) renders first and
  wins over the base position for `hero`, `facts` and `section-head`. For `story` / `tour` base renders first, so an
  inner include of those slots only renders when the device does nothing at base level (botanical-engraving,
  double-line-frame, stepped-frame, underline-bar render inside only). Use `slot='section-head'` inside sections (always
  honoured, <= 3 total). Optional variables: `align='center'`, `lead_em` / `lead_caps` (italic-lead-in), `bar_text`
  (underline-bar), `counter_index` / `counter_total` (counter), `section_label` (vertical-label; renders nothing without one).
- Dark set: `.btn` labels use `var(--on-accent, #fff)`, fields `var(--field, #fff)`, `.band-deep` / `.btn-light`
  use `--on-deep` / `--deep`, `.band-ink` text uses `--paper`. `responsive.css.j2` (included last) also overrides the
  hard-coded `#fff` in `sections/guide.css.j2` (`.guide-band`) and `moments/light-shift.css.j2` (night state).
- Display floors: `--h1-floor` (pairing minimum, or the hairline-safe size for weight-400 sentence faces: 56 px for Forum,
  Libre Caslon Display, Italiana, Instrument Serif; 48 px for the rest, measured with `probe.py`), `--h1-min` (pairing
  minimum only), `--h2-floor`; `--h1` / `--h2` clamp from them. On <= 600 px every `h1` renders at
  `max(--h1-min, --h1-size)` and every h2 (except `.card h2`, `.card-title`, `.display-2`) at `max(--h2-floor, --h2-size)`:
  set `--h1-size` / `--h2-size` on a heading to go larger. `.card h2` / `.card-title` and `h3` use the secondary face
  (`--display-2`, `.display-2`) when the pairing has one, else the body face. `.foot-h` is in the body face.
- E16: `.card .sub`, `.confirm p`, `.hold`, `.slot-empty`, `.picked`, `.glance-item p`, `.tour-notes`, `.sched-notes li`,
  `.foot-grid p/li`, `.index-row .use/.blurb` >= 16.5 px; `main :where(p:not(.fine):not(.cap)) { max-width: 72ch }`.
- Motion: `.reveal` uses `--reveal-ms` / `--reveal-offset` / `--ease` from `t` (`fade-up` and `slide` translate by the
  offset); reduced-motion branch unchanged. Kicker `small-caps` branch (+ 48 px hairline above in coastal); photo edge
  `arch` (hero photo only) / `rounded`; deco `mono` photos: `.ph.mono img`, `.ph[data-mono] img`, `img.mono`, `img[data-mono]`.

## Ornaments (25 ids of contract 1.4, all exist; `lib/templates.py --refresh` run but `data/dialects.json` is not mine to commit)

Every SVG inline, `aria-hidden`, <= 40 lines, colours from tokens (`--metal` with `--accent` fallback, `--line`,
`--accent-text`, `--ink`, `--on-deep`). Draw-in devices (crest rings, double-line frame, sprigs) animate
`stroke-dashoffset` with `pathLength="1"`; the base state is the final state so `animation: none` (QA freeze,
reduced motion) shows them complete. Contact sheets: `.factory-check/ornaments-sheet-1440.png`, `-390.png`.

QA per forced build (`build.py ... --force ornament=<id>`), problems left are not in my files unless marked **mine**:
- botanical-line, leaf-rule, watercolour-wash, rounded-arch: PASS (0 problems).
- drop-cap, italic-lead-in, vertical-label: only the `hero-1800.webp` preload console warning (hero / build).
- crest-roundel, double-rule, keyline-frame, small-caps-kicker (estate, crest-centred hero): contrast of `.crest-loc`,
  `.crest-btn`, `.crest-sub` on the photo, E9 flat scrim on `.crest-media`, h1 at 40 px (Libre Caslon fails the 1x probe
  below 56 px: use `var(--h1-floor)` as the clamp minimum in `heroes/_h1.css.j2`).
- candlelit (double-line-frame, botanical-engraving, brass-rule): silent hero h1 at 40 px (Forum needs >= 56 px at 1x and
  2x, measured 0.35 / 0.38 hairline share at 40, 0.06 / 0.14 at 56); `[date error]` `.btn-accent` 6.98:1 (dark palette
  `accent-fill` vs `on-accent` is 0.02 short: palette.py margin); panel hero copy padding is smaller than the frame
  inset, so the inner frame line touches the headline at the left: give `.panel` copy >= 32 px padding or set the frame
  insets smaller.
- modern-luxe (hairline-grid, counter): qa.py crashes in the guide flow (`#g-email` missing: the modern-luxe section plan
  has no guide form); nothing measured after that.
- coastal (compass-rose): Josefin Sans h1 hairline warning only.
- ranch (olive-band, rope-rule, wood-keyline, brand-mark): cinematic hero `.cine-meta` contrast on the photo; light
  palette `[date error]` `.btn-accent` 6.55:1 (`accent-fill` vs #fff, palette margin).
- deco (underline-bar, stepped-frame, sunburst, geometric-rule): an unnamed h2 at 40 px (`sections/uses.css.j2`
  `.uses-band h2 { clamp(28px, 3vw, 40px) }` is below Big Shoulders' 48 px minimum); pair-split `.pair-num` contrast 3.7.

## Requests to other owners

- `tests/test_templates.py`: `test_real_filesystem_statuses` and `test_dialect_build_falls_back_and_records` assert the
  pre-2B state (crest-centred must not exist); they fail now that the heroes exist (53 other tests pass).
- `pairings.json`: add `hairline_floor_px` (56 Forum / Libre Caslon Display / Italiana / Instrument Serif, 48 Cardo,
  Gloock, DM Serif Display); base reads it when present. Consider dropping `candlelit-forum`: 56 px mobile h1 is large.
- `palette.py`: `accent-fill` vs its label is 6.55 (light) / 6.98 (dark) in the date-error state; fit with a margin.
- heroes: use `var(--h1)` / `var(--h1-floor)` for the h1 minimum; set `--h1-size` when you want a bigger mobile h1.
- story-split's `slot='story'` wrapper makes any placed root absolute: only botanical-engraving renders there (by design).
