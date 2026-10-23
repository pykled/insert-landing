"""3A item 6: Cinzel hairline share (qa.py stroke_probe maths, 2x) by weight and size, plus the 1x desktop sizes."""
import io, numpy as np
from PIL import Image, ImageFilter
from playwright.sync_api import sync_playwright
def share(png, scale):
    im = Image.open(io.BytesIO(png)).convert('L'); ink = im.point(lambda v: 255 if v < 160 else 0); I0 = np.asarray(ink).astype(bool).sum()
    k1 = int(2 * round(scale) + 1); op = np.asarray(ink.filter(ImageFilter.MinFilter(k1)).filter(ImageFilter.MaxFilter(k1))).astype(bool).sum()
    return round(1 - op / I0, 3)
with sync_playwright() as pw:
    for scale in (2,):
        p = pw.chromium.launch().new_context(viewport={'width': 1400, 'height': 300}, device_scale_factor=scale).new_page()
        p.set_content('<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400..900&display=block" rel="stylesheet"><div id=d style="font-family:Cinzel;white-space:nowrap;padding:20px;letter-spacing:.14em;background:#fff;color:#000;display:inline-block">Stonehurst garden estate Hamburgefonstiv 1907</div>')
        p.wait_for_timeout(1500)
        for w in (500, 600, 700, 800, 900):
            row = []
            for sz in (28, 32, 36, 44):
                p.evaluate("([w,s]) => { const d = document.getElementById('d'); d.style.fontWeight = w; d.style.fontSize = s + 'px'; }", [w, sz]); p.wait_for_timeout(80)
                row.append((sz, share(p.locator('#d').screenshot(), scale)))
            print(scale, w, row)
