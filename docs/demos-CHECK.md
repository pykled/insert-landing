# Checker report: HomeStead / Lindley-Scott / Stonehurst demos

Checked 2026-10-29. Read-only plus screenshots. No files edited, nothing deployed, nothing committed.
Build under test: `.factory-check/demos/<slug>/index.html`. It is byte-identical (`cmp`) to the copy in `private-previews/2d32be7dda6d361dd89ffdfd/demos/<slug>/`, and the live Railway page hashes match (md5 identical for all three).

## 1. Re-run results (mine, not earlier claims)

| Check | Command | Result |
|---|---|---|
| QA homestead | `python3 factory/qa.py .factory-check/demos/homestead --strict` (against the existing local server on :4821, repo root) | exit 0, PROBLEMS 0, WARNINGS 1 (diversity: 0.481 vs stonehurst-b, warn band 0.35-0.50) |
| QA lindley-scott | same | exit 0, PROBLEMS 0, WARNINGS 4 (1592 KB at load; h1/h2 hairline share at 1x and mobile) |
| QA stonehurst | same | exit 0, PROBLEMS 0, WARNINGS 2 (hairline share on h1 mobile and h2 at 1x) |
| Factory tests | `cd factory && python3 -m pytest -q tests` | **123 passed in 530 s** (exit 0). `python3 factory/tests/run_all.py` from the repo root fails with `No module named 'tests'`; it must be run as `python3 -m tests.run_all` from `factory/` per tests/README. This is a doc/invocation trap, not a code failure. |

The claims "qa.py --strict passes" and "123 tests" are confirmed.

Live: all three `/private-previews/<token>/demos/<slug>/` return 200 with `x-robots-tag: noindex, nofollow, noarchive`. A wrong token returns 404.

## 2. Fact check

Sources fetched today: homesteadoakglen.com (/about, /information, /contact, /guests, 2027 overview booklet PDF), lindleyscotthouse.com (/about-us, /weddings, /receptions, /faq, /additional-services, /film-shoots, /contact-us, home), thestonehurst.com (home, /faq, /our-history, space pages).

### The HomeStead (Oak Glen)

| Claim on page | Status | Source |
|---|---|---|
| 5.5 acres, Wilshire Peak, San Bernardino Mtns, oaks, sycamores, apple trees, lilac field | VERIFIED | /about, /information |
| One wedding a day; private estate not open to the public | VERIFIED | booklet FAQ "only 1 wedding per day" |
| Up to 180 guests, "comfortably" | VERIFIED | booklet "maximum of ~180" (page says "at most"; venue says "~180", a small rounding up) |
| Blackie Wilshire "more than a hundred years ago", original homestead pieces stand | VERIFIED | /about |
| Owners Don and Paula Christante | UNVERIFIED in my fetch (JSON cites /about; the fetched /about text does not name them, only "Paula and the worker-bees" on /contact). Recheck the cited page or drop surnames. | |
| Four spaces: ceremony, reception, beverage area, cottage and cabin | VERIFIED as venue areas. The count "4" is the Maker's own, noted in JSON | /about |
| Terraced stage, fire pit and s'mores, string lights, self-serve beverage station | VERIFIED | /about |
| Cottage and Cabin with fridge, ice, microwave, one for each party | VERIFIED (fridge, ice, microwave on /information; "one for each party" is a mild paraphrase of "Our Cottage and Cabin await both groups") | /information |
| Capacity "on request" for ceremony and reception | HONEST (venue publishes none) | |
| Outside vendors welcome, no extra fee; no service/admin/corkage fees; tax included; own DJ "generally no"; 40x60 tent; guests arrive no earlier than 30 min; pets; payments 210/150/60; 3-week contract | VERIFIED | booklet FAQ and /information |
| 4,734 ft, about 10 degrees cooler, no gas stations in Oak Glen | VERIFIED | /guests |
| Address 11951 Oak Glen Road, Oak Glen, CA 92399 | VERIFIED | /contact |
| info@homesteadoakglen.com | VERIFIED | /about, /contact, booklet |
| (909) 790-8010 | VERIFIED (also on /about). The venue lists a second number, (951) 840-6974, as the booking text/call line in the booklet; the page shows only the 909 number. Acceptable. | /about, /contact |
| "Tours by appointment" | VERIFIED | /information |
| Micro weddings (in JSON uses) | not shown on page |
| Image caption "Wilshire Ranch, lettered on an old saw" | UNVERIFIED (caption describes a photo; not a venue claim, nit) | |
| "A family-owned ... ranch wedding venue" | VERIFIED | home |

No WRONG claims.

### Lindley-Scott House (Azusa)

| Claim | Status | Source |
|---|---|---|
| Built 1911 for Charles Lindley, president of the Foothill Ranch; 1924 Mabelle Scott Anderson, Rancho School for Girls | VERIFIED | /about-us |
| Weddings since 1978 | VERIFIED (venue says weddings, receptions, banquets, catering since 1978) | /about-us |
| 4 acres of gardens; hitching post; little changed | VERIFIED | /about-us |
| Ceremony on front lawn under old oak and cypress, arch, mountains | VERIFIED | /about-us, /weddings |
| Grand staircase, foyer, Victorian dressing room | VERIFIED | /about-us |
| Carriage House built 2003, seats 200, two-minute walk, commercial kitchen, bar | VERIFIED | /about-us, /receptions |
| "Up to 200 seated" on Front Lawn | VERIFIED ("The Garden holds up to 200 seated") | /weddings |
| One event a day | VERIFIED | /receptions, /faq |
| Ceremony 1.5 h, reception 5 h; vendors from 11 AM; own coordinator in addition; no receptions on lawns; outside vendors add food after entree; horse and carriage; lighting; 25% deposit; 20% service charge on meal; restrictions; photos without wedding | VERIFIED | /faq, /receptions |
| **Footer, JSON-LD and hero: "Tours by appointment, Monday to Sunday"** | **WRONG / misleading.** FAQ: "Mon-Thur by Appointment Only; Fri, Sat and Sun 10:00am - 11:00am". Neither the homepage nor contact page says "Monday to Sunday" (JSON cites contact-us and home; home only says "Contact us to make an appointment"). | /faq |
| Address, (626) 334-5215, historicallindleyscotthouse@gmail.com | VERIFIED (footer on every page) | |
| "Quinceañeras, corporate events and film shoots" | VERIFIED | /additional-services, /film-shoots |
| "The pricing guide, in full." / "Send the guide" | The venue publishes no pricing guide on the pages I fetched. The widget is labelled preview, but the heading promises a guide that may not exist. See must-fix 4. | |

### The Stonehurst (Shadow Hills)

| Claim | Status | Source |
|---|---|---|
| 9 acres, corner of Sunland and Stonehurst Ave | VERIFIED | /our-history |
| 6 spaces (greenhouse, barn, flower, bamboo, terrace, bungalow) | VERIFIED | home |
| Up to 200 guests; one event a day; 3-4 spaces; 12-hour rental, gates 12, end 10, breakdown to midnight; planner required; valet/site manager/restrooms/security included | VERIFIED | /faq |
| Greenhouse 200; barn 150; flower garden 175; bamboo 60 ceremony / 120 cocktail; bungalow 1-15; barn 3 chandeliers; HVAC; "where industry meets nature" | VERIFIED | space pages |
| Barn "greets you at the gate" | Mild paraphrase ("greets you when entering the property"). Nit. | |
| Barn 1907 Boy Scout meetings, doors 2015, Joe Stromei, name carved in greenhouse beam, South American fig, cactus garden | VERIFIED | /our-history |
| History credit to Shadow Hills Property Owners Association | VERIFIED | /our-history |
| Bungalow "mid-century", "original to the property" | VERIFIED (home says mid-century bungalow; bungalow page says original) | |
| thestonehurst@gmail.com | VERIFIED (named on /faq); no phone invented | /faq |
| Tours by appointment | VERIFIED ("by Appointment Only") | home |
| "One wedding a day" in headline | Nit. The venue says "one event a day" and also hosts filming and private events. Equivalent for a wedding, but narrower than the source. | |
| **FAQ and JSON-LD: "email us and we'll come back with availability and rates for your dates"** | **WRONG / invented.** The venue only says "please email thestonehurst@gmail.com". It does not promise rates or availability. | /faq |
| "A hand-laid cobblestone path" caption | Nit. Venue says hand-laid stone work on the pathways; "cobblestone" is added. | |
| Featured-in row (Junebug, Loverly, Style Me Pretty, Vogue India, The Knot, Zola, Wedding Chicks, PartySlate) | PARTLY VERIFIED. Homepage HTML text matched Junebug, Vogue, Zola, PartySlate; the rest are likely images, so not confirmed. Third-party press marks on an unaffiliated page imply endorsement; see must-fix 3. | home |
| Greenhouse "Up to 200" | VERIFIED. | |

### Relationship and placeholder checks

- No "None", "null", "undefined", "TODO", "{{", "NaN" text in any rendered page.
- Disclosure of unsolicited status: the words "Prepared by Insert as an unsolicited design preview. Not affiliated with the venue." exist **only in the meta description** (invisible). The visible text is a small footer chip: "Concept preview by Insert · photography © <venue> · not affiliated with the venue". It never says "unsolicited", and nothing is visible above the fold. A visitor who lands on the page (venue staff, or a couple the venue forwards it to) sees a page that looks like the venue's own site. See must-fix 1.
- Every page is titled and written as the venue ("The HomeStead | Weddings in Oak Glen, CA", footer "© The HomeStead at Wilshire Ranch") and JSON-LD sets `@id`/`url` to the venue's real domain and lists its email and phone. noindex mitigates indexing, but the structured data asserts the venue's identity.
- Photography is the venue's own (credited in the footer chip). Copyright credit is present; licensing is not established.
- No third-party personal data beyond the venue's published contact details. Owner names (Homestead) are published by the venue (but see UNVERIFIED above). Reviewer names on the venue sites were not reproduced.

## 3. Visual (Playwright, system Chrome, 1440 and 390, .reveal forced visible, scrolled through to trigger lazy images)

- Horizontal overflow: none at either width on all three (`scrollWidth == clientWidth`, no unclipped element past the viewport).
- Broken images: none (all `<img>` loaded after scroll; zero 4xx or failed requests). Note: in a plain full-page screenshot without scrolling, the lazy images in the spaces and journey sections render as blank tan boxes. They load on scroll, so this is a screenshot artifact, not a bug, but a user who jumps via anchor on a slow connection will briefly see empty boxes.
- Homestead "A guest's day": the sticky stage shows one image at a time, steps 02-04 have no thumbnail until scrolled to; mobile shows an image per step. Works.
- Contrast: qa.py lowest small-text ratio 7.23 on Homestead; I found no unreadable text in the screenshots. Chip text in the footer is small and low-contrast-looking on mobile (nit).
- Mobile layout: heroes, forms, calendars, FAQ accordions, footers all lay out cleanly. Lindley and Stonehurst hero headlines wrap to 4-5 lines on 390 (acceptable).
- Page weight: Lindley 1592 KB at load (QA warning), Homestead 1220 KB, Stonehurst 1354 KB.

## 4. Links and forms

- All `href` values are `#id` anchors that resolve, `mailto:`/`tel:` links, Google Fonts links, or `#`. No dead in-page anchors.
- **`Privacy policy` links to `href="#"` on all three** (dead link; it also appears on a page that collects an email/mobile). Must-fix 2.
- Forms (`#date-form`, `#guide-form`): `novalidate`, no `action`, no `fetch`/XHR/sendBeacon in the page. Nothing is posted anywhere. Each shows "Preview only: nothing was held / booked / sent" and the input area carries "Preview of how inquiries could work". Calendars say "Times are sample times, not the venue's calendar". Well labelled.
- `mailto:` links (Lindley, Stonehurst "Email about a shoot or event", and contact lists) open a real email to the venue. That is the published contact, but it is the one place a visitor can send real mail from the preview, with a subject line "Filming or private event" preset. Fine as long as it is understood.
- Date and guest inputs hold placeholder values ("120", you@email.com); no personal data stored.

## Verdicts

### The HomeStead: PASS-WITH-CONDITIONS
Facts are the strongest of the three. Conditions: must-fix 1 (visible disclosure), 2 (privacy link), 5 (owner surnames).

### Lindley-Scott House: FAIL (one factual error, fixable in minutes)
"Tours by appointment, Monday to Sunday" contradicts the venue's FAQ. Fix and re-run QA, then it is PASS-WITH-CONDITIONS on the same shared items.

### The Stonehurst: FAIL (one invented venue statement, fixable in minutes)
The filming FAQ answer puts words in the venue's mouth ("availability and rates for your dates"), on-page and in JSON-LD. Fix, then PASS-WITH-CONDITIONS on the shared items.

## Must-fix (numbered)

1. **All three: make the unsolicited concept status visible.** Currently only in the meta description plus a small footer chip. Add a visible line near the top ("An unsolicited concept by Insert, not made by or affiliated with <venue>") and say "unsolicited" in the footer chip. Applies equally if the venue's own name and `©` line stay in the footer.
2. **All three: `Privacy policy` is `href="#"`.** Either point it somewhere real (Insert's privacy page) or remove it. The footer reads `© <venue>` next to it, which implies the venue's policy.
3. **Stonehurst: remove or soften the "As featured in" press row** (third-party brand marks shown on an unaffiliated page; only 4 of 8 outlets text-confirmed on the venue's homepage), or confirm each against the venue homepage images. Same concern, lighter, for Homestead's awards (not shown on page, good).
4. **Lindley-Scott:** (a) replace "Tours by appointment, Monday to Sunday" in the footer, tour copy and JSON-LD with the venue's published wording (Mon-Thu by appointment; Fri-Sun 10-11am) or "Tours by appointment"; (b) the pricing section heading "The pricing guide, in full." promises a guide the venue does not appear to publish; reword.
5. **Stonehurst:** reword the filming FAQ answer (page and JSON-LD) to the venue's statement: "For filming and photoshoots, email thestonehurst@gmail.com."
6. **Homestead:** confirm "Don and Paula Christante" on the cited page or drop the surnames; the fetched /about does not show them.
7. **All three: JSON-LD identifies the page as the venue's LocalBusiness** (`@id`/`url` at the venue's domain, with phone/email). Remove or retarget it, since the page is noindex and unaffiliated.

## Nits

- Stonehurst "One wedding a day" headline: the venue says "one event a day".
- Stonehurst "hand-laid cobblestone path" caption; barn "greets you at the gate".
- Homestead "180 guests, at most" (venue: "~180, comfortably"); "Wilshire Ranch, lettered on an old saw" caption is unverifiable.
- Lazy images show blank boxes until scrolled; consider `loading="eager"` for the spaces section's first image or a tinted `blur-up` placeholder.
- Lindley page weight 1.6 MB; QA warns.
- Diversity WARN: Homestead 0.481 vs stonehurst-b (inside the warn band, still passes).
- `python3 factory/tests/run_all.py` fails from the repo root; run as `python3 -m tests.run_all` from `factory/` (documented in tests/README only).
- Footer chip text is small; low emphasis on mobile.
