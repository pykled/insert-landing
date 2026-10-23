# Stage 2D notes: factory open items (Maker: Claude Opus 5.5, 2026-10-23)

Fixes the open items in `STAGE-2C-NOTES.md`. Commits `dfd8bae..5c15aab` plus this note (local only, not pushed). Working
files: `.factory-check/2d/` (probe_multi.py, cz_scan.py, cz_blur.py, b.sh, q.sh, proof.sh, abc.sh, shot_bottom.py,
build/QA logs, `matrix-final.txt`, `shots/`). Still untracked and kept out of every build and the registry:
`content/stonehurst-moments-test.json` and `previews/venue-shortlist.md`. The regenerated `previews/stonehurst-variants`
working-tree changes are still only the generator hash and were left uncommitted.

Regression after every numbered fix: `abc.sh` (`FACTORY_OUT=... ./build-all.sh`, then `diff` against the committed a/b/c
`index.html` with the generator meta line dropped): **a, b, c byte-identical**. Final test run: `python3 -m pytest -q tests`,
**72 passed** (new: `tests/test_stage2d.py`, 16 tests).

## What changed

| # | Item | Fix | Evidence |
|---|---|---|---|
| 1 | candlelit had one pairing | Three new candlelit pairings: `candlelit-brygada` (Brygada 1918 600 + Nunito Sans), `candlelit-castoro` (Castoro 400 + Source Sans 3), `candlelit-baskerville` (Libre Baskerville 400 + Libre Franklin). Each has pinned weights, tracking, a measured floor and a risk note. All imports verified online (`lib/fonts.verify_import`, cached in `fonts-verified.json`). In-dialect variation: `personality.usage_penalised()` adds 0.04 to a pairing's fit for each registered same-dialect site that uses it (on top of the existing "never the last one" rule). The axes are placed so Marcellus still wins at the dialect centre, which keeps the existing candlelit proof stable. | Forced builds (`--force pairing=...`): no hairline warnings at all (Marcellus has 2). An unforced second candlelit build picks `candlelit-castoro` (ranked 0.112 / 0.113 / 0.123). |
| 2 | Thin hairline margins | Every dialect sentence display face measured in page context: `probe_multi.py` uses the qa.py stroke-probe maths with antialiasing at 40-72 px, 1x and 2x (`probe-all.txt`). Floor rule: the smallest size with at least 0.04 margin under each fail line, i.e. 1x <= 0.16 and 2x <= 0.21 on desktop, 2x <= 0.21 on mobile. The floors are stored as `hairline_floor_px` / `mobile_floor_px` (with the measured numbers in `hairline_note`) and read by `base.css` (`--h1-floor`, `--h1-min`), `heroes/_h1` and `crest-centred`. Libre Caslon Display goes from 56 to 64 px on desktop and from 48 to 56 px on mobile. `heritage-garalde` and the Cormorant Garamond secondaries (estate-cinzel, coastal-engraved) go from 500 to 600: at 500 they needed 64-72 px. Instrument Serif: 64 / 56. Cardo, Italiana, EB Garamond, Spectral and Marcellus are floored as measured. | Estate proof: mobile warning gone (2C: 24% against the 25% limit); 1x is now 16% (2C: 19% against the 20% limit). Candlelit: mobile 19%, 1x 12%. |
| 3 | modern-luxe failed strict QA | (a) Captions: dialect builds caption photos with `build.short_caption()`. The content's optional `caption` field wins; otherwise the build takes the longest leading clause of the alt text that fits in 60 characters (E5) and 14 words, preferring a punctuation boundary. Nothing is cut mid-phrase: if no clause fits, the caption is left empty. Documented in `lib/schema.md`. (b) Seat-picker summary is 17 px and its notes 16.5 px in dialect builds; on phones the capacity column moves under the name. Pre-dialect variant c is unchanged. | modern-luxe on the flower, greenhouse, barn and bungalow leads: `qa --strict` 0 problems. Greenhouse caption: "The Greenhouse at night." (was 168 characters). |
| 4 | Page bottoms were identical | `templates/bottoms/`: three variants, each with a guide band, a filming band, a footer and its CSS. **letterpress** (estate / editorial): centred, double rules, keyline card with a content facts line, small-caps centred footer. **almanac** (botanical / coastal / ranch): asymmetric with a ruled margin, a numerals ledger (guests / acres / spaces), a sentence-case `dl` footer on paper-2. **marquee** (candlelit / deco / modern-luxe): hairline-grid cells on deep, an ink filming band with a large count, a deep footer with an oversized wordmark. `dialects.json` `bottoms` lists all three in tone order. build.py takes the first, rotates by the number of registered same-dialect sites (the same mechanism as nav and rhythm) and accepts `--force bottom=<id>`. Recorded in choices and in `fingerprint.bottom`, which is not weighted. Facts come only from `tagline_facts` (`build.bottom_facts`). The guide form partial and its ids are unchanged, so app.js and the QA flows work. | Scratch builds of all five dialects: strict 0 problems. 1440 and 390 shots reviewed (`.factory-check/2d/shots/2d_p-{est,bot,cand}-*`). Fixed after review: an off-centre letterpress kicker, the marquee wordmark losing on specificity, and mobile label tracking. |
| 5 | Stale archetype statuses | `templates.refresh_archetypes()` (run by `--refresh`). 25 records whose templates exist become `built`. Records that only now became built are also marked `dialect_only`, so the pre-dialect pool (built and not dialect_only) is exactly the set it was before. Idempotent. | `test_pre_dialect_pool_unchanged_by_the_refresh` freezes the pool; a/b/c byte-identical. |
| 6 | cinematic unreachable | **Veil**: `palette.copy_zone_veil()` measures the cinematic copy zone on the real 1440x860 crop with a 32 px Gaussian blur under the copy. It uses the strictest dialect cap (25%), which covers candlelit. `cinematic.needs.veil_zone`: the hero stays eligible when the plain zone fails and the veiled zone passes. build.py then renders `hero_copy_on='veil'`: a feathered `backdrop-filter: blur(32px)` box under the copy, desktop only (mobile copy already sits on paper). It adds no colour, and every gradient stop stays at or below the dialect cap (E9 unchanged). Also fixed: cinematic mobile `sizes` went from 140vw to 200vw, because the 390x520 cover box needs about 693 css px (QA "image soft"). | Stonehurst veil estimates: greenhouse 2.01 -> 4.85:1, bungalow 4.49 -> 5.78, hero 4.08, bamboo 4.06; flower, barn and reception stay excluded. Forced candlelit cinematic on the greenhouse: `qa --strict` 0 problems, fold reviewed (`shots/cine-fold-1440.png`). |
| 7 | Proofs | The four proofs were rebuilt with `--register`; their picks are identical to 2C. New `stonehurst-proof-modern-luxe` (lead bungalow). pHashes stored from each QA report. | See the table below. |

## Proof builds (`.factory-check/proof/<name>`, registered as `stonehurst-proof-<name>`)

| proof | command (from factory/, plus `--offline-fonts --register`) | bottom | `qa.py --strict` (warnings) |
|---|---|---|---|
| botanical | `build.py content/stonehurst.json --lead hero` | almanac | PASS 0; transfer size |
| estate | `... --dialect estate --lead barn` | letterpress | PASS 0; transfer size, Libre Caslon 1x 16% (h1 64 px, h2 66 px) |
| candlelit | `build.py content/stonehurst-candlelit.json --lead greenhouse` | marquee | PASS 0; transfer size, Marcellus mobile 19%, 1x 12% |
| editorial | `... --dialect editorial --lead flower` | letterpress | PASS 0; transfer size, "20 of 25 lazy" (runtime count, as in 2C) |
| modern-luxe (new) | `... --dialect modern-luxe --lead bungalow` | marquee | PASS 0; no pricing link in the header, Instrument Serif 1x 16% / 14% |

Distance matrix over all 10 registered sites (`python3 lib/fingerprint.py data/registry.json --matrix`, saved in
`.factory-check/2d/matrix-final.txt`): min **0.522** (proof-botanical vs stonehurst-b, unchanged from 2C), max 0.931;
modern-luxe nearest 0.597 (proof-editorial). Every pair clears the cross-dialect 0.50 warn line, and no two sites share a
dialect. pHash: every proof `ok`; the nearest fold/strip distance is 92/256 (estate vs a strip), against warn <= 18 and refuse <= 12.

## Deferred / not done

- **coastal proof**: not built. Stonehurst's water/sky share is 0.057 (the coastal rule wants >= 0.25 on bright photos),
  so a coastal override would misrepresent the venue. It needs a coastal venue's photos.
- **panel hero is soft on the greenhouse lead** (candlelit, found in forced pairing builds): the panel's photo half is
  720x1131 at 1440, so a 3:2 lead needs about 2260 px and the source has 1800. Not a type issue and no proof uses panel. Fix
  later by capping the panel height or adding `needs.lead_min_width`.
- **modern-luxe has no price / pricing-guide link in the header** (baseline warning, not a problem). The spec 2.4 rhythm has
  no guide block. Adding a pricing path means a spec decision.
- `copy_zone_contrast` (the plain, unblurred estimate) still uses the 35% cap and a coarse 288 px grid. At the real 1440 px
  it reads lower (bungalow 3.90 vs 4.49), and candlelit's template cap is 25%. Left unchanged so the 2C verdicts hold. The
  veil estimate is measured at full resolution and 25%.
- Mobile display floors (48-56 px for the thin faces) sit above spec 1's 30-44 px mobile range. This is the 2C trade-off
  (the hairline probe wins), now data-driven per face.
- Variable faces with pinned opsz (Bodoni Moda, Fraunces, Newsreader in dialect builds, Bricolage) were not re-probed
  standalone. Their pinned instances pass in the proofs that use them, and they declare no floors.
