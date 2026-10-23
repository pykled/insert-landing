# /venues rehaul: Checker round 2

2026-10-23. Checker (did not build the fixes). Local only: nothing pushed, deployed or sent; every `/api/*` call was aborted by Playwright. Commits 4d18a8f..107abc0. Test scripts in `/tmp/ck/*.py` (not committed).

## Verdict: PASS-WITH-CONDITIONS

All five round-1 must-fixes are resolved in substance. Conditions to promote are small and are decisions or one-line checks, not layout work (section 5).

## 1. Round-1 must-fix list

| # | Round-1 item | Status | Evidence |
|---|---|---|---|
| 1 | Calendly white slab + dead strip | **FIXED (with a cosmetic remainder)** | Widget renders at 1440 (iframe 602 px) and 390 (602 px) after Calendly's `page_height` message; `data-resize` works and the frame is 626/618 px, so nothing clips. Placeholder (grid + "Loading calendar…") is visible at t=1 s. With `calendly.com` blocked, the fallback ("Open it in a new tab" / "email us through the form") appears by t=14 s at both widths and the placeholder message hides. Ivory mat with a linen hairline looks intentional, like a printed card set into the dark band. Remainder: Calendly's white interior, slate "Powered by" ribbon and blue day pills are off-palette (free plan, cannot be themed), and about 100 px of blank white sits under the time zone picker before a date is chosen (Calendly's minimum height). It reads as card padding, not a bug. |
| 1b | Fallback email real/working | **OK, by design there is no email** | `dig MX useinsert.com` returns nothing, so a mailto would bounce. The fallback links to `#contact-form` (exists, scrolls to top) and the Calendly URL. No address appears anywhere on the page. |
| 2 | Focus rings on every control | **FIXED** | Tab-through at 1440 (20 stops) and 390 (18 stops), ring measured as the pixel diff between focused and blurred screenshots (real rendered pixels). Bronze ring on ivory/linen/card: 7.84 to 8.54:1. Gilt ring on night band, inputs, button, footer: 9.44:1. Header "Book a call" and brand 7.84:1. Skip link 15:1. Inputs now have a real 2 px ring. Only the Calendly iframe interior is out of our control. |
| 3 | Promote script overwrote its backup on re-run | **FIXED** | See section 3. |
| 4 | "no-show follow-up" weakened | **ACCEPTED** | Now "a gentle reschedule note goes out if a visit is missed", which is the one-pager's no-show follow-up in softer words. |
| 5 | Claims beyond one-pager | **FIXED, 4 nits** | Contract, "deposit received", signed-date and payment-processing language all gone. Reply time is hedged ("typically", "usually", "we aim", "under a minute" tied to aim). No "%" anywhere, no 1% fee. $300 "locked for as long as you remain a partner". Nothing to pay until live, six-month minimum then month to month, build free, later partners $3,000-$4,500 + $500-$600, refresh from $2,500 and separate: all match. Nits (illustrative, not in the one-pager): sample card says "Replied in 40 seconds"; reminders "the day before, two hours before"; review request "a week after... Google or The Knot"; "They work with the tools you already use"; "two venues first" (seat count is not in the one-pager). "The full build, at no cost" should say "no build charge" to sit beside $300/month. |
| 6 | og image | **FIXED** | `assets/og-venues.jpg` is a real 1200x630 progressive JPEG, 98 KB (limit 250 KB), tracked in git, served by `express.static` (not in `.dockerignore`). Local fetch is byte-identical to the file. `og:image` and `twitter:image` are `https://insert-landing-production.up.railway.app/assets/og-venues.jpg`, matching the path exactly. The live host currently returns `200 text/html` for it because it is not deployed yet; re-check after deploy that it returns `image/jpeg`. The card looks good, with a small orphan ("BY / APPLICATION"). `og:url` is on the Railway host while `canonical` is `useinsert.com`: harmless but inconsistent. |
| 7-9 | Orphans, label sizes, role=img, charter focus, rhythm, wireframe thumbnail | **MOSTLY FIXED** | Cards now `role=group`-style with text; "Sample" tag visible; charter card is clearly the focal point (raised ivory card with double rule on linen, $300 in display serif); rhythm varied (lead mount, bare framed card, left-set tight card, photo with overlap); Site Refresh is a sharp photo print in a frame. Label sizes are still 14-16 px (see section 2). |

## 2. Technical sweep (1440 and 390, 2x where relevant)

| Check | Result |
|---|---|
| Text contrast, rendered pixels (text hidden, background sampled, 104 / 102 nodes in view) | 0 failures, worst 6.91:1 (bronze "Sample" tag on linen) |
| Horizontal overflow at 320/390/768/1024/1440/1920 | none (`scrollWidth` equals viewport; only the off-screen skip link) |
| Mobile body size | paragraph median 18 px. Still under 17 px at 390: header "Book a call" 15, buttons/links/notes/labels/card meta 16, "Sample" tag 14, footer copyright 14.2 (all secondary UI, not running body) |
| Console | only Calendly third-party noise (`requestStorageAccess`, WebGL/adapter warnings from its iframe in headless). No first-party errors |
| Failed requests / 4xx | none besides the ones I aborted on purpose |
| Image sharpness at 2x | all `<img>` have natural width >= displayed x 2 (hero 1240/1240, roses 610/621, evening 660/621, refresh 300/272) |
| Anchors | `#stack #charter #book #contact-form` all land at top 0 (smooth scroll settles after about 2 s) |
| Mobile nav | header shows brand + "Book a call" only; "How it works"/"Charter seats" hidden below the breakpoint (still in footer). Header is not sticky |
| Reduced motion | no hidden `.reveal`, 0 running animations, `scroll-behavior: auto` |
| Form | submit sends exactly one request, `POST /api/contact`, body `{"name","email","business":"Wedding venue (/venues) — Oak Test","message"}`. Field names, the business tag and the submit JS are identical to the old live page except friendlier copy. Abort shows "Network error. Please try again." |
| Analytics | `/api/track` is suppressed when the path contains `private-previews`; after promotion it fires exactly like the old page |
| Weight | about 550 KB at 390 and 610 KB at 1440 after scrolling the whole page (300 KB of that is web fonts); first view 107 KB local + fonts |
| Cold load, 9 Mbps / 170 ms RTT, 4x CPU on mobile | load 1.1 s, FCP 0.52 s, LCP 0.94 s (390); load 1.0 s, LCP 0.86 s (1440) |
| Heading eyebrow spacing | eyebrow sits about 6-8 px above centered `h2`s ("The Venue Ops Stack", "An Invitation", "Book a call"); tight, reads as touching |

## 3. Promote script (temp copy of the repo only)

- First run: backup written, `venues.html` equals the preview. Second run printed "backup exists, keeping it"; `cmp` shows the backup is still the original page.
- Rollback line (`cp scripts/backups/venues.prev.html venues.html`) restores a byte-identical original.
- With no backup and `venues.html` already equal to the preview, it refuses with an explanation.
- Asset paths stay absolute (`/assets/venues2-*.webp`, `/assets/og-venues.jpg`) and resolve under `/venues`; all 12 referenced assets exist and are git-tracked.
- `scripts/` is excluded from deploys, so the backup does not ship. Not run in the real repo.

## 4. LOOK (senior designer read)

It is now elegant and hospitality-grade, not techy. Warm paper ground, one serif with a single italic phrase per heading, tracked-caps labels, hairline rules, candlelit photography, and a dark closing band. The charter section is the strongest part: the raised, double-ruled invitation card with a large serif "$300 a month" is a real focal point and feels like a printed invitation. The varied card mounts (tinted mat, bare framed card, photo with overlapping card) break the repetition that round 1 criticised. Mobile holds up: single column, generous leading, full-width ink buttons. The Calendly mat is believable as a deliberate print on the dark band.

Still weak, ranked:
1. **Calendly interior is off-brand** (white, slate ribbon, blue pills) and has about 100 px blank under the picker. Only a paid-plan theme or a custom booking flow fixes it. Cheap mitigation: shorter min-height or a heading above the mat that sets the expectation.
2. **Eyebrow-to-heading gap is too tight** on every centered section head. Add 10-14 px.
3. **No persistent CTA on mobile**: header is not sticky and the nav drops to one button. On a 10,000 px page a slim sticky "Book a call" would help.
4. **Sample mat for the first card** is left-heavy: the card hugs the left of a wide tinted mat on desktop, leaving an empty right third.
5. **Site Refresh print is a candle photo, not a website**; it looks lovely but does not show the product. A real before/after homepage crop would sell it.
6. **Secondary text is 14-16 px**: header button 15, "Sample" 14. Raise to 16-17 on mobile.
7. Only three distinct photos, reused as crops.
8. og card orphan ("BY / APPLICATION").

## 5. Conditions to promote

Must (one-liners, none block the design):
1. Dillon approves the wording nits in 1.5: change "at no cost" to "no build charge", and confirm or cut "two venues first", the sample "Replied in 40 seconds" and the "Google or The Knot" detail.
2. After deploy, confirm `https://insert-landing-production.up.railway.app/assets/og-venues.jpg` returns `image/jpeg` (it returns HTML today because the file is not live yet) and that `/venues` serves the new page.
3. Deploy only with the promote script run once; keep `scripts/backups/venues.prev.html` until the live page is verified.

Should (follow-ups): items 2, 3 and 6 in section 4; point `og:url` and canonical at the same host once `useinsert.com` resolves (it has no MX or live site yet; add a real contact email only after MX exists).
