# Wedding-venue websites: market, conversion, and local SEO evidence

Compiled 2026-10-20. Every URL below was fetched during this pass; HTTP status observed is listed in the final section. Strength: STRONG = primary source with stated method or normative spec; MEDIUM = primary source, method not stated, or secondary report of a primary study; WEAK = vendor blog, unknown method, or undated.

## Top 12 decision-relevant facts

| # | Fact | Number | Source | Strength |
|---|------|--------|--------|----------|
| 1 | Pricing is the #1 factor couples use to decide which vendors to contact | 77-78% | https://pros.weddingpro.com/?p=35190 ; https://www.theknotww.com/press-releases/the-knot-worldwide-announces-new-products-to-help-wedding-professionals-get-discovered-and-connect-with-more-couples | MEDIUM (TKWW survey, n not stated) |
| 2 | Venues that showed rates on their Knot storefront got more couple replies in a TKWW test | +25% response rate | https://pros.weddingpro.com/?p=35190 | MEDIUM (vendor-run test) |
| 3 | Couples inquire with ~5 venues and tour ~4 | 5 / 4 | https://pros.weddingpro.com/report/what-couples-really-want-from-their-wedding-venues | MEDIUM (781-couple Venue Selection Study + 11,646 Real Weddings) |
| 4 | ~80% start venue research within 2 months of engagement; avg engagement 15 months | 80% / 15 mo | same as #3 and https://pros.weddingpro.com/report/the-knot-real-weddings-venue-report/ | MEDIUM |
| 5 | Venue takes nearly 40% of the budget; avg venue spend $12,200 (2024 weddings) | ~40% / $12,200 | https://pros.weddingpro.com/report/the-knot-real-weddings-venue-report/ ; https://www.foxbusiness.com/lifestyle/wedding-season-here-how-much-one-cost-2025 | MEDIUM |
| 6 | Avg wedding cost 2025 (10,474 couples); 52% cite responsiveness as a trust factor | $34,000 / 52% | https://www.theknotww.com/press-releases/the-knot-worldwide-unveils-2026-real-weddings-study | STRONG (n stated) |
| 7 | Share of wedding planning done on phone/tablet | 46% (2020) ; 44% (2025) | https://www.theknotww.com/press-releases/weddingwire2020newlywedreport ; https://pros.weddingpro.com/report/hello-to-hired-your-guide-to-lead-replies/ | MEDIUM/STRONG (2020: n=25,000) |
| 8 | Replying to a lead in under 3 hours makes couples 2.2x more likely to reply | 2.2x | https://pros.weddingpro.com/report/hello-to-hired-your-guide-to-lead-replies/ | MEDIUM (TKWW platform data, method not stated) |
| 9 | 53% of mobile visits abandoned if load exceeds 3 s (Google, 2017, all industries) | 53% / 3 s | https://blog.amp.dev/2017/02/28/new-industry-benchmarks-for-mobile-page-speed/ | MEDIUM (dated, non-wedding) |
| 10 | Core Web Vitals "good" thresholds at p75 | LCP 2.5 s, INP 200 ms, CLS 0.1 | https://web.dev/articles/vitals | STRONG |
| 11 | WCAG 2.2 AA: text contrast 4.5:1, UI/graphics 3:1, targets 24x24 CSS px, focus visible | spec | https://www.w3.org/TR/WCAG22/ | STRONG |
| 12 | FAQ rich results now only for "well-known, authoritative government and health websites" | since Aug 2023 | https://developers.google.com/search/blog/2023/08/howto-faq-changes | STRONG |

---

## Part 1. Builders and templates the venue market uses

### Showit (the dominant "wedding-pro" platform)
- Pricing: $27/mo (site only), $34/mo with starter blog, $49/mo with advanced WordPress blog; higher tiers $79-$149 for 100K-200K visits (https://showit.com/pricing/). Templates are bought separately from third-party designers, so a venue typically pays $400-$1,500 for the design plus the subscription.
- Who uses it: wedding photographers first, then planners, florists and venues. Showit's own March 2026 roundup of "event professional" templates lists ten planner/designer templates (Kinsley Lane, Bliss Weddings, Fete Events, Lavender Lane, Clover, etc.) and describes them with the same vocabulary: "fine-art, editorial", "magazine-worthy", "gallery-forward", "testimonial sliders" (https://showit.com/website-tips/showits-top-event-professional-website-templates/).
- Venue-specific templates are rare. The clearest example is **Honeysuckle House** by Alex Collier Design: $900 (or 4 x $270); pages = Home, About, Weddings, Gallery, Individual Gallery, Contact, Coming Soon, Links, 404, Blog; large hero imagery, testimonials on multiple pages, "calls to action that prompt couples to schedule a tour" (https://alexcollierdesign.com/honeysuckle-house). It was the only venue-targeted template Andrea Shah could name in her 2025 roundup of Showit templates for wedding pros (https://andreashah.com/the-5-best-showit-website-templates-for-wedding-pros/).
- Multi-purpose templates that list venues as a target: Elizabeth McCravy's **Alice** and **Taylor**, each $797 (or 4 x $247), with Home / About / Services / Portfolio / Contact / two landing pages / "Call Scheduler" page / blog, and a contact form included (https://elizabethmccravy.com/alice, https://elizabethmccravy.com/taylor).
- Tonic Site Shop: cocktail-named templates (Aperol Spritz, Martini, Gin & Tonic...), six core pages "home, about, services, portfolio, contact, and opt-in", up to 15 pages, "ceaseless CTAs", 7,500+ customers; Aperol Spritz listed at $1,525 with licensed Jen Wagner fonts and a "dedicated proposal page" (https://tonicsiteshop.com/shop/showit-websites-templates/gin-and-tonic ; https://andreashah.com/the-5-best-showit-website-templates-for-wedding-pros/). No venue-specific product on the shop page (https://tonicsiteshop.com/shop-page).
- Davey & Krista: templates positioned on SEO; every template ships "inquiry forms", editable titles, heading structure, gallery layouts (https://daveyandkrista.com/showit-templates/). Their font guide is the clearest statement of the industry's typographic default: "The 3-Font Formula" = one serif for headings, one sans for body/nav, one script "used sparingly" for logo text, quotes and highlights; worked example for a wedding-planner site = Editor's Note (serif) + Work Sans (sans) + California Palms (script); free fallbacks Playfair Display, Cormorant Garamond, Lato, DM Sans, Allura, Great Vibes (https://daveyandkrista.com/?p=84437).
- With Grace and Gold: 13 templates, all $399, described as "editorial", "romantic", "refined", "luxury", with "serif typography" called out (https://www.withgraceandgold.com/shop).
- Northfolk: full templates $697-$997 (Heirloom, Cupertino, Sunday), add-ons $27-$397 (https://northfolk.co/).
- Shop ecosystem: Salted Pages lists roughly a dozen Showit shops (Northfolk, Garden of Muses, Seventh Made, Ashley Ferreira, Saffron Avenue, Story Muse, With Grace and Gold, Revel West, Tonic, Jennifer Carfora, Vanilla and Oak, Buffalo Collective) and describes them with overlapping adjectives ("European elegance", "editorial and minimal", "impact and romance") (https://saltedpages.com/blog/showit-template-shops/).

### Squarespace
- Plans: Basic $19, Core $29, Plus $49, Advanced $99 per month billed annually (https://www.squarespace.com/pricing). Squarespace's "Weddings" template topic targets couples' day-of sites, not venue businesses; venues use general portfolio templates.
- Example venue: Lily Farm House (Western Australia) on the premium **Lora** template: full-width featured image hero + one-line description + "download the wedding guide" CTA, then About, Weddings, Gallery; black/white with grey footer; "alternating split sections" (https://www.applet.studio/squarespace-showcase/squarespace-website-for-wedding-venue).
- Applet Studio's roundup of 20 wedding-pro Squarespace sites (incl. Greystone Hall, a venue) summarises the common skeleton: video or full-bleed carousel hero -> services -> portfolio/gallery -> testimonials -> blog/CTA -> footer with newsletter; "delicate", handwritten typefaces; muted/earthy palettes; some sites add availability checkers (https://www.applet.studio/blog/squarespace-wedding-websites). WEAK (agency showcase) but consistent with the Showit evidence.

### WordPress (Flothemes, Elementor, Kadence)
- Flothemes was acquired by Pixieset in August 2021 and now sits inside the "Pixieset Family"; it still sells photographer-oriented WordPress themes plus the "Pronto" all-in-one (https://flothemes.com/ ; https://slrlounge.com/why-did-pixieset-acquire-flothemes-interview-with-the-founders/). No venue positioning.
- Elegant Themes' January 2025 wedding-theme roundup: ChicLuxe $149 (Elementor), Delphine $149 (Elementor Pro), Maeve $149 (Elementor Pro), Qi $69/yr, Zakra $69/yr, Blossom Wedding Pro $59/yr, Divi $89/yr. Elementor dominates (6 of 10); none is venue-specific (https://www.elegantthemes.com/blog/wordpress/best-wedding-wordpress-themes).
- "Fleura Wedding" (Gumroad) is marketed for venues and event spaces on Elementor/Kadence/Gutenberg, but the product page exposes almost no detail (https://rublyjackie.gumroad.com/l/fleurawedding). WEAK.

### Pixieset Website, Format, Webflow
- Pixieset Website: Free (15 pages, 100 photos), Plus $12/mo, Pro $18/mo annual; built for photographers (https://pixieset.com/pricing-website/).
- Format: Basic $10, Pro $12, Pro Plus $15 per month annual; portfolio builder for photographers and other creatives, no venue features (https://www.format.com/pricing).
- Webflow: searching the template marketplace for "wedding venue" returns ~21 templates, almost all couple-wedding or photographer sites (Alyra, Belle Amour, LoveBond, Vows, Wedoora...). **Marrymint** ($29) is the one that names venues: sections for services, galleries, timelines, RSVP; pitched for "planners, venues, and studios" and "farm house weddings" (https://webflow.com/templates/search/wedding-venue ; https://templates.webflow.com/html/marrymint-website-template).

### Why venue sites converge on one look
1. Shared template families: the same dozen Showit shops sell to photographers, planners and venues alike, and most venue-usable templates are photographer templates with the copy swapped (McCravy's Alice/Taylor list "wedding venues" tenth in a list that starts with photographers).
2. Same stock structure: every shop ships the same page set (Home, About, Services/Weddings, Portfolio/Gallery, Contact + inquiry form, optional blog) and the same homepage order (hero image -> intro -> services -> gallery -> testimonials -> CTA). Tonic's "six core pages" and Honeysuckle House's page list are near-identical.
3. Same font trio: the serif + sans + script formula is taught explicitly by the designers who sell the templates (D&K), and premium shops advertise licensed display serifs and scripts as a selling point (Tonic/Jen Wagner).
4. Same imagery: template demos are art-directed with editorial wedding photography, and venues populate them with their own photographers' work shot in the same style, so the hero and gallery blocks read identically across sites.
5. Marketplace incentives: Showit's own curation and third-party roundups reward "editorial", "fine-art", "luxury" descriptors; shops that deviate have less distribution. Even a template seller's April 2026 piece on why Showit templates are not selling blames lack of audience specificity rather than oversupply, which is itself evidence that the shops see sameness as the default (https://withgraceandgold.com/2026/04/showit-templates-arent-selling/, WEAK).

---

## Part 2. Conversion and UX for venue sites

### Inquiry form length
- HubSpot (Dan Zarrella, 40,000+ customer landing pages): conversion "decrease[s] slightly, but not as steeply as I expected" as fields increase; "very little decrease" for single-line text fields; "multiple textareas have a powerful depressing effect"; multiple dropdowns associated with lower conversion (https://blog.hubspot.com/blog/tabid/6307/bid/6746/which-types-of-form-fields-lower-landing-page-conversions.aspx). MEDIUM: large sample, but B2B content-offer forms, not high-intent venue inquiries, and the page's original date is obscured by an "updated 2025" stamp.
- Venture Harbour's round-up collects the usual case studies (Marketo/MarketingExperiments, Unbounce/ConversionXL label test, a 30-question multi-step form converting at 53%) without methods (https://ventureharbour.com/how-form-length-impacts-conversion-rates/). WEAK. Widely repeated "11% per extra field" and Venngage figures could not be traced to a primary page in this pass; treat as unverified.
- Applicability: a venue inquiry is high intent and the venue genuinely needs date, guest count and budget. The defensible reading of the evidence is: keep required fields to name, email, phone, date (or season), guest count; avoid multiple free-text areas and dropdowns; move "tell us about your day" to optional or a second step.

### Availability / date-check and pricing transparency
- TKWW (The Knot + WeddingWire) now lets vendors show "starting price, what couples usually spend and displaying packages — and availability" on storefronts; vendors who add them see "nearly twice as many two-way conversations" (https://www.theknotww.com/press-releases/the-knot-worldwide-announces-new-products-to-help-wedding-professionals-get-discovered-and-connect-with-more-couples). WeddingPro's guidance: "at a minimum" show a starting price, a "couples usually spend" figure, and packages; venues showing rates saw +25% couple response rate in a test; 78% of couples say pricing is the #1 factor for deciding whom to contact; 60% raise their budget at least once (https://pros.weddingpro.com/?p=35190). MEDIUM.
- Top three venue selection factors per TKWW's Venue Selection Study: price, capacity for ceremony + reception, availability (https://pros.weddingpro.com/report/what-couples-really-want-from-their-wedding-venues). A date-check widget addresses the third directly; no public A/B data on date checkers was found.

### Tour booking tools (what each offers venues)
- HoneyBook: Starter $29, Essentials $49, Premium $109 /mo annual; lead forms on all tiers (2 / 10 / unlimited); the Scheduler ("set and share your availability so clients can book your time") is Essentials and up (https://www.honeybook.com/pricing).
- Calendly: Free; Standard $10, Teams $16 per seat/mo annual; embeddable with colour customisation and custom confirmation redirects (https://calendly.com/pricing). Generic, not venue-aware.
- Tripleseat: inquiry inbox, website lead form, proposals/contracts/BEOs, payments, 2D/3D floor plans; 20,000+ venues; pricing not published (https://www.tripleseat.com/).
- Perfect Venue: Professional $199, Premium $299 /mo per location (annual); inquiry capture, AI reply, proposals/BEOs, Stripe deposits, calendar (https://www.perfectvenue.com/).
- Planning Pod: lead-capture forms, booking calendar, BEOs, floor plans, e-sign contracts; claims "64% booking growth after switching" (unverified marketing) (https://www.planningpod.com/).
- Releventful: "Lead capture, Sales pipeline, Follow-up, Tours and appointments, Proposals", room-conflict detection, payment schedules; pricing by demo (https://www.releventful.com/).
- Weven: weven.co now 301-redirects to theknot.com; Weven "was acquired by The Knot" (Boston Seed portfolio note, undated) (https://bostonseed.com/?p=11938). Treat as absorbed into TKWW.
- Tock: the private-events page is behind a Cloudflare challenge (403) and could not be read; no claims made.

### Response time
- TKWW/WeddingPro 2025: replying in under 3 hours makes couples "2.2X more likely to reply"; ending with an open-ended question 2.7x; couples contact 5 vendors per category; "over 9 million leads sent to pros every year" (https://pros.weddingpro.com/report/hello-to-hired-your-guide-to-lead-replies/). MEDIUM (platform data, no method). The 2026 Real Weddings Study adds that 52% of couples name responsiveness as a trust factor and 37% contacted more vendors than planned to find budget fits (https://www.theknotww.com/press-releases/the-knot-worldwide-unveils-2026-real-weddings-study).
- Not wedding-specific: Oldroyd, McElheran and Elkington, "The Short Life of Online Sales Leads", HBR March 2011 (https://hbr.org/2011/03/the-short-life-of-online-sales-leads ; https://scholarsarchive.byu.edu/facpub/9711/). The commonly quoted figures (2,241 firms audited; responding within an hour ~7x more likely to qualify the lead than waiting a second hour, 60x vs 24 h) come from the article body, which is paywalled; this pass verified the article's existence and authorship only. MEDIUM, and it is B2B sales, not couples.

### Speed
- Core Web Vitals: LCP <= 2.5 s, INP <= 200 ms, CLS <= 0.1, assessed at the 75th percentile of page loads, mobile and desktop separately; INP became stable in 2024 (https://web.dev/articles/vitals). STRONG.
- Google (Daniel An, 2017): average mobile landing page fully loads in 22 s; "53% of mobile site visitors leave a page that takes longer than three seconds to load" (https://blog.amp.dev/2017/02/28/new-industry-benchmarks-for-mobile-page-speed/ ; PDF https://www.thinkwithgoogle.com/_qs/documents/57/mobile-page-speed-new-industry-benchmarks.pdf). MEDIUM, dated, cross-industry. Image-heavy venue templates are the obvious risk.

### Couple behaviour and mobile share
- WeddingWire 2020 Newlywed Report (n > 25,000): 46% of planning on mobile; 88% online; 15 vendors hired; 131 guests; 68% started planning before engagement (https://www.theknotww.com/press-releases/weddingwire2020newlywedreport). STRONG for its year.
- WeddingPro 2025: 44% of planning on smartphones/tablets (https://pros.weddingpro.com/report/hello-to-hired-your-guide-to-lead-replies/).
- TKWW venue reports: 91% booked a venue; ~80% began venue research within 2 months of engagement; venue ~40% of budget; 76% of venue fees included rentals, 44% catering, 39% alcohol (2023 weddings, n = 9,138) (https://pros.weddingpro.com/report/the-knot-real-weddings-venue-report/). Couples inquire with 5, tour 4; engagement 15 months (https://pros.weddingpro.com/report/what-couples-really-want-from-their-wedding-venues).
- The Knot 2026 Real Weddings Study: $34,000 average, $292 per guest, 117 guests, 13 vendors, AI use 36% (https://www.theknotww.com/press-releases/the-knot-worldwide-unveils-2026-real-weddings-study). The prior year's study (2024 weddings) put the venue at $12,200 of $33,000 (Fox Business summary; theknot.com itself returned 403 to this fetch) (https://www.foxbusiness.com/lifestyle/wedding-season-here-how-much-one-cost-2025). MEDIUM.
- Zola 2026 First Look (11,500+ engaged couples): $36,000 average budget, 145 guests, 87% made a planning choice based on social media, 10% toured a venue before getting engaged (https://www.zola.com/expert-advice/the-first-look-report-2026). MEDIUM (self-selected Zola users). The "$8,573 venue" figure seen in search snippets was not on the fetched page; do not use.

### Accessibility (WCAG 2.2, W3C Recommendation; latest edition 12 Dec 2024)
- 1.4.3 Contrast (Minimum), AA: text and images of text at least 4.5:1 (large text 3:1).
- 1.4.11 Non-text Contrast, AA: UI components and graphical objects at least 3:1 against adjacent colours.
- 2.4.7 Focus Visible, AA; 2.4.11 Focus Not Obscured (Minimum), AA: focused component not entirely hidden by author content.
- 2.5.8 Target Size (Minimum), AA: "at least 24 by 24 CSS pixels" unless spacing/equivalent/inline/user-agent/essential exceptions apply (https://www.w3.org/TR/WCAG22/ ; https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html). STRONG. Practical hits for venue templates: thin grey script text on photos (fails 4.5:1), icon-only social links under 24 px, and hover-only nav with no focus ring.

---

## Part 3. Local SEO and schema.org

### Types and the exact properties that matter
- `EventVenue` (Thing > Place > CivicStructure > EventVenue) inherits from Place: `address`, `geo`, `telephone`, `amenityFeature`, `maximumAttendeeCapacity`, `photo`, `image`, `hasMap`, `publicAccess`, `tourBookingPage`, `containedInPlace`, `aggregateRating`, `review`; from CivicStructure: `openingHours`, `openingHoursSpecification` (https://schema.org/EventVenue).
- `LocalBusiness` is both Organization and Place; adds `priceRange`, `openingHours`, `currenciesAccepted`, `paymentAccepted` (https://schema.org/LocalBusiness). Combining `"@type": ["EventVenue","LocalBusiness"]` is valid because both are Place subtypes.
- `amenityFeature` expects `LocationFeatureSpecification` (a PropertyValue with `name`, `value`, `hoursAvailable`, `validFrom`, `validThrough`) (https://schema.org/amenityFeature ; https://schema.org/LocationFeatureSpecification).
- `Event`: `location`, `startDate`, `endDate`, `offers`, `eventStatus`, `eventAttendanceMode`, `maximumAttendeeCapacity`, `organizer`, `performer`, `image`, `eventSchedule` (https://schema.org/Event). `Offer`: `price`, `priceCurrency`, `priceSpecification`, `availability`, `url`, `validFrom`, `validThrough`, `itemOffered` (https://schema.org/Offer).
- `FAQPage` (WebPage subtype) uses `mainEntity` -> `Question` (`name`, `acceptedAnswer` -> `Answer`.`text`) (https://schema.org/FAQPage ; property names confirmed on Google's FAQ doc, which now redirects to the "removing FAQ rich result" update).

### What Google actually rewards
- Search gallery (current): Event, Local business, Organization, Review snippet, Breadcrumb, Image metadata, Video, Product, etc. FAQ and HowTo are no longer in the gallery (https://developers.google.com/search/docs/appearance/structured-data/search-gallery).
- FAQ: Google's 8 Aug 2023 post: "FAQ (from FAQPage structured data) rich results will only be shown for well-known, authoritative government and health websites. For all other sites, this rich result will no longer be shown regularly"; HowTo deprecated entirely by 13 Sep 2023 (https://developers.google.com/search/blog/2023/08/howto-faq-changes). The FAQPage doc URL itself now 301s to https://developers.google.com/search/updates#removing-faq-rich-result. A venue gets no FAQ rich result; FAQ markup is hygiene only.
- LocalBusiness: required `name` and `address`; recommended `geo`, `openingHoursSpecification`, `priceRange`, `telephone`, `url`, `aggregateRating`, `review`; drives knowledge-panel details, hours, directions and booking actions (https://developers.google.com/search/docs/appearance/structured-data/local-business). EventVenue is not mentioned, so the LocalBusiness type in the array is what Google reads.
- Event rich results require `location` (with street address and venue name), `name`, `startDate`; events must be public and at a physical place; "business hours", "coupons", and "trip packages" are explicitly disallowed (https://developers.google.com/search/docs/appearance/structured-data/event). Use Event only for real open-house / tour-day events, never for "weddings available".
- Google Business Profile: eligible if customers can visit a physical location; venues must have permanent signage and staff during stated hours; Google says event venues are among businesses that "shouldn't provide hours" (https://support.google.com/business/answer/3038177). Category advice ("Wedding venue" primary; "Event venue", "Banquet hall" secondary) comes only from SEO blogs; the one fetched tells you to pick from the live category editor and makes no ranking claims (https://thestacc.com/blog/wedding-venue-google-business-profile/, WEAK).

### Marketplace listings vs the venue's own site
73% of couples use The Knot/WeddingWire-type sites for venue research (https://pros.weddingpro.com/report/what-couples-really-want-from-their-wedding-venues), and TKWW reports 9M+ leads a year. The listing wins discovery and comparison (price, capacity, availability shown side by side); the venue's own site wins the tour booking and the trust check (full gallery, FAQ, real pricing, fast reply). Design the site to answer the three storefront questions (price, capacity, availability) above the fold so the couple does not bounce back to the marketplace.

### Recommended JSON-LD skeleton (homepage)
```json
{
  "@context": "https://schema.org",
  "@type": ["EventVenue", "LocalBusiness"],
  "@id": "https://example-venue.com/#venue",
  "name": "Example Estate",
  "url": "https://example-venue.com/",
  "image": ["https://example-venue.com/img/hero-16x9.jpg", "https://example-venue.com/img/hero-4x3.jpg", "https://example-venue.com/img/hero-1x1.jpg"],
  "telephone": "+1-555-555-0100",
  "priceRange": "$$$",
  "address": {"@type": "PostalAddress", "streetAddress": "1 Vineyard Rd", "addressLocality": "Temecula", "addressRegion": "CA", "postalCode": "92591", "addressCountry": "US"},
  "geo": {"@type": "GeoCoordinates", "latitude": 33.4936, "longitude": -117.1484},
  "hasMap": "https://maps.google.com/?cid=...",
  "maximumAttendeeCapacity": 200,
  "amenityFeature": [
    {"@type": "LocationFeatureSpecification", "name": "On-site ceremony space", "value": true},
    {"@type": "LocationFeatureSpecification", "name": "Bridal suite", "value": true},
    {"@type": "LocationFeatureSpecification", "name": "Parking spaces", "value": 120}
  ],
  "tourBookingPage": "https://example-venue.com/tour",
  "openingHoursSpecification": [{"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday","Tuesday","Wednesday","Thursday","Friday"], "opens": "09:00", "closes": "17:00"}],
  "sameAs": ["https://www.theknot.com/marketplace/...", "https://www.instagram.com/..."],
  "makesOffer": {"@type": "Offer", "name": "Saturday wedding package", "price": "12000", "priceCurrency": "USD", "url": "https://example-venue.com/pricing"}
}
```
Separate node on the FAQ page only: `{"@type":"FAQPage","mainEntity":[{"@type":"Question","name":"...","acceptedAnswer":{"@type":"Answer","text":"..."}}]}`.

Rewarded by Google: `name`, `address`, `geo`, `telephone`, `url`, `image`, `openingHoursSpecification`, `priceRange`, `aggregateRating`/`review` (if real) via the LocalBusiness rich result; `Event` nodes for public open-house days. Hygiene only (valid, harmless, no visible SERP effect): `EventVenue` type, `maximumAttendeeCapacity`, `amenityFeature`, `tourBookingPage`, `makesOffer`, `FAQPage`. Keep them because they are cheap, machine-readable facts for AI answer engines and marketplace scrapers, not because they change ranking.

---

## URLs cited and HTTP status observed (curl with browser UA, 2026-10-20; "WF" = content retrieved via WebFetch)
| URL | Status |
|-----|--------|
| https://showit.com/pricing/ | 200 |
| https://alexcollierdesign.com/honeysuckle-house | 200 (403 only when curl sends a Chrome UA string) |
| https://alexcollierdesign.com/shop | 200 WF; curl with Chrome UA 403 |
| https://elizabethmccravy.com/alice | 200 |
| https://elizabethmccravy.com/taylor | 200 |
| https://andreashah.com/the-5-best-showit-website-templates-for-wedding-pros/ | 200 |
| https://showit.com/website-tips/showits-top-event-professional-website-templates/ | 200 |
| https://saltedpages.com/blog/showit-template-shops/ | 200 |
| https://www.withgraceandgold.com/shop | 200 |
| https://withgraceandgold.com/2026/04/showit-templates-arent-selling/ | 200 |
| https://northfolk.co/ | 200 |
| https://daveyandkrista.com/showit-templates/ | 301 -> 200 (/showit-templates-built-for-seo/) |
| https://daveyandkrista.com/?p=84437 | 301 -> 200 (/how-to-pair-fonts-like-a-pro/) |
| https://tonicsiteshop.com/shop-page | 301 -> 200 (/shop/) |
| https://tonicsiteshop.com/shop/showit-websites-templates/gin-and-tonic | 301 -> 200 (/shop-showit-website-templates/) |
| https://www.squarespace.com/pricing | 200 |
| https://www.applet.studio/squarespace-showcase/squarespace-website-for-wedding-venue | 200 |
| https://www.applet.studio/blog/squarespace-wedding-websites | 200 |
| https://flothemes.com/ | 200 (one curl attempt with Chrome UA failed to connect; default UA 200) |
| https://slrlounge.com/why-did-pixieset-acquire-flothemes-interview-with-the-founders/ | 301 -> 200 |
| https://pixieset.com/pricing-website/ | 200 |
| https://www.format.com/pricing | 301 -> 200 (/pricing-portfolio) |
| https://www.elegantthemes.com/blog/wordpress/best-wedding-wordpress-themes | 200 |
| https://rublyjackie.gumroad.com/l/fleurawedding | 200 |
| https://webflow.com/templates/search/wedding-venue | 200 |
| https://templates.webflow.com/html/marrymint-website-template | 200 |
| https://blog.hubspot.com/blog/tabid/6307/bid/6746/which-types-of-form-fields-lower-landing-page-conversions.aspx | 200 |
| https://ventureharbour.com/how-form-length-impacts-conversion-rates/ | 200 |
| https://pros.weddingpro.com/?p=35190 | 301 -> 200 (/blog/vendor-storefront-pricing/) |
| https://www.theknotww.com/press-releases/the-knot-worldwide-announces-new-products-to-help-wedding-professionals-get-discovered-and-connect-with-more-couples | 200 |
| https://pros.weddingpro.com/report/hello-to-hired-your-guide-to-lead-replies/ | 200 |
| https://pros.weddingpro.com/report/what-couples-really-want-from-their-wedding-venues | 301 -> 200 |
| https://pros.weddingpro.com/report/the-knot-real-weddings-venue-report/ | 200 |
| https://www.theknotww.com/press-releases/the-knot-worldwide-unveils-2026-real-weddings-study | 200 |
| https://www.foxbusiness.com/lifestyle/wedding-season-here-how-much-one-cost-2025 | 200 |
| https://www.theknotww.com/press-releases/weddingwire2020newlywedreport | 200 |
| https://www.zola.com/expert-advice/the-first-look-report-2026 | 301 -> 200 (/expert-advice/the-first-look-report) |
| https://hbr.org/2011/03/the-short-life-of-online-sales-leads | 200 (body paywalled) |
| https://scholarsarchive.byu.edu/facpub/9711/ | 200 |
| https://www.honeybook.com/pricing | 200 |
| https://calendly.com/pricing | 200 |
| https://www.tripleseat.com/ | 200 |
| https://www.perfectvenue.com/ | 200 |
| https://www.planningpod.com/ | 200 |
| https://www.releventful.com/ | 200 |
| https://weven.co/ | 301 -> https://www.theknot.com/ (403 to curl) |
| https://bostonseed.com/?p=11938 | 301 -> 200 (/portfolio/weven/) |
| https://www.exploretock.com/join/private-events | 403 (Cloudflare challenge; not used for claims) |
| https://web.dev/articles/vitals | 200 |
| https://blog.amp.dev/2017/02/28/new-industry-benchmarks-for-mobile-page-speed/ | 200 |
| https://www.thinkwithgoogle.com/_qs/documents/57/mobile-page-speed-new-industry-benchmarks.pdf | 200 (PDF) |
| https://www.w3.org/TR/WCAG22/ | 200 (403 only with a spoofed Chrome UA) |
| https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html | 200 (403 only with a spoofed Chrome UA) |
| https://schema.org/EventVenue | 200 |
| https://schema.org/LocalBusiness | 200 |
| https://schema.org/Event | 200 |
| https://schema.org/Offer | 200 |
| https://schema.org/FAQPage | 200 |
| https://schema.org/amenityFeature | 200 |
| https://schema.org/LocationFeatureSpecification | 200 |
| https://developers.google.com/search/docs/appearance/structured-data/faqpage | 301 -> 200 (/search/updates#removing-faq-rich-result) |
| https://developers.google.com/search/blog/2023/08/howto-faq-changes | 200 |
| https://developers.google.com/search/docs/appearance/structured-data/local-business | 200 |
| https://developers.google.com/search/docs/appearance/structured-data/event | 200 |
| https://developers.google.com/search/docs/appearance/structured-data/search-gallery | 200 |
| https://support.google.com/business/answer/3038177 | 200 |
| https://thestacc.com/blog/wedding-venue-google-business-profile/ | 200 |

Not reachable in this pass (403 to both tools, no claims drawn from them): https://www.theknot.com/content/average-wedding-cost, https://www.businesswire.com/news/home/20260218045442/en, https://themeforest.net/search/wedding%20venue, https://www.templatemonster.com/category/wedding-venues-templates/, https://vendorsupport.weddingwire.com/hc/en-us/articles/30743246106644.
