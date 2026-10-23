# /venues rehaul: Checker report

Checker run 2026-10-23. Not the builder. Local only: nothing pushed, deployed, sent or submitted (all `/api/*` posts were intercepted and mocked or aborted).
Files under test: `private-previews/2d32be7dda6d361dd89ffdfd/venues-rehaul/index.html` (md5 02cc20f2, identical to the Railway preview copy) vs current `venues.html`.
Method: own Playwright scripts (`/tmp/chk/*.py`, not the Maker's), real `server.js` run locally on 3111 (pg/resend stubbed), promote script run in a throwaway rsync copy on 3112.

## Verdict: PASS-WITH-CONDITIONS

The page delivers the brief. It reads as a boutique hospitality brand, terms are intact, the form payload is byte-identical to the old page, nothing overflows at six widths, and it is lighter than the old page. Conditions before promoting are in section 7.

## 1. Content / terms audit

Approved terms, new page vs old:

| Term | Old | New | Status |
|---|---|---|---|
| Two charter seats, by application | yes | hero note, section head, heading | kept |
| Free build | "Full build at no cost" | "The full build, at no cost" | kept |
| $300/month locked for as long as the venue remains a partner | "$300 per month, locked" | "Locked for as long as you remain a partner." | kept (now explicit, as approved) |
| Six-month minimum, then month to month | yes | "Six months, then month to month" | kept |
| Billing starts at go-live | yes | "Billing begins on your go-live date." | kept |
| Standard $3,000-$4,500 build + $500-$600/mo; charter keeps $300, skips build fee | yes | yes | kept |
| Site Refresh optional from $2,500, homepage preview on the call | "quoted on its own", "Ask on the call" | "from $2,500", "We'll bring a homepage preview to the call." | kept; $2,500 and preview are new on-page, both approved |
| No percentage fee | none | none (no `%` anywhere in visible text) | kept |
| Four automations | yes | yes | kept |
| Payments via venue's own link; Insert never processes | "deposit link" | "Payable to Willow Creek Estate through the venue's own payment link", "Couples pay you directly through your payment link" | kept, clearer |
| Willow Creek / Maya & Jordan illustrative | no disclaimer | explicit line "Willow Creek Estate and its couple are an illustrative example." plus "Sample ..." in every card aria-label | improved. The line is small italic below the 4th card; the first card, 1,400 px higher, carries no visible "sample" tag |
| Invented testimonials/clients/stats/awards/applicant counts/guarantees | none | none | clean |

Claims in the new page that are NOT in the old page:
1. "written in your voice and approved by you" (supported by the one-pager: venue approves every template).
2. "nothing left waiting until Monday"; "Moments later they have a personal answer" (copy colour, no number).
3. "We are opening the Venue Ops Stack to two venues first, and building it closely with them" (consistent with charter, no count claim).
4. "stay as long as it serves you" (soft restatement of month to month).
5. "Reminders: the day before, two hours before" (old: 24 h / 2 h; same).
6. "$2,500" and "homepage preview" (approved).

Claims DROPPED: the "You're losing bookings..." headline and "Couples inquire with several venues and book whoever replies first"; "< 60 s", "24 / 7", "Your part" tiles; the inbound text from Maya & Jordan; "Booked in 4 min", "Added to calendar", "Date locked", "Contract signed Thu 9:48 PM" timings; the notification stack; footer tagline "AI workflows for serious businesses" (brand line now only "Less busywork, more business."); **"no-show follow-up"** (old: "Self-serve booking, reminders, and no-show follow-up"; new: "if plans change, a gentle note offers another day", which is a weaker, different promise).

Inherited claims (in both pages) that go beyond the charter one-pager's four items, for Dillon/attorney to confirm, not regressions: a **contract** step ("the contract and a deposit request arrive", "Contract signed"); "**you hear the moment it's done**" / "Deposit received" / "a deposit paid" (implies payment-status notification; one-pager says deposit requests and reminders only); and the hero "a warm, personal reply **within the minute**" reads as a promise where the one-pager says the under-a-minute reply is "a target, not a promise".

## 2. Technical (1440 and 390 at 2x, own script)

| Check | Result |
|---|---|
| Contrast (every text node vs sampled rendered bg) | all pass. Two flags were measurement artifacts (offscreen skip link; a wrapped inline `<b>` whose bbox contained parent text). Lowest real pair: bronze `I` mark 5.28:1. Body/ink pairs 7:1+ |
| Body text on mobile >= 17 px | paragraphs 17+. Under 17: eyebrow labels, card headers and footers 15 px, buttons and the "30-minute conversation"/"Two charter seats" notes 16 px (MINOR) |
| Horizontal overflow | none at 320, 390, 768, 1024, 1440, 1920 (scrollWidth == viewport, no element past edge) |
| Console errors | only `requestStorageAccess: Permission denied` from the third-party Calendly iframe (localhost headless). None from page code |
| Failed requests / 4xx | none |
| Image sharpness | hero file 2400 px shown at 1240 css px = 1.9x; evening file 1600 px at 660 css = 2.4x; mobile hero 800 px at 390 = 2.05x. Sharp at 2x |
| Alt text | hero and evening have descriptive alt; the third `<img>` (Site Refresh thumbnail) is `alt=""` (decorative, fine). Cards are `role="img"` with a summary label, which hides the card's own text from screen readers (MINOR) |
| Heading hairline | Newsreader 500, measured stem 9-11% of font size at 88/60/40 px, no thin strokes at 1x. (At 2x my edge-thinness share reads 0.16-0.29 but that is anti-aliasing noise; stem width is the reliable number.) Not hairline |
| Keyboard | logical order: skip link, brand, nav, hero CTAs, charter CTA, refresh link, Calendly iframe, form, footer. Visible focus on paper: 2 px bronze outline. **Footer links on the dark band keep the bronze outline `rgb(92,69,41)` on night `rgb(27,23,18)` = ~2.0:1, effectively invisible** (MAJOR a11y). Form inputs use only a 1 px gilt box-shadow (weak, MINOR) |
| Reduced motion | 0 hidden reveals, 0 animations. Without it, 15 elements reveal on scroll; `.js` gate means no-JS users still see everything |
| Anchors | `#stack`, `#charter`, `#book` all scroll (book clamps at page end, fine). Header is not sticky (the Book a call button leaves with the scroll) |
| Mobile nav | only "Book a call" shown (How it works / Charter seats hidden below breakpoint); works |
| Weight / speed (cold cache, 1.6 Mbps / 150 ms) | same-origin transfer: new 195 KB desktop / 72 KB mobile vs old 293 KB / 116 KB. FCP 0.5 s both. `load` ~18 s in both pages is the Calendly/Stripe third-party chain, not page assets. LCP API returned null in this build |
| Widths | six widths looked clean; 320 h = 10,164 px, no clipping |

## 3. Form and Calendly

- POST `/api/contact`: JSON keys `name,email,business,message`, business prefixed `Wedding venue (/venues) — <venue>`; **payload identical to the old page** for a hostile input (`O'Neil & <b>Co</b>`, quotes, `<script>`, newlines) in all five scenarios. Nothing real was sent (route-mocked).
- States (mocked): 200 shows "Thank you. Your message is with us, and we'll be in touch shortly." and clears the form; 400 and 500 show the server's `error` string; non-JSON 502 shows "Something went wrong..."; network abort shows "Network error..."; button re-enables and relabels each time. Same logic as old, copy softened. Server-side HTML escaping is invisible to the client (payload is raw text both before and after).
- `/api/track`: no call on the preview path (guard is `pathname.includes('private-previews')`); one call `{"page":"/venues",...}` once promoted (verified in the promote copy).
- **Calendly**: the widget DOES render. The Maker's "empty box" is timing, not headless: the cross-origin iframe paints 3-7 s after load and the screenshots were taken earlier. Evidence: headless and headed Chromium both show the full "Select a Day" calendar after waiting 7-9 s, desktop and 390, on the live preview and locally; `Calendly` object defined, iframe 200, all Calendly requests 200. **Real problems seen**: (a) Calendly ignores the dark colour params and renders a bright white calendar inside the dark band, the single most off-palette element on the page (MAJOR visual); (b) the iframe is 640/680 px tall but the content ends ~500 px, leaving a dead dark strip under the white box on both widths; (c) the box has no frame, padding or border. I did not visually verify whether the old page was the same white (same params style); I would expect it.

## 4. Look: senior designer view

Verdict: **it reads as a boutique hospitality brand, not software.** Ivory paper, one serif at a sturdy weight, one italic phrase per heading, tracked-caps labels, hairline rules, a single monogram ornament, quiet ink buttons, a dark candlelit closing band. It matches the research boards' signals 1, 3, 5 and 7 (place-first hero, inset photo with margins, one idea per screen, facts not adjectives) and avoids the "cheapens" list (no badges, popups, star ratings, counters). No mono, no device frames.

Photography: hero tablescape is sharp, warm, people-free, text-free and carries the first screen. The long-table-under-oak image is also sharp, people-free, and does its job in "What stays yours". Both are AI renders (Gemini) and the page makes no claim they are Insert venues; keep it that way. Only two photos for 8,600 px of page is thin; the evening image is also reused a third time inside the Site Refresh mock.

Printed-card visuals: a real improvement (serif text on linen mounts, soft shadow). But four near-identical card+mount blocks stacked in a zig-zag read as repetitive; the linen mounts are large and mostly empty; the cards are small; and the Site Refresh thumbnail with grey skeleton bars is the one place that still looks like a software wireframe.

Hierarchy and focal point: H1 and the black "Apply for a charter seat" button are clear. In the charter section the $300 is large and the invitation frame is elegant, but the card (`#F4EFE6`) sits on near-identical paper (`#FBF8F2`) so it has little figure/ground; it is calm rather than the focal point. The closing CTA is obvious (gilt button, dark band). The header "Book a call" disappears on scroll.

Ranked improvements:
1. Frame Calendly: ivory (or linen) mat with hairline border and padding, set iframe height to the content (~520), so no white slab or dead dark strip in the night band.
2. Give the charter card real weight: a slightly darker mount or a deeper hairline/shadow, or invert the section to the night palette so the offer is the page's focal point.
3. Break the card rhythm: vary mount sizes, let one chapter use the photograph, or enlarge the cards; cut the mount padding by about a third.
4. Replace the wireframe-bar Site Refresh thumbnail with a plain framed photo or a text-only card; stop reusing the evening photo three times.
5. A third photographic moment (ideally a real venue exterior or doorway once available) between charter and booking; extend the hero below the fold on desktop to remove the empty band above the H1.
6. Sticky slim header (or floating Book a call) on scroll, desktop and mobile.
7. Fix orphans: "Thursday, June / 11 at 4 pm" (nbsp is between "at" and "4", should glue "June 11"); "$3,000–/$4,500" breaks across lines on mobile (`white-space:nowrap`); add a visible "Sample" tag to the first card.

## 5. Promote script safety

Ran `scripts/promote-venues-rehaul.sh` in a throwaway copy (`/tmp/chk/repo`, never the real tree):
- Backs up `venues.html` to `scripts/backups/venues.prev.html` (byte-identical to the old page; also tracked in git, last commit d0c6f9e, no local changes).
- Copies the preview over `venues.html` (cmp identical to the preview). A full md5 diff of the tree shows only those two paths changed: nothing else removed.
- Absolute asset paths (`/assets/venues2-*.webp`) work at `/venues`; all assets return 200 on both local and Railway; 0 failed requests.
- `/scripts/*` is blocked by `server.js`, `scripts/` and `docs/` are in `.railwayignore`, so the backup is neither served nor deployed.
- Rollback (tested, byte-identical): `cd ~/projects/insert && cp scripts/backups/venues.prev.html venues.html` or `git checkout -- venues.html` (valid until venues.html is committed with the new page).
- **Defect: not idempotent.** A second run copies the already-promoted page over the backup, destroying the pre-promotion copy (git still has it). Suggested fix: `[ -e scripts/backups/venues.prev.html ] || cp venues.html scripts/backups/venues.prev.html`, or timestamp the backup.
- After promotion at `/venues` (server.js route `/venues` and `/venues/` -> `venues.html`): 200, no `noindex` meta, no `X-Robots-Tag` (that header is only on `/private-previews`), `robots.txt` unchanged (disallows only `/private-previews/`), analytics `/api/track` fires with `page:/venues`, zero console errors, title/description/canonical/og:url present. No structured data (the old page had none either). `/venues.html` also serves (same as before).
- Notes: `og:url`/canonical point at `https://useinsert.com/venues`, which does not resolve yet (curl gives no connection); no change from old.

## 6. SEO / share

| Item | Old | New | Regression? |
|---|---|---|---|
| Title | "Venue Ops Stack — Insert for Wedding Venues" | "Venue Ops Stack · Insert for Wedding Venues" | no |
| Meta description | "...in under 60 seconds... Two Charter Venue Partner seats open." | "...within a minute... Two Charter Venue Partner seats, by application." | no (still within length) |
| og:title / og:description / twitter | fear-led | "Your front desk, always on" / calmer copy | improvement |
| Canonical, og:url | useinsert.com/venues | same | unchanged; domain not live |
| og:image / twitter:image | `/og-image.png` | `/og-image.png` | **both broken**: relative URL, and `/og-image.png` returns 200 `text/html` (SPA fallback; only `og-image.html` exists). Link previews will have no image. Pre-existing; fix with an absolute URL and a real PNG |
| Favicon | square dark data URI | ivory circle with italic I data URI | no |
| Structured data | none | none | no |
| robots meta | none | none | no |

## 7. Findings and conditions

| # | Sev | Finding | Evidence / repro | Fix |
|---|---|---|---|---|
| 1 | MAJOR | Calendly renders as a white slab in the dark band, with a dead dark strip under it (iframe taller than content) | headed + headless screenshots after 8 s, desktop and 390; `/tmp/chk/calh_*.png` | frame it on ivory with padding, height ~520, or accept and say so |
| 2 | MAJOR | Footer links have ~2:1 focus ring on the dark band; inputs focus is a 1 px shadow | Tab to footer link; outline `rgb(92,69,41)` on `rgb(27,23,18)` | `.night :focus-visible {outline-color: var(--gilt)}`, 2 px ring on inputs |
| 3 | MINOR (process) | Promote script overwrites its own backup on a second run | run twice in temp copy; backup becomes the new page | guard the cp, or timestamp |
| 4 | MINOR | "no-show follow-up" weakened to "a gentle note offers another day" | text diff | restore "reminders and no-show follow-up" if the automation does it |
| 5 | MINOR | Inherited claims beyond the one-pager: contract step, "you hear the moment it's done"/"Deposit received", "within the minute" as a promise | one-pager says reply time is a target; deposit items are requests and reminders only | Dillon/attorney decision; e.g. "we aim to reply within a minute" |
| 6 | MINOR | og:image broken on both pages; og:url domain not live | `/og-image.png` returns text/html | absolute URL + real PNG |
| 7 | MINOR | Orphan wraps ("June / 11", "$3,000–/$4,500"); mobile labels 15 px and buttons 16 px | screenshots at 390 | nbsp / nowrap; raise to 16-17 |
| 8 | MINOR | Cards are `role="img"`, which hides their text from screen readers; first card has no visible "Sample" tag | DOM | `role="group"` with real text; add tag |
| 9 | MINOR | Charter offer is calm, not the focal point; repetitive card rhythm; wireframe Site Refresh thumbnail | section 4 | improvements 2-4 |
| 10 | INFO | Calendly console message `requestStorageAccess: Permission denied` is third-party | console log | none |

Conditions to promote (all small): fix #1 and #2, patch #3 before running the script, and have Dillon decide #4 and #5 (wording only, no layout work). #6 to #9 can follow after promotion. Content, form, analytics, assets, robots and rollback all check out.
