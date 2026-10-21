"""Fingerprint schema 2: weights, same-dialect rule, quota, pHash, registry integrity."""
import os
import numpy as np
from PIL import Image
from tests import _util
from lib import fingerprint as FP, phash as PH

BASE = {'display_family': 'Cardo', 'display_class': 'garalde', 'body_family': 'Nunito Sans', 'accent_hue': 120.0, 'paper_temperature': 'warm',
        'hero': 'frame', 'hero_family': 'photo-matted', 'spaces': 'stack', 'story': 'timeline', 'faq': 'accordion-split', 'tour': 'scheduler-split',
        'section_order': ['hero', 'spaces', 'story', 'day', 'tour', 'guide', 'faq', 'uses'], 'moment': 'light-shift', 'button_style': 'soft-solid',
        'radius': 4, 'lead_photo': 'hero', 'dialect': 'botanical', 'pairing': 'botanical-cardo', 'paper_tone': 'light', 'hero_framing': 'inset',
        'display_case': 'sentence', 'ornament': 'botanical-line', 'body_px': 19, 'photo_edge': 'arch', 'motion_device': 'draw-in', 'nav_style': 'bar'}


def _site(i, **kw):
    fp = dict(BASE); fp.update(kw)
    return {'id': 's%d' % i, 'fingerprint': fp, 'meta': {}}


def test_weights_sum_to_one_and_scale():
    assert abs(sum(FP.WEIGHTS.values()) - 1.0) < 1e-6
    assert abs(FP.WEIGHTS['display_family'] - 0.16 * 0.66) < 1e-9
    assert FP.WEIGHTS['paper_tone'] == 0.06 and FP.WEIGHTS['ornament'] == 0.06
    assert 'dialect' not in FP.WEIGHTS and 'pairing' not in FP.WEIGHTS


def test_same_dialect_needs_four_key_differences():
    # Many weighted differences (display face, accent hue, hero archetype, story, faq, tour, motion, nav) but only three
    # of the seven key dims differ: the weighted sum alone would pass; the same-dialect rule refuses.
    other = dict(BASE, display_family='EB Garamond', display_class='garalde', body_family='Karla', accent_hue=300.0, hero='arch-split',
                 hero_family='split', story='pullquote', faq='numbered', tour='scheduler-centered', button_style='square-outline-caps',
                 radius=12, nav_style='centered', motion_device='none', section_order=['hero', 'story', 'faq'],
                 pairing='garden-garamond', ornament='leaf-rule', paper_tone='tinted')
    assert FP.key_differences(BASE, other) == ['pairing', 'ornament', 'paper_tone']
    d = FP.distance(BASE, other)
    assert d >= FP.SAME_WARN, d
    status, dist, why, _ = FP.pair_verdict(BASE, other)
    assert status == 'refuse' and '3 of 7' in why, why
    four = dict(other, body_px=17)
    assert FP.pair_verdict(BASE, four)[0] == 'ok'


def test_same_dialect_uses_lower_thresholds():
    near = dict(BASE, pairing='x', hero_framing='split', ornament='leaf-rule', paper_tone='tinted', accent_hue=150.0, display_family='Fraunces', story='pullquote')
    d = FP.distance(BASE, near)
    st, _, why, _ = FP.pair_verdict(BASE, near)
    assert FP.SAME_REFUSE <= d < FP.REFUSE and st in ('warn', 'ok'), (d, st)   # would refuse across dialects
    cross = dict(near, dialect='estate')
    assert FP.pair_verdict(BASE, cross)[0] == 'refuse'


def test_quota_warns_on_second_refuses_on_third():
    reg = {'sites': []}
    assert FP.quota(BASE, reg)[0] == 'ok'
    reg['sites'].append(_site(1, accent_hue=300, ornament='leaf-rule', paper_tone='tinted', spaces='index', moment='guest-journey', body_px=17))
    assert FP.quota(BASE, reg)[0] == 'warn'
    reg['sites'].append(_site(2, accent_hue=200, ornament='watercolour-wash', paper_tone='mid', spaces='index', moment='season-toggle', body_px=21))
    st, ids = FP.quota(BASE, reg)
    assert st == 'refuse' and ids == ['s1', 's2']
    g = FP.guard(BASE, reg)
    assert g['status'] == 'refuse' and g['quota']['status'] == 'refuse'


def test_pre_dialect_sites_never_trigger_same_dialect_rule():
    a = dict(BASE, dialect='none'); b = dict(BASE, dialect='none', accent_hue=300.0)
    assert not FP.same_dialect(a, b)
    assert FP.quota(a, {'sites': [_site(1, dialect='none')]})[0] == 'ok'


def test_phash_identical_and_different(tmp_path):
    rng = np.random.default_rng(1)
    img = Image.fromarray((rng.random((900, 1440)) * 255).astype('uint8')).convert('RGB')
    h1 = {'fold': PH.fold_hash(img), 'strip': PH.strip_hash(img)}
    assert len(h1['fold']) == 64 and PH.hamming(h1['fold'], h1['fold']) == 0
    stripes = Image.new('RGB', (1440, 900), 'white')
    for y in range(0, 900, 120):
        stripes.paste((20, 20, 20), (0, y, 1440, y + 60))
    h2 = {'fold': PH.fold_hash(stripes), 'strip': PH.strip_hash(stripes)}
    assert PH.hamming(h1['fold'], h2['fold']) > PH.WARN
    reg = {'sites': [{'id': 'same', 'phash': h1}, {'id': 'other', 'phash': h2}, {'id': 'none'}]}
    st, rows = PH.compare(h1, reg)
    assert st == 'refuse' and rows[0]['id'] == 'same' and rows[0]['min'] == 0
    st, rows = PH.compare(h1, reg, exclude_id='same')
    assert st == 'ok'
    flat = Image.new('RGB', (1440, 900), (240, 238, 232))
    assert PH.fold_hash(flat) == PH.fold_hash(flat.resize((2880, 1800)))   # DPR does not change the hash


def test_registry_schema_two_and_matrix():
    reg = _util.data('registry.json')
    assert reg['schema_version'] == 2
    assert len(reg['sites']) >= 5
    for s in reg['sites']:
        for k in ('dialect', 'paper_tone', 'hero_framing', 'display_case', 'ornament', 'body_px', 'photo_edge', 'motion_device', 'nav_style'):
            assert k in s['fingerprint'], (s['id'], k)
    lines = FP.matrix_lines(reg)
    assert len(lines) == len(reg['sites']) + 2


if __name__ == '__main__':
    import sys
    sys.exit(_util.run_module(sys.modules[__name__]))
