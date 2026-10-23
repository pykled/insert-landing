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
- item 7 registry policy: DONE d68152d (exposure demo|internal-proof; 5 stonehurst-proof-* internal, rest demo; thresholds unchanged + asserted in a test; Lindley estate guard OK nearest stonehurst-b 0.645). next: item 3 editorial decision, then item 8 demos
- item 3 editorial: DONE 7d38211 (removed from selection: selectable false + reason in dialects.json; auto never picks it; qa --strict refuses it; 123 tests). next: item 8 build the three demos
- item 8 demos: DONE 995d9dc. .factory-check/demos/<slug>/ (shots/ = 1440 and 390 @2x full page): homestead ranch (frame, ranch-display-sans; scorer) | lindley-scott estate (frame, estate-caslon forced: scorer's inscriptional-marcellus failed min-size + mobile hairline 43%) | stonehurst botanical (arch-split, botanical-cardo; scorer). All qa --strict exit 0. Rejected on review: crest-centred for Lindley and cinematic for HomeStead (full-bleed needs 2160 px; the 400 KB/SSIM bar caps these leads at 1500-1800 px; cinematic text contrast 1.96). Distances:
  - homestead-demo (ranch): WARN, nearest counted stonehurst-b 0.481; vs other demos: lindley-scott-demo 0.551, stonehurst-demo 0.768
  - lindley-scott-demo (estate): OK, nearest counted homestead-demo 0.551; vs other demos: homestead-demo 0.551, stonehurst-demo 0.623
  - stonehurst-demo (botanical): OK, nearest counted lindley-scott-demo 0.623; vs other demos: homestead-demo 0.768, lindley-scott-demo 0.623
  - registry matrix (~ = internal-proof pair, not counted):
                                  stonehurst-mo lindley-scott stonehurst-a  stonehurst-b  stonehurst-c  stonehurst-pr stonehurst-pr stonehurst-pr stonehurst-pr stonehurst-pr homestead-dem lindley-scott stonehurst-de 
        stonehurst-mock-v2        0.000         0.717         0.804         0.665         0.734         0.821 ~       0.794 ~       0.707 ~       0.807 ~       0.925 ~       0.786         0.806         0.847         
        lindley-scott-mock        0.717         0.000         0.830         0.669         0.712         0.703 ~       0.758 ~       0.788 ~       0.740 ~       0.880 ~       0.735         0.723         0.698         
        stonehurst-a              0.804         0.830         0.000         0.830         0.626         0.846 ~       0.689 ~       0.823 ~       0.689 ~       0.699 ~       0.876         0.726         0.811         
        stonehurst-b              0.665         0.669         0.830         0.000         0.747         0.522 ~       0.829 ~       0.765 ~       0.730 ~       0.859 ~       0.481         0.605         0.737         
        stonehurst-c              0.734         0.712         0.626         0.747         0.000         0.767 ~       0.753 ~       0.793 ~       0.732 ~       0.624 ~       0.833         0.752         0.767         
        stonehurst-proof-botanica 0.821 ~       0.703 ~       0.846 ~       0.522 ~       0.767 ~       0.000 ~       0.656 ~       0.788 ~       0.689 ~       0.820 ~       0.743 ~       0.628 ~       0.279*~       
        stonehurst-proof-estate   0.794 ~       0.758 ~       0.689 ~       0.829 ~       0.753 ~       0.656 ~       0.000 ~       0.682 ~       0.635 ~       0.816 ~       0.773 ~       0.293*~       0.582 ~       
        stonehurst-proof-candleli 0.707 ~       0.788 ~       0.823 ~       0.765 ~       0.793 ~       0.788 ~       0.682 ~       0.000 ~       0.746 ~       0.931 ~       0.773 ~       0.690 ~       0.822 ~       
        stonehurst-proof-editoria 0.807 ~       0.740 ~       0.689 ~       0.730 ~       0.732 ~       0.689 ~       0.635 ~       0.746 ~       0.000 ~       0.597 ~       0.712 ~       0.503 ~       0.723 ~       
        stonehurst-proof-modern-l 0.925 ~       0.880 ~       0.699 ~       0.859 ~       0.624 ~       0.820 ~       0.816 ~       0.931 ~       0.597 ~       0.000 ~       0.841 ~       0.715 ~       0.825 ~       
        homestead-demo            0.786         0.735         0.876         0.481         0.833         0.743 ~       0.773 ~       0.773 ~       0.712 ~       0.841 ~       0.000         0.551         0.768         
        lindley-scott-demo        0.806         0.723         0.726         0.605         0.752         0.628 ~       0.293*~       0.690 ~       0.503 ~       0.715 ~       0.551         0.000         0.623         
        stonehurst-demo           0.847         0.698         0.811         0.737         0.767         0.279*~       0.582 ~       0.822 ~       0.723 ~       0.825 ~       0.768         0.623         0.000         
        (* same dialect: refuse < 0.32, warn < 0.45, and >= 4 of 7 key dims must differ; otherwise refuse < 0.35, warn < 0.50; ~ internal-proof in the pair: not counted)

  next: item 9 preview staging
- item 9 staging: DONE (local only, not committed, not deployed). preview.py refused an unchecked build (no QA record) and staged after --mark-qa-strict: private-previews/2d32be7dda6d361dd89ffdfd/demos/homestead/ (14 img, 2.8 MB, max 363 KB), .../demos/lindley-scott/ (14 img, 2.8 MB, max 385 KB), .../demos/stonehurst/ (23 img, 4.5 MB, max 360 KB); each has noindex + the 'Concept preview by Insert' chip. Left untracked: venue photos stay out of git; deploying is Dillon's call. next: item 10 docs
