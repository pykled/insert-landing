#!/usr/bin/env python3
"""QA gate for any factory-built (or hand-built) venue homepage.

  qa.py <dir> [--base http://localhost:4821] [--registry data/registry.json] [--strict]

<dir> is a built site folder containing index.html, img/manifest.json and (for factory builds) build-meta.json.
The URL is derived from the folder's position under ~/projects/insert unless --url is given.

Checks, per viewport (1440x900 @2x desktop, 390x844 @2x mobile):
  1. no horizontal overflow; no console errors / page errors / failed requests; only Google Fonts off-origin
  2. web fonts actually loaded (display + body from build-meta, or detected from the stylesheet)
  3. images: alt present (empty alt only inside aria-hidden), loaded, cover-aware sharpness
     (served px >= rendered px x DPR, capped 1.5x on desktop), never above the native crop width
  4. CONTRAST under every text node and placeholder, measured against a screenshot of the page with
     all text transparent, so photos / gradients / tints are sampled per pixel. Worst pixel must meet
     WCAG AA (4.5 small / 3 large); small text under 7:1 is a warning. Measured in every state we can
     reach: default, hover (CDP forced), open menu, form errors, three confirmations, moment states.
  5. DISPLAY LEGIBILITY: rule check (display face at >= its min size and pinned weight; opsz pinned when
     the family has an opsz axis) + a stroke probe: the h1's computed font is rendered black on white,
     binarised, eroded once; mean stroke width ~ 2 x ink / vanished-edge-ink. Fails under 1.6 CSS px.
  6. Lighthouse-style basics: title, description, lang, viewport, one h1, heading order, landmarks,
     hero fetchpriority, lazy below the fold, HTML < 120 KB, JSON-LD parses, focus-visible + reduced
     motion rules present, tap targets >= 24 px on mobile, LCP element reported.
  7. interactive flows: date check (error + success + reset), tour (open panel if needed, pick, book,
     reset), guide (invalid + valid), and the site's signature moment.
  8. diversity: fingerprint guard against every registered site (schema 2: same-dialect rule + quota); FAIL on
     'refuse'. Screenshot pHash of the 1440 fold and the full-page rhythm strip (lib/phash.py) against every
     registered site's stored hashes: Hamming <= 18/256 WARN, <= 12 FAIL.
  9. spec 05 section 5 exclusions E1-E19 (lib/exclusions.py) on a DOM snapshot of the desktop page. Dialect builds:
     FAIL; pre-dialect builds and hand-built mocks: WARN (they predate the spec).
 10. motion: under prefers-reduced-motion every .reveal is visible and nothing animates (no running animations, no
     auto-advancing [data-autoplay]); with motion on, the reveal transition is 600-1200 ms.
 12. focus: every Tab stop shows a focus indicator (lib/focus.py; >= 3:1 change over a 2 css px ring)
 11. template fallbacks recorded in build-meta.json (a dialect asked for a template stage 2B has not built yet):
     WARN, FAIL with --strict.
Writes shots + qa-report.json into <dir>/qa/. Exit 1 on any problem.
  qa.py --self-test   run the exclusion fixtures (factory/tests/test_exclusions.py) without a browser
"""
import os, re, io, json, sys, math, argparse
if '--self-test' in sys.argv:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from tests import test_exclusions as _T
    sys.exit(_T.main())
from playwright.sync_api import sync_playwright
from PIL import Image, ImageFilter
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from lib import fingerprint as FP, exclusions as EX, phash as PH, overflow as OV, claims as CL, focus as FO

ap = argparse.ArgumentParser()
ap.add_argument('dir')
ap.add_argument('--base', default='http://localhost:4821')
ap.add_argument('--url')
ap.add_argument('--registry', default=os.path.join(HERE, 'data', 'registry.json'))
ap.add_argument('--no-shots', action='store_true')
ap.add_argument('--strict', action='store_true', help='template fallbacks are problems, not warnings')
ap.add_argument('--content', help='content JSON (default: build-meta content_path, else content/<slug>.json)')
a = ap.parse_args()

DIR = os.path.abspath(a.dir)
ROOT = os.path.dirname(HERE)   # F12: the checkout this qa.py lives in, not a hard-coded path
URL = a.url or (a.base + '/' + os.path.relpath(DIR, ROOT) + '/index.html')
OUT = os.path.join(DIR, 'qa'); os.makedirs(OUT, exist_ok=True)
MAN = {m['name']: m for m in json.load(open(os.path.join(DIR, 'img', 'manifest.json')))} if os.path.exists(os.path.join(DIR, 'img', 'manifest.json')) else {}
META = json.load(open(os.path.join(DIR, 'build-meta.json'))) if os.path.exists(os.path.join(DIR, 'build-meta.json')) else None

DIALECT = ((META or {}).get('dialect') or {}).get('id') if isinstance((META or {}).get('dialect'), dict) else None
DIALECT_MODE = DIALECT not in (None, 'none')
_cpath = a.content or ((META or {}).get('content_path') and os.path.join(ROOT, META['content_path'])) or (META and os.path.join(HERE, 'content', META['id'].split('-')[0] + '.json'))
CONTENT = json.load(open(_cpath)) if _cpath and os.path.exists(_cpath) else {}
HTML = open(os.path.join(DIR, 'index.html')).read() if os.path.exists(os.path.join(DIR, 'index.html')) else ''
problems, warnings, info = [], [], {}
contrast_rows = []

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


MOMENT_ROOTED = ('slideshow-counter', 'numbers-count', 'candle-count', 'then-now', 'pairs-counter', 'hours-dial', 'crest-reveal', 'sprig-draw')


def run(pw, name, width, height, scale, mobile):
    ctx = pw.chromium.launch().new_context(viewport={'width': width, 'height': height}, device_scale_factor=scale, is_mobile=mobile, has_touch=mobile)
    page = ctx.new_page(); errors = []; transferred = []
    page.on('console', lambda m: errors.append('%s: %s' % (m.type, m.text)) if m.type in ('error', 'warning') else None)
    page.on('pageerror', lambda e: errors.append('pageerror: %s' % e))
    page.on('requestfailed', lambda r: errors.append('requestfailed: %s' % r.url))
    page.on('response', lambda r: transferred.append((r.url, r.headers.get('content-length'))))
    resp = page.goto(URL, wait_until='load')
    if not resp or not resp.ok:
        sys.exit('qa: %s returned %s; is the http.server running from %s? (or pass --url)' % (URL, resp and resp.status, ROOT))
    page.wait_for_function('document.fonts.ready.then(()=>true)'); page.wait_for_timeout(500)
    # --- fonts ---
    fams = []
    if META: fams = [META['pairing']['display']['family'], META['pairing']['body']['family']]
    else:
        css = page.evaluate("[...document.querySelectorAll('link[href*=\"fonts.googleapis\"]')].map(l => l.href).join(' ')")
        fams = [f.replace('+', ' ') for f in re.findall(r'family=([^:&]+)', css)]
    weights = [META['pairing']['display']['weight'], META['pairing']['body']['weight']] if META else [400, 400]
    for f, w in zip(fams, weights):
        # fonts.check() is true when no face matches, so test the weight the page actually uses
        if not page.evaluate('document.fonts.check(\'%d 16px "%s"\')' % (w, f)):
            problems.append('%s: web font not loaded: %s %d' % (name, f, w))
    info.setdefault('fonts', fams)
    # --- basics (desktop only) ---
    if not mobile:
        b = page.evaluate("""() => ({title: document.title, desc: (document.querySelector('meta[name=description]')||{}).content || '', lang: document.documentElement.lang,
          viewport: (document.querySelector('meta[name=viewport]')||{}).content || '', h1: document.querySelectorAll('h1').length,
          headings: [...document.querySelectorAll('h1,h2,h3,h4')].filter(h => h.offsetWidth > 0).map(h => +h.tagName[1]), landmarks: ['header','main','footer'].map(t => !!document.querySelector(t)),
          heroPrio: !!document.querySelector('img[fetchpriority=high]'), lazyCount: document.querySelectorAll('img[loading=lazy]').length, imgCount: document.images.length,
          ld: [...document.querySelectorAll('script[type="application/ld+json"]')].map(s => s.textContent), css: [...document.styleSheets].map(s => { try { return [...s.cssRules].map(r => r.cssText).join(' ') } catch (e) { return '' } }).join(' '),
          htmlBytes: new Blob([document.documentElement.outerHTML]).size, robots: (document.querySelector('meta[name=robots]')||{}).content || ''})""")
        if not b['title']: problems.append('no <title>')
        _var = str((META or {}).get('id') or '').rsplit('-', 1)[-1]   # build id = <slug>-<variant>
        if re.search(r'concept|proof|preview', b['title'], re.I) or (len(_var) > 1 and re.search(r'\b%s\b' % re.escape(_var), b['title'], re.I)):
            problems.append('<title> carries a concept/proof/variant label: %r (the page chip says it; the title is the venue\'s)' % b['title'])
        if not b['desc']: problems.append('no meta description')
        if b['lang'] != 'en': problems.append('html lang missing')
        if 'width=device-width' not in b['viewport']: problems.append('viewport meta missing')
        if b['h1'] != 1: problems.append('expected exactly one h1, found %d' % b['h1'])
        prev = 1
        for lv in b['headings']:
            if lv > prev + 1: problems.append('heading level skip: h%d after h%d' % (lv, prev)); break
            prev = lv
        if not all(b['landmarks']): problems.append('missing landmark(s) header/main/footer: %s' % b['landmarks'])
        if not b['heroPrio']: problems.append('no fetchpriority=high on the hero image')
        if b['lazyCount'] < b['imgCount'] - 4: warnings.append('only %d of %d images are loading=lazy' % (b['lazyCount'], b['imgCount']))
        if b['htmlBytes'] > 120_000: problems.append('HTML is %d KB (> 120 KB)' % (b['htmlBytes'] // 1024))
        try:
            ld = [json.loads(x) for x in b['ld']]; types = [g.get('@type') for d in ld for g in d.get('@graph', [d])]
            info['jsonld_types'] = types
            if not any('EventVenue' in (t if isinstance(t, list) else [t]) for t in types): problems.append('JSON-LD has no EventVenue')
        except Exception as e:
            problems.append('JSON-LD does not parse: %s' % e)
        if ':focus-visible' not in b['css']: problems.append('no :focus-visible rule')
        if 'prefers-reduced-motion' not in b['css']: problems.append('no prefers-reduced-motion rule')
        if 'noindex' not in b['robots']: warnings.append('no noindex meta (fine for a public site, required for previews)')
        info['html_kb'] = b['htmlBytes'] // 1024
        lcp = page.evaluate("""() => new Promise(res => { const po = new PerformanceObserver(l => { const e = l.getEntries().pop(); res(e ? {t: Math.round(e.startTime), el: e.element ? e.element.tagName + '.' + e.element.className : ''} : null); po.disconnect(); }); po.observe({type: 'largest-contentful-paint', buffered: true}); setTimeout(() => res(null), 800); })""")
        info['lcp'] = lcp
        tot = sum(int(c) for u, c in transferred if c and c.isdigit())
        info['transferred_kb_at_load'] = tot // 1024
        if tot > 1_500_000: warnings.append('%d KB transferred at load (desktop)' % (tot // 1024))
    # --- display legibility: rule check + stroke probe ---
    if META and META['pairing']['display']['family'] != META['pairing']['body']['family']:
        disp = META['pairing']['display']
        rows = page.evaluate("""() => [...document.querySelectorAll('h1,h2,h3,.display')].filter(e => e.offsetWidth > 0).map(e => { const cs = getComputedStyle(e); return {tag: e.tagName, family: cs.fontFamily.split(',')[0].replace(/"/g, ''), size: parseFloat(cs.fontSize), weight: parseInt(cs.fontWeight), fvs: cs.fontVariationSettings, fos: cs.fontOpticalSizing}; })""")
        seen = set()
        for r in rows:
            if r['family'] != disp['family']: continue
            key = (r['tag'], round(r['size']))
            if key in seen: continue
            seen.add(key)
            if r['size'] < disp['min_px'] - 0.5:
                problems.append('%s: %s uses %s at %.0fpx, below the pairing minimum %dpx' % (name, r['tag'], disp['family'], r['size'], disp['min_px']))
            if r['weight'] < disp['weight']:
                problems.append('%s: %s %s weight %d < pinned %d' % (name, r['tag'], disp['family'], r['weight'], disp['weight']))
            if disp.get('has_opsz') and ('opsz' not in (r['fvs'] or '') or r['fos'] != 'none'):
                problems.append('%s: %s %s optical size not pinned (fvs=%s, font-optical-sizing=%s)' % (name, r['tag'], disp['family'], r['fvs'], r['fos']))
    sp = stroke_probe(page, scale, 'h1')
    if sp:
        info.setdefault('stroke', {})[name] = sp
        # calibrated 2026-10-20 (qa-calibration.md): Bodoni Moda auto-opsz 400 @72px = 0.37 hairline share, pinned opsz18/500 = 0.19,
        # Cormorant 300 = 0.42; sturdy faces (Fraunces 500, Instrument Sans 500, Jost 400) <= 0.10. Floor: 0.25.
        if sp['hairline_share_1px'] > 0.25:
            problems.append('%s: h1 hairlines: %.0f%% of the letterform is <= 1 css px thick (%s %s %s @ %.0fpx)' % (name, sp['hairline_share_1px'] * 100, sp['family'], sp['weight'], sp['fvs'], sp['size_css']))
        elif sp['hairline_share_1px'] > 0.18:
            warnings.append('%s: h1 hairline share %.0f%% (%s %s %s)' % (name, sp['hairline_share_1px'] * 100, sp['family'], sp['weight'], sp['fvs']))
    # --- motion freeze + reveal; header stays in flow but stops sticking (sticky headers get painted into every tile) ---
    page.evaluate("document.querySelectorAll('.reveal').forEach(e=>e.classList.add('visible')); document.querySelector('header').style.position='relative'")
    page.add_style_tag(content="*,*::before,*::after{transition:none!important;animation:none!important}")
    page.wait_for_timeout(200)
    sw = page.evaluate('document.documentElement.scrollWidth'); iw = page.evaluate('window.innerWidth')
    for o in OV.element_overflow(page):   # 3A: per element, incl. text wider than its own box and clipped spill-over
        problems.append('%s: horizontal overflow, %s' % (name, o))
    if sw > iw:
        problems.append('%s: horizontal overflow scrollWidth=%d innerWidth=%d' % (name, sw, iw))
        problems.append('  offenders: %s' % page.evaluate("""() => [...document.querySelectorAll('body *')].filter(e => e.getBoundingClientRect().right > window.innerWidth + 1).slice(0, 8).map(e => e.tagName + '.' + e.className + ' right=' + Math.round(e.getBoundingClientRect().right))"""))
    # --- focus visibility (3A F5): Tab through every control, focused vs blurred pixels must change >= 3:1 over a 2 px ring ---
    fp, frows = FO.check(page, name, scale)
    problems.extend(fp); info.setdefault('focus', {})[name] = {'controls': len(frows), 'min_margin': min((r['changed'] / max(1, r['need']) for r in frows), default=0)}
    page.evaluate("document.querySelectorAll('img[loading=lazy]').forEach(i=>i.loading='eager')")
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)"); page.wait_for_timeout(800)
    page.evaluate("window.scrollTo(0, 0)"); page.wait_for_timeout(300)
    page.wait_for_function("[...document.images].every(i => i.complete)")
    page.evaluate("Promise.all([...document.images].map(i => i.decode().catch(()=>0)))")
    # --- images (cover-aware) ---
    imgs = page.evaluate("""() => [...document.images].map(i => { const r = i.getBoundingClientRect(); const hid = !!i.closest('[aria-hidden=true]'); return {alt: i.getAttribute('alt'), cur: i.currentSrc.split('/').pop(), cw: r.width, ch: r.height, nw: i.naturalWidth, fit: getComputedStyle(i).objectFit, deco: hid, hidden: r.width === 0 || getComputedStyle(i).opacity === '0'}; })""")
    factor = scale if mobile else min(scale, 1.5)
    counted = 0
    for i in imgs:
        if i['alt'] is None or (i['alt'].strip() == '' and not i['deco']):
            problems.append('%s: image without alt: %s' % (name, i['cur']))
        if i['nw'] == 0:
            problems.append('%s: image failed to load: %s' % (name, i['cur'])); continue
        if i['hidden'] or i['cw'] < 2: continue
        counted += 1
        m = re.match(r'(.+)-(\d+)\.webp$', i['cur']); base, src_w = (m.group(1), int(m.group(2))) if m else (None, i['nw'])
        man = MAN.get(base)
        if man:
            w0, h0 = man.get('kept_copy_size') or man['crop']
            s = max(i['cw'] / w0, i['ch'] / h0) if i['fit'] == 'cover' else i['cw'] / w0
            disp_w = w0 * s
        else:
            disp_w = i['cw']
        need = disp_w * factor
        if src_w < need * 0.9:
            problems.append('%s: image soft: %s served %dpx, needs %dpx (box %dx%d css, cover-scaled %dpx x %.1f)' % (name, i['cur'], src_w, need, i['cw'], i['ch'], disp_w, factor))
        if man:
            native_w = man['crop'][0]
            if src_w > native_w: problems.append('%s: image upscaled beyond source: %s %d > native %d' % (name, i['cur'], src_w, native_w))
            if need > native_w * 1.02: problems.append('%s: image displayed larger than native allows: %s needs %d > native %d' % (name, i['cur'], need, native_w))
        elif MAN:
            problems.append('%s: image not in manifest: %s' % (name, i['cur']))
    info.setdefault('images_checked', {})[name] = counted
    # --- spec exclusions E1-E19 on a DOM snapshot (desktop; mobile adds the first-screen fact check) ---
    page.evaluate("window.scrollTo({top: 0, behavior: 'instant'})"); page.wait_for_timeout(100)
    snap = page.evaluate(EX.COLLECT_JS)   # all positions in document coordinates, so the scroll offset does not matter
    if not mobile:
        ex_p, ex_w, ex_sum = EX.run_all(snap, META, CONTENT, HTML, dialect_mode=DIALECT_MODE)
        info['exclusions'] = {'mode': 'dialect' if DIALECT_MODE else 'pre-dialect (warnings only)', 'failures_by_rule': ex_sum, 'sections': snap.get('sections'), 'first_screen_text': snap.get('first_screen_text', '')[:400], 'content': _cpath}
        problems.extend('%s: %s' % (name, x) for x in ex_p); warnings.extend('%s: %s' % (name, x) for x in ex_w)
    else:
        p19, w19 = EX.e19_first_screen_facts(snap, CONTENT)
        (problems if DIALECT_MODE else warnings).extend('%s: %s' % (name, x) for x in p19)
    # --- contrast: default ---
    check_contrast(page, name, 'default', None, scale)
    # --- hover states ---
    cdp = ctx.new_cdp_session(page); cdp.send('DOM.enable'); cdp.send('CSS.enable')
    for sel in ['.nav .btn', '.btn-accent', '.btn-solid', '.btn-ghost', '.btn-light', '.link', '.nav-links a', '.cal button:not(:disabled)', '.slot-list button', 'summary', '.light-ctl button', '.foot-grid a', '.stack-row', '.index-row']:
        if page.locator(sel).count() == 0 or not page.locator(sel).first.is_visible(): continue
        page.evaluate("s => { document.querySelector(s).setAttribute('data-probe', '1'); }", sel)
        root_id = cdp.send('DOM.getDocument', {'depth': 0})['root']['nodeId']
        nid = cdp.send('DOM.querySelector', {'nodeId': root_id, 'selector': '[data-probe]'})['nodeId']
        cdp.send('CSS.forcePseudoState', {'nodeId': nid, 'forcedPseudoClasses': ['hover']}); page.wait_for_timeout(80)
        check_contrast(page, name, 'hover ' + sel, '[data-probe]', scale)
        cdp.send('CSS.forcePseudoState', {'nodeId': nid, 'forcedPseudoClasses': []})
        page.evaluate("document.querySelectorAll('[data-probe]').forEach(e => e.removeAttribute('data-probe'))")
    # --- mobile menu ---
    if page.locator('.nav-toggle').is_visible():
        page.click('.nav-toggle'); page.wait_for_timeout(150)
        check_contrast(page, name, 'menu open', 'header', scale)
        page.click('.nav-toggle')
    # --- tap targets (mobile) ---
    if mobile:
        small = page.evaluate("""() => [...document.querySelectorAll('a,button,input,summary')].filter(e => { const r = e.getBoundingClientRect(); const cs = getComputedStyle(e); return r.width > 0 && cs.visibility !== 'hidden' && (r.width < 24 || r.height < 24); }).map(e => e.tagName + '.' + e.className + ' ' + Math.round(e.getBoundingClientRect().width) + 'x' + Math.round(e.getBoundingClientRect().height)).slice(0, 10)""")
        if small: problems.append('%s: tap targets under 24px: %s' % (name, small))
    # --- date form ---
    page.click('#date-form button[type=submit]')
    if page.evaluate("document.getElementById('date-error').hidden"): problems.append('%s: date form did not show a validation error on empty submit' % name)
    check_contrast(page, name, 'date error', '#check', scale)
    page.fill('#f-date', '2027-05-15'); page.fill('#f-guests', '140'); page.fill('#f-contact', 'sam@example.com')
    page.click('#date-form button[type=submit]'); page.wait_for_timeout(250)
    if not page.is_visible('#date-confirm'): problems.append('%s: date confirmation not shown' % name)
    txt = page.inner_text('#date-confirm') if page.is_visible('#date-confirm') else ''
    for want in ('Saturday, May 15', '140', 'sam@example.com', 'Preview only'):   # 3A: a labelled preview, never a promised hold
        if want not in txt: problems.append('%s: date confirmation missing "%s"' % (name, want))
    check_contrast(page, name, 'date confirm', '#check', scale)
    page.click('#date-again'); page.wait_for_timeout(150)
    if not page.is_visible('#date-form'): problems.append('%s: date form did not reset' % name)
    # --- tour ---
    has_tour = bool(page.locator('#scheduler').count())
    if not has_tour:
        info.setdefault('skipped', []).append('%s: tour flow (no #scheduler on this page)' % name)
    if has_tour and page.locator('#tour-open').count():
        page.click('#tour-open'); page.wait_for_timeout(150)
        if not page.is_visible('#scheduler'): problems.append('%s: tour panel did not open' % name)
    if has_tour: page.click('#cal-next'); page.wait_for_timeout(80)
    if has_tour:
        page.locator('#cal button:not([disabled])').first.click(); page.locator('#slots button').first.click()
        if page.is_disabled('#book'): problems.append('%s: book button still disabled after picking day + slot' % name)
        check_contrast(page, name, 'tour picked', '#scheduler', scale)
        page.click('#book'); page.wait_for_timeout(250)
        if not page.is_visible('#tour-confirm') or 'Preview only' not in page.inner_text('#tour-confirm'): problems.append('%s: tour confirmation not shown' % name)
        check_contrast(page, name, 'tour confirm', '#scheduler', scale)
        page.click('#tour-again'); page.wait_for_timeout(150)
        if not page.is_visible('#cal'): problems.append('%s: tour scheduler did not reset' % name)
    # --- guide (some dialect rhythms have no guide block: skipped and recorded, never a crash) ---
    has_guide = bool(page.locator('#guide-form').count())
    if not has_guide:
        info.setdefault('skipped', []).append('%s: guide flow (no #guide-form on this page)' % name)
    if has_guide:
        page.fill('#g-email', 'nope'); page.click('#guide-form button[type=submit]')
        if page.evaluate("document.getElementById('guide-error').hidden"): problems.append('%s: guide form accepted an invalid email' % name)
        check_contrast(page, name, 'guide error', '#guide-wrap', scale)
        page.fill('#g-email', 'sam@example.com'); page.click('#guide-form button[type=submit]'); page.wait_for_timeout(250)
        if not page.is_visible('#guide-confirm') or 'sam@example.com' not in page.inner_text('#guide-confirm'): problems.append('%s: guide confirmation not shown' % name)
        check_contrast(page, name, 'guide confirm', '#guide-wrap', scale)
    # --- signature moment ---
    moment = page.evaluate("document.body.getAttribute('data-moment')")
    if moment and moment != 'none' and moment in MOMENT_ROOTED and not page.locator('[data-moment-root]').count():
        # --force moment= skips needs; a moment whose data is missing renders no section. Flag it, skip its hook step.
        (problems if DIALECT_MODE else warnings).append('%s: moment %s chosen but rendered nothing (no [data-moment-root]; needs not met?)' % (name, moment))
        moment = 'skipped'
    if moment == 'light-shift':
        for k in ('golden', 'night'):
            page.evaluate("window.__setLight('%s')" % k); page.wait_for_timeout(150)
            if page.evaluate("document.getElementById('day').getAttribute('data-light')") != k: problems.append('%s: light-shift did not switch to %s' % (name, k))
            check_contrast(page, name, 'light ' + k, '#day', scale)
        page.evaluate("window.__setLight('noon')")
    elif moment == 'seat-picker':
        page.evaluate("window.__fitSet(180)"); page.wait_for_timeout(100)
        fits = page.evaluate("[...document.querySelectorAll('.fit-row')].map(r => r.id + ':' + r.getAttribute('data-fit'))")
        if 'fit-greenhouse:yes' not in fits or 'fit-bamboo:no' not in fits or 'fit-barn:no' not in fits: problems.append('%s: seat picker wrong at 180: %s' % (name, fits))
        check_contrast(page, name, 'fit 180', '#fit', scale)
        page.evaluate("window.__fitSet(50)"); page.wait_for_timeout(100)
        if 'fit-bamboo:yes' not in page.evaluate("[...document.querySelectorAll('.fit-row')].map(r => r.id + ':' + r.getAttribute('data-fit'))"): problems.append('%s: seat picker wrong at 50' % name)
        page.evaluate("window.__fitSet(120)")
    elif moment == 'slideshow-counter':
        page.evaluate("window.__slideTo(1)"); page.wait_for_timeout(150)
        if '02' not in (page.inner_text('[data-counter]') if page.locator('[data-counter]').count() else ''): problems.append('%s: slideshow counter did not advance to 02' % name)
        check_contrast(page, name, 'slide 2', '[data-moment-root]', scale)
    elif moment in ('numbers-count', 'candle-count'):
        page.evaluate("window.__countFinish()"); page.wait_for_timeout(100)
        bad = page.evaluate("[...document.querySelectorAll('[data-count-to]')].filter(e => e.textContent.trim() !== e.getAttribute('data-count-to')).map(e => e.textContent)")
        if bad or not page.locator('[data-count-to]').count(): problems.append('%s: numbers did not settle on their content values: %s' % (name, bad))
        check_contrast(page, name, 'numbers settled', '[data-moment-root]', scale)
    elif moment == 'then-now':
        page.evaluate("window.__thenNow(25)"); page.wait_for_timeout(100)
        if page.evaluate("document.querySelector('[data-moment-root]').getAttribute('data-split')") != '25': problems.append('%s: then-now slider did not move to 25' % name)
    elif moment == 'pairs-counter':
        page.evaluate("window.__pairsTo(1)"); page.wait_for_timeout(150)
        if '2' not in (page.inner_text('[data-counter]') if page.locator('[data-counter]').count() else ''): problems.append('%s: pairs counter did not advance' % name)
        check_contrast(page, name, 'pair 2', '[data-moment-root]', scale)
    elif moment == 'hours-dial':
        page.evaluate("window.__dialSet(18)"); page.wait_for_timeout(100)
        if page.evaluate("document.querySelector('[data-moment-root]').getAttribute('data-dial-hour')") != '18': problems.append('%s: hours dial did not move to 18' % name)
        check_contrast(page, name, 'dial 18', '[data-moment-root]', scale)
    elif moment in ('crest-reveal', 'sprig-draw'):
        if not page.locator('[data-motion-device="draw-in"]').count(): problems.append('%s: %s moment without a [data-motion-device=draw-in] element' % (name, moment))
    elif moment == 'guest-journey':
        page.evaluate("window.__journeyActivate(2)"); page.wait_for_timeout(100)
        on = page.evaluate("[...document.querySelectorAll('.jstage-img')].findIndex(i => i.classList.contains('on'))")
        if on != 2 or not page.evaluate("document.querySelectorAll('.jstep')[2].classList.contains('active')"): problems.append('%s: journey step activation failed (on=%s)' % (name, on))
        check_contrast(page, name, 'journey step 3', '#journey', scale)
    # --- screenshots (last, because moving the sticky header out of flow shifts the layout) ---
    if not a.no_shots:
        page.evaluate("document.querySelectorAll('.reveal').forEach(e=>e.classList.add('visible')); window.scrollTo(0,0)")
        page.evaluate("Promise.all([...document.images].map(i => i.decode().catch(()=>0)))")
        full = fullshot(page, os.path.join(OUT, '%s.png' % name))
        hero_h = page.evaluate("document.querySelector('.hero').getBoundingClientRect().height")
        fullshot(page, os.path.join(OUT, '%s-hero.png' % name), clip=(0, 0, width, max(200, min(hero_h, 2400))))
    # --- screenshot pHash (desktop): fold + full-page rhythm strip ---
    if not mobile:
        if a.no_shots:
            page.evaluate("document.querySelectorAll('.reveal').forEach(e=>e.classList.add('visible')); window.scrollTo(0,0)")
            full = fullshot(page)
        info['phash'] = {'fold': PH.fold_hash(full), 'strip': PH.strip_hash(full)}
    # --- network ---
    reqs = page.evaluate("performance.getEntriesByType('resource').map(r => r.name).filter(u => !u.startsWith(location.origin))")
    ext = [u for u in reqs if 'fonts.g' not in u]
    if ext: problems.append('%s: unexpected external requests: %s' % (name, ext[:5]))
    for e in errors: problems.append('%s: console %s' % (name, e))
    ctx.close()


# 3A: nothing on the page may state a venue fact or policy the content file lacks; automations are labelled previews
if HTML and CONTENT:
    for pr in CL.check(HTML, CONTENT):
        problems.append('content trace: ' + pr)
elif HTML:
    problems.append('content trace: no content file found for this build (pass --content); invented-content checks could not run')
with sync_playwright() as pw:
    run(pw, 'desktop', 1440, 900, 2, False)
    run(pw, 'mobile', 390, 844, 2, True)
    # 1x DPR stroke probe: hairlines fail on non-retina screens first. Thresholds from docs/qa-calibration.md
    # (1x, ink<160, 3x3 opening): Cormorant 300 @60px = 0.225, Cormorant 500 @44px = 0.239, Bodoni Moda @60px = 0.12,
    # Newsreader 500 @44px = 0.09-0.12, Fraunces/Instrument/Jost <= 0.03. FAIL > 0.20, WARN > 0.12.
    ctx = pw.chromium.launch().new_context(viewport={'width': 1440, 'height': 900}, device_scale_factor=1)
    pg = ctx.new_page(); pg.goto(URL, wait_until='load'); pg.wait_for_function('document.fonts.ready.then(()=>true)'); pg.wait_for_timeout(400)
    for sel in ('h1', 'h2'):
        sp = stroke_probe(pg, 1, sel)
        if not sp: continue
        info.setdefault('stroke_1x', {})[sel] = sp
        if sp['size_css'] < 36:  # below display size the pairing's min_px rule governs; the opening kernel is too coarse here
            continue
        if sp['hairline_share_1px'] > 0.20:
            problems.append('1x: %s hairlines: %.0f%% of the letterform is <= 1 px thick at 1x DPR (%s %s %s @ %.0fpx)' % (sel, sp['hairline_share_1px'] * 100, sp['family'], sp['weight'], sp['fvs'], sp['size_css']))
        elif sp['hairline_share_1px'] > 0.12:
            warnings.append('1x: %s hairline share %.0f%% at 1x DPR (%s %s @ %.0fpx): fine on retina, watch on 1x screens' % (sel, sp['hairline_share_1px'] * 100, sp['family'], sp['weight'], sp['size_css']))
    ctx.close()

    # reduced motion: everything static; motion on: reveal timing inside the baseline
    for reduce in (True, False):
        ctx = pw.chromium.launch().new_context(viewport={'width': 1440, 'height': 900}, device_scale_factor=1, reduced_motion='reduce' if reduce else 'no-preference')
        pg = ctx.new_page(); pg.goto(URL, wait_until='load'); pg.wait_for_timeout(700)
        m = pg.evaluate("""() => { const run = document.getAnimations().filter(x => x.playState === 'running');
          const rev = [...document.querySelectorAll('.reveal')]; const hidden = rev.filter(e => e.getBoundingClientRect().top < innerHeight && parseFloat(getComputedStyle(e).opacity) < 0.99).length;
          const dur = rev.length ? getComputedStyle(rev[0]).transitionDuration : '';
          const dev = [...document.querySelectorAll('[data-motion-device]')].map(e => ({id: e.getAttribute('data-motion-device'), anims: e.getAnimations({subtree: true}).map(x => x.effect ? x.effect.getComputedTiming().duration : 0)}));
          const auto = [...document.querySelectorAll('[data-autoplay]')].map(e => e.getAttribute('data-autoplay'));
          return {running: run.length, running_names: run.slice(0, 5).map(x => x.animationName || x.transitionProperty || 'anim'), hidden_reveals: hidden, reveal_duration: dur, devices: dev, autoplay: auto}; }""")
        info.setdefault('motion', {})['reduced' if reduce else 'normal'] = m
        sink = problems if DIALECT_MODE else warnings
        if reduce:
            if m['running']: sink.append('motion: %d animations still running under prefers-reduced-motion (%s)' % (m['running'], m['running_names']))
            if m['hidden_reveals']: sink.append('motion: %d .reveal elements in the first screen stay hidden under prefers-reduced-motion' % m['hidden_reveals'])
            if [x for x in m['autoplay'] if str(x).lower() not in ('off', 'false', 'none', '0')]: sink.append('motion: [data-autoplay] still on under prefers-reduced-motion')
        else:
            secs = [float(x[:-2]) / 1000 if x.endswith('ms') else float(x[:-1]) for x in re.findall(r'[\d.]+m?s', m['reveal_duration'] or '')]
            if secs and any(d0 > 0 and not (0.6 <= d0 <= 1.2) for d0 in secs): sink.append('motion: reveal transition %s outside 600-1200 ms' % m['reveal_duration'])
            for d in m['devices']:
                for ms in d['anims']:
                    if ms and not (600 <= ms <= 1600): warnings.append('motion: device %s runs %d ms (dialect devices stay within 600-1600 ms)' % (d['id'], ms))
        ctx.close()

# --- 3A item 3: a dialect taken out of selection (dialects.json selectable: false) never passes --strict ---
if DIALECT_MODE:
    _dd = {d['id']: d for d in json.load(open(os.path.join(HERE, 'data', 'dialects.json')))['dialects']}
    if DIALECT in _dd and not _dd[DIALECT].get('selectable', True):
        (problems if a.strict else warnings).append('dialect %s is not selectable: %s' % (DIALECT, _dd[DIALECT].get('not_selectable_reason', '')[:160]))
# --- template fallbacks (stage 2B not built yet) ---
for f in (META or {}).get('fallbacks', []):
    msg = 'template fallback: %s "%s" -> %s (%s)' % (f['kind'], f['wanted'], f['used'] or 'omitted', 'planned for stage 2B')
    (problems if a.strict else warnings).append(msg)
info['fallbacks'] = len((META or {}).get('fallbacks', []))

# --- diversity ---
if META:
    reg = FP.load_registry(a.registry)
    g = FP.guard(META['fingerprint'], reg, exclude_id=META['id'])
    status, nid, dist = g['status'], g['driver'], g['distance']
    info['diversity'] = {'status': status, 'nearest': nid, 'distance': dist, 'all': [(r['id'], r['distance'], r['status']) for r in g['rows']], 'quota': g['quota']}
    why = next((r['rule'] for r in g['rows'] if r['id'] == nid), g['quota']['status'] + ' quota')
    if status == 'refuse': problems.append('diversity: too close to %s (%s)' % (nid, why))
    elif status == 'warn': warnings.append('diversity: family resemblance to %s (%s)' % (nid, why))
if 'phash' in info:
    reg = FP.load_registry(a.registry)
    ph_status, ph_rows = PH.compare(info['phash'], reg, exclude_id=(META or {}).get('id'))
    info['phash_compare'] = [(r['id'], r.get('fold'), r.get('strip'), r['status']) for r in ph_rows]
    near = next((r for r in ph_rows if r['status'] in ('refuse', 'warn')), None)
    if ph_status == 'refuse': problems.append('pHash: looks like %s (fold %s, strip %s of 256 bits differ; refuse <= %d)' % (near['id'], near['fold'], near['strip'], PH.REFUSE))
    elif ph_status == 'warn': warnings.append('pHash: close to %s (fold %s, strip %s of 256 bits; warn <= %d)' % (near['id'], near['fold'], near['strip'], PH.WARN))

json.dump({'url': URL, 'problems': problems, 'warnings': warnings, 'info': info, 'contrast': contrast_rows}, open(os.path.join(OUT, 'qa-report.json'), 'w'), indent=0, default=str)
small = [r for r in contrast_rows if not (r['size'] >= 24 or (r['size'] >= 18.66 and r['weight'] >= 700))]
print('%s\ntext nodes measured: %d (small %d). Lowest small-text ratio: %.2f, lowest overall: %.2f' % (URL, len(contrast_rows), len(small), min(r['min'] for r in small), min(r['min'] for r in contrast_rows)))
print('info:', json.dumps({k: v for k, v in info.items() if k not in ('diversity', 'motion', 'phash_compare', 'stroke', 'stroke_1x')}, default=str)[:1500])
if 'diversity' in info: print('diversity:', info['diversity']['status'].upper(), 'nearest', info['diversity']['nearest'], '%.3f' % info['diversity']['distance'], info['diversity']['all'])
print('\nWARNINGS: %d' % len(warnings))
for w in warnings: print('  ' + w)
print('\nPROBLEMS: %d' % len(problems))
for p in problems: print('  ' + p)
sys.exit(1 if problems else 0)
