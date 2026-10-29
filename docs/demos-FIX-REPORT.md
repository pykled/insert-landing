# Demos fix round: report (Maker, 2026-10-29)

Fixes for `docs/demos-CHECK.md` must-fix 1-7 and the cheap nits. Made in the factory (templates, build.py, qa.py, voices, content JSON), so every future demo gets them. The three demos were rebuilt with `factory/new-demo.sh <url> <slug> --from build` (REGISTER=1; Lindley with `BUILD_ARGS="--force pairing=estate-caslon"`, as before) and re-staged locally into `private-previews/2d32be7dda6d361dd89ffdfd/demos/<slug>/`. Nothing deployed, pushed or sent. The preview dirs are still untracked. Other people's WIP (index.html, venues.html, fonts-verified.json and so on) was not committed. I am not the approver; a fresh Checker should re-verify.

## Per item

| # | Change | Commit |
|---|---|---|
| 1 | New `partials/preview-notice.j2`, placed before the nav in `base.html.j2` on every private build: "An unsolicited concept by Insert, not made by or affiliated with <venue>." It is ink on paper at 14 px, 15.4-17.0:1 measured on all three at both widths. The footer chip is now built by `build.preview_chip()`: "Unsolicited concept by Insert · <photos.credit> · not affiliated with <venue>", solid background, ink text, ≥7:1, 13.5 px. `qa.py` now fails a noindex preview if the notice is missing, lacks the words, falls outside the first viewport, is under 13 px or under 7:1, if the chip lacks "unsolicited", or if either is under 7:1 in the pixel contrast pass. `preview.py` injects its fallback chip when "Unsolicited concept by Insert" is missing. | d591ba7, 1a16c66, 08ee2ff |
| 2 | All 4 footers now link `Insert privacy policy` to `https://insert-landing-production.up.railway.app/privacy.html` (`build.INSERT_PRIVACY_URL`; returns 200 today). `qa.py` fails any `href="#"` and any footer privacy link outside Insert's site. | d591ba7 |
| 3 | `build.confirmed_press()`: the press row renders only if every `featured_in` entry is `{name, source, confirmed: true}`. Bare strings drop the whole row and the build logs a warning. Stonehurst `featured_in` is now `[]`, with a note: the homepage strip is logo images and only 4 of 8 outlets matched as text. `schema.md` updated. | d591ba7, b575a3a |
| 4a | Lindley `contact.hours` = "Open Mon–Thu by appointment only; Fri–Sun 10–11 am", from the FAQ ("Our hours of operation are: Mon-Thur by Appointment Only Fri, Sat and Sun 10:00am – 11:00am"), re-fetched today with curl. The source and quote are in `hours_note`/`hours_source`. "Monday to Sunday" no longer appears anywhere on the page, and the JSON-LD no longer carries hours. | 5d53941 |
| 4b | Heritage voice `guide_title` changed from "The pricing guide, in full." to "Pricing, on request." CTA set 1 `guide_cta` changed from "Send the guide" to "Ask for pricing". | 5d53941 |
| 5 | Stonehurst filming FAQ answer is now "For filming and photoshoots, email thestonehurst@gmail.com." (FAQ: "please email thestonehurst@gmail.com"). The JSON-LD no longer has an FAQPage. | b575a3a |
| 6 | **Names kept.** The raw HTML of homesteadoakglen.com/about signs its welcome "Don and Paula Christante, Owners" (fetched with curl today). Readability-style extractors drop that line, which likely explains the Checker's miss. The site's TLS certificate had expired today, so web_fetch failed and curl -k was needed. A `verified` note was added to the `owners` fact. | 8a155f5 |
| 7 | `build.jsonld()`: private builds emit only a `WebPage` ("Concept homepage for <venue> (unsolicited, by Insert)") with creator Insert (Insert URL) and `about` a Place: name plus locality/state. There is no @id or url at the venue domain, no phone, email or FAQPage, and no EventVenue/LocalBusiness. Public (engaged) builds keep the old graph. `qa.py` fails EventVenue/LocalBusiness/telephone/email/@id, or a url outside Insert, on a noindex page. | d591ba7 |

Nits:
- New `{per_day_noun}` slot, from `tagline_facts.events_per_day_noun` (default "event"). Stonehurst and Lindley now say "One event a day"; HomeStead keeps "wedding", citing its booklet.
- Stonehurst stone-path alt is now "A stone-paved path…" (no "hand-laid cobblestone"). The barn now "greets you as you enter the property".
- HomeStead: "~180 / guests, comfortably" and "for about 180 guests"; the saw caption is now "An old saw blade among the grasses". These are in b575a3a and 8a155f5.
- The first spaces image in every spaces template now loads `eager` with `fetchpriority="low"`. For spaces-index this is the first desktop stage image (79736d0).
- The top-level README documents running factory tests from `factory/` (79736d0).

Not done:
- Lindley page weight is still 1589 KB at load (warning only).
- The HomeStead diversity warning is unchanged (0.481 vs stonehurst-b, inside the warn band).
- The `© <legal_name>` footer line was kept; the notice and chip now state the relationship.

Tests added: `factory/tests/test_demos_fix.py` (notice/chip, no `href="#"` + Insert privacy URL, press gating, private JSON-LD). Updated: `test_templates.py` (the Stonehurst heritage headline is now "Nine acres. One event a day.") and `test_stage3a_part2.py` (chip text).

## Commands and results

| Check | Command | Result |
|---|---|---|
| Rebuild + strict QA + stage | `REGISTER=1 [BUILD_ARGS=...] zsh factory/new-demo.sh https://x <slug> --from build` (runs `python3 factory/qa.py .factory-check/demos/<slug> --strict`, then preview.py) | homestead exit 0, PROBLEMS 0, WARNINGS 1 (diversity 0.481). lindley-scott exit 0, PROBLEMS 0, WARNINGS 4 (1589 KB at load; Caslon hairline shares, unchanged). stonehurst exit 0, PROBLEMS 0, WARNINGS 2 (Cardo hairline shares, unchanged). Guards: HS WARN 0.481, LS OK 0.551, SH OK 0.620. The first HomeStead QA run hit a page.goto timeout against the local http.server; it passed on a re-run (`--from qa`). |
| Full suite | `cd factory && python3 -m pytest -q tests` | 127 passed in 530 s (exit 0) after 1a16c66; re-run at final HEAD 08ee2ff: **127 passed in 523 s (exit 0)**. |
| Screenshots | Playwright, 1440x900 and 390x844, fold + footer after scroll-through: `.factory-check/fix-shots/<slug>-<w>-{fold,footer}.png` (untracked; venue photos) | All six viewed. The notice bar is the first thing on every page and readable at 390 (wraps to two lines). The chip wraps cleanly. Horizontal overflow 0 on all six. |
| Staged-page grep | `private-previews/<token>/demos/<slug>/index.html` | Each has 1 notice, 0 `href="#"`, 1 Insert privacy link, 0 LocalBusiness/EventVenue/telephone, 0 featured row, 0 "Monday to Sunday", 0 "availability and rates", 0 "in full", 0 "cobblestone". |
