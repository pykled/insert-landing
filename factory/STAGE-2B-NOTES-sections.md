# Stage 2B-2 notes: sections + nav-two-row (Maker: Claude Fable 5.1, 2026-10-21)

Owned paths: `templates/sections/**`, `templates/partials/nav-two-row.j2`, `templates/partials/nav-two-row.css.j2`.
Everything below that touches another owner's file is a request, not a change.

## What landed

| file | id | notes |
|---|---|---|
| `sections/story-split.j2` + css | story `split` | port of the mock's `#property` (7/5 grid, 3:4 photo, offset keyline frame now in `--metal` with `--line-strong` fallback). First paragraph in the display face (secondary when the display is caps-only; body face when the pairing is name-and-one-headline-only). The mock's facts row renders only when the page has neither `facts-strip` nor `statement`. The ornament partial is included with `slot='story'` inside `.story-text` (botanical-engraving goes there, z-index 0 behind the copy). `cite` is no longer tracked caps: credits run past 60 characters (E5). |
| `sections/spaces-strip.j2` + css | spaces `strip` | CSS grid, 6 → 3 → 2 → 1 columns, hairlines via borders; never `overflow-x` (E8). 4:5 photos, tracked-caps caption `01 · Up to 200`, use at 16.5 px, features as `.fine`. |
| `sections/spaces-stack-olive.j2` + css | spaces `stack-olive` | the stack on `--deep` with `--on-deep-accent` small-caps kickers. The section is the ranch motion device: `data-motion-device="band-fade"` when `t.motion_device == 'band-fade'`; background transitions paper → deep over `t.motion_device_ms` when `.visible` lands (section carries `.reveal`). Static under reduced motion (base's `transition-duration: .01ms`). |
| `sections/gallery-pairs.j2` + css | gallery `pairs` | 3:2 pairs, gap clamp(24, 3vw, 40), captions with `01..04`. Photos: not the lead, not the story photo; photos no space uses first; max four. Renders nothing with fewer than two. |
| `sections/statement.j2` + css | section `statement` | `copy.hero_lede` (else `v.story.lead`) at `max(display.min_px, clamp(28px, 2.6vw, 34px))`, 38ch measure, secondary face when the display is caps-only. A facts line under it (`data-fact` guests / acres / spaces / year from `tagline_facts` + `vibe.era`, nulls omitted). Kicker (locality · region) only for coastal and botanical. Ornament: `drop-cap` → the sentence carries `data-ornament="drop-cap"` and the css draws it (`initial-letter: 3`, float fallback); `watercolour-wash` → `.statement-wash` radial `--accent-tint` at 8% (the only allowed gradient); anything else → ornament partial included with `slot='section-head'` (sprig). |
| `sections/facts-strip.j2` + css | section `facts-strip` | year (`vibe.era`), acres, guests, spaces from `tagline_facts`; topped up to four from `v.numbers` (skipping repeated values; those carry no `data-fact`). Numerals in the display face (body face for name-only pairings), labels follow `t.kicker_style` (small-caps / italic / tracked caps; deco tracks +0.2em). Dark set: labels and rules in `--metal`. Includes the ornament partial with `slot='facts'` after the row (for `geometric-rule`; renders nothing unless the ornament uses that slot). |
| `sections/daylight-band.j2` + css | section `daylight-band` | first `light: day` photo that is not the lead or story photo (grounds/building/place first). Light ground = the dark set's `--ink`, text = `--paper`, scoped as `--dl-*` on `.daylight` (no global token change). Copy is `v.day` (hours, included, requirement) + the nav CTA link. |
| `partials/nav-two-row.j2` + css | nav `two-row` | row 1: wordmark, locality · region, CTA, burger; row 2: hairlined sub-nav, at most six section links (header total ≤ 8 links, no nested lists). **The css is included from inside the partial in a `<style>` block** because `base.html.j2` includes only `partials/nav-<style>.j2`; base may move it to `<head>` with `{% include 'partials/nav-' ~ nav_style ~ '.css.j2' ignore missing %}` and the inline block can then be deleted. |

Existing sections, gated on `dialect` so pre-dialect builds are byte-identical: `spaces-index` `.use`/`.blurb` 15.5 → 16.5 px,
`glance` `p` 15 → 16.5 px, `story-timeline` `.tl-paras p` 58ch → 54ch (E16 measured 73 characters at Karla 17 px).

## Needs a change outside my paths

1. **`build.py` can never pick `two-row`.** `nav_style` is `minimal | centered | bar` from the axes, then `if nav_style not in dialect['nav']: nav_style = dialect['nav'][0]`. For modern-luxe the formula gives `minimal` (era ≥ 85) which is in the list; for deco it gives `centered`, also in the list; so `two-row` is unreachable and `--force` does not accept `nav`. Suggest: `--force nav=two-row`, or rotate `dialect['nav']` by registered-site count like rhythm. Verified here with a test-only wrapper (`.factory-check/sections/nav_harness.py`) that sets `dialect['nav'] = ['two-row']`.
2. **`lib/templates.py --refresh` + tests.** `data/dialects.json` statuses still say `planned-2B` for the sections above; `tests/test_dialects.py::test_statuses_match_filesystem` fails until `--refresh` is run (data/ is stage 2A's). `tests/test_templates.py::test_real_filesystem_statuses` and `::test_dialect_build_falls_back_and_records` assert that `crest-centred` does **not** exist; the heroes maker's files now exist, so those two assertions are stale, not a regression. 52 of 55 pass.
3. **Base css** (not mine, seen while verifying): h2 renders below `pair.display.min_px` on mobile (ranch: Lora 28 px vs min 40); coastal `coastal-engraved` sets h2 in Josefin tracked caps (67-char caps run, E5) where the pairing says headings use the secondary face; `.band-deep h2`/`.btn-light` still hard-code `#fff`.
4. **Modern-luxe has no `guide` block** in either rhythm, so the header has no pricing link (`nav.pricing` in QA); if that matters, add a `Pricing` link target or a guide block to the rhythm.
5. **Ornament slots** my templates include: `story` (story-split), `section-head` (statement), `facts` (facts-strip). Ornament partials that do not use a slot must render nothing for it.

## Verification

```
.factory-check/sections/build.sh            # 8 dialect builds (two via the nav harness)
python3 qa.py ../.factory-check/sections/<dialect>
python3 .factory-check/sections/shoot.py    # contact sheet of every owned section at 1440 / 390
FACTORY_OUT=../.factory-check/sections/sv-after ./build-all.sh   # proof variants: diff vs .factory-check/sv-before = none
```
