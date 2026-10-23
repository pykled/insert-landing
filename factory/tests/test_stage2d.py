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


# --- 3. modern-luxe strict QA: captions and small text -------------------------------------------------------------

def _build_mod():
    import importlib.util
    spec = importlib.util.spec_from_file_location('factory_build', os.path.join(_util.FACTORY, 'build.py'))
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod


def test_short_caption_fits_tracked_caps_and_word_limit():
    B = _build_mod()
    for name, m in _util.content()['photos']['items'].items():
        c = B.short_caption(m['alt'])
        assert c and len(c) <= 60 and len(c.split()) <= 14, (name, c)
        assert B.caption_from_alt(m['alt']).startswith(c.rstrip('.')), (name, c)   # a leading clause, never new words
    assert B.short_caption('The Greenhouse at night, its glass walls glowing from inside, with strings of lights') == 'The Greenhouse at night.'
    assert B.short_caption('anything long ' * 9, explicit='The barn at dusk.') == 'The barn at dusk.'
    assert B.short_caption('x' * 90) == ''                       # no boundary fits: dropped, not cut mid-word


def test_seat_picker_text_meets_body_floor_in_dialect_builds_only():
    tpl = _env().get_template('moments/seat-picker.css.j2')
    pair = PAIRINGS['luxe-tracked-sans']
    on = tpl.render(dialect=True, pair=pair, t={}, v={}, tokens={})
    off = tpl.render(dialect=None, pair=pair, t={}, v={}, tokens={})
    assert '.fit-body p { color: var(--ink-soft); font-size: 16.5px' in on and '.fit-summary { margin-top: 20px; font-size: 17px' in on
    assert '.fit-body p { color: var(--ink-soft); font-size: 14.5px' in off   # pre-dialect variant c stays byte-identical
    assert '.fit-cap { grid-column: 2; text-align: left; }' in on and 'grid-column: 2' not in off   # phones: capacity under the name


# --- 4. page-bottom variants -----------------------------------------------------------------------------------------

BOTTOMS = ('letterpress', 'almanac', 'marquee')
TONE = {'estate': 'letterpress', 'editorial': 'letterpress', 'botanical': 'almanac', 'coastal': 'almanac', 'ranch': 'almanac',
        'candlelit': 'marquee', 'deco': 'marquee', 'modern-luxe': 'marquee'}


def test_every_dialect_lists_all_bottoms_in_tone_order():
    for d in DOC['dialects']:
        assert sorted(d['bottoms']) == sorted(BOTTOMS), d['id']
        assert d['bottoms'][0] == TONE[d['id']], d['id']
    for b in BOTTOMS:
        for part in ('-guide.j2', '-uses.j2', '-footer.j2', '.css.j2'):
            assert os.path.exists(os.path.join(_util.FACTORY, 'templates', 'bottoms', b + part)), (b, part)


def _bottom_ctx(bottom):
    B = _build_mod()
    v = _util.content()
    looks = [s['name'].replace('The ', '').lower() for s in v['spaces']]
    return dict(v=v, dialect={'id': 'x'}, bottom=bottom, bottom_facts=B.bottom_facts(v), looks_sentence=', '.join(looks[:-1]) + ' and ' + looks[-1],
                copy={'guide_kicker': 'K', 'guide_title': 'T', 'guide_lede': 'L', 'guide_cta': 'C', 'footer_blurb': 'F', 'nav_cta': 'N'},
                sections=[{'id': 'spaces', 'nav': 'Spaces'}], pair=PAIRINGS['estate-caslon'], guide_layout='band', uses_band='deep')


def test_bottom_variants_differ_and_use_only_content_facts():
    env = _env(); v = _util.content(); f = v['tagline_facts']
    allowed_numbers = {str(f[k]) for k in ('max_guests', 'acres', 'space_count')}
    seen = {}
    for b in BOTTOMS:
        ctx = _bottom_ctx(b)
        html = ''.join(env.get_template(t).render(**ctx) for t in ('sections/guide.j2', 'sections/uses.j2', 'partials/footer.j2'))
        assert html.count('data-bottom="%s"' % b) == 3, b
        assert 'id="guide-form"' in html and 'id="guide-title"' in html and 'id="uses"' in html, b   # app.js + QA hooks
        text = re.sub(r'<[^>]+>', ' ', html)
        nums = set(re.findall(r'\b\d+\b', text)) - {'2026', '2025'}
        assert nums <= allowed_numbers, (b, nums - allowed_numbers)
        seen[b] = set(re.findall(r'class="([^"]+)"', html))
    for a_ in BOTTOMS:
        for b_ in BOTTOMS:
            if a_ < b_:
                assert len(seen[a_] ^ seen[b_]) >= 8, (a_, b_)          # different structure, not a restyle of one tree


def test_pre_dialect_bottom_is_the_old_markup():
    env = _env(); ctx = _bottom_ctx(None); ctx['dialect'] = None
    for t in ('sections/guide.j2', 'sections/uses.j2', 'partials/footer.j2'):
        out = env.get_template(t).render(**ctx)
        assert 'data-bottom' not in out and out.strip(), t
    assert env.get_template('partials/footer.j2').render(**ctx).rstrip().endswith('</footer>')


# --- 5. archetype statuses ---------------------------------------------------------------------------------------------

PRE_DIALECT_POOL = {'heroes': ['cover-type', 'frame', 'masthead'], 'spaces': ['index', 'spec-sheet', 'stack'], 'story': ['ledger', 'pullquote', 'timeline'],
                    'faq': ['accordion-split', 'numbered', 'plain-list'], 'tour': ['band-cta', 'scheduler-centered', 'scheduler-split'], 'gallery': ['none'],
                    'moments': ['guest-journey', 'light-shift', 'seat-picker'], 'voices': ['editorial', 'plainspoken', 'romantic', 'warm-host']}


def test_archetype_statuses_match_filesystem():
    from lib import templates as TPL
    arch = _util.data('archetypes.json'); deferred = set(DOC.get('deferred', []))
    for key, kind in TPL.ARCH_KINDS.items():
        for it in arch.get(key, []):
            built = TPL.status(kind, it['id'], deferred) == 'exists'
            assert (it.get('status', 'built') == 'built') == built, (key, it['id'], it.get('status'), 'run python3 lib/templates.py --refresh')


def test_pre_dialect_pool_unchanged_by_the_refresh():
    """The three committed variants select from built, non-dialect_only items; the 2D refresh must not widen that pool."""
    arch = _util.data('archetypes.json')
    for key, ids in PRE_DIALECT_POOL.items():
        got = sorted(i['id'] for i in arch[key] if i.get('status', 'built') == 'built' and not i.get('dialect_only'))
        assert got == ids, (key, got)


def test_refresh_is_idempotent(tmp_path):
    import shutil
    from lib import templates as TPL
    dst = os.path.join(str(tmp_path), 'archetypes.json')
    shutil.copy(os.path.join(_util.FACTORY, 'data', 'archetypes.json'), dst)
    assert TPL.refresh_archetypes(dst) == 0
    assert open(dst).read() == open(os.path.join(_util.FACTORY, 'data', 'archetypes.json')).read()


# --- 6. cinematic veil -------------------------------------------------------------------------------------------------

def _photo(name):
    v = _util.content(); src = os.path.join(_util.FACTORY, 'content', v['photos']['source_dir'])
    f = next(x for x in os.listdir(src) if x.startswith(name + '.'))
    return os.path.join(src, f), v['photos']['items'][name].get('focal', '50% 50%')


def test_veil_estimate_unlocks_dark_leads_only():
    from lib import palette as P
    assert P.VEIL_SCRIM <= 0.25 <= P.COPY_ZONE_SCRIM <= 0.35          # estimated at the strictest dialect cap; E9 untouched
    gh = P.copy_zone_veil(*_photo('greenhouse'))['cinematic-veil']
    assert gh >= P.COPY_ZONE_MIN > P.copy_zone_contrast(*_photo('greenhouse'))['cinematic']
    assert P.copy_zone_veil(*_photo('flower'))['cinematic-veil'] < P.COPY_ZONE_MIN   # a bright daylight lead stays excluded
    assert P.copy_zone_veil(*_photo('greenhouse')) == P.copy_zone_veil(*_photo('greenhouse'))   # deterministic


def test_cinematic_eligible_through_the_veil():
    arch = _util.data('archetypes.json')
    cine = next(h for h in arch['heroes'] if h['id'] == 'cinematic')
    assert cine['needs']['veil_zone'] == 'cinematic-veil'
    stub = lambda i: {'id': i, 'status': 'built', 'axes': {}, 'fingerprint': {}}
    libs = {'pairings': [PAIRINGS['inscriptional-marcellus']], 'heroes': [cine], 'spaces': [stub('index')], 'story': [stub('split')], 'faq': [stub('plain-list')],
            'tour': [stub('band-cta')], 'gallery': [stub('none')], 'moments': [stub('candle-count')], 'voices': [stub('evening')]}
    def ranked(cz):
        content = {'photos': {'items': {'x': {'subject': 'grounds'}}}, '_lead': 'x', '_lead_width': 2400, '_copy_zone_min': 4.5, '_copy_zone': cz}
        _, rep = PERS.select(libs, PERS.axes_centre(DIALECTS['candlelit']), lambda fp: ('ok', None, 1.0), content=content, dialect_mode=True)
        return rep['needs_relaxed']
    assert ranked({'cinematic': 2.0, 'cinematic-veil': 4.8}) == []          # eligible: the veil carries the copy
    assert ranked({'cinematic': 2.0, 'cinematic-veil': 3.0}) == ['hero']    # excluded (needs had to be relaxed)
    assert ranked({'cinematic': 5.0}) == []


def test_veil_markup_only_in_veil_mode():
    env = _env()
    for mode, want in (('veil', True), ('photo', False), ('paper', False)):
        css = env.get_template('heroes/cinematic.css.j2').render(hero_copy_on=mode, veil_blur_px=32, dialect={'id': 'candlelit'}, pair=PAIRINGS['candlelit-castoro'], t={'display_case': 'sentence'})
        assert ('backdrop-filter: blur(32px)' in css) == want, mode
        for stop in re.findall(r'rgba\(0,0,0,([0-9.]+)\)', css):
            assert float(stop) <= 0.25 + 1e-9, stop                    # candlelit cap, veil adds no darkening


# --- 7. proofs ---------------------------------------------------------------------------------------------------------

def test_every_built_dialect_proof_is_registered_with_phash():
    reg = _util.data('registry.json')
    proofs = {s['id']: s for s in reg['sites'] if s['id'].startswith('stonehurst-proof-')}
    for name in ('botanical', 'estate', 'candlelit', 'editorial', 'modern-luxe'):
        site = proofs['stonehurst-proof-' + name]
        assert site.get('phash') and site['fingerprint'].get('bottom') in BOTTOMS, name
        assert site['fingerprint']['dialect'] == name


if __name__ == '__main__':
    sys.exit(_util.run_module(sys.modules[__name__]))
