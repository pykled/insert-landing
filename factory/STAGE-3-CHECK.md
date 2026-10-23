# Stage 3 check (Checker: Claude Sonnet 5.5, 2026-10-23)

Worktree `/tmp/factory-check` @ c90c636 (main tree untouched). Scratch: `/tmp/factory-check/.fc/` (own.py, own2.py, tiles.py, logs, shots).
Server: `python3 -m http.server 4931 --directory /tmp/factory-check`. All builds used `--offline-fonts` and a COPY of data/registry.json (`--registry`).

## Task 1: reproduction

| check | Maker claim | Actual |
|---|---|---|
| `python3 -m pytest -q factory/tests` | 56 passed | **56 passed** (22.7 s) |
| a/b/c rebuilt via build-all.sh vs committed `previews/stonehurst-variants/{a,b,c}` | byte-identical bar generator hash | **identical** x3 (generator `<meta>` stripped) |
| 4 proof builds (commands from 2C notes) | built, guard OK | built, guard OK. Rebuilding into a copy of the registry reports nearest = another proof (0.635-0.682), as expected |
| `qa.py --strict` botanical | PASS, 0 problems, 1 warning | **PASS 0 / 1 warning** (1891 KB) |
| estate | PASS 0, warnings: transfer, Libre Caslon 24%/19% | **PASS 0 / 4 warnings** (2713 KB, h1 24% mobile, h1 19% 1x, h2 16% 1x) |
| candlelit | PASS 0, transfer + Marcellus 19% | **PASS 0 / 3 warnings** (2482 KB, Marcellus 19% mobile, 12% 1x) |
| editorial | PASS 0, transfer + 20/25 lazy | **PASS 0 / 2 warnings** (3259 KB, 20 of 25 lazy) |

Repro notes (findings F9/F10): `qa.py` hardcodes `ROOT=~/projects/insert` (line 62), so `qa.py <dir>` from any other checkout builds a wrong URL and then crashes with a null `header` evaluate (no clear error). Workaround `--url`. qa.py also crashes (`Cannot read properties of null (reading 'style')`) when the page 404s instead of failing with a message.

## Task 2: independent QA (own Playwright, `.fc/own.py`, `.fc/own2.py`)

Method: contrast = text made transparent, full-page screenshot, per-text-node rect sampled at p5/p95 luminance of the true pixels behind it (images included), colour composited with computed alpha/opacity, WCAG ratio; large-text 3:1 else 4.5:1. 1x scale for sampling, reduced motion on so reveals settle. Everything else at DPR 2.

| site / width | text nodes | contrast <4.5 (<3 large) | lowest ratio seen | h-overflow | broken / alt-less imgs | blank imgs | img rendered@2x > 1.5x intrinsic |
|---|---|---|---|---|---|---|---|
| botanical 1440 | 210 | 0 | 7.63 | none | 0 / 0 | 1* | 6 |
| botanical 390 | 203 | 0 | - | none | 0 / 0 | 1* | 9 |
| estate 1440 | 185 | 0 | - | none | 0 / 0 | 0 | 9 |
| estate 390 | 182 | 0 | - | none | 0 / 0 | 0 | 8 |
| candlelit 1440 | 150 | 0 | 7.32 | none | 0 / 0 | 0 | 9 |
| candlelit 390 | 147 | 0 | - | none | 0 / 0 | 1* | 8 |
| editorial 1440 | 204 | 0 | - | none | 0 / 0 | 0 | 15 |
| editorial 390 | 201 | 0 | - | none | 0 / 0 | 0 | 15 |

*"blank" = element screenshot std-dev 0 for `img/stonepath-900.webp` (botanical) and `img/greenhouse-1200.webp` (candlelit mobile): lazy image not decoded at capture time. I could not reproduce a blank image in the stepped screenshots (they render), so this is an unconfirmed lazy-load capture artefact, not a finding.
Agreement with qa.py on contrast: full (0 failures both). Every text node I sampled is >= 7.3:1 (the 7:1 token design holds, including text over photos).

(b) Body-ish text under 16.5 px: independent list of distinct (class, size) under 16.5 px lives in `.fc/own/*-static.json` (15-21 classes per page). All are uppercase kickers/labels/chips/captions/fine print (10.5-13.5 px) or buttons at 13-13.5 px; the exceptions worth noting: candlelit FAQ answers render as small grey text (about 13-14 px, see screenshots), and estate/editorial photo captions at 13 px. No paragraph-length body copy under 16.5 px found except FAQ answers on candlelit (MINOR).
(c) Overflow: none at either width on any site (documentElement.scrollWidth == innerWidth, no unclipped element past the viewport).
(d) Images: no broken, no alt-less. 6 empty-alt (decorative) per dialect page, plausible. **Retina softness: 6-15 images per page are drawn at >1.5x (up to 2.0x) their intrinsic width at DPR 2** (e.g. barn-2400 full-bleed hero at 1440 = 2.00x; stonepath 457 css px from a 489 px file = 1.87x). The ladder is "never upscaled" so this is the source photo resolution (previews/stonehurst/img/real), not a bug, but the hero crops will look soft on retina. qa.py does not report it (MINOR/MAJOR: see F6).
(e) Heading stroke (coverage-weighted mean stroke width = 2*ink area/perimeter, text-vs-text-hidden diff, 1x vs 2x): no heading is hairline. Lowest: estate 390 h2 38 px = 1.52 css px at 2x / 1.77 at 1x (0.040-0.047 em); candlelit mobile Marcellus 2.2 px; editorial/botanical 2.6-5.3 px. 1x is 6-13% thinner than 2x for estate mobile only. Agrees with qa.py (warnings only, no fail).
(f) Focus + flows: Tab order reaches 35-54 focusables per page. Date form (empty error, valid submit -> confirmation), tour scheduler (open, next month, pick day+slot, book -> "You're on the calendar", reset) and pricing guide (bad email blocked, valid -> "Guide sent") work on all four sites at both widths; no page errors. **Disagreement with qa.py:** the pricing-guide confirmation says only "Guide sent. It's on its way to <email>" and contains no link; the guide is never actually delivered or linked (it is a front-end mock; flows are only a preview stub, acceptable for a concept preview but must be said). **Focus indicator on the guide email input is effectively invisible** (see F1): outline none, border transparent, box-shadow ring at alpha about 0.17 and 3 px; same glow on the white date inputs but their border goes to 0.7-alpha accent so they pass.
(g) `prefers-reduced-motion: reduce`: `document.getAnimations()` running = 0 and 0 `.reveal` elements under 0.9 opacity on all four sites at both widths. Agrees with qa.py.

## Task 3: LOOK (viewport-stepped screenshots, `.fc/shots/<site>-T1440-*.png`, `-T390-*.png`)

Note: Playwright `full_page` screenshots of these pages show empty bands because scroll reveals are not triggered; stepped viewport shots are right. This is a capture artefact, the pages are fine.

**botanical** (Fraunces/Karla, arch hero) - verdict **FIX FIRST**.
- Reads as a calm, premium garden venue. Arch crop, sprig ornament, cream paper and green pair well; the six rooms alternate cleanly; the property band and timeline are tasteful.
- Fixes: (1) The same sentence is printed twice: hero deck "A private estate of greenhouse, barn..." then immediately again as the intro statement (desktop and mobile). (2) Hero on 1440x900: the date-check card is cut by the fold and overlaps the arch caption area; first screen is dense vs the other three. (3) Big empty band under the property block on desktop (cream gap before "Ceremony under the fig"). (4) Guide band h2 breaks into 4 lines ("Know the / numbers / before the tour.") touching its paragraph on desktop. (5) Sprig ornaments are small and repeat 3x (hero, property, footer) at near-identical size.
**estate** (Libre Caslon, crest) - verdict **SHIP** (with 2 small fixes).
- The most convincing luxury wedding venue of the four: letterboxed barn photo, crest roundel, tracked caps name, serif display, hairline-ruled index of rooms, brown pricing band. Clearly different from the other three.
- Fixes: (1) hero photo is a thin letterbox of the barn, the first photo is a plain wide shot with sky; crop is ordinary. (2) mobile h1/h2 Libre Caslon thin (1.5 px stroke) - fine on retina, watch.
**candlelit** (Marcellus, dark warm) - verdict **SHIP** (condition F4).
- The strongest first impression: Greenhouse-at-night hero with double-line frame, gold accents, 9/6/1/1907 numbers band, evening copy. Genuinely evokes a candlelit dinner and is the most distinctive of the set.
- Fixes: (1) copy claims "A garden for 200 at dinner." and "See the hall by appointment." / "The Hall": "hall" and "at dinner" are not facts about Stonehurst (F4). (2) FAQ answers are small grey text on dark. (3) "The hall" heading wraps to 6 lines inside the frame on desktop. (4) The calendar-less "See the hall by appointment" block repeats the same panel treatment as the guide band.
**editorial** (Literata, inset-caption) - verdict **REWORK**.
- Reads as a magazine / blog, not a luxury wedding venue: sans-less newspaper serif, drop-cap, "In pairs / Two views of Stonehurst, side by side" gallery, numbered FAQ two-column, caption-heavy layout. It is the least premium and the one that most resembles the earlier mocks' family (b).
- Fixes: (1) hero photo is huge and the name/h1 sit below the fold at 1440x900. (2) same sentence duplicated hero deck + drop-cap statement (mobile shows both stacked). (3) guide band: h2 "before the tour." touches paragraph, no breathing room. (4) tour block bullet icons lost; three plain columns underneath the calendar are orphaned text. (5) the long photo alt text used as caption ("The weathered wood barn seen from the entrance...") makes captions heavy.

Shared boilerplate (guide band, filming band, footer) is identical in structure across all four. In the stepped shots the last 2.5 screens of every page are the same: guide band, FAQ, filming band, footer, only recoloured/re-fonted. Of the three flagged regions the filming band ("6 distinct looks on one property ...") hurts most because its wording and size are the same everywhere; a venue owner comparing two sites would notice. MAJOR for the set, MINOR per site (F5).

Distinctness: estate vs candlelit vs botanical vs editorial are clearly different families; botanical vs earlier mock b and editorial vs variant b are the closest pairs (0.52 and 0.73).
