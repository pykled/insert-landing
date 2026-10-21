"""Responsive WebP sets from the venue's source photos. Never upscales.

A width is written only when it is <= the source's pixel width. Output names are <name>-<w>.webp so the
QA gate can read the served width from the filename and compare it with the rendered size. Quality steps
down from 82 until the file is under the budget for its width (hero 2400px gets 560 KB, everything else
~320 KB), matching the pipeline used for the Stonehurst mock.
"""
import os, json, hashlib
from PIL import Image

ROLE_WIDTHS = {
    'hero': [1200, 1800, 2400],
    'large': [800, 1200, 1800],
    'medium': [600, 900, 1200],
    'small': [400, 600, 800],
    'portrait': [600, 900, 1152],
}


def budget_for(w):
    return 560_000 if w >= 2400 else (400_000 if w >= 1800 else 320_000)


def build_set(src_path, name, role, out_dir, extra_widths=()):
    im = Image.open(src_path)
    im = im.convert('RGB')
    sw, sh = im.size
    widths = sorted(set([w for w in ROLE_WIDTHS[role] + list(extra_widths) if w <= sw]))
    if not widths or widths[-1] < sw and sw - widths[-1] > 300 and sw <= 2400:
        widths.append(sw)  # keep the native width as the top candidate when it is close
    os.makedirs(out_dir, exist_ok=True)
    written = []
    for w in widths:
        h = round(sh * w / sw)
        out = os.path.join(out_dir, '%s-%d.webp' % (name, w))
        if os.path.exists(out) and os.path.getmtime(out) >= os.path.getmtime(src_path):
            written.append((w, h, os.path.getsize(out)))
            continue
        r = im.resize((w, h), Image.LANCZOS) if w != sw else im
        q = 82
        while True:
            r.save(out, 'WEBP', quality=q, method=6)
            if os.path.getsize(out) <= budget_for(w) or q <= 54:
                break
            q -= 6
        written.append((w, h, os.path.getsize(out)))
    return {'name': name, 'source': src_path, 'native': [sw, sh], 'variants': written, 'role': role}


def srcset(name, variants):
    return ', '.join('img/%s-%d.webp %dw' % (name, w, w) for w, h, s in variants)


def pick_default(variants, target):
    """Default src: the smallest variant >= target, else the largest."""
    for w, h, s in variants:
        if w >= target:
            return w
    return variants[-1][0]
