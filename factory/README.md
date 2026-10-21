# Insert venue site factory

Static, mobile-first venue homepages from one content file + a personality vector. Python 3.9, Jinja2, Pillow, numpy,
Playwright (QA only). No build framework.

```
factory/
  build.py            content.json + personality -> index.html, img/*.webp, build-meta.json
  qa.py               Playwright gate: contrast under every glyph, legibility probe, overflow, images, flows, diversity
  build-all.sh        the three Stonehurst proof variants
  lib/color.py        OKLab/OKLCH <-> sRGB, WCAG contrast, gamut clamp
  lib/palette.py      k-means on the venue's photos -> accessible token set (every pair verified >= 7:1 for small text)
  lib/personality.py  6 axes -> tokens; fit-ranked selection with the diversity guard inside the loop
  lib/fingerprint.py  per-site fingerprint, weighted distance, registry, refuse/warn thresholds
  lib/images.py       responsive WebP ladders, never upscaled, size-budgeted
  lib/schema.md       content schema
  data/pairings.json  10 vetted Google-font pairings with pinned weights/opsz and legibility notes
  data/archetypes.json  heroes, sections, moments, voices with axis positions and honest build status
  data/voices.json    copy presets (facts come from content slots, never from the preset)
  data/registry.json  fingerprints of every site built so far (two hand-built mocks + generated sites)
  templates/          base, css, partials, heroes/, sections/, moments/
  content/            one JSON per venue
```

Build one site:
```
python3 build.py content/stonehurst.json --variant d --out ../previews/stonehurst-variants/d \
  --personality formality=60,scale=50,era=40,density=50,temperature=30,voice=50 --lead flower --register
```
QA it (needs `python3 -m http.server 4821` in ~/projects/insert):
```
python3 qa.py ../previews/stonehurst-variants/d
```
Distances between everything registered: `python3 lib/fingerprint.py data/registry.json --matrix`.

Design docs: `../docs/venue-site-factory.md` (system), `../docs/venue-design-research.md` (research synthesis),
`../docs/research/*.md` (cited source notes), `../docs/qa-calibration.md` (legibility probe calibration).
