"""Derive an accessible token palette from the venue's own photographs.

Steps
1. Downscale each chosen photo to ~160px and convert every pixel to OKLab.
2. k-means (k=7) per photo; merge clusters across photos, weighting the lead photo 2x.
3. Candidate accents = chromatic mid-tone clusters (C >= 0.045, 0.25 <= L <= 0.78), scored by
   pixel share x chroma^0.7 x temperature affinity (the personality's warm/cool bias).
4. Accent hue + a 'deep' secondary hue (>= 55 degrees away) drive the token set.
5. Every text/surface pair the templates use is checked with WCAG 2.x contrast and the lightness
   is walked until the pair passes. Small text targets 7:1 (we measure the darkest pixel under
   each glyph in QA, so AA at 4.5 is not enough headroom); large text 4.5; UI fills 4.5 with white.

All of this is deterministic (fixed seed), so the same photos + the same personality always give
the same palette, and a human can override any token in the build config.
"""
import json
import numpy as np
from PIL import Image
from . import color as C

SEED = 7


def _kmeans(X, k, iters=18, seed=SEED):
    rng = np.random.default_rng(seed)
    cent = X[rng.choice(len(X), k, replace=False)]
    for _ in range(iters):
        d = ((X[:, None, :] - cent[None, :, :]) ** 2).sum(-1)
        lab = d.argmin(1)
        new = np.array([X[lab == i].mean(0) if np.any(lab == i) else cent[i] for i in range(k)])
        if np.allclose(new, cent, atol=1e-4):
            break
        cent = new
    d = ((X[:, None, :] - cent[None, :, :]) ** 2).sum(-1)
    lab = d.argmin(1)
    counts = np.bincount(lab, minlength=k) / len(X)
    return cent, counts


def photo_clusters(path, k=8, width=160):
    im = Image.open(path).convert('RGB')
    im.thumbnail((width, width * 3))
    arr = np.asarray(im, dtype=np.float64).reshape(-1, 3) / 255
    lab = C.rgb_to_oklab(arr)
    cent, counts = _kmeans(lab, k)
    out = []
    for c, w in zip(cent, counts):
        L, Ch, h = C.lab_to_lch(c)
        out.append({'L': float(L), 'C': float(Ch), 'h': float(h), 'w': float(w)})
    return out


def temperature_affinity(h, temperature):
    """temperature: 0 warm .. 100 cool. Returns 0.45..1.0 multiplier for a hue."""
    t = temperature / 100
    warm = 1.0 if C.is_warm(h) else 0.45
    cool = 1.0 if (130 <= h <= 300) else 0.45
    return warm * (1 - t) + cool * t


def derive(photo_paths, personality, lead=None, overrides=None):
    """photo_paths: dict name -> path. lead: name of the lead photo (weighted 2x)."""
    clusters = []
    for name, p in photo_paths.items():
        wmul = 2.0 if name == lead else 1.0
        for cl in photo_clusters(p):
            cl = dict(cl); cl['w'] *= wmul; cl['photo'] = name
            clusters.append(cl)
    temp = personality.get('temperature', 50)
    density = personality.get('density', 50)
    formality = personality.get('formality', 50)

    cands = [c for c in clusters if c['C'] >= 0.035 and 0.22 <= c['L'] <= 0.80]
    if not cands:  # monochrome photos: fall back to the most chromatic thing we have
        cands = sorted(clusters, key=lambda c: -c['C'])[:3]
    for c in cands:
        # accents are by nature small chromatic areas: favour chroma over pixel share
        c['score'] = (c['w'] ** 0.5) * (c['C'] ** 1.5) * temperature_affinity(c['h'], temp)
    cands.sort(key=lambda c: -c['score'])
    accent = cands[0]
    deep = next((c for c in cands[1:] if C.hue_distance(c['h'], accent['h']) >= 55), None)
    if deep is None:
        # no second hue in the photos: stay tonal (a deep cut of the accent hue) rather than invent one
        deep = {'L': 0.3, 'C': min(accent['C'], 0.06), 'h': accent['h'], 'photo': accent['photo'], 'w': 0, 'tonal': True}

    h_a, h_d = accent['h'], deep['h']
    C_a = min(accent['C'], 0.14)

    # Paper: minimal personalities get near-white, lush ones a visibly tinted stock.
    paper_L = 0.985 - 0.03 * (1 - density / 100)
    paper_C = 0.002 + 0.012 * (1 - density / 100)
    paper_h = h_a if (C.is_warm(h_a) or temp >= 50) else 75  # cool accent + warm bias -> cream paper
    tokens = {}
    tokens['paper'] = C.lch_to_hex(paper_L, paper_C, paper_h)
    tokens['paper-2'] = C.lch_to_hex(paper_L - 0.03, paper_C * 1.6, paper_h)
    tokens['paper-3'] = C.lch_to_hex(paper_L - 0.065, paper_C * 2.0, paper_h)
    tokens['white'] = '#ffffff'

    ink_h = h_d if formality >= 50 else h_a
    tokens['ink'] = C.lch_to_hex(0.21, 0.012, ink_h)
    L, tokens['ink-soft'] = C.fit_lightness(0.014, ink_h, tokens['paper-2'], 9.0, True, 0.40)
    L, tokens['ink-faint'] = C.fit_lightness(0.016, ink_h, tokens['paper-3'], 7.0, True, 0.50)

    tokens['accent-tint'] = C.lch_to_hex(paper_L - 0.045, min(0.045, C_a * 0.5), h_a)
    # Accent for small text: walk darker until >= 7:1 on accent-tint (the darkest light surface it sits on).
    L, tokens['accent-text'] = C.fit_lightness(min(C_a, 0.12), h_a, tokens['accent-tint'], 7.0, True, 0.50)
    # Accent for non-text uses (rails, dots, focus rings, range thumb): white >= 4.5 if anything sits on it.
    L, tokens['accent'] = C.fit_lightness(C_a, h_a, '#ffffff', 5.0, True, 0.62)
    # Accent for button fills with white labels: 7:1, same bar as every other small text on the page.
    L, tokens['accent-fill'] = C.fit_lightness(C_a, h_a, '#ffffff', 7.3, True, 0.55)
    # Deep band colour and the text that sits on it.
    L, tokens['deep'] = C.fit_lightness(min(deep['C'], 0.08), h_d, tokens['paper'], 9.0, True, 0.34)
    tokens['on-deep'] = '#ffffff'
    L, tokens['on-deep-soft'] = C.fit_lightness(0.02, h_d, tokens['deep'], 9.0, False, 0.86)
    L, tokens['on-deep-accent'] = C.fit_lightness(min(C_a, 0.08), h_a, tokens['deep'], 7.0, False, 0.80)
    L, tokens['on-ink-soft'] = C.fit_lightness(0.012, ink_h, tokens['ink'], 9.0, False, 0.86)
    tokens['line'] = 'rgba(%d,%d,%d,0.14)' % tuple(int(v * 255) for v in C.hex_to_rgb(tokens['ink']))
    tokens['line-strong'] = 'rgba(%d,%d,%d,0.30)' % tuple(int(v * 255) for v in C.hex_to_rgb(tokens['ink']))
    tokens['focus'] = tokens['accent']
    if overrides:
        tokens.update(overrides)

    checks = [
        ('ink on paper', tokens['ink'], tokens['paper'], 7),
        ('ink-soft on paper-2', tokens['ink-soft'], tokens['paper-2'], 7),
        ('ink-faint on paper-3', tokens['ink-faint'], tokens['paper-3'], 7),
        ('accent-text on paper-2', tokens['accent-text'], tokens['paper-2'], 7),
        ('white on accent', '#ffffff', tokens['accent'], 4.5),
        ('white on accent-fill', '#ffffff', tokens['accent-fill'], 7),
        ('paper on deep', tokens['paper'], tokens['deep'], 7),
        ('on-deep-soft on deep', tokens['on-deep-soft'], tokens['deep'], 7),
        ('on-deep-accent on deep', tokens['on-deep-accent'], tokens['deep'], 7),
        ('paper on ink', tokens['paper'], tokens['ink'], 7),
        ('on-ink-soft on ink', tokens['on-ink-soft'], tokens['ink'], 7),
        ('ink on accent-tint', tokens['ink'], tokens['accent-tint'], 7),
        ('accent-text on accent-tint', tokens['accent-text'], tokens['accent-tint'], 7),
    ]
    report = []
    ok = True
    for label, fg, bg, need in checks:
        r = C.contrast(fg, bg)
        report.append({'pair': label, 'fg': fg, 'bg': bg, 'ratio': round(float(r), 2), 'need': need, 'ok': bool(r >= need)})
        ok = ok and r >= need

    accent_lch = C.hex_to_lch(tokens['accent'])
    meta = {
        'accent_hue': round(float(accent_lch[2]), 1), 'accent_chroma': round(float(accent_lch[1]), 3),
        'accent_from_photo': accent['photo'], 'deep_hue': round(h_d, 1), 'deep_from_photo': deep.get('photo'),
        'paper_L': round(paper_L, 3), 'paper_C': round(paper_C, 4), 'paper_hue': round(paper_h, 1),
        'temperature': 'warm' if C.is_warm(accent_lch[2]) else 'cool',
        'candidates': [{k: (round(v, 3) if isinstance(v, float) else v) for k, v in c.items()} for c in cands[:6]],
        'all_pairs_pass': bool(ok),
    }
    return tokens, report, meta


def css_vars(tokens):
    return '\n'.join('    --%s: %s;' % (k, v) for k, v in tokens.items())


if __name__ == '__main__':
    import sys
    paths = {p.split('/')[-1].split('.')[0]: p for p in sys.argv[1:]}
    t, rep, meta = derive(paths, {'temperature': 50, 'density': 50, 'formality': 50})
    print(json.dumps({'tokens': t, 'report': rep, 'meta': meta}, indent=1))
