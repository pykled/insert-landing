"""Stage 2D fixes: candlelit pairings + in-dialect pairing variation, measured hairline floors, modern-luxe strict QA,
dialect page-bottom variants, archetype statuses, cinematic copy-zone panel."""
import json, os, re, sys
from tests import _util
from lib import personality as PERS, fonts as FONTS

PAIRINGS = {p['id']: p for p in _util.data('pairings.json')['pairings']}
DOC = _util.data('dialects.json')
DIALECTS = {d['id']: d for d in DOC['dialects']}


def _env():
    from jinja2 import Environment, FileSystemLoader
    return Environment(loader=FileSystemLoader(os.path.join(_util.FACTORY, 'templates')), trim_blocks=True, lstrip_blocks=True)


# --- 1. candlelit pairings -----------------------------------------------------------------------------------------

def test_candlelit_has_three_or_more_vetted_pairings():
    ids = [it['id'] for it in DIALECTS['candlelit']['pairings']]
    assert len(ids) >= 3, ids
    cache = FONTS.load_cache()['verified']
    for pid in ids:
        p = PAIRINGS[pid]
        assert 'candlelit' in p['dialects'] and not p.get('dropped'), pid
        assert 400 <= p['display']['weight'] <= 600, pid                 # spec 1: display weight 400-600 pinned
        assert p['display'].get('hairline_floor_px') and p['display'].get('mobile_floor_px'), pid
        assert p['import'] in cache, (pid, 'verify the import on fonts.googleapis.com (lib/fonts.verify_import)')
        assert p['display']['family'] not in ('Playfair Display', 'Montserrat', 'Raleway', 'Poppins', 'Open Sans')
    assert FONTS.validate_pairings([PAIRINGS[i] for i in ids]) == []
    # three different display families, so the pairing knob changes the page
    assert len({PAIRINGS[i]['display']['family'] for i in ids}) == len(ids)


def test_usage_penalty_spreads_pairings_inside_a_dialect():
    items = [PAIRINGS[it['id']] for it in DIALECTS['candlelit']['pairings']]
    p = PERS.axes_centre(DIALECTS['candlelit'])
    first = PERS.rank(items, p, dialect_mode=True)[0][1]['id']
    used = {first: 2}
    again = PERS.rank(PERS.usage_penalised(items, used), p, dialect_mode=True)
    assert again[0][1]['id'] != first
    assert all('_use_penalty' not in it for it in items)                 # the library itself is never mutated
    assert PERS.usage_penalised(items, {}) == items


# --- 2. measured hairline floors -----------------------------------------------------------------------------------

def _faces_with_floors():
    for p in PAIRINGS.values():
        for key in ('display', 'secondary'):
            f = p.get(key)
            if f and f.get('hairline_floor_px'):
                yield p['id'], key, f


def test_declared_floors_are_measured_and_sane():
    n = 0
    for pid, key, f in _faces_with_floors():
        n += 1
        assert f['mobile_floor_px'] <= 56, (pid, key)       # a 390px phone still sets a short headline on <= 3 lines
        assert f['mobile_floor_px'] <= f['hairline_floor_px'], (pid, key)
        assert f['hairline_floor_px'] >= f['min_px'], (pid, key)
        assert '1x/2x' in f.get('hairline_note', ''), (pid, key)
    assert n >= 10
    assert PAIRINGS['estate-caslon']['display']['hairline_floor_px'] >= 64   # 56 px measured 0.19 at 1x vs the 0.20 line
    assert PAIRINGS['heritage-garalde']['display']['weight'] == 600         # 500 needs 64/56 px floors


def test_h1_partial_uses_declared_floors():
    tpl = _env().get_template('heroes/_h1.css.j2')
    pair = json.loads(json.dumps(PAIRINGS['estate-caslon']))
    css = tpl.render(sel='.x h1', pair=pair, dialect=True, t={'display_case': 'sentence'})
    assert 'clamp(64px' in css and 'clamp(56px, 10.5vw, 60px)' in css, css
    pair['display'].pop('hairline_floor_px'); pair['display'].pop('mobile_floor_px')
    css = tpl.render(sel='.x h1', pair=pair, dialect=True, t={'display_case': 'sentence'})
    assert 'clamp(56px' in css and 'clamp(48px, 10.5vw, 60px)' in css    # the 2C fallback list still applies


if __name__ == '__main__':
    sys.exit(_util.run_module(sys.modules[__name__]))
