# QA gate calibration: the display-legibility probe

Date: 2026-10-20. Script: `factory/qa.py` (`stroke_probe`). Purpose: give the "Bodoni lesson" (contrast alone is not
legibility; hairline display type disappears) a measurable gate instead of a rule of thumb.

## What the probe does

1. Reads the computed font of the page's `h1` (and `h2` in the 1x pass): family, weight, size, style,
   `font-variation-settings`, `font-optical-sizing`, letter-spacing.
2. Renders "Stonehurst garden estate Hamburgefonstiv 1907" with exactly those properties, black on white, as an
   absolutely positioned probe element, screenshots it, removes it.
3. Binarises at grey < 160 (so anti-aliased hairlines count as ink), then applies a morphological opening with a
   (2·DPR+1)-pixel square kernel. Opening deletes every stroke thinner than ~1 CSS px.
4. `hairline_share_1px` = share of the letterform's ink that the opening deleted. High = much of the glyph is made of
   strokes a 1x screen will render as a grey smear or nothing.

Runs at 2x (desktop and mobile contexts, h1) and at 1x (desktop, h1 and h2). The 1x pass is the one that matters:
hairlines fail on non-retina screens first.

## Calibration data

Probe text at three sizes, Chromium, black on white. Lower is sturdier.

**1x DPR (ink < 160, 3x3 opening)**

| Face / setting | 88 px | 60 px | 44 px |
|---|---|---|---|
| Bodoni Moda 400, auto opsz | 0.090 | 0.123 | 0.163 |
| Bodoni Moda 500, opsz 18 pinned (Stonehurst v2 fix) | 0.098 | 0.114 | 0.153 |
| Newsreader 500, auto opsz | 0.012 | 0.033 | 0.116 |
| Newsreader 500, opsz 24 pinned (variant A) | 0.004 | 0.024 | 0.090 |
| Fraunces 500, opsz 36 / SOFT 40 (variant B) | 0.002 | 0.006 | 0.033 |
| Cormorant Garamond 300 | 0.128 | 0.225 | 0.395 |
| Cormorant Garamond 500 (Lindley-Scott mock) | 0.079 | 0.144 | 0.239 |
| Instrument Sans 500 (variant C) | 0.000 | 0.002 | 0.003 |
| Jost 400 | 0.002 | 0.004 | 0.010 |

**2x DPR (ink < 128, 5x5 opening), 72 px / 40 px**

| Face / setting | 72 px | 40 px |
|---|---|---|
| Bodoni Moda 400 auto | 0.079 | 0.156 |
| Bodoni Moda 500 opsz 18 | 0.099 | 0.168 |
| Newsreader 500 opsz 24 | 0.018 | 0.179 |
| Fraunces 500 opsz 36 | 0.004 | 0.109 |
| Cormorant Garamond 300 | 0.198 | 0.745 |
| Cormorant Garamond 500 | 0.127 | 0.298 |
| Instrument Sans 500 | 0.001 | 0.006 |
| Jost 400 | 0.003 | 0.013 |

## Thresholds chosen

- 1x pass: FAIL above 0.20, WARN above 0.12. Fails Cormorant 300 at 60 px and below and Cormorant 500 at 44 px;
  warns on Bodoni Moda (either cut) at 60 px and below and Cormorant 300 at 88 px. Passes every sturdy face.
- 2x pass: FAIL above 0.25, WARN above 0.18 (only Cormorant trips these).

## What the probe can and cannot tell you (honest limits)

- It separates **light cuts from sturdy cuts** (Cormorant 300 vs 500: 0.225 vs 0.144 at 60 px) and **Garamond /
  Didone shapes from text serifs and sans** (Bodoni 0.12 vs Newsreader 0.03 vs Instrument 0.002 at 60 px). That is
  enough to stop the two failure modes we have actually shipped: a thin Garamond and a Didone used too small.
- It does **not** separate Bodoni Moda at automatic optical size from the pinned opsz-18/500 cut (0.123 vs 0.114 at
  60 px). Black-on-white at these sizes, both cuts have hairlines around one device pixel; the visible difference in
  Stonehurst v1 came from the combination of weight 400, white text on a scrimmed photo and 1x screens. The opsz pin
  is therefore enforced by the **rule check** instead (computed `font-variation-settings` must contain `opsz` and
  `font-optical-sizing` must be `none` for any pairing whose display family has an opsz axis), and by the pairing
  library's `min_px`/`weight` fields. The probe is the second line, not the first.
- A probe at 1x with grey < 160 counts anti-aliased strokes as ink; a stricter threshold (grey < 96) made every
  serif look worse and did not improve discrimination (tested: Bodoni auto vs pinned "faint share" 0.165 vs 0.137
  at 88 px).
- Numbers are Chromium-specific. Safari and Windows ClearType render hairlines differently; treat the thresholds as
  Chromium regression gates, not cross-platform truth.

## Related gates in qa.py that cover the rest of legibility

- Contrast under every glyph, measured per pixel against a screenshot with all text made transparent (default,
  hover, open menu, form errors, three confirmations, each moment state). Floor 4.5:1 / 3:1 (WCAG AA); warning under
  7:1 for small text. The three variants' lowest small-text ratios: A 6.87 (one button in the error state), B 6.65
  (two buttons in error states), C 7.63.
- Display rule check (pairing `min_px`, pinned weight, pinned opsz) for every `h1/h2/h3/.display` element that uses
  the display family.
- Cover-aware image sharpness (served width >= rendered width x DPR, 1.5x cap on desktop; never above the source
  crop width) so no photo is ever upscaled, including inside `object-fit: cover` frames.
