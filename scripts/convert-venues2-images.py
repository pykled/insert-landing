#!/usr/bin/env python3
"""Write the venues2-* WebPs for the /venues rehaul. Downscale only (never upscale), q stepped down to stay <= ~250 KB.
Sources: assets/venues-banner-2400.webp (native 2K Gemini render, 2400x1018) and assets/venues-hero.webp (1600x893).
Re-run with --src-hero <png> after regenerating with scripts/generate-venues2-images.mjs."""
import sys, os
from PIL import Image
A = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets')
def save(im, name, w, cap=250):
    if w > im.width: print('skip', name, w, '> native', im.width); return
    r = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS) if w < im.width else im
    for q in (86, 82, 78, 74, 70, 66):
        p = os.path.join(A, f'{name}-{w}.webp'); r.save(p, 'WEBP', quality=q, method=6)
        if os.path.getsize(p) <= cap * 1024: break
    print(f'{name}-{w}.webp', r.size, os.path.getsize(p) // 1024, 'KB q', q)
src_hero = sys.argv[sys.argv.index('--src-hero') + 1] if '--src-hero' in sys.argv else os.path.join(A, 'venues-banner-2400.webp')
hero = Image.open(src_hero).convert('RGB')
for w in (1200, 1800, 2400): save(hero, 'venues2-hero', w)
# mobile art direction: 4:3 crop around the candle and the arrangement
H = hero.height; cw = round(H * 4 / 3); x0 = round(hero.width * 0.235)
crop = hero.crop((x0, 0, x0 + cw, H))
for w in (800, 1200): save(crop, 'venues2-hero-m', w)
ev = Image.open(os.path.join(A, 'venues-hero.webp')).convert('RGB')
for w in (800, 1200, 1600): save(ev, 'venues2-evening', w)
