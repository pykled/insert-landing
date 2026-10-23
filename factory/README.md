# Insert venue site factory

Static, mobile-first venue homepages from one content file + a dialect + a personality vector. Python 3.9, Jinja2,
Pillow, numpy, Playwright (QA only). No build framework, no other runtime dependency.

```
factory/
  build.py              content.json -> dialect -> personality -> index.html, img/*.webp, build-meta.json
  qa.py                 Playwright gate: contrast under every glyph, legibility probe, overflow, images, flows,
                        spec exclusions E1-E19, reduced motion, template fallbacks, diversity + screenshot pHash
  build-all.sh          the three Stonehurst proof variants (pre-dialect: --dialect none)
  STAGE-2B-CONTRACT.md  the templates stage 2B owes: files, context, QA hooks
  lib/color.py          OKLab/OKLCH <-> sRGB, WCAG contrast, gamut clamp
  lib/palette.py        k-means on the venue's photos -> accessible token set (every pair verified >= 7:1 for small
                        text); dialect paper ranges; the charcoal (dark) set; photo signals for dialect scoring
  lib/personality.py    6 axes -> tokens; dialect scorer + axis clamping; fit-ranked selection with the guard inside
  lib/templates.py      which template ids exist; nearest-existing fallback; --missing / --refresh
  lib/fingerprint.py    fingerprint (schema 2), weighted distance, same-dialect rule, quota, registry, matrix CLI
  lib/phash.py          16x16 DCT pHash of the fold and the full-page rhythm strip (numpy + Pillow)
  lib/exclusions.py     spec 05 section 5 exclusions as checks over a DOM snapshot (used by qa.py)
  lib/schema.py         content / voice validation; lib/schema.md is the schema
  lib/fonts.py          pairing rules + build-time Google Fonts verification (cached for offline builds)
  lib/images.py         responsive WebP ladders, never upscaled, size-budgeted
  data/dialects.json    the eight luxury dialects (axis clamps, palettes, allowed ids with status, rhythms, motion)
  data/pairings.json    29 vetted Google-font pairings with pinned weights/opsz and legibility notes
  data/archetypes.json  heroes, sections, moments, voices with axis positions and honest build status
  data/voices.json      copy presets (facts come from content slots, never from the preset); CTA sets
  data/registry.json    fingerprints + pHashes of every site built so far (schema 2)
  data/fonts-verified.json  last successful fonts.googleapis.com check per import string
  templates/            base, css, partials, heroes/, sections/, moments/ (stage 2B adds ornaments/ and more)
  content/              one JSON per venue
  tests/                focused tests (tests/README.md)
```

Build one site (dialect scored from the photos and the content `vibe` block; axes clamped to the dialect):
```
python3 build.py content/stonehurst.json --variant d --out ../.factory-check/d --lead flower
python3 build.py content/stonehurst.json --variant e --out ../.factory-check/e --dialect estate --lead greenhouse \
  --personality formality=90,scale=70 --register
```
`--dialect auto` (default) picks the top of the score table, `--dialect <id>` is a recorded human override,
`--dialect none` is the pre-dialect path (needs `--personality`). The score table, clamps, palette checks, every
template fallback and the guard verdict land in `build-meta.json`. `--force dim=id` also accepts `ornament`, `rhythm`,
`tone`, `nav` and `bottom`, and must name an id the dialect allows. `--allow-close "<reason>"` registers past a refusal and stores the
reason. `--offline-fonts` skips the network check (cached verification only); `--strict-fonts` fails when an import
cannot be verified at all.

Rebuild the proof variants (published output in `previews/stonehurst-variants`; redirect for a regression check):
```
FACTORY_OUT=../.factory-check/stonehurst-variants ./build-all.sh
```
QA a build (needs `python3 -m http.server 4821` in ~/projects/insert; `--strict` makes template fallbacks fail):
```
python3 qa.py ../.factory-check/stonehurst-variants/a
```
Distances between everything registered: `python3 lib/fingerprint.py data/registry.json --matrix`.
What stage 2B still owes: `python3 lib/templates.py --missing`. Tests: `python3 -m pytest -q tests`.

Heroes that set copy on the photo declare `needs.copy_zone`; build.py measures every photo (`copy_zone` in build-meta) and
excludes them, or switches crest-centred to copy on paper, when the lead is under 4.5:1 below the 35% scrim cap.
Stage 2C integration notes: `STAGE-2C-NOTES.md`. Stage 2D (open items: candlelit pairings, measured hairline floors in
pairings.json, page-bottom variants in `templates/bottoms/` via dialects.json `bottoms` + `--force bottom=`, archetype
status refresh, cinematic blur veil): `STAGE-2D-NOTES.md`.

Design docs: `../docs/venue-site-factory.md` (system; section 9 is the dialect layer), `../docs/venue-design-research.md`
(research synthesis), `../docs/research/04-luxury-venue-vocabulary.md` + `05-luxury-dialects-spec.md` (dialects),
`../docs/research/*.md` (cited source notes), `../docs/qa-calibration.md` (legibility probe calibration).

## Demo pipeline (venue URL to private preview)
`factory/new-demo.sh <venue-url> <slug>` runs intake (`intake/intake.py`: polite crawl, stated facts with source URLs,
largest photos + scorer signals, draft + report) -> human review (`intake/curate.py` contact sheets and photo naming) ->
`lib/schema.py` + `intake/score.py` -> `build.py --dialect auto` -> `qa.py --strict` -> `preview.py` (stages index.html +
images under the private-previews token path; refuses without a strict QA pass or with images over 400 KB). Stage timings
go to `data/timings.log`. Venue photos live in the gitignored `content/photos/<slug>/`. Rules, timings, what the reviewer
checks and what is never allowed: `INTAKE.md`. Tests: `python3 -m pytest -q tests/test_intake.py`.

## Stage 3A rules the gate enforces (2026-10-23)
- Focus: `qa.py` Tab-walks every control at 1440 and 390 and fails one whose focused-vs-blurred pixels change < 3:1 over a
  2 CSS px ring (`lib/focus.py`). Rings are two-tone (focus colour + halo) so they read on paper, deep bands and photos.
- Copy: any sentence of 40+ characters printed twice fails the build lint; secondary copy (`data-optional-copy`) is dropped
  when it repeats, and an optional section left empty goes with it.
- Images: one budget (400 KB, SSIM >= 0.97); cover boxes ask for the drawn width (`|cover`) or take a less tall ratio
  (`fit_ratio`) so nothing renders soft. Button fills hold 7:1 for both label colours.
- Titles carry no concept/proof/variant label (the footer chip says it). Editorial is not selectable; Cinzel is retired.
- Registry exposure: `demo` counts in the guard, `internal-proof` does not. Demos live in `.factory-check/demos/<slug>/`
  and stage with `preview.py` into `private-previews/<token>/demos/<slug>/` (local; deploy is a separate approved step).
- Notes and evidence: STAGE-3A-NOTES.md. Tools: `tools/focus_sweep.py` (focus across dialects), `tools/cinzel_probe.py`.
