# The Stonehurst — homepage concept notes

Private spec mock. Built 2026-10-16 by Insert as an unsolicited "here's what your site could be" preview. Nothing has been sent to the venue. Nobody at the venue has been contacted.

- Mock: `previews/stonehurst/index.html` (+ `img/` WebP assets, `img/real/` source copies + manifest, `shots/` screenshots)
- Deployed copy (unlisted, noindex, `X-Robots-Tag`, `robots.txt` disallow): `private-previews/2d32be7dda6d361dd89ffdfd/stonehurst/` → https://insert-landing-production.up.railway.app/private-previews/2d32be7dda6d361dd89ffdfd/stonehurst/
- Containment: `<meta name="robots" content="noindex, nofollow">`, `previews/` is listed in `.railwayignore` so it never uploads to Railway, and `server.js` returns a 404 for every `/previews/*` path even if it did. Not pushed to GitHub. Local only.
- Preview locally: `cd ~/projects/insert && python3 -m http.server 4821` then open `http://localhost:4821/previews/stonehurst/index.html`.

## Source pages read (all HTTP 200 on 2026-10-16)

| Page | URL |
|---|---|
| Home | https://www.thestonehurst.com/ |
| Our History | https://www.thestonehurst.com/our-history |
| Greenhouse | https://www.thestonehurst.com/greenhouse-los-angeles |
| Barn | https://www.thestonehurst.com/rustic-barn-los-angeles |
| Bamboo Garden | https://www.thestonehurst.com/the-gardens-gallery |
| Flower Garden | https://www.thestonehurst.com/copy-of-bamboo-garden |
| Bungalow | https://www.thestonehurst.com/copy-of-greenhouse-1 |
| FAQ | https://www.thestonehurst.com/faq |
| Privacy ("about-4") | https://www.thestonehurst.com/about-4 |

Platform: Wix (meta generator "Wix.com Website Builder"). Homepage HTML alone is 640 KB before any media.

## Facts used on the page (all from the venue's own site)

- 9-acre garden property in Shadow Hills, Los Angeles County, "on the corner of Sunland and Stonehurst Ave" (Our History). Footer on the live site says only "SHADOW HILLS, CA".
- "6 stunning spaces": a full functioning greenhouse, a historical barn, cactus, bamboo and flower gardens, a grand terrace with views of the mini desert garden, and a private mid-century bungalow (Home).
- Greenhouse: indoor ceremony or reception, floor-to-ceiling glass, existing beams for decor and floral hanging, holds up to 200, HVAC climate controlled.
- Barn: one of the oldest structures in this part of Los Angeles County, greets you on entry; holds up to 150; original wood; 3 cascading chandeliers; natural lighting. Hosted some of the original Boy Scout meetings in the area dating to 1907; today's doors were reclaimed from the original horse stalls in 2015 (Our History).
- Bamboo Garden: small intimate ceremony, cocktail hour, pre-ceremony photos; up to 60 (ceremony) / 120 (cocktail); three types of bamboo; private and intimate.
- Flower Garden: towering South American fig tree; ceremony, cocktail hour or private party; up to 175 (ceremony / cocktail); greenery all around.
- Bungalow: original to the property, two rooms plus a large open communal room; reserved for the couple, green room, or pre-approved special events; 1-15 guests.
- Terrace: "grand terrace with endless views of our mini desert garden" (Home). No capacity or page exists for it; the mock shows it without a number.
- History: name comes from the street and the hand-laid stone work on the main pathways; Joe Stromei (owner of Aaardvark's Odd Ark) planted most of the vegetation by hand; his name is carved into a greenhouse beam, which still has its original beams. 500 chickens, 200 canaries. The history text is credited to the Shadow Hills Property Owners Association.
- FAQ (verbatim answers paraphrased): max 200 guests; one event per day, private; private events may use 3-4 of the 6 spaces unless otherwise approved; standard 12-hour rental including breakdown, gates open 12 PM, event ends 10 PM, breakdown 10 PM-12 AM; a minimum partial-service planner is required; valet, site manager, luxe restrooms and security are included; filming and photoshoot inquiries go by email.
- Hours: by appointment only. Contact: thestonehurst@gmail.com (the only contact on the site). Copyright "Stonehurst, LLC".
- "featured in" row on the live homepage shows logos for Junebug Weddings, Loverly, Style Me Pretty, Vogue India, The Knot, Zola, Wedding Chicks, PartySlate. The mock lists these as plain text names (no logos copied).
- Weddings, filming and private events are the three stated uses.

## What's weak on the current site

1. **Gmail-only contact and no phone.** `thestonehurst@gmail.com` is the only way in. There is no phone number anywhere on the site, and no domain email.
2. **"Opening hours: by Appointment Only"** with no way to make the appointment. Tours are not bookable; a couple emails and waits.
3. **No pricing, packages, or guide.** Nothing tells a couple what a Saturday costs or how to get that information. (Zola publicly lists a starting price; the site itself says nothing. The mock does not print any price.)
4. **Inquiry form is generic and buried.** Eight fields at the bottom of the page, including "How did you find us?" and a free-text message; no date-availability feedback, no auto-reply beyond a static thank-you line.
5. **No clear journey.** The homepage is hero → paragraph → five alternating photo tiles with "VIEW GALLERY" → form. Capacities, inclusions, rental hours and the planner requirement are all hidden on the FAQ page.
6. **Dated layout and weight.** Wix template, 640 KB of HTML before images, uppercase DIN headings with a semi-transparent box over the hero, 320px fixed-width mobile layout (`viewport width=320`), grey #ededee page background.
7. **Housekeeping.** Gallery URLs are `copy-of-bamboo-garden` (Flower Garden) and `copy-of-greenhouse-1` (Bungalow); the Privacy page is at `/about-4` and still contains unfilled template brackets like "[website/mobile app]" and "[List your company's payment processors…]"; the body copy has "cactus. bamboo, and flower gardens"; page titles alternate between "Stonehurst Venue" and "Stonehurst Website". The terrace and cactus garden are named but have no page or capacity.
8. **Geography line.** The site says the property is "nestled between downtown Los Angeles and West Hollywood". Shadow Hills is in the northeast San Fernando Valley, so the mock drops that line and says "Shadow Hills, Los Angeles County" instead. Flag for the venue.

## What we kept

- Their name, logo spirit (a high-contrast serif wordmark; the mock uses Bodoni Moda as a stand-in and does not copy the logo file), the three-part positioning "Weddings · Filming · Private events", the exact space names and the "6 spaces / 9 acres" framing.
- Their palette: warm off-white, charcoal, and the terracotta/clay accent (`rgb(160,88,65)` in their Wix theme) plus the blush and deep-teal secondary colours from the same theme, used sparingly.
- All capacities, inclusions, hours and rules exactly as stated. All FAQ answers are from their FAQ page.
- Contact on the page is `hello@thestonehurst.com`, a **placeholder** domain-style address that does not exist yet (the brief asked for no Gmail on the page). The venue's real, current contact is `thestonehurst@gmail.com`. Swap before any real use.

## What we changed and why

- **Hero with "Check your date".** Date + guest count + email/phone, three fields, submits client-side only and shows a realistic hold confirmation ("held for 24 hours, text in under a minute"). This replaces the eight-field form as the first ask. Nothing is sent anywhere; there is no network call.
- **Property story** using only Our History wording.
- **Spaces grid** with capacity chips and "what it's for" lines taken from each space page, including the terrace (no number) and cactus garden (mentioned in the terrace card, no number).
- **"Plan your day" band**: Inquire → Tour → Hold the date, which is the automation Insert would wire up.
- **Tour scheduler**: a static calendar + time-slot picker with a confirmation state. Slots are illustrative; the venue's real availability would drive it.
- **Pricing guide capture**: email field, instant "guide sent" state, no price shown.
- **FAQ** with the seven real answers and a "what's included / hours at a glance" strip pulled from the same answers.
- **Footer** with Shadow Hills, "Corner of Sunland & Stonehurst Ave" (from Our History; the site does not print a street number), the placeholder domain email above, and no phone (the site has none). Discreet "Concept preview by Insert · photography © The Stonehurst · not affiliated with the venue" chip.

## Revision 2 (2026-10-16, afternoon): readability + real imagery

Dillon's notes on v1: "the font against the background is a bit hard to read" and "make sure you are using real imagery from their site if possible."

### Readability

Measured with the contrast walker in `scripts/verify-stonehurst-preview.py` (see Verification). v1 numbers were measured by re-running the same walker against commit 48c0015.

| Text | v1 min ratio (worst pixel, either viewport) | v2 min ratio | Change |
|---|---|---|---|
| Hero kicker (white on photo) | 1.00 | 7.26 | two-layer scrim (vertical + left-anchored), kicker pure white, 11.5→12.5px |
| Hero headline (Bodoni, 43–88px) | 1.00 | 6.85 | scrim; mobile copy pushed lower into the dark band |
| Hero sub-copy / meta | 1.59 | ≥ 7.3 | weight 300→400, full white instead of 72–88% white, scrim |
| Captions / fine print (`--ink-faint`) | 3.43 (#8a8176) | ≥ 7.5 (#4f4740) | darker token, 12→13.5px |
| Clay kicker / labels (`--clay`) | 4.86 (#9a5039) | ≥ 7.7 (#733425) | darker text clay; original clay kept for dots, focus rings, button fills |
| Input placeholders | 2.75 (#a39b90) | 7.3 (#5c544c) | darker, opacity 1 |
| Calendar unavailable days | 1.24 (#c3bbb0 + strike-through) | ≥ 7.5 | muted weight on a paper-2 tile, no strike |
| Plan band small copy (78% white on teal) | 6.2 | ≥ 10 | solid #ece5dc / #e9cfc5 instead of alpha text |
| Filming band copy (72% paper on ink) | ≈ 8 | ≥ 11 | solid #e9e3db |

v1 numbers come from running the same walker against `git archive 48c0015` (the 1.00s are white text over white sky / white chair cushions with a 6–22% scrim). 

Also: body 17px/300 → 17.5px/400 (17px on mobile, was 16), nav links 500 weight, chips/labels +1px, story frame line moved onto a wrapper so it no longer crosses the caption, header backdrop 86%→94%.

Result: 621 text nodes measured across both viewports and all states (default, hover, open mobile menu, validation errors, three confirmations). Lowest small-text ratio 7.26:1, lowest large-text ratio 6.85:1. WCAG AA floor is 4.5 / 3.

### Real imagery

Every photo on the page is now the venue's own, pulled from the untransformed Wix originals (`https://static.wixstatic.com/media/<id>` with no `/v1/fill/` transform returns the uploaded file). Crawl: all 12 pages in `pages-sitemap.xml` fetched with curl; 86 unique media ids found (78 photos ≥ 800px after dropping logos and press badges). Originals were reviewed on contact sheets and the best per section picked; originals live in `/tmp/sh/orig` (not committed, ~380 MB). `img/real/` keeps a ≤2400px JPEG of each chosen crop plus `manifest.json`.

| Use | Source (original) | Native px | Crop px | WebP widths served | Found on |
|---|---|---|---|---|---|
| `hero` | https://static.wixstatic.com/media/41b656_c53749f9cc334a58bca20dc46128b8ca~mv2.jpg | 11648x8736 | 11648x8736 | 1200, 1800, 2400 | /copy-of-bamboo-garden (Flower Garden page) |
| `greenhouse` | https://static.wixstatic.com/media/41b656_faf7efa119644297a7e9df7107b7a1e9~mv2.jpg | 11648x8736 | 11648x8736 | 800, 1200, 1800 | /greenhouse-los-angeles |
| `barn` | https://static.wixstatic.com/media/41b656_93561ad4073f4c769a70ce03e4aa63c5~mv2.jpg | 5685x3790 | 5053x3790 | 800, 1200, 1800 | / (home) |
| `flower` | https://static.wixstatic.com/media/41b656_1fbdb1ce5c8d4febab7d0a4987605e06~mv2.jpg | 5097x6596 | 5097x3823 | 800, 1200, 1800 | /copy-of-bamboo-garden (Flower Garden page) |
| `bamboo` | https://static.wixstatic.com/media/41b656_dda286a194e34c70addb74f1575a8432~mv2.png | 4636x6000 | 4636x3477 | 800, 1200, 1800 | /the-gardens-gallery (Bamboo Garden page) |
| `terrace` | https://static.wixstatic.com/media/41b656_13d8c023d33b4bdba5aa9ff0d7a4d612~mv2.jpg | 1600x1200 | 1600x1200 | 800, 1200, 1600 | /grand-terrace-gallery |
| `bungalow` | https://static.wixstatic.com/media/41b656_3c0747cbc41349d580c09bae9a3b173a~mv2.jpg | 5246x3497 | 4663x3497 | 800, 1200, 1800 | / (home) |
| `reception` | https://static.wixstatic.com/media/41b656_3d58f3b1103849e888d99cc30eae9cfa~mv2.jpg | 3755x5644 | 3755x2816 | 800, 1200, 1800 | /greenhouse-los-angeles |
| `stonepath` | https://static.wixstatic.com/media/41b656_fad86b73f0eb42b5a660be4a9f5604eb~mv2.jpeg | 1152x1618 | 1152x1536 | 600, 900, 1152 | /our-history |

Pipeline: `scripts/convert-stonehurst-real.py` (Pillow, LANCZOS, WebP q82 stepping down to stay near 300 KB per file; the 2400px hero is 520 KB). Nothing is upscaled: a width is only written when it is ≤ the crop width, and the verifier checks each rendered image against the manifest (served width ≥ CSS width × DPR, capped at 1.5× on desktop; CSS width × that factor ≤ native width).

Limited-resolution sources and how the layout handles them:
- **Terrace** (1600×1200): the only wide view of the terrace; the 4:3 card is ≤ 566 CSS px on desktop (≤ 849 device px at 1.5×) and 350 px on mobile (700 at 2×).
- **Stone path** (1152×1618): the one photo of the hand-laid stone work; moved to a portrait 3:4 frame capped at 440 px (660 device px at 1.5×; 780 at mobile 2×) and given a caption. The `detail` tablescape it replaced was generated.

Sections with no real photo: none. All eight generated images (`hero`, `detail`, `greenhouse`, `barn`, `flower-garden`, `bamboo`, `terrace`, `bungalow`) and the "Illustrative imagery" chip are gone. The page footer now reads "photography © The Stonehurst".

Note on sourcing: `copy-of-bamboo-garden` is the Flower Garden gallery and `the-gardens-gallery` is the Bamboo Garden gallery on the live site (the URL slugs are swapped); the picks above follow what each photo actually shows.

## Verification (2026-10-16, revision 2)

`scripts/verify-stonehurst-preview.py` (Playwright Chromium, numpy, Pillow) against `python3 -m http.server 4821`:

- 1440×900 and 390×844, both at 2× device pixel ratio: no horizontal overflow; no console errors, page errors or failed requests; only off-origin requests are Google Fonts.
- Both web fonts load; every `<img>` has alt text, loads, is sharp for its rendered size and is never displayed beyond its native source width (manifest-checked).
- Contrast walker: every visible text node (plus `::placeholder`) is paired with a screenshot taken with all text made transparent (transitions frozen), so the real background under each glyph line (photo + scrim, gradients, translucent header, tinted tiles) is sampled per pixel; the minimum ratio per node is checked against 4.5:1 (3:1 for ≥24px). States covered: default, ten hover targets (forced via CDP `CSS.forcePseudoState`), open mobile menu, both validation errors, and all three confirmations. Bodies of closed `<details>` are skipped (not rendered). Result: 0 failures, 0 nodes under 7:1 for small text.
- Check-your-date, scheduler and pricing-guide flows: validation error → valid submit → confirmation text checked → reset, as in v1.
- Screenshots in `shots/`: `desktop.png` (2880×18342), `mobile.png` (780×25330), plus `-hero`, `-spaces`, `-tour`, `-date-confirm`, `-tour-confirm` crops; `contrast.json` has every measured node.

## Caveats

- Terrace capacity, phone number and a street number are unknown; the mock does not invent them.
- "Featured in" names are reproduced as text from the live homepage's logo row; verify each placement before any public use.
- Tour slots, the 24-hour hold and the one-minute text are product promises for the Insert automation, not current venue policy.
- The photos are the venue's own, used only on this private unlisted preview so the venue can see its own property; they must not be reused on any public Insert page.
- The hero scrim is deep (up to 92% at the foot of the photo, heavier on mobile where the copy stacks over the image) because the verifier takes the darkest pixel under each line; a lighter treatment would need the copy moved off the photo.
- Zola's public "from $11,500" and review counts are deliberately absent.
