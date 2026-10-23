# Stage 3A notes (part 2, 2026-10-23, Maker: Claude Opus 5.5)

Local only: nothing pushed, deployed or sent. Progress log with commit per item: STAGE-3A-PROGRESS.md. 123 tests pass.

## What changed

| Item | Change | Evidence |
|---|---|---|
| 1 Focus (F5, F12) | Two-tone ring (`--focus` + `--focus-halo` filling the 3 px offset) on every control; inputs lose `outline: none`; dark bands and band-ink set their own ring colours. `lib/focus.py` Tab-walks the page in `qa.py` and fails a control whose focused-vs-blurred pixels change by < 3:1 over a 2 CSS px perimeter (perimeter honours border-radius). `qa.py` ROOT from `__file__`, clear error on a non-200. | Old CSS: every input fails (0-112 px changed vs 3000-5800 needed). New: `tools/focus_sweep.py`, 8 dialects x 3 venues x 1440/390, all pass (min margin 1.07). The probe's first version was flaky because smooth scrolling moved the page between shots; it now forces `scroll-behavior: auto`. |
| 2 Deck twice (F10) | `lint.duplicate_sentences` (in the build lint and so in qa) flags any 40+ char block printed twice (contact lines exempt). Secondary copy is `data-optional-copy` and is removed when repeated; `data-optional-section` (statement band) goes when its copy is gone. | The scan found the deck repeat on botanical/editorial/coastal/modern-luxe plus four more repeats (crest line, sprig text, dial rule, journey blurbs); all builds now clean. |
| 3 Editorial (F8) | Not selectable (`dialects.json` selectable false + reason); the scorer never picks it, explicit `--dialect editorial` still builds with a warning, `qa.py --strict` refuses it. | Viewed at 1440/390 on three venues: index list for spaces, name below a wide photo, light type over empty paper, press strip, pairs block. Reads as a magazine. |
| 4 Titles | `build.page_title`: content `seo.title`, else `<Venue> \| Weddings in <locality>, <state>`. No concept/proof/variant suffix; qa fails one. Footer chip keeps "Concept preview by Insert". | `The Stonehurst \| Weddings in Shadow Hills, CA`. |
| 5 Images | One budget: `images.MAX_BYTES` (400 KB, also `preview.MAX_IMG`) and SSIM >= 0.97 vs the resized source at the lowest WebP quality that reaches it; widths that cannot meet both are dropped; 1500 rungs added; stale renditions removed; sidecar `{q, ssim, bytes}`. Soft photos were landscape photos cover-cropped into 3:4 / 4:5 boxes with `sizes` for the box: `fit_ratio` (crop <= 1.25) on single photo boxes and stages, `|cover` scales `sizes` (and the hero preload) by the drawn width. | HomeStead hero (3200 px, grass and leaves): SSIM 0.97 needs q80 = 322 KB at 1400w, 403 KB at 1600w, 480 KB at 1800w, so it serves 1500w. All demo renditions <= 385 KB. |
| 6 Contrast, Cinzel, facts | accent-fill fitted against the final paper (light) / the lighter dark label (dark), plus a 'paper on accent-fill' pair in every palette check. Cinzel retired. Frame hero prints its facts under the headline; kickers centred to their content. | The 6.47 warning was a paper label on the fill across hover/focus. Cinzel table (qa maths, 2x, mixed case) 500: 0.38/0.34/0.29/0.20 at 28/32/36/44 px; 700: 0.24/0.19/0.15/0.08; floor 0.25, warn 0.18. Needs >= 700 at >= 36 px, about 11 caps a line at 390. |
| 7 Registry | `exposure`: demo (default, counts) or internal-proof (listed, not counted) in the guard, quota and pHash. Only the five `.factory-check/proof/*` Stonehurst proofs are internal. Thresholds unchanged and asserted in a test. | Lindley-Scott estate was refused at 0.199 by the never-shown estate proof; against shown sites it is OK. |
| 8 Demos | `.factory-check/demos/{homestead, lindley-scott, stonehurst}`: ranch / estate / botanical, all `qa.py --strict` exit 0. Review fixes: journey provenance note no longer printed, facts strip skipped under the frame hero (repeat), headline auto-hyphenation off ("wed-dings"), marquee label wraps, Stonehurst email is the real published `thestonehurst@gmail.com` (the content had a placeholder domain) and its hero is wedding-first. | Distances: HS-LS 0.551, LS-SH 0.623, HS-SH 0.768; HomeStead WARN 0.481 vs stonehurst-b. Shots in each `shots/`. |
| 9 Staging | `preview.py` staged all three into `private-previews/2d32be7dda6d361dd89ffdfd/demos/<slug>/` after `--mark-qa-strict`; it refused a build without a QA record. Not committed, not deployed. | 2.8 / 2.8 / 4.5 MB, max file 385 KB. |

## Judgement calls to review
- Lindley-Scott uses `--force pairing=estate-caslon`: the scorer's inscriptional-marcellus fails qa (h3 at 20 px < 24 px
  minimum, mobile h1 hairline 43%). That pairing should be fixed or retired too.
- HomeStead and Lindley-Scott both use the frame hero. Full-bleed heroes were tried and rejected: at 1440 they need a 2160 px
  rendition, which neither lead can serve within 400 KB at SSIM 0.97 (Lindley's source is 1920 px), and HomeStead's
  cinematic headline over the photo measured 1.96:1. They differ in dialect, palette, type, spaces, story, moment and bottom.
- HomeStead's guard warning (0.481 vs stonehurst-b) is a warning, not a refusal; stonehurst-b is a shown variant, so it stays
  counted.
- Stonehurst copy_overrides (kicker, lede, spaces title) were written by the Maker from facts in the file; a reviewer
  should read them.

## Deferred
- Editorial rework (warm photographic hero with the name on screen, sturdier display weight, venue pacing).
- inscriptional-marcellus minimum sizes; the scorer should not offer pairings that fail qa at mobile sizes.
- Previews a/b/c and the older proofs were not rebuilt with these fixes (they keep their committed HTML).
- Page weight at load is 1.5-1.6 MB on desktop for the estate demo (warning only).
