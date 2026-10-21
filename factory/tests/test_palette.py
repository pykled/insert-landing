"""Dark (charcoal) token set + the 7:1 walker, photo signals, and the never-white paper baseline."""
import os
import numpy as np
from PIL import Image
from tests import _util
from lib import palette as P, color as C


def _img(path, rgb, size=(64, 48)):
    Image.new('RGB', size, rgb).save(path)
    return path


def test_dark_tokens_pass_every_pair():
    # warm and cool charcoal grounds, every accent hue family, low and high chroma: the walker must always land >= need
    for paper_L, paper_h in ((0.17, 70), (0.20, 70), (0.23, 260), (0.18, 85)):
        for accent_h in (30, 85, 145, 250, 330):
            for accent_C in (0.07, 0.12):
                t = P.dark_tokens(paper_L, 0.012, paper_h, accent_h, accent_C)
                report, ok = P.run_checks(P.dark_checks(t))
                bad = [r for r in report if not r['ok']]
                assert ok and not bad, (paper_L, paper_h, accent_h, accent_C, bad)


def test_dark_tokens_spec_targets():
    t = P.dark_tokens(0.20, 0.012, 70, 30, 0.10)
    L_paper = float(C.hex_to_lch(t['paper'])[0])
    assert 0.16 <= L_paper <= 0.24, L_paper                       # charcoal L 0.16-0.24
    assert float(C.hex_to_lch(t['ink'])[0]) >= 0.90                # warm off-white text
    assert float(C.hex_to_lch(t['metal'])[0]) >= 0.74              # brass walked to L >= 0.74
    assert float(C.hex_to_lch(t['ink-soft'])[0]) >= 0.80           # captions L >= 0.80
    assert C.contrast(t['on-accent'], t['accent-fill']) >= 7       # dark label on the button fill


def test_derive_dark_from_photos(tmp_path):
    d = _util.data('dialects.json')
    candlelit = next(x for x in d['dialects'] if x['id'] == 'candlelit')
    paths = {'a': _img(os.path.join(str(tmp_path), 'a.jpg'), (40, 28, 18)), 'b': _img(os.path.join(str(tmp_path), 'b.jpg'), (150, 40, 30))}
    for tone in ('dark-warm', 'dark-cool'):
        t, report, meta = P.derive(paths, {'temperature': 30}, lead='a', dialect=candlelit, tone=tone)
        assert meta['mode'] == 'dark' and meta['all_pairs_pass'], [r for r in report if not r['ok']]
        assert t['paper'] != '#ffffff'


def test_light_dialect_paper_inside_baseline_and_never_white(tmp_path):
    d = _util.data('dialects.json')
    paths = {'a': _img(os.path.join(str(tmp_path), 'a.jpg'), (250, 250, 250)), 'b': _img(os.path.join(str(tmp_path), 'b.jpg'), (90, 120, 160))}
    for dia in d['dialects']:
        if dia['paper']['mode'] != 'light':
            continue
        for tone in dia['paper']['tones']:
            t, report, meta = P.derive(paths, {'temperature': 50, 'density': 95, 'formality': 80}, lead='a', dialect=dia, tone=tone)
            L, Ch, h = (float(x) for x in C.hex_to_lch(t['paper']))
            assert t['paper'].lower() != '#ffffff', (dia['id'], tone)
            assert 0.925 <= L <= 0.99 and Ch >= 0.003, (dia['id'], tone, t['paper'], L, Ch)
            assert meta['all_pairs_pass'], (dia['id'], tone, [r for r in report if not r['ok']])
    assert P.never_white('#ffffff') != '#ffffff'
    assert P.never_white('#f4f1ea') == '#f4f1ea'


def test_signals_from_pixels():
    green = np.tile([[0.25, 0.55, 0.20]], (100, 1))
    s = P.signals_from_pixels(green)
    assert s['foliage_share'] > 0.9 and s['mono_share'] < 0.1
    grey = np.tile([[0.80, 0.80, 0.80]], (100, 1))
    s = P.signals_from_pixels(grey)
    assert s['mono_share'] > 0.9 and s['mean_L'] > 0.8
    dark = np.tile([[0.12, 0.08, 0.05]], (100, 1))
    s = P.signals_from_pixels(dark)
    assert s['dark_share'] > 0.9 and s['shadow_warm'] > 0.9
    sea = np.tile([[0.20, 0.45, 0.75]], (100, 1))
    assert P.signals_from_pixels(sea)['water_share'] > 0.9


def test_signals_lead_weighted():
    per = {'lead': {k: 1.0 for k in P.SIGNAL_KEYS}, 'other': {k: 0.0 for k in P.SIGNAL_KEYS}}
    agg = P.aggregate_signals(per, lead='lead')
    assert abs(agg['foliage_share'] - 2 / 3) < 1e-3


if __name__ == '__main__':
    import sys
    sys.exit(_util.run_module(sys.modules[__name__]))
