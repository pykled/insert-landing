#!/usr/bin/env python3
"""Full-resolution Playwright verification for previews/stonehurst/index.html.

Expects a static server on http://localhost:4821 serving ~/projects/insert.
Writes screenshots to previews/stonehurst/shots and prints a check report.

Checks per viewport (1440x900 @2x, 390x844 @2x):
  - no horizontal overflow, no console errors / page errors / failed requests
  - web fonts loaded; every <img> has alt, loads, and the chosen srcset candidate is
    sharp (>= rendered width x DPR, capped at 1.5x on desktop) and never upscaled
    beyond the native source width recorded in img/real/manifest.json
  - CONTRAST: walks every visible text node (plus input placeholders), resolves the
    effective foreground colour (with ancestor opacity), captures the page with all
    text made transparent so the real background (scrims, photos, gradients,
    translucent layers) can be sampled per glyph line, and reports the MINIMUM
    contrast ratio across every background pixel under the text. Fails when below
    WCAG AA (4.5:1 small, 3:1 large). Also lists small text under 7:1 as warnings.
    Runs in the default state, each confirmation state, hover states, and the open
    mobile menu.
  - the three fake submit flows (date check, tour booking, pricing guide)
"""
import os, re, io, json, sys, math
from playwright.sync_api import sync_playwright
from PIL import Image
import numpy as np

BASE = os.environ.get('BASE', 'http://localhost:4821/previews/stonehurst/index.html')
HERE = os.path.dirname(os.path.abspath(__file__))
PREV = os.path.join(HERE, '..', 'previews', 'stonehurst')
OUT = os.environ.get('OUT', os.path.join(PREV, 'shots'))
os.makedirs(OUT, exist_ok=True)
MANIFEST = {m['name']: m for m in json.load(open(os.path.join(PREV, 'img', 'real', 'manifest.json')))}

REVEAL = """document.querySelectorAll('.reveal').forEach(e=>e.classList.add('visible'));
document.querySelectorAll('.hero-copy > *, .hero .card, .hero-media img').forEach(e=>{e.style.animation='none'});
document.querySelector('.hero-media img').style.transform='none';"""

WALK_JS = r"""
(rootSel) => {
  const root = rootSel ? document.querySelector(rootSel) : document.body;
  const out = [];
  const sx = window.scrollX, sy = window.scrollY;
  function parseColor(c) { const m = c.match(/rgba?\(([^)]+)\)/); if (!m) return null; const p = m[1].split(',').map(parseFloat); return [p[0], p[1], p[2], p.length > 3 ? p[3] : 1]; }
  function visible(el) {
    let op = 1;
    if (el.offsetWidth <= 1 && el.offsetHeight <= 1) return null; // .sr-only
    for (let e = el; e && e !== document.documentElement; e = e.parentElement) {
      const cs = getComputedStyle(e);
      if (cs.display === 'none' || cs.visibility === 'hidden' || e.hidden) return null;
      op *= parseFloat(cs.opacity);
      if (op === 0) return null;
    }
    return op;
  }
  function label(el) {
    const parts = [];
    for (let e = el, n = 0; e && e !== document.body && n < 4; e = e.parentElement, n++) {
      let s = e.tagName.toLowerCase();
      if (e.id) s += '#' + e.id; else if (e.classList.length) s += '.' + [...e.classList].filter(c => c !== 'visible' && c !== 'reveal').slice(0, 2).join('.');
      parts.unshift(s);
    }
    return parts.join('>');
  }
  const tw = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
  let n;
  while ((n = tw.nextNode())) {
    const t = n.textContent.replace(/\s+/g, ' ').trim();
    if (!t) continue;
    const el = n.parentElement;
    if (!el || ['SCRIPT', 'STYLE', 'NOSCRIPT', 'TEMPLATE'].includes(el.tagName)) continue;
    // bodies of closed <details> are not rendered (Chromium reports stale rects for them)
    const det = el.closest('details');
    if (det && !det.open && !el.closest('summary')) continue;
    const op = visible(el);
    if (op === null) continue;
    const cs = getComputedStyle(el);
    const col = parseColor(cs.color); if (!col) continue;
    const r = document.createRange(); r.selectNodeContents(n);
    const rects = [...r.getClientRects()].filter(b => b.width > 1 && b.height > 1).map(b => ({x: b.left + sx, y: b.top + sy, w: b.width, h: b.height}));
    if (!rects.length) continue;
    out.push({text: t.slice(0, 60), fg: col, op, rects, size: parseFloat(cs.fontSize), weight: parseInt(cs.fontWeight) || 400, el: label(el)});
  }
  // placeholders
  root.querySelectorAll('input[placeholder]').forEach(inp => {
    const op = visible(inp); if (op === null) return;
    if (inp.value) return;
    const cs = getComputedStyle(inp, '::placeholder');
    const col = parseColor(cs.color); if (!col) return;
    const b = inp.getBoundingClientRect();
    const pad = parseFloat(getComputedStyle(inp).paddingLeft) || 12;
    const fs = parseFloat(cs.fontSize) || 16;
    const w = Math.min(b.width - pad * 2, inp.placeholder.length * fs * 0.55);
    out.push({text: '[placeholder] ' + inp.placeholder, fg: col, op, rects: [{x: b.left + sx + pad, y: b.top + sy + (b.height - fs) / 2, w, h: fs}], size: fs, weight: 400, el: label(inp)});
  });
  return out;
}
"""

PROBE_CSS = "*{color:transparent!important;-webkit-text-fill-color:transparent!important;text-shadow:none!important;caret-color:transparent!important;transition:none!important;animation:none!important} ::placeholder{color:transparent!important;-webkit-text-fill-color:transparent!important} input{color:transparent!important}"

problems, warnings = [], []
contrast_rows = []

def contrast_arr(fg, px):
    """min + p10 contrast between fg (r,g,b,a) and an (N,3) array of background pixels."""
    px = px.astype(np.float64)
    a = fg[3]
    comp = np.array(fg[:3]) * a + px * (1 - a)  # fg composited over bg
    def lum(arr):
        c = arr / 255.0
        c = np.where(c <= 0.03928, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
        return 0.2126 * c[:, 0] + 0.7152 * c[:, 1] + 0.0722 * c[:, 2]
    lf, lb = lum(comp), lum(px)
    hi, lo = np.maximum(lf, lb), np.minimum(lf, lb)
    cr = (hi + 0.05) / (lo + 0.05)
    return float(cr.min()), float(np.percentile(cr, 10))

def fullshot(page, path=None, clip=None):
    """Full-page screenshot, tiled so very tall pages stay under Chromium's texture limit. Returns PIL image."""
    scale = page.evaluate('window.devicePixelRatio')
    W = page.evaluate('document.documentElement.clientWidth')
    H = page.evaluate('document.documentElement.scrollHeight')
    x0, y0, w, h = clip if clip else (0, 0, W, H)
    tile = int(7000 / scale)
    img = Image.new('RGB', (int(round(w * scale)), int(round(h * scale))))
    y = 0
    while y < h:
        th = min(tile, h - y)
        png = page.screenshot(full_page=True, clip={'x': x0, 'y': y0 + y, 'width': w, 'height': th})
        im = Image.open(io.BytesIO(png)).convert('RGB')
        img.paste(im, (0, int(round(y * scale))))
        y += th
    if path:
        img.save(path)
    return img

def check_contrast(page, name, state, root=None, scale=2):
    nodes = page.evaluate(WALK_JS, root)
    if not nodes:
        return
    xs = [r['x'] for n in nodes for r in n['rects']]; ys = [r['y'] for n in nodes for r in n['rects']]
    xe = [r['x'] + r['w'] for n in nodes for r in n['rects']]; ye = [r['y'] + r['h'] for n in nodes for r in n['rects']]
    W = page.evaluate('document.documentElement.clientWidth'); H = page.evaluate('document.documentElement.scrollHeight')
    cx0, cy0 = max(0, math.floor(min(xs)) - 2), max(0, math.floor(min(ys)) - 2)
    cx1, cy1 = min(W, math.ceil(max(xe)) + 2), min(H, math.ceil(max(ye)) + 2)
    page.add_style_tag(content=PROBE_CSS)
    page.wait_for_timeout(200)
    bg = fullshot(page, clip=(cx0, cy0, cx1 - cx0, cy1 - cy0))
    page.evaluate("document.querySelectorAll('style').forEach(s => { if (s.textContent.startsWith('*{color:transparent')) s.remove(); })")
    arr = np.asarray(bg)
    for n in nodes:
        fg = (n['fg'][0], n['fg'][1], n['fg'][2], n['fg'][3] * n['op'])
        large = n['size'] >= 24 or (n['size'] >= 18.66 and n['weight'] >= 700)
        need = 3.0 if large else 4.5
        worst, p10 = 99.0, 99.0
        for r in n['rects']:
            x0 = int(round((r['x'] - cx0 + 1) * scale)); y0 = int(round((r['y'] - cy0 + 1) * scale))
            x1 = int(round((r['x'] + r['w'] - cx0 - 1) * scale)); y1 = int(round((r['y'] + r['h'] - cy0 - 1) * scale))
            x0, y0 = max(0, x0), max(0, y0); x1, y1 = min(arr.shape[1], x1), min(arr.shape[0], y1)
            if x1 <= x0 or y1 <= y0:
                continue
            px = arr[y0:y1, x0:x1].reshape(-1, 3)
            m, p = contrast_arr(fg, px)
            worst, p10 = min(worst, m), min(p10, p)
        row = {'view': name, 'state': state, 'el': n['el'], 'text': n['text'], 'size': n['size'], 'weight': n['weight'], 'min': round(worst, 2), 'p10': round(p10, 2), 'need': need}
        contrast_rows.append(row)
        if worst < need:
            problems.append('%s [%s] contrast %.2f < %.1f (%spx/%d, fg %s op %.2f) %s "%s"' % (name, state, worst, need, n['size'], n['weight'], n['fg'], n['op'], n['el'], n['text']))
        elif not large and worst < 7.0:
            warnings.append('%s [%s] contrast %.2f < 7 (%spx/%d) %s "%s"' % (name, state, worst, n['size'], n['weight'], n['el'], n['text']))

def run(pw, name, width, height, scale, mobile):
    ctx = pw.chromium.launch().new_context(viewport={'width': width, 'height': height}, device_scale_factor=scale, is_mobile=mobile, has_touch=mobile)
    page = ctx.new_page()
    errors = []
    page.on('console', lambda m: errors.append('%s: %s' % (m.type, m.text)) if m.type in ('error', 'warning') else None)
    page.on('pageerror', lambda e: errors.append('pageerror: %s' % e))
    page.on('requestfailed', lambda r: errors.append('requestfailed: %s' % r.url))
    page.goto(BASE, wait_until='load')
    page.wait_for_function('document.fonts.ready.then(()=>true)')
    page.wait_for_timeout(600)
    fonts = page.evaluate("[document.fonts.check('16px \"Bodoni Moda\"'), document.fonts.check('16px Jost')]")
    if not all(fonts):
        problems.append('%s: web fonts not loaded %s' % (name, fonts))
    page.evaluate(REVEAL)
    # freeze motion so every hover / reveal / confirm state is measured at its final values
    page.add_style_tag(content="*,*::before,*::after{transition:none!important;animation:none!important}")
    page.wait_for_timeout(300)
    sw = page.evaluate('document.documentElement.scrollWidth'); iw = page.evaluate('window.innerWidth')
    if sw > iw:
        problems.append('%s: horizontal overflow scrollWidth=%d innerWidth=%d' % (name, sw, iw))
        wide = page.evaluate("""() => [...document.querySelectorAll('body *')].filter(e => e.getBoundingClientRect().right > window.innerWidth + 1).slice(0, 8).map(e => e.tagName + '.' + e.className + ' right=' + Math.round(e.getBoundingClientRect().right))""")
        problems.append('  offenders: %s' % wide)
    page.evaluate("document.querySelectorAll('img[loading=lazy]').forEach(i=>i.loading='eager')")
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)"); page.wait_for_timeout(800)
    page.evaluate("window.scrollTo(0, 0)"); page.wait_for_timeout(400)
    page.wait_for_function("[...document.images].every(i => i.complete)")
    # --- images ---
    imgs = page.evaluate("""() => [...document.images].map(i => ({alt: (i.alt||''), cur: i.currentSrc.split('/').pop(), cw: Math.round(i.getBoundingClientRect().width), ch: Math.round(i.getBoundingClientRect().height), nw: i.naturalWidth}))""")
    factor = scale if mobile else min(scale, 1.5)
    for i in imgs:
        if not i['alt'].strip():
            problems.append('%s: image without alt: %s' % (name, i['cur']))
        if i['nw'] == 0:
            problems.append('%s: image failed to load: %s' % (name, i['cur'])); continue
        m = re.match(r'(.+)-(\d+)\.webp$', i['cur'])
        base, src_w = (m.group(1), int(m.group(2))) if m else (None, i['nw'])
        if src_w < i['cw'] * factor * 0.9:
            problems.append('%s: image soft: %s source=%dpx needed=%dpx (css %dpx x %.1f)' % (name, i['cur'], src_w, i['cw'] * factor, i['cw'], factor))
        man = MANIFEST.get(base)
        if man:
            native_w = man['crop'][0]
            if src_w > native_w:
                problems.append('%s: image upscaled beyond source: %s %d > native %d' % (name, i['cur'], src_w, native_w))
            if i['cw'] * factor > native_w + 1:
                problems.append('%s: image displayed larger than native allows: %s css %dpx x %.1f = %d > native %d' % (name, i['cur'], i['cw'], factor, i['cw'] * factor, native_w))
        else:
            problems.append('%s: image not in manifest: %s' % (name, i['cur']))
    # --- screenshots ---
    page.evaluate("document.querySelector('header').style.position='absolute'")
    fullshot(page, os.path.join(OUT, '%s.png' % name))
    hero_h = page.evaluate("document.querySelector('.hero').getBoundingClientRect().height")
    fullshot(page, os.path.join(OUT, '%s-hero.png' % name), clip=(0, 0, width, max(200, hero_h)))
    for sel, lab in (('#spaces', 'spaces'), ('#tour', 'tour')):
        box = page.evaluate("s => { const r = document.querySelector(s).getBoundingClientRect(); return {y: r.top + window.scrollY, h: r.height}; }", sel)
        fullshot(page, os.path.join(OUT, '%s-%s.png' % (name, lab)), clip=(0, box['y'], width, min(box['h'], 4000)))
    # --- contrast: default state ---
    check_contrast(page, name, 'default', None, scale)
    # --- hover states (forced via CDP so the state survives full-page capture on mobile emulation) ---
    cdp = ctx.new_cdp_session(page); cdp.send('DOM.enable'); cdp.send('CSS.enable')
    for sel in ['.nav .btn-solid', '.btn-clay', '.btn-light', '.faq-aside .btn', '.link', '.nav-links a', '.cal button:not(:disabled)', '.slot-list button', '.guide-form .btn', '.foot-grid a']:
        if page.locator(sel).count() == 0 or not page.locator(sel).first.is_visible():
            continue
        page.evaluate("s => { document.querySelector(s).setAttribute('data-probe', '1'); }", sel)
        root_id = cdp.send('DOM.getDocument', {'depth': 0})['root']['nodeId']
        nid = cdp.send('DOM.querySelector', {'nodeId': root_id, 'selector': '[data-probe]'})['nodeId']
        cdp.send('CSS.forcePseudoState', {'nodeId': nid, 'forcedPseudoClasses': ['hover']}); page.wait_for_timeout(100)
        check_contrast(page, name, 'hover ' + sel, '[data-probe]', scale)
        cdp.send('CSS.forcePseudoState', {'nodeId': nid, 'forcedPseudoClasses': []})
        page.evaluate("document.querySelectorAll('[data-probe]').forEach(e => e.removeAttribute('data-probe'))")
    # --- mobile menu ---
    if page.locator('.nav-toggle').is_visible():
        page.click('.nav-toggle'); page.wait_for_timeout(200)
        check_contrast(page, name, 'menu open', 'header', scale)
        page.click('.nav-toggle')
    # --- date form ---
    page.click('#date-form button[type=submit]')
    if page.evaluate("document.getElementById('date-error').hidden"):
        problems.append('%s: date form did not show a validation error on empty submit' % name)
    check_contrast(page, name, 'date error', '#check', scale)
    page.fill('#f-date', '2027-05-15'); page.fill('#f-guests', '140'); page.fill('#f-contact', 'sam@example.com')
    page.click('#date-form button[type=submit]'); page.wait_for_timeout(300)
    if not page.is_visible('#date-confirm'):
        problems.append('%s: date confirmation not shown' % name)
    txt = page.inner_text('#date-confirm')
    for want in ('Saturday, May 15', '140', 'sam@example.com', 'Held for 24 hours'):
        if want not in txt:
            problems.append('%s: date confirmation missing "%s"' % (name, want))
    check_contrast(page, name, 'date confirm', '#check', scale)
    fullshot(page, os.path.join(OUT, '%s-date-confirm.png' % name), clip=(0, 0, width, max(200, page.evaluate("document.querySelector('.hero').getBoundingClientRect().height"))))
    page.click('#date-again'); page.wait_for_timeout(200)
    if not page.is_visible('#date-form'):
        problems.append('%s: date form did not reset' % name)
    # --- tour ---
    page.click('#cal-next'); page.wait_for_timeout(100)
    page.locator('#cal button:not([disabled])').first.click()
    page.locator('#slots button').first.click()
    if page.is_disabled('#book'):
        problems.append('%s: book button still disabled after picking day + slot' % name)
    check_contrast(page, name, 'tour picked', '#scheduler', scale)
    page.click('#book'); page.wait_for_timeout(300)
    if not page.is_visible('#tour-confirm') or 'on the calendar' not in page.inner_text('#tour-confirm'):
        problems.append('%s: tour confirmation not shown' % name)
    check_contrast(page, name, 'tour confirm', '#scheduler', scale)
    box = page.evaluate("() => { const r = document.querySelector('#tour').getBoundingClientRect(); return {y: r.top + window.scrollY, h: r.height}; }")
    fullshot(page, os.path.join(OUT, '%s-tour-confirm.png' % name), clip=(0, box['y'], width, min(box['h'], 4000)))
    page.click('#tour-again'); page.wait_for_timeout(200)
    if not page.is_visible('#cal'):
        problems.append('%s: tour scheduler did not reset' % name)
    # --- guide ---
    page.fill('#g-email', 'nope'); page.click('#guide-form button[type=submit]')
    if page.evaluate("document.getElementById('guide-error').hidden"):
        problems.append('%s: guide form accepted an invalid email' % name)
    check_contrast(page, name, 'guide error', '#guide-wrap', scale)
    page.fill('#g-email', 'sam@example.com'); page.click('#guide-form button[type=submit]'); page.wait_for_timeout(300)
    if not page.is_visible('#guide-confirm') or 'sam@example.com' not in page.inner_text('#guide-confirm'):
        problems.append('%s: guide confirmation not shown' % name)
    check_contrast(page, name, 'guide confirm', '#guide-wrap', scale)
    # --- network / errors ---
    reqs = page.evaluate("performance.getEntriesByType('resource').map(r => r.name).filter(u => !u.startsWith(location.origin))")
    ext = [u for u in reqs if 'fonts.g' not in u]
    if ext:
        problems.append('%s: unexpected external requests: %s' % (name, ext[:5]))
    for e in errors:
        problems.append('%s: console %s' % (name, e))
    ctx.close()

with sync_playwright() as pw:
    run(pw, 'desktop', 1440, 900, 2, False)
    run(pw, 'mobile', 390, 844, 2, True)

json.dump(contrast_rows, open(os.path.join(OUT, 'contrast.json'), 'w'), indent=0)
small = [r for r in contrast_rows if not (r['size'] >= 24 or (r['size'] >= 18.66 and r['weight'] >= 700))]
print('text nodes measured: %d (small %d). Lowest small-text ratio: %.2f, lowest overall: %.2f' % (
    len(contrast_rows), len(small), min(r['min'] for r in small), min(r['min'] for r in contrast_rows)))
print('\nWARNINGS (small text under 7:1): %d' % len(warnings))
for w in warnings: print('  ' + w)
print('\nPROBLEMS: %d' % len(problems))
for p in problems: print('  ' + p)
sys.exit(1 if problems else 0)
