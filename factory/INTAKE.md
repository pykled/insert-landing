# Demo pipeline: venue URL to private preview

**Wedding venues only, for now (2026-10-23).** Insert is niching down to wedding venues first, so this pipeline is
wedding-venue-specific: weddings are the lead offer on every demo. The tagline (`tagline_facts.uses[0]` = `Weddings`), the
hero copy (`copy_overrides` hero_kicker / hero_headline / hero_lede), the spaces framing (spaces_title / spaces_lede and
each space's `use`) and the vibe block (`vibe.lead_offer: "weddings"`, words that describe the wedding day) are written
wedding-first. Other event types (filming, private events, corporate, quinceañeras) appear only as secondary lines
(`uses[1:]`, the closing uses band, the footer) and only when the venue's own site states them; never as a headline.
Intake runs a **wedding-first check** and flags any venue where weddings are not clearly primary; a flagged venue is not
built until a person confirms it fits.

Goal: give it a venue's homepage, get a verified content file, its photos and a private preview in under an hour, while
every site stays unlike the others (the dialect scorer + the registry guard decide the design, not a person picking a
template). One command runs it with pause points:

```
factory/new-demo.sh https://venue.example/ <slug>                 # all stages, pauses for review
factory/new-demo.sh https://venue.example/ <slug> --from validate  # resume after the review
factory/new-demo.sh ... --from build --to qa                      # any stage range: intake review validate build qa preview
```
Env: `LEAD=<photo>` (default `hero`), `BUILD_ARGS="--force hero=frame ..."`, `REGISTER=1`, `NONINTERACTIVE=1`.
Every stage appends `date  slug  stage  seconds  kind` to `factory/data/timings.log`.

## Stages

| # | Stage | Tool | Kind | Measured (2026-10-23) |
|---|---|---|---|---|
| 1 | intake | `intake/intake.py <url> --slug <slug>` | automated | 200 s (13 pages, 41 photos) to 362 s (14 pages, 119 photos, robots.txt Crawl-delay 10 s); re-runs 22-242 s (photos cached) |
| 2 | review | a person or reviewing agent, `intake/curate.py` | judgement | agent: 5.3 min and 9.5 min; a person doing the same checks: estimate 30-45 min (not yet measured) |
| 3 | validate | `lib/schema.py` + `intake/score.py` | automated | 1 s |
| 4 | build | `build.py --dialect auto` | automated | ~2 s plus font checks |
| 5 | qa | `qa.py --strict` (local http.server :4821) then `preview.py --mark-qa-strict` | automated | ~35 s |
| 6 | preview | `preview.py <build> --name <slug>` | automated | < 1 s |

So the automated part is about 4-7 minutes per venue and the hour is almost all review. Deploying the staged preview is a
separate, approved step (Insert deploy skill); nothing in this pipeline pushes, deploys or contacts anyone.

### 1. Intake (automated)
- Polite crawl: robots.txt respected (its Crawl-delay too), at least 1 s between requests to any host, same registrable
  domain, public HTML only. Follows the homepage's nav links first, then sitemap.xml (page sitemaps before post sitemaps),
  blog-like paths last; skips PDFs, admin, carts, feeds, tag/author archives and off-site booking portals. `--max-pages 30`.
- Extracts only what pages state, each fact with its source URL and a confidence (structured data or link = high, a
  pattern on the page = medium, heading heuristics = low): name, address, phones, emails, socials, JSON-LD
  (LocalBusiness/EventVenue/FAQPage), meta description, spaces (headings with a space noun + following text + stated
  capacities), capacities, hours, rules, prices (only sentences with a $ figure), FAQ pairs, featured/award blocks, history
  paragraphs, uses, tools (HoneyBook, Dubsado, Calendly, Acuity, Planning Pod, Tripleseat, builders, pixels).
  Unknown fields stay null. History excerpts and space text go into `_intake` / `_excerpt`, never into rendered slots.
- Photos: img/srcset/data-srcset/picture/og:image/lightbox links/CSS backgrounds/Wix and Showit media URLs, grouped per
  distinct photo, largest variant first (Wix original, Showit `variant/3200`, WordPress original without `-WxH`,
  Squarespace `format=2500w`). Discards logo/icon-like names, anything under 800 px wide, pHash duplicates. Flags likely
  stock files (`stock? yes`). Per photo: size, orientation, sharpness, the `lib/palette.py` signals the dialect scorer uses,
  three dominant colours, a light guess, subject/flora guesses from alt text, faces via OpenCV when installed (else
  `unchecked`).
- Wedding-first check (`intake/wedding.py`): counts wedding terms against other-use terms (corporate, quinceañera,
  birthday, filming, private events and the like) over three units of the venue's own site: each page (own text + URL
  path, site chrome and text repeated on most pages removed), each distinct heading, and each testimonial on its own pages
  (a block opening with a quote mark, or text on a testimonials/reviews page). Share = wedding / (wedding + other), neutral
  units left out. Verdict `primary` when every share and the overall term share are >= 60%; `not primary` when the page or
  term share is under 40%; otherwise `mixed`. Anything but `primary` goes to the top of `review` as a FLAG. The report
  opens with the table, the other uses the site names (secondary-line candidates) and the pages led by other uses. The
  draft puts `Weddings` first in `uses` whenever the site says weddings at all. Re-run on a past crawl:
  `python3 factory/intake/wedding.py <slug>` (reads `_pages/`, exit 1 when flagged).
  2026-10-23: HomeStead primary (pages 92%, headings 90%, reviews 100%, terms 94%); Lindley-Scott primary (73/89/100/78%).
- Writes `content/<slug>.draft.json` (schema shape + `review` list + `_intake`), `content/<slug>.intake-report.md` (facts,
  photos, discards, needs-a-human list, suggested vibe, dialect shortlist, crawl log) and, gitignored,
  `content/photos/<slug>/` (pNN.jpg, manifest.json, `_pages/*.txt` page text for checking facts).

### 2. Review (judgement)
The reviewer writes `content/<slug>.json` from the draft. Checklist:
1. Open `_pages/*.txt` (or the live pages) next to the draft. Keep a fact only if a page of the venue's own site, or a
   document the site links (cite its URL), states it. Cite the URL on every fact, space, FAQ, number and timeline entry.
2. Rewrite every sentence as a short factual paraphrase. FAQ answers: one or two sentences.
3. Drop third-party ratings and review counts, testimonials, reviewer phrases, and anything time-varying.
4. Leave unknowns null (region, rental hours, build year). Put the reason in a `_note`.
5. Photos: `python3 factory/intake/curate.py <slug> --sheet`, look at every sheet, choose 8-14 (the place first, sharp,
   varied: wide grounds, buildings, spaces, a detail, an evening shot if any), then name them:
   `python3 factory/intake/curate.py <slug> hero=p07 barn=p12 ...`. Write alt text from what the photo shows and a caption
   (<= 60 characters). Tag `subject` and `light`; `flora` only if the site names the plant.
6. Wedding-first: read the check in the report; if it is flagged, stop and ask before building. Set `uses` to
   `Weddings` first, then only other uses the site states (each with its page in `_uses_note`). Write `copy_overrides`
   (hero_kicker, hero_headline, hero_lede, spaces_kicker, spaces_title, spaces_lede, footer_blurb) as wedding-first lines
   built only from stated facts, give each space a wedding `use` (ceremony, getting ready, reception), and copy the check's
   shares into the content file's `wedding_first` block.
7. Vibe: `lead_offer: "weddings"`, type from the controlled list, three words from `data/dialects.json` `vibe_words` that the site and photos
   actually support; era only with a stated build year and `era_source`.
8. `python3 factory/lib/schema.py content/<slug>.json` must report 0 errors.

### 3-6. Validate, build, QA, preview (automated)
`score.py` prints build.py's dialect table for the reviewed file (with and without the vibe block). `build.py --dialect auto`
takes the top dialect and the registry guard refuses a site too close to a registered one (change `--force`/`--lead`).
`qa.py --strict` must exit 0; `preview.py --mark-qa-strict` records the pass with the index.html hash. `preview.py` copies
only index.html and the images it references to `private-previews/<token>/demos/<slug>/`, adds the noindex meta and the
"Concept preview by Insert" chip in the staged copy if the build lacks them, and refuses on a missing or stale QA pass, a
referenced file outside the build, or any image over 400 KB. `preview.py --remove <slug>` deletes it (venue declined).

## Never allowed
- Invented facts: no number, phone, address, capacity, price, year or award that the venue's own site does not state.
- A people photo as the lead (exclusion 6). People may appear small (< 10% of the frame) in place photos.
- Copying another site's text: paraphrase; fixtures and content files never carry a venue's paragraphs wholesale.
- Public hosting of a venue's photos: photos stay in the gitignored `content/photos/`, previews live only under the
  unlisted token path (noindex, robots-disallowed, X-Robots-Tag), and a declined venue's preview is removed.
- Stock images presented as the venue (intake flags likely stock; the reviewer drops them).

## Known gaps (2026-10-23)
- Fixed 2026-10-23 for wedding-first: the closing uses band now shows only non-wedding uses from `uses[1:]` (and is left
  out when there are none, e.g. HomeStead), with shoot wording only when filming is among them; the nav bar falls back to
  the state when `region` is null; JSON-LD description and the tour list no longer print "None"; `copy_slots` null-guards
  `day.spaces_per_event`. Still open: `seo.title_tail` is hard-coded "Garden Wedding Estate in <locality>" for every venue.
- `copy_overrides` are applied by `build.py` from 2026-10-23 (before that only `--copy` on the command line worked).
- PDFs are skipped by the crawler; brochure facts (HomeStead's capacity, vendor rule, FAQ) are read by the reviewer.
- No face detector offline here (OpenCV not installed): people are checked by eye on every chosen photo.
- `--max-photos` (default 120) can stop before the end of large galleries (HomeStead: 28 not downloaded).
- Some templates assume Stonehurst's `day` fields (`rental_hours`, `event_end`) and a non-null `region`; content without
  them must avoid those sections or the templates must null-guard (see the two content files' `_note`s).
- Real builds currently fail `qa.py --strict` on some pairings (Cinzel hairlines) and `preview.py` refuses the existing
  2400w WebP ladders (440-670 KB > 400 KB); the image budget in `lib/images.py` must drop under 400 KB per file.
