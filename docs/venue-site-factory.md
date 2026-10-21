# Venue site factory: system design and proof

Written 2026-10-20. Code lives in `factory/` (Python 3.9, Jinja2, Pillow, numpy; Playwright for QA only). Research
behind the choices: `docs/venue-design-research.md`. Proof: three Stonehurst variants under
`previews/stonehurst-variants/{a,b,c}` and, for remote viewing, `/private-previews/2d32be7dda6d361dd89ffdfd/variants/{a,b,c}/`.

## 0. The problem in one paragraph

Every venue site we build from a shared template will converge on the same page, because the things a visitor reads
as "the look" (header, hero class, display face, accent, section rhythm, one signature device) are exactly the things a
template fixes. The research says rotating those five levers is what separates memorable venue sites from the
Showit/Squarespace default, and that photo swaps alone do not. So the factory fixes the *components* (forms, scheduler,
FAQ, footer, JSON-LD, legibility rules) and varies the *levers* from a six-axis personality, with a guard that refuses
a new site whose levers land too close to a site we already built.

## 1. Personality model

Six axes, each 0-100, scored by a human in about five minutes from the venue's own site and photos:

| Axis | 0 | 100 | What it decides |
|---|---|---|---|
| `formality` | rustic | refined | corner radius, caps tracking vs sentence case, hairline rules, keyline vs rounded photo edges, button style |
| `scale` | intimate | grand | container width, display size multiplier, hero class |
| `era` | heritage | modern | serif vs grotesk family, radius to 0 at ≥85, nav style (minimal at ≥85), motion |
| `density` | lush, layered | minimal, airy | section padding, paper chroma (tinted vs near-white), section rhythm, guide/FAQ archetypes, reveal motion |
| `temperature` | warm | cool | palette bias when scoring photo clusters, paper hue, shadow colour |
| `voice` | romantic | editorial / plainspoken | copy preset, kicker style (italic vs caps vs label), section order |

Continuous tokens are direct functions of the axes (`lib/personality.py: tokens_from_axes`):

| Token | Rule |
|---|---|
| radius | `10 x (1 - formality/100) x (1 - 0.5 x era/100)`, forced 0 when era ≥ 85 |
| button style | pill-solid if formality < 45 and temperature < 45; square-solid if era ≥ 80; square-outline-caps if formality ≥ 60; else soft-solid |
| kicker style | caps-rule if formality ≥ 55 and era < 85; italic if voice < 40; else label |
| section padding | `72 + 0.6 x density` to `130 + 0.9 x density` px |
| container | `1120 + 1.8 x scale` px |
| image edge | rounded if radius ≥ 6; keyline if formality ≥ 70 and era < 70; else flush |
| reveal | none if density ≥ 85; slide if density < 40; else fade |
| display scale | `1 + 0.25 x scale/100 (+0.08 if voice ≥ 70)` |
| nav | minimal if era ≥ 85; centred if formality ≥ 75 and voice ≥ 60; else bar |
| section rhythm | modern (spaces and moment first, history late, no glance strip) if density ≥ 80; editorial (credentials, history, then spaces) if voice ≥ 65; else warm (straight to the grounds) |

Discrete choices (pairing, hero, spaces, story, FAQ, tour, moment, voice) are selected by fit: every library item has
an `axes` position on the same scale, fit = RMS distance over the axes it declares. The selector takes the top three
per dimension and scores every combination of pairing x hero x spaces x moment x story by fit plus a penalty when the
resulting fingerprint is within the warn (0.35 penalty) or refuse (1.5 penalty) distance of any registered site. The
guard is inside the loop, so the second-best hero is chosen automatically when the best one would make a near-copy.
Explicit `--force dim=id` always wins and is recorded as forced.

**Proof mapping.** The three variants were given only a personality vector, a lead photo and the palette photos:

| Variant | Personality (f, s, e, d, t, v) | Selected (no forcing) |
|---|---|---|
| A | 85, 70, 55, 70, 65, 80 | Newsreader + Figtree; masthead hero; editorial index of spaces; pull-quote story; guest-journey moment; numbered FAQ; centred scheduler; editorial voice; centred nav; deep-band guide |
| B | 30, 45, 35, 25, 15, 25 | Fraunces + Karla; framed-photo hero; alternating stack of spaces; timeline story; light-shift moment; accordion FAQ; split scheduler; warm-host voice; bar nav; photo guide; pill buttons |
| C | 70, 55, 95, 92, 55, 92 | Instrument Sans only; typographic cover hero; spec-sheet spaces; ledger story; seat-picker moment; plain-list FAQ; band CTA tour; plainspoken voice; minimal nav; plain guide; zero radius |

## 2. Variation dimensions

### 2.1 Palette from the venue's photographs (`lib/palette.py`)

1. Each chosen photo (lead weighted 2x, plus three others) is downscaled to 160 px and every pixel converted to OKLab.
2. k-means (k = 8, fixed seed) per photo; clusters merged.
3. Accent candidates: chroma ≥ 0.035, lightness 0.22-0.80; score = `sqrt(pixel share) x chroma^1.5 x temperature affinity` (accents are small chromatic areas, so chroma outranks area). A second "deep" hue needs ≥ 55° of hue separation, otherwise the deep band stays tonal (a dark cut of the accent) rather than inventing a colour.
4. Tokens in OKLCH, gamut-clamped: paper (L 0.955-0.985, chroma 0.002-0.014 by density), paper-2/-3, ink (L 0.21, hue from the deep cluster for refined personalities), ink-soft, ink-faint, accent-tint, accent-text, accent (non-text uses), accent-fill (button fills), deep, on-deep-soft, on-deep-accent, on-ink-soft, line.
5. Every pair the templates use is walked in lightness until it passes: small text 7:1 (ink on paper, ink-soft on paper-2, ink-faint on paper-3, accent-text on accent-tint, paper on deep, white on accent-fill at 7.3:1), white on accent 4.5:1. The QA walker then re-measures against the rendered page, so the 7:1 target gives headroom for anti-aliasing and photo backgrounds. This is the Bodoni lesson applied to colour: pass the arithmetic first, then measure the pixels.
6. Human overrides: `--accent-hue` forces the hue (recorded as "human override" in the report), `--palette-photos` chooses which photos count.

Results on the Stonehurst photos: A took a dusky slate blue (hue 247°) from the greenhouse night sky with a forest-green deep band; B took the terrace stone's ochre (97°) with a tonal dark olive; C took the hero photo's green (128°) on near-white paper. Each report lists the candidate clusters with their source photo, so the choice is auditable.

### 2.2 Type pairing library (`data/pairings.json`)

Ten pairings, every family and axis range fetched from fonts.googleapis.com on 2026-10-20. Each declares the display family, class (didone, garalde, transitional, soft-serif, grotesk, geometric-sans, humanist-sans, inscriptional, scotch), pinned weight, italic weight, minimum display size, the `font-variation-settings` string, fallbacks, body family and sizes, a mood tag, axis position and a legibility risk note.

| id | mood | display / body | pin | risk note |
|---|---|---|---|---|
| editorial-didone | editorial-refined | Bodoni Moda 500 / Jost | opsz 18, min 30 px | hairlines; never auto opsz or weight 400 above 40 px (Stonehurst v2) |
| heritage-garalde | heritage-classic | Cormorant Garamond 500 / Inter | min 28 px | light face; 500+ only (Lindley-Scott mock) |
| warm-fraunces | warm-organic | Fraunces 500 / Karla | opsz 36, SOFT 40, WONK 1, min 26 px | opsz 144 is hairline-fine; pinned it stays soft (variant B) |
| modern-instrument | modern-minimal | Instrument Sans 500 / same | wdth 100, min 20 px | single family reads as SaaS without white space (variant C) |
| quiet-instrument-serif | quiet-luxury | Instrument Serif 400 / Instrument Sans | min 32 px | single weight; never over busy photos |
| coastal-newsreader | coastal-airy | Newsreader 500 / Figtree | opsz 24, min 26 px | 72 master is fine; pinned at 24 keeps text sturdiness (variant A) |
| garden-garamond | garden-romantic | EB Garamond 500 / Nunito Sans | min 30 px | small x-height; run ~8% larger |
| desert-dm | desert-modern | DM Serif Display / DM Sans | DM Sans opsz 14, min 28 px | display-only serif; body never uses it |
| inscriptional-marcellus | mediterranean-heritage | Marcellus / Work Sans | min 24 px | single weight, no italic |
| loft-archivo | industrial-loft | Archivo 600 wdth 112 / Archivo | min 22 px | expanded caps get wide; cap line length |

Rules baked into the CSS: `font-optical-sizing: none` plus the pinned `font-variation-settings` on every element that uses the display face; h3 falls back to the body face when the pairing's minimum size is above 24 px; Playfair Display is deliberately absent (no opsz axis, and it is the generic wedding face).

### 2.3 Hero archetypes (`data/archetypes.json`)

| id | status | what it is |
|---|---|---|
| masthead | built (A) | magazine masthead: dateline strip, giant wordmark, dek + four facts, full-bleed photo beneath, inline date-check bar |
| frame | built (B) | photo matted in a paper margin under a centred headline, italic caption, lede + facts beside the date card |
| cover-type | built (C) | headline fills the viewport width, lede + six-row ledger + inline date check, one 4:5 photo |
| cinematic | mock-only | full-bleed photo, deep scrim, copy bottom-left, date card right (Stonehurst mock v2; not yet a template) |
| editorial-split | mock-only | text-first column, inquiry card, media grid (Lindley-Scott mock) |
| panel | spec | 50/50 photo and solid palette panel holding copy and date check |
| mosaic | spec | asymmetric three-photo grid with the headline in a cell |
| slideshow | spec | three cross-fading photos with caption counter, static under reduced motion |

Each hero declares `needs` (minimum lead-photo width, photo count) that the selector checks against the manifest, so a 1600 px terrace photo can never be chosen for a full-bleed hero.

### 2.4 Section archetypes

| Dimension | built | mock-only / spec |
|---|---|---|
| spaces | index (numbered rows + sticky swapping photo), stack (alternating bands), spec-sheet (ruled table) | bento, three-col (mock-only); strip (spec) |
| story | pullquote (drop cap, two columns, two photos), timeline (dated rail + sticky portrait), ledger (four big figures) | split (mock-only) |
| faq | numbered (two columns, all open), accordion-split, plain-list | |
| tour | scheduler-centered, scheduler-split, band-cta (scheduler opens inside a dark band) | |
| guide | photo / band / plain layouts (one template, chosen by density) | |
| glance, uses, featured | shared | |
| gallery | none | filmstrip, pairs (spec) |

### 2.5 Photography treatment rules

- Lead photo must meet the hero's `needs.lead_min_width`; the QA gate verifies every rendered image served width ≥ rendered width x DPR (1.5x cap on desktop), computed cover-aware (`scale = max(box_w/w0, box_h/h0)`) so portrait frames cut from landscape sources are checked at their true scale, and never above the source crop width.
- Frame ratios are owned by the archetype: masthead 16:9 (4:3 on mobile), frame 3:2, cover 4:5, index stage 4:5, journey stage 4:5, stack 4:3, spec thumbnails 1:1, story portraits 3:4.
- Edge treatment from the formality axis: keyline (1 px line), flush, or rounded with a warm or soft shadow; shadows are kept short (34 px blur, -22 px spread) because the QA walker found a card shadow darkening the caption under it.
- `focal` per photo in the content file drives `object-position`; alt text is mandatory and captions are derived from the first clause of the alt.
- Ordering: the lead photo is a fingerprint dimension; the light-shift moment picks photos by their `light` tag (day / golden / night); the journey uses each space's own photo.
- Nothing is generated and nothing is upscaled; widths are only written when ≤ the source width.

### 2.6 Signature moments

| id | status | device | facts it is built from |
|---|---|---|---|
| guest-journey | built (A) | scroll story: five steps of a guest's day with a sticky photo that swaps per step; inline photos on mobile | each space's stated use (barn greets you on entry, ceremony in the flower garden, cocktails in the bamboo, reception under glass) |
| light-shift | built (B) | Noon / Golden hour / Night control that crossfades a photo set and washes the section paper → tint → deep | gates 12 PM, event ends 10 PM, breakdown to midnight, greenhouse HVAC, bamboo 120 cocktail |
| seat-picker | built (C) | guest-count slider; spaces that hold the number stay on, others recede by colour and greyscale; live sentence | published capacities, 60-ceremony / 120-cocktail distinction, 3-4 of 6 spaces rule, 200 max |
| hours-dial | spec | the 12-hour rental day as an arc | FAQ schedule |
| grounds-constellation | spec | abstract linked-node diagram of the spaces (not a map) | space list |
| season-toggle | spec | needs seasonal photo sets | |
| window-reveal | spec | hero revealed through a pane-shaped mask | |
| numbers-count | spec | count-up ledger | numbers |

Every moment has a QA hook (`window.__setLight`, `window.__fitSet`, `window.__journeyActivate`) so the gate drives it into each state and measures contrast there. Inactive states recede by colour, never by opacity: the first draft dimmed rows to 38% opacity and failed the walker at 2.0:1.

### 2.7 Copy voice presets (`data/voices.json`)

romantic, warm-host, editorial, plainspoken. A preset holds kicker, headline, lede, CTA labels, section titles and
footer blurb with `{slots}` filled from the content file (acres, space count, max guests, rental hours, the spaces-per-
event rule). Presets contain tone, never facts: the first draft of warm-host said "six gardens" and was caught on
visual review (the venue has six spaces, two of them gardens). Any slot can be overridden per build with `--copy` or
`content.copy_overrides`; that is where the human writes the three lines that matter.

## 3. Diversity guard (`lib/fingerprint.py`, `data/registry.json`)

Fingerprint = display family, display class, body family, accent hue, paper temperature, hero id and family, spaces /
story / faq / tour archetypes, section order, moment, button style, radius bucket, lead photo.

Distance in [0, 1] = weighted sum: categorical dimensions 0/1 (display family 0.16, hero 0.14, accent hue 0.12 as angular
distance / 180, moment 0.08, spaces 0.08, section order 0.07 as 1 - LCS/len, hero family 0.06, display class 0.06, body
family 0.06, story 0.04, paper temperature 0.04, tour 0.03, faq 0.02, button style 0.02, radius bucket 0.02).
Thresholds: < 0.35 refuse, < 0.50 warn. The registry holds the two hand-built mocks (transcribed) and the three variants.

Matrix on 2026-10-20 (`python3 lib/fingerprint.py data/registry.json --matrix`):

| | stonehurst-mock-v2 | lindley-scott-mock | A | B | C |
|---|---|---|---|---|---|
| stonehurst-mock-v2 | 0 | 0.859 | 0.884 | 0.781 | 0.885 |
| lindley-scott-mock | 0.859 | 0 | 0.879 | 0.832 | 0.807 |
| A | 0.884 | 0.879 | 0 | 0.924 | 0.797 |
| B | 0.781 | 0.832 | 0.924 | 0 | 0.858 |
| C | 0.885 | 0.807 | 0.797 | 0.858 | 0 |

The closest pair is B to the existing Stonehurst mock at 0.781 (both warm paper, both accordion FAQ, both split
scheduler). The two hand-built mocks, which Dillon felt resembled each other, score 0.859 apart: on this metric they
differ in almost every lever and share only paper temperature and square buttons. That is evidence the metric under-
weights what the eye catches on those two (same warm cream paper, same serif-on-cream mood, same hero-then-story
rhythm), so the thresholds are set low and a pHash of screenshots is the planned second signal once there are more
sites to calibrate on. The guard is useful today for the failure it is built to catch, the same pairing + hero +
moment reused, and it reports the drivers of every distance so a human can disagree with it.

**Superseded 2026-10-20 by registry schema 2** (section 9.4): new dimensions, the same-dialect rule, a quota and the
screenshot pHash. The table above is the schema-1 record.

## 4. Content schema

`factory/lib/schema.md`. One JSON per venue; every fact, space, FAQ and photo carries its source URL; nulls are allowed
and rendered honestly ("Capacity on request", no phone line). Personality, forced choices, lead photo and copy
overrides are build inputs, not content, so one file yields many sites. `factory/content/stonehurst.json` is the
reference instance, built from the facts verified in `previews/stonehurst/NOTES.md`.

## 5. Generator and optimiser (`build.py`, `lib/images.py`)

`build.py content.json --variant x --out dir --personality ... [--force dim=id] [--lead photo] [--palette-photos a,b,c] [--accent-hue 247] [--copy key=value] [--register] [--allow-close]`

Steps and measured times (warm cache, M-series Mac): palette 0.2-0.3 s, selection < 0.05 s, image sets 0.1 s cached /
17.7-18.1 s cold (nine photos, three to four WebP widths each, Pillow method 6, quality stepping down to stay under
320 KB per file and 560 KB for the 2400 px hero), render 0.04 s, total 0.4 s warm. Output: a self-contained
`index.html` (65-71 KB, inline CSS, inline JS, JSON-LD with `["EventVenue","LocalBusiness"]` and `FAQPage`), `img/`,
`img/manifest.json` for QA, and `build-meta.json` (choices, selection ranking, palette report with every candidate
cluster and contrast pair, fingerprint, guard result, timings).

Shared components: date check (three fields, validation, hold confirmation, reset), tour scheduler (calendar, slots,
booking confirmation, reset; opens from a CTA in the band variant), pricing-guide capture, FAQ, footer, skip link,
focus-visible, reduced-motion, noindex meta and disclaimer chip when `preview.private` is true. No network calls.

## 6. QA gate (`qa.py`)

Per viewport (1440 x 900 at 2x, 390 x 844 at 2x), plus a 1x pass for the legibility probe:

1. no horizontal overflow, no console/page errors, no failed requests, no off-origin requests except Google Fonts
2. web fonts loaded at the weights actually used
3. images: alt present (empty alt only inside `aria-hidden`), loaded, cover-aware sharpness, never above source width
4. contrast under every text node and placeholder, measured per pixel against a screenshot with text made transparent, in the default, hover (CDP-forced), open-menu, form-error, three confirmation and every moment state; AA floor, 7:1 warning
5. display legibility: rule check (pairing min size, pinned weight, pinned opsz) and the hairline probe (calibration and limits in `docs/qa-calibration.md`)
6. basics: title, description, lang, viewport, one h1, heading order, landmarks, hero `fetchpriority`, lazy below the fold, HTML < 120 KB, JSON-LD parses with EventVenue, focus-visible and reduced-motion rules, tap targets ≥ 24 px on mobile, LCP element and bytes transferred at load reported
7. flows: date check, tour, guide, and the site's moment driven through its states
8. diversity: distance to every registered site; refuse fails the gate

Results for the proof: A 682 text nodes, lowest small-text ratio 6.87 (one button label in the error state), 0 problems;
B 704 nodes, lowest 6.65, 0 problems; C 572 nodes, lowest 7.63, 0 problems. 24-31 s per variant. Screenshots and
`qa-report.json` land in each variant's `qa/` folder.

What the gate found during the build, which is the argument for having it: inactive journey steps and non-fitting
seat-picker rows dimmed by opacity (2.0:1), a tapped calendar day where sticky `:hover` beat the selected style on
touch screens (1.08:1), card shadows darkening captions (6.7:1), four-column facts and the inline date row overflowing
390 px, footer links and the brand link under the 24 px target size, footer `h4` after `h2`, and a voice preset that
mis-stated a fact. It also found two defects in itself: the sticky header painted into every screenshot tile, and a
stroke metric that could not see the thing it was built for until recalibrated.

## 7. Turnaround workflow and time budget per venue

| Step | Who | Time | Notes |
|---|---|---|---|
| Intake and crawl: sitemap, every page, untransformed photo originals, fact ledger with source URL per fact | agent, then human verifies | 45-90 min agent, 15 min human | the Stonehurst crawl took the previous session about half a day; the content file from an existing fact ledger took 20 min |
| Photo curation: pick 8-10 from a contact sheet, write alt text, set focal points, tag light/season | human (agent drafts alt) | 20-30 min | taste; no photo of the venue is ever generated |
| Personality scoring | human | 5 min | six numbers; defaults are fine for a first pass |
| Generate (selection, palette, images, render) | machine | 0.4 s warm, ~20 s cold | the three Stonehurst variants rebuilt in 1.2 s total |
| QA gate | machine | 25-30 s | fails are specific and usually CSS-local |
| Taste pass: look at desktop and mobile shots, override accent hue or a forced archetype, write 3-5 lines of copy, rebuild | human | 20-40 min, 1-3 rebuilds | this is where the site stops being "a build" |
| Deploy to the private-preview token path and poll | machine + human check | 5 min | |
| **Total** | | **about 2.5-4 hours, of which 60-90 minutes are human judgement** | versus roughly 1.5 working days for the hand-built Stonehurst v1 + v2 |

Measured on 2026-10-20 for the proof: once the factory existed, each variant was one command; A, B and C generated in
0.4 s each warm (first cold run 17.9 s and 18.4 s for B and C because of WebP encoding), QA 29 s, 31 s and 24 s. The
honest total for the three variants including visual review and the fixes the gate demanded was about two hours, most
of it template work that is now reusable.

## 8. What is still manual, and what is still missing

- **Facts and photos.** The content file is the product; writing it from a crawl is agent-assisted but needs a human to verify every number and to choose the photographs. Nothing on the page may come from anywhere but the venue's site, and only a person can sign that off.
- **Copy.** Voice presets produce acceptable, slot-filled headlines. The best line on each variant should still be written by a person.
- **Palette review.** Photo-derived palettes are only as good as the photos (dusk greenhouse gave a blue; stone gave ochre). The override exists because a human will sometimes prefer the venue's existing brand colour.
- **Library breadth.** Built today: 3 heroes, 3 spaces, 3 story, 3 faq, 3 tour, 3 moments, 4 voices, 10 pairings. Specified but not built: 5 heroes (two of them exist only as the hand-written mocks), gallery sections, 5 moments. Each new archetype costs about 30-60 minutes and immediately multiplies the space.
- **Guard calibration.** Five sites is not enough to trust the thresholds; the screenshot pHash now exists (section 9.4) and every threshold is re-tuned after ten sites.
- **Page weight on desktop.** A and B transfer about 2.5 MB at load in the QA run because Chromium's lazy-load threshold pulls the swapping photo stacks early; C transfers 632 KB. Fix candidates: smaller width ladders for stage images, or load them on first interaction.
- **Three sub-7:1 labels.** White button labels on the accent fill measure 6.65-6.87 at the anti-aliased edge in error states (AA passes at 4.5). Raising the fill target further darkens warm accents toward brown; a human call per site.
- **Containment.** Variants are noindex, under the tokenised private path with `X-Robots-Tag` and `Cache-Control: no-store`; `previews/`, `factory/` and `docs/` are in `.railwayignore` so content files and research never reach the server. Not pushed to GitHub.

## 9. Dialect layer (stage 2A, 2026-10-20)

Implements `docs/research/05-luxury-dialects-spec.md` sections 1-7 except the templates (stage 2B, contract in
`factory/STAGE-2B-CONTRACT.md`). A dialect is chosen before fit-ranked selection; the selector then runs unchanged over
the dialect's ids.

### 9.1 Data

- `data/dialects.json`: the eight dialects (estate, editorial, candlelit, modern-luxe, coastal, botanical, ranch, deco)
  with axis clamps, paper / ink / deep / accent ranges (OKLCH), metallic, 7:1 pairs, type knobs (headline case, body
  px, kicker styles), allowed pairings / heroes / spaces / story / faq / tour / gallery / moments / ornaments / voices,
  nav styles, photo rules, two rhythm variants, motion device and token overrides; plus the shared baseline, the
  controlled vibe words, type priors and the fallback chains. Every listed id has `status`: exists, planned-2B or
  deferred (`python3 lib/templates.py --missing` lists the 57 not yet available; `--refresh` rewrites the labels).
- `data/pairings.json`: 16 new pairings (the spec inventory says 14; its dialect blocks name 16), all `dialect_only`,
  with pinned weight / opsz / tracking, optional `secondary` face, `display.case`; the spec's working names are kept as
  `aliases` (editorial-playfair-free -> editorial-gloock, ranch-canela-free -> ranch-lora, deco-poiret-free ->
  deco-big-shoulders). `lib/fonts.py` enforces the rules (display weight 400-600, pinned opsz, didone hairline caution,
  banned families) and verifies the chosen import on fonts.googleapis.com at build time (cache in
  `data/fonts-verified.json`; offline uses the cache; HTTP 4xx stops the build). All 26 verified 2026-10-20.
- `data/voices.json`: heritage, evening, lyric, each with three CTA sets (rotated per registered site using the voice).
  Values may be candidate lists; the first one whose `{slots}` all have content values is used, an unfillable one stops
  the build, and strict voices contain no number outside a slot. The four older voices still state "Six spaces" /
  "One event a day" literally (warned, not changed: the proof variants render from them).
- `data/archetypes.json`: the new heroes / sections / moments as `planned-2B` with `needs`, `hero_framing` on every hero.
- Content schema: per-photo `subject`, `mono`, `flora`, `archival` (+ `rights`), a `vibe` block; validated by
  `lib/schema.py`. `content/stonehurst.json` gained subject tags, two `flora: fig` tags and a vibe block (garden; lush,
  garden, romantic) set by the Maker from the file, to be confirmed by a human.

### 9.2 Selection (`lib/palette.py`, `lib/personality.py`, `build.py`)

1. Photo signals over the palette photos (lead 2x): mean L, mono / foliage / water / dark / earth shares, warm shadows.
2. Score table: the spec section 3 signal rules + vibe words (+2 each) + type prior + era rules. Top score wins; ties go
   to the dialect with fewer registered sites, then file order. `--dialect <id>` is a recorded human override;
   `--dialect none` is the pre-dialect path. The full table with every reason is written to `build-meta.json`
   `dialect.scores`.
3. Axes clamp to the dialect's region (missing `--personality` = the dialect centre); the density >= 85 + voice >= 85
   corner is pulled back everywhere except modern-luxe.
4. Within-dialect knobs: paper tone (light / mid / tinted, or dark-warm / dark-cool from the shadows; estate and deco
   switch to their charcoal variant on dark photos), ornament (least used in the dialect), rhythm variant (alternates),
   pairing (never the same as the dialect's last registered site), body px 17/19/21, headline case, photo edge, kicker.
5. Palette: dialect paper ranges; accent prefers candidates inside the dialect's hue ranges (reported when none is);
   the charcoal set (`derive_dark`) walks every small-text pair to 7:1 with the same lightness walker and adds
   `--on-accent`, `--metal`, `--field`. Pure white paper is never output.
6. Templates resolve by id; a missing one falls back along `fallbacks` (dialect-allowed ids first) and is recorded in
   `build-meta.json` `fallbacks[]` and flagged by QA. Fingerprints and the guard use what is actually rendered.

Stonehurst with the vibe block scores botanical 6, editorial 2, modern-luxe 1, coastal 1 and builds as botanical
(botanical-cardo, frame hero for the planned arch-split, stack, timeline, light-shift for the planned sprig-draw).
Forced estate / candlelit / deco / coastal builds also complete, with their fallbacks listed.

The three proof variants build with `--dialect none` (build-all.sh) and are byte-identical to the published files except
the generator hash (`FACTORY_OUT=../.factory-check/stonehurst-variants ./build-all.sh`, then diff).

### 9.3 QA additions (`qa.py`, `lib/exclusions.py`)

- Exclusions E1-E19 from spec section 5 run on one DOM snapshot per viewport (`COLLECT_JS`); each message starts with
  its E-number. Dialect builds fail on them; pre-dialect builds and mocks get them as warnings (A, B, C: four or five
  sub-16.5 px card/dateline paragraphs, B one 73-character line, C the density/voice corner E17). Fixtures: `tests/test_exclusions.py`,
  also `python3 qa.py --self-test`.
- Reduced motion: every first-screen `.reveal` visible and zero running animations; motion on: reveal 600-1200 ms,
  `[data-motion-device]` animations 600-1600 ms.
- Moment hooks for the new moments (`__slideTo`, `__countFinish`, `__thenNow`, `__pairsTo`, `__dialSet`, draw-in marker).
- Template fallbacks: warning, or a problem with `--strict`.
- pHash: 16 x 16 DCT hash of the 1440 fold and of the full page as a 64 x 256 rhythm strip, stored in `qa-report.json`
  and compared with every registered site (<= 18 of 256 bits warn, <= 12 fail).
- The existing contrast walker and legibility probe are unchanged.

Current state: A, B, C pass (0 problems). Dialect builds of Stonehurst do not pass yet, for template reasons listed in
the contract section 3: botanical 6 problems, estate 7, candlelit 40 (hard-coded white on charcoal, display minimums
and the hairline probe on mobile for Cardo and Libre Caslon Display, body copy under 16.5 px).

### 9.4 Diversity guard, registry schema 2

New fingerprint dimensions paper_tone, hero_framing, display_case, ornament, body_px, photo_edge, motion_device,
nav_style (weights 0.06 / 0.06 / 0.04 / 0.06 / 0.03 / 0.03 / 0.03 / 0.03; schema-1 weights x 0.66); dialect, pairing
and voice stored unweighted. Same dialect: refuse < 0.32, warn < 0.45, and refuse unless 4 of 7 key dimensions differ
(pairing, hero framing, ornament, paper tone, spaces, moment, body size). Quota: the 2nd site sharing dialect + pairing +
hero framing warns, the 3rd refuses. `--allow-close "<reason>"` stores the reason with the registration. All five sites
were re-registered (mocks: new dimensions transcribed from the rendered pages; variants: from the byte-identical
rebuild) with pHashes.

```
                          stonehurst-mo lindley-scott stonehurst-a  stonehurst-b  stonehurst-c  
stonehurst-mock-v2        0.000         0.717         0.804         0.665         0.734         
lindley-scott-mock        0.717         0.000         0.830         0.669         0.712         
stonehurst-a              0.804         0.830         0.000         0.830         0.626         
stonehurst-b              0.665         0.669         0.830         0.000         0.747         
stonehurst-c              0.734         0.712         0.626         0.747         0.000         
(* same dialect: refuse < 0.32, warn < 0.45, and >= 4 of 7 key dims must differ; otherwise refuse < 0.35, warn < 0.50)
```

Distances fell from 0.78-0.92 to 0.63-0.83 because the new dimensions mostly agree across the five (no ornament, no
motion device, 17 px body): the new levers have not been used yet. The two mocks are 0.717 apart (was 0.859), which is
closer to how alike they look.
