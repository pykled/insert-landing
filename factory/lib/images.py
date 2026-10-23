"""Responsive WebP sets from the venue's source photos. Never upscales.

A width is written only when it is <= the source's pixel width. Output names are <name>-<w>.webp so the
QA gate can read the served width from the filename and compare it with the rendered size.
3A item 5 (one budget for build and preview): every rendition is <= MAX_BYTES (400 KB, the same constant preview.py
refuses on) AND measures SSIM >= MIN_SSIM (0.97, luminance, Gaussian window) against the source resized to the same
width. Quality steps up from 60 to the lowest that meets the SSIM bar; a width that cannot meet both is not written (the next width down
serves instead), so the ladder never ships a file that is either heavy or visibly mushier than the source.
Non-hero photos stop at 1800w; the hero may go to 2400w. Each file has a sidecar <file>.json {q, ssim, bytes}; a cached
file is reused only when its sidecar shows it passed under the current rules.
"""
import os, re, json, hashlib
import numpy as np
from PIL import Image

MAX_BYTES = 400 * 1024
MIN_SSIM = 0.97
RULES = 'b400k-s0.97-v2'

ROLE_WIDTHS = {
    'hero': [1200, 1500, 1800, 2400],
    'large': [800, 1200, 1500, 1800],
    'medium': [600, 900, 1200],
    'small': [400, 600, 800],
    'portrait': [600, 900, 1152],
}


def budget_for(w):
    return MAX_BYTES


def ssim(a, b):
    """Mean SSIM of two same-size RGB PIL images on luminance (Gaussian sigma 1.5, the Wang et al. constants)."""
    from scipy.ndimage import gaussian_filter
    x = np.asarray(a.convert('L'), np.float64); y = np.asarray(b.convert('L'), np.float64)
    C1, C2 = (0.01 * 255) ** 2, (0.03 * 255) ** 2
    mx, my = gaussian_filter(x, 1.5), gaussian_filter(y, 1.5)
    sxx = gaussian_filter(x * x, 1.5) - mx * mx; syy = gaussian_filter(y * y, 1.5) - my * my; sxy = gaussian_filter(x * y, 1.5) - mx * my
    m = ((2 * mx * my + C1) * (2 * sxy + C2)) / ((mx * mx + my * my + C1) * (sxx + syy + C2))
    return float(m.mean())


QUALITIES = (60, 68, 74, 80, 85, 89, 92, 95)


def _encode(r, out):
    """Lowest WebP quality whose SSIM vs the resized source is >= MIN_SSIM, if that file fits MAX_BYTES; else None."""
    for q in QUALITIES:
        r.save(out, 'WEBP', quality=q, method=5)
        size = os.path.getsize(out)
        if size > MAX_BYTES:
            break   # higher qualities only get bigger
        sc = ssim(r, Image.open(out).convert('RGB'))
        if sc >= MIN_SSIM:
            return {'q': q, 'ssim': round(sc, 4), 'bytes': size, 'rules': RULES}
    if os.path.exists(out): os.remove(out)
    return None


def build_set(src_path, name, role, out_dir, extra_widths=()):
    im = Image.open(src_path)
    im = im.convert('RGB')
    sw, sh = im.size
    widths = sorted(set([w for w in ROLE_WIDTHS[role] + list(extra_widths) if w <= sw]))
    cap = ROLE_WIDTHS[role][-1]
    if not widths or widths[-1] < sw and sw - widths[-1] > 300 and sw <= cap:
        widths.append(sw)  # keep the native width as the top candidate when it is close (never past the role's cap)
    os.makedirs(out_dir, exist_ok=True)
    written, dropped = [], []
    for w in widths:
        h = round(sh * w / sw)
        out = os.path.join(out_dir, '%s-%d.webp' % (name, w))
        side = out + '.json'
        if os.path.exists(out) and os.path.exists(side) and os.path.getmtime(out) >= os.path.getmtime(src_path):
            meta = json.load(open(side))
            if meta.get('rules') == RULES and os.path.getsize(out) == meta.get('bytes'):
                written.append((w, h, meta['bytes']))
                continue
        r = im.resize((w, h), Image.LANCZOS) if w != sw else im
        meta = _encode(r, out)
        if meta is None:
            dropped.append(w)
            if os.path.exists(side): os.remove(side)
            continue
        json.dump(meta, open(side, 'w'))
        written.append((w, h, meta['bytes']))
    keep = {'%s-%d.webp' % (name, w) for w, _, _ in written}
    for f in os.listdir(out_dir):
        if re.match(re.escape(name) + r'-\d+\.webp(\.json)?$', f) and f.replace('.json', '') not in keep:
            os.remove(os.path.join(out_dir, f))
    if not written:
        raise SystemExit('images: %s: no width fits %d KB at SSIM >= %.2f' % (name, MAX_BYTES // 1024, MIN_SSIM))
    return {'name': name, 'source': src_path, 'native': [sw, sh], 'variants': written, 'role': role, 'dropped': dropped}


def srcset(name, variants):
    return ', '.join('img/%s-%d.webp %dw' % (name, w, w) for w, h, s in variants)


def pick_default(variants, target):
    """Default src: the smallest variant >= target, else the largest."""
    for w, h, s in variants:
        if w >= target:
            return w
    return variants[-1][0]


# --- 3A item 5: cover boxes. A landscape photo in a portrait cover box is drawn wider than its box, so the browser
# must be told the drawn width (sizes) or it fetches a rendition that renders soft; and a box that crops away more than
# MAX_CROP of the photo gets a less tall ratio instead (narrower crop, fewer bytes, more of the photo).
MAX_CROP = 1.25
_RATIOS = ('4 / 5', '1 / 1', '5 / 4', '4 / 3', '3 / 2')


def _r(s):
    a, b = [float(x) for x in str(s).split('/')]
    return a / b


def cover_factor(photo, ratio):
    """How much wider than its box a cover-fitted photo is drawn (1 when it fits or is taller than the box)."""
    return max(1.0, (photo['width'] / photo['height']) / _r(ratio))


def fit_ratio(photo, wanted):
    """The wanted box ratio, or the first less-tall ratio that keeps the cover crop within MAX_CROP."""
    if cover_factor(photo, wanted) <= MAX_CROP:
        return wanted
    for c in [x for x in _RATIOS if _r(x) > _r(wanted)]:
        if cover_factor(photo, c) <= MAX_CROP:
            return c
    return _RATIOS[-1]


def cover_sizes(sizes, photo, ratio):
    """Scale each slot length of a sizes attribute by the cover factor ('(min-width: 861px) 400px, 100vw' -> '... 805px, 201vw')."""
    f = cover_factor(photo, ratio)
    if f <= 1.0:
        return sizes
    def one(part):
        m = re.match(r'^(.*?)(\d+(?:\.\d+)?)(px|vw)\s*$', part)
        if not m: return part
        return '%s%d%s' % (m.group(1), round(float(m.group(2)) * f + 0.4999), m.group(3))
    return ', '.join(one(x.strip()) for x in sizes.split(','))
