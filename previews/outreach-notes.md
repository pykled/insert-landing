# Venue website outreach notes

Research date: 2026-10-01. All sites fetched live and returned HTTP 200. Nobody has been contacted.
Mock built: `previews/lindley-scott-house/index.html` (local only, noindex, excluded from Railway via `.railwayignore` and a 404 route in `server.js`).

## Candidates

### 1. Lindley-Scott House, Azusa (San Gabriel Valley) — CHOSEN
- URL: https://lindleyscotthouse.com/ (WordPress, Salient theme)
- What's wrong:
  - Homepage body copy is a single 449-character paragraph; the `/weddings/` page is one sentence.
  - No inquiry form on the homepage or weddings page. The only form there is site search; the real form is buried on `/contact-us/`.
  - Viewport meta disables pinch-zoom (`maximum-scale=1, user-scalable=0`).
  - No pricing, packages, or capacity on the information page; nothing tells a couple what a wedding includes.
  - Contact email is a Gmail address, not a domain address.
- Public contact: (626) 334-5215, (626) 665-4235, historicallindleyscotthouse@gmail.com. No owner name listed on the site.
- Why chosen: strongest product of the three (1911 estate, 4 acres, 200-seat Carriage House, weddings since 1978, one event per day) with the thinnest site, so the before/after gap is the most visible. It is also in the priority SGV area.

### 2. Greenspot Farms, Mentone (Inland Empire)
- URL: https://www.greenspotfarms.com/wedding-venue (Duda builder)
- What's wrong:
  - 63 deprecated `<font>` tags on the wedding page with hard-coded sizes; mixed typography.
  - Footer still contains the builder placeholder `mailto:mymail@mailservice.com`.
  - Site is Christmas-tree-farm first; weddings are one tab among nine, and the page title is about Christmas trees.
  - No inquiry form with date or guest count, just an email-capture box. Copy is keyword-stuffed.
  - No capacity published.
- Public contact: 10133 Ward Way, Mentone, CA 92359; (909) 583-1257; katiebuoye9@gmail.com (owner name not stated).

### 3. Elegante Ranch, Riverside (Inland Empire)
- URL: https://eleganteranch.com/ (GoDaddy Website Builder 8)
- What's wrong:
  - Homepage has about 386 characters of text; tile labels render as duplicated "CORPORATE / SOCIAL" strings.
  - Package page repeats the same lines three times and shows no prices despite being the "package guide".
  - No email address anywhere on the site; two different ZIP codes and no street number.
  - Hours say closed Saturday and Sunday, for a wedding venue.
- Public contact: (909) 559-1561; Palm Road, Riverside, CA 92504. No owner name, no email.

### Alternate (not top 3): Hurst Ranch, West Covina
https://www.hurstranch.com/ — WordPress 6.2.8, Yahoo email, weddings buried under "Site Rental", bookings routed to an outside caterer. Excluded because it is foundation-run with a board, not owner-operated. General Manager listed as Elmer Berdugo.

## Draft cold email (Lindley-Scott House)

Subject: A quick redesign sketch of lindleyscotthouse.com

Hi there,

I'm Dillon, I run Insert, a small studio in the San Gabriel Valley that builds websites and booking automations for wedding venues.

I came across the Lindley-Scott House while researching venues near Pasadena and the property is remarkable: a 1911 estate, four acres of gardens, a 200-seat Carriage House, and one event per day. The website undersells it. The weddings page is a single sentence, there is no way for a couple to check a date or request a tour from the homepage, and the contact form is three clicks deep.

I put together a one-page concept of what the homepage could look like, using only the text already on your site, with a date-check form at the top and a tour button that confirms instantly. It took me an afternoon and there is no obligation attached. If you'd like to see it, reply and I'll send the link, or I can walk you through it in 15 minutes.

Either way, congratulations on 48 years of weddings in Azusa.

Dillon
Insert · useinsert.com/venues

## Needs Dillon's decision
- Whether to send the email above, and from which address.
- Whether to host the mock on a private URL for the send (currently local only and blocked on Railway).
- The mock uses placeholder image blocks; swap in the venue's own photos only with their permission.
