#!/usr/bin/env python3
"""Crop + convert The Stonehurst's own photos (downloaded from static.wixstatic.com
originals) into WebP variants for previews/stonehurst/index.html.

Never upscales: a variant is only written when its width <= the crop's native width.
Source originals: /tmp/sh/orig/<wix-id> (fetched 2026-10-16 from
https://static.wixstatic.com/media/<wix-id>, the untransformed original).
Keeps a <=2400px JPEG copy of each chosen crop source in previews/stonehurst/img/real/.
"""
import os, sys, json
from PIL import Image
Image.MAX_IMAGE_PIXELS = None

ROOT = os.path.join(os.path.dirname(__file__), '..', 'previews', 'stonehurst', 'img')
REAL = os.path.join(ROOT, 'real')
ORIG = os.environ.get('ORIG', '/tmp/sh/orig')
os.makedirs(REAL, exist_ok=True)

# name, wix id, source page, crop aspect (w/h) or None, focal (fx, fy), widths
PICKS = [
    ('hero',       '41b656_c53749f9cc334a58bca20dc46128b8ca~mv2.jpg', 'copy-of-bamboo-garden', None,   (0.5, 0.5),  [1200, 1800, 2400]),
    ('greenhouse', '41b656_faf7efa119644297a7e9df7107b7a1e9~mv2.jpg', 'greenhouse-los-angeles', 4/3,  (0.5, 0.5),  [800, 1200, 1800]),
    ('barn',       '41b656_93561ad4073f4c769a70ce03e4aa63c5~mv2.jpg', 'home',                  4/3,   (0.5, 0.55), [800, 1200, 1800]),
    ('flower',     '41b656_1fbdb1ce5c8d4febab7d0a4987605e06~mv2.jpg', 'copy-of-bamboo-garden', 4/3,   (0.5, 0.56), [800, 1200, 1800]),
    ('bamboo',     '41b656_dda286a194e34c70addb74f1575a8432~mv2.png', 'the-gardens-gallery',   4/3,   (0.5, 0.5),  [800, 1200, 1800]),
    ('terrace',    '41b656_13d8c023d33b4bdba5aa9ff0d7a4d612~mv2.jpg', 'grand-terrace-gallery', 4/3,   (0.5, 0.5),  [800, 1200, 1600]),
    ('bungalow',   '41b656_3c0747cbc41349d580c09bae9a3b173a~mv2.jpg', 'home',                  4/3,   (0.5, 0.5),  [800, 1200, 1800]),
    ('reception',  '41b656_3d58f3b1103849e888d99cc30eae9cfa~mv2.jpg', 'greenhouse-los-angeles', 4/3,  (0.5, 0.55), [800, 1200, 1800]),
    ('stonepath',  '41b656_fad86b73f0eb42b5a660be4a9f5604eb~mv2.jpeg', 'our-history',          3/4,   (0.5, 0.5),  [600, 900, 1152]),
]

def crop_to(im, aspect, focal):
    w, h = im.size
    if aspect is None:
        return im
    if w / h > aspect:   # too wide: trim width
        cw, ch = int(round(h * aspect)), h
    else:                # too tall: trim height
        cw, ch = w, int(round(w / aspect))
    fx, fy = focal
    x0 = min(max(int(round(fx * w - cw / 2)), 0), w - cw)
    y0 = min(max(int(round(fy * h - ch / 2)), 0), h - ch)
    return im.crop((x0, y0, x0 + cw, y0 + ch))

manifest = []
for name, wid, page, aspect, focal, widths in PICKS:
    src = os.path.join(ORIG, wid)
    im = Image.open(src)
    nat_w, nat_h = im.size
    im = im.convert('RGB')
    c = crop_to(im, aspect, focal)
    cw, ch = c.size
    written = []
    for tw in widths:
        if tw > cw:
            print(f'  skip {name}-{tw}: crop is only {cw}px wide (no upscaling)')
            continue
        th = int(round(ch * tw / cw))
        out = c.resize((tw, th), Image.LANCZOS)
        path = os.path.join(ROOT, f'{name}-{tw}.webp')
        q = 82
        out.save(path, 'WEBP', quality=q, method=6)
        while os.path.getsize(path) > 300_000 and q > 60:
            q -= 6
            out.save(path, 'WEBP', quality=q, method=6)
        written.append((tw, th, os.path.getsize(path), q))
        print(f'  {name}-{tw}.webp {tw}x{th} {os.path.getsize(path)//1024}KB q{q}')
    # <=2400px source copy of the crop for the record
    keep = c.copy()
    keep.thumbnail((2400, 2400), Image.LANCZOS)
    kp = os.path.join(REAL, f'{name}.jpg')
    keep.save(kp, 'JPEG', quality=90, optimize=True)
    manifest.append({'name': name, 'wix_id': wid, 'source_url': f'https://static.wixstatic.com/media/{wid}',
                     'source_page': f'https://www.thestonehurst.com/{"" if page == "home" else page}',
                     'native': [nat_w, nat_h], 'crop': [cw, ch], 'variants': written,
                     'kept_copy': f'img/real/{name}.jpg', 'kept_copy_size': list(keep.size)})

json.dump(manifest, open(os.path.join(REAL, 'manifest.json'), 'w'), indent=1)
print(json.dumps(manifest, indent=1))
