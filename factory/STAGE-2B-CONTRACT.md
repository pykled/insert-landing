# Stage 2B contract: templates for the luxury dialects

Written by stage 2A (2026-10-20). Stage 2B owns `factory/templates/**` and nothing else; stage 2A owns the code and
data (`build.py`, `qa.py`, `lib/`, `data/`, `tests/`). Everything below is what the builder already passes in and what
QA already checks. Spec: `docs/research/05-luxury-dialects-spec.md` (section numbers below refer to it).

How to see what is owed at any moment:

```
cd factory
python3 lib/templates.py --missing     # every id still planned-2B / deferred, with the dialects that use it
python3 lib/templates.py --refresh     # after adding templates: rewrite the statuses in data/dialects.json
python3 -m pytest -q tests             # test_statuses_match_filesystem fails until --refresh is run
```

A template "exists" when every file in its row below exists (`lib/templates.py` KIND_PATHS). Until it exists the
builder renders the nearest existing template (`data/dialects.json` `fallbacks`), records it in `build-meta.json`
`fallbacks[]`, and `qa.py` warns (`--strict`: fails). Nothing else is needed to switch a template on: drop the files in,
run `--refresh`, rebuild.

## 1. Files to create

### 1.1 Heroes (`templates/heroes/<id>.j2` + `templates/heroes/<id>.css.j2`, both required)

| id | dialects | framing | needs (builder checks) | layout (spec) | date form |
|---|---|---|---|---|---|
| `cinematic` (port from `previews/stonehurst/index.html`) | estate, candlelit, botanical, ranch | bleed | lead >= 2400 px | full-bleed photo, gradient scrim (<= 35% black; none on dark photos in candlelit), copy bottom-left, date card right | in hero (`partials/date-card.j2`) |
| `crest-centred` | estate | crest | lead >= 2400 px | full-bleed photo; crest + tracked-caps name + italic one-line subline centred; two square buttons (`copy.nav_cta`, `copy.guide_cta`) | below the photo (see 2.3) |
| `inset-caption` | editorial, coastal | inset | lead >= 1800 px | inset 16:9 photo with 48-80 px margins; headline in the display face bottom-left on paper below the photo, small-caps kicker above | below the photo |
| `panel` | candlelit | split | lead >= 1200 px | 50/50: photo + charcoal panel with the double-line frame, kicker, headline, two buttons | in the panel |
| `silent` | candlelit | silent | lead >= 2400 px and lead `subject` = building | full-height photo, nav bar at the foot of the hero, one outlined "Inquire" | below the photo |
| `inset-wide` | modern-luxe | inset | lead >= 1800 px | inset 2:1 photo under a two-row minimal header; headline on paper beneath at 40-56 px, no kicker | below the photo |
| `landscape-silent` | modern-luxe, ranch | silent | lead >= 2400 px, subject place/grounds/building | full-height photo, no text on it; headline arrives directly below | below the photo |
| `arch-split` | botanical | split | lead >= 1200 px | photo in an arch mask (`border-radius: 999px 999px 0 0`) left; copy + date check right on paper with the wash | in hero |
| `pair-split` | deco | split | 2 photos | headline band on ivory, then a b/w (`mono: true` photo) + colour pair at 4:5, date check inline | in hero |
| `slideshow` | coastal, modern-luxe | bleed | lead >= 2400 px, 3 photos | three equal landscape photos, cross-fade, "1 — 3" counter, **user-advanced only** (`data-autoplay="off"`), static under reduced motion | below the photo |

### 1.2 Sections (`templates/sections/<file>.j2`; a `.css.j2` next to it is included automatically when present)

| file | kind / id | dialects | content |
|---|---|---|---|
| `sections/story-split.j2` (port from the mock) | story `split` | estate, candlelit, coastal, ranch | photo + story copy side by side; candlelit places `botanical-engraving` behind the copy |
| `sections/spaces-strip.j2` | spaces `strip` | modern-luxe | horizontal strip of spaces with hairlines and 4:5 photos (not a scrolling carousel: E8 fails `overflow-x` rows of equal cards) |
| `sections/spaces-stack-olive.j2` | spaces `stack-olive` | ranch | `stack` on the deep olive band (`--deep`), ochre small-caps kickers (`--on-deep-accent`) |
| `sections/gallery-pairs.j2` | gallery `pairs` | editorial | photo pairs 3:2 with a 24-40 px gap and captions; placed by the builder right after the spaces section |
| `sections/statement.j2` | section `statement` | editorial, modern-luxe, coastal, botanical | one serif sentence 28-34 px right after the hero (`copy.hero_lede` or `v.story.lead`); carries the drop cap / sprig / wash when that is the site's ornament |
| `sections/facts-strip.j2` | section `facts-strip` | estate, editorial, candlelit, ranch, deco | year, acres, guests, spaces from `v.tagline_facts` / `v.vibe.era` / `v.numbers` only; omit any null; each value wrapped in `data-fact` (2.4). Fallback today: `sections/glance.j2` |
| `sections/daylight-band.j2` | section `daylight-band` | candlelit | the one light band on a dark page, with a `light: day` photo; uses the light tokens through a local class (do not redefine `--paper` globally) |
| `partials/nav-two-row.j2` | nav `two-row` | modern-luxe, deco | two-row header with sub-nav; <= 8 links total, no dropdowns (E14). Fallback today: `nav-bar.j2` |

Every section renders as `<section id="<id>" ...>` and is a direct child of `<main>` (QA counts `main > section` for
E18 and finds `#tour`, `#story`, `#featured`). Ids: `statement`, `facts-strip`, `daylight-band`, `gallery`, and the
role ids `spaces`, `story`, `tour`, `guide`, `faq` as today.

### 1.3 Moments (`templates/moments/<id>.j2`, optional `<id>.css.j2` and `<id>.js.j2`)

Root element: `<section id="<id>" data-moment-root ...>`. `base.html.j2` already sets `<body data-moment="{{ ch.moment }}">`
and includes `moments/<id>.js.j2` if present. QA drives each moment through a `window.__*` hook and measures contrast in
the resulting state; these hooks are already in `qa.py`:

| id | dialects | needs | QA hook (must exist) | QA asserts |
|---|---|---|---|---|
| `slideshow-counter` | modern-luxe, coastal | 3 photos | `window.__slideTo(i)` (0-based) | `[data-counter]` text contains `02` after `__slideTo(1)` |
| `crest-reveal` | estate | — | none | an element `[data-motion-device="draw-in"]` exists (the crest rings) |
| `sprig-draw` | botanical | a photo with `flora` | none | an element `[data-motion-device="draw-in"]` exists (the sprig) |
| `numbers-count` | modern-luxe, ranch, deco | 3 `v.numbers` | `window.__countFinish()` | every `[data-count-to]` ends with text equal to its attribute (values from `v.numbers[].value` only) |
| `candle-count` | candlelit | 3 `v.numbers` | `window.__countFinish()` | as numbers-count (brass numerals, `--metal`) |
| `then-now` | deco | a photo with `archival: true` + `rights` | `window.__thenNow(pct)` | root `data-split` equals the pct |
| `pairs-counter` | editorial | 4 photos | `window.__pairsTo(i)` | `[data-counter]` text contains `2` after `__pairsTo(1)` |
| `hours-dial` | estate, candlelit, coastal | `v.day` | `window.__dialSet(hour)` | root `data-dial-hour` equals the hour; arc from `v.day.gates_open` to `v.day.event_end` |

`crest-reveal` and `sprig-draw` share one draw-in module: put it in `templates/partials/draw-in.js.j2` and include it
from both `.js.j2` files. Deferred (named in the spec, not owed by 2B; the builder falls back): `season-toggle`,
`window-reveal`, `grounds-constellation`.

The builder places a moment section with id = the moment id (legacy moments keep `journey`, `day`, `fit`) and nav
label "A day here" unless 2B asks for a mapping in `build.py` `MOMENT_NAV` (tell stage 2A / 3).

### 1.4 Ornaments (`templates/ornaments/<id>.j2` + `templates/ornaments/<id>.css.j2`, both required)

One device per site, at most three placed instances (spec section 1, E13). Every SVG is inline, `aria-hidden="true"`,
<= 40 lines, stroke/fill colours from tokens only (`var(--metal, var(--accent))` for brass, `var(--line)`,
`var(--accent-text)`, `var(--ink)`), never a hex.

The `.j2` is included with a variable `slot` telling it where it is rendered: `header`, `hero`, `section-head`,
`story`, `tour`, `footer`. It renders nothing for slots it does not use. `base.html.j2` (2B edits it) includes
`ornaments/<ornament>.css.j2` once in `<style>` and the `.j2` at the slots, when `ornament != 'none'`.

Scope decides how QA counts it (E13):
- **placed**: each instance root carries `data-ornament="<id>"`; at most 3 per page.
- **page**: a CSS treatment applied across the page; declare it once as `<body data-ornament="<id>">` and do not mark
  individual elements (body counts as the one device, not as an instance).

| id | dialect | scope | what (spec section 2) |
|---|---|---|---|
| `crest-roundel` | estate | placed | 56 px circle, 1 px brass stroke, initials (`v.short_name`) in the display face at 22 px, optional inner ring at 44 px; header centre, hero, footer |
| `double-rule` | estate | placed | two 1 px `--line` rules 6 px apart under centred headings, 64 px wide |
| `keyline-frame` | estate | page | photos get `outline: 1px solid var(--line); outline-offset: -8px`, 0 radius |
| `small-caps-kicker` | estate, coastal | page | kickers in `font-variant: small-caps; letter-spacing: .14em` in `--accent-text`; coastal adds a 48 px hairline above |
| `drop-cap` | editorial | placed | story/statement first letter, display face, 3 lines, accent (`initial-letter: 3` with float fallback) |
| `italic-lead-in` | editorial | placed | `<em>` lowercase italic word + `<span class="caps">` +0.18 em before tracked caps |
| `vertical-label` | editorial | placed | section name rotated -90° in small caps at the left margin (<= 3 sections) |
| `double-line-frame` | candlelit | placed | SVG rect pair, outer 1 px brass inset 12 px, inner 1 px inset 20 px, square corners; hero copy panel + tour card. Its strokes draw in once (`data-motion-device="draw-in"`, 1400 ms) |
| `botanical-engraving` | candlelit | placed | one 320 x 320 line drawing (laurel / olive / ivy; three generic files, never a photo trace), 1 px brass, opacity .35, behind the story copy |
| `brass-rule` | candlelit | placed | 1 px brass rule with a 6 px diamond at centre |
| `hairline-grid` | modern-luxe | page | 1 px rules between rows/columns of the facts strip and spaces list |
| `counter` | modern-luxe, coastal | placed | slide or section counter "01 — 04" in tracked caps |
| `compass-rose` | coastal | placed | 40 px eight-point star, footer only |
| `botanical-line` | botanical | placed | leaf sprig / branch, 1 px ink stroke, 120-240 px; six files chosen by the first photo `flora` tag: `ornaments/sprigs/{olive,fig,fern,lavender,oak,eucalyptus}.svg.j2` |
| `leaf-rule` | botanical | placed | 1 px rule with a 12 px leaf glyph at centre |
| `watercolour-wash` | botanical | page | `radial-gradient` of `--accent-tint` at <= 8% alpha behind the statement paragraph (QA E11 allows exactly this) |
| `rounded-arch` | botanical | page | the frame/arch-split hero photo gets `border-radius: 999px 999px 0 0` |
| `olive-band` | ranch | page | spaces or tour section on the deep olive band with ochre small-caps kickers |
| `rope-rule` | ranch | placed | `border-top: 1px dashed` with 8 px dashes in accent |
| `wood-keyline` | ranch | page | photos get a 1 px warm-brown keyline inset 6 px |
| `brand-mark` | ranch | placed | 48 px circle + initials, 2 px stroke, cattle-brand style |
| `underline-bar` | deco | placed | `linear-gradient(transparent 62%, var(--accent) 62%, var(--accent) 88%, transparent 88%)` on an inline span behind the name; slides in once (`scaleX` 0→1, 600 ms, `data-motion-device="bar-slide"`). The element carries `data-ornament` so E11 does not read it as a background gradient |
| `stepped-frame` | deco | placed | SVG frame with three 6 px steps per corner in brass around the tour card |
| `sunburst` | deco | placed | 64 px, 12 brass radiating lines, footer only |
| `geometric-rule` | deco | placed | 100% wide, 8 px tall row of 6 px chevrons (inline-SVG `background-image`, 1 px brass) under the facts strip |

Deferred (named in the spec, builder falls back to no ornament): `hairline-rule`, `monogram-seal`, `arrow-glyph`,
`inset-margin`.

## 2. What every template receives (Jinja context, `build.py` step 9)

Existing (unchanged): `v` (content file), `t` (tokens), `pair` (pairing record), `ch` (rendered ids per dimension:
`pairing hero spaces story faq tour gallery moment voice ornament`), `copy` (voice strings, already filled from
content), `photos` (per name: `src srcset width height alt focal caption native variants`), `lead`, `sections`, `p`
(clamped axes), `css_vars`, `nav_style`, `guide_layout`, `guide_photo`, `hero_sizes`, `spaces_by_id`, `story_second`,
`light_photos`, `uses_band`, `looks_sentence`, `seo`, `jsonld`, `build`.

New in stage 2A:
- `photos[n]` adds `subject`, `mono` (bool), `flora`, `archival` (bool).
- `ornament`: the ornament id to render, or `'none'`.
- `palette_mode`: `'light'` or `'dark'`.
- `dialect`: `None` for pre-dialect builds (`--dialect none`: the three Stonehurst proof variants; render exactly as
  today), else a dict: `id label ornament tone paper_mode rhythm display_case photo_edge body_px kicker_style
  hero_framing light_shift_default motion photo fallbacks`. `dialect.motion` = `{reveal, reveal_ms, offset_px, device,
  device_target, device_ms, ...}`; `dialect.photo` = the dialect's photo rules (edges, ratios, grain, mono, ...).
- `t` adds, for dialect builds: `reveal` (`none` | `fade` | `fade-up` | `slide`), `reveal_ms`, `reveal_offset_px`,
  `ease` (`cubic-bezier(.2,.7,.2,1)`), `motion_device` (`draw-in` | `cross-fade` | `scale-in` | `band-fade` | `bar-slide`),
  `motion_device_ms`, `kicker_style` (adds `small-caps`), `photo_edge` (`flush` | `keyline` | `arch` | `rounded`),
  `body_px` (17/19/21; `pair.body.size_px` is already set to it), `display_case` (`sentence` | `caps` | `mixed`),
  `paper_mode`, `paper_tone`; and the dialect's token overrides (`radius`, `section_pad_*`, `container`, `gutter`).
  `t.image_edge` stays the legacy three-value token (`arch` maps to `flush` there).
- `pair` may carry `secondary` (a second display face for sentence-case headings when the primary is caps-only or
  wordmark-only: estate-cinzel, editorial-gloock, candlelit-cormorant-sc, luxe-tracked-sans, coastal-engraved) and
  `display.case`, `display.caps_only`, `display.wordmark_only`, `display.max_px`, `display.max_words_per_line`. The
  `import` string already loads the secondary family.

New CSS variables (in `css_vars`, dialect builds): `--metal` (brass; light dialects with a metallic: graphics only, 3:1;
dark set: text-safe, 7:1); dark set only: `--on-accent` (label colour on accent fills), `--field` (form-field ground).
Use fallbacks so light builds keep working: `var(--on-accent, #fff)`, `var(--field, #fff)`, `var(--metal, var(--accent))`.

## 3. Base template / CSS changes 2B must make (these are why dialect builds fail QA today)

Measured on dialect builds of Stonehurst with the current templates (`.factory-check/dialects/*`, `qa.py`):
1. **Dark palette**: `base.css.j2` hard-codes `#fff` (form fields, button labels, `--on-deep`). On charcoal this gives
   1.2-2.6:1 contrast (32 of the 40 problems on the candlelit build). Use `--field`, `--on-accent`, `--on-deep` from
   the tokens.
2. **Display minimums and hairlines**: headings must never render below `pair.display.min_px` at any viewport (Cardo
   40 px and Libre Caslon Display 36 px rendered at 28-36 px on mobile h2s). Clamp with
   `max({{ pair.display.min_px }}px, ...)` or use the body/secondary face below it. The 1x/2x hairline probe also
   fails the mobile h1 for Libre Caslon Display 400 @ 40 px (35% of the letterform <= 1 css px) and Cardo 400 @ 40 px
   (29%): render those faces at >= 48 px on mobile or set the mobile h1 in the secondary/body face. If they still fail
   at sizes the layout can hold, report it to stage 3: the pairing should be dropped, not the probe loosened.
3. **Facts in the first screen** (E19): current heroes pass through their copy; new heroes must keep at least two
   content facts inside the first 900 px (desktop) and mark them (4.1).
4. **Body measure** (E16): running text <= 72 characters per line; body copy >= 16.5 px (date-card sub copy at
   14.5 px and the glance/day notes at 15 px fail; fine print may use `.fine` / `small` / `figcaption`, which QA
   excludes).
5. **Reveal**: implement `t.reveal` = `fade-up` (translateY `t.reveal_offset_px`) and use `t.reveal_ms` / `t.ease`;
   QA requires the `.reveal` transition to be 600-1200 ms when motion is on.
6. **Kicker** `small-caps` branch; **photo edge** `arch` / `rounded` from `t.photo_edge`; **mono** photos
   (`photos[n].mono`, never the lead) get `filter: grayscale(1) contrast(1.05)` in deco only.
7. `base.html.j2`: add `data-dialect`, `data-ornament`, `data-motion`, `data-paper` on `<body>` (2.4) and include the
   ornament css/partials.

## 4. QA hooks (what `qa.py` and `lib/exclusions.py` look for)

### 4.1 Attributes

| Hook | Where | Rule |
|---|---|---|
| `<body data-dialect="{{ dialect.id }}" data-ornament="{{ ornament }}" data-motion="{{ t.motion_device }}" data-paper="{{ palette_mode }}" data-moment="..." data-hero="...">` | body | `data-ornament` on body is always the site's ornament id (or `none`); for page-scope ornaments it is the only marker |
| `data-ornament="<id>"` | each placed ornament root | one distinct id per page; <= 3 placed instances; must match `ch.ornament` (E13 fails if the build chose an ornament and the page has no marker) |
| `class="hero hero-<id>" data-hero="<id>" data-hero-framing="{{ dialect.hero_framing }}"` | hero `<section>` | exactly one `.hero`; one `h1` on the page; the hero image has `fetchpriority="high"` |
| `data-fact="guests\|acres\|year\|spaces\|distance"` | the element holding each fact number | E19 counts marked facts inside the first 900 px; text must come from `v` (never typed into the template) |
| `data-autoplay="off"` | slideshow root | any other value fails E8 (hero sliders) and the reduced-motion check |
| `data-motion-device="<device>"` | every element the motion device animates | under `prefers-reduced-motion: reduce` it must not animate (QA: `document.getAnimations()` running = 0 after 700 ms) and must show its final state; with motion on, device animations last 600-1600 ms (warn outside) |
| `data-moment-root`, `data-counter`, `data-count-to`, `data-split`, `data-dial-hour` | moments | see 1.3 |
| `data-reduced-motion` | any `<video autoplay>` (with a `poster`) | required by E12 |
| `data-press` or `id="featured"` | press row | below the story, below the fold, text names from `v.featured_in`, logos (if ever) <= 24 px tall (E7) |

### 4.2 Things QA fails on (dialect builds; full list in `lib/exclusions.py`)

E1 pure-white paper, saturated fills C > 0.14 outside deco · E2 any weight <= 200, display <= 300 on a photo, unpinned
weight/opsz · E3/E4 script, typewriter, Playfair, Montserrat, Raleway, Poppins, Arial, Open Sans as the first family ·
E5 tracked caps over 60 characters · E6 people as the lead · E7 badges/stars/press above the fold · E8 slider classes
(`swiper slick splide glide flickity carousel slider owl-`) in the hero, auto-advance, equal-card `overflow-x` rows,
three "Learn more" cards · E9 flat scrims; gradient scrims over 35% black / 20% white · E10 dialogs, fixed overlays,
names matching `popup modal newsletter subscribe chat intercom drift crisp tawk promo-bar announcement-bar age-gate
cookie` · E11 wave/curve dividers (class names `wave curve shape-divider divider-svg`), `clip-path` on sections, blur >
34 px shadows, paper/parchment/noise textures (editorial grain only at <= 6% opacity), background gradients (except
scrims over images, `[data-ornament]` elements, and the botanical radial wash <= 8%) · E12 YouTube/Vimeo iframes,
autoplay video without poster / `data-reduced-motion` · E13 ornament rules · E14 > 8 header links, dropdowns
(`details`, `aria-haspopup`, `dropdown`, `mega`, `submenu`) · E15 "luxury, luxurious, stunning, unforgettable,
dream, magical, elegance & grandeur" in h1/h2/.kicker · E16 body < 16.5 px, > 72 characters per line, headline > 14
words · E17 density/voice corner · E18 > 6 sections before `#tour` · E19 no fact in the first screen. Plus the
existing gate: 7:1 small-text contrast under every glyph, the legibility stroke probe, overflow, images, flows.

### 4.3 Flows QA clicks (must keep working in every hero/section)

`#date-form` (with `#f-date`, `#f-guests`, `#f-contact`, `#date-error`, `#date-confirm`, `#date-again`) inside `#check`;
`#tour-open` (optional) → `#scheduler`, `#cal`, `#cal-next`, `#slots`, `#book`, `#tour-confirm`, `#tour-again`;
`#guide-wrap` with `#guide-form`, `#g-email`, `#guide-error`, `#guide-confirm`; `.nav-toggle` on mobile; `header`,
`main`, `footer`. Heroes with no form in the hero (crest-centred, inset-caption, silent, inset-wide, landscape-silent,
slideshow) include `partials/date-inline.j2` in a band directly under the photo, still inside the hero section, so
there is exactly one `#date-form` per page.

## 5. Done for 2B means

1. The files in section 1 exist; `python3 lib/templates.py --refresh` run; `python3 -m pytest -q tests` passes.
2. For each dialect, `python3 build.py content/stonehurst.json --variant x-<dialect> --out ../.factory-check/dialects/<dialect> --dialect <dialect> --lead <photo>`
   builds with no `FALLBACK` lines except deferred ids, and `python3 qa.py ../.factory-check/dialects/<dialect> --strict`
   exits 0 (QA needs `python3 -m http.server 4821` in `~/projects/insert`).
3. `FACTORY_OUT=../.factory-check/stonehurst-variants ./build-all.sh` still produces the three proof variants byte-for-byte
   (apart from the generator hash) and `qa.py` passes them: pre-dialect builds have `dialect = None` and must render
   exactly as before.
