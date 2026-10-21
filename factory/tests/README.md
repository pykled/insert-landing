# factory/tests

Focused tests for the stage-2A dialect layer. No browser needed except `qa.py` itself; `test_templates.py` runs one
real `build.py` dialect build into a temp dir (about 20 s, image encoding) with `--offline-fonts` and a copy of the
registry, so it never touches `data/registry.json` or `previews/`.

Run from `factory/`:

```
python3 -m pytest -q tests            # with pytest (installed here: 8.4)
python3 -m tests.run_all              # without pytest: plain asserts, same functions
python3 -m tests.test_exclusions      # one module
python3 qa.py --self-test             # the exclusion fixtures only, through the QA entry point
```

| File | Covers |
|---|---|
| `test_palette.py` | dark (charcoal) token set: every pair in `palette.dark_checks` passes its 7:1 / 5:1 bar across warm/cool grounds and accent hues; spec targets (paper L 0.16-0.24, brass L >= 0.74, captions L >= 0.80); light dialect papers stay in the baseline and never `#ffffff`; photo signals on synthetic pixels; lead weighting |
| `test_dialects.py` | `dialects.json` integrity (eight ids, axis keys, formality floor, statuses match the filesystem), scoring determinism and its explanation table, vibe/type/era rules, tie-break to fewer registered sites, axis clamping incl. the density/voice corner rule, ornament rotation |
| `test_fingerprint.py` | schema-2 weights, same-dialect rule (refuse with < 4 of 7 key dims differing even when the weighted distance is high; lower thresholds), quota (2nd warns, 3rd refuses), pre-dialect sites exempt, pHash identity / difference / DPR invariance / thresholds, registry schema 2 + matrix |
| `test_schema.py` | content schema (existing Stonehurst file valid; photo `subject`/`mono`/`flora`/`archival`; `vibe` block; required keys), the lead-photo rule, strict voices state no numbers outside `{slots}`, pairing rules (400-600 weight, pinned opsz, didone hairline caution, banned families) |
| `test_exclusions.py` | each of E1-E19 (spec 05 section 5) on a clean fixture page and a broken one; pre-dialect mode downgrades to warnings |
| `test_templates.py` | template resolution and fallback chains, copy candidates (no invented facts, unfillable slot stops the build, CTA sets), an end-to-end estate build forcing a stage-2B hero that falls back and is recorded, forcing outside a dialect is rejected |

When stage 2B adds a template, run `python3 lib/templates.py --refresh` (statuses in `data/dialects.json`) or
`test_dialects.py::test_statuses_match_filesystem` fails and says so.
