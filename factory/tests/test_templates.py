"""Template resolution + fallback, copy resolution, and one end-to-end dialect build (planned templates fall back,
the build records it, nothing crashes)."""
import importlib.util, json, os, shutil, subprocess, sys
from tests import _util
from lib import templates as TPL

DOC = _util.data('dialects.json')
FB = DOC['fallbacks']


def _build_module():
    spec = importlib.util.spec_from_file_location('factory_build', os.path.join(_util.FACTORY, 'build.py'))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_resolve_prefers_wanted_then_allowed_chain():
    have = {('hero', 'frame'), ('hero', 'cover-type'), ('hero', 'masthead')}
    ex = lambda k, i: (k, i) in have
    assert TPL.resolve('hero', 'frame', [], FB, ex) == ('frame', None)
    used, rec = TPL.resolve('hero', 'silent', ['cover-type'], FB, ex)
    assert used == 'cover-type' and rec['wanted'] == 'silent' and rec['chain'] == ['cinematic', 'cover-type', 'frame']
    used, rec = TPL.resolve('hero', 'silent', [], FB, ex)
    assert used == 'cover-type'          # cinematic does not exist; next in the chain
    used, rec = TPL.resolve('section', 'statement', [], FB, ex)
    assert used is None and 'omitted' in rec['reason']


def test_real_filesystem_statuses():
    assert TPL.exists('hero', 'frame') and not TPL.exists('hero', 'crest-centred')
    assert TPL.exists('gallery', 'none') and TPL.exists('ornament', 'none')
    assert TPL.exists('pairing', 'estate-caslon') and TPL.exists('voice', 'heritage')
    used, rec = TPL.resolve('hero', 'crest-centred', ['cinematic', 'frame'], FB)
    assert used in ('cinematic', 'frame') and rec
    used, rec = TPL.resolve('ornament', 'crest-roundel', [], FB)
    assert used == 'none' and rec['kind'] == 'ornament'


def test_every_fallback_chain_ends_somewhere_buildable_or_omits():
    for kind, chains in FB.items():
        if kind == 'nav':
            continue
        for wanted, chain in chains.items():
            used, rec = TPL.resolve(kind, wanted, [], FB)
            assert used is None or TPL.exists(kind, used), (kind, wanted, used)
            if kind in ('hero',):
                assert used, (kind, wanted)   # a page always has a hero


def test_copy_candidates_and_no_invented_facts():
    B = _build_module()
    v = _util.content('stonehurst')
    voices = _util.data('voices.json')
    c = B.resolve_copy(voices['heritage'], v, {}, voices['heritage']['cta_sets'][1])
    assert str(c['hero_headline']) == 'Nine acres. One wedding a day.'      # no era -> second candidate; numbers from content
    assert str(c['nav_cta']) == 'Arrange a visit'                           # CTA set 1
    assert '{' not in ''.join(str(x) for x in c.values())
    v2 = json.loads(json.dumps(v)); v2['vibe']['era'] = 1927; v2['vibe']['type'] = 'villa'
    assert str(B.resolve_copy(voices['heritage'], v2, {})['hero_headline']) == 'A villa in Shadow Hills, built 1927.'
    v3 = json.loads(json.dumps(v)); v3['tagline_facts']['acres'] = None; v3['tagline_facts']['events_per_day'] = None
    assert str(B.resolve_copy(voices['heritage'], v3, {})['hero_headline']) == 'The Stonehurst, Shadow Hills.'
    bad = dict(voices['lyric']); bad['hero_headline'] = ['{era} by the sea.']
    try:
        B.resolve_copy(bad, v, {})
        raise AssertionError('an unfillable slot must stop the build')
    except ValueError:
        pass
    legacy = B.resolve_copy(voices['romantic'], v, {})
    assert str(legacy['hero_headline']).startswith('Nine acres')


def test_dialect_build_falls_back_and_records(tmp_path):
    out = os.path.join(str(tmp_path), 'site')
    reg = os.path.join(str(tmp_path), 'registry.json')
    shutil.copy(os.path.join(_util.FACTORY, 'data', 'registry.json'), reg)
    cmd = [sys.executable, 'build.py', 'content/stonehurst.json', '--variant', 'test-estate', '--out', out, '--dialect', 'estate',
           '--lead', 'greenhouse', '--force', 'hero=crest-centred', '--offline-fonts', '--registry', reg]
    r = subprocess.run(cmd, cwd=_util.FACTORY, capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, r.stdout[-1500:] + r.stderr[-1500:]
    meta = json.load(open(os.path.join(out, 'build-meta.json')))
    assert meta['dialect']['id'] == 'estate' and meta['dialect']['source'].startswith('human override')
    assert meta['wanted']['hero'] == 'crest-centred'
    assert meta['choices']['hero'] in ('cinematic', 'frame')
    kinds = {(f['kind'], f['wanted']) for f in meta['fallbacks']}
    assert ('hero', 'crest-centred') in kinds
    assert meta['fingerprint']['dialect'] == 'estate' and meta['fingerprint']['hero'] == meta['choices']['hero']
    for k, (lo, hi) in next(d for d in DOC['dialects'] if d['id'] == 'estate')['axes'].items():
        assert lo <= meta['personality'][k] <= hi
    assert [r_['id'] for r_ in meta['dialect']['scores']][0] == meta['dialect']['scored_winner']
    html = open(os.path.join(out, 'index.html')).read()
    assert '{' + 'era}' not in html and 'None' not in html.split('<body')[1][:20000]
    assert json.load(open(reg)) == json.load(open(os.path.join(_util.FACTORY, 'data', 'registry.json')))   # no --register: untouched


def test_forcing_outside_the_dialect_is_rejected(tmp_path):
    cmd = [sys.executable, 'build.py', 'content/stonehurst.json', '--variant', 'test-bad', '--out', os.path.join(str(tmp_path), 'x'),
           '--dialect', 'deco', '--force', 'hero=frame', '--offline-fonts']
    r = subprocess.run(cmd, cwd=_util.FACTORY, capture_output=True, text=True, timeout=120)
    assert r.returncode != 0 and 'not in dialect deco' in r.stderr


if __name__ == '__main__':
    sys.exit(_util.run_module(sys.modules[__name__]))
