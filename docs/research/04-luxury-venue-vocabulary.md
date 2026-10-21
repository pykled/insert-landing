# Luxury venue vocabulary: what top-tier wedding venue sites actually look like

Written 2026-10-20 for Insert's venue site factory (phase 1 of the "luxury dialects" work). Companion spec:
`05-luxury-dialects-spec.md`. This extends `01-venue-site-survey.md` (36 mostly mid-market SoCal homepages) with a
sample drawn from the top of the market: Relais & Châteaux / Auberge / Aman / Rosewood / Montage properties,
venues on The Wed, Carats & Cake, Loverly and Brides "best venues" lists, Soho House, and a few design-studio builds
(Inness, Shou Sugi Ban House, Cherry Hollow Farm, The Sea Ranch Lodge, Parker Palm Springs).

## Method

- Candidate list: 68 URLs (`candidates.txt`) built from https://thewed.com/magazine/best-wedding-venues-in-the-US,
  https://caratsandcake.com/articles/wedding-venues-in-california-top-spots,
  https://loverly.com/planning/wedding-101/best-wedding-venues-in-us, https://www.brides.com/best-rustic-wedding-venues-usa-6231828,
  Awwwards' wedding tag (https://www.awwwards.com/inspiration_search/wedding/ returned only photographer/planner sites, no venues),
  plus known SoCal luxury properties. Junebug's California venue list (https://junebugweddings.com/vendors/wedding-venues/california/)
  returned 403 to a non-browser fetch and was not used.
- Every URL was verified with curl, then loaded in headless Chromium (Python Playwright) at 1440x900 and 390x844,
  cookie banners dismissed where a button matched, scrolled to trigger lazy loads, screenshotted (fold + full page)
  into `shots/` (git-ignored, internal analysis only), and probed for computed styles: h1/h2/paragraph font family,
  weight, size, letter-spacing, case; body background; nav link count; first large image or video and its rendered
  height; image and video counts; slider / smooth-scroll libraries; award-badge strings; CTA labels; capacity and
  price mentions. Script: `shoot.py`; data: `style-facts.json`. Judgements below come from looking at the
  screenshots (contact sheets in `shots/sheets/`), with the probe data as the factual backbone.
- 51 sites rendered usably. Failures: 11 small SoCal domains did not resolve or had broken TLS from this machine
  (Ethereal, The Villa SJC, La Venta Inn, Valentine DTLA, Hotel Californian, Natirar, Lowndes Grove, Villa Balbiano,
  Haiku Mill, Lake House on Canandaigua, Stone Manor), Kestrel Park returned 503, Pelican Hill served a bot wall,
  Oheka served a Cloudflare block on desktop (mobile loaded), triunfocreekvineyards.com and theruins.net are parked,
  babingtonhouse.com is a school (the venue is Soho House's, re-shot at sohohouse.com), Belmond Caruso's weddings
  path 404s. None of these is in the table.
- Southern California (incl. Santa Barbara / Ojai) rows: 19. Types covered: estate, resort, coastal, desert, vineyard,
  villa, garden, historic club, loft, castle, ranch, country inn, modern retreat, museum villa, international.

## 1. Sample table

Columns: hero = what fills the first screen at 1440; palette = what the page is made of; type = measured h1 family /
weight / size / case plus body family; ornament = rules, frames, crests, line art; photo = scale and treatment;
motion = what moves; nav = header pattern; CTA = where the inquiry ask sits; tone = copy register; verdict = what
makes it feel expensive, or not. "Inset" means the hero photo sits inside page margins rather than bleeding.

| # | Venue (type, place) | URL | Hero | Palette | Type | Ornament | Photo | Motion | Nav | Inquiry CTA | Tone | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | San Ysidro Ranch (estate, Montecito) | https://www.sanysidroranch.com/weddings-and-events | Short (450 px) full-bleed couple in lavender rows, logo + SR monogram centred over it | White, sage green, grey watercolour wash | Jost 400 30 px caps +1 px / Jost 18 | Short centred rule under headings; watercolour leaf wash behind sections | One space per full-width band, 3:2, flush | slick slider only | Burger left, split wordmark around monogram, green "Check accommodations" | Green "Request information" on every space band; form at page end | Hotel-brochure ("Storybook settings") | Restraint of green + white and the "up to N guests" line on every space read premium; hairline geometric caps headlines read spa-brochure |
| 2 | Ojai Valley Inn (resort, Ojai) | https://www.ojaivalleyinn.com/ | Full-height (900 px) landscape video, no headline on it | Cream paper, terracotta button, warm greys | Wordmark serif; h1 Termina caps 17 px +2.4 px (kicker-as-h1) / Brandon Grotesque 16 | None; whitespace is the ornament | Overlapping photo clusters with lots of air; cards in a muted grid | Swiper; slow video | Serif wordmark left, caps links, terracotta "Book now" | None on first screen; "Gatherings" in nav | Place-first ("Welcome to the valley") | Expensive because nothing shouts: landscape first, cream, overlapped collage. Horizontal overflow at 390 px |
| 3 | Rosewood Miramar Beach (coastal hotel, Montecito) | https://www.rosewoodhotels.com/en/miramar-beach-montecito/weddings | Full-bleed ocean-front video with engraved caps name and italic serif subline | Cream, black, deep green reserve button | Engravers Gothic 700 48 px caps +4.8 px / Austin Light 16 | Thin rules between footer columns; "1 — 2" slide counter | Curated-experience grid, big quiet landscape bands, dark "On the house" band | Cross-fade slideshow, 2 videos | Wordmark left, serif links, green "Reserve" | "Inquire" (opens new tab) inside page, not in header | Hotel-editorial ("The American Riviera Estate") | Engraved tracked caps + light transitional serif is the classic Rosewood register; counter and pacing are slow |
| 4 | Montage Laguna Beach (coastal resort) | https://www.montage.com/lagunabeach/weddings/ | Full-bleed ocean photo/video under heavy dark scrim, script "Weddings" + small-caps line | Navy-black scrim, white, khaki cookie bar | Garamond Nova Pro 300 48 px (script-style italic display) / Spezia 20 | Bullet separators between nav links; hairline under "Reservations" | Three venue cards, itinerary split, gallery slider | Swiper | Burger + script logo + caps links with bullets | None on first screen; contact card beside copy | Resort-formal | Scrim so heavy the sea goes grey; identical template to Healdsburg (#23). Luxury signalled by darkness, lost in sameness |
| 5 | Parker Palm Springs (desert modern) | https://www.parkerpalmsprings.com/weddings | Didone caps "WEDDINGS" 80 px with orange underline bar over a monochrome + colour photo pair | Cream, chocolate booking bar, orange, lime circle | Essonnes Display 300 80 px caps / Gotham SSm 14 | Orange underline bar, grey circle ground, hand illustration | B/W + colour pairing, inset, playful crops | Lenis smooth scroll, 4 videos, marquee ticker | Centred wordmark, caps links, booking bar beneath | "Request information" in booking bar; form mid-page | Witty ("Love, laughter, and a bit of mischief") | The strongest brand voice in the sample; luxury as personality (Jonathan Adler era). Most things here are not reusable, which is the point |
| 6 | Korakia Pensione (desert, Palm Springs) | https://www.korakia.com/weddings | Full-bleed floral tablescape, light serif "Weddings At Korakia", two gold buttons | White, ochre gold, dark wood from photo | Crimson Pro 300 67 px sentence case / Aileron 14 | Thin rule + caps kicker ("CELEBRATING"); sub-nav "EVENTS \| WEDDINGS" | Two-column essays with 4:5 photos, floor-plan line drawing | Swiper, Lottie | Centred wordmark, "Menu" left, gold buttons right | "Download Brochure" + "Inquire Today" on the hero | Warm hospitality | Light garalde + gold + floor plan feels bespoke; buttons are a little loud |
| 7 | Greengate Ranch & Vineyard (vineyard ranch, SLO) | https://greengateweddings.com/ | Full-bleed barn-and-string-lights photo under white header | White, forest green | Montserrat 400 28 px / Montserrat 12 | None | One hero, small gallery | Mailing-list popup | Logo left, two rows of caps links, outlined "Wedding pricing" | Outlined "Wedding pricing" in the header (rare and good) | Plain | Pricing button in the nav is the one premium confidence signal; otherwise Squarespace default |
| 8 | Sunstone Villa (villa, Santa Ynez) | https://www.sunstonevilla.com/ | Full-height video of the stone villa, tracked caps name, italic subline | Taupe header, white, warm stone | Cormorant Garamond 700 60 px caps +4 px / Cormorant 15 | Chevron scroll cue; centred caps section titles | Room grid, dark-brown "Book your villa" band | Swiper, GSAP | Centred wordmark, burger | "Contact" in menu; none on hero | Formal ("A Provençal Dream") | Caps garalde on stone reads old-world; the cream+taupe pairing is the right instinct |
| 9 | Monserate Winery (vineyard, Fallbrook) | https://www.monseratewinery.com/weddings | Full-height video with a large white award badge ("Best Venue of 2026 Winner") centred in the hero | White, taupe, hills | Playfair Display 400 65 px +6.5 px / Arial 16 | Crest monogram, award crown | Alternating bands, three villa cards, press-logo band | Video | Transparent caps links over video, cart icon | Outlined "Inquire Today" on hero | Boast ("The Difference") | Badge in the hero and Playfair + Arial cheapen a genuinely beautiful property |
| 10 | Rancho Valencia (estate resort, Rancho Santa Fe) | https://www.ranchovalencia.com/weddings | No hero: 2x2 photo grid straight under a two-row navy nav | Navy, orange "Book now", turquoise from the photos | ActaDisplay 400 56 px / HCo Verlag 16 | None | Dense grids throughout | None | Two-row navy bar, 14 links | "Book now" only | Corporate | Dense navigation and grids read like a resort group site, not an estate |
| 11 | Terranea (coastal resort, Palos Verdes) | https://www.terranea.com/weddings | Aerial of clifftop ceremony, hairline "Weddings" bottom-centre | White, navy | Larken 100 56 px / Larken 25 | None | Three venue cards with carousel | Chat widget | Burger + caps links, centred logo, navy "Book now" | "Plan your wedding" below the fold | Resort-formal | Hairline (100) headline disappears on the photo; generic resort page |
| 12 | Inn at the Mission (mission hotel, SJC) | https://www.innatthemissionsjc.com/weddings | Dark overlay with two popups (newsletter + notifications) over the photo | Dark, gold | GardaTitlingTwo 400 50 px caps +8 px / Hypatia Sans 17 | Promo bar | Alternating bands | Promo ticker | Logo left, caps links, "Book now" | Inquiry at page end | Promo | Popups on arrival destroy any luxury the typography was building |
| 13 | Lodge at Torrey Pines (coastal lodge, La Jolla) | https://www.lodgetorreypines.com/weddings | Sunset couple photo, full-width, no text | White, brown, craftsman green | Libre Baskerville 500 35 px / Open Sans 17 | Craftsman logotype | Alternating cards | None | Logo + phone, grey bar of caps links, brown "Plan my stay" | "Request a wedding quote" below | Hotel-plain | Craftsman logotype is the only character; the rest is a template |
| 14 | Serra Plaza (hacienda, SJC) | https://serraplaza.com/ | Chandelier hanging in a tree, full-bleed, under a cream header | Cream, coral button, charcoal | Cormorant Garamond 600 160 px / Cormorant 18 | Three-column fact row with hairlines; centred wordmark; serif monogram | Two-up 3:2 photos, big cream gaps | Video (1) | Cream bar, caps links, coral "See your date & price" | "See your date & price" in the header; "Begin your story" band | Confident, brief | 160 px garalde name on cream with "Up to 450 guests" fact row: the most Insert-like page in the sample. Coral button is the one loud note |
| 15 | Ebell of Long Beach (historic club) | https://www.ebelllongbeach.com/ | Full-bleed courtyard photo, wide-tracked caps "REVIVED", award badge under it | White, dark brown header, brass | Futura Light 18 px caps (kicker-as-h1) / Futura 17 | Award crown, "Virtual tour" bar | Alternating bands, catering band | Swiper, Lottie | Logo left, caps links incl. "Pricing", outlined "Get in touch" | "Get in touch" header + "Pricing" nav | Boast | Wide-tracked light caps on the photo is a real signature; badge in hero undercuts it |
| 16 | The Ranch at Laguna Beach (coastal canyon) | https://www.theranchlb.com/weddings | Full-bleed canyon ceremony photo (720 px) | Sage, olive, ochre, cream | Canela 400 50 px / Open Sans 16 | Olive bands, ochre serif subheads | Alternating photo/text, venue cards on olive | slick | Burger, centred script logo, phone, sage "Reserve" | "Wedding inquiries" + "Wedding brochure" under the hero | Nature-forward | Palette taken straight from the canyon; olive band for venues is a good "deep band" precedent |
| 17 | Maravilla Gardens (garden, Camarillo) | https://www.maravillagardens.com/ | Couple close-up, full-bleed, long serif headline over it | White, pale sage, teal buttons | Raleway 300 caps 15 px kicker; serif headline ~60 px / Raleway 17 | Teal buttons | Pale sage bands, grid | Swiper, Lottie | Logo left, caps links, teal "Schedule a tour" | "Get my free wedding booklet" on hero; booklet band later | Lead-gen | Couple-first hero hides the garden; booklet CTA is funnel-first |
| 18 | The Ebell of Los Angeles (historic club) | https://ebellevents.com/ | Full-bleed floral ballroom photo under a centred monogram wordmark | White, mustard wave, florals | Script-E monogram + serif wordmark; h1 absent / Nunito Sans 14 | Mustard wave divider, badge-logo strip | Grid of events | None | Centred logo, small links | "Contact us" | Plain | The wave divider and badge strip pull a grand room down to template |
| 19 | Greengate / Maravilla / Monserate / Serra as a SoCal set | — | — | — | — | — | — | — | — | — | — | Of 19 SoCal rows, only Serra Plaza, Parker, Ojai, Rosewood and The Ranch would pass as "expensive" at first glance; the rest are resort or Squarespace templates with good photos |
| 20 | Blackberry Farm weddings (estate, TN) | https://www.blackberryweddings.com/ | Inset pond photo with page margins, serif "Weddings on the Farm" bottom-left, monogram top-left | White, charcoal, farm greens | Old Standard TT 400 58 px / Open Sans 15 | BB monogram; tracked small-caps wordmark | One inset 16:9 hero, two-up 3:2 below | GSAP (subtle) | Monogram, centred wordmark, burger | "Inquiry" in menu; "Contact us" band | Declarative, short | Three sections, one photo per idea, margins everywhere: luxury by omission |
| 21 | Auberge du Soleil (vineyard resort, Napa) | https://auberge.com/auberge-du-soleil/ | Full-bleed wine-pour photo with a date card "Check availability" top-right | Cream, gold, charcoal | Financier Light 36 px / CentraNo1 14 | Date card; gold rules | 172 images: grids of rooms, dining, experiences | Swiper | Burger, centred wordmark + collection name, phone | Date card in hero (stay, not wedding) | Hotel | Booking-first; luxury via Financier + gold, diluted by density |
| 22 | Auberge Collection weddings (brand page incl. Stanly Ranch) | https://auberge.com/events/weddings/ | Full-bleed poolside ceremony | Cream, gold | CentraNo1 caps kicker 14 px +2.5 px as h1; Financier Light 24 body | Numbered property list | Property rows with photo | Swiper | Collection wordmark, sub-nav "Incentives \| Weddings" | "Inquire" per property | Catalogue | Big light serif body (24 px) is a luxury tell worth copying; page is a catalogue |
| 23 | Montage Healdsburg (vineyard resort) | https://www.montage.com/healdsburg/weddings/ | Identical to #4 with a vineyard dinner photo | Same | Same | Same | Same | Same | Same | Same | Same | Sister template; see #4 |
| 24 | Alila Ventana Big Sur (coastal forest) | https://www.ventanabigsur.com/wedding-celebration-spaces/ | Aerial over redwood roofs, light serif headline, two arrow buttons | Charcoal, white, slate | SangBleu Sunrise 300 56 px / Noto Sans 18 | Arrow glyphs on buttons; hairline nav | Space grid with capacities, FAQ | Lenis, Swiper | Phone + centred Alila lockup + "Reserve →", second row of caps links with arrows | "Inquire now →" on hero | Spec-forward | Capacity grid + FAQ is the right content; the type is elegant but the page is a hotel CMS |
| 25 | The Sea Ranch Lodge (coastal, Sonoma) | https://www.thesearanchlodge.com/ | Full-bleed photo of the timber lodge against sun | Pine green, black, sand | Helvetica Neue 400 56 px (bold on mobile) / Helvetica 14 | Ram supergraphic logo; strict grid | Grids, B/W archival in "General store" | slick | Wordmark + ram, 8 links, black "Book now" | "Private events" in nav | Architectural-modern | Modernist sans + supergraphic is a legitimate luxury dialect (architecture, not romance); closures popup hurt |
| 26 | Shou Sugi Ban House (modern retreat, Hamptons) | https://shousugibanhouse.com/ | Grey-washed fire-pit video, booking bar beneath, almost no copy on screen | White, warm grey, charcoal | LTC Bodoni 175 italic 100 32 px / Fira Sans 19 | None | Small inset photos, enormous whitespace | AOS fades | Boxed logotype left, caps links, outlined "Reserve" | "Check availability" bar; "Private events" nav | Wellness-serene | Quiet luxury by whitespace; the hairline Bodoni italic is exactly the legibility trap the factory pins against |
| 27 | Amangiri (desert modern, Utah) | https://www.aman.com/resorts/amangiri/weddings | Inset dusk-canyon photo with wide margins under a two-row light header | Warm grey paper, charcoal, dusk | Lyon Text 400 31 px / Lyon Display 14 | Tracked wordmark; hairline rows | Inset photos, small captions, big gaps | slick | Menu + search left, centred ĀMAN, language + "Reserve" | "Contact us" in sub-nav | Minimal, tracked | The canonical quiet-luxury page: small type, tracked caps, grey paper, dusk photography, nothing bleeds |
| 28 | Commodore Perry Estate (estate, Austin) | https://auberge.com/commodore-perry/ | Full-bleed interior video (lamp, wallpaper), date card top-right | Cream, gold, deep interior colour | Financier Light 36 px / CentraNo1 14 | Date card, gold rules, wreath imagery | Room grids | Swiper | Auberge template | Date card | Hotel | Interiors-first hero reads "estate hotel"; same chassis as #21 |
| 29 | Glenmere Mansion (mansion, NY) | https://www.glenmeremansion.com/ | Full-bleed aerial video with tracked caps "GLENMERE MANSION" | White, brown, blue-grey | Montserrat 400 50 px caps +2 px / Red Hat Display 16 | Crest logo; tracked caps everywhere | Alternating bands; dark brown band | Video | Logo left, 7 dropdowns, brown "Book now" | "Inquire now" | Grand ("A magnificent 150-acre estate") | Mobile runs a whole paragraph in tracked caps: the single clearest "cheapening" move seen |
| 30 | Inness (modern farm, Hudson Valley) | https://www.inness.co/ | Full-bleed autumn landscape, hairline display sans headline | Cream, terracotta, field colours | ABC Arizona Flare 100 73 px / Arizona Flare 24 | Double-line glyph logo; hairlines | Cabin grid, big landscape bands | Scroll cue | Cream two-row bar, orange "Book" | Offer popup; "Events" nav | Design-studio | A studio-built site: cream + terracotta + one odd display face. Hairline weight again |
| 31 | The Six Bells (country inn, CT) | https://thesixbells.com/ | Storefront photo with illustrated sign, two promo bars, newsletter modal | Barn red, mustard, cream | Sandleford 400 42 px / Sandleford 16 | Hand-lettered signs, storybook illustration | Shop grids | Swiper + slick | Shop mega-nav | None (shop) | Storybook | Charming, not luxury; a shop with rooms. Included as the "country" counter-example |
| 32 | Santa Lucia Preserve (ranch estate, Carmel) | https://www.santaluciapreserve.com/ | Full-bleed golf-and-lupine landscape with transparent nav | Cream, oxblood, landscape | Iskry 400 56 px / Brandon Grotesque 20 | Diamond logo; oxblood bands | Alternating landscape bands | Swiper | Transparent, 7 links, login | "Contact" | Club ("A place with a cadence all its own") | Oxblood + cream + landscape = private club; works |
| 33 | Cherry Hollow Farm (barn, GA) | https://www.cherryhollowfarm.com/ | Full-bleed barn photo under a centred Didot wordmark, two-row nav (second row black) | White, black, barn greys | Didot 400 84 px / Cormorant Garamond 16 | Monogram; drop cap; vertical section labels; press logos | Full-bleed hero, inset pairs | Scroll chevron | Centred monogram wordmark, caps links, black category bar | "Inquire now" nav; split inquiry section | Editorial ("A timeless and distinctive event…") | Didot wordmark + drop cap + vertical labels: the best "romantic editorial" reference in the set |
| 34 | Early Mountain Vineyards (vineyard, VA) | https://www.earlymountain.com/weddings | Wedding-party walking photo, headline bottom-left, red "Contact us" | White, red, navy | No h1; Raleway 16 | Red arrow glyph | Three-up grids | Video (1) | Logo centred, links right | Red "Contact us" on hero | Promo ("let us show you…") | Red button + party photo = winery marketing, not luxury |
| 35 | Castle Hill Inn (coastal inn, Newport RI) | https://www.castlehillinn.com/weddings | Inset photo of a sailcloth-and-hydrangea ceremony with margins; "Weddings" centred below | White, navy, hydrangea blue | Playfair Display 400 46 px / Literata 15 | Small-caps kicker "IN LOVE, ON THE OCEAN"; thin rules | Inset 16:9 hero, two-up below | None | Logo left, caps links, black "Book now" | "Request a custom proposal" mid-page | Lyrical, short | Margins + one kicker + navy: the "coastal and airy" dialect done quietly; Playfair is the only generic tell |
| 36 | Oheka Castle (castle, Long Island) | https://www.oheka.com/weddings | (mobile) Overhead couple photo under black header; castle silhouette crest | Black, white, gold, navy footer | Mrs Eaves roman lining 500 40 px caps +4 px / Mr Eaves 18 | Castle crest, double square buttons, association logos | Alternating | slick | Black bar, crest, 6 dropdowns | "Book a tour" + "Book a room" as two square buttons | Grand ("Celebrating the art of entertaining®") | Black + Mrs Eaves caps + crest is the old-world register; desktop was bot-blocked |
| 37 | Weylin (historic hall, Brooklyn) | https://www.weylin.com/ | Full-height dusk photo of the dome; nav sits at the bottom of the hero | Black, dusk | No h1; small-caps nav | Monogram W | One hero, scroll gallery | Video | Bottom-of-hero bar: logo, caps links, outlined "Inquire here" | "Inquire here" in the bar | Silent | A one-photo site: the dome does the talking. Shows how little copy a strong building needs |
| 38 | Wythe Hotel (loft hotel, Brooklyn) | https://wythehotel.com/weddings | Inset candlelit dinner photo (540 px) with margins on blush paper | Blush, cream, red candlelight | Light serif 300 44 px / grotesk 16 | Hairline numbered rows; bullets of facts | Inset hero, two-up 3:2 | Lenis | Wordmark centred, "Menu" left, "Submit inquiry →" right | "Submit inquiry →" in the header | Specific ("13,000 square feet… up to 200 guests") | Blush paper + facts in the first screen; the loft dialect with warmth |
| 39 | Hotel Emma (historic brewery hotel, San Antonio) | https://www.thehotelemma.com/weddings | Split: dark panel with gold double-line frame + botanical line art and copy, couple photo right | Charcoal, gold, ivy green | Display serif; body Special Elite 14 (typewriter) | Gold double-line frame, botanical engraving, crest shield | Split hero, grid | Swiper | Dark bar, crest centre, gold caps links | "Request for proposal" in the panel | Hospitable | The one real "dark + ornament" page: frames and engraving read deco-industrial. Typewriter body cheapens it |
| 40 | Nestldown (redwood garden, Los Gatos) | https://www.nestldown.com/ | Inset redwood aerial video with script headline "Connect. Inspire. Celebrate." | Dark green, white, botanical line art | Beloved script 300 95 px / sans | Count-up numbers "180 / 150 / 36 / 20"; white botanical line drawings | Inset video, grid | Video | Logo left, "Plan an event", burger | "Plan an event" header | Slogan | Script at 95 px reads mid-market; the four-number strip and line-art botanicals are good |
| 41 | Holman Ranch (ranch vineyard, Carmel Valley) | https://www.holmanranch.com/weddings | Full-bleed ceremony aerial under an age gate; serif "The Celebration of a Lifetime" bottom-left | Cream, burgundy, oak | Lyon Text; h1 absent on desktop / Lyon 16 | Quote band on cream; burgundy buttons | Alternating, gallery grid | None | Wordmark left, 3 dropdowns, cart | Burgundy "Inquire" | Statement | Age gate on a wedding page is a conversion wall; the large burgundy serif paragraph on mobile is handsome |
| 42 | Brush Creek Ranch (ranch, WY) | https://www.brushcreekranch.com/weddings | Short couple photo (420 px), then centred caps "LUXURY WESTERN WEDDINGS" | White, navy | Lusitana 400 40 px caps / Montserrat 16 | Small-caps kicker | Packages grid, dense gallery | None | Navy bar, 7 links, "Book now" | "Inquire now" + "Wedding pricing" buttons | Sell ("unmatched, all-inclusive") | Says "luxury" in the headline; the layout does not |
| 43 | Twin Farms (country inn, VT) | https://www.twinfarms.com/ | Inset lake-and-canoe photo with margins; serif logotype | White, yellow "Book now" | Serif logotype; body Karla 22 | Relais & Châteaux crest; Forbes / Michelin logos | Inset hero, big gaps | Video | Logotype left, 7 links, phone, yellow "Book now" | "Gather" nav | Quiet | Margins + big Karla body + a crest from an outside authority: airy heritage |
| 44 | Vizcaya (historic villa museum, Miami) | https://vizcaya.org/visit-2/wedding-events/ | B/W couple-on-steps photo with light sans headline | Navy, white, teal | Ranade 500 48 px / Work Sans 16 | Museum nav | YouTube embed, grid | Swiper, slick, Flickity, Lottie | Museum nav with promo bar | "Request information" accordion | Institutional | Monochrome photo is a smart choice for a 1916 villa; everything else is museum CMS |
| 45 | Bella Collina (Tuscan estate, FL) | https://www.bellacollina.com/weddings-events/weddings | Full-bleed long-table photo under a heavy white scrim, tracked caps + italic subline | Navy, white | Libre Baskerville 400 64 px caps +6.4 px / Raleway 16 | Crest; review stars | Package lists, cards | AOS | Navy bar, crest centre | "Contact our wedding team" | Sell ("Orlando luxury weddings") | White scrim washes the photo to grey; packages + WeddingWire badge read mid-market |
| 46 | The Clifton (inn, Charlottesville) | https://www.the-clifton.com/ | Full-bleed white-house photo through branches | White, gold, slate | Lora 400 italic caps 60 px / Nunito 15 | Centred tracked caps intro | Room-option grid | slick | Monogram + wordmark, links, gold "Book now" | "Weddings" nav | Southern-formal | Gold + slate + white house: "Southern estate" is its own dialect; italic caps is an odd choice |
| 47 | Babington House, Soho House (country house, UK) | https://www.sohohouse.com/houses/babington-house | No hero: title, tab sub-nav, two rows of filmstrip carousels | Cream, brown, peach block | Cardo 400 48 px / HK Grotesk 24 | Tab underline; peach content block | 4:3 filmstrips, inset house photo | Carousels | Soho House grid icon, plain links, "Membership" | "Weddings" tab | Factual ("Occupying a Grade II-listed manor built in 1705…") | Big serif paragraph as the hero, 24 px body, carousels of interiors: unhurried, editorial, no headline needed |
| 48 | The Wildflower 301 (garden estate, GA) | https://wildflower301.com/ | Full-bleed garden photo with couple; tracked serif caps name with italic "the" | Cream, blush rule | Serif caps ~40 px tracked; italic lead-in / serif | Monogram W; blush footer rule | One hero, three-up | WebGL (Squarespace) | Monogram only | None on hero | Testimonial-first (stars) | The italic-lowercase-into-tracked-caps lockup is a nice typographic move; yellow stars undercut it |
| 49 | Cuixmala (estate, Mexico) | https://cuixmala.com/ | Full-bleed video of the hacienda dome and coast, centred white paragraph, gold button | White, gold, jungle | Avenir 400 22 px caps +2.2 px / Avenir 23 | Hairline outlined secondary button | Landscape bands | slick | Burger, centred tracked wordmark, "Book now" | "Book now" | Factual ("A nature reserve of more than 30,000 acres") | Light tracked sans + 23 px body + landscape video: modern luxury without a serif |
| 50 | Greenhouse Loft (loft, Chicago) | https://greenhouseloft.com/ | Typographic: "see GREENHOUSE LOFT in a new light" in caps + italic garamond on oatmeal paper, no photo on first screen | Oatmeal, olive bar, black | Titling Gothic 300 63 px caps +4.4 px / Adobe Garamond 18 | Italic serif interjections; olive sister-venue bar | Photos arrive later, inset | None | Caps links incl. "Pricing", "Floor plans" | "Pricing" nav; rates published in-page ("2026-2027 Rates") | Plain, honest | Type-only hero + published rates is the loft dialect at its most confident |
| 51 | Hotel Bel-Air (hotel estate, LA) | https://www.dorchestercollection.com/los-angeles/hotel-bel-air | Dorchester group template; weddings path 404s; mobile hero "The legendary hideaway" in light sans over jungle | Taupe, gold | Acumin Pro 300 36 px / Acumin 16 | Group monogram | Grid | None | Group header + hotel sub-nav | "Contact" | Group-corporate | A legendary venue hidden in a group CMS; proof that the property's own vibe can be erased by a template |

Rows 1-18 and 51 are Southern California (19). Rows 7 and 20-50 are the national and international reference set.

## 2. Pattern counts (n = 51 usable, from `style-facts.json`)

| Pattern | Count |
|---|---|
| First large element is a video | 14 (video somewhere on the page: 17) |
| First large element ≥ 800 px tall at 1440 | 26 |
| h1 is a serif | 33; sans 11; no visible h1 7 |
| h1 in all caps | 16 |
| h1 weight 300 or lighter | 12 (Terranea 100, Inness 100, Shou Sugi Ban 100) |
| h1 ≥ 56 px | 17 |
| A slider library shipped (Swiper, slick, Flickity) | 25 |
| Smooth-scroll or GSAP | 5 |
| A script face loaded | 1 (Nestldown); Montage uses a script-like italic serif |
| Award badge strings in the HTML | 4 (Monserate, Serra footer, Bella Collina, Ebell LA) |
| Any guest number on the page | 16; any price / rates / pricing string 15 |
| Median nav links | 8 |
| Body text median | 16 px; six sites run 20-25 px (Montage, Auberge weddings, Terranea, Inness, Babington, Cuixmala) |
| Serif body | 15 |
| Platform | custom/other 24, WordPress 18, Squarespace 5, Webflow 2, Wix 1, Shopify 1 |
| Horizontal overflow at 390 px | 5 (Ojai, Torrey Pines, Sea Ranch, Holman, Ebell LA) |

Compared with the mid-market survey (`01-venue-site-survey.md`): Showit/Wix almost vanish, custom builds dominate,
script faces vanish, badges nearly vanish, body sizes go up, and the hero is more often an inset photo with margins
(Blackberry, Amangiri, Castle Hill, Wythe, Twin Farms, Nestldown, Babington) rather than a full-bleed couple.

## 3. Synthesis: what consistently signals luxury

1. **Pacing and margins.** The expensive pages put air around everything: inset heroes with 40-80 px page margins
   (Amangiri, Blackberry, Castle Hill, Wythe, Twin Farms), one idea per screen, three to five sections on a wedding
   page (Blackberry has three). Babington's "hero" is a paragraph. Generic pages stack 8-12 sections and 3-up card
   rows.
2. **The place, not the couple.** Ojai, Sea Ranch, Weylin, Santa Lucia, Cuixmala, Amangiri, Sunstone and Cherry
   Hollow open on the land or the building with no people. Couple-first heroes (Maravilla, Early Mountain, Torrey
   Pines, Brush Creek) read as marketing. Where a couple appears on a premium page they are small in a big frame
   (San Ysidro, Wildflower, Holman).
3. **Restraint in colour.** Cream or warm-grey paper plus one deep accent taken from the property: Rosewood's green,
   The Ranch's olive/ochre, Santa Lucia's oxblood, Inness's terracotta, Parker's orange, Sunstone's taupe. Pure white
   plus a saturated button (Early Mountain red, Maravilla teal, Rancho Valencia orange) reads cheaper. Black grounds
   work when the photography is dusk or candlelit (Oheka, Weylin, Hotel Emma, Montage).
4. **Type that is large, light and spaced, but not hairline.** Two luxury registers recur: (a) a light transitional or
   garalde serif at 44-84 px in sentence case (Korakia 67, Inness 73, Cherry Hollow 84, Serra 160, Blackberry 58,
   Ventana 56), and (b) small tracked caps at 14-48 px with +2 to +8 px letter-spacing (Rosewood, Oheka, Cuixmala,
   Amangiri, Greenhouse Loft, Ebell LB). Weight 100 (Terranea, Inness, Shou Sugi Ban) and auto-opsz didones
   (Shou Sugi Ban's Bodoni italic) go hairline on photos; the sites that look best run 300-500. Body copy at 18-24 px
   with a serif (Babington 24, Auberge weddings 24, Cuixmala 23, Montage 20) is a tell on its own.
5. **Ornament is small and singular.** A monogram or crest (Oheka, Cherry Hollow, Blackberry, San Ysidro, Wildflower,
   Hotel Emma), a hairline rule under a centred heading (San Ysidro, Castle Hill), one engraved botanical (Hotel
   Emma, Nestldown), numbered rows (Wythe, Auberge weddings). Nobody expensive stacks ornaments; nobody expensive
   uses wave dividers (Ebell LA), parchment textures (Beaulieu), or star ratings (Wildflower, Bella Collina).
6. **Slow, few, deliberate motion.** Cross-fade slideshows with a counter (Rosewood "1 — 2"), smooth scroll (Parker,
   Wythe, Ventana, Inness), one scroll cue chevron (Cherry Hollow, Sunstone). Autoplay video is common (14) but the
   good ones are landscape and slow, under a light or no scrim; Montage's near-black scrim and Bella Collina's white
   scrim both flatten the photo.
7. **Copy that states facts, briefly.** "Occupying a Grade II-listed manor built in 1705" (Babington), "A nature
   reserve of more than 30,000 acres" (Cuixmala), "13,000 square feet… up to 200 guests" (Wythe), "Up to 450"
   (Serra). The cheaper pages use adjectives ("Luxury Western Weddings", "Majestic and Magical", "Orlando Luxury
   Weddings"). Saying "luxury" is the surest sign a page is not.
8. **Confidence about money and dates.** Greengate and Brush Creek put "Wedding pricing" in the header, Greenhouse
   Loft publishes rates, Serra Plaza's header button is "See your date & price", Ebell LB has "Pricing" in the nav.
   These are rare (15 of 51 mention price at all) and read as confidence, which matches the conversion evidence in
   `02-market-conversion-seo.md`.
9. **The inquiry CTA is quiet and placed once.** Outlined or small solid button in the header ("Submit inquiry →",
   "Inquire here", "See your date & price") and one closing band. The loud versions (red "Contact us" on the hero,
   three stacked gold buttons, "Get my free wedding booklet") belong to the funnel-first pages.

### What cheapens an otherwise good property

- Award badges inside the hero (Monserate, Ebell LB) and badge/logo strips high on the page (Ebell LA, Bella Collina).
- Popups on arrival: newsletter + notification (Inn at the Mission), offers (Inness), mailing list (Greengate),
  age gates (Holman), closure notices (Sea Ranch). Cookie banners are unavoidable but the premium sites keep them
  small and neutral (Aman's is a centred card in its own type).
- Heavy scrims in either direction (Montage black, Bella Collina white).
- Tracked caps used for paragraphs (Glenmere mobile) or hairline weights on photos (Terranea).
- Generic faces in the generic pairing: Playfair + Arial (Monserate), Montserrat everywhere (Greengate, Glenmere,
  Brush Creek), Raleway (Maravilla, Early Mountain). Script headlines (Nestldown) and typewriter body (Hotel Emma).
- Template tells: wave dividers, parchment textures, YouTube embeds in the content column (Beaulieu, Vizcaya), 3-up
  equal cards with "Learn more", star ratings, two-row dropdown navs with 14 links (Rancho Valencia).
- Couple close-ups as the hero on a venue page (Maravilla, Torrey Pines).
- Slider carousels of everything (25 of 51 ship one; the expensive pages use them for filmstrips of interiors, not for
  the hero).
- Group CMS chrome that erases the property (Hotel Bel-Air inside Dorchester, Montage x2, Auberge x3 share one chassis).

### How the successful ones still differ from each other

The premium band is wide. The same restraint is executed in at least seven distinct voices in this sample:

| Voice | Examples | What varies |
|---|---|---|
| Old-world / crest | Oheka, Sunstone Villa, Glenmere, The Clifton | black or taupe ground, tracked caps garalde or Mrs Eaves, crest, double buttons |
| Romantic editorial | Cherry Hollow, Wildflower 301, Castle Hill, Wythe | Didot/Playfair at display size, drop caps, italic lead-ins, inset photos, blush or white paper |
| Quiet modern luxury | Amangiri, Shou Sugi Ban, Cuixmala, Ventana | small tracked sans or Lyon-class serif, grey/cream paper, nothing bleeds or everything bleeds, slow video |
| Dark and candlelit | Hotel Emma, Weylin, Montage, Oheka | black/charcoal ground, gold or brass accent, dusk/candle photography, frames |
| Coastal / airy heritage | Castle Hill, Twin Farms, Rosewood, Blackberry | white paper, navy or green accent, inset 16:9 photo with margins, serif + small caps |
| Rustic-refined / ranch | The Ranch at Laguna, Santa Lucia, Holman, Inness | olive/ochre/oxblood/terracotta, landscape heroes, cream bands, light serif or odd display sans |
| Loft / architectural | Greenhouse Loft, Sea Ranch, Parker | type-only hero or supergraphic, caps grotesk + italic serif, published rates, one eccentric colour |

Across these the levers that actually change are: paper tone (white / cream / oatmeal / grey / blush / black), the
accent's source, the display face class and its case, whether the hero is inset or bleeds, whether it has a headline
at all, the ornament (crest / rule / frame / botanical / none), the body size, and the one motion device. Everything
else (header with a wordmark, a spaces section, an inquiry band) is shared and does not need to vary.

### Which dimensions buy the most perceived uniqueness for the least build effort

Ranked by (visual difference seen in the sheets) ÷ (template work):

1. **Paper tone + accent source** (tokens only): cream vs blush vs oatmeal vs charcoal changes the whole page at zero
   template cost. Sunstone's taupe, Wythe's blush, Greenhouse's oatmeal and Oheka's black are instantly different.
2. **Hero framing: inset-with-margins vs full-bleed vs type-only vs no-hero-paragraph** (one template each): Blackberry,
   Ojai, Greenhouse Loft and Babington are four different sites before any colour is applied.
3. **Display face class + case + size** (pairing data): tracked small caps (Rosewood) vs 84 px sentence-case Didot
   (Cherry Hollow) vs 160 px garalde name (Serra) vs light display sans (Inness).
4. **One ornament** (an inline SVG each): crest, hairline rule, double-line frame, botanical engraving, drop cap,
   numbered rows. Hotel Emma's frame + engraving is the only thing on that page that is not a template.
5. **Body size** (a token): 16 px vs 22 px changes the pace of reading more than any font choice.
6. **Motion device** (one JS module): slide counter cross-fade, smooth scroll, scroll cue, count-up numbers.
7. **Section count** (content rule): three to five sections reads premium; eight reads template.

## 4. Mobile treatments (390 px)

- The premium pages keep the hero photo tall (San Ysidro, Montage, Sunstone, Oheka all fill the first screen) and move
  the headline below it onto paper (Terranea, Ventana, Cherry Hollow, Castle Hill, Holman). Text-on-photo on mobile is
  rarer and smaller (Bella Collina, Maravilla).
- Serif headlines hold at 30-44 px on mobile; tracked caps shrink to 20-28 px and still read (Oheka, Rosewood).
  Glenmere's caps paragraph and Houdini's stacked grey nav tiles show what not to do.
- Headers collapse to wordmark + burger, with the booking/inquiry button kept visible (Terranea "Book now",
  Oheka's two full-width buttons, Rosewood's full-width green "Reserve" bar at the bottom of the fold).
- Five sites overflow horizontally at 390 px (Ojai, Torrey Pines, Sea Ranch, Holman, Ebell LA), always from a wide
  nav row or an unconstrained hero element. The factory's QA already fails this.
- Cookie banners take 30-50% of the first mobile screen on about half the sample; the Aman and Auberge banners are
  the least damaging because they match the site's type and sit in a card.

## 5. How not to look generic (checklist for the factory)

1. Open on the place. A couple may appear only if they occupy under ~10% of the frame.
2. Choose the paper first (cream, oatmeal, blush, warm grey, charcoal), then one accent measured from the photos;
   never white + saturated button.
3. Display face from a vetted pairing, pinned weight 400-600, pinned opsz; sentence case at 48-96 px or tracked caps
   at 14-40 px; never weight ≤ 300 on a photo, never a script face, never Playfair/Montserrat/Raleway.
4. Body 17-22 px; a serif body is allowed and reads premium.
5. One ornament per site, chosen from the dialect's set; never a wave divider, parchment texture, star rating, award
   badge in the hero, or logo strip above the fold.
6. Hero framing is a deliberate choice between inset-with-margins, full-bleed landscape, type-only, or paragraph-first;
   the scrim is never darker than 35% or lighter than 20% white.
7. Three to five sections before the inquiry band; facts in the first screen (guests, acres, year, spaces); price or a
   pricing-guide path visible in the header.
8. One motion device, slow (600-1200 ms), reduced-motion safe; no slider for the hero; no popups on arrival.
9. The inquiry CTA appears once in the header (outlined or small solid, 2-4 words) and once as a closing band.
10. Copy states facts and places; the word "luxury" is banned from headlines.

## 6. Verification

All 50 venue URLs cited in the table were re-opened on 2026-10-21 with curl (Chrome UA, following redirects);
raw results in `verify-final.txt`. 46 returned 200. Four returned 403 to curl but had rendered normally in headless
Chromium a few hours earlier (Playwright status 200, screenshots in `shots/`): Terranea, Inn at the Mission, Vizcaya
and Hotel Bel-Air (Dorchester). Treat those four as bot-walled to non-browser clients, not as dead. Every Google
Fonts family named in `05-luxury-dialects-spec.md` was fetched from fonts.googleapis.com/css2 with the exact axis
string used in the spec; 20 of 20 returned 200 (`fonts-check.txt`).
