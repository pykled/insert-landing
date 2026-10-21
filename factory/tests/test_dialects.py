"""Dialect scoring determinism + explainability, axis clamping, data integrity of dialects.json."""
import copy, json, os
from tests import _util
from lib import personality as PERS, templates as TPL, palette as P

DOC = _util.data('dialects.json')
IDS = [d['id'] for d in DOC['dialects']]


def _signals(**kw):
    s = {k: 0.0 for k in P.SIGNAL_KEYS}
    s.update(kw)
    s.setdefault('warm_shadows', s.get('shadow_warm', 0) >= 0.5)
    return s


def test_eight_dialects_with_spec_ranges():
    assert IDS == ['estate', 'editorial', 'candlelit', 'modern-luxe', 'coastal', 'botanical', 'ranch', 'deco']
    for d in DOC['dialects']:
        assert set(d['axes']) == set(PERS.AXES)
        assert d['axes']['formality'][0] >= 40          # the formality floor keeps the premium band
        assert len(d['rhythm_variants']) == 2
        for key in TPL.LIST_KINDS:
            assert d[key], (d['id'], key)
            for it in d[key]:
                assert it['status'] in ('exists', 'planned-2B', 'deferred'), (d['id'], key, it)
    assert DOC['dialects'][IDS.index('ranch')]['axes']['density'][1] <= 50
    assert DOC['dialects'][IDS.index('botanical')]['axes']['density'][1] <= 55


def test_statuses_match_filesystem():
    deferred = set(DOC['deferred'])
    for d in DOC['dialects']:
        for key, kind in TPL.LIST_KINDS.items():
            for it in d[key]:
                assert it['status'] == TPL.status(kind, it['id'], deferred), (d['id'], key, it, 'run python3 lib/templates.py --refresh')


def test_scoring_is_deterministic_and_explained():
    content = {'vibe': {'type': 'castle', 'era': 1911, 'words': ['evening', 'moody', 'grand']}, 'photos': {'items': {}}}
    sig = _signals(dark_share=0.6, shadow_warm=0.8, mean_L=0.3)
    pm = {'candidates': [{'h': 30, 'C': 0.13}], 'temperature': 'warm'}
    a = PERS.score_dialects(DOC, sig, content, pm, {'sites': []})
    b = PERS.score_dialects(copy.deepcopy(DOC), dict(sig), copy.deepcopy(content), dict(pm), {'sites': []})
    assert a == b
    winner, rows = a
    assert winner == 'candlelit'
    cand = next(r for r in rows if r['id'] == 'candlelit')
    # dark share +3, saturated accent +1, clubhouse/theatre prior absent, two vibe words +4 = 8
    assert cand['score'] == 8, cand
    assert all(isinstance(w, str) and isinstance(p, int) for w, p in cand['reasons'])
    assert sum(p for _, p in cand['reasons']) == cand['score']


def test_vibe_type_and_era_rules():
    _, rows = PERS.score_dialects(DOC, _signals(), {'vibe': {'type': 'clubhouse', 'era': 1927, 'words': ['glam', 'period', 'graphic']}}, {}, None)
    deco = next(r for r in rows if r['id'] == 'deco')
    assert rows[0]['id'] == 'deco' and deco['score'] == 2 + 2 + 6, deco   # type prior, era 1920-1945, three words


def test_tie_goes_to_fewer_registered_sites():
    content = {'vibe': {'type': None, 'era': None, 'words': ['water', 'lush', 'serene']}}
    winner, rows = PERS.score_dialects(DOC, _signals(), content, {}, {'sites': []})
    assert [r['score'] for r in rows[:3]] == [2, 2, 2]
    assert winner == 'modern-luxe'      # nothing registered: dialects.json order breaks the tie
    reg = {'sites': [{'id': 'x', 'fingerprint': {'dialect': 'modern-luxe'}}]}
    winner, rows = PERS.score_dialects(DOC, _signals(), content, {}, reg)
    assert winner == 'coastal' and rows[0]['registered'] == 0


def test_clamp_axes_per_dialect():
    for d in DOC['dialects']:
        extreme_lo = {k: 0 for k in PERS.AXES}
        extreme_hi = {k: 100 for k in PERS.AXES}
        for p in (extreme_lo, extreme_hi, PERS.axes_centre(d)):
            out, changes = PERS.clamp_axes(p, d)
            for k in PERS.AXES:
                lo, hi = d['axes'][k]
                assert lo <= out[k] <= hi, (d['id'], k, out[k])
            if d['id'] != 'modern-luxe':
                assert not (out['density'] >= 85 and out['voice'] >= 85), d['id']
            assert all(len(c) == 3 for c in changes)
    luxe = DOC['dialects'][IDS.index('modern-luxe')]
    out, _ = PERS.clamp_axes({k: 100 for k in PERS.AXES}, luxe)
    assert out['density'] == 95 and out['voice'] == 95     # the corner survives only inside modern-luxe
    deco = DOC['dialects'][IDS.index('deco')]
    out, changes = PERS.clamp_axes({'formality': 80, 'scale': 60, 'era': 60, 'density': 85, 'temperature': 50, 'voice': 90}, deco)
    assert out['density'] == 85 and out['voice'] == 84.0    # deco allows both 85s: the corner rule pulls voice back
    assert ['voice', 90, 84.0] in changes


def test_rotation_never_repeats_last():
    assert PERS.rotate_pick(['a', 'b', 'c'], {'a': 2, 'b': 0, 'c': 0}) == 'b'
    assert PERS.rotate_pick(['a', 'b'], {}, last='a') == 'b'
    assert PERS.rotate_pick(['a'], {}, last='a') == 'a'


def test_every_dialect_pairing_and_voice_exists():
    pairings = {p['id'] for p in _util.data('pairings.json')['pairings']}
    voices = set(_util.data('voices.json'))
    for d in DOC['dialects']:
        for it in d['pairings']:
            assert it['id'] in pairings, it
        for it in d['voices']:
            assert it['id'] in voices, it


if __name__ == '__main__':
    import sys
    sys.exit(_util.run_module(sys.modules[__name__]))
