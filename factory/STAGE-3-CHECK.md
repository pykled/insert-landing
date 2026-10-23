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

(b) Body-ish text under 16.5 px: independent list of distinct (class, size) under 16.5 px lives in `.fc/own/*-static.json` (15-21 classes per page). All are uppercase kickers/labels/chips/captions/fine print (10.5-13.5 px) or buttons at 13-13.5 px; captions at 13 px. A DOM pass (`.fc/spec.py`) found no paragraph-length body copy under 16.5 px on the four proofs except the botanical timeline event text (16 px, spans, so qa.py's `p`-only E16 never sees it; MINOR). (An earlier draft note about small candlelit FAQ answers was a half-scale screenshot impression and is withdrawn: measured >= 16.5 px.)
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
- Fixes: (1) copy claims "A garden for 200 at dinner." and "See the hall by appointment." / "The Hall": "hall" and "at dinner" are not facts about Stonehurst (F4). (2) (withdrawn: FAQ size is fine). (3) "The hall" heading wraps to 6 lines inside the frame on desktop. (4) The calendar-less "See the hall by appointment" block repeats the same panel treatment as the guide band.
**editorial** (Literata, inset-caption) - verdict **REWORK**.
- Reads as a magazine / blog, not a luxury wedding venue: sans-less newspaper serif, drop-cap, "In pairs / Two views of Stonehurst, side by side" gallery, numbered FAQ two-column, caption-heavy layout. It is the least premium and the one that most resembles the earlier mocks' family (b).
- Fixes: (1) hero photo is huge and the name/h1 sit below the fold at 1440x900. (2) same sentence duplicated hero deck + drop-cap statement (mobile shows both stacked). (3) guide band: h2 "before the tour." touches paragraph, no breathing room. (4) tour block bullet icons lost; three plain columns underneath the calendar are orphaned text. (5) the long photo alt text used as caption ("The weathered wood barn seen from the entrance...") makes captions heavy.

Shared boilerplate (guide band, filming band, footer) is identical in structure across all four. In the stepped shots the last 2.5 screens of every page are the same: guide band, FAQ, filming band, footer, only recoloured/re-fonted. Of the three flagged regions the filming band ("6 distinct looks on one property ...") hurts most because its wording and size are the same everywhere; a venue owner comparing two sites would notice. MAJOR for the set, MINOR per site (F5).

Distinctness: estate vs candlelit vs botanical vs editorial are clearly different families; botanical vs earlier mock b and editorial vs variant b are the closest pairs (0.52 and 0.73).

## Task 4: stress the factory (second venue, Lindley-Scott House)

Content: `/tmp/factory-check/factory/content/lindley-scott.json` (worktree only, not committed; schema.py: 0 errors 0 warnings). Every fact cites its page on https://lindleyscotthouse.com/: built 1911 for Charles Lindley, president of the Foothill Ranch; 1924 Mabelle Scott Anderson acquires it; since 1978; 4 acres; Carriage House built 2003 seats 200; garden holds 200 seated; one event per day; opens 11 AM for vendors; address 720 East Foothill Blvd, Azusa 91702; (626) 334-5215; Gmail address; four FAQs verbatim (/faq/); spaces The Residence, The Garden, The Carriage House (/about-us/, /weddings/, /receptions/). `featured_in` empty (none on site). Photos: 3 downloaded to `/tmp/lsh/real` (never committed or deployed): new-website-5-1 (residence, 1920 px), new-website-12-1 (Carriage House at night), new-wesbite-16 (reception interior). The site has no ceremony photo without guests, so only 3 were usable; the Garden space therefore reuses the residence photo. Vibe: estate / 1911 / heritage, grand, formal (my call, `era_source` cited).

| # | command (from factory/, plus `--offline-fonts --registry ../.fc/reg-ls.json`) | result |
|---|---|---|
| 1 | `build.py content/lindley-scott.json --variant ls --out ../.fc/ls/auto` (no --lead) | **CRASH** `KeyError: 'hero'` at build.py:289 `pal_paths = {n: paths[n] for n in pal_names}`. Default lead and palette photo are hard-coded `'hero'` (build.py:285); a venue with no photo called hero cannot build without `--lead`. |
| 2 | same + `--lead residence` | **CRASH** `TypeError: 'NoneType' object is not subscriptable` at build.py:78 (`v['day']['spaces_per_event'][:1]`). The venue states no spaces-per-event; schema.py accepts null. |
| 3 | `day.spaces_per_event=''` | clean stop (rc 3): `ERROR: copy slot guide_lede: no candidate can be filled ... {rental_hours}` . Venue states no rental hours. |
| 4 | content `copy_overrides.guide_lede` | **ignored**: schema.md documents `copy_overrides` in the content file but build.py never reads it (grep: zero hits); only `--copy key=value` works. Docs/code mismatch. |
| 5 | + `--copy "guide_lede=..."` (scorer, no override) | builds. Scorer: `estate 10, ranch 1, deco 1, botanical 1` -> estate. Guard **REFUSE** vs stonehurst-proof-estate at 0.561 (same dialect; only 3 of 7 key dims differ: pairing, hero_framing, ornament; needs 4). Correct per spec 6; built with `--allow-close "stage3 stress"`. |
| 6 | `--dialect estate` | identical to 5 (scorer already picked estate). |
| 7 | `--dialect botanical` | **CRASH** `jinja2.exceptions.UndefinedError: 'dict object' has no attribute 'flower'` at templates/moments/light-shift.j2:17; build.py:521 `light_photos` falls back to hard-coded `'flower'` when no day-ceremony / golden / night photos exist. The moment is chosen without checking the photos it needs. |
| 8 | `qa.py ../.fc/ls/auto --strict` | **FAIL, 6 problems**: E19 no fact in first screen (desktop + mobile); mobile h1 hairlines 51% (Cinzel 500 @ 28 px); mobile `residence-1200.webp` soft (needs 1504 px, source is 1920 px wide so the ladder stops at 1200); mobile contrast 1.08 on the uses-band h2; diversity refuse. 1 warning (6.92:1). |

What the LSH build shows (own screenshots + checks, `.fc/shots/.._ls_auto-T*.png`):
- **Mobile 390: horizontal scroll (scrollWidth 404 > 390) and 1.08:1 text.** The uses band h2 "Receptions and quinceañeras and film shoots." sets QUINCEAÑERAS in tracked caps wider than the column; the word and the "Email about a shoot or event" button run past the band onto the cream paper (white on cream). qa.py flagged only the contrast, not the overflow.
- Copy presets leak Stonehurst: heading "The house, the gardens and the long table." (Lindley has no long table), intro "Residence, garden and carriage house. ." (double full stop), stat label "1911 / ESTABLISHED" (the house was built in 1911; weddings since 1978), page title "... Garden Wedding Estate in Azusa", "3 distinct looks on one private property".
- 3 photos: the residence photo appears four times (hero, two spaces, story). Thin but not broken; a `single photo` build is below.
- Header name wraps to two lines at 390 and sits tight to the menu button.

### Hostile content (5 variants of the LSH file, all `--dialect estate --lead residence`, files `content/h-*.json`, outputs `.fc/h/*`)

| variant | build | result |
|---|---|---|
| longname (72-char name, `& " <b>` and accents, legal name with `<LLC>`) | rc 0 | HTML-escaped correctly (`&amp; &#34; &lt;b&gt;` in `<title>`, JSON-LD parses, `<\/b>` escaped); no overflow at 1440. 390: same scrollWidth 404 as above (long word issue, not the name). |
| single photo (one item, all spaces point to it) | rc 0 | builds, no broken images, no crash. Page repeats one photo ~8 times (expected). |
| nulls (acres, space_count, max_guests, events_per_day, capacities, numbers[] all null; era null) | rc 0 | **JS ReferenceError `None is not defined` x2** in inline scripts (Python `None` rendered into JS): the date form shows no confirmation and the tour calendar never populates (`#cal button:not([disabled])` timeout). `max="None"` on the guest input; JSON-LD description "A None-acre garden wedding...". |
| missing (no FAQ, timeline, paragraphs, press, phone, email, hours, day facts) | rc 0 | `<a href="mailto:None?subject=...">`, `<cite>None</cite>`, visible "Bring your planner if you have one. None." (null `day.requirement`, also present in longname/quotes builds). |
| quotes / ampersands / accents / `<script>alert(1)</script>` in name, blurb, FAQ | rc 0 | all HTML escaped; no executable injection; JSON-LD valid. FAQ and blurb escaped. No fabricated facts introduced beyond preset copy above. |

Tag balance (html.parser) clean; the only "stray" end tags are self-closing SVG children. No invented numbers beyond the preset copy listed in task 5.

## Task 5: spec audit (E1-E19, baseline) and fact trace

Evidence from `.fc/spec.py` (DOM pass at both widths on the four proofs) plus reading `lib/exclusions.py`:

| E | Rule | Proofs (measured) | Enforced by qa.py? |
|---|---|---|---|
| 1 | no white paper / saturated fill | paper rgb(251,250,246), (250,246,241), (26,21,16), (252,250,247); white only on cards/inputs; no C>0.14 fill | yes, checks body/html bg + fills; cards/inputs white is allowed |
| 2 | display 400-600, pinned, no <=300 | h weights 400/500/700; no text <=300 | yes (pairing meta + computed weights) |
| 3/4 | no script / generic faces | none loaded (Fraunces, Karla, Libre Caslon, Marcellus, Work Sans, Literata) | yes (font imports + computed families) |
| 5 | tracked caps run <= 60 chars | no tracked caps run >60 | **weak**: needs text-transform or uppercase source letters AND letter-spacing >= 0.05em; caps-only faces (Cinzel) and small-caps escape. LSH has a 157-char Cinzel caption that passes only because tracking is normal. |
| 6 | lead not people | all leads place/grounds | yes, but trusts the human `subject` tag |
| 7 | no press/badges above fold | press strip below story on all four, plain text | yes (first-screen badges, press top, order, logo height) |
| 8 | no hero slider / equal-card carousel / learn-more row | none in hero. **editorial has a "Next pair / 1-3" gallery pager** | **weak**: detects only horizontal scrollers of equal-width children and hero markup; the editorial pager passes. Spec ambiguity: arguably a carousel of equal cards (MINOR) |
| 9 | scrims gradient <= 35% | no overlays in proofs | yes, but only absolutely-positioned text-free overlays |
| 10 | no popups/chat/promo | none, no fixed non-header elements | yes |
| 11 | no waves/textures, shadow <= 34 | max blur 34 px | yes |
| 12 | no YouTube/Vimeo, autoplay needs poster | no iframes/video | yes |
| 13 | one ornament, <= 3 instances | botanical-line 3, crest-roundel 3, double-line-frame 3, drop-cap 3 (+ body marker) | yes |
| 14 | <= 8 links, no dropdowns | 8 links at 1440 (at the limit), 1 at 390 (menu), 0 dropdowns | yes |
| 15 | banned words in headings/kickers | none anywhere in visible text | **weak**: only h1/h2/kicker (spec text says headings; body copy unchecked) |
| 16 | body >= 16.5 px, line <= 72, headline <= 14 words | none over; **botanical timeline text is 16 px** | **weak**: only `<p>` in main, excludes dd/dt/spans; timeline spans never seen |
| 17 | density/voice corner | n/a (dialect clamps) | **vacuous in dialect builds**: reads personality only; dialect clamping makes it unreachable |
| 18 | <= 6 sections before tour | within limit (qa reports) | yes |
| 19 | fact in first screen | pass on proofs; **fails on LSH** | yes |
| 20 | 7:1 small text | my own pass: lowest 7.11-7.63:1 on proofs | yes, agrees |

Nothing is only claimed: every E has code. Weak/partial: E5, E8, E15, E16, E17.

### Fact trace (every visible string not found verbatim in the content file, 1440 px, `.fc/own/untraced.json`)
Numbers, names, FAQ answers, spaces, capacities, addresses, press names and quotes all trace to `stonehurst*.json` (featured-in row is in the content `facts` ledger, sourced to the live homepage). Text that does **not** trace:
1. Service promises written as the venue's own: "A reply in under a minute", "We'll text you in under a minute", "We've placed a courtesy hold for ... Held for 24 hours ... releases on its own", "text confirmation right away and a reminder the day before", "one-tap reschedule link", "Directions to the gate ... arrive with your confirmation", "One email, no drip sequence", "Check your inbox in the next minute, and the spam folder if it's shy". All four sites. The tour calendar offers fabricated slots ("Your tour is Monday, November 2 at 10:00 AM") and shades past days "unavailable".
2. candlelit only: **"A garden for 200 at dinner."** (content gives a 200 capacity, not at dinner); **"See the hall by appointment." / "The hall"** (Stonehurst has no hall); "Six rooms, lit for the night"; "By candlelight, by the numbers"; "1907 Barn's first recorded gathering" (content: barn hosted early Boy Scout meetings in 1907).
3. estate: "The house, the gardens and the long table." ("long table" appears nowhere in the content).
4. All filming bands: "6 distinct looks on one private property" (content: six spaces; "looks" is preset wording).
5. All pages: `<title>` "... Garden Wedding Estate in <locality> (Concept PROOF-<NAME>)" is a constant, including the internal variant name "PROOF-CANDLELIT" in a title a venue owner will see.
6. Journey-step phrases ("Dinner under glass") come from the content `journey_step` field, traced to the content file though not to a source URL.

candlelit vs stonehurst.json: top-level keys that differ: **vibe only**; within vibe: `words` (evening, candlelit vs lush, garden) and `_note`; `photos.items` content identical, key order differs (Greenhouse-at-night first). The tone is a build input. Claim confirmed.

## Task 6: diversity guard

Matrix (`python3 lib/fingerprint.py data/registry.json --matrix`) reproduces the Maker's numbers exactly, all 9 sites. Min 0.522 (proof-botanical vs stonehurst-b), max 0.846 (proof-botanical vs a); among proofs 0.635-0.788. pHash for every proof `ok`.

Trying to fool it (same venue, same dialect `estate`, registry = copy with proof-estate registered; none of these used --allow-close):

| attempt | distance to proof-estate | outcome |
|---|---|---|
| only `--lead hero --accent-hue 200` | 0.404 | **REFUSE** (same dialect 0.32/0.45 + 4 of 7 dims) |
| `--lead flower --accent-hue 30` | 0.442 | **REFUSE** |
| `--lead barn --personality warmth=10` | 0.372 | **REFUSE** |
| `--lead flower --force pairing=heritage-garalde --force ornament=double-rule --force nav=bar` | 0.293 | **REFUSE** |
| `--lead hero --force pairing=... --force hero=frame --force ornament=keyline-frame --force nav=bar` | 0.432 | **REFUSE** |
| a different venue (Lindley) in the same dialect | 0.561 | **REFUSE** (3 of 7 key dims differ; needs 4) |

The guard behaves as spec section 6 requires: same-dialect cosmetic variants refuse, and the refusal message says what to change. I could not fool it with colour, photo or tone changes. Note it is strict for second venues: a new venue that lands in an already-used dialect is refused until 4 of 7 key dimensions are forced apart or `--allow-close "<reason>"` is given.

## Task 7: findings

| # | Sev | Finding | Evidence / repro | Suggested fix |
|---|---|---|---|---|
| F1 | BLOCKER (factory) | build.py crashes on ordinary content: default lead `'hero'` hard-coded; null `day.spaces_per_event`; light-shift moment falls back to photo `'flower'` | `python3 build.py content/lindley-scott.json --variant x --out ../.fc/x --offline-fonts` -> `KeyError: 'hero'`; with `--lead residence` -> `TypeError ... build.py:78`; `--dialect botanical` -> `UndefinedError: ... 'flower'` | derive lead from photo tags (or first item); null-safe slots; select moments only if the photos they need exist; validate in schema.py |
| F2 | BLOCKER (factory) | Null values are rendered as Python `None`: inline JS `None is not defined` kills date + tour flows; `max="None"`, "A None-acre", `mailto:None`, `<cite>None</cite>`, "None." | build `h-nulls`/`h-missing` (see task 4); open page, fill date form: no confirmation | Jinja `tojson` for JS config; guard every optional with `{% if %}`; schema.md promises "omit the element" |
| F3 | BLOCKER (factory) | Long tracked-caps word overflows the uses band on phones: horizontal scroll 404 > 390 and white text on cream (1.08:1); qa.py misses the overflow | `qa.py ../.fc/ls/auto --strict --url ...`; own check `.fc/own.py ../ls/auto 390 contrast` | `overflow-wrap:anywhere`/smaller tracking for `.uses-band h2`, `max-width:100%` on the button; add a real overflow assert to qa that includes clipped descendants |
| F4 | BLOCKER (send) | candlelit copy invents facts: "A garden for 200 at dinner.", "See the hall by appointment" / "The hall" | read `.fc/proof/candlelit/index.html`; not in `stonehurst-candlelit.json` | voice copy_overrides for this proof; fix the evening voice so it never names a "hall" |
| F5 | MAJOR | Guide email input has no visible focus indicator (outline none, transparent border, ~17% alpha 3 px glow) on all four sites, worst on the dark band | `.fc/shots/g-editorial.png`; computed styles in report task 2(f) | give `.guide input:focus-visible` a 2 px solid accent outline (3:1 vs band); add a pixel-diff focus test to qa |
| F6 | MAJOR | Invented service promises and fake availability in every site (reply in a minute, 24-hour hold, text confirmation, reminder, reschedule link, fake slots/past dates) | task 5 list | label flows as demo inside the page or strip the claims; keep only what the content says |
| F7 | MAJOR | Preset copy leaks Stonehurst: "the long table", "Established" for a build year, "Garden Wedding Estate" title, "distinct looks", "Residence, garden and carriage house. ." | LSH build, task 4 | move phrases into content-driven slots with fallbacks; stat label from the number's own label |
| F8 | MAJOR | editorial does not read as a luxury venue (magazine / blog); hero photo pushes the name below the fold; duplicated opening sentence; cramped guide band | task 3 | rework or drop from the preview set |
| F9 | MAJOR | Shared bottom third (guide band, filming band, footer) is the same across dialects; the filming band is word-for-word identical | task 3 | give each dialect its own guide/filming composition or fold the filming band into one ruled line |
| F10 | MAJOR | botanical and editorial print the hero deck twice back to back | screenshots T1440-0 / T390-0 | suppress the intro statement when it equals the hero deck |
| F11 | MINOR | 6-15 images per page render at >1.5x of their intrinsic width on retina (up to 2.0x on the 2400 hero) | `.fc/own/*-static.json` | use bigger source crops for the lead or accept; qa should warn |
| F12 | MINOR | qa.py hard-codes `ROOT=~/projects/insert` (line 62) and crashes with a null-`header` error on a 404 | run qa from any other checkout | derive ROOT from `__file__`; fail with a clear message |
| F13 | MINOR | Weak checks: E5 (caps-only faces / small-caps), E8 (gallery pager), E15 (body text), E16 (non-`p` text: botanical timeline 16 px), E17 vacuous | task 5 | widen the selectors |
| F14 | MINOR | `copy_overrides` documented in schema.md but not implemented; `--copy` accepts only `key=value` | task 4 | implement or delete from schema.md |
| F15 | MINOR | estate hairline margins stay thin (h1 24% mobile, 1x h1 19% / h2 16%); transfer sizes 1.9-3.3 MB at load; "20 of 25 images lazy" on editorial | qa warnings | known open items 2 of 2C |
| F16 | MINOR | Stage 2C open items 1 (candlelit has one pairing) and 3 (no Stonehurst lead supports on-photo copy) still apply at c90c636; 2D may have changed them | not re-verified (2D is in the main tree) | - |

Per-site verdicts (proofs at c90c636): **estate SHIP**, **candlelit SHIP after F4**, **botanical FIX FIRST** (F10, F5, desktop first-screen density and the empty band), **editorial REWORK** (F8).

Overall: **PASS-WITH-CONDITIONS for the four Stonehurst proofs** (no contrast failure, no overflow, no broken flow, flows and reduced motion verified independently); **FAIL for the factory as a general system** (F1-F3: three crash/break classes on a second venue's ordinary content). Conditions before the proofs go on the unlisted preview link: (1) F4 copy fix for candlelit; (2) F5 focus ring; (3) F6 either label the booking flows as a demo on the page or remove the invented promises; (4) F10 duplicate sentence on botanical; (5) drop or rework editorial; (6) fix the `<title>` suffix "PROOF-<NAME>" so no internal id shows. Before the factory builds a second venue for real: F1, F2, F3, F7, F14, and re-run this stress on Lindley-Scott with a human-written content file.

Repro bundle: `/tmp/factory-check/.fc/` (own.py contrast/static, own2.py headings + focus + flows + reduced motion, spec.py E-audit, tiles.py screenshots, hostile.py variants), report numbers come from those files. Limits: the stepped screenshots were viewed at half scale on desktop; blank-image warnings for two lazy images were not reproduced and are not findings; `/tmp/factory-check` is a worktree of c90c636, so 2D fixes in the main tree are not covered.
