# /venues rehaul: research and design principles

Written 2026-10-23. Goal from Dillon: make the /venues page "less techy, more elegant and refined, perhaps even
slightly luxurious." This note covers sites that sell a *service* to premium hospitality and wedding clients, as
opposed to the 51 venue sites already covered in `docs/research/04-luxury-venue-vocabulary.md`.

Method: Playwright (Chromium, headless) loaded each URL below at 1440x900 and 390x844, scrolled to trigger lazy
content, took fold and full-page screenshots (`docs/research/shots/rehaul/`, gitignored), and read computed styles:
page background, largest background fills, h1/body face, weight and size, filled/outlined buttons, CTA wording,
motion libraries, `<hr>` count, any monospace face. 21 of 22 loaded; Mr Boddington's Studio
(mrboddingtonsstudio.com) timed out and is not counted.

## Sites loaded

| # | Site | Type | Paper / palette | Type voice | Proof without numbers | CTA tone |
|---|---|---|---|---|---|---|
| 1 | https://www.aman.com/ | hotel group | warm stone `#F3EEE7`, charcoal `#313131` button, 0 radius | Lyon Display; tiny caps eyebrows ("FESTIVE WITH AMAN") | the photography; place names as captions | "Reserve", "Discover more" (underlined text link) |
| 2 | https://aubergeresorts.com/ | hotel group | white + `#ECEAE8`, muted gold button | Financier Light 40 px h1, 20 px serif body | the list of properties, set like an index | "Start planning", "Check availability" |
| 3 | https://www.firmdalehotels.com/ | hotel group | ivory `#FAF7F2`, sage `#DBE0DE` band | Caslon 540 at 48 px, Gill Sans body; one hairline rule under the intro | founders' story in one paragraph: "Founded by Tim and Kit Kemp in 1985" | "Book a room", pill outlines for city filters |
| 4 | https://www.mindyweiss.com/ | planner | white, black | large serif wordmark, few words | a single editorial photo of a couple on a stair | "Contact" in the nav only |
| 5 | https://www.eastonevents.com/ | planner | slate blue `#54697A` over cream `#F2EDE8` | wordmark only above the fold | an aerial of a real event fills the screen | none above the fold |
| 6 | https://www.sarahhaywood.com/ | planner | oatmeal `#EFEDE7`, ink `#141414`, navy `#00263A` | small caps h1 (14 px), serif display at section level; a monogram "S" with hairlines | one press line (Vogue) in small caps; otherwise photos | "Enquire", "Contact us" |
| 7 | https://josevilla.com/ | photographer | white, ink `#161616` | light wordmark, no h1 | the work, full-bleed | "Send message" (square ink button) |
| 8 | https://www.corbingurkin.com/ | photographer | white card floating on a blurred floral photo | Venezian caps, italic serif tagline, Crimson body | the photo set like a mounted print inside a white mat with a hairline frame | "Submit an inquiry" |
| 9 | https://www.saipua.com/ | florist | sand `#EEDCC4`, olive-brown `#826717` | EB Garamond 32 px body, caps nav | one still life of the studio sink and linen | none above the fold |
| 10 | https://www.putnamflowers.com/ | florist | white; arrival popup | Caslon-style wordmark | product photos | newsletter modal on arrival (the cheapening pattern) |
| 11 | https://www.philippacraddock.com/ | florist turned mentor | parchment `#F1ECDF`, ink-blue `#2A3A4B` | Cormorant Garamond 38 px, DM Sans 16 px | founder portrait, plain first-person story, quote cards | dark slate rectangular buttons with arrow |
| 12 | https://www.smythson.com/us/ | stationer | deep green `#041E42`-navy accents on white | Gill Sans Nova, very small | heritage line "Est. 1887"; craft close-ups (gold stamping) | "Book an appointment"; arrival popup |
| 13 | https://www.bernardmaisner.com/ | stationer / calligrapher | white with a single heavy keyline frame | Copperplate caps 90 px | four plain categories, nothing else | none |
| 14 | https://www.romanandwilliams.com/ | design studio | white, linen `#DCDAD1` | Lyon Display 56 px, Lyon Text 18 px body, italic "of" | candlelit restaurant interiors with no people; italic serif captions | "Contact" only |
| 15 | https://www.studioilse.com/ | design studio | near-white, black | condensed caps wordmark | interiors in raking daylight, set tables with no people | none |
| 16 | https://www.mbds.com/ | hospitality design | warm white `#FFFBF8` | huge grotesk wordmark over a mosaic detail | the work, as details | "Menu" only |
| 17 | https://www.honeybook.com/ | B2B tool | white + highlighter yellow `#FFFA77` | Bureau Serif 64 px, sans 24 px | "15K+ reviews" stars above the h1, product dashboard, floating photo tiles | "Get started for free" (pill) + promo bar |
| 18 | https://tave.com/ | B2B tool | grey `#F2F2F2` | VSCO Gothic caps 54 px | floating UI cards (calendar, invoice, "New lead") over a bride photo | "Try for free", "Book demo" (pills) |
| 19 | https://www.planningpod.com/ | B2B tool | white, pale blue, orange `#FFA634` | Golos 700 58 px | "grow their event bookings by 64%" in red; diagram of floating app cards | "Schedule a Demo" (orange, 22 px radius) |
| 20 | https://www.perfectvenue.com/ | B2B tool | white, coral `#FE6257`, indigo | Gazpacho 700 56 px | "AI Reply" in nav; modal on arrival | "Start free trial", "Request demo" |
| 21 | https://tripleseat.com/ | B2B tool | white, forest `#183D38`, hot pink `#FF4593` | Archivo Black caps | "Trusted by more than 20,000", Capterra / G2 badges, dashboard screenshot | "Request a demo" (pink pill), mega-menu |

## What the refined service brands share

- **Paper, not white.** Aman, Firmdale, Sarah Haywood, Saipua and Philippa Craddock sit on stone, ivory, oatmeal or
  parchment (L ~0.93-0.97). Ink is near-black or a dark muted colour (charcoal, navy, ink-blue, olive-brown). There
  is one accent at most, and it is never saturated.
- **A serif with a sturdy cut, at normal weight.** Lyon Display (Aman, Roman and Williams), Caslon 540 (Firmdale),
  Financier (Auberge): weight 400, 40-56 px, sentence case, often one italic word. Body is either a text serif at
  18-20 px or a humanist sans (Gill Sans at Firmdale and Smythson). Labels are small tracked caps, never monospace:
  0 of 21 sites load a mono face.
- **Proof is the work, the founder, or the date, not a number.** "Founded by Tim and Kit Kemp in 1985", "Est. 1887",
  a portrait and a first-person paragraph, a list of properties set like an index. No counters, no star ratings, no
  charts. Where a service brand shows its product (Corbin Gurkin), it mounts it like a print: white mat, hairline
  frame, generous margin.
- **Buttons are quiet rectangles.** Charcoal or ink fill with 0-3 px radius (Aman, Jose Villa, Philippa Craddock) or
  an underlined text link ("Discover more"). One primary action per screen.
- **Ornament is one thing.** A monogram (Sarah Haywood's S between hairlines), a single rule under an intro
  (Firmdale), a keyline frame (Bernard Maisner). Never several.
- **Motion is slow or absent.** Lenis smooth scroll (Firmdale, Haywood), fades. No counters or typing effects.

## What "techy" looks like (the four B2B tools)

Pill buttons in saturated colours (orange, coral, hot pink); bold grotesk or heavy display at weight 700; floating
UI cards at angles over photos; dashboards and tables as the hero image; numbers as proof ("64%", "20,000", "15K+
reviews" with stars); badges (Capterra, G2); promo bars and arrival modals; mega-menus. The current /venues page
borrows a gentler version of this: mono micro-labels, a "LIVE"-style status chip, a reply-time counter that counts
up, glossy phone mocks with status bars, "< 60 s" and "24 / 7" stat tiles, numbered "01 / 02 / 03" kickers. These
are what make it read as software.

## Design principles for the rehaul

1. **Ivory paper and ink, one muted accent.** Paper `#F5F0E6`, ink `#1E1C17`, deep olive `#3B4232` as the accent
   (from the generated photography's hedges and olive branches), a bronze used only in hairlines and large type. Small
   text stays ink or olive so every pair clears 7:1.
2. **One serif, pinned.** Newsreader 500 with `opsz` pinned (24 for headings, so it can't go hairline at large
   sizes), sentence case, one italic phrase per heading at most. Body in Source Sans 3 (humanist) at 18 px, line
   height 1.65. Labels in small tracked caps of the body face. No monospace anywhere.
3. **Lead with a place, not a phone.** The hero is a large, calm photograph of a venue at blue hour seen through
   open doors (no people), set inset with page margins. The product appears later, small.
4. **Show the product like stationery.** Each automation is shown as a printed card: a note, a tour confirmation, a
   deposit request, a thank-you, set in the page's serif on a linen mount with a soft shadow, the way Corbin Gurkin
   mounts a print. No device frames, status bars, ticks or timers.
5. **Proof is what the couple experiences.** Replace stat tiles with a plain sentence about the couple's evening. The
   one timing example (40 seconds) stays inside the clearly labelled fictional Willow Creek sample.
6. **The offer is set like an invitation.** The charter section is a framed card with a centred serif heading, plain
   terms, the price in the display face. The site refresh is a smaller companion card, not a strip.
7. **One ornament: a small monogram "I" between two hairlines.** Used three times: header, invitation card, footer.
8. **Slow, single motion.** One reveal (opacity + 12 px rise, 900 ms, `cubic-bezier(.2,.7,.2,1)`), nothing that
   counts, types or loops. Everything static under reduced motion.

## Remove / keep

**Remove:** IBM Plex Mono and every mono micro-label; the LIVE/"Auto-reply · on" chips; the reply-time count-up and
"✓✓ Delivered · replied in 0 s"; the glossy phone frames with status bars and 5G; the "< 60 s / 24 / 7 / Your part"
stat tiles; "01 / 02 / 03" index kickers; the grid/terminal background motifs; Playfair Display + Inter (both on the
exclusion list in spec 05); the "You're losing bookings" fear headline.

**Keep:** the four automations and what each does; the fictional Willow Creek example (labelled as illustrative,
with the 40-second reply); "your part is the tour and the wedding day"; the charter terms (two seats by
application, free build, $300/month locked for as long as the venue remains a partner, six-month minimum then month
to month, billing from go-live, 30-minute conversation); standard pricing for later partners, now worded so the
$300 clearly continues; Site Refresh as a separate project from $2,500, upgraded to a card; the Calendly embed, the
contact form (`/api/contact`, `data.business` tag) and `/api/track`; anchors `#stack`, `#charter`, `#book`.
