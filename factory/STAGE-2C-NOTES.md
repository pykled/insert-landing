# Stage 2C notes: integration (Maker: Claude Opus 5.5, 2026-10-21)

Integrator for the four 2B makers. Every factory file was in scope. Commits `9026a72..3c930d6` (local only, not pushed).
Working files: `.factory-check/2c/` (proof.sh, qa.sh, shots.py, elshot.py, navcheck.py, probe_aa*.py, build/QA logs,
`matrix.txt`). Untracked and kept out of every build and the registry: `content/stonehurst-moments-test.json` (then-now test
fixture) and `previews/venue-shortlist.md`. The regenerated `previews/stonehurst-variants/{a,b,c}` working-tree changes were
left uncommitted: only the generator hash differs.

## Fix list

| # | What was wrong | Root-cause fix | Evidence |
|---|---|---|---|
| 1 | cinematic / crest-centred copy measured 2.3-4.7:1 on Stonehurst's bright leads | `lib/palette.copy_zone_contrast`: worst-case (p99) white-copy contrast in each hero's copy zone of a 1440x860 cover crop under the 35% E9 cap. Heroes declare `needs.copy_zone` (archetypes.json). `cinematic` is excluded when the lead is < 4.5:1. `crest-centred` (`paper_mode_ok`) renders a copy-on-paper mode at every width, with the facts inside the crest block. A forced on-photo hero warns and lists darker leads. build-meta records `copy_zone.per_photo`. Scrims unchanged. | No Stonehurst photo passes in either zone (best: bungalow 4.49 cinematic). The greenhouse-at-night photo is 2.01 / 2.22 because of its lights. Estate QA: 0 contrast problems. |
| 2 | Forum 400 and Libre Caslon Display hairlines | Probe thresholds unchanged. **candlelit-forum dropped**: it needs >= 56 px on phones (2x 0.26 @48), which is above the 30-44 px mobile range. **Libre Caslon Display kept**: its failures came from a synthesised italic (the face has none). Dialect builds now set `font-synthesis-style: none`; upright it passes at the existing 56 / 48 px floors. | estate QA: mobile h1 24% (WARN, limit 25), 1x 19% (limit 20). Thin margin; see open items. |
| 2b | Found while building candlelit | `candlelit.type.headline_case` was `[caps]`, but spec 2.3 sets candlelit headings in sentence case and keeps caps for the name and kickers. Changed to `[sentence]`. **candlelit-cormorant-sc dropped**: its sentence h1 face (Cormorant Garamond 500) passes with no margin (1x 0.21 @56, 2x 0.24 @48), and Cormorant SC as a caps h1 fails at every caps size. Marcellus got `hairline_floor_px: 56`. `heroes/_h1` never renders a thin primary face below its floor on desktop (the silent hero's 40 px cap had put Marcellus at 40). | Probe numbers come from **page context** (`-webkit-font-smoothing: antialiased`, as in base.css): `.factory-check/2c/probe_aa*.py`. The bare 2B probe tool under-reads by ~0.08 (Marcellus @40 1x: 0.18 bare vs 0.26 in page). |
| 3 | preload `imagesizes`, two-row nav unreachable, two-row menu | `build.HERO_SIZES` equals each hero's lead `<img sizes>` (dialect builds only; a new test keeps the two in sync). inset-wide `sizes` no longer uses `var(--gutter)`, which is invalid there. nav: the axis formula's style first, then rotated through `dialect.nav` by the count of registered same-dialect sites (same mechanism as rhythm), plus `--force nav=<id>`. Nav CSS now goes in `<head>`. | `navcheck.py` on a modern-luxe `--force nav=two-row` build at 390: 0 links visible closed, 5 open, link hit-test ok, closes on tap, no page errors. |
| 4 | app.js crash without `#guide-form`; qa.py crash | app.js null-guards the guide form (dialect builds). qa.py skips the guide / tour flows when absent and records them in `info.skipped`; a chosen moment with no `[data-moment-root]` is flagged as a problem instead of crashing. **Moment inline scripts kept**: they are guarded (no double run) and keep moments working if app.js ever throws again. | modern-luxe QA now runs to the end (the remaining problems are listed below). |
| 5 | crest-reveal h2 overflow, uses h2, accent-fill margin, stale tests, refresh | crest-reveal name is an `.h-label` (a body-face label heading, exempt from the mobile display floor; tighter tracking at <= 600 px). `.uses-band h2` is never below `--h2-floor`. Dark palette accent-fill fitted to 7.3:1 (was 7.0, measured 6.98). Tests updated to the shipped state. The end-to-end estate test now uses a registry of the pre-dialect sites only, because the registered proofs made the guard refuse it, which is correct behaviour. `--refresh` run. | estate 390: no horizontal overflow. pytest 56 passed. |
| 6 | SVG text / scrims / initials | Crest initials and ring use accent-text / metal whenever the crest sits on paper (was on-deep, 1.08:1). Every SVG `<text>` uses `fill: currentColor`. No solid chips sit over photos in the proof heroes. **crest-reveal initials are not hidden pre-scroll**: text opacity 1 before and after; only the rings are primed (dashoffset 1 -> 0); under reduced motion they are already settled. | Playwright check in this session. |

Also from the screenshot review (commit `e5aea04`): the double-line frame cut through the story text (copy now inset past
the inner line); a duplicate header crest medallion appeared on crest heroes; the inset-caption photo left a dead right
column at 1440x900; on phones spaces-index squeezed copy to about 20 characters a line; silent and inset-caption now keep
two facts in the first screen.

Archetype `status` fields in `data/archetypes.json` were **not** refreshed (e.g. hours-dial still says `spec`).
`--refresh` only rewrites dialects.json, and pre-dialect selection reads those statuses (`built` only), so changing them
could alter a/b/c. Dialect builds accept every planned status, so nothing depends on them there.

## Proof builds (`.factory-check/proof/<name>`, registered as `stonehurst-proof-<name>`)

| proof | command (from factory/) | dialect source | picks | `qa.py --strict` |
|---|---|---|---|---|
| botanical | `build.py content/stonehurst.json --lead hero` | scored (botanical 6) | botanical-fraunces, arch-split, stack/timeline, sprig-draw, botanical-line (fig, from photo `flora`), nav bar | PASS, 0 problems; 1 warning (1.9 MB) |
| estate | `... --dialect estate --lead barn` | **override**: the content's vibe (lush, garden, romantic) + garden type score botanical 7 / estate 1 | estate-caslon, crest-centred (paper mode: barn 2.04:1), index/pullquote, crest-reveal, crest-roundel, nav centered | PASS, 0; warnings: transfer size, Libre Caslon hairline 24% mobile / 19% 1x |
| candlelit | `build.py content/stonehurst-candlelit.json --lead greenhouse` | scored (candlelit 4, botanical 3) | inscriptional-marcellus, silent on the Greenhouse at night, index/split, candle-count, double-line-frame, dark-warm | PASS, 0; warnings: transfer size, Marcellus 19% mobile |
| editorial | `... --dialect editorial --lead flower` | **override**: same reason as estate | editorial-literata, inset-caption, index/pullquote, gallery pairs, pairs-counter, drop-cap | PASS, 0; warnings: transfer size, "20 of 25 images lazy" (in the static HTML only the lead is eager, which is correct; the other count is runtime) |

All builds append `--offline-fonts` (verified fonts cache). `content/stonehurst-candlelit.json` is a text copy of
stonehurst.json; `diff` shows only the vibe words (evening, candlelit, romantic), the vibe note and the photo order.
"lush" was dropped from the first draft because with it the scorer still picked botanical.

Screenshots (2x): `.factory-check/proof/<name>/shots/<name>-{1440,390}.png` (+ `-fold`). Contact sheet:
`.factory-check/proof/contact-sheet.png`. Folds next to the hand mock: `.factory-check/proof/folds-1440.png`. In every
shot: no unloaded images, no horizontal overflow, no page errors.

### Distance matrix (`python3 lib/fingerprint.py data/registry.json --matrix`, all 9 registered sites)

```
                          mock-v2 lindley  a      b      c      p-bot  p-est  p-cand p-edit
stonehurst-mock-v2        0.000   0.717   0.804  0.665  0.734  0.821  0.794  0.707  0.807
lindley-scott-mock        0.717   0.000   0.830  0.669  0.712  0.703  0.758  0.788  0.740
stonehurst-a              0.804   0.830   0.000  0.830  0.626  0.846  0.689  0.823  0.689
stonehurst-b              0.665   0.669   0.830  0.000  0.747  0.522  0.829  0.765  0.730
stonehurst-c              0.734   0.712   0.626  0.747  0.000  0.767  0.753  0.793  0.732
stonehurst-proof-botanical 0.821  0.703   0.846  0.522  0.767  0.000  0.656  0.788  0.689
stonehurst-proof-estate   0.794   0.758   0.689  0.829  0.753  0.656  0.000  0.682  0.635
stonehurst-proof-candlelit 0.707  0.788   0.823  0.765  0.793  0.788  0.682  0.000  0.746
stonehurst-proof-editorial 0.807  0.740   0.689  0.730  0.732  0.689  0.635  0.746  0.000
```
Min 0.522 (proof-botanical vs stonehurst-b: both garden / soft-serif / stacked spaces); max 0.846 (proof-botanical vs
a). Among the proofs: 0.635-0.788. No two registered sites share a dialect, so the same-dialect rule (0.32 / 0.45 + 4 of
7 key dims) and the dialect quota are not exercised by this set; every pair clears the cross-dialect 0.50 warn line.
pHash (stored via `--set-phash` from each proof's QA report): every proof is `ok`. Nearest fold/strip distances are
104/98 (botanical vs lindley), 124/102, 140/108, 126/114; warn <= 18, refuse <= 12.

## Regression

`FACTORY_OUT=../.factory-check/sv ./build-all.sh`: a, b, c `index.html` are byte-identical to the committed previews
apart from the generator meta (checked after the last template change; one newline slip in spaces-index was caught and
fixed in `3c930d6`). `python3 -m pytest -q tests`: 56 passed (one test added: preload sizes vs hero `<img sizes>`).

## Open items for the Checker / stage 3

1. **candlelit has one pairing** (inscriptional-marcellus). Spec 4.3 wants 2-3. Every vetted candidate measured in page
   context failed or had no margin; stage 3 owes a second face with a measured `hairline_floor_px`.
2. **Hairline margins are thin**: estate-caslon mobile h1 24% vs 25%; Libre Caslon 1x 19% vs 20%. The base and 2B probe
   tooling measured without antialiasing; stage 3 should re-measure every pairing in page context and move all floors
   into `pairings.json` (`hairline_floor_px` is read now; Marcellus is the only pairing that sets it).
3. **No Stonehurst lead supports on-photo copy**, so `cinematic` is unreachable for this venue, and botanical / ranch /
   estate / candlelit lose it as an option. The estimate is conservative (uniform 35%, p99) and was not calibrated against
   QA on a passing dark photo, because Stonehurst has none.
4. **modern-luxe (not a proof)** still fails strict QA: E5 tracked-caps caption of 152 chars in inset-wide (long alt text
   as caption) and E16 14.5-16 px text in spec-sheet / seat-picker. It has no guide block, so no pricing link (warning).
5. The bottom of every page (guide band, filming band, footer) shares one structure across dialects. The fingerprint and
   pHash both pass, but it is the most "same" region in the contact sheet.
6. Two of four proofs needed `--dialect` overrides because the Stonehurst vibe block is garden / romantic. That is
   correct scoring, not a bug.
