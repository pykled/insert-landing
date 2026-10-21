# 03 — Generation approaches: many distinct small sites from one system

Research date: 2026-10-20. Scope: how a one-person studio plus AI agents can emit many genuinely different-looking static marketing sites from a single generator, hosted on the existing Express/Railway app or any static host. Every factual claim below carries a bracketed source number; the numbered list at the end records the URL and the HTTP status actually observed. Claims marked **(opinion)** are my synthesis, not sourced. Claims marked **(weak)** rest on a secondary or partially-fetched source.

---

## 1. Design tokens, theme packs, and schema-driven generation

### 1.1 Token formats and tooling

- **W3C DTCG format.** The Design Tokens Format Module (draft "2025.10", a Draft Community Group Report that warns implementers not to build on the preview) defines a JSON file (`.tokens` / `.tokens.json`) where every token has `$value`, usually `$type`, optionally `$description`/`$deprecated`/`$extensions`. Atomic types: color, dimension, fontFamily, fontWeight, duration, cubicBezier, number; composites: shadow, border, transition, gradient, typography, strokeStyle. Groups are nested objects without `$value`; `$extends` deep-merges groups; aliases are `{group.token}` or JSON-Pointer `#/path`; cycles are prohibited. [1]
- **Style Dictionary v4** exports token JSON to CSS variables, iOS, Android, JS and is "forward-compatible with Design Tokens Community Group spec". [2] Optional for us: a 40-line walker that prints `--name: value` does the one job needed. **(opinion)**
- **Open Props**: 500+ custom properties (colors with light/dark, gradients, shadows, type, easings, sizes, radii, aspect ratios, z-index, masks, durations), ~4.0 kB Brotli, MIT, also shipped as JSON design tokens. [3]
- **Radix Colors** is the cleanest *semantic* scale: 12 steps — 1-2 backgrounds, 3-5 interactive backgrounds, 6-8 borders, 9-10 solid fills (9 highest chroma), 11-12 text — with steps 11/12 "guaranteed to Lc 60 and Lc 90 APCA contrast ratio on top of a step 2 background from the same scale". [4]
- **Tailwind v4**: 11 shades (50-950) per hue, all in OKLCH (`--color-blue-500: oklch(62.3% 0.214 259.815)`); custom palettes are plain variables in `@theme { --color-*: ... }`. [5]

**"Theme = tokens + component variants."** Common pattern: (a) a flat token file (colour steps, type/space scales, radius, shadow, motion), (b) semantic roles mapped onto steps (`--surface`, `--on-surface`, `--accent`), (c) components that read only role variables and accept a small enum of structural variants. Tokens change mood; variants change structure; both must vary or output converges. **(opinion, consistent with [4][5][6-8])**

### 1.2 How platforms ship visually different sites from one codebase

**Shopify Online Store 2.0 / Dawn.** A JSON template is a `sections` object plus an `order` array, rendered in order "with no markup between"; limits: 25 sections/template, 50 blocks/section, 1,000 templates/theme; sections must define `presets` to be addable in the editor. [6] Section schema separates `settings`, `blocks`, `presets` ("different layouts and use cases"), `default`, `limit`, `max_blocks`, and `enabled_on`/`disabled_on` gating. [7] Theme-level tokens live in `settings_schema.json`, exposed to Liquid as `settings` [9]; the `color_scheme_group` type (only allowed there) defines named schemes with required roles `background`, `text`, `primary_button`, `secondary_button`, their borders, `on_*`, `links`, `icons`, and any section or block picks one via a `color_scheme` setting. [8] Dawn is source-available, server-rendered Liquid, "lean" by policy, ~3.1k stars / ~4.5k forks, with forks pulling upstream via git remotes. [10] That is the architecture we want: tokens + a finite section library + per-page JSON that orders sections and binds a scheme to each.

**Webflow/Relume.** Relume advertises 1k+ components in Figma, Webflow (Client-First) and React, named "Name + Number" (Header 1…, Layout 1…), grouped into Navbars, Footers, Hero, Feature, CTA, Pricing, Testimonial, FAQ, Blog, etc. [11] Variety comes from archetype count plus per-site class tokens, not per-component cleverness. Framer's marketplace lists templates across 56 categories (21 free / 9 paid at $2-$149 on the fetched page) with no exposed theming model. [12] **(weak on Framer internals)**

### 1.3 Static generators for schema-driven content

- **Astro content collections:** `src/content.config.ts` + `defineCollection()`; `glob()` (md/mdx/markdoc/json/yaml/toml directories) and `file()` (one JSON/YAML/TOML array, entries need `id`); Zod schemas drive validation and types; `getCollection`/`getEntry`/`render`. [13]
- **Eleventy data cascade:** computed → template front matter → template data files → directory data files → layout front matter → config global data → global data files; deep-merge unless `override:`; Nunjucks, Liquid, Handlebars, JS/TS, WebC. [14] 11ty's 4,000-markdown-file benchmark: Hugo 0.68 s, Eleventy 1.93 s, Astro 22.90 s, Gatsby 29.05 s, Next 70.65 s (July 2022 — **dated**). [15]
- **Hugo:** Go binary, "world's fastest framework"; YAML/TOML/JSON front matter; `cascade` pushes values down a section tree. [16][17] Go templates are the cost. **(opinion)**
- **Keystatic** (schema in code, 30+ field types, local/GitHub storage, YAML/JSON/MDX, Next/Astro/Remix) [18] and **Decap CMS** (git-backed React UI, `config.yml` collections/fields) [19] add a non-developer editing surface over the same files; not needed while agents write the JSON.
- Engines for a hand-rolled generator: **Jinja** 3.1 (inheritance, autoescape, sandbox, macros; one dependency, MarkupSafe) [20]; **Nunjucks** ("inspired by Jinja2", inheritance, macros, async; 8 kB gzipped) [21]; **Eta** (TypeScript, EJS-like, layouts/partials/async; homepage states no size or zero-dep claim) [22].

### 1.4 Comparison (one-person studio, agents emit JSON)

| Option | Learning curve | Dependency weight | Build speed | Fit for agent-written JSON content | Verdict |
|---|---|---|---|---|---|
| Python + Jinja2 | Very low; Jinja is the lingua franca of LLM training data **(opinion)** | Jinja + MarkupSafe + Pillow/PyYAML | Fast for <1k pages; single process | Excellent: load JSON, validate with `jsonschema`/pydantic, render | Strong candidate |
| Node + Nunjucks | Very low (same syntax family) | nunjucks + sharp; already on Railway/Express | Fast | Excellent; same runtime as the host app | Strongest candidate given the existing Node host |
| Node + Eta | Low; EJS style | Tiny | Fast | Good, but less structured (no block inheritance idiom like Jinja's) | Fine; less familiar to agents |
| Astro | Medium (components, islands, config) | Vite, Rollup, many transitive deps | Slowest of the four in 11ty's benchmark [15] | Very good typing via Zod [13], but heavy for pure static marketing pages | Over-engineered for this |
| Eleventy | Low-medium | Moderate; batteries (Image plugin [23]) | Fast [15] | Very good; data cascade suits per-site + per-page JSON [14] | Good second choice |
| Hugo | Medium-high (Go templates) | Single binary | Fastest [15][16] | Good, but template authoring friction | Not recommended |

---

## 2. Programmatic palette extraction from photos

**Extractors.**
- **node-vibrant**: MMCQ quantizer, returns named swatches (Vibrant, Muted, DarkVibrant, LightVibrant, …), same API in Node, browser and workers; colours can differ slightly across platforms because of canvas decoding. [24]
- **Color Thief**: `getColor()`/`getPalette()`; the current docs say it quantizes in OKLCH by default and in Node requires `sharp` as a peer dependency; it also exposes WCAG contrast helpers. [25]
- **Material Color Utilities (MCU)**: C++/Dart/Java/Swift/TS/Kotlin; modules `hct`, `quantize` (Celebi, "uses results from Wu and WSMeans"), `score`, `palettes`, `scheme`, `dynamiccolor`, `contrast`, `blend`, `temperature`. [26][29] Scoring rewards hue spread (30° neighbourhoods) and proximity to a target chroma of 48, and filters near-greys and rare colours. [29]
- Classical algorithms: **median cut** recursively splits the colour set at the median of its longest axis (Heckbert 1982) [30]; **k-means** (Lloyd's) partitions to nearest means, is NP-hard in general and converges to local minima, and is widely used for colour quantization. [31] In practice MMCQ is fine for "what is this photo's palette"; the quality problem is downstream (choosing *usable* hues), which is what MCU's `score` step solves. **(opinion)**

**HCT and guaranteed contrast.** HCT combines CAM16 hue and chroma with L\*a\*b\* lightness ("Cam16-JCH and L\*a\*b\* was used to introduce HCT"). [28] A tonal palette varies tone 0-100 at fixed hue/chroma. [26] MCU's own concept doc states: "a difference of 40 in tone guarantees a WCAG contrast ratio ≥ 3.0" and "a difference of 50 in tone guarantees a contrast ratio ≥ 4.5"; its default scheme "meets AA", medium contrast "exceeds AA", high contrast "meets AAA". [27] The TS `contrast.ts` exposes `ratioOfTones`, `lighter(tone, ratio)`, `darker(tone, ratio)`, with the WCAG formula `(lighter+5)/(darker+5)` on Y, noting that linearised Y "becomes HCT's tone". [32] This is the single most useful idea for our generator: pick hue/chroma from the photo, then pick *tones* by rule, and contrast is arithmetic rather than trial and error.

**OKLCH tooling.** culori supports Oklab/Oklch/Okhsl/Okhsv plus Lab/LCh/P3/Rec2020 and exports `wcagContrast`, `wcagLuminance`, `clampChroma`, `clampGamut`, `toGamut`, `formatCss`. [33][34] chroma.js has `chroma.oklch()`, `scale().mode('oklch')`, `chroma.contrast()` (WCAG) and `chroma.contrastAPCA()`. [35] color.js `contrast()` supports `WCAG21`, `APCA`, `Michelson`, `Weber`, `Lstar`, `DeltaPhi`. [36] Evil Martians' case for OKLCH over HSL: HSL lightness is not perceptual ("hue changes could also change lightness, thus making text unreadable"), OKLCH lets you change L alone with predictable contrast, and reaches P3. [37] Note that OKLCH L and HCT tone are both perceptual-lightness axes but differ numerically; the tone-delta guarantees above are stated for HCT tone, not OKLCH L. **(opinion/caution)**

**APCA vs WCAG 2.** APCA (Myndex) is a perceptual contrast model producing Lc values; the apca-w3 README's lookup guidance puts Lc 90 at maximum/body-preferred, Lc 75 as the body-text baseline, Lc 60 for larger text, Lc 45 sub-fluent, Lc 30 spot text (placeholders, disabled), with text/background order mattering; it is "beta" and "being evaluated as a replacement for WCAG 2 contrast math for future standards", licensed to W3/AGWG for that purpose. [38][39] WCAG 2.2 (W3C Recommendation, 12 Dec 2024) remains the enforceable baseline: SC 1.4.3 requires 4.5:1 for text and 3:1 for large text (18 pt, or 14 pt bold); SC 1.4.11 requires 3:1 for UI components and graphics. [40] WCAG 3.0 is still a Working Draft (10 Sep 2026) that says "it is inappropriate to cite this document as other than a work in progress" and "The contrast algorithm used in WCAG 3 is yet to be determined." [41] **Policy: gate on WCAG 2.x ratios; use APCA (or MCU tone deltas) only as a design heuristic for choosing nicer pairs within the WCAG-passing set.**

**Recipe: accessible pairs from an extracted hue (OKLCH).** (1) Extract 5-8 swatches (node-vibrant or MCU quantize+score). (2) Convert the accent to OKLCH; keep H, `clampChroma` to sRGB. (3) Build a 12-step ladder at fixed L (e.g. 0.99, 0.97, 0.94, 0.90, 0.85, 0.78, 0.70, 0.60, 0.52, 0.46, 0.40, 0.22), tapering C toward the ends, with Radix-style roles [4]. (4) Verify every (text, surface) and (on-accent, accent) pair with `wcagContrast` ≥ 4.5 (≥ 3 at display sizes), nudging L until it passes. [33][34][40] The L values are a starting point, not a standard. **(opinion)**

---

## 3. Font pairing at scale

**Optical size.** `font-optical-sizing: auto` is the default and Baseline since March 2020; the browser maps the `opsz` axis to the CSS `font-size` (12 px → opsz ≈ 12, 36 px → ≈ 36), so small sizes get sturdier strokes and large sizes get more delicate, higher-contrast forms. [42] Google Fonts' glossary: small optical sizes "have less stroke contrast, more open and wider spacing, and a taller x-height" than display sizes; browsers map opsz to px because they have no physical size; it can be forced off or set explicitly with `font-variation-settings`. [43] Axis ranges from the Google Fonts metadata endpoint [44-50]:

| Family | opsz | wght | Other | Designer |
|---|---|---|---|---|
| Bodoni Moda | 6-96 (default 11) | 400-900 | — | Owen Earl |
| Fraunces | 9-144 (default 14) | 100-900 | SOFT 0-100, WONK 0-1 | Undercase Type |
| Newsreader | 6-72 (default 16) | 200-800 | — | Production Type |
| Literata | 7-72 (default 14) | 200-900 | — | TypeTogether |
| Source Serif 4 | 8-60 (default 14) | 200-900 | — | Frank Grießhammer |
| DM Sans | 9-40 | 100-1000 | — | Colophon |
| Bricolage Grotesque | 12-96 | 200-800 | wdth 75-100 | Mathieu Triay |

The Fraunces repo documents that at 9 pt "the x-height increases, spacing opens up, and the characters expand in width", 144 is the display master, and WONK auto-disables above opsz 18. [51] **Why display text can go hairline:** auto optical sizing drives opsz to the px size, so a 96-128 px headline in Bodoni Moda or Fraunces lands at the maximum-contrast master, where thins are finest; add a light weight, a low-DPR screen, light-on-dark or a photo background and the hairlines vanish. Fix: pin a mid master in the hero, `font-variation-settings: "opsz" 48;` (or `font-optical-sizing: none` and choose explicitly), keeping `auto` for body. Mechanism from [42][43][51]; the pin is practice, not a quoted guideline. **(opinion)**

**Pairing sources.** Fontjoy pairs fonts with a neural net trained on Google Fonts [52]; FontPair curates 500+/"1,000+" Google Fonts and Fontshare pairings [53]; Typewolf publishes a Site of the Day, Top-40 lists and "Top 10 Serif + Sans-Serif Font Combos on Google Fonts" [54]. Treat them as a seed list, then freeze a finite, tested set — unbounded choice is itself a sameness generator because every agent picks Playfair + Montserrat. **(opinion)**

**The generic wedding trio.** High-contrast serif (Playfair Display, wght 400-900, no opsz axis per the metadata endpoint) + geometric sans (Montserrat/Jost) + script (Great Vibes, Pinyon Script). It reads generic because it is the default output of every pairing tool and marketplace, the script carries no information, and Playfair has the hairline problem with no opsz axis to correct it. **(opinion)**

**Loading.** `font-display`: `block` (short block, infinite swap), `swap` (tiny block, infinite swap), `fallback` (tiny block, short swap), `optional` (tiny block, no swap) [55]; web.dev: `optional` when CLS matters most, `swap` as a balance, WOFF2 only, `unicode-range` subsetting, `size-adjust` metric overrides on the fallback. [56] Google Fonts CSS2: `family=Fraunces:opsz,wght@9..144,100..900`, axes alphabetical, `display=swap`, `text=` subsetting (up to 90% smaller). [57] Generator rule: self-host WOFF2, one `@font-face` per family with the full axis range, `font-display: swap`, metric-matched fallback per pairing.

**Ten candidate pairings** (display / body; all open-licence Google Fonts; axis data from [44-50] and the same metadata endpoint for the others):

| # | Mood | Display | Body | Pin / weights | Legibility risk at display size |
|---|---|---|---|---|---|
| 1 | editorial-refined | Newsreader | Source Serif 4 | Display opsz 36-48, wght 500; body auto, 400 | Low |
| 2 | warm-organic | Fraunces | DM Sans | opsz 72, wght 600, SOFT 50, WONK 1; body 400 | Medium: opsz 144 + wght ≤300 is hairline-thin — never auto at ≥96 px |
| 3 | modern-minimal | Inter (opsz 14-32) | Inter | 600 display, 400 body; letter-spacing −0.02em | Low |
| 4 | garden-romantic | Cormorant Garamond (wght 300-700) | Karla | Display 500-600, never 300; body 400 | High: Cormorant is light by design; 300 on photos vanishes |
| 5 | coastal-airy | Bricolage Grotesque | Literata | opsz 96, wght 300-400, wdth 90; body opsz auto | Medium: wght 200 at hero size is faint |
| 6 | heritage-classic | EB Garamond (400-800) | Albert Sans | Display 500, body 400 | Medium: small x-height; keep hero ≥ 56 px |
| 7 | bold-contemporary | Space Grotesk (300-700) | Work Sans | 700 display, 400 body | Low |
| 8 | quiet-luxury | Bodoni Moda | Figtree | opsz 48, wght 500 (not auto); body 400 | High: auto opsz 96 + light weight is the textbook hairline failure |
| 9 | craft-grotesque | Instrument Serif (static) | Instrument Sans | Display 400 italic sparingly; body 400-500 | Medium: single weight, thin at >120 px |
| 10 | playful-precise | Young Serif (static) | Plus Jakarta Sans | Display 400; body 400/600 | Low |

Risk notes are judgement from axis ranges and the optical-size mechanism, not from a legibility study. **(opinion)**

---

## 4. Layout archetypes and "sameness"

**Vocabularies.** Atomic design: atoms → molecules → organisms → templates → pages, explicitly "not a linear process" but "a mental model". [58] Every Layout (Pickering & Bell) defines 13 intrinsic primitives — Stack, Box, Center, Cluster, Sidebar, Switcher, Cover, Grid, Frame, Reel, Imposter, Icon, Container — built to work "without the need for @media breakpoints". [59] Utopia (Gilyead & Mudford, Clearleft) generates fluid type and space scales with `clamp()` between a small and a large viewport, plus space pairs. [60] Bento grids are compartmentalised, mixed-size tiles implemented with `grid-template-areas`/spans, popularised by Apple's keynote graphics; stated cons include weak hierarchy when tiles are uniform and screen-reader order issues. [61] Relume's 1k+ numbered sections [11] are the industrial version of an archetype library.

**Why template sites look the same.** Goree, Doosti, Crandall & Su (Indiana University; CHI 2021, "Investigating the Homogenization of Web Design") analysed ~200,000 screenshots from ~10,000 sites (Russell 1000, Alexa top 500, Webby nominees) with three distances — colour, layout, and a learned classifier — and found between-site differences peaked 2008-2010 and then fell, layout distance dropping by over 30%; the driver was shared libraries (Bootstrap, FontAwesome, jQuery UI) rather than copying. [62][63] (The PDF is no longer at its original URL — 301 to the lab homepage — so these figures come from two press write-ups; **weak**.) Boris Müller's 2018 essay argues CMS templates are "content agnostic. And that is the problem", because "form should both reflect and shape content". The essay is behind a Medium 403 and an archive block; quotes are from search snippets only. **(weak)** [64]

**What creates perceived uniqueness (opinion):** in rough order of weight — (1) hero composition and image treatment (full-bleed / framed / split / type-only); (2) type personality (serif vs grotesque, weight, opsz, measure, case); (3) palette *character* (chroma, warm/cool neutral, dark vs light surface), not hue alone; (4) section rhythm (density alternation, asymmetric Sidebar vs symmetric Switcher, Cover height); (5) shape language (radius, borders, shadows); (6) motion; (7) copy voice. A different combination across 1-5 reads as a different site; swapping hue alone does not.

**Measuring similarity.** Bohunsky & Gatterbauer (WWW 2010) argue rendering is a "lossy mapping", so visual structure rather than DOM is what users perceive, and formalise a visual box-model representation for similarity. [65] The CHI 2021 work used colour and layout distances plus a learned embedding. [62] Perceptual hashing (aHash, pHash via DCT, dHash, wHash, HSV colorhash) with Hamming distance on 64-bit hashes is the cheap screenshot metric. [66] Proposed fingerprint: per site, (a) pHash + colorhash of a 1280×800 and a 390×844 screenshot, (b) section-sequence string (archetype IDs in order), (c) token vector (hue, chroma, surface L, font-pair ID, radius, density). Distance = weighted Hamming(pHash) + Hamming(colorhash) + normalised edit distance of the sequence + token distance; reject a site whose nearest neighbour is under threshold on any two components. Weights must be tuned empirically; the literature gives none. **(opinion)**

---

## 5. Image pipeline

- **sharp (Node):** `resize({ fit, position, kernel, withoutEnlargement })` — `withoutEnlargement: true` prevents upscaling; fit modes cover/contain/fill/inside/outside; default kernel lanczos3. [67] `.webp()` quality 80, effort 4; `.avif()` quality 50, effort 4 (0-9), chroma 4:4:4; `.jpeg({ mozjpeg: true })` enables trellis/overshoot/scan optimisation. [68]
- **Pillow (Python):** WebP `quality` (default 80), `method` 0-6 (default 4), `lossless`, `alpha_quality`; AVIF `quality` (default 75), `speed` 0-10 (default 6), `codec`, `subsampling`; Pillow's thumbnail/resize does not forbid upscaling, so guard with `if target < source.width`. [69] Both are adequate; sharp is faster in practice and lives in the same runtime as Express, Pillow wins if the generator is Python. **(opinion on speed; not benchmarked here)**
- **Markup:** `srcset` with `w` descriptors + `sizes` for resolution switching; `<picture>` + `<source media>` for art direction; the browser takes the first matching `sizes` condition and the smallest candidate ≥ slot × DPR. [70] Eleventy's Image plugin is a reference implementation: `widths`, formats webp/avif/jpeg/png/svg, emits `<img>`/`<picture>` with srcset, "does not upscale raster images larger than original size", disk cache, HTML-transform mode since v3. [23]
- **Lighthouse "properly size images"** flags an image when the rendered size (accounting for DPR) implies ≥ 4 KiB of savings versus the delivered file. [71] So a 3-4 width ladder per slot (e.g. 480/768/1200/1600 for full-bleed; 400/800 for cards) with honest `sizes` keeps it green.
- **LCP:** images start Low priority until layout proves they are in-viewport; `fetchpriority="high"` on the hero starts it High immediately (Google Flights LCP 2.6 s → 1.9 s); use `fetchpriority="low"` on offscreen carousel slides and never `loading="lazy"` on the hero. [72]
- **Placeholders:** BlurHash encodes an image into a 20-30-character string [73]; ThumbHash encodes more detail in similar space, includes aspect ratio and alpha, with no tunable parameters. [74] A 16-px-wide inline WebP data URI is the dependency-free alternative. **(opinion)**

---

## 6. Recommendation for Insert (one page)

**Generator: Node + Nunjucks, one script, no framework.** The host is already Express on Railway, so a `generate.js` that reads `sites/{slug}/site.json`, validates against JSON Schema (`ajv`), renders Nunjucks, runs sharp, and writes `dist/{slug}/` costs three dependencies. Jinja2 + Pillow is an equally light Python twin; pick Node only to avoid a second runtime on deploy. Astro adds typing and islands we do not need and had the slowest build in the one benchmark found [15]; Eleventy is the fallback if we later want a dev server, the data cascade and the Image plugin for free [14][23]. Hugo's speed is irrelevant at our page counts and Go templates are a tax.

**Content schema (JSON, agent-authored).** `site.json` = `{ brand: {name, tagline, voice}, theme: {pack, accentSource: "hero.jpg" | "#hex", mode}, fonts: {pairId, headlineOpsz}, pages: [{ path, sections: [{ archetype, variant, scheme, data }] }] }` — Shopify's split: site-level tokens, a `scheme` per section, ordered sections per page, each archetype with a small `variant` enum and a schema-typed `data` block [6-9][13].

**Theme packs = DTCG token files.** 8-12 packs as `.tokens.json` [1]: colour-ladder rules (OKLCH L steps + chroma curve), Utopia-style `clamp()` type and space scales [60], radius, border/shadow language, motion. A build step derives the palette from the hero photo (quantize+score → hue/chroma → L ladder → `wcagContrast` gate at 4.5/3) [24][26][27][29][33][40] and emits `:root { --token: value }`. Packs change character (chroma, neutral temperature, dark/light surface, shape), not just hue.

**Finite archetype library.** ~6 heroes × 4 feature/story × 3 gallery × 3 testimonial × 2 offer × 3 CTA × 2 footer, built from Every Layout primitives [59], each with 2-3 structural variants — about 70 blocks, far short of Relume's 1k [11] but with 10 font pairs and 10 packs the space is in the millions; the guard below stops agents from always picking the same corner of it.

**Diversity guard.** After build, screenshot desktop and mobile, compute pHash + colorhash [66], the section sequence and the token vector; a new site must clear a minimum distance from every existing site on at least two of {pixel, colour, structure, tokens}, otherwise re-roll the weakest dimension (usually hero or pack) before a human sees it. Cheap, deterministic, and aimed at the two axes the CHI 2021 work found collapsing [62].

**Trade-offs.** (1) A hand-rolled generator means owning dev server, cache-busting and incremental builds; keep it under ~600 lines or switch to Eleventy. (2) Photo-derived palettes are only as good as the photo; keep a `#hex` override and a neutral fallback pack. (3) Finite archetypes cap novelty; the guard reduces repetition but cannot invent composition — budget a new archetype or pack every few sites. (4) Pinned opsz/weights and WCAG gating will reject some "prettier" combinations; that is the point. (5) Fingerprint thresholds are untuned and the literature gives no numbers; expect two or three calibration rounds.

---

## Sources (URL — HTTP status observed; "WF" = content retrieved via WebFetch, "curl" = status from a direct curl sweep)

1. https://www.designtokens.org/TR/drafts/format/ — WF 200 (reached via 301 from design-tokens.github.io → tr.designtokens.org); curl 301
2. https://styledictionary.com/ — 200
3. https://open-props.style/ — 200
4. https://www.radix-ui.com/colors/docs/palette-composition/understanding-the-scale — 200
5. https://tailwindcss.com/docs/colors — 200
6. https://shopify.dev/docs/storefronts/themes/architecture/templates/json-templates — 200
7. https://shopify.dev/docs/storefronts/themes/architecture/sections/section-schema — 200
8. https://shopify.dev/docs/storefronts/themes/architecture/settings/input-settings — 200
9. https://shopify.dev/docs/storefronts/themes/architecture/config/settings-schema-json — 200
10. https://github.com/Shopify/dawn — 200
11. https://www.relume.ai/components — 200 (301 from relume.io/components)
12. https://www.framer.com/marketplace/templates/ — 200
13. https://docs.astro.build/en/guides/content-collections/ — 200
14. https://www.11ty.dev/docs/data-cascade/ — 200
15. https://www.11ty.dev/docs/performance/ — 200 (benchmark is July 2022; weak/dated)
16. https://gohugo.io/ — 200
17. https://gohugo.io/content-management/front-matter/ — 200
18. https://keystatic.com/docs/introduction — 200
19. https://decapcms.org/docs/intro/ — 200
20. https://jinja.palletsprojects.com/en/stable/ — 200
21. https://mozilla.github.io/nunjucks/ — 200
22. https://eta.js.org/ — 200
23. https://www.11ty.dev/docs/plugins/image/ — 200
24. https://github.com/Vibrant-Colors/node-vibrant — 200
25. https://lokeshdhakar.com/projects/color-thief/ — 200
26. https://github.com/material-foundation/material-color-utilities — 200
27. https://raw.githubusercontent.com/material-foundation/material-color-utilities/main/concepts/contrast_for_accessibility.md — 200
28. https://raw.githubusercontent.com/material-foundation/material-color-utilities/main/concepts/color_spaces.md — 200
29. https://raw.githubusercontent.com/material-foundation/material-color-utilities/main/concepts/color_extraction.md — 200
30. https://en.wikipedia.org/wiki/Median_cut — 200
31. https://en.wikipedia.org/wiki/K-means_clustering — 200
32. https://github.com/material-foundation/material-color-utilities/blob/main/typescript/contrast/contrast.ts — 200
33. https://culorijs.org/color-spaces/ — 200
34. https://culorijs.org/api/ — 200
35. https://gka.github.io/chroma.js/ — 200
36. https://colorjs.io/docs/contrast — 200
37. https://evilmartians.com/chronicles/oklch-in-css-why-quit-rgb-hsl — 200
38. https://github.com/Myndex/SAPC-APCA — 200
39. https://github.com/Myndex/apca-w3 — 200
40. https://www.w3.org/TR/WCAG22/ — WF 200; curl 403 (bot block)
41. https://www.w3.org/TR/wcag-3.0/ — WF 200; curl 403 (bot block)
42. https://developer.mozilla.org/en-US/docs/Web/CSS/font-optical-sizing — WF 200; curl 301 (MDN path move)
43. https://raw.githubusercontent.com/google/fonts/main/cc-by-sa/knowledge/glossary/terms/optical_size_axis/content.md — 200 (source of fonts.google.com/knowledge/glossary/optical_size_axis, which is a JS shell)
44. https://fonts.google.com/metadata/fonts/Bodoni%20Moda — 200 (JSON; axes/designers)
45. https://fonts.google.com/metadata/fonts/Fraunces — 200
46. https://fonts.google.com/metadata/fonts/Newsreader — 200
47. https://fonts.google.com/metadata/fonts/Literata — 200
48. https://fonts.google.com/metadata/fonts/Source%20Serif%204 — 200
49. https://fonts.google.com/metadata/fonts/DM%20Sans — 200
50. https://fonts.google.com/metadata/fonts/Bricolage%20Grotesque — 200 (same endpoint also returned 200 for Inter, Playfair Display, Cormorant Garamond, Karla, EB Garamond, Albert Sans, Space Grotesk, Work Sans, Figtree, Instrument Serif/Sans, Young Serif, Plus Jakarta Sans, Great Vibes, Pinyon Script, Jost)
51. https://github.com/undercasetype/Fraunces — 200
52. https://fontjoy.com/ — 200
53. https://www.fontpair.co/ — WF 200; curl 302
54. https://www.typewolf.com/ — 200
55. https://developer.mozilla.org/en-US/docs/Web/CSS/@font-face/font-display — WF 200; curl 301
56. https://web.dev/articles/font-best-practices — 200
57. https://developers.google.com/fonts/docs/css2 — 200
58. https://atomicdesign.bradfrost.com/chapter-2/ — 200
59. https://every-layout.dev/layouts/ — 200
60. https://utopia.fyi/ — 200
61. https://www.freecodecamp.org/news/bento-grids-in-web-design/ — 200 (secondary/blog)
62. https://thenextweb.com/news/researchers-analyzed-10000-websites-and-yes-they-all-look-the-same — 200 (secondary press report of the CHI 2021 paper)
63. https://www.thefashionlaw.com/remember-blanding-well-websites-are-all-starting-to-look-the-same-too/ — 200 (secondary)
64. https://borism.medium.com/on-the-visual-weariness-of-the-web-8af1c969ce73 — 403 (not retrieved; quotes from search snippets only — weak)
65. https://archives.iw3c2.org/www2010/proceedings/www/p1067.pdf — 200 (PDF; abstract read via pypdf)
66. https://github.com/JohannesBuchner/imagehash — 200
67. https://sharp.pixelplumbing.com/api-resize/ — 200
68. https://sharp.pixelplumbing.com/api-output/ — 200
69. https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html — 200
70. https://developer.mozilla.org/en-US/docs/Web/HTML/Guides/Responsive_images — 200
71. https://developer.chrome.com/docs/lighthouse/performance/uses-responsive-images — 200
72. https://web.dev/articles/fetch-priority — 200
73. https://blurha.sh/ — 200
74. https://evanw.github.io/thumbhash/ — 200

Not retrievable (recorded for honesty): https://vision.soic.indiana.edu/papers/websimilarity2021chi.pdf — 301 to lab homepage, PDF gone; https://dl.acm.org/doi/10.1145/3411764.3445156 — 403; https://m3.material.io/styles/color/system/how-the-system-works and https://m3.material.io/blog/science-of-color-design — 200 but JS shells with no extractable text (replaced by the MCU concept docs, items 27-29); https://bigthink.com/technology-innovation/all-websites-look-the-same — 403; web.archive.org — blocked by the fetch tool.
