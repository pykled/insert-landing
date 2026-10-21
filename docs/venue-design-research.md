# Wedding venue website design, 2026: research synthesis

Written 2026-10-20 for Insert's venue site factory. This is the short, decision-oriented version. The full source
notes with every URL and the HTTP status observed when it was fetched are in `docs/research/`:

- `01-venue-site-survey.md`: 36 live venue homepages (24 Southern California, 12 national) fetched and screenshotted on 2026-10-20, pattern counts, what made the memorable ones memorable.
- `02-market-conversion-seo.md`: builders and template shops, conversion evidence, couple behaviour data, WCAG 2.2, schema.org and Google's structured-data policy. Each fact is graded STRONG / MEDIUM / WEAK.
- `03-generation-approaches.md`: design tokens, theme packs, static generators, palette extraction, optical sizing, layout archetypes, the homogenisation literature, image pipelines.

Nothing below is a claim we could not fetch. Where the only evidence is a vendor's own data or a secondary report, it says so.

## 1. How venue sites are designed now

**The sample converges on one page.** Across 36 homepages the default order is: announcement bar (optional) → header with logo, links and one button → full-bleed hero (photo or muted video) with a two-to-four-word adjective headline ("A Charming Hideaway", "Picturesque & Spectacular", "Elegance & Grandeur") and a Schedule-a-Tour or Contact button → centred "Welcome to [Venue]" paragraph → three cards → image slider or grid → a couple's testimonial → closing CTA or form → footer with vendor links and photo credits. Lombardi House, Franciscan Gardens and Rancho Las Lomas (the latter two share H2 text verbatim), Walnut Grove, Rimrock, Hummingbird Nest Ranch and Venue at the Edge follow it almost exactly (survey §d, URLs and screenshots in `01-venue-site-survey.md`).

**Counts that matter (n = 36, survey §b):**

| Pattern | Count |
|---|---|
| Full-bleed static photo hero | 13 |
| Full-bleed autoplay video hero (7 of these are ranch, vineyard or estate venues) | 11 |
| Slideshow hero | 4; inset video 2; split 1; text-first or editorial with no full-width hero 5 |
| Header: left logo + right links / centred logo / hamburger-only / none | 19 / 13 / 5 / 1 |
| Embedded inquiry form on the homepage | 2 (same operator; about 10 questions including a budget bracket) |
| Embedded availability calendar on the homepage | 0 |
| Any guest number visible on the homepage without a click | 4 (7 in the HTML) |
| Any price on the homepage | 0; 13 have a Pricing / Rates / Packages / Wedding Cost nav item; 1 links an un-gated pricing PDF |
| Serif display + sans body / all-sans / loads a script face | about 25 / 9 / 7 |
| Accent colour visibly taken from the property | 12; black ground 6; white plus photo with no real accent 18 |
| Autoplay video somewhere on the page / slider library shipped / no motion at all | 14 / about 19 / 4 |

**Video heroes fail in practice.** Frederick Loewe Estate rendered blank in a headless browser, Ponte Winery hides its video behind a 21+ gate, Sunstone behind a dark overlay plus cookie modal, Los Willows needs an "Unmute" pill (survey §e.3). Design the poster frame as the composition; the moving version is a bonus.

**Platforms.** Squarespace 9, WordPress/Elementor family 14, Wix 5, custom 3, one each of Webflow, Duda, GoHighLevel and Showit. The platform predicts the header more than the venue type does (survey §e.1). Showit, which dominates wedding photographers and planners, was hard to find among venues: the Showit candidates we chased were parked or off-DNS, and only one Showit venue could be verified.

**Template market.** Showit costs $27-$49 a month plus a third-party template at $400-$1,525 (Honeysuckle House at $900 is the only purpose-built venue template found; McCravy's Alice/Taylor at $797 list venues tenth after photographers). Squarespace $19-$99, Webflow's Marrymint $29, Pixieset Website $0-$18, Format $10-$15, Elementor themes $59-$149. Davey & Krista teach the "3-Font Formula" explicitly: one serif for headings, one sans for body, one script "used sparingly"; free fallbacks Playfair Display, Cormorant Garamond, Lato, DM Sans, Allura, Great Vibes (all in `02-market-conversion-seo.md` Part 1 with pricing-page URLs).

## 2. Why they all look the same, and what actually reads as different

**Causes (sourced).** The same dozen Showit shops sell to photographers, planners and venues alike; every shop ships the same page set and homepage order; the serif + sans + script trio is taught as the formula; demo templates are art-directed with the same editorial wedding photography the venue then fills in; and marketplace curation rewards "editorial, fine-art, luxury" descriptors. Operators also clone builds across sister venues (Franciscan Gardens ↔ Rancho Las Lomas; SmogShoppe ↔ Millwick). The academic backdrop: Goree et al. (CHI 2021) analysed about 200,000 screenshots of about 10,000 sites and found layout distance between sites fell by more than 30% after 2008-2010, driven by shared libraries rather than copying (the PDF has vanished from its host; cited via two press reports, so WEAK).

**What created perceived uniqueness in the sample (survey §c), in rough order of weight:**

1. Colour taken from the place, not from a palette tool: Rancho Las Lomas runs the casita's stucco, trees and roof tile; the Lautner Compound sets desert sage against an archival black-and-white photo; Cedar Lakes frames its lake video in the shoreline's pine green; Audrey Irmas repeats the building's green glass as header arcs.
2. A typographic voice instead of "serif + sans": Hudson Loft's viewport-wide extended grotesk with Courier for everything else; Pippin Hill's GT Sectra + Maison Neue; Condor's Nest's light Fraunces on empty sky; The Wilds' italic bronze second line on every headline.
3. A first-screen fact: The Wilds' three sentences of specifics (125 acres, covered pavilion, climate-controlled reception for 200) and "800+ five-star reviews"; Gainey's "60 Years / 4 Generations / 3 Vineyards"; SmogShoppe's capacity, square footage and furniture inventory.
4. Layout rhythm that mirrors the building or the offer: Hudson Loft's floors as chapters; Cedar Lakes' three-season triptych; Dos Pueblos' single portrait and nothing else above the fold.
5. One signature interaction, used once: Cedar Lakes' video corners rounding on scroll; Audrey Irmas' skewed slider; Darlington's hand-written "Now booking 2028!" marquee. Nobody memorable stacked two.
6. Utility presented as confidence: The Foundry's hero is the three words GALLERY RATES INFO; Dos Pueblos' only CTA is "Request Availability"; Los Willows writes "Up to 250 guests" inside the nav label.
7. Photography that shows the place, not a couple: Gather Greene opens on a meadow with no people and no text; contrast with heroes where the venue is invisible behind a dip-kiss close-up.

The practical conclusion for a studio: rotate five controlled variables (hero class, header archetype, display-face family, accent source, one signature device) and the output reads as a different site; swapping photos does not (survey §e.4). That list is the spine of the factory's fingerprint.

## 3. Conversion and UX evidence for venues

| Finding | Number | Source and strength |
|---|---|---|
| Price is the first factor couples use to decide whom to contact | 77-78% | TKWW / WeddingPro survey, n not stated (MEDIUM) |
| Venues showing rates on their Knot storefront got more couple replies in TKWW's own test | +25% | WeddingPro blog (MEDIUM, vendor-run) |
| Storefronts that add pricing and availability get "nearly twice as many two-way conversations" | about 2x | TKWW press release, July 2025 (MEDIUM) |
| Couples inquire with about 5 venues and tour about 4; about 80% start venue research within 2 months of engagement | 5 / 4 / 80% | TKWW Venue Selection Study, 781 couples (MEDIUM) |
| Venue share of budget; average venue spend for 2024 weddings | about 40%; $12,200 | TKWW venue report; Fox Business summary (MEDIUM) |
| Planning done on phone or tablet | 46% (2020, n = 25,000); 44% (2025) | WeddingWire Newlywed Report; WeddingPro (STRONG for its year / MEDIUM) |
| Replying to a lead within 3 hours makes couples 2.2x more likely to reply; 52% cite responsiveness as a trust factor | 2.2x; 52% | WeddingPro 2025; Knot 2026 Real Weddings Study, n = 10,474 (MEDIUM / STRONG) |
| The classic lead-response study (respond within an hour, far higher qualification odds) | HBR 2011 | B2B, paywalled, not wedding-specific (MEDIUM, and not ours to lean on) |
| 53% of mobile visits abandon a page that takes over 3 s | 2017, all industries | Google / AMP blog (MEDIUM, dated) |
| Core Web Vitals "good" at p75 | LCP 2.5 s, INP 200 ms, CLS 0.1 | web.dev (STRONG) |
| WCAG 2.2 AA | text 4.5:1, large text and UI 3:1, targets 24 x 24 CSS px, focus visible | w3.org (STRONG) |

**Form length.** HubSpot's 40,000-page study found conversion falls only slightly as single-line fields are added, while multiple text areas and dropdowns hurt (MEDIUM; B2B content forms). The widely quoted "11% per extra field" and Venngage numbers could not be traced to a primary page and are not used. Defensible reading for a venue: date, guest count and one contact field as the first ask; "tell us about your day" as an optional second step. That is exactly the three-field date check already in the Stonehurst mock.

**Tour booking.** HoneyBook's scheduler starts at the $49 tier; Perfect Venue is $199-$299 per location; Tripleseat, Planning Pod and Releventful bundle inquiry, calendar, proposals and floor plans; Weven now redirects to The Knot (acquired); Tock could not be read (Cloudflare). Six of 36 surveyed venues hand the couple to one of these third-party forms, each with its own typography, which is exactly where polish collapses (survey §e.5). A native short form in the venue's own type is a differentiator by itself.

**Schema.org and Google.** `EventVenue` (a Place) and `LocalBusiness` can be combined as `"@type": ["EventVenue","LocalBusiness"]`; relevant properties are `address`, `geo`, `telephone`, `maximumAttendeeCapacity`, `amenityFeature` (as `LocationFeatureSpecification`), `tourBookingPage`, `openingHoursSpecification`, `priceRange`. Google rewards only the LocalBusiness subset (name, address, geo, hours, priceRange, real ratings) and genuine public `Event` nodes (open-house days, never "weddings available"). FAQ rich results have been restricted to government and health sites since 8 August 2023; `FAQPage`, `EventVenue`, capacity and amenities are hygiene for machine readers, not ranking levers (all primary URLs in `02-market-conversion-seo.md` Part 3). Google Business Profile lists event venues among businesses that "shouldn't provide hours". The generator emits this JSON-LD on every build.

## 4. How to produce many different sites from one system

**Token model.** The W3C Design Tokens Community Group format (draft 2025.10) is the right on-disk shape; Style Dictionary is optional. Radix's 12-step semantic scale and Tailwind v4's OKLCH shades are the palette shape to copy. The architectural precedent that fits best is Shopify Online Store 2.0: a JSON template is an ordered list of sections, each section has presets and binds a named colour scheme from a theme-level schema. Relume ships 1,000+ numbered sections; variety there comes from archetype count, not component cleverness.

**Generator choice.** For a one-person studio whose content is written by agents, Python + Jinja2 or Node + Nunjucks beats Astro (heaviest, slowest in 11ty's 2022 benchmark) and Hugo (Go templates). Eleventy is the sensible fallback if we later want its data cascade and Image plugin. We chose Python + Jinja2 because Pillow, numpy, Playwright and the existing Stonehurst verifier were already in that runtime and the result is three dependencies and about 1,500 lines (see `venue-site-factory.md`).

**Palette from photographs.** Quantise (k-means or MMCQ), then score candidates for usable chroma rather than pixel share (Material Color Utilities scores toward a target chroma and 30° hue spread), then choose tones by rule: in HCT a tone difference of 50 guarantees WCAG 4.5:1. We work in OKLCH and walk lightness until each pair passes, which is the same idea with a verification step instead of a guarantee. WCAG 2.2 remains the compliance baseline; APCA is beta and WCAG 3 says its contrast algorithm is "yet to be determined", so APCA is a design heuristic at most.

**Optical size is the legibility trap.** `font-optical-sizing: auto` maps the opsz axis to the pixel size, so a 96-128 px headline in Bodoni Moda (opsz 6-96), Fraunces (9-144), Newsreader (6-72), Literata (7-72) or Source Serif 4 (8-60) lands on the hairline display master. Pinning `font-variation-settings: "opsz" N` at a mid value and a weight of 500 is the fix, which is what Stonehurst v2 did and what every pairing in the library now declares. Playfair Display has no opsz axis to correct with, which is one more reason the generic wedding trio reads badly at display size.

**Measuring sameness.** Bohunsky & Gatterbauer (WWW 2010) argue the rendered visual structure, not the DOM, is what users perceive; perceptual hashes (pHash, dHash, colorhash with Hamming distance) are the cheap screenshot metric. The literature gives no thresholds. Our fingerprint uses the designed choices directly (type family and class, accent hue, hero family, section archetypes and order, signature moment, shape language) because they are known before a pixel is rendered; a pHash of the screenshots is the obvious second metric to add once we have more than five sites to calibrate against.

**Images.** `srcset` with `w` descriptors and honest `sizes`; never upscale (sharp's `withoutEnlargement`; Pillow needs an explicit guard); Lighthouse flags any image whose delivered size implies 4 KiB of savings over rendered x DPR; `fetchpriority="high"` on the hero and never `loading="lazy"` on it. The factory's QA gate checks all of this per rendered image, including inside `object-fit: cover` frames.

## 5. The five findings that changed the design

1. Nobody shows a price and almost nobody shows a capacity, yet price and capacity are the first two things couples want. A first-screen facts strip and an honest pricing-guide path are differentiators on their own, and TKWW's own data says they roughly double conversations.
2. The header and hero class are what the eye reads as "the same site". Varying them, plus the display face and the accent source, matters more than any amount of photo swapping.
3. One signature device per site, built from the venue's own facts (its schedule, its capacities, its guest's day), is what the memorable sites had and the templates lack.
4. Legibility has to be measured, not asserted: contrast under every glyph against the real background, pinned optical size and weight, and a stroke probe for hairlines. The calibration data (`docs/qa-calibration.md`) also says what the probe cannot see.
5. The lead handoff is where polish collapses. Keep the date check, tour scheduler and guide capture native, three fields or fewer for the first ask, in the venue's own type.
