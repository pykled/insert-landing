"""Stage 3A part 2: focus visibility, one hero deck, honest titles, image budget, button contrast, registry policy."""
import json, os, subprocess, sys

import numpy as np
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
FACTORY = os.path.dirname(HERE)
sys.path.insert(0, FACTORY)
from lib import focus as FO  # noqa: E402

LSH = os.path.join(FACTORY, 'content', 'lindley-scott.json')
HS = os.path.join(FACTORY, 'content', 'homestead.json')
SH = os.path.join(FACTORY, 'content', 'stonehurst.json')


def _build(content_path, out, *extra):
    r = subprocess.run([sys.executable, os.path.join(FACTORY, 'build.py'), content_path, '--variant', 't3p2', '--out', out,
                        '--allow-close', 'stage3a part 2 test', '--offline-fonts'] + list(extra), capture_output=True, text=True, cwd=FACTORY)
    return r.returncode, r.stdout + r.stderr


# --- item 1: focus ------------------------------------------------------------------------------------------------

def test_focus_change_counts_only_pixels_changed_by_3_to_1():
    before = np.full((10, 10, 3), 245, np.uint8)
    after = before.copy(); after[0:2, :] = 40          # dark ring rows on paper: 20 px change by > 3:1
    after[5, :] = 200                                   # faint tint: < 3:1, not counted
    assert FO.changed_pixels(before, after) == 20


def test_focus_required_area_uses_component_perimeter():
    assert FO.required_area(100, 40, 2) == pytest.approx(2 * 140 * 2 * 4 * FO.AREA_SHARE)
    pill = FO.required_area(100, 40, 2, radius=999)    # radius clamps to h/2 = 20
    assert pill < FO.required_area(100, 40, 2) and pill == pytest.approx((280 - (8 - 2 * 3.14159265) * 20) * 2 * 4 * FO.AREA_SHARE)


def _focus_probe(html):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        b = pw.chromium.launch(); p = b.new_context(viewport={'width': 600, 'height': 400}, device_scale_factor=2).new_page()
        p.set_content(html); probs, rows = FO.check(p, 't', 2); b.close()
        return probs, rows


def test_focus_probe_fails_outline_none_and_faint_glow_passes_two_tone_ring():
    body = '<p><input id="a" aria-label="email" style="font:16px sans-serif;padding:10px;border:1px solid #bbb;background:#fff"></p>'
    bad = '<style>body{background:#f6f1e7} input:focus{outline:none;box-shadow:0 0 0 3px rgba(130,108,52,.18)}</style>' + body
    probs, rows = _focus_probe(bad)
    assert rows and probs and 'focus not visible' in probs[0]
    good = ('<style>body{background:#f6f1e7} :focus-visible{outline:2px solid #5b4a1f;outline-offset:3px;'
            'box-shadow:0 0 0 3px #f6f1e7}</style>' + body)
    probs, rows = _focus_probe(good)
    assert rows and not probs, probs


def test_built_css_has_visible_focus_on_inputs_and_dark_bands(tmp_path):
    rc, log = _build(HS, str(tmp_path / 'hs'), '--dialect', 'ranch')
    assert rc == 0, log[-800:]
    html = open(tmp_path / 'hs' / 'index.html').read()
    assert 'outline: none' not in html.split('.field input:focus')[1][:120]
    assert '.field input:focus-visible' in html
    assert '.band-ink { --focus: var(--paper)' in html     # band-ink is the light band in dark-paper dialects


# --- item 2: the hero deck (or any sentence) is printed once ------------------------------------------------------

def test_duplicate_sentence_lint_and_optional_copy_drop():
    from lib import lint as LINT
    deck = 'Nine acres in Shadow Hills with a greenhouse, a barn and a flower garden.'
    html = ('<main><section class="hero"><p class="lede">%s</p></section>'
            '<section id="statement" data-optional-section><p class="statement-text" data-optional-copy>%s</p></section>'
            '<section><ul><li><p>Short.</p></li></ul></section></main>') % (deck, deck)
    assert any('printed twice' in p for p in LINT.lint_html(html))
    out = LINT.drop_repeated_optional(html)
    assert out.count(deck) == 1 and 'id="statement"' not in out and not LINT.duplicate_sentences(out)
    keep = html.replace(deck, 'A different sentence that the statement section carries on its own.', 1)
    assert 'id="statement"' in LINT.drop_repeated_optional(keep)


@pytest.mark.parametrize('dialect', ['botanical', 'editorial'])
def test_botanical_and_editorial_print_the_hero_deck_once(tmp_path, dialect):
    from lib import lint as LINT
    rc, log = _build(SH, str(tmp_path / dialect), '--dialect', dialect)
    assert rc == 0, log[-800:]
    html = open(tmp_path / dialect / 'index.html').read()
    assert LINT.duplicate_sentences(html) == []


# --- item 4: titles come from the content file, no concept/proof/variant suffix -----------------------------------

def test_title_is_venue_and_place_without_concept_suffix(tmp_path):
    import re
    rc, log = _build(SH, str(tmp_path / 'sh'), '--dialect', 'botanical')
    assert rc == 0, log[-800:]
    html = open(tmp_path / 'sh' / 'index.html').read()
    title = re.search(r'<title>(.*?)</title>', html).group(1)
    assert title == 'The Stonehurst | Weddings in Shadow Hills, CA'
    assert 'Concept preview by Insert' in html          # the in-page chip stays
    import build
    assert build.page_title({'name': 'X', 'seo': {'title': 'X | Garden weddings'}}) == 'X | Garden weddings'
    assert build.page_title({'name': 'X', 'tagline_facts': {'locality': None, 'state': None}}) == 'X | Weddings'
