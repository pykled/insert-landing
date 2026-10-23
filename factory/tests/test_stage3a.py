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


# --- item 2: horizontal overflow per element ---------------------------------------------------------------------

LONG = 'QUINCEAÑERASQUINCEAÑERAS'


def _overflow(html, width=390):
    pw_mod = pytest.importorskip('playwright.sync_api')
    from lib.overflow import element_overflow
    with pw_mod.sync_playwright() as pw:
        b = pw.chromium.launch()
        try:
            pg = b.new_page(viewport={'width': width, 'height': 844})
            pg.set_content(html)
            return element_overflow(pg)
        finally:
            b.close()


def test_overflow_flags_long_word_in_its_own_box_past_viewport_and_clipped():
    css = '<style>body{margin:0} h2{font:700 40px sans-serif;letter-spacing:.2em;text-transform:uppercase}</style>'
    own = _overflow(css + '<section style="overflow:visible"><div style="width:300px"><h2>%s</h2></div></section>' % LONG)
    assert any('text overflows box' in o and 'h2' in o for o in own), own
    past = _overflow(css + '<div style="width:600px" class="band"><p>wide</p></div>')
    assert any('past viewport' in o and 'div.band' in o for o in past), past
    clipped = _overflow(css + '<div style="overflow:hidden;width:390px"><h2 style="white-space:nowrap">%s</h2></div>' % LONG)
    assert clipped, clipped


def test_overflow_clean_when_wrap_rules_apply():
    css = '<style>body{margin:0} h2{font:700 40px sans-serif;letter-spacing:.2em;text-transform:uppercase;overflow-wrap:anywhere}</style>'
    assert _overflow(css + '<div style="width:300px"><h2>%s</h2></div>' % LONG) == []


def test_long_word_uses_band_does_not_overflow_in_any_bottom(tmp_path):
    v = H.longword(LSH)
    v['tagline_facts']['uses'] = ['Weddings', LONG, 'Extraordinarycelebrationsandfilmproductions']
    src = H.write(v, str(tmp_path / 'llong.json'))
    for d in ('estate', 'botanical', 'candlelit'):   # letterpress, almanac, marquee bottoms
        out = tmp_path / d
        rc, log = _build(src, str(out), '--dialect', d)
        assert rc == 0, log[-800:]
        html = open(out / 'index.html').read().replace('href="', 'data-x="')   # no network: CSS is inline, assets ignored
        assert [o for o in _overflow(html) if 'uses' in o] == [], d


# --- item 3: nothing invented ------------------------------------------------------------------------------------

from lib import claims as CL, schema as SCHEMA  # noqa: E402

CONTENT_MIN = {'tagline_facts': {'max_guests': 200, 'events_per_day': None, 'acres': 4}, 'spaces': [{'capacity': 150}],
               'contact': {'phone': '(626) 334-5215'}}


def test_deny_list_flags_promises_and_preset_venue_words():
    html = ('<h1>A garden for 200 at dinner.</h1><p>See the hall by appointment.</p>'
            '<div class="hold"><b>Held for 24 hours.</b> We\'ll text you in under a minute.</div><h3>You\'re on the calendar.</h3>')
    probs = CL.deny_list(html, CONTENT_MIN)
    for want in ('at dinner', 'the hall', 'by appointment', 'Held for 24', "We'll text", 'in under a minute', "You're on the calendar"):
        assert any(want.lower() in p.lower() for p in probs), want


def test_deny_list_allows_what_the_venue_states():
    c = dict(CONTENT_MIN, faqs=[{'q': 'Tours?', 'a': 'Tours are by appointment.'}], tagline_facts={'events_per_day': 1})
    assert CL.deny_list('<p>Tours by appointment.</p><h1>One wedding a day.</h1>', c) == []


def test_numbers_must_trace_to_content_or_arithmetic():
    probs = CL.untraced_numbers('<h2>Up to 350 guests</h2><p class="lede">120 at dinner</p><dd>4 acres</dd>'
                                '<span class="jnum">07</span><h3>Call (626) 334-5215</h3>', CONTENT_MIN)
    assert len(probs) == 1 and '120' in probs[0]      # 350 = 200 + 150; 4 stated; 07 is a sequence label; phone is the venue's


def test_preview_label_required_on_every_automation_surface():
    bare = '<div class="card" id="check"><form></form></div><div class="scheduler" id="scheduler"></div><div id="guide-wrap"></div>'
    assert len(CL.preview_labels(bare)) == 3
    lab = '<p class="fine preview-label">%s.</p>' % CL.PREVIEW_PHRASE
    ok = bare.replace('<form>', lab + '<form>').replace('id="scheduler">', 'id="scheduler">' + lab).replace('id="guide-wrap">', 'id="guide-wrap">' + lab)
    assert CL.preview_labels(ok) == []


def test_all_voices_valid_including_dialect_lines():
    errors, _ = SCHEMA.validate_voices(json.load(open(os.path.join(FACTORY, 'data', 'voices.json'))))
    assert errors == []


def test_built_pages_state_nothing_the_content_lacks(tmp_path):
    for src, dialect in ((LSH, 'auto'), (HS, 'auto'), (LSH, 'candlelit'), (HS, 'botanical'), (os.path.join(FACTORY, 'content', 'stonehurst.json'), 'ranch')):
        out = tmp_path / ('%s-%s' % (os.path.basename(src), dialect))
        rc, log = _build(src, str(out), '--dialect', dialect)
        assert rc == 0, log[-800:]
        html = open(out / 'index.html').read()
        assert CL.check(html, json.load(open(src))) == [], (src, dialect)
        assert 'Garden Wedding Estate' not in html or json.load(open(src)).get('vibe', {}).get('type') == 'garden'
