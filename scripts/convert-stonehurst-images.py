#!/usr/bin/env python3
"""Convert the raw Gemini output in /tmp/stonehurst-raw to WebP srcset widths for
previews/stonehurst/img. Never upscales: a width larger than the source is skipped.
Quality steps down (to a floor of 50) until each file is under the byte cap; a width that
still cannot meet the cap at q50 is dropped so the page never ships an oversize asset.

Widths: hero 1200/1800/2400 (full-bleed); every other image 800/1200/1800 (cards render
at most ~820 CSS px wide, so 1800 covers 2x displays without waste).

Usage: python3 scripts/convert-stonehurst-images.py [raw_dir] [out_dir]
"""
import os
import sys
from PIL import Image

RAW = sys.argv[1] if len(sys.argv) > 1 else '/tmp/stonehurst-raw'
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(__file__), '..', 'previews', 'stonehurst', 'img')
WIDTHS = {'hero': (1200, 1800, 2400)}
DEFAULT_WIDTHS = (800, 1200, 1800)
CAP = 250 * 1024
Q_FLOOR = 50

os.makedirs(OUT, exist_ok=True)
for stale in os.listdir(OUT):
    if stale.endswith('.webp'):
        os.remove(os.path.join(OUT, stale))

rows = []
for name in sorted(os.listdir(RAW)):
    if not name.lower().endswith(('.jpg', '.jpeg', '.png')):
        continue
    key = os.path.splitext(name)[0]
    src = Image.open(os.path.join(RAW, name)).convert('RGB')
    sw, sh = src.size
    for w in WIDTHS.get(key, DEFAULT_WIDTHS):
        if w > sw:
            rows.append((key, w, 'skipped (source %dpx, no upscale)' % sw))
            continue
        h = round(sh * w / sw)
        im = src if w == sw else src.resize((w, h), Image.LANCZOS)
        out = os.path.join(OUT, '%s-%d.webp' % (key, w))
        q = 82
        while True:
            im.save(out, 'WEBP', quality=q, method=6)
            size = os.path.getsize(out)
            if size <= CAP:
                rows.append((key, w, '%d KB q%d %dx%d' % (size // 1024, q, w, h)))
                break
            if q <= Q_FLOOR:
                os.remove(out)
                rows.append((key, w, 'dropped (%d KB at q%d)' % (size // 1024, q)))
                break
            q -= 6

for r in rows:
    print('%-14s %5d  %s' % r)
