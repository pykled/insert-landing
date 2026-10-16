# The Stonehurst — homepage concept notes

Private spec mock. Built 2026-10-16 by Insert as an unsolicited "here's what your site could be" preview. Nothing has been sent to the venue. Nobody at the venue has been contacted.

- Mock: `previews/stonehurst/index.html` (+ `img/` WebP assets, `shots/` screenshots)
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
- **Footer** with Shadow Hills, "Corner of Sunland & Stonehurst Ave" (from Our History; the site does not print a street number), the placeholder domain email above, and no phone (the site has none). Discreet "Concept preview by Insert · illustrative imagery · not affiliated with the venue" chip.

## Verification (2026-10-16)

`scripts/verify-stonehurst-preview.py` (Playwright, Chromium) against `python3 -m http.server 4821`:

- 1440×900 desktop at 1x and 390×844 mobile at 2x: no horizontal overflow (scrollWidth equals innerWidth on both).
- Both web fonts load; every image has alt text, loads, and the chosen srcset candidate is at least 90% of the rendered width × DPR.
- Check-your-date: empty submit shows a validation error; a valid submit shows the 24-hour-hold confirmation with the formatted date, guest count and contact; "Check another date" resets.
- Scheduler: next month → first available day → first slot → "Book this tour" shows the confirmation; "Choose a different time" resets.
- Pricing guide: invalid email is rejected; valid email shows "Guide sent".
- No console errors or page errors; the only off-localhost requests are Google Fonts. No form posts anywhere.
- Screenshots in `shots/`: `desktop.png`, `mobile.png` (full page), plus `-hero`, `-spaces`, `-tour`, `-date-confirm`, `-tour-confirm` crops for each.

## Placeholders for the venue to fill (marked here, not on the page)

The page's FAQ contains only answers that exist on the live site. These questions are *not* answered anywhere on the site and are left out of the page rather than guessed; the venue should supply them:

- Pricing or starting rates (the page offers a guide capture instead).
- Catering: preferred/required vendors, outside catering, bar policy.
- Parking capacity and valet details beyond "valet included".
- Noise / amplified music cutoff beyond the 10 PM event end.
- Rain plan (the greenhouse is implied as the indoor option but not stated as such).
- Accessibility of the gardens and restrooms.
- Terrace and cactus garden capacities.
- A public phone number.

## Illustrative imagery

Every photo on the mock is AI-generated (Gemini `gemini-3.1-flash-image-preview`, native 2K, no people/faces/text) from `scripts/generate-stonehurst-images.mjs`, then converted to WebP at 1200/1800/2400 widths (never upscaled, each file under 250 KB) by `scripts/convert-stonehurst-images.py`. None of the venue's own photos were downloaded, hotlinked or copied. The page carries an unobtrusive "Illustrative imagery" caption chip; a real build would use the venue's photography.

## Caveats

- Terrace capacity, phone number and a street number are unknown; the mock does not invent them.
- "Featured in" names are reproduced as text from the live homepage's logo row; verify each placement before any public use.
- Tour slots, the 24-hour hold and the one-minute text are product promises for the Insert automation, not current venue policy.
- Zola's public "from $11,500" and review counts are deliberately absent.
