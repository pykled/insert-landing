#!/usr/bin/env python3
"""Verify the /venues rehaul page (default: the private preview) at 1440 and 390, both at 2x.
  python3 scripts/verify-venues-rehaul.py [--base http://localhost:4822] [--path /private-previews/.../venues-rehaul/] [--shots DIR]
Checks: horizontal overflow, console/page errors, contrast under every text node (worst pixel, 7:1 small / 4.5 large),
display stroke probe at 1x and 2x (qa.py method), image sharpness (served px >= css px x DPR / 1.5) + alt text,
focus-visible, reduced-motion (no running animations, all reveals visible), anchors, form submit (intercepted).
The WALK_JS / contrast / stroke-probe code is copied from factory/qa.py."""
import io, sys, json, math, argparse, os
from playwright.sync_api import sync_playwright
from PIL import Image, ImageFilter
import numpy as np
ap = argparse.ArgumentParser()
ap.add_argument('--base', default='http://localhost:4822')
ap.add_argument('--path', default='/private-previews/2d32be7dda6d361dd89ffdfd/venues-rehaul/')
ap.add_argument('--shots', default=os.path.expanduser('~/projects/insert/docs/venues-rehaul-shots'))
a = ap.parse_args()
os.makedirs(a.shots, exist_ok=True)
problems, warnings, contrast_rows = [], [], []
WALK_JS = r"""
(rootSel) => {
  const root = rootSel ? document.querySelector(rootSel) : document.body;
  const out = []; const sx = window.scrollX, sy = window.scrollY;
  function parseColor(c) { const m = c.match(/rgba?\(([^)]+)\)/); if (!m) return null; const p = m[1].split(',').map(parseFloat); return [p[0], p[1], p[2], p.length > 3 ? p[3] : 1]; }
  function visible(el) {
    let op = 1;
    if (el.offsetWidth <= 1 && el.offsetHeight <= 1) return null;
    for (let e = el; e && e !== document.documentElement; e = e.parentElement) {
      const cs = getComputedStyle(e);
      if (cs.display === 'none' || cs.visibility === 'hidden' || e.hidden) return null;
      op *= parseFloat(cs.opacity); if (op === 0) return null;
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
  const tw = document.createTreeWalker(root, NodeFilter.SHOW_TEXT); let n;
  while ((n = tw.nextNode())) {
    const t = n.textContent.replace(/\s+/g, ' ').trim(); if (!t) continue;
    const el = n.parentElement; if (!el || ['SCRIPT', 'STYLE', 'NOSCRIPT', 'TEMPLATE'].includes(el.tagName)) continue;
    const det = el.closest('details'); if (det && !det.open && !el.closest('summary')) continue;
    const op = visible(el); if (op === null) continue;
    const cs = getComputedStyle(el); const col = parseColor(cs.color); if (!col) continue;
    const r = document.createRange(); r.selectNodeContents(n);
    const rects = [...r.getClientRects()].filter(b => b.width > 1 && b.height > 1).map(b => ({x: b.left + sx, y: b.top + sy, w: b.width, h: b.height}));
    if (!rects.length) continue;
    out.push({text: t.slice(0, 60), fg: col, op, rects, size: parseFloat(cs.fontSize), weight: parseInt(cs.fontWeight) || 400, el: label(el), family: cs.fontFamily.split(',')[0].replace(/"/g, ''), fvs: cs.fontVariationSettings});
  }
  root.querySelectorAll('input[placeholder]').forEach(inp => {
    const op = visible(inp); if (op === null) return; if (inp.value) return;
    const cs = getComputedStyle(inp, '::placeholder'); const col = parseColor(cs.color); if (!col) return;
    const b = inp.getBoundingClientRect(); const pad = parseFloat(getComputedStyle(inp).paddingLeft) || 12; const fs = parseFloat(cs.fontSize) || 16;
    const w = Math.min(b.width - pad * 2, inp.placeholder.length * fs * 0.55);
    out.push({text: '[placeholder] ' + inp.placeholder, fg: col, op, rects: [{x: b.left + sx + pad, y: b.top + sy + (b.height - fs) / 2, w, h: fs}], size: fs, weight: 400, el: label(inp), family: '', fvs: ''});
  });
  return out;
}
"""
PROBE_CSS = "*{color:transparent!important;-webkit-text-fill-color:transparent!important;text-shadow:none!important;caret-color:transparent!important;transition:none!important;animation:none!important} ::placeholder{color:transparent!important;-webkit-text-fill-color:transparent!important} input{color:transparent!important} input[type=range]{opacity:0!important}"


def contrast_arr(fg, px):
    px = px.astype(np.float64); a_ = fg[3]
    comp = np.array(fg[:3]) * a_ + px * (1 - a_)
    def lum(arr):
        c = arr / 255.0; c = np.where(c <= 0.03928, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
        return 0.2126 * c[:, 0] + 0.7152 * c[:, 1] + 0.0722 * c[:, 2]
    lf, lb = lum(comp), lum(px); hi, lo = np.maximum(lf, lb), np.minimum(lf, lb)
    cr = (hi + 0.05) / (lo + 0.05)
    return float(cr.min()), float(np.percentile(cr, 10))


def fullshot(page, path=None, clip=None):
    scale = page.evaluate('window.devicePixelRatio'); W = page.evaluate('document.documentElement.clientWidth'); H = page.evaluate('document.documentElement.scrollHeight')
    x0, y0, w, h = clip if clip else (0, 0, W, H); tile = int(7000 / scale)
    img = Image.new('RGB', (int(round(w * scale)), int(round(h * scale)))); y = 0
    while y < h:
        th = min(tile, h - y)
        png = page.screenshot(full_page=True, clip={'x': x0, 'y': y0 + y, 'width': w, 'height': th})
        img.paste(Image.open(io.BytesIO(png)).convert('RGB'), (0, int(round(y * scale)))); y += th
    if path: img.save(path)
    return img


def check_contrast(page, name, state, root=None, scale=2):
    nodes = page.evaluate(WALK_JS, root)
    if not nodes: return
    xs = [r['x'] for n in nodes for r in n['rects']]; ys = [r['y'] for n in nodes for r in n['rects']]
    xe = [r['x'] + r['w'] for n in nodes for r in n['rects']]; ye = [r['y'] + r['h'] for n in nodes for r in n['rects']]
    W = page.evaluate('document.documentElement.clientWidth'); H = page.evaluate('document.documentElement.scrollHeight')
    cx0, cy0 = max(0, math.floor(min(xs)) - 2), max(0, math.floor(min(ys)) - 2); cx1, cy1 = min(W, math.ceil(max(xe)) + 2), min(H, math.ceil(max(ye)) + 2)
    page.add_style_tag(content=PROBE_CSS); page.wait_for_timeout(150)
    bg = fullshot(page, clip=(cx0, cy0, cx1 - cx0, cy1 - cy0))
    page.evaluate("document.querySelectorAll('style').forEach(s => { if (s.textContent.startsWith('*{color:transparent')) s.remove(); })")
    arr = np.asarray(bg)
    for n in nodes:
        fg = (n['fg'][0], n['fg'][1], n['fg'][2], n['fg'][3] * n['op'])
        large = n['size'] >= 24 or (n['size'] >= 18.66 and n['weight'] >= 700); need = 3.0 if large else 4.5
        worst, p10 = 99.0, 99.0
        for r in n['rects']:
            x0 = int(round((r['x'] - cx0 + 1) * scale)); y0 = int(round((r['y'] - cy0 + 1) * scale)); x1 = int(round((r['x'] + r['w'] - cx0 - 1) * scale)); y1 = int(round((r['y'] + r['h'] - cy0 - 1) * scale))
            x0, y0 = max(0, x0), max(0, y0); x1, y1 = min(arr.shape[1], x1), min(arr.shape[0], y1)
            if x1 <= x0 or y1 <= y0: continue
            m, p = contrast_arr(fg, arr[y0:y1, x0:x1].reshape(-1, 3)); worst, p10 = min(worst, m), min(p10, p)
        contrast_rows.append({'view': name, 'state': state, 'el': n['el'], 'text': n['text'], 'size': n['size'], 'weight': n['weight'], 'min': round(worst, 2), 'p10': round(p10, 2), 'need': need})
        if worst < need:
            problems.append('%s [%s] contrast %.2f < %.1f (%spx/%d) %s "%s"' % (name, state, worst, need, n['size'], n['weight'], n['el'], n['text']))
        elif not large and worst < 7.0:
            warnings.append('%s [%s] contrast %.2f < 7 (%spx/%d) %s "%s"' % (name, state, worst, n['size'], n['weight'], n['el'], n['text']))


def stroke_probe(page, scale, sel='h1'):
    """Render the element's computed font black-on-white and estimate the mean stroke width in CSS px."""
    props = page.evaluate("""(sel) => { const els = [...document.querySelectorAll(sel)].filter(e => e.offsetWidth > 0); if (!els.length) return null;
      const e = els.sort((a, b) => parseFloat(getComputedStyle(b).fontSize) - parseFloat(getComputedStyle(a).fontSize))[0]; const cs = getComputedStyle(e);
      return {family: cs.fontFamily, weight: cs.fontWeight, size: parseFloat(cs.fontSize), style: cs.fontStyle, fvs: cs.fontVariationSettings, fos: cs.fontOpticalSizing, ls: cs.letterSpacing}; }""", sel)
    if not props: return None
    page.evaluate("""(p) => { const d = document.createElement('div'); d.id = '__probe'; d.textContent = 'Stonehurst garden estate Hamburgefonstiv 1907';
      Object.assign(d.style, {position: 'absolute', left: '0px', top: '0px', zIndex: 9999, background: '#fff', color: '#000', padding: '20px', whiteSpace: 'nowrap', fontFamily: p.family, fontWeight: p.weight, fontSize: p.size + 'px', fontStyle: p.style, fontVariationSettings: p.fvs, fontOpticalSizing: p.fos, letterSpacing: p.ls, lineHeight: '1.1', width: 'max-content'});
      document.body.appendChild(d); window.scrollTo(0, 0); }""", props)
    page.wait_for_timeout(150)
    box = page.evaluate("(() => { const r = document.getElementById('__probe').getBoundingClientRect(); return {x: r.left, y: r.top, w: Math.min(r.width, document.documentElement.clientWidth), h: r.height}; })()")
    png = page.screenshot(clip={'x': box['x'], 'y': box['y'], 'width': box['w'], 'height': box['h']})
    page.evaluate("document.getElementById('__probe').remove()")
    im = Image.open(io.BytesIO(png)).convert('L')
    ink = im.point(lambda v: 255 if v < 160 else 0)  # ink = white in this mask (160: counts anti-aliased hairlines)
    I0 = np.asarray(ink).astype(bool).sum()
    if I0 == 0: return None
    def opened(k):  # morphological opening removes every stroke thinner than k device px
        return np.asarray(ink.filter(ImageFilter.MinFilter(k)).filter(ImageFilter.MaxFilter(k))).astype(bool).sum()
    k1 = int(2 * round(scale) + 1)      # strokes <= 1 css px   (3 at 1x, 5 at 2x)
    k2 = int(2 * round(1.5 * scale) + 1)  # strokes <= 1.5 css px
    thin1 = 1 - opened(k1) / I0; thin15 = 1 - opened(k2) / I0
    return {'family': props['family'].split(',')[0], 'weight': props['weight'], 'size_css': props['size'], 'fvs': props['fvs'], 'ink_px': int(I0),
            'hairline_share_1px': round(thin1, 3), 'thin_share_1_5px': round(thin15, 3)}



def reveal_all(page):
    page.evaluate("document.querySelectorAll('.reveal').forEach(e=>e.classList.add('is-in'))")
    page.wait_for_timeout(1200)

def view(pw, name, w, h, scale, mobile, shots=True):
    b = pw.chromium.launch()
    ctx = b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=scale, is_mobile=mobile, has_touch=mobile)
    page = ctx.new_page(); errs = []
    page.on('console', lambda m: errs.append(m.text) if m.type == 'error' else None)
    page.on('pageerror', lambda e: errs.append(str(e)))
    sent = []
    page.route('**/api/contact', lambda r: (sent.append(r.request.post_data), r.fulfill(status=200, body='{"ok":true}', content_type='application/json')))
    page.route('**/api/track', lambda r: (sent.append('TRACK'), r.fulfill(status=200, body='{}')))
    page.route('**/calendly.com/**', lambda r: r.abort())
    page.route('**/assets.calendly.com/**', lambda r: r.abort())
    page.goto(a.base + a.path, wait_until='networkidle')
    page.evaluate('document.fonts.ready'); reveal_all(page)
    page.evaluate("document.querySelectorAll('img[loading=lazy]').forEach(i=>i.loading='eager')"); page.wait_for_load_state('networkidle'); page.wait_for_timeout(400)
    ow = page.evaluate('document.documentElement.scrollWidth - document.documentElement.clientWidth')
    if ow > 0: problems.append(f'{name}: horizontal overflow {ow}px')
    real_errs = [e for e in errs if 'calendly' not in e.lower() and 'ERR_FAILED' not in e]
    if real_errs: problems.append(f'{name}: console errors {real_errs[:3]}')
    if 'TRACK' in sent: problems.append(f'{name}: /api/track fired on preview')
    fonts = page.evaluate("[document.fonts.check('500 40px Newsreader'), document.fonts.check('400 18px \"Source Sans 3\"')]")
    if not all(fonts): problems.append(f'{name}: fonts not loaded {fonts}')
    # body text size floor (paragraphs, list items, labels inputs)
    small = page.evaluate("""[...document.querySelectorAll('main p, main li, main span, main label, footer p, footer a')].filter(e=>e.offsetWidth>0 && e.textContent.trim() && !e.closest('[aria-hidden=true]')).map(e=>[parseFloat(getComputedStyle(e).fontSize), e.tagName, e.className, e.textContent.trim().slice(0,30)]).filter(x=>x[0]<15)""")
    if small: problems.append(f'{name}: text under 15px {small[:4]}')
    # images
    imgs = page.evaluate("""[...document.images].map(i=>({src:i.currentSrc.split('/').pop(), nat:+(i.currentSrc.match(/-(\\d+)\\.webp/)||[0,0])[1], css:i.getBoundingClientRect().width, cssH:i.getBoundingClientRect().height, natH:+(i.currentSrc.match(/-(\\d+)\\.webp/)||[0,0])[1]*i.naturalHeight/i.naturalWidth, alt:i.getAttribute('alt'), hidden:!!i.closest('[aria-hidden=true]')}))""")
    for i in imgs:
        if i['alt'] is None or (not i['alt'] and not i['hidden']): problems.append(f"{name}: missing alt {i['src']}")
        cover = max(i['css'] / i['nat'], i['cssH'] / i['natH']) if i['nat'] else 9
        up = cover * scale
        i['upscale_at_dpr'] = round(up, 2)
        if up > 1.5: problems.append(f"{name}: {i['src']} upscaled {up:.2f}x at {scale}x DPR")
    # contrast
    check_contrast(page, name, 'default', None, scale)
    # stroke probe on h1 and h2
    probes = {s: stroke_probe(page, scale, s) for s in ('h1', 'h2', 'h3')}
    # anchors
    page.evaluate("document.documentElement.style.scrollBehavior='auto'")
    for anc in ('#stack', '#charter', '#book'):
        page.evaluate(f"document.querySelector('a[href=\"{anc}\"]').click()"); page.wait_for_timeout(900)
        top = page.evaluate(f"document.querySelector('{anc}').getBoundingClientRect().top")
        if abs(top) > 4: problems.append(f'{name}: anchor {anc} top={top:.0f}')
    # focus visible
    page.goto(a.base + a.path, wait_until='networkidle'); foc = []
    for _ in range(4):
        page.keyboard.press('Tab')
        foc.append(page.evaluate("(()=>{const e=document.activeElement; const c=getComputedStyle(e); return [e.tagName, e.textContent.trim().slice(0,20), c.outlineStyle, c.outlineWidth]})()"))
    page.focus('#email')
    foc.append(page.evaluate("(()=>{const e=document.activeElement; const c=getComputedStyle(e); return [e.tagName, e.id, c.boxShadow.slice(0,30), c.borderColor]})()"))
    if any(f[2] == 'none' for f in foc[:4]) or 'none' == foc[4][2]: problems.append(f'{name}: no visible focus {foc}')
    page.evaluate("document.querySelectorAll('.reveal').forEach(e=>e.classList.add('is-in'))")
    # form (intercepted)
    page.fill('#name', 'Test Person'); page.fill('#email', 'test@example.com'); page.fill('#business', 'Oak Hollow'); page.fill('#message', 'test')
    page.click('#contact-submit'); page.wait_for_timeout(800)
    st = page.text_content('#contact-status')
    posted = [s for s in sent if s and s != 'TRACK']
    form_ok = bool(posted) and 'Wedding venue (/venues) — Oak Hollow' in posted[0] and 'Thank you' in (st or '')
    if not form_ok: problems.append(f'{name}: form flow failed {posted[:1]} {st}')
    if shots:
        page.evaluate("document.querySelector('#book').scrollIntoView()"); page.wait_for_timeout(300)
    b.close()
    return {'imgs': imgs, 'probes': probes, 'focus': foc, 'form_ok': form_ok}

def shoot(pw, name, w, h, mobile):
    # final screenshot with the real Calendly embed loaded (checks above run with it blocked)
    b = pw.chromium.launch(); ctx = b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=2, is_mobile=mobile, has_touch=mobile)
    page = ctx.new_page(); page.route('**/api/**', lambda r: r.fulfill(status=200, body='{}'))
    page.goto(a.base + a.path, wait_until='networkidle'); page.evaluate('document.fonts.ready'); reveal_all(page)
    page.evaluate("document.querySelector('#book').scrollIntoView()"); page.wait_for_timeout(6000)
    page.evaluate('window.scrollTo(0,0)'); page.wait_for_timeout(500)
    H = page.evaluate('document.documentElement.scrollHeight')
    png = page.screenshot(full_page=True)
    open(os.path.join(a.shots, f'venues-rehaul-{name}.png'), 'wb').write(png)
    b.close(); return H

def reduced(pw):
    b = pw.chromium.launch(); ctx = b.new_context(viewport={'width': 1440, 'height': 900}, reduced_motion='reduce')
    page = ctx.new_page(); page.route('**/calendly.com/**', lambda r: r.abort()); page.route('**/api/**', lambda r: r.fulfill(status=200, body='{}'))
    page.goto(a.base + a.path, wait_until='networkidle'); page.wait_for_timeout(500)
    page.evaluate('window.scrollTo(0, document.body.scrollHeight)'); page.wait_for_timeout(500)
    r = page.evaluate("({anims: document.getAnimations().filter(x=>x.playState==='running').length, hidden: [...document.querySelectorAll('.reveal')].filter(e=>parseFloat(getComputedStyle(e).opacity)<1).length, trans: getComputedStyle(document.querySelector('.reveal')).transitionDuration})")
    if r['anims'] or r['hidden']: problems.append(f'reduced-motion: {r}')
    b.close(); return r

def motion_on(pw):
    b = pw.chromium.launch(); page = b.new_page(viewport={'width': 1440, 'height': 900})
    page.route('**/calendly.com/**', lambda r: r.abort()); page.route('**/api/**', lambda r: r.fulfill(status=200, body='{}'))
    page.goto(a.base + a.path, wait_until='networkidle')
    d = page.evaluate("getComputedStyle(document.querySelector('#stack .reveal')).transitionDuration")
    b.close(); return d

with sync_playwright() as pw:
    out = {'desktop': view(pw, 'desktop-1440', 1440, 900, 2, False), 'mobile': view(pw, 'mobile-390', 390, 844, 2, True)}
    # stroke probe at 1x for comparison
    b = pw.chromium.launch(); page = b.new_page(viewport={'width': 1440, 'height': 900}, device_scale_factor=1)
    page.goto(a.base + a.path, wait_until='networkidle'); page.evaluate('document.fonts.ready'); page.wait_for_timeout(300)
    out['probe_1x'] = {s: stroke_probe(page, 1, s) for s in ('h1', 'h2', 'h3')}; b.close()
    out['reduced'] = reduced(pw); out['motion_duration'] = motion_on(pw)
    out['shot_heights'] = [shoot(pw, 'desktop-1440', 1440, 900, False), shoot(pw, 'mobile-390', 390, 844, True)]

# hairline limits from pairings.json notes: share of ink in strokes <= 1 css px: 1x <= 0.20, 2x <= 0.25
for k, lim, src in (('probe_1x', 0.20, out['probe_1x']), ('probe_2x', 0.25, out['desktop']['probes'])):
    for s, p in src.items():
        if p and p['hairline_share_1px'] > lim: problems.append(f"{k} {s} hairline share {p['hairline_share_1px']} > {lim}")
small = [r for r in contrast_rows if not (r['size'] >= 24 or (r['size'] >= 18.66 and r['weight'] >= 700))]
large = [r for r in contrast_rows if r not in small]
for r in small:
    if r['min'] < 7: problems.append(f"small text under 7:1: {r['view']} {r['min']} {r['el']} '{r['text']}'")
summary = {
    'text_nodes': len(contrast_rows),
    'small_min': min(r['min'] for r in small), 'small_min_el': min(small, key=lambda r: r['min'])['el'] + ' / ' + min(small, key=lambda r: r['min'])['text'],
    'large_min': min(r['min'] for r in large) if large else None,
    'probe_1x': {s: p and p['hairline_share_1px'] for s, p in out['probe_1x'].items()},
    'probe_2x': {s: p and p['hairline_share_1px'] for s, p in out['desktop']['probes'].items()},
    'h1_font': out['desktop']['probes']['h1'] and (out['desktop']['probes']['h1']['family'], out['desktop']['probes']['h1']['weight'], out['desktop']['probes']['h1']['size_css'], out['desktop']['probes']['h1']['fvs']),
    'images': [(i['src'], i['upscale_at_dpr']) for v in ('desktop', 'mobile') for i in out[v]['imgs']],
    'focus': out['desktop']['focus'], 'form_ok': [out['desktop']['form_ok'], out['mobile']['form_ok']],
    'reduced': out['reduced'], 'motion_duration': out['motion_duration'],
}
json.dump({'summary': summary, 'problems': problems, 'warnings': warnings[:40], 'contrast': contrast_rows}, open('/tmp/rehaul/verify-report.json', 'w'), indent=1)
print(json.dumps(summary, indent=1)[:2500])
print('PROBLEMS', len(problems)); [print(' -', p[:200]) for p in problems[:25]]
sys.exit(1 if problems else 0)
