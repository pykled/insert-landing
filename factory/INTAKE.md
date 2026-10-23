# Demo pipeline: venue URL to private preview

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
6. Vibe: type from the controlled list, three words from `data/dialects.json` `vibe_words` that the site and photos
   actually support; era only with a stated build year and `era_source`.
7. `python3 factory/lib/schema.py content/<slug>.json` must report 0 errors.

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
- PDFs are skipped by the crawler; brochure facts (HomeStead's capacity, vendor rule, FAQ) are read by the reviewer.
- No face detector offline here (OpenCV not installed): people are checked by eye on every chosen photo.
- `--max-photos` (default 120) can stop before the end of large galleries (HomeStead: 28 not downloaded).
- Some templates assume Stonehurst's `day` fields (`rental_hours`, `event_end`) and a non-null `region`; content without
  them must avoid those sections or the templates must null-guard (see the two content files' `_note`s).
- Real builds currently fail `qa.py --strict` on some pairings (Cinzel hairlines) and `preview.py` refuses the existing
  2400w WebP ladders (440-670 KB > 400 KB); the image budget in `lib/images.py` must drop under 400 KB per file.
