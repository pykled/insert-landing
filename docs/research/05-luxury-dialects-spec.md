# Luxury dialects: specification for the venue site factory

Written 2026-10-20 (phase 1 of 2). Evidence: `04-luxury-venue-vocabulary.md` (51 top-tier venue sites, screenshots
and computed-style probe). Extends `docs/venue-site-factory.md`, `factory/data/archetypes.json`,
`factory/data/pairings.json`, `factory/data/voices.json`. Phase 2 implements what is below; everything here is
meant to be implementable as data files, Jinja partials, inline SVG and CSS tokens, with no new runtime dependency.

## 0. The change in one paragraph

Today the factory places a venue on six continuous axes and lets fit-ranked selection pick from a library that spans
from "spec-table SaaS" (variant C) to "pale magazine masthead" (variant A). The research says the target market
sits almost entirely inside one band, "premium / elegant", and that the band is wide enough to hold eight clearly
different voices. So the factory gets a **dialect** layer above the axes: a dialect is a bounded region of the
personality space plus a curated sub-library (paper tones, accent rules, pairings, ornament set, hero framings,
section rhythm, motion device, copy voice, moments). Selection first picks a dialect from the venue's photos and a
three-word vibe input, then varies freely *inside* it. Looks outside the premium band become unreachable rather
than merely unlikely.

## 1. Shared premium baseline (applies to every dialect)

These are hard rules the templates enforce regardless of dialect. Each cites the observation it comes from
(numbers are table rows in `04-luxury-venue-vocabulary.md`).

| Rule | Value | Evidence |
|---|---|---|
| Lead photo subject | the place; people allowed only if their bounding box < 10% of the frame (human-tagged `subject` in content) | rows 2, 20, 25, 27, 37, 49 open on the land; 17, 34 (couple-first) read as marketing |
| Paper | never pure white (#fff); paper L 0.93-0.985 with chroma 0.004-0.022, or charcoal L 0.16-0.24 for dark dialects | 3, 14, 27, 38, 50 (cream / oatmeal / blush / grey); 36, 37, 39 (dark) |
| Accent | one chromatic accent measured from the photos, plus an optional metallic (brass / gold) in dark dialects; no second saturated colour | 3, 16, 30, 32 |
| Display weight | 400-600 pinned; never ≤ 300 on photos; `font-optical-sizing: none` + pinned opsz where the family has the axis | 11, 26, 30 (hairline failures) vs 14, 33, 6 |
| Display size | sentence case 48-96 px desktop / 30-44 px mobile, or tracked caps 14-40 px with +0.08 to +0.22 em | section 3.4 of 04 |
| Body | 17-22 px, line-height 1.55-1.7, serif or humanist sans | 47, 22, 49, 4 |
| Sections before the inquiry band | 3-5 | 20, 35, 37, 38 |
| Facts in the first screen | at least two of: max guests, acres, year, number of spaces, distance; price or pricing-guide path visible in the header | 14, 38, 49, 7, 42, 50 |
| Ornament | exactly one device from the dialect set, used at most three times per page | section 3.5 of 04 |
| Hero scrim | if text sits on a photo: gradient from 0 to max 35% black (or 20% white for pale dialects), never a flat wash | 4, 45 (flat scrims) |
| Motion | one device, 600-1200 ms, `cubic-bezier(.2,.7,.2,1)`; everything static under `prefers-reduced-motion`; no hero slider; no autoplay video without a composed poster | 3, 5, 33 |
| CTA | header: outlined or small solid button, 2-4 words; closing band once; no popups on arrival; no badge above the fold | 38, 37, 14 vs 12, 9, 15 |
| Copy | place-first, facts-first, ≤ 14 words per headline; "luxury", "stunning", "unforgettable", "dream" banned from headlines | 47, 49 vs 42, 45 |

## 2. The eight dialects

Each dialect block gives: fit, palette, type, ornament, photography, heroes, rhythm, motion, voice, moments, and
archetype mapping. Palette values are OKLCH (L 0-1, C, H°). "7:1 pairs" lists the text/surface pairs the generator
must pass at ≥ 7:1 (the existing `lib/palette.py` lightness walker does this; the targets below start inside the
passing region so the walk is short). All families are on Google Fonts; `import` strings follow the css2 syntax
already used in `pairings.json` and were checked on 2026-10-21 (see `fonts-check.txt`).

### 2.1 Old-world estate (`estate`)

**Fits.** Stone villas, mansions, castles, mission and hacienda buildings, formal gardens; photo moods: warm stone,
boxwood, terracotta roofs, interiors with chandeliers. Evidence: Sunstone Villa (8), Oheka (36), Glenmere (29),
The Clifton (46), Serra Plaza (14), Inn at the Mission (12), Vizcaya (44).

**Palette.** Paper: warm cream or taupe, L 0.955-0.975, C 0.008-0.018, H 70-95. Deep band: stone-brown or taupe,
L 0.28-0.36, C 0.02-0.05, H 55-85 (Sunstone's header taupe), or charcoal L 0.20 for the castle variant (Oheka).
Accent: from the photos, prefer H 20-60 (terracotta, oxblood) or H 120-160 (boxwood) at C 0.06-0.12, L 0.38-0.48.
Metallic: brass `L 0.70 C 0.09 H 80` for rules and crest only, never for text. 7:1 pairs: ink `L 0.22 C 0.015 H 60`
on paper; paper on deep; `accent-text` walked to L ≤ 0.40 on `accent-tint` L ≥ 0.94; on-deep-soft `L 0.86` on deep.

**Type.** (a) `estate-cormorant`: Cormorant Garamond 600 (caps, tracking +0.10 em) for the name and 500 sentence case
for section titles, min 28 px; body Inter 400 17.5 px / 1.62 (`import=family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500&family=Inter:opsz,wght@14..32,400;14..32,500`).
Caution: weight 500 minimum; small x-height, run display 8% larger. (b) `estate-caslon`: Libre Caslon Display 400
(single weight, min 36 px, tracking -0.005 em) with Libre Caslon Text 400 body 17 px (`family=Libre+Caslon+Display&family=Libre+Caslon+Text:ital,wght@0,400;0,700;1,400`).
Caution: display-only face, never under 36 px; never on busy photos (use it on paper or deep). (c) `estate-cinzel`:
Cinzel 500 tracked caps +0.14 em for the name and kickers only, min 18 px, paired with Cormorant Garamond 500 for
sentence-case headings and Work Sans 400 17 px body (`family=Cinzel:wght@500;600&family=Cormorant+Garamond:ital,wght@0,500;1,500&family=Work+Sans:wght@400;500`).
Caution: Cinzel has no lowercase; limit to ≤ 4 words per line.

**Ornament set (pick one).** `crest-roundel`: inline SVG 56 px circle, 1 px brass stroke, venue initials in the
display face at 22 px, optional inner ring at 44 px; used in header centre, hero, footer. `double-rule`: two 1 px
rules 6 px apart in `line` colour under centred headings, width 64 px. `keyline-frame`: photos get a 1 px `line`
border inset 8 px inside a 0 px-radius box (`outline: 1px solid var(--line); outline-offset: -8px`). `small-caps-kicker`:
`font-variant: small-caps; letter-spacing: .14em` in accent-text.

**Photography.** Crop 3:2 landscape and 4:5 portraits; edge = keyline (formality ≥ 70 already does this); no radius;
no grain; the hero may be full-bleed if the lead photo ≥ 2400 px and shows the building, else inset with margins.
Mild warm grade allowed (+3% warmth via `filter: sepia(.06)` is acceptable, nothing more).

**Heroes.** `cinematic` (mock-only today; port it) with the crest centred and the name in tracked caps; `frame`
(built) with the crest above the headline; new `crest-centred`: full-bleed photo, crest + tracked-caps name +
italic one-line subline centred, two square buttons ("Book a tour" / "Request pricing") like Oheka's pair.

**Rhythm.** hero → facts strip (year, acres, guests, spaces) → story (`split` or `pullquote` with drop cap) → spaces
(`stack` with keyline photos, or `index`) → moment → tour → guide → FAQ (`accordion-split`) → footer. Four to five
sections before tour.

**Motion.** `reveal: fade` 900 ms; crest draws itself once (SVG stroke-dashoffset 1200 ms) on first paint; no parallax.

**Voice.** `heritage` (new preset): declarative, third person, dates and materials. Headlines: "A stone villa in the
Santa Ynez hills, built 1927." / "Twelve acres. One wedding a day." / "The house, the gardens and the long table."
CTA: "Request pricing", "Arrange a visit", "Hold a date". Kicker style caps-rule.

**Signature moments.** `timeline` story (built) when the venue has dates; `crest-reveal` (new, cheap): the crest's
rings draw in as the hero loads; `hours-dial` (spec) rendered as a brass arc for the 12-hour day; `grounds-constellation`
(spec) drawn as a plan with keylines.

**Maps to.** Pairings `heritage-garalde`, `inscriptional-marcellus`; heroes `cinematic`, `frame`; spaces `stack`,
`index`; story `split`, `timeline`, `pullquote`; faq `accordion-split`; tour `scheduler-split`. **New:** pairings
`estate-caslon`, `estate-cinzel`; hero `crest-centred`; ornament partials `crest-roundel`, `double-rule`; voice
`heritage`; moment `crest-reveal`.

### 2.2 Romantic editorial (`editorial`)

**Fits.** Barns and farms that photograph like magazines, garden estates, white houses, venues with a strong
photographer culture; photo moods: soft daylight, florals, film grain, pale sky. Evidence: Cherry Hollow (33),
Wildflower 301 (48), Castle Hill (35), Wythe (38), Blackberry (20).

**Palette.** Paper: white-cream or blush, L 0.965-0.985, C 0.004-0.014, H 40-80 (blush H 20-40 at C 0.012-0.02 is
the Wythe variant). Ink: near-black L 0.20, C ≤ 0.01. Accent: a muted botanical or blush from the photos, C 0.04-0.09,
H 20-45 (blush/rose) or 100-150 (sage), L 0.42-0.55; the accent is used for italics, rules and the kicker, rarely for
fills. Deep band: optional, ink-tinted L 0.22. 7:1 pairs: ink on paper; accent-text walked to L ≤ 0.40; paper on ink.

**Type.** (a) `editorial-didone` (existing: Bodoni Moda 500, opsz 18 pinned, Jost body) for the Cherry Hollow / Didot
register; the 84 px wordmark is allowed because weight 500 and opsz 18 are pinned. (b) `editorial-playfair-free`: not
Playfair; use Gloock 400 (single weight, high-contrast didone, min 40 px, tracking 0) for wordmarks only, Newsreader
500 opsz 24 for headings, Figtree body (`family=Gloock&family=Newsreader:ital,opsz,wght@0,6..72,500;1,6..72,400&family=Figtree:wght@400;500`).
Caution: Gloock only as the name, never as running headings. (c) `editorial-literata`: Literata 500 with `"opsz" 24`
pinned (axis 7-72; auto would thin at 72) for headings 32-64 px, italic 400 for lead-ins, body Literata 400 17 px
opsz 14 (`family=Literata:ital,opsz,wght@0,7..72,400;0,7..72,500;1,7..72,400`). Caution: pin opsz on every element;
a single-family serif system needs the body at ≥ 17 px.

**Ornament set.** `drop-cap`: first letter of the story in the display face, 3 lines tall, accent colour (`initial-letter: 3`
with a float fallback). `italic-lead-in`: a lowercase italic word before tracked caps ("the WILDFLOWER 301") built as
`<em>` + `<span class="caps">` with +0.18 em tracking. `hairline-rule`: 1 px accent rule 48 px wide, centred, under
kickers. `vertical-label`: section name rotated -90° in small caps at the left margin (Cherry Hollow). `press-row`:
only if the venue has real press, as grey wordmarks at 24 px, below the fold.

**Photography.** Inset heroes with 48-80 px margins (Blackberry, Castle Hill); ratios 16:9 hero, 3:2 pairs, 4:5
portraits; edge flush; optional film grain overlay (`background: url(noise.svg); opacity: .06; mix-blend-mode: multiply`)
off by default, on when the photos are already filmic; pairs of photos with a 24-40 px gap (gallery `pairs`, spec).

**Heroes.** `frame` (built, the inset photo under the centred wordmark); `masthead` (built) only if the accent is
muted and the dateline is replaced by the facts strip; new `inset-caption`: inset 16:9 photo, headline in the display
face bottom-left *on paper* below the photo, not on it; kicker above in small caps (Blackberry's placement moved off
the photo for legibility).

**Rhythm.** hero → statement paragraph (one big serif sentence, 28-34 px, with drop cap) → spaces (`index`, or new
`pairs`) → story (`pullquote`) → moment → tour → guide → FAQ (`numbered`) → footer.

**Motion.** `reveal: fade-up` 10 px 800 ms; photos cross-fade in `index`; slide counter "1 — 3" on the pairs gallery
(no autoplay); nothing else.

**Voice.** `romantic` (existing) tightened to facts: "Six gardens, a glasshouse and one long table." / "A 1907 farm,
kept for exactly this." / "Ceremony under the fig. Dinner under glass." CTA: "Check a date", "Request the guide",
"Come see it". Kicker italic.

**Signature moments.** `guest-journey` (built); new `pairs-counter` gallery with captions; `season-toggle` (spec) if
the venue has seasonal sets; `light-shift` (built) works when the photos include golden hour.

**Maps to.** Pairings `editorial-didone`, `coastal-newsreader`, `garden-garamond`; heroes `frame`, `masthead`; spaces
`index`; story `pullquote`; faq `numbered`; tour `scheduler-centered`; gallery `pairs` (spec → build). **New:** pairings
`editorial-literata`, `editorial-gloock`; hero `inset-caption`; ornaments `drop-cap`, `italic-lead-in`, `vertical-label`;
section `statement` (one-paragraph hero follow-up).

### 2.3 Dark and candlelit (`candlelit`)

**Fits.** Historic halls, ballrooms, industrial-heritage hotels, rooftop and dome venues, anything photographed at
dusk or by candle; photo moods: tungsten, brass, deep red, night skyline. Evidence: Hotel Emma (39), Weylin (37),
Oheka (36), Montage (4, the darkness without the scrim), Wythe's candlelit hero (38).

**Palette.** Paper (ground): charcoal L 0.17-0.23, C 0.006-0.02, H from the photos' shadows (warm 60-80 or cool
250-270). Surface-2: L 0.24-0.28 for cards. Ink (text): warm off-white L 0.93, C 0.01. Accent: brass/gold `L 0.72-0.78,
C 0.09-0.12, H 75-90` for rules, frames and kickers; one chromatic accent from the photos (candle red H 25-35, ivy
green H 140-150) at C 0.07-0.12, L 0.55-0.65 for buttons only. 7:1 pairs: ink L 0.93 on ground L ≤ 0.23 (passes at
≈ 13:1); brass on ground must be walked to L ≥ 0.74; button label dark `L 0.18` on brass fill; captions L ≥ 0.80.
Never light paper sections except one "daylight" band mid-page if the venue has daytime photos.

**Type.** (a) `candlelit-marcellus` (reuses `inscriptional-marcellus`): Marcellus 400 tracked caps +0.16 em for the
name and kickers, sentence case at ≥ 36 px for headings, Work Sans body 17 px in off-white. Caution: single weight;
emphasis by small caps. (b) `candlelit-cormorant-sc`: Cormorant SC 600 (small-caps family) for kickers and the name,
Cormorant Garamond 500 for headings ≥ 32 px, body Nunito Sans 400 17.5 px opsz 12 (`family=Cormorant+SC:wght@500;600&family=Cormorant+Garamond:ital,wght@0,500;1,500&family=Nunito+Sans:opsz,wght@12,400;12,600`).
Caution: 600 minimum on dark grounds (thin strokes bloom). (c) `candlelit-forum`: Forum 400 (inscriptional, single
weight) for the name at ≥ 40 px, DM Sans 400 opsz 14 body (`family=Forum&family=DM+Sans:opsz,wght@14,400;14,500`).
Caution: Forum only for the name and one headline; it is decorative.

**Ornament set.** `double-line-frame`: an inline SVG rect pair, outer 1 px brass at inset 12 px, inner 1 px at inset
20 px, corners square, drawn around the hero copy panel and the tour card (Hotel Emma). `botanical-engraving`: one
inline SVG line drawing (laurel, olive or ivy, 320 x 320, 1 px brass stroke, opacity .35) placed behind the story copy,
`aria-hidden`; the factory ships three generic engravings, never a photo trace of the venue. `brass-rule`: 1 px brass
rule with a 6 px diamond at centre. `monogram-seal`: 48 px shield or circle with initials, brass stroke.

**Photography.** Full-bleed or inset on charcoal with a 1 px brass keyline at inset 10 px; ratios 16:9 and 3:2;
portraits 4:5 in pairs; no grain (dark photos already carry it); tungsten photos only in the hero; if the lead is a
daylight photo, the dialect is wrong (selection rule §3). Scrim: none on dark photos; max 25% black gradient on
mid-tone.

**Heroes.** `panel` (spec → build) as a 50/50 with the charcoal panel carrying the double-line frame, kicker, headline,
two buttons; `cinematic` (port) with no scrim; new `silent`: full-height photo with the nav bar at the bottom of the
hero and a single outlined "Inquire" (Weylin) — only when the lead photo ≥ 2400 px and `subject = building`.

**Rhythm.** hero → facts strip in brass small caps → spaces (`stack` on charcoal with keylines, or `index`) → story
(`split` with the engraving) → one daylight band (optional) → tour (`band-cta`, which already is a dark band; on this
ground it becomes a brass-framed card) → guide → FAQ (`plain-list` in off-white) → footer.

**Motion.** `reveal: fade` 1000 ms; the frame's rect strokes draw in on first view (stroke-dashoffset, 1400 ms);
candle-warm hover: buttons shift fill L +0.04 over 300 ms; no parallax, no video.

**Voice.** `evening` (new preset): short, sensory, nouns: "Brass, brick and two hundred candles." / "A 1911 ballroom
for 180 at dinner." / "The dome at dusk. The hall till midnight." CTA: "Inquire", "See the hall", "Hold an evening".
Kicker small caps in brass.

**Signature moments.** `light-shift` (built) reversed: Night is the default, Noon the alternate; new `candle-count`:
`numbers-count` (spec) styled as brass numerals with a flicker-free ease; `hours-dial` (spec) as a brass arc from
first light to last call.

**Maps to.** Pairings `inscriptional-marcellus`; heroes `cinematic`, `panel`; spaces `stack`, `index`; story `split`;
faq `plain-list`; tour `band-cta`. **New:** pairings `candlelit-cormorant-sc`, `candlelit-forum`; hero `silent`;
ornaments `double-line-frame`, `botanical-engraving`, `brass-rule`; dark token set (`paper` = charcoal) in `palette.py`;
voice `evening`.

### 2.4 Modern luxe (`modern-luxe`)

**Fits.** Architect-designed resorts, desert and canyon properties, glass pavilions, minimalist retreats; photo moods:
dusk desert, concrete, water, long shadows. Evidence: Amangiri (27), Shou Sugi Ban (26), Cuixmala (49), Ventana (24),
Sea Ranch Lodge (25, the architectural edge).

**Palette.** Paper: warm grey, L 0.93-0.96, C 0.004-0.010, H 60-90 (Aman) or cool grey H 240-260 at C ≤ 0.006.
Ink: charcoal L 0.24, C 0.01. Accent: a single low-chroma earth from the photos (sand H 70-85, sage H 120-140, slate
H 230-250) at C 0.03-0.06, L 0.45-0.55; buttons are outlined in ink or filled in ink, never in the accent. Deep band:
ink itself. 7:1 pairs: ink on paper; paper on ink; accent-text walked to L ≤ 0.42 (low chroma walks fast).

**Type.** (a) `luxe-instrument` (reuse `quiet-instrument-serif`: Instrument Serif 400 ≥ 32 px, Instrument Sans body)
for the Lyon-class register. (b) `luxe-tracked-sans`: Manrope 500 tracked caps +0.18 em at 13-20 px for names,
kickers and nav, with Instrument Serif 400 at 40-64 px for one headline per page, body Manrope 400 17 px
(`family=Manrope:wght@400;500;600&family=Instrument+Serif:ital@0;1`). Caution: tracked caps never above 24 px; the
serif headline never below 36 px. (c) `luxe-sans-only`: Hanken Grotesk 400/500 (tracked caps 14-18 px for names,
sentence case 44-64 px with -0.02 em for the one headline), body 17.5 px (`family=Hanken+Grotesk:ital,wght@0,400;0,500;1,400`).
Caution: this is the Cuixmala / Sea Ranch register and reads SaaS without ≥ 120 px section padding and inset photos.

**Ornament set.** `hairline-grid`: 1 px rules between rows and columns of the facts strip and spaces list (Aman's
ledger). `counter`: slide or section counter "01 — 04" in tracked caps. `arrow-glyph`: `→` after link labels
(Ventana). `wide-margins`: not an SVG but a token: container 1120 px with 72 px gutters and 160-200 px section padding.

**Photography.** Inset with wide margins (Amangiri) *or* full-bleed landscape with no text (Ojai / Cuixmala); ratios
16:9 and 2:1 panoramic; small captions in tracked caps under each photo; edge flush, zero radius; no grain; cool or
neutral grade untouched. Dusk and overcast photos preferred; a bright midday lead photo pushes selection to
`coastal`.

**Heroes.** `cover-type` (built) with the photo widened to 16:9 and the ledger kept; new `inset-wide`: inset
panoramic photo under a two-row minimal header, headline on paper beneath at 40-56 px, no kicker (Amangiri); new
`landscape-silent`: full-height photo, no text, header only, headline arrives in the next section (Ojai).

**Rhythm.** hero → one-line statement + facts ledger → spaces (`spec-sheet` restyled with hairlines and 4:5 photos,
or `strip` spec → build) → story (`ledger`) → moment → tour (`scheduler-centered`) → FAQ (`plain-list`) → footer.
Three to four sections before tour; padding 160-200 px.

**Motion.** `reveal: none` or `fade` 700 ms; smooth-scroll is *not* added (Lenis-class libraries are out of scope);
cross-fade slideshow with counter (`slideshow` spec → build) at 6 s intervals, static under reduced motion.

**Voice.** `plainspoken` (existing), with the ledger. Headlines: "Thirty acres of canyon. Twelve rooms. One table."
/ "Built 2019. Glass, cedar and the sea." CTA: "Inquire", "Check availability", "Plan a visit".

**Signature moments.** `seat-picker` (built) restyled with hairlines; `slideshow-counter` (new); `numbers-count` (spec);
`window-reveal` (spec) suits the architecture.

**Maps to.** Pairings `quiet-instrument-serif`, `modern-instrument` (only with the padding rule), `desert-dm`; heroes
`cover-type`, `slideshow`; spaces `spec-sheet`, `strip`; story `ledger`; faq `plain-list`; tour `scheduler-centered`;
moment `seat-picker`. **New:** pairings `luxe-tracked-sans`, `luxe-sans-only`; heroes `inset-wide`, `landscape-silent`;
ornaments `hairline-grid`, `counter`.

### 2.5 Coastal and airy (`coastal`)

**Fits.** Ocean-front and lake estates, sailcloth-tent venues, New England and California coast inns, white houses
near water; photo moods: bright, blue-white, hydrangea, sailcloth, haze. Evidence: Castle Hill (35), Rosewood Miramar
(3), Twin Farms (43), Montage Laguna's sea (4), Terranea's clifftop (11).

**Palette.** Paper: white-cream L 0.975-0.985, C 0.003-0.008, H 80-100. Ink: navy-black L 0.22, C 0.03, H 250-260, or
deep green L 0.26, C 0.05, H 150-165 (Rosewood). Accent: from the water or the flowers, H 220-250 (navy/slate blue) or
H 150-170 (sea green) at C 0.05-0.10, L 0.38-0.48; a sand neutral `L 0.90 C 0.02 H 80` for paper-2. 7:1 pairs: navy
ink on paper; paper on navy; accent-text L ≤ 0.42 on tint L ≥ 0.94; white on accent-fill walked to accent L ≤ 0.46.

**Type.** (a) `coastal-newsreader` (existing: Newsreader 500 opsz 24, Figtree). (b) `coastal-engraved`: Rosewood's
register with free faces: Josefin Sans 500 tracked caps +0.22 em at 14-30 px for the name and kickers (geometric,
engraved feel), Cormorant Garamond 500 italic for the one-line subline, body Figtree 400 17 px
(`family=Josefin+Sans:wght@400;500&family=Cormorant+Garamond:ital,wght@0,500;1,500&family=Figtree:wght@400;500`).
Caution: Josefin's lowercase is quirky; caps only. (c) `coastal-spectral`: Spectral 500 for headings 36-64 px
(sentence case, -0.01 em), Spectral 400 italic lead-ins, body Spectral 400 17 px or Figtree
(`family=Spectral:ital,wght@0,400;0,500;1,400&family=Figtree:wght@400;500`). Caution: Spectral is light at small sizes;
body ≥ 17 px.

**Ornament set.** `small-caps-kicker` with a 48 px hairline above it (Castle Hill: "IN LOVE, ON THE OCEAN").
`inset-margin`: the hero photo sits inside 56-80 px margins (the margin *is* the ornament). `slide-counter` "1 — 2"
in tracked caps. `compass-rose`: a 40 px inline SVG eight-point star in the footer only.

**Photography.** Inset 16:9 with margins; pairs 3:2; portraits 4:5; edge flush; no grain; keep highlights bright
(never a dark scrim); if text must sit on the photo use a 20% white gradient from the bottom; prefer photos with sky
or water in the upper third.

**Heroes.** `frame` (built) with the headline *below* the photo; new `inset-caption` (shared with editorial); `masthead`
(built) when the venue has a strong wordmark; `slideshow` (spec → build) for properties with three equal landscape
photos (Rosewood's counter).

**Rhythm.** hero → kicker + short lyric statement + facts (guests, acres, water) → spaces (`stack` with flush photos
on paper-2 sand bands, or `index`) → story (`pullquote` or `split`) → moment → tour (`scheduler-split`) → guide →
FAQ (`accordion-split`) → footer.

**Motion.** `reveal: fade` 800 ms; slideshow cross-fade 1200 ms at 7 s; photos scale from 1.02 to 1.00 on reveal
(`transform`, 1200 ms) once; nothing on scroll.

**Voice.** `lyric` (new preset, short sentences, nouns of weather and water): "Lawns to the water. A lighthouse at
the edge." / "Sailcloth, hydrangea, the bay at seven." / "Ninety acres of shoreline for 200." CTA: "Request a
proposal", "Check the date", "Walk the lawn".

**Signature moments.** `light-shift` (built: noon / golden / night is a natural fit by the water); `slideshow-counter`
(new); `season-toggle` (spec) for four-season coasts; `hours-dial` as a tide-like arc.

**Maps to.** Pairings `coastal-newsreader`, `garden-garamond`; heroes `frame`, `masthead`, `slideshow`; spaces `stack`,
`index`; story `pullquote`, `split`; faq `accordion-split`; tour `scheduler-split`; moment `light-shift`. **New:**
pairings `coastal-engraved`, `coastal-spectral`; hero `inset-caption`; ornaments `small-caps-kicker`, `compass-rose`;
voice `lyric`.

### 2.6 Botanical garden (`botanical`)

**Fits.** Garden estates, orchid farms, glasshouses, redwood and canyon gardens, venues whose best photos are plants;
photo moods: green-on-green, dappled light, florals, lavender rows. Evidence: San Ysidro (1), Nestldown's line art
(40), Korakia's florals (6), Maravilla's setting (17), Beaulieu Garden's content (21).

**Palette.** Paper: warm white L 0.97-0.985, C 0.005-0.012, H 90-110 (a hint of green-cream). Ink: deep green-black
L 0.22, C 0.02, H 150-170. Accent: a leaf or flower colour from the photos: sage/olive H 110-150 at C 0.05-0.09,
L 0.40-0.50 (text use) or a floral H 10-40 / 320-350 at C 0.08-0.12 only for the kicker and one rule. Deep band:
forest green L 0.28, C 0.05, H 155. 7:1 pairs: ink on paper; paper on deep; sage accent-text walked to L ≤ 0.40 on
tint L ≥ 0.94; floral accent is never a text colour.

**Type.** (a) `garden-garamond` (existing: EB Garamond 500, Nunito Sans). (b) `botanical-fraunces`: Fraunces 500 with
`"opsz" 48, "SOFT" 60, "WONK" 0` pinned for headings 36-72 px (soft, slightly rounded serif), italic 400 for captions,
body Karla 400 17 px (`family=Fraunces:ital,opsz,wght,SOFT,WONK@0,9..144,400,60,0;0,9..144,500,60,0;1,9..144,400,60,0&family=Karla:wght@400;500`).
Caution: pin opsz 48, never auto (hairline at 144); SOFT above 60 goes cartoonish. (c) `botanical-cardo`: Cardo 400
for headings 40-64 px (Babington's register) and italic 400 lead-ins, body Nunito Sans 400 17.5 px opsz 12
(`family=Cardo:ital,wght@0,400;0,700;1,400&family=Nunito+Sans:opsz,wght@12,400;12,600`). Caution: Cardo 400 is light;
only on paper, never on photos.

**Ornament set.** `botanical-line`: one inline SVG line drawing of a leaf sprig or branch, 1 px ink stroke, 120-240 px,
placed as a section opener or footer flourish, `aria-hidden` (Nestldown's white line botanicals; the factory ships
six generic sprigs: olive, fig, fern, lavender, oak, eucalyptus, chosen by a `flora` tag in content). `leaf-rule`:
a 1 px rule with a 12 px leaf glyph at centre. `watercolour-wash`: a very light radial wash (`radial-gradient` of
accent-tint at 8% opacity) behind the statement paragraph (San Ysidro); CSS only. `rounded-arch`: the frame hero's
photo gets `border-radius: 999px 999px 0 0` (glasshouse / arch), only in this dialect.

**Photography.** Ratios 3:2 and 4:5; edge flush or the arch; soft radius 6 px allowed on secondary photos; no grain;
prefer dappled light; the hero may be full-bleed if green dominates the frame (≥ 45% of pixels in H 90-160).

**Heroes.** `frame` (built) with the arch option; `cinematic` (port) with the headline in Fraunces at 56 px over a
light bottom gradient; new `arch-split`: 50/50 with the photo in an arch mask left and copy + date check right on
paper with the wash.

**Rhythm.** hero → statement with a sprig → spaces (`stack`, each band one garden, with "up to N guests" like San
Ysidro's bands) → story (`timeline` if the garden has history, else `pullquote`) → moment → tour (`scheduler-split`)
→ guide → FAQ (`accordion-split`) → footer with a sprig.

**Motion.** `reveal: fade-up` 800 ms; the sprig draws in (stroke-dashoffset 1600 ms) once; `light-shift` crossfades;
hover on space bands tints the paper to accent-tint over 400 ms.

**Voice.** `romantic` (existing) with plant nouns: "Lavender rows, an orchard, a glasshouse for 160." / "Six gardens.
One wedding a day." CTA: "See if it's open", "Walk the gardens", "Send the guide".

**Signature moments.** `light-shift` (built); `season-toggle` (spec, strongest here: gardens change); `guest-journey`
(built) when the spaces form a route; new `sprig-draw` (cheap: the botanical line drawing animates once).

**Maps to.** Pairings `garden-garamond`, `warm-fraunces` (with WONK off); heroes `frame`, `cinematic`; spaces `stack`;
story `timeline`, `pullquote`; faq `accordion-split`; tour `scheduler-split`; moments `light-shift`, `guest-journey`,
`season-toggle`. **New:** pairings `botanical-fraunces`, `botanical-cardo`; hero `arch-split`; ornaments
`botanical-line` (six SVGs), `leaf-rule`, `watercolour-wash`, `rounded-arch`.

### 2.7 Rustic-refined (`ranch`)

**Fits.** Ranches, vineyards, barns with good bones, canyon and foothill venues, farm retreats; photo moods: golden
grass, oaks, olive, ochre dust, timber. Evidence: The Ranch at Laguna Beach (16), Santa Lucia Preserve (32), Holman
Ranch (41), Inness (30), Greengate's barn (7), Sunstone's hills.

**Palette.** Paper: oatmeal/cream L 0.95-0.97, C 0.012-0.022, H 75-95 (warmer and more tinted than editorial). Ink:
warm brown-black L 0.23, C 0.02, H 60. Accent: ochre H 65-85 at C 0.08-0.12, L 0.50-0.58 (non-text) with accent-text
walked to L ≤ 0.42; or oxblood H 15-30 C 0.10 L 0.38; or terracotta H 35-50 (Inness). Deep band: olive L 0.30, C 0.04,
H 110-125 (The Ranch's venue band) or oxblood. 7:1 pairs: ink on paper; paper on olive deep; on-deep-accent (ochre)
walked to L ≥ 0.76 on olive; white on accent-fill requires ochre L ≤ 0.46 (so ochre fills become a darker "bronze";
the walker already does this).

**Type.** (a) `warm-fraunces` (existing: Fraunces 500, opsz 36, SOFT 40, WONK 1, Karla). (b) `ranch-canela-free`: Lora
500 (sentence case 40-64 px, -0.01 em) with Lora 400 italic lead-ins and body Karla 400 17 px
(`family=Lora:ital,wght@0,400;0,500;1,400&family=Karla:wght@400;500`). Caution: Lora 500 only; 400 greys out on
oatmeal. (c) `ranch-display-sans`: Bricolage Grotesque 400 with `"opsz" 96, "wdth" 100` pinned for one 56-72 px
headline (the Inness-style odd display sans, at a legible weight), Hanken Grotesk 400 body 17.5 px
(`family=Bricolage+Grotesque:opsz,wdth,wght@12..96,100,400;12..96,100,500&family=Hanken+Grotesk:wght@400;500`).
Caution: never weight < 400 (Inness runs 100 and goes hairline); never for body.

**Ornament set.** `olive-band`: a full-width deep band in olive for the spaces or tour section with ochre small-caps
kickers (The Ranch). `rope-rule`: a 1 px dashed rule (`border-top: 1px dashed`) with 8 px dashes in accent (subtle,
the only "rustic" ornament allowed). `wood-keyline`: photos get a 1 px warm-brown keyline inset 6 px. `brand-mark`:
a simple line-drawn cattle-brand style monogram (circle + initials, 2 px stroke) 48 px, inline SVG.

**Photography.** Landscape heroes full-bleed (golden hour preferred); ratios 3:2, 16:9; edge flush or wood keyline;
radius 0-4 px; warm grade untouched; no grain. If the barn interior is the lead, use `frame`.

**Heroes.** `cinematic` (port) with the headline bottom-left in Fraunces/Lora over a ≤ 30% warm gradient; `frame`
(built) with the brand-mark above; new `landscape-silent` (shared with modern-luxe) when the land is the point.

**Rhythm.** hero → facts strip (acres, guests, oaks, year) → story (`timeline` for family-owned land, or `split`) →
spaces in the `olive-band` (`stack` on deep) → moment → tour (`scheduler-split`) → guide → FAQ (`accordion-split`) →
footer with the brand-mark.

**Motion.** `reveal: slide` 12 px 800 ms; olive band fades in from paper over 600 ms; `light-shift` golden-hour default.

**Voice.** `warm-host` (existing) with land nouns: "Three hundred acres of oak and grass, forty minutes from town." /
"The barn greets you. The oaks do the rest." CTA: "Come walk it", "Check a date", "Get the guide".

**Signature moments.** `light-shift` (built; golden hour is the point); `guest-journey` (built); `grounds-constellation`
(spec) as a ranch plan with a dashed trail; `numbers-count` for acres.

**Maps to.** Pairings `warm-fraunces`; heroes `cinematic`, `frame`; spaces `stack`; story `timeline`, `split`; faq
`accordion-split`; tour `scheduler-split`; moments `light-shift`, `guest-journey`. **New:** pairings `ranch-lora`,
`ranch-display-sans`; hero `landscape-silent`; ornaments `olive-band`, `rope-rule`, `wood-keyline`, `brand-mark`.

### 2.8 Deco glam (`deco`)

**Fits.** 1920s-40s clubhouses, theatres, downtown lofts with period detail, Palm Springs hotels with a strong brand,
venues with black-and-white archival photography; photo moods: monochrome, geometric, brass, lacquer, pink stucco.
Evidence: Parker Palm Springs (5: the didone + underline bar + b/w pairing), Ebell of Long Beach (15: wide-tracked
light caps), Hotel Emma's frames (39), Greenhouse Loft's caps + italic (50), Vizcaya's monochrome (44).

**Palette.** Paper: ivory L 0.96-0.975, C 0.008-0.014, H 80-95 *or* charcoal L 0.18 (two variants, chosen by photo
brightness). Ink: black L 0.18, C 0.005. Accent: one saturated period colour from the photos or brand (Parker's
orange H 45-55 C 0.16; emerald H 150-160 C 0.10; oxblood H 20 C 0.12) at L 0.45-0.55 for the underline bar and
buttons only; brass `L 0.72 C 0.09 H 82` for frames and rules. 7:1 pairs: ink on ivory; ivory on charcoal; accent is
never body text; accent-text walked to L ≤ 0.40 for kickers only.

**Type.** (a) `deco-bodoni` (reuse `editorial-didone` settings: Bodoni Moda 500, opsz 18, but caps with +0.06 em for
the name at 64-96 px; Jost body). (b) `deco-poiret-free`: not Poiret One (too thin). Use Big Shoulders Display 500 with
tracked caps +0.12 em at 48-80 px for the name (tall condensed deco), Jost 400 body 17 px
(`family=Big+Shoulders+Display:wght@500;600&family=Jost:wght@400;500`). Caution: condensed caps need line-height 1.0
and ≤ 3 words per line. (c) `deco-italiana`: Italiana 400 (single weight, high-contrast geometric) for the name only at
≥ 48 px, Jost 500 tracked caps +0.2 em at 13-16 px for everything else that is a label, Jost 400 body
(`family=Italiana&family=Jost:wght@400;500`). Caution: Italiana is thin; ivory paper only, never on photos or charcoal.

**Ornament set.** `underline-bar`: a 10-14 px tall accent bar sitting behind the lower third of the name (Parker),
built as `background: linear-gradient(transparent 62%, var(--accent) 62%, var(--accent) 88%, transparent 88%)` on an
inline span. `stepped-frame`: inline SVG frame with stepped corners (three 6 px steps) in brass, around the tour card.
`sunburst`: a 64 px inline SVG of 12 brass radiating lines, footer only. `geometric-rule`: a rule of repeating 6 px
chevrons (`background-image` of an inline SVG, 1 px brass), 100% width, 8 px tall.

**Photography.** Monochrome conversion allowed and encouraged for archival or architectural photos
(`filter: grayscale(1) contrast(1.05)`, applied per photo by a `mono: true` tag in content, never to the lead photo
unless the venue's own site is monochrome); pairing a b/w and a colour photo side by side (Parker); ratios 4:5 and 1:1;
edge flush with a 1 px brass keyline on charcoal; no grain.

**Heroes.** `masthead` (built) with the name in deco caps and the underline bar replacing the dateline; `cover-type`
(built) with the 4:5 photo in monochrome; new `pair-split`: headline band on ivory, then a b/w + colour photo pair at
4:5 under it, date check inline.

**Rhythm.** hero → facts strip in tracked caps with the geometric rule → story (`pullquote` with the name of the
architect / year as the kicker) → spaces (`index`, numbered in deco caps) → moment → tour (`band-cta` with the
stepped frame) → guide → FAQ (`numbered`) → footer with the sunburst.

**Motion.** `reveal: fade` 700 ms; the underline bar slides in from left (`scaleX` 0→1, 600 ms, transform-origin left)
once; marquee tickers are *not* allowed (Parker's is brand-specific).

**Voice.** `editorial` (existing), period-specific nouns: "A 1927 clubhouse for 300, restored." / "Lacquer, brass and
a 60-foot ballroom." CTA: "Inquire", "Book a tour", "See rates".

**Signature moments.** `numbers-count` (spec) in deco numerals; `window-reveal` (spec) as a stepped mask; new
`then-now`: a two-photo slider (b/w archival ↔ today) with a brass handle, only when the venue supplies an archival
photo with rights.

**Maps to.** Pairings `editorial-didone`, `loft-archivo` (caps only); heroes `masthead`, `cover-type`; spaces `index`;
story `pullquote`; faq `numbered`; tour `band-cta`. **New:** pairings `deco-big-shoulders`, `deco-italiana`; hero
`pair-split`; ornaments `underline-bar`, `stepped-frame`, `sunburst`, `geometric-rule`; moment `then-now`.

### Dialects considered and folded in

- "Loft / industrial" (Greenhouse Loft, Wythe, Weylin) is not its own dialect for this market: Wythe lands in
  `editorial` (blush paper, inset hero, facts), Weylin in `candlelit`, Greenhouse Loft in `deco` (caps + italic serif,
  ivory). The existing `loft-archivo` pairing stays available inside `deco` and `modern-luxe`.
- "Southern estate" (The Clifton) is `estate` with a white-house photo and gold accent; no new dialect.
- "Quirky brand" (Parker, Six Bells) is not reproducible by a factory and is excluded by design.

## 3. Dialect selection rule

Inputs the factory already has: the palette report (`lib/palette.py`: per-photo OKLab clusters, paper temperature,
accent candidates) and the content file's photo manifest. New inputs: (1) a cheap per-photo analysis added to
`lib/palette.py` (mean L, share of pixels with C < 0.03 ("mono share"), share with H 90-160 and C > 0.05
("foliage share"), share with H 200-260 ("water/sky share"), share with L < 0.35 ("dark share"), share with
H 20-90 and C 0.03-0.10 ("stone/earth share")); (2) a `vibe` block in content: `type` from
{estate, mansion, castle, villa, hacienda, barn, ranch, vineyard, garden, glasshouse, coastal, lake, desert, resort,
hotel, loft, clubhouse, theatre}, `era` (build year or null), and three words from the controlled list below chosen by
the human in 60 seconds.

Controlled vibe words (each maps to dialect weights): *grand, heritage, formal* → estate; *romantic, soft, floral,
editorial* → editorial; *evening, candlelit, moody, brass* → candlelit; *minimal, architectural, serene, modern* →
modern-luxe; *bright, breezy, water, nautical* → coastal; *lush, garden, green, dappled* → botanical; *rustic, land,
golden, timber* → ranch; *glam, period, graphic, monochrome* → deco.

Score each dialect = Σ (photo signals) + Σ (vibe words) + type prior, then take the top score; ties go to the dialect
with the fewer registered sites (diversity). Signals, computed over the palette photos (lead weighted 2x):

| Signal | Threshold | Adds to |
|---|---|---|
| dark share ≥ 0.45 and warm shadows | | candlelit +3 |
| mean L ≥ 0.62 and water/sky share ≥ 0.25 | | coastal +3 |
| foliage share ≥ 0.40 | | botanical +3, ranch +1 |
| stone/earth share ≥ 0.35 and foliage < 0.30 | | estate +2, ranch +1 |
| mono share ≥ 0.70 (near-monochrome photos) and mean L ≥ 0.55 | | modern-luxe +2, deco +1 |
| any photo tagged `mono: true` or an archival photo present | | deco +2 |
| accent candidate chroma ≥ 0.12 (a saturated brand colour) | | deco +1, candlelit +1 |
| warm ochre accent (H 60-90, C ≥ 0.07) and foliage ≥ 0.2 | | ranch +2 |
| paper temperature = warm (existing) | | estate +1, ranch +1, botanical +1 |
| paper temperature = cool | | coastal +1, modern-luxe +1 |
| type prior: estate/mansion/castle/villa/hacienda → estate +2; barn/ranch/vineyard → ranch +2 (barn also editorial +1); garden/glasshouse → botanical +2; coastal/lake → coastal +2; desert/resort → modern-luxe +2; clubhouse/theatre → deco +2 (candlelit +1); loft → deco +1, modern-luxe +1; hotel → estate +1, modern-luxe +1 | | |
| era ≤ 1930 → estate +1, deco +1 (1920-1945: deco +2); era ≥ 2005 → modern-luxe +1 | | |
| each vibe word | | +2 to its dialect |

The build report records the score table so a human can override with `--dialect <id>` (recorded as "human
override", like `--accent-hue`). The dialect then *clamps* the six axes to its region before fit-ranked selection
runs, so the existing selector keeps working unchanged:

| Dialect | formality | scale | era | density | temperature | voice |
|---|---|---|---|---|---|---|
| estate | 75-95 | 55-85 | 10-40 | 40-65 | 20-50 | 50-75 |
| editorial | 65-85 | 45-70 | 35-60 | 55-80 | 35-60 | 20-55 |
| candlelit | 70-90 | 60-90 | 25-60 | 45-70 | 10-40 | 45-70 |
| modern-luxe | 70-90 | 55-80 | 80-100 | 75-95 | 50-80 | 75-95 |
| coastal | 70-85 | 50-75 | 45-65 | 60-85 | 60-85 | 35-60 |
| botanical | 55-75 | 40-65 | 25-55 | 30-55 | 25-50 | 10-40 |
| ranch | 40-65 | 50-80 | 20-50 | 25-50 | 5-35 | 25-50 |
| deco | 75-95 | 55-80 | 55-80 | 60-85 | 40-70 | 65-90 |

Note the floor on `formality` (≥ 40 everywhere) and the ceiling on `density` for `ranch`/`botanical`: that is what
keeps variant-C-style spec sheets and variant-A-style pale mastheads out unless a dialect calls for them (C's
`spec-sheet` survives only inside `modern-luxe`, restyled; A's `masthead` survives inside `editorial`, `coastal` and
`deco` with the dateline replaced by facts).

## 4. Variation inside a dialect

Two venues in the same dialect must still read as different sites. Independent knobs, each a separate selector
dimension with its own fingerprint weight (§6):

1. **Paper tone** within the dialect's range: three buckets (light / mid / tinted; for dark dialects: charcoal-warm /
   charcoal-cool). Chosen from the photos' paper temperature and chroma.
2. **Accent hue** from the photos (existing), plus **accent role**: text-and-rules only vs buttons-and-band.
3. **Pairing**: 2-3 per dialect (above), never the same pairing for consecutive registered sites in a dialect.
4. **Hero framing**: 2-3 per dialect (inset / bleed / type-only / silent / split / crest).
5. **Headline case**: sentence vs tracked caps (where the pairing allows both).
6. **Ornament**: one of 3-4 per dialect.
7. **Body size**: 17 / 19 / 21 px (a token; changes the whole page's pace).
8. **Section rhythm variant**: two orders per dialect (story-before-spaces vs spaces-before-story; facts strip vs
   statement paragraph).
9. **Spaces archetype**: 2 per dialect.
10. **Story archetype**: 2 per dialect.
11. **Signature moment**: 2-3 per dialect.
12. **Motion device**: the dialect's reveal plus one optional device (counter / draw-in / cross-fade) or none.
13. **Photo treatment**: edge (flush / keyline / arch / rounded 6 px), grain on/off (editorial only), mono pairs (deco
    only), crop ratio of the hero (16:9 / 3:2 / 2:1 / 4:5).
14. **Nav style**: centred wordmark + burger / bar / two-row with sub-nav (existing `nav` token plus one new `two-row`).
15. **CTA wording set**: three sets per voice preset, rotated.
16. **Kicker style**: existing (caps-rule / italic / label / small-caps).
17. **Lead photo** (existing fingerprint dimension).

With 2-3 options on each of the ten most visible knobs a dialect has on the order of 10^3 distinct configurations;
the guard (§6) ensures the ones chosen are far apart.

## 5. Exclusions: looks the factory must never output

Enforced by the selector (unreachable) and by `qa.py` (fail if present in rendered HTML/CSS):

1. Pure white paper (`#fff`) with a saturated accent button; any accent C > 0.14 used as a fill outside `deco`.
2. Display weight ≤ 300 on a photo; any display face without pinned weight/opsz; weight 100/200 anywhere.
3. Script, brush, handwriting or typewriter faces (Beloved, Great Vibes, Allura, Special Elite and class).
4. Playfair Display, Montserrat, Raleway, Poppins, Arial, Open Sans as display or body (the generic trio and the
   CMS defaults in the sample).
5. Tracked caps for any run of text longer than 60 characters (Glenmere's caps paragraph).
6. A couple close-up as the lead photo (content `subject` must be `place`, `building`, `grounds`, `interior` or
   `detail`; `people` is allowed only for secondary photos).
7. Award badges, review stars, press logos or association seals above the fold; press wordmarks only in a dedicated
   row below the story, grey, ≤ 24 px tall, and only from the content file.
8. Any slider in the hero; any carousel of equal cards; any "Learn more" card row of three.
9. Flat scrims (a solid overlay over a photo) darker than 35% or lighter than 20% white; gradients only.
10. Popups, newsletter modals, notification prompts, age gates, chat widgets, promo bars.
11. Wave or curved section dividers, parchment / paper textures, drop shadows larger than the existing 34 px / -22 px
    rule, gradients as backgrounds (other than scrims and the botanical wash at ≤ 8%).
12. YouTube/Vimeo iframes in the content column; any autoplay video without a composed poster frame and a
    reduced-motion fallback.
13. More than one ornament device per site; more than three instances of it.
14. Two-row navigation with more than 8 links; dropdown menus; mega-menus.
15. The words "luxury", "luxurious", "stunning", "unforgettable", "dream", "magical", "elegance & grandeur" in
    headlines or kickers (QA greps h1/h2/.kicker).
16. Body text under 16.5 px; line length over 72 characters; headline over 14 words.
17. `density ≥ 85` with `voice ≥ 85` (the spec-sheet SaaS corner) outside `modern-luxe`, and inside it only with
    section padding ≥ 160 px and inset photos.
18. More than six sections before the tour section.
19. Hero without any fact (guests / acres / year / spaces) within the first screen.
20. Any colour pair under 7:1 for small text (existing rule) and any photo-background text without a measured pass.

## 6. Fingerprints and the diversity guard

### 6.1 Fingerprint of each existing variant and each dialect

Existing dimensions: display family, display class, body family, accent hue, paper temperature, hero id and family,
spaces, story, faq, tour, section order, moment, button style, radius bucket, lead photo. New dimensions (added to
`lib/fingerprint.py`): `dialect`, `paper_tone` (light / mid / tinted / dark-warm / dark-cool), `hero_framing`
(inset / bleed / type / silent / split / crest), `display_case` (sentence / caps / mixed), `ornament`, `body_px`
bucket (17 / 19 / 21), `photo_edge` (flush / keyline / arch / rounded), `motion_device`, `nav_style`.

| Site / dialect | dialect | paper tone | display (class, case) | body px | hero (framing) | ornament | spaces / story | moment | motion |
|---|---|---|---|---|---|---|---|---|---|
| Stonehurst variant A | *(pre-dialect; nearest: editorial)* | light cool | Newsreader (transitional, mixed) | 17 | masthead (type) | none | index / pullquote | guest-journey | fade |
| Stonehurst variant B | *(nearest: botanical / ranch)* | tinted warm | Fraunces (soft-serif, sentence) | 17 | frame (inset) | none (rounded photos) | stack / timeline | light-shift | slide |
| Stonehurst variant C | *(outside the band; nearest: modern-luxe without the padding rule)* | light neutral | Instrument Sans (grotesk, sentence) | 16.5 | cover-type (type) | none | spec-sheet / ledger | seat-picker | none |
| estate | estate | light-warm / mid-warm | Cormorant / Libre Caslon / Cinzel (garalde, caps or mixed) | 17-19 | crest-centred / cinematic / frame | crest-roundel / double-rule / keyline-frame | stack or index / split, timeline, pullquote | timeline, crest-reveal, hours-dial | fade + crest draw |
| editorial | editorial | light / blush | Bodoni Moda / Gloock+Newsreader / Literata (didone or transitional, sentence) | 17-19 | frame / inset-caption / masthead | drop-cap / italic-lead-in / vertical-label | index or pairs / pullquote | guest-journey, pairs-counter, light-shift | fade-up + cross-fade |
| candlelit | candlelit | dark-warm / dark-cool | Marcellus / Cormorant SC / Forum (inscriptional, caps) | 17 | panel / cinematic / silent | double-line-frame / botanical-engraving / brass-rule | stack or index / split | light-shift (night), candle-count, hours-dial | fade + frame draw |
| modern-luxe | modern-luxe | light-grey warm / cool | Instrument Serif / Manrope+Instrument Serif / Hanken (transitional or grotesk, caps labels) | 17-19 | cover-type / inset-wide / landscape-silent / slideshow | hairline-grid / counter / arrow-glyph | spec-sheet or strip / ledger | seat-picker, slideshow-counter, numbers-count | none or fade + cross-fade |
| coastal | coastal | light cool / sand | Newsreader / Josefin+Cormorant / Spectral (transitional, sentence or caps) | 17-19 | frame / inset-caption / masthead / slideshow | small-caps-kicker / inset-margin / compass-rose | stack or index / pullquote, split | light-shift, slideshow-counter, season-toggle | fade + scale-in |
| botanical | botanical | light green-cream | EB Garamond / Fraunces soft / Cardo (garalde or soft-serif, sentence) | 17-19 | frame (arch) / cinematic / arch-split | botanical-line / leaf-rule / watercolour-wash | stack / timeline, pullquote | light-shift, season-toggle, guest-journey, sprig-draw | fade-up + sprig draw |
| ranch | ranch | tinted oatmeal | Fraunces / Lora / Bricolage (soft-serif, garalde or grotesk, sentence) | 17-21 | cinematic / frame / landscape-silent | olive-band / rope-rule / wood-keyline / brand-mark | stack on deep / timeline, split | light-shift (golden), guest-journey, constellation | slide + band fade |
| deco | deco | ivory / charcoal | Bodoni Moda caps / Big Shoulders / Italiana (didone or condensed, caps) | 17 | masthead / cover-type / pair-split | underline-bar / stepped-frame / sunburst / geometric-rule | index / pullquote | numbers-count, window-reveal, then-now | fade + bar slide |

Reading the first three rows against the table: A and C were legal outputs of a system with no band; under the
dialect layer A can only exist as `editorial`/`coastal` with its dateline replaced by facts and its paper tinted, and
C cannot exist at all except as the restyled `modern-luxe` spec sheet with 160 px padding and 17 px body.

### 6.2 Extending the guard so same-dialect sites still register as different

Problem: with eight dialects and many venues, most pairs of sites will share a dialect, and the current weights
(display family 0.16, hero 0.14, accent hue 0.12…) let two same-dialect sites that share a pairing and a hero fall
under the 0.35 refuse line even when paper, ornament, body size and framing differ. Proposal:

1. **Add the new dimensions with these weights** (categorical 0/1 unless stated): `paper_tone` 0.06, `hero_framing`
   0.06, `display_case` 0.04, `ornament` 0.06, `body_px` 0.03, `photo_edge` 0.03, `motion_device` 0.03, `nav_style`
   0.03. Re-normalise the existing weights so the total stays 1.0 (scale existing by 0.66). `dialect` itself is *not*
   a distance dimension (sharing a dialect is expected) but is used for the quota rule below.
2. **Same-dialect scaling.** When two sites share a dialect, compute the distance over the non-dialect dimensions and
   require ≥ 0.45 (warn) / ≥ 0.32 (refuse) instead of 0.50 / 0.35, *and* additionally require that at least four of the
   following seven differ: pairing, hero framing, ornament, paper tone, spaces archetype, moment, body size. The
   second test catches the case the weighted sum misses (same pairing + hero + moment with small differences elsewhere).
3. **Dialect quota.** Refuse the third registered site that shares `dialect` + `pairing` + `hero_framing`; warn on the
   second. This is the rule that would have prevented the two hand-built mocks reading alike (both warm cream,
   serif-on-cream, hero-then-story) even though the current metric scored them 0.859 apart.
4. **Screenshot pHash as a second signal.** `qa.py` already screenshots the fold at 1440 and 390; add a 16 x 16
   DCT pHash of the 1440 fold (greyscale) and of a 1440 x 2400 "rhythm strip" (the full page downscaled to 64 x 256,
   which encodes section order and photo/paper alternation). Store both in the registry. Warn when the Hamming
   distance to any registered site is ≤ 18 of 256 on either hash, refuse at ≤ 12, and report which site. Thresholds are
   a starting point; re-tune after ten sites (the design doc already plans this). Implementation: Pillow + numpy DCT,
   no new dependency.
5. **Report the drivers** exactly as today (`build-meta.json` lists the dimensions that contributed to the closest
   distance) so a human can disagree, and add a `--allow-close` reason field that gets stored with the registration.

## 7. Implementation inventory for phase 2 (what is new, roughly in build order)

| Item | Kind | Est. | Notes |
|---|---|---|---|
| `data/dialects.json` | data | 1 h | eight dialect records: axis clamps, paper ranges, accent rules, allowed pairings / heroes / spaces / story / faq / tour / moments / ornaments / voices, rhythm variants, motion device |
| `lib/palette.py` photo signals + dark token set | code | 2 h | mono / foliage / water / dark / earth shares; charcoal paper variant with the same 7:1 walker |
| dialect scorer + `--dialect` override + axis clamping in `lib/personality.py` | code | 1.5 h | writes the score table into `build-meta.json` |
| 14 new pairings in `pairings.json` | data | 1 h | import strings above; verify each family on fonts.googleapis.com at build time (existing practice) |
| Ornament partials (inline SVG/CSS): crest-roundel, double-rule, keyline-frame, drop-cap, italic-lead-in, vertical-label, double-line-frame, botanical-engraving ×3, brass-rule, hairline-grid, counter, small-caps-kicker, compass-rose, botanical-line ×6, leaf-rule, watercolour-wash, rounded-arch, olive-band, rope-rule, wood-keyline, brand-mark, underline-bar, stepped-frame, sunburst, geometric-rule | templates | 4-5 h | each ≤ 40 lines; all `aria-hidden`; all stroke colours from tokens |
| Heroes: port `cinematic`, build `crest-centred`, `inset-caption`, `panel`, `silent`, `inset-wide`, `landscape-silent`, `arch-split`, `pair-split`, `slideshow` | templates | 5-6 h | `needs` for each (lead width, subject, photo count) |
| Sections: `statement`, `pairs` gallery, `strip` spaces, olive-band variant of `stack`, two rhythm variants per dialect | templates | 3 h | |
| Moments: `slideshow-counter`, `crest-reveal`/`sprig-draw` (one SVG draw-in module), `numbers-count`, `then-now`, `hours-dial` | templates + JS | 4 h | all with QA hooks and reduced-motion branches |
| Voices: `heritage`, `evening`, `lyric` + three CTA sets per voice | data | 1 h | facts only from content slots |
| Fingerprint: new dimensions, same-dialect rule, quota, pHash | code | 3 h | registry schema bump; re-register the five existing sites |
| QA additions: exclusions 1-19 as greps/measures; pHash capture | code | 2 h | |
| Content schema: `subject` per photo, `mono`, `flora`, `vibe` block, `archival` | schema | 0.5 h | |
| Proof: rebuild Stonehurst as `botanical` and `estate`, plus one dark venue (needs a candlelit content file) | build | 2-3 h | register all three; run the matrix |

Roughly 30-35 hours of template and data work, most of it the SVG ornaments and heroes. Nothing requires a new
runtime dependency.
