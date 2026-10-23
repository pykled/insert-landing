# Stage 3A-r2 PART 1 progress (Maker: Claude Opus 5.5, 2026-10-23)

- step 0 triage: DONE, kept all uncommitted factory work (86 tests pass) as 578d402 (intake wedding-first) + aef2de9 (build/templates/content); previews/**, venue-shortlist.md, boards README, stonehurst-moments-test.json left uncommitted. next: item 1
- item 1 generality + lint: DONE 2826561 (99 tests; 390-build hostile matrix clean via .factory-check/3a/matrix.py; LSH estate + HomeStead ranch build, lint clean; a/b/c previews now differ in copy only, left uncommitted). next: item 2 overflow
- item 2 overflow: DONE da16e16 (long-word fixture fails before / passes after; proofs + 3a builds 0 offenders at 390/1440). next: item 3 invented content
- item 3 invented content: DONE 7ec1851 (108 tests). next: qa --strict on .factory-check/3a builds
- qa --strict on .factory-check/3a (server 127.0.0.1:8765, --content given): both FAIL only on non-3A ids. 0 overflow, 0 lint, 0 content-trace, flows pass with preview wording.
  - lindley-estate (estate, scorer; built with --allow-close because the guard refuses a 2nd estate venue at 0.518): 4 problems = image soft x2 (facade story photo), Cinzel 500 mobile h1 hairline 51%, diversity refuse.
  - homestead-ranch (ranch, scorer, no overrides): 2 problems = image soft x2 (sawmill timeline photo). Warnings: one first-screen fact, button error-state contrast 6.47-6.80 (<7), family resemblance to stonehurst-b 0.481.
- repro tools (uncommitted, .factory-check/3a/): matrix.py (contents x dialects x forced archetypes; `all quick` = 48 builds), lintall.py, claimsall.py, untraced.py.
- previews/stonehurst-variants a/b/c regenerate with copy-only diffs (JSON-LD 'garden' dropped, uses band, tour notes, light-shift, preview labels, whitespace): NOT committed (brief); republishing them is Dillon's call.

OPEN FOR PART 2: (1) focus ring on guide email input (F5); (2) botanical/editorial hero deck printed twice (F10); (3) editorial dialect reads as a magazine (F8); (4) <title> suffix '(Concept PROOF-<NAME>)' / variant id visible; (5) image-size budget (1.2-3.3 MB at load) and soft story/timeline photos (ladder for role 'large' stops at 1200 px while portrait cover boxes need 1208-1409 px); (6) estate-cinzel mobile h1 hairline 51% (Cinzel 500 @ 28 px); (7) E19 'two facts in the first screen' on both new venues; (8) qa.py ROOT hard-coded (F12); (9) diversity guard refuses a second venue in an already-used dialect until 4 of 7 dims differ (by design, needs a policy decision).

# Stage 3A-r2 PART 2 progress (Maker: Claude Opus 5.5, 2026-10-23)

- item 1 focus (F5, F12): DONE fadd002 (lib/focus.py Tab-walk probe in qa.py; sweep .factory-check/3b/focus_sweep.py: 8 dialects x 3 venues x 1440/390 all pass, min margin 1.07; old CSS fails on every input; 112 tests). next: item 2 hero deck twice
- item 2 hero deck once (F10): DONE 1095fc7 (duplicate-sentence lint in build+qa; optional copy/sections dropped when repeated; statement band gone when it only repeated the hero; 115 tests). next: item 4 titles, then 5/6, then 3 editorial after viewing
- item 4 titles: DONE d5fa771 (title '<Venue> | Weddings in <place>' or content seo.title; chip stays in footer; qa fails concept/proof/variant in <title>). next: item 5 images
- item 5 images: DONE 064a0f2 (400 KB + SSIM>=0.97 per rendition, shared with preview.py; fit_ratio + cover sizes; homestead-ranch strict 0 problems; first build of a new out dir now ~20 s for encoding search, cached after; 118 tests). next: item 6 contrast/Cinzel/first-screen facts
- item 6 contrast/Cinzel/facts: DONE d3fa699 (fill fitted vs paper: paper+white labels >= 7 in all dialects/tones; estate-cinzel retired with probe table, factory/tools/cinzel_probe.py; frame facts above photo; homestead-ranch strict 0 problems, lindley estate only diversity refusal; 121 tests). next: item 7 registry policy
