# Stage 2B-3 notes: moments (maker: Claude Opus 5.5, 2026-10-21)

Owned: `templates/moments/**`, `templates/partials/draw-in.js.j2`. All 8 moments of contract 1.3 exist:
`slideshow-counter`, `crest-reveal`, `sprig-draw`, `numbers-count`, `candle-count`, `then-now`, `pairs-counter`,
`hours-dial` (+ shared `partials/draw-in.js.j2`). Each is `<section id="<id>" data-moment-root>` with the contract hooks.

## Verified
- Builds: `build.py content/stonehurst.json --dialect <d> --lead hero --force moment=<id>` for slideshow-counter
  (modern-luxe, coastal), crest-reveal (estate), sprig-draw (botanical), numbers-count (ranch), candle-count
  (candlelit), pairs-counter (editorial), hours-dial (estate, candlelit); then-now (deco) on the test fixture below.
- `qa.py` moment checks: no moment problems on any build (hooks, counters, data-split, data-dial-hour, draw-in present,
  contrast in the driven state, no running animations under reduced motion). The remaining QA problems are in the
  heroes, base CSS, glance, nav and fonts, which other makers own (see below).
- Playwright: every hook driven at 1440 and 390, no horizontal overflow, contact sheets checked.
- Clean worktree at HEAD + only these files + `lib/templates.py --refresh`: `pytest -q tests` 55 passed. Proof variants
  (`--dialect none`) rebuilt byte-identical (apart from the generator meta).

## For stage 2A / base owners (not changed by me)
1. **app.js aborts the whole end-of-body script** when `#guide-form` is absent (seen on the modern-luxe build:
   `guideForm.addEventListener` on null). That killed every moment hook placed after it. Workaround inside my files:
   each moment inlines its own `<script>` right after its section (`{% set mo_inline = true %}`), and base's
   `moments/<id>.js.j2` include renders nothing (the file is guarded by `mo_inline is defined`). Suggest base.html.j2
   gives each include its own `<script>` tag, or app.js null-guards the guide/tour flows.
2. `data/dialects.json` / `data/archetypes.json` statuses need `python3 lib/templates.py --refresh` (archetypes still
   list hours-dial / numbers-count as `spec`). HEAD already fails `test_real_filesystem_statuses` on story `split`.
3. `build.py MOMENT_NAV`: suggested labels slideshow-counter "The spaces", crest-reveal "The house", sprig-draw
   "The garden", numbers-count / candle-count "In figures", then-now "Then and now", pairs-counter "In pairs",
   hours-dial "The day".
4. Degrading: when data is missing, these moments render no section at all: sprig-draw (no flora photo), then-now (no
   archival photo with rights), hours-dial (no gates_open / event_end), numbers/candle (no numbers), slideshow (< 3
   non-lead photos), pairs (< 4). Normally the builder's `needs` check prevents this, but `--force moment=` skips
   `needs`, and then qa.py's hook step throws (`document.querySelector('[data-moment-root]')` is null). Suggest guarding
   that step in qa.py.
5. The template context `photos[n]` has no `tags`, `light` or `rights`. Moments read `v.photos['items'][n]` for those.
6. QA on the modern-luxe build aborts with a Page.fill timeout in the guide flow before the moment step (other
   makers' guide-form issue), so slideshow-counter was verified on coastal.

## For the other 2B makers (lessons from QA)
- **SVG `<text>`**: QA's glyph contrast probe reports 1.00 unless the text uses `fill: currentColor` with `color:` set
  (crest-roundel / brand-mark initials will hit this).
- **Opaque chips over photos**: E9 reads any element with a solid background over a photo as a "flat scrim". The
  then-now handle is an SVG circle for that reason.
- **Draw-in**: `partials/draw-in.js.j2` is idempotent (`window.__drawIn`) and scans every
  `[data-motion-device="draw-in"]` on the page, rescanning at DOMContentLoaded, so ornaments (double-line-frame) can
  include it too. Strokes are primed only when motion is allowed and IntersectionObserver exists, so the markup's
  final state shows otherwise. Duration comes from `data-draw-ms` (clamped to 600-1600), stagger from
  `data-draw-stagger`, and easing from `t.ease`. `window.__drawFinish()` settles all strokes.

## Test fixture
`factory/content/stonehurst-moments-test.json` (left uncommitted, because the commit scope covers only my paths)
is stonehurst.json with `barn` set to `archival: true, mono: true` and a rights note that says plainly it is a test
fixture. Use it only to exercise then-now. Never publish or register it.
