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
from PIL import Image, ImageFilter
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


def _gather_clusters(photo_paths, lead=None):
    clusters = []
    for name, p in photo_paths.items():
        wmul = 2.0 if name == lead else 1.0
        for cl in photo_clusters(p):
            cl = dict(cl); cl['w'] *= wmul; cl['photo'] = name
            clusters.append(cl)
    return clusters


def _accent_pick(clusters, temp, accent_spec=None):
    """Return (accent cluster, deep cluster, ranked candidates, note). With a dialect accent_spec, the best candidate whose
    hue falls inside the dialect's hue ranges wins; if none does, the photo's own best accent is kept and the note says so."""
    cands = [c for c in clusters if c['C'] >= 0.035 and 0.22 <= c['L'] <= 0.80]
    if not cands:  # monochrome photos: fall back to the most chromatic thing we have
        cands = sorted(clusters, key=lambda c: -c['C'])[:3]
    for c in cands:
        # accents are by nature small chromatic areas: favour chroma over pixel share
        c['score'] = (c['w'] ** 0.5) * (c['C'] ** 1.5) * temperature_affinity(c['h'], temp)
    cands.sort(key=lambda c: -c['score'])
    accent = cands[0]
    note = 'photo'
    if accent_spec and accent_spec.get('hue_ranges'):
        inside = [c for c in cands if in_ranges(c['h'], accent_spec['hue_ranges'])]
        if inside:
            accent = inside[0]
            note = 'photo, inside the dialect hue range' if accent is cands[0] else 'photo candidate #%d (best inside the dialect hue range)' % (cands.index(accent) + 1)
        else:
            note = 'photo (no candidate inside the dialect hue range; kept the photo accent)'
    deep = next((c for c in cands if c is not accent and C.hue_distance(c['h'], accent['h']) >= 55), None)
    if deep is None:
        # no second hue in the photos: stay tonal (a deep cut of the accent hue) rather than invent one
        deep = {'L': 0.3, 'C': min(accent['C'], 0.06), 'h': accent['h'], 'photo': accent['photo'], 'w': 0, 'tonal': True}
    return accent, deep, cands, note


def derive(photo_paths, personality, lead=None, overrides=None, dialect=None, tone=None):
    """photo_paths: dict name -> path. lead: name of the lead photo (weighted 2x).
    dialect: a record from data/dialects.json, or None for pre-dialect builds (identical to the original behaviour).
    tone: paper tone bucket (light / mid / tinted / dark-warm / dark-cool); dark tones go to derive_dark()."""
    if tone and tone.startswith('dark'):
        return derive_dark(photo_paths, personality, lead, dialect, tone, overrides)
    clusters = _gather_clusters(photo_paths, lead)
    temp = personality.get('temperature', 50)
    density = personality.get('density', 50)
    formality = personality.get('formality', 50)
    acc_spec = dialect.get('accent') if dialect else None
    accent, deep, cands, accent_note = _accent_pick(clusters, temp, acc_spec)

    h_a, h_d = accent['h'], deep['h']
    C_a = min(accent['C'], 0.14)
    text_L0, fill_L0 = 0.50, 0.55
    if acc_spec:
        C_a = min(max(accent['C'], acc_spec['C'][0]), acc_spec['C'][1], acc_spec.get('fill_max_C', 0.14))
        text_L0 = min(text_L0, acc_spec.get('text_max_L', text_L0))
        fill_L0 = min(fill_L0, acc_spec.get('fill_max_L', fill_L0))

    # Paper: minimal personalities get near-white, lush ones a visibly tinted stock.
    paper_L = 0.985 - 0.03 * (1 - density / 100)
    paper_C = 0.002 + 0.012 * (1 - density / 100)
    paper_h = h_a if (C.is_warm(h_a) or temp >= 50) else 75  # cool accent + warm bias -> cream paper
    if dialect:
        tone = tone or dialect['paper']['tones'][0]
        paper_L, paper_C, paper_h = dialect_paper(dialect['paper'], tone, paper_h)
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
    L, tokens['accent-text'] = C.fit_lightness(min(C_a, 0.12), h_a, tokens['accent-tint'], 7.0, True, text_L0)
    # Accent for non-text uses (rails, dots, focus rings, range thumb): white >= 4.5 if anything sits on it.
    L, tokens['accent'] = C.fit_lightness(C_a, h_a, '#ffffff', 5.0, True, 0.62)
    # Accent for button fills with white labels: 7:1, same bar as every other small text on the page.
    L, tokens['accent-fill'] = C.fit_lightness(C_a, h_a, '#ffffff', 7.3, True, fill_L0)
    # Deep band colour and the text that sits on it.
    deep_C, deep_L0 = min(deep['C'], 0.08), 0.34
    if dialect and dialect.get('deep'):
        dsp = dialect['deep']
        h_d = _nearest_in_ranges(h_d, dsp['H'])
        deep_C, deep_L0 = min(max(deep['C'], dsp['C'][0]), dsp['C'][1]), dsp['L'][1]
    L, tokens['deep'] = C.fit_lightness(deep_C, h_d, tokens['paper'], 9.0, True, deep_L0)
    tokens['on-deep'] = '#ffffff'
    L, tokens['on-deep-soft'] = C.fit_lightness(0.02, h_d, tokens['deep'], 9.0, False, 0.86)
    L, tokens['on-deep-accent'] = C.fit_lightness(min(C_a, 0.08), h_a, tokens['deep'], 7.0, False, 0.80)
    L, tokens['on-ink-soft'] = C.fit_lightness(0.012, ink_h, tokens['ink'], 9.0, False, 0.86)
    tokens['line'] = 'rgba(%d,%d,%d,0.14)' % tuple(int(v * 255) for v in C.hex_to_rgb(tokens['ink']))
    tokens['line-strong'] = 'rgba(%d,%d,%d,0.30)' % tuple(int(v * 255) for v in C.hex_to_rgb(tokens['ink']))
    tokens['focus'] = tokens['accent']
    if overrides:
        tokens.update(overrides)
    tokens['paper'] = never_white(tokens['paper'], paper_h)
    metal = (acc_spec or {}).get('metallic')
    if metal:
        # brass for rules, frames and the crest on light paper: graphics, never text, so 3:1 (WCAG non-text) on paper-3
        mL = metal['L'][0] if isinstance(metal['L'], list) else metal['L']
        mC = metal['C'][0] if isinstance(metal['C'], list) else metal['C']
        mH = (metal['H'][0] + metal['H'][1]) / 2 if isinstance(metal['H'], list) else metal['H']
        L, tokens['metal'] = C.fit_lightness(mC, mH, tokens['paper-3'], 3.0, True, mL)

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
    if dialect:
        meta.update({'mode': 'light', 'tone': tone, 'dialect': dialect['id'], 'accent_note': accent_note})
    return tokens, report, meta


def in_ranges(h, ranges):
    return any(lo <= h <= hi for lo, hi in ranges)


def never_white(hex_, h=75):
    """Shared baseline: paper is never pure white. Pull #ffffff back to the top of the allowed paper range."""
    if hex_.lower() in ('#ffffff', '#fff'):
        return C.lch_to_hex(0.985, 0.004, h)
    return hex_


def _nearest_in_ranges(h, ranges):
    if in_ranges(h, ranges):
        return h
    best = None
    for lo, hi in ranges:
        for edge in (lo, hi):
            d = C.hue_distance(h, edge)
            if best is None or d < best[0]:
                best = (d, edge)
    return best[1]


def dialect_paper(spec, tone, h_hint):
    """(L, C, h) for a light dialect paper. light = top of the L range / bottom of C; mid = the middle; tinted = bottom
    of L / top of C (or the dialect's named tinted variant, e.g. editorial blush). Hue: the photo-derived hint clamped
    into the dialect's hue ranges. Always inside the shared baseline (L 0.93-0.985, C 0.004-0.022)."""
    Ls, Cs, Hs = spec['L'], spec['C'], spec['H']
    if tone == 'tinted' and spec.get('tinted'):
        Cs, Hs = spec['tinted'].get('C', Cs), spec['tinted'].get('H', Hs)
    pos = {'light': 0.0, 'mid': 0.5, 'tinted': 1.0}.get(tone, 0.5)
    L = Ls[1] - pos * (Ls[1] - Ls[0])
    Ch = Cs[0] + pos * (Cs[1] - Cs[0])
    L, Ch = min(max(L, 0.93), 0.985), min(max(Ch, 0.004), 0.022)
    return L, Ch, _nearest_in_ranges(h_hint, Hs)


# --- photo signals for dialect selection (spec section 3) ---------------------------------------------------------
SIGNAL_KEYS = ('mean_L', 'mono_share', 'foliage_share', 'water_share', 'dark_share', 'earth_share', 'shadow_warm')


def signals_from_pixels(rgb):
    """rgb: (n, 3) floats 0..1. Shares are fractions of all pixels, in OKLCH:
      mean_L        mean OKLab lightness
      mono_share    C < 0.03 (near-neutral)
      foliage_share H 90-160 and C > 0.05
      water_share   H 200-260 and C > 0.02 (hue is meaningless below that chroma)
      dark_share    L < 0.35
      earth_share   H 20-90 and 0.03 <= C <= 0.10 (stone, terracotta, ochre)
      shadow_warm   of the dark (L < 0.35) chromatic (C > 0.015) pixels, the share with a warm hue (10-110)"""
    lch = C.lab_to_lch(C.rgb_to_oklab(np.asarray(rgb, dtype=np.float64)))
    L, Ch, H = lch[:, 0], lch[:, 1], lch[:, 2]
    n = float(len(L))
    dark_chroma = (L < 0.35) & (Ch > 0.015)
    out = {
        'mean_L': float(L.mean()),
        'mono_share': float((Ch < 0.03).sum() / n),
        'foliage_share': float(((H >= 90) & (H <= 160) & (Ch > 0.05)).sum() / n),
        'water_share': float(((H >= 200) & (H <= 260) & (Ch > 0.02)).sum() / n),
        'dark_share': float((L < 0.35).sum() / n),
        'earth_share': float(((H >= 20) & (H <= 90) & (Ch >= 0.03) & (Ch <= 0.10)).sum() / n),
        'shadow_warm': float((dark_chroma & (H >= 10) & (H <= 110)).sum() / max(1.0, float(dark_chroma.sum()))),
    }
    return {k: round(v, 4) for k, v in out.items()}


def photo_signal(path, width=160):
    im = Image.open(path).convert('RGB')
    im.thumbnail((width, width * 3))
    return signals_from_pixels(np.asarray(im, dtype=np.float64).reshape(-1, 3) / 255)


def aggregate_signals(per, lead=None):
    """Weighted mean of per-photo signals, lead weighted 2x. warm_shadows = shadow_warm >= 0.5."""
    wts = {name: (2.0 if name == lead else 1.0) for name in per}
    tot = sum(wts.values())
    agg = {k: round(sum(per[n][k] * wts[n] for n in per) / tot, 4) for k in SIGNAL_KEYS}
    agg['warm_shadows'] = bool(agg['shadow_warm'] >= 0.5)
    agg['per_photo'] = per
    agg['lead'] = lead
    return agg


def photo_signals(photo_paths, lead=None):
    """Deterministic (no sampling): the same photos always give the same signals."""
    return aggregate_signals({name: photo_signal(p) for name, p in photo_paths.items()}, lead)


# --- text-on-photo feasibility (stage 2C) ---------------------------------------------------------------------------
# Where a hero sets copy on the lead photo, as fractions (left, top, right, bottom) of a 1440 x 860 cover crop.
COPY_ZONES = {'cinematic': (0.04, 0.50, 0.55, 0.95), 'crest': (0.22, 0.25, 0.78, 0.85)}
COPY_ZONE_MIN = 4.5     # small text on the photo (kicker, lede, buttons) needs 4.5:1 in qa.py
COPY_ZONE_SCRIM = 0.35  # the E9 cap: no scrim stop darker than 35% black


def copy_zone_contrast(path, focal='50% 50%', scrim=COPY_ZONE_SCRIM, q=99, viewport=(1440, 860)):
    """Estimated worst-case contrast of white copy over each COPY_ZONES box of the photo under a uniform `scrim`
    (conservative: the real gradients reach the cap only at their darkest stop). qa.py takes the minimum ratio under
    every glyph, so the estimate uses the q-th percentile of zone luminance, not the mean. Deterministic."""
    im = Image.open(path).convert('RGB')
    W, H = im.size
    fx, fy = [float(s.strip('%')) / 100 for s in focal.split()]
    ar = viewport[0] / float(viewport[1])
    cw, ch = (H * ar, H) if W / float(H) > ar else (W, W / ar)
    x0 = min(max(fx * W - cw / 2, 0), W - cw); y0 = min(max(fy * H - ch / 2, 0), H - ch)
    gw, gh = 288, int(round(288 / ar))
    a = np.asarray(im.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize((gw, gh)), dtype=np.float64) / 255
    Y = C.srgb_to_linear(a) @ np.array([0.2126, 0.7152, 0.0722])
    out = {}
    for z, (l, t, r, b) in COPY_ZONES.items():
        y = float(np.percentile(Y[int(t * gh):int(b * gh), int(l * gw):int(r * gw)], q))
        out[z] = round(1.05 / (y * (1 - scrim) + 0.05), 2)
    return out


VEIL_BLUR_PX = 32     # 2D: cinematic "veil": a feathered backdrop-filter blur under the copy (heroes/cinematic.css.j2)
VEIL_SCRIM = 0.25     # estimated at the strictest dialect cap (candlelit 25%), so the verdict holds in every dialect
VEIL_ZONES = {'cinematic-veil': 'cinematic'}


def copy_zone_veil(path, focal='50% 50%', blur=VEIL_BLUR_PX, scrim=VEIL_SCRIM, q=99, viewport=(1440, 860)):
    """Worst-case white-copy contrast in each veil zone when the photo under the copy is blurred by `blur` css px
    (Gaussian sigma, as CSS blur()) and darkened by at most `scrim`. Measured at the real 1440 px viewport, not the coarse
    grid of copy_zone_contrast, because blur removes exactly the small highlights (lamps, sky gaps) that fail the p99.
    The blur changes no colour and adds no flat wash (E9); qa.py re-measures the rendered page."""
    im = Image.open(path).convert('RGB')
    W, H = im.size
    fx, fy = [float(s.strip('%')) / 100 for s in focal.split()]
    ar = viewport[0] / float(viewport[1])
    cw, ch = (H * ar, H) if W / float(H) > ar else (W, W / ar)
    x0 = min(max(fx * W - cw / 2, 0), W - cw); y0 = min(max(fy * H - ch / 2, 0), H - ch)
    crop = im.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize(viewport, Image.BILINEAR).filter(ImageFilter.GaussianBlur(blur))
    with np.errstate(all='ignore'):   # spurious BLAS matmul warnings on macOS Accelerate; values are finite
        Y = C.srgb_to_linear(np.asarray(crop, dtype=np.float64) / 255) @ np.array([0.2126, 0.7152, 0.0722])
    gh, gw = Y.shape
    out = {}
    for vz, z in VEIL_ZONES.items():
        l, t, r, b = COPY_ZONES[z]
        y = float(np.percentile(Y[int(t * gh):int(b * gh), int(l * gw):int(r * gw)], q))
        out[vz] = round(1.05 / (y * (1 - scrim) + 0.05), 2)
    return out


# --- dark (charcoal paper) token set ------------------------------------------------------------------------------
def dark_tokens(paper_L, paper_C, paper_h, accent_h, accent_C, metal=None, text_min_L=0.70):
    """Charcoal-ground token set. Same names as the light set so templates need no special cases, plus:
      on-accent  label colour on accent / accent-fill buttons (dark, L 0.18; light labels on a mid accent fail 7:1)
      metal      brass for rules / frames / kickers, walked lighter until it passes 7:1 on paper-3
      field      form-field background
    Every small-text pair is walked to >= 7:1 with the same lightness walker as the light set (color.fit_lightness),
    against the lightest surface it can sit on (paper-3), so it passes on paper and paper-2 too."""
    metal = metal or {'L': [0.74, 0.78], 'C': [0.09, 0.12], 'H': [75, 90]}
    mL = metal['L'][0] if isinstance(metal['L'], list) else metal['L']
    mL = max(mL, metal.get('walk_min_L', 0.74))
    mC = metal['C'][0] if isinstance(metal['C'], list) else metal['C']
    mH = (metal['H'][0] + metal['H'][1]) / 2 if isinstance(metal['H'], list) else metal['H']
    paper_L = min(max(paper_L, 0.16), 0.24)
    t = {}
    t['paper'] = C.lch_to_hex(paper_L, paper_C, paper_h)
    t['paper-2'] = C.lch_to_hex(paper_L + 0.05, paper_C * 1.2, paper_h)   # surface-2 for cards (spec L 0.24-0.28)
    t['paper-3'] = C.lch_to_hex(paper_L + 0.08, paper_C * 1.4, paper_h)
    t['white'] = t['paper-2']   # templates use --white for card grounds; on charcoal the card is surface-2
    L, t['ink'] = C.fit_lightness(0.01, paper_h, t['paper-3'], 9.0, False, 0.93)
    L, t['ink-soft'] = C.fit_lightness(0.012, paper_h, t['paper-3'], 7.0, False, 0.80)   # captions L >= 0.80
    L, t['ink-faint'] = C.fit_lightness(0.014, paper_h, t['paper-3'], 7.0, False, 0.74)
    t['accent-tint'] = C.lch_to_hex(paper_L + 0.05, min(0.03, accent_C * 0.4), accent_h)
    L, t['accent-text'] = C.fit_lightness(min(accent_C, 0.10), accent_h, t['paper-3'], 7.0, False, max(0.70, text_min_L))
    L, t['metal'] = C.fit_lightness(mC, mH, t['paper-3'], 7.0, False, mL)
    t['on-accent'] = C.lch_to_hex(0.18, 0.01, paper_h)
    # 2C: same 7.3 target as the light set's accent-fill: 7.0 exactly measured 6.98 in qa.py (hex rounding + AA)
    L, t['accent-fill'] = C.fit_lightness(accent_C, accent_h, t['on-accent'], 7.3, False, 0.60)
    L, t['accent'] = C.fit_lightness(accent_C, accent_h, t['on-accent'], 5.0, False, 0.58)
    t['deep'] = C.lch_to_hex(max(0.11, paper_L - 0.06), paper_C, paper_h)
    t['on-deep'] = t['ink']
    L, t['on-deep-soft'] = C.fit_lightness(0.012, paper_h, t['deep'], 9.0, False, 0.84)
    L, t['on-deep-accent'] = C.fit_lightness(mC, mH, t['deep'], 7.0, False, mL)
    L, t['on-ink-soft'] = C.fit_lightness(0.012, paper_h, t['ink'], 9.0, True, 0.30)
    t['field'] = t['paper-3']
    t['line'] = 'rgba(%d,%d,%d,0.18)' % tuple(int(v * 255) for v in C.hex_to_rgb(t['ink']))
    t['line-strong'] = 'rgba(%d,%d,%d,0.34)' % tuple(int(v * 255) for v in C.hex_to_rgb(t['ink']))
    t['focus'] = t['accent']
    return t


def dark_checks(t):
    """Every text/surface pair the dark set must pass. Small text 7:1; the UI accent 5:1 with its label."""
    return [
        ('ink on paper', t['ink'], t['paper'], 7), ('ink on paper-2', t['ink'], t['paper-2'], 7), ('ink on paper-3', t['ink'], t['paper-3'], 7),
        ('ink-soft on paper', t['ink-soft'], t['paper'], 7), ('ink-soft on paper-2', t['ink-soft'], t['paper-2'], 7),
        ('ink-faint on paper-3', t['ink-faint'], t['paper-3'], 7),
        ('accent-text on paper-2', t['accent-text'], t['paper-2'], 7), ('accent-text on accent-tint', t['accent-text'], t['accent-tint'], 7),
        ('ink on accent-tint', t['ink'], t['accent-tint'], 7),
        ('metal on paper', t['metal'], t['paper'], 7), ('metal on paper-2', t['metal'], t['paper-2'], 7),
        ('on-accent on accent-fill', t['on-accent'], t['accent-fill'], 7), ('on-accent on accent', t['on-accent'], t['accent'], 5),
        ('on-deep on deep', t['on-deep'], t['deep'], 7), ('on-deep-soft on deep', t['on-deep-soft'], t['deep'], 7),
        ('on-deep-accent on deep', t['on-deep-accent'], t['deep'], 7),
        ('paper on ink', t['paper'], t['ink'], 7), ('on-ink-soft on ink', t['on-ink-soft'], t['ink'], 7),
        ('ink on field', t['ink'], t['field'], 7),
    ]


def run_checks(checks):
    report, ok = [], True
    for label, fg, bg, need in checks:
        r = C.contrast(fg, bg)
        report.append({'pair': label, 'fg': fg, 'bg': bg, 'ratio': round(float(r), 2), 'need': need, 'ok': bool(r >= need)})
        ok = ok and r >= need
    return report, ok


def derive_dark(photo_paths, personality, lead=None, dialect=None, tone='dark-warm', overrides=None):
    """Dark dialects (candlelit; the estate castle and deco charcoal variants). Paper hue comes from the dialect's warm
    or cool shadow range (tone), the chromatic accent from the photos (dialect hue ranges preferred)."""
    clusters = _gather_clusters(photo_paths, lead)
    dialect = dialect or {}
    spec = dialect.get('paper', {})
    if spec.get('mode') != 'dark':
        spec = dialect.get('paper_dark') or {'L': [0.17, 0.23], 'C': [0.006, 0.02], 'H': [[60, 80], [250, 270]]}
    acc_spec = dialect.get('accent')
    accent, deep, cands, accent_note = _accent_pick(clusters, personality.get('temperature', 50), acc_spec)
    warm_r = [r for r in spec['H'] if C.is_warm((r[0] + r[1]) / 2)] or spec['H']
    cool_r = [r for r in spec['H'] if not C.is_warm((r[0] + r[1]) / 2)] or spec['H']
    rng = cool_r if tone == 'dark-cool' else warm_r
    paper_h = (rng[0][0] + rng[0][1]) / 2
    paper_L = (spec['L'][0] + spec['L'][1]) / 2
    paper_C = (spec['C'][0] + spec['C'][1]) / 2
    C_a = min(accent['C'], 0.14)
    if acc_spec:
        C_a = min(max(accent['C'], acc_spec['C'][0]), acc_spec['C'][1], acc_spec.get('fill_max_C', 0.14))
    t = dark_tokens(paper_L, paper_C, paper_h, accent['h'], C_a, (acc_spec or {}).get('metallic'), (acc_spec or {}).get('text_min_L', 0.70))
    if overrides:
        t.update(overrides)
    report, ok = run_checks(dark_checks(t))
    accent_lch = C.hex_to_lch(t['accent'])
    meta = {
        'mode': 'dark', 'tone': tone, 'dialect': dialect.get('id'), 'accent_note': accent_note,
        'accent_hue': round(float(accent_lch[2]), 1), 'accent_chroma': round(float(accent_lch[1]), 3), 'accent_from_photo': accent['photo'],
        'deep_hue': round(paper_h, 1), 'deep_from_photo': None,
        'paper_L': round(paper_L, 3), 'paper_C': round(paper_C, 4), 'paper_hue': round(paper_h, 1),
        'temperature': 'warm' if C.is_warm(accent_lch[2]) else 'cool',
        'candidates': [{k: (round(v, 3) if isinstance(v, float) else v) for k, v in c.items()} for c in cands[:6]],
        'all_pairs_pass': bool(ok),
    }
    return t, report, meta


def css_vars(tokens):
    return '\n'.join('    --%s: %s;' % (k, v) for k, v in tokens.items())


if __name__ == '__main__':
    import sys
    paths = {p.split('/')[-1].split('.')[0]: p for p in sys.argv[1:]}
    t, rep, meta = derive(paths, {'temperature': 50, 'density': 50, 'formality': 50})
    print(json.dumps({'tokens': t, 'report': rep, 'meta': meta}, indent=1))
