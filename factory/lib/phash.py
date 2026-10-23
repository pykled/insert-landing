"""Perceptual hashes of rendered pages (spec 05 section 6.2 item 4). Pillow + numpy only.

Two 256-bit hashes per site, both a 16 x 16 DCT pHash of a greyscale image:
  fold   the 1440 x 900 first screen, downscaled to 64 x 64
  strip  the full 1440-wide page downscaled to 64 x 256 (w x h): encodes section order and photo/paper alternation

pHash: greyscale -> resize -> 2-D DCT-II -> keep the 16 x 16 lowest frequencies -> bit = coefficient > median
(the DC term is excluded from the median so a flat page does not set every bit). Distance = Hamming bits of 256.
Thresholds (starting point; re-tune after ten registered sites): <= 12 REFUSE, <= 18 WARN.

CLI
  python3 lib/phash.py <image.png> [<image2.png>]            print hashes (and the Hamming distance)
  python3 lib/phash.py capture <url> [--out shot.png]        screenshot a page at 1440 (Playwright) and print both hashes
"""
import io, sys
import numpy as np
from PIL import Image

BITS = 256
REFUSE, WARN = 12, 18


def _dct_matrix(n):
    k = np.arange(n)[:, None]
    i = np.arange(n)[None, :]
    m = np.cos(np.pi * (2 * i + 1) * k / (2.0 * n)) * np.sqrt(2.0 / n)
    m[0, :] = np.sqrt(1.0 / n)
    return m


def dct2(a):
    """Orthonormal 2-D DCT-II of a (h, w) array."""
    h, w = a.shape
    # einsum, not @: numpy 2.0 + macOS Accelerate emits spurious divide-by-zero warnings from float64 matmul
    return np.einsum('ij,jk,lk->il', _dct_matrix(h), a, _dct_matrix(w))


def phash_array(grey, keep=16):
    """grey: 2-D float array. Returns a hex string of keep*keep bits."""
    d = dct2(np.asarray(grey, dtype=np.float64))[:keep, :keep]
    flat = d.flatten()
    med = np.median(flat[1:])
    bits = (flat > med).astype(np.uint8)
    bits[0] = 0
    return ''.join('%x' % int(''.join(str(b) for b in bits[i:i + 4]), 2) for i in range(0, len(bits), 4))


def phash_image(img, size=(64, 64)):
    """img: PIL image. size: (w, h) of the downscale before the DCT."""
    g = img.convert('L').resize(size, Image.LANCZOS)
    return phash_array(np.asarray(g, dtype=np.float64))


def fold_hash(img):
    """First screen: crop to 1440 x 900 CSS px worth of the image (any DPR), then 64 x 64."""
    w, h = img.size
    scale = w / 1440.0
    return phash_image(img.crop((0, 0, w, min(h, int(round(900 * scale))))), (64, 64))


def strip_hash(img):
    """Whole page as a 64 x 256 rhythm strip."""
    return phash_image(img, (64, 256))


def hamming(a, b):
    if not a or not b or len(a) != len(b):
        return None
    return bin(int(a, 16) ^ int(b, 16)).count('1')


def compare(hashes, registry, exclude_id=None):
    """hashes: {'fold': hex, 'strip': hex}. Returns (status, rows) with rows sorted by the smaller distance.
    A site without stored hashes is skipped (reported as 'no phash')."""
    rows = []
    for s in registry.get('sites', []):
        if s['id'] == exclude_id:
            continue
        ph = s.get('phash') or {}
        if not ph.get('fold'):
            rows.append({'id': s['id'], 'fold': None, 'strip': None, 'status': 'no phash'})
            continue
        f, st = hamming(hashes.get('fold'), ph.get('fold')), hamming(hashes.get('strip'), ph.get('strip'))
        m = min(x for x in (f, st) if x is not None)
        status = 'refuse' if m <= REFUSE else ('warn' if m <= WARN else 'ok')
        if (s.get('exposure') or 'demo') != 'demo':   # 3A item 7: internal proofs are listed, never counted
            status = 'internal'
        rows.append({'id': s['id'], 'fold': f, 'strip': st, 'min': m, 'status': status})
    rows.sort(key=lambda r: r.get('min', 999))
    worst = 'ok'
    for r in rows:
        if r['status'] == 'refuse':
            worst = 'refuse'
        elif r['status'] == 'warn' and worst == 'ok':
            worst = 'warn'
    return worst, rows


def capture(url, out=None):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        ctx = pw.chromium.launch().new_context(viewport={'width': 1440, 'height': 900}, device_scale_factor=1)
        page = ctx.new_page()
        page.goto(url, wait_until='load')
        page.wait_for_function('document.fonts.ready.then(()=>true)')
        page.evaluate("document.querySelectorAll('.reveal').forEach(e=>e.classList.add('visible'))")
        page.add_style_tag(content='*,*::before,*::after{transition:none!important;animation:none!important}')
        page.evaluate("document.querySelectorAll('img[loading=lazy]').forEach(i=>i.loading='eager')")
        page.evaluate('window.scrollTo(0, document.body.scrollHeight)'); page.wait_for_timeout(800)
        page.evaluate('window.scrollTo(0, 0)'); page.wait_for_timeout(300)
        fold = Image.open(io.BytesIO(page.screenshot())).convert('RGB')
        full = Image.open(io.BytesIO(page.screenshot(full_page=True))).convert('RGB')
        ctx.close()
    if out:
        full.save(out)
    return {'fold': fold_hash(fold), 'strip': strip_hash(full)}


if __name__ == '__main__':
    if len(sys.argv) >= 3 and sys.argv[1] == 'capture':
        out = sys.argv[sys.argv.index('--out') + 1] if '--out' in sys.argv else None
        print(capture(sys.argv[2], out))
    elif len(sys.argv) >= 2:
        hs = []
        for p in sys.argv[1:3]:
            im = Image.open(p)
            hs.append({'fold': fold_hash(im), 'strip': strip_hash(im)})
            print(p, hs[-1])
        if len(hs) == 2:
            print('hamming fold %s strip %s' % (hamming(hs[0]['fold'], hs[1]['fold']), hamming(hs[0]['strip'], hs[1]['strip'])))
    else:
        print(__doc__)
