"""Stage 3A: the factory builds ordinary content for a new venue (no Stonehurst names, null-safe templates, no
None/null/undefined/NaN in the output), long words do not overflow, and no copy states a fact the content lacks."""
import json, os, subprocess, sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
FACTORY = os.path.dirname(HERE)
sys.path.insert(0, FACTORY)
import build  # noqa: E402
from lib import lint as LINT, personality as PERS  # noqa: E402
from tests.fixtures import hostile as H  # noqa: E402

LSH = os.path.join(FACTORY, 'content', 'lindley-scott.json')
HS = os.path.join(FACTORY, 'content', 'homestead.json')


def _build(content_path, out, *extra):
    r = subprocess.run([sys.executable, os.path.join(FACTORY, 'build.py'), content_path, '--variant', 't3a', '--out', out,
                        '--allow-close', 'stage3a test', '--offline-fonts'] + list(extra), capture_output=True, text=True, cwd=FACTORY)
    return r.returncode, r.stdout + r.stderr


# --- lint ---------------------------------------------------------------------------------------------------------

def test_lint_flags_python_none_in_text_attr_and_mailto():
    html = '<p>A None-acre garden.</p><a href="mailto:None?subject=x">mail</a><input max="None">'
    probs = LINT.lint_html(html)
    assert len(probs) >= 3
    assert any('mailto:None' in p or "'None'" in p for p in probs)


def test_lint_flags_null_undefined_nan_text_and_empty_slot_gaps():
    for bad in ('<p>Up to undefined guests</p>', '<p>NaN acres</p>', '<p>null</p>', '<p>Residence, garden and carriage house. .</p>',
                '<p>Spaces ()</p>'):
        assert LINT.lint_html(bad), bad


def test_lint_scans_inline_js_values_but_allows_code_literals():
    assert LINT.lint_html('<script>var MAXG = None;</script>')
    assert LINT.lint_html("<script>var label = 'undefined';</script>")
    assert not LINT.lint_html('<script>var selDay = null; if (x === undefined) {}</script>')


def test_lint_rejects_null_in_json_ld():
    assert LINT.lint_html('<script type="application/ld+json">{"maximumAttendeeCapacity": null}</script>')
    assert not LINT.lint_html('<script type="application/ld+json">{"name": "Lindley-Scott House"}</script>')


def test_lint_clean_on_ordinary_markup():
    assert LINT.lint_html('<p>Nonetheless, the garden holds 200. Annulled? No.</p><a href="mailto:a@b.co">a@b.co</a>') == []


# --- photo roles / moments ----------------------------------------------------------------------------------------

def test_default_lead_and_roles_come_from_tags_not_names():
    items = {'facade': {'subject': 'building', 'light': 'day', 'tags': ['house']},
             'lawn': {'subject': 'grounds', 'light': 'day', 'tags': ['ceremony', 'wide']},
             'dusk': {'subject': 'building', 'light': 'night', 'tags': ['evening']},
             'tables': {'subject': 'interior', 'light': 'day', 'tags': ['reception', 'interior']}}
    lead = build.default_lead(items)
    assert lead == 'lawn'
    r = build.photo_roles(items, lead)
    assert set(r['light'].values()) <= set(items) and r['light']['night'] == 'dusk'
    assert r['guide'] == 'tables' and r['story_second'] in items
    one = {'only': {'subject': 'grounds', 'light': 'day', 'tags': []}}
    r1 = build.photo_roles(one, build.default_lead(one))
    assert set(r1['light'].values()) == {'only'} and r1['guide'] == 'only'


def test_fallback_moment_must_meet_its_needs():
    journey = {'id': 'guest-journey', 'needs': {'journey': True}}
    assert not PERS.moment_needs_ok_for(journey, {'journey': []})
    seat = {'id': 'seat-picker', 'needs': {'capacities': True, 'max_guests': True}}
    assert not PERS.moment_needs_ok_for(seat, {'tagline_facts': {'max_guests': None}, 'spaces': []})


# --- whole builds -------------------------------------------------------------------------------------------------

@pytest.mark.parametrize('dialect', ['auto', 'botanical', 'candlelit', 'ranch'])
def test_hostile_null_content_builds_and_lints_clean(tmp_path, dialect):
    src = H.write(H.nulls(LSH), str(tmp_path / 'lnull.json'))
    rc, log = _build(src, str(tmp_path / 'out'), '--dialect', dialect)
    assert rc == 0, log[-1500:]
    html = open(tmp_path / 'out' / 'index.html').read()
    assert LINT.lint_html(html) == []
    assert 'mailto:' not in html          # no email in the content: no mail link anywhere


def test_single_photo_venue_builds(tmp_path):
    src = H.write(H.single_photo(LSH), str(tmp_path / 'l1.json'))
    rc, log = _build(src, str(tmp_path / 'out'), '--dialect', 'botanical')
    assert rc == 0, log[-1500:]


def test_new_venues_build_with_scorer_dialect_and_no_lead(tmp_path):
    for src in (LSH, HS):
        rc, log = _build(src, str(tmp_path / os.path.basename(src)))
        assert rc == 0, log[-1500:]
        assert LINT.lint_html(open(tmp_path / os.path.basename(src) / 'index.html').read()) == []
