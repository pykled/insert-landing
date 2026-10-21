"""Spec 05 section 5: looks the factory must never output, as concrete checks.

qa.py loads the built page in Chromium, runs COLLECT_JS once per viewport and passes the snapshot (a plain dict) to
run_all() together with build-meta.json, the content file and the raw index.html. Every check is a pure function of
those inputs, so tests feed it small fixture dicts (factory/tests/test_exclusions.py).

Each failure message starts with "E<n>" (the spec's exclusion number) and says what to change. Exclusion 20 (7:1 small
text, measured photo-background text) is the existing contrast walker in qa.py and is not repeated here.

Severity: for dialect builds every failure is a QA problem. Pre-dialect builds (build-meta dialect "none", and
hand-built mocks) get the same checks reported as warnings: those sites predate the spec and some are knowingly
outside the premium band (variant C).
"""
import re
from . import color as C

BANNED_SCRIPT = ('beloved', 'great vibes', 'allura', 'special elite', 'pacifico', 'dancing script', 'parisienne', 'sacramento',
                 'alex brush', 'pinyon script', 'tangerine', 'satisfy', 'kaushan script', 'courier prime', 'cutive mono', 'homemade apple',
                 'lobster', 'caveat', 'shadows into light', 'indie flower', 'courier new', 'courier')
BANNED_GENERIC = ('playfair display', 'montserrat', 'raleway', 'poppins', 'arial', 'open sans')
BANNED_WORDS = re.compile(r'\b(luxury|luxurious|stunning|unforgettable|dream(s|y|ing)?|magical)\b|elegance\s*(&|and|&amp;)\s*grandeur', re.I)
BADGE_RE = re.compile(r'award|badge|seal|rating|stars?\b|theknot|the knot|weddingwire|zola|best of 20\d\d|certified|as seen (in|on)|★|☆', re.I)
SLIDER_RE = re.compile(r'swiper|slick|splide|glide|flickity|carousel|slider|owl-', re.I)
POPUP_RE = re.compile(r'popup|pop-up|modal|newsletter|subscribe|chat-?widget|intercom|drift|crisp|tawk|promo-?bar|announcement-?bar|age-?gate|cookie', re.I)
WAVE_RE = re.compile(r'wave|curve|shape-divider|divider-svg|squiggle', re.I)
TEXTURE_RE = re.compile(r'paper|parchment|texture|grunge|noise|canvas|linen', re.I)
PASTE_IFRAME_RE = re.compile(r'<iframe[^>]+(youtube|vimeo)', re.I)
NOTIFY_RE = re.compile(r'Notification\.requestPermission|PushManager', re.I)
NUMBER_WORDS = {1: 'one', 2: 'two', 3: 'three', 4: 'four', 5: 'five', 6: 'six', 7: 'seven', 8: 'eight', 9: 'nine', 10: 'ten', 11: 'eleven', 12: 'twelve'}

# The snapshot every check reads. Keep it boring: one pass over the DOM, plain data out.
COLLECT_JS = r"""
() => {
  const vw = document.documentElement.clientWidth, vh = window.innerHeight, sy = window.scrollY;
  const r = e => { const b = e.getBoundingClientRect(); return {x: b.left, y: b.top + sy, w: b.width, h: b.height}; };
  const vis = e => { if (!e.getClientRects().length) return false; const cs = getComputedStyle(e); return cs.visibility !== 'hidden' && cs.display !== 'none' && parseFloat(cs.opacity) > 0; };
  const cls = e => (typeof e.className === 'string' ? e.className : (e.getAttribute('class') || ''));
  const imgs = [...document.images].filter(vis).map(i => ({el: i, b: r(i)}));
  const overlap = (a, b) => Math.max(0, Math.min(a.x + a.w, b.x + b.w) - Math.max(a.x, b.x)) * Math.max(0, Math.min(a.y + a.h, b.y + b.h) - Math.max(a.y, b.y));
  const overImage = b => imgs.some(i => i.b.w * i.b.h > 0 && overlap(b, i.b) / (b.w * b.h || 1) > 0.5);
  const textOf = e => [...e.childNodes].filter(n => n.nodeType === 3).map(n => n.textContent).join(' ').replace(/\s+/g, ' ').trim();
  const out = {viewport: {w: vw, h: vh}, text: [], fills: [], overlays: [], gradients: [], shadows: [], fixed: [], iframes: [], videos: [],
               ornaments: [], sections: [], hero: {}, nav: {}, carousels: [], learn_more_rows: 0, first_screen_text: '', facts_marked: [], dialogs: 0};
  out.paper = getComputedStyle(document.body).backgroundColor; out.html_bg = getComputedStyle(document.documentElement).backgroundColor;
  const hero = document.querySelector('.hero');
  for (const e of document.querySelectorAll('body *')) {
    if (['SCRIPT', 'STYLE', 'NOSCRIPT', 'TEMPLATE', 'svg', 'path'].includes(e.tagName) || !vis(e)) continue;
    const cs = getComputedStyle(e); const b = r(e); const c = cls(e);
    const t = textOf(e);
    if (t) {
      const lh = parseFloat(cs.lineHeight) || parseFloat(cs.fontSize) * 1.4;
      out.text.push({tag: e.tagName.toLowerCase(), cls: c, text: t.slice(0, 400), len: t.length, size: parseFloat(cs.fontSize), weight: parseInt(cs.fontWeight) || 400,
        family: cs.fontFamily.split(',')[0].replace(/["']/g, '').trim(), transform: cs.textTransform, ls: parseFloat(cs.letterSpacing) || 0, lh, h: b.h, top: b.y, w: b.w,
        on_photo: overImage(b), in_main: !!e.closest('main'), in_hero: !!(hero && hero.contains(e)), kicker: c.split(/\s+/).includes('kicker'),
        excluded: !!e.closest('figcaption,cite,small,label,.fine,.caption,.kicker,nav,header,footer,button,.btn,summary,dt,dd,th,td,.chips,.chip,[aria-hidden=true]')});
    }
    const bg = cs.backgroundColor; const bi = cs.backgroundImage;
    if (bg && bg !== 'rgba(0, 0, 0, 0)' && b.w * b.h >= 400) out.fills.push({tag: e.tagName.toLowerCase(), cls: c, bg, area: b.w * b.h, ornament: e.getAttribute('data-ornament')});
    const pseudo = ['::before', '::after'].map(p => ({p, cs: getComputedStyle(e, p)})).filter(x => x.cs.content && x.cs.content !== 'none');
    const layers = [{cs, b, own_text: t.length > 0 || !!e.querySelector('h1,h2,p,a,button,form'), name: e.tagName.toLowerCase() + '.' + c}].concat(pseudo.map(x => ({cs: x.cs, b, own_text: false, name: e.tagName.toLowerCase() + '.' + c + x.p})));
    for (const L of layers) {
      const pos = L.cs.position;
      if (L.b.w * L.b.h > 0 && (pos === 'absolute' || pos === 'fixed') && !L.own_text && e.tagName !== 'IMG' && overImage(L.b)) {
        out.overlays.push({name: L.name, bg: L.cs.backgroundColor, bgimage: L.cs.backgroundImage, opacity: parseFloat(L.cs.opacity)});
      }
      if (L.cs.backgroundImage && L.cs.backgroundImage.includes('gradient(')) out.gradients.push({name: L.name, bgimage: L.cs.backgroundImage, over_image: overImage(L.b), ornament: e.getAttribute('data-ornament') || (e.closest('[data-ornament]') ? e.closest('[data-ornament]').getAttribute('data-ornament') : null), opacity: parseFloat(L.cs.opacity)});
      if (L.cs.backgroundImage && /url\(/.test(L.cs.backgroundImage)) out.gradients.push({name: L.name, bgimage: L.cs.backgroundImage, url: true, over_image: false, ornament: null, opacity: parseFloat(L.cs.opacity)});
      if (L.cs.boxShadow && L.cs.boxShadow !== 'none') out.shadows.push({name: L.name, shadow: L.cs.boxShadow});
    }
    if ((cs.position === 'fixed' || cs.position === 'sticky') && !e.closest('header') && !c.includes('skip')) out.fixed.push({name: e.tagName.toLowerCase() + '.' + c + (e.id ? '#' + e.id : ''), area: b.w * b.h, position: cs.position});
    if (POPUP_TEST(e.id + ' ' + c)) out.fixed.push({name: 'named:' + e.tagName.toLowerCase() + '.' + c + (e.id ? '#' + e.id : ''), area: b.w * b.h, position: cs.position, named: true});
    if (WAVE_TEST(e.id + ' ' + c)) out.shadows.push({name: e.tagName.toLowerCase() + '.' + c, wave: true});
    if (cs.clipPath && cs.clipPath !== 'none' && e.tagName === 'SECTION') out.shadows.push({name: 'section.' + c, clip: cs.clipPath});
    if ((cs.overflowX === 'auto' || cs.overflowX === 'scroll') && e.scrollWidth > e.clientWidth + 4 && e.children.length >= 3) {
      const ws = [...e.children].map(k => Math.round(k.getBoundingClientRect().width));
      if (ws.every(w => Math.abs(w - ws[0]) <= 2)) out.carousels.push(e.tagName.toLowerCase() + '.' + c);
    }
  }
  out.dialogs = [...document.querySelectorAll('dialog[open],[role=dialog],[aria-modal=true]')].filter(vis).length;
  out.iframes = [...document.querySelectorAll('iframe')].map(f => f.src || '');
  out.videos = [...document.querySelectorAll('video')].map(v => ({autoplay: v.autoplay, poster: v.getAttribute('poster') || '', reduced: v.getAttribute('data-reduced-motion') || '', in_hero: !!(hero && hero.contains(v))}));
  out.ornaments = [...document.querySelectorAll('[data-ornament]')].map(e => ({id: e.getAttribute('data-ornament'), body: e === document.body, tag: e.tagName.toLowerCase()}));
  out.sections = [...document.querySelectorAll('main > section, main > div > section')].map(s => s.id || ('.' + cls(s).split(' ')[0]));
  if (hero) {
    out.hero = {cls: cls(hero), slider_hits: [...hero.querySelectorAll('*')].concat([hero]).map(e => e.id + ' ' + cls(e)).filter(SLIDER_TEST).slice(0, 5),
      autoplay: [...hero.querySelectorAll('[data-autoplay]')].map(e => e.getAttribute('data-autoplay')), imgs: hero.querySelectorAll('img').length,
      framing: hero.getAttribute('data-hero-framing') || ''};
  }
  const head = document.querySelector('header');
  if (head) {
    const links = [...head.querySelectorAll('a')].filter(vis);
    out.nav = {links: links.length, labels: links.map(a => a.textContent.trim()).slice(0, 14), nested: head.querySelectorAll('nav li ul, nav li ol').length,
      dropdowns: [...head.querySelectorAll('details, [aria-haspopup], [class*=dropdown], [class*=mega], [class*=submenu]')].length,
      pricing: links.some(a => /pric|rate|guide/i.test(a.textContent + ' ' + (a.getAttribute('href') || '')))};
  }
  const lm = {}; for (const a of document.querySelectorAll('a,button')) { if (/^\s*learn more\s*$/i.test(a.textContent)) { const k = a.parentElement && a.parentElement.parentElement; if (k) { k.__lm = (k.__lm || 0) + 1; out.learn_more_rows = Math.max(out.learn_more_rows, k.__lm); } } }
  const first = []; const tw = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT); let n;
  while ((n = tw.nextNode())) { const el = n.parentElement; if (!el || !vis(el) || el.closest('script,style,nav')) continue; const b = el.getBoundingClientRect(); if (b.top + sy < vh && b.bottom + sy > 0) first.push(n.textContent); }
  out.first_screen_text = first.join(' ').replace(/\s+/g, ' ').slice(0, 4000);
  out.facts_marked = [...document.querySelectorAll('[data-fact]')].filter(vis).filter(e => e.getBoundingClientRect().top + sy < vh).map(e => e.getAttribute('data-fact'));
  out.badges_first_screen = [...document.images].filter(vis).filter(i => i.getBoundingClientRect().top + sy < vh).map(i => (i.alt || '') + ' ' + i.src.split('/').pop() + ' ' + cls(i)).filter(s => BADGE_TEST(s));
  const feat = document.querySelector('#featured, [data-press]');
  out.press = feat ? {top: feat.getBoundingClientRect().top + sy, imgs: [...feat.querySelectorAll('img')].map(i => i.getBoundingClientRect().height)} : null;
  return out;
}
"""
COLLECT_JS = (COLLECT_JS
              .replace('POPUP_TEST(', '(s => /%s/i.test(s))(' % POPUP_RE.pattern)
              .replace('WAVE_TEST(', '(s => /%s/i.test(s))(' % WAVE_RE.pattern)
              .replace('SLIDER_TEST', '(s => /%s/i.test(s))' % SLIDER_RE.pattern)
              .replace('BADGE_TEST(', '(s => /%s/i.test(s))(' % BADGE_RE.pattern.replace('/', '\\/')))


def parse_rgba(s):
    m = re.match(r'rgba?\(([^)]+)\)', s or '')
    if not m:
        return None
    p = [float(x) for x in m.group(1).replace('/', ',').split(',') if x.strip()]
    return (p[0], p[1], p[2], p[3] if len(p) > 3 else 1.0)


def chroma_of(rgba):
    L, Ch, h = C.lab_to_lch(C.rgb_to_oklab(__import__('numpy').array([rgba[0] / 255, rgba[1] / 255, rgba[2] / 255])))
    return float(L), float(Ch), float(h)


def gradient_alphas(bgimage):
    """[(lum 0..1, alpha)] for every colour stop in a computed background-image."""
    out = []
    for m in re.finditer(r'rgba?\([^)]+\)', bgimage or ''):
        c = parse_rgba(m.group(0))
        if c:
            out.append(((0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]) / 255, c[3]))
    return out


def _fact_tokens(content):
    tf = content.get('tagline_facts') or {}
    toks = {}
    for key in ('max_guests', 'acres', 'space_count'):
        val = tf.get(key)
        if isinstance(val, (int, float)):
            toks[key] = [str(int(val))] + ([NUMBER_WORDS[int(val)]] if int(val) in NUMBER_WORDS else [])
    era = (content.get('vibe') or {}).get('era')
    if era:
        toks['year'] = [str(era)]
    for t in (content.get('story') or {}).get('timeline') or []:
        if str(t.get('year', '')).isdigit():
            toks.setdefault('year', []).append(str(t['year']))
    return toks


# --- the checks: each returns a list of failure strings ---------------------------------------------------------

def e1_paper_and_fills(page, meta, dialect):
    out = []
    for key in ('paper', 'html_bg'):
        c = parse_rgba(page.get(key))
        if c and c[3] > 0 and c[:3] == (255.0, 255.0, 255.0):
            out.append('E1 pure white paper (%s %s): paper must be L 0.93-0.985 with a tint (or charcoal)' % (key, page.get(key)))
    if dialect != 'deco':
        for f in page.get('fills', []):
            c = parse_rgba(f['bg'])
            if not c or c[3] < 0.5:
                continue
            L, Ch, h = chroma_of(c)
            if Ch > 0.14:
                out.append('E1 saturated fill C %.3f > 0.14 on %s.%s (%s): only deco may fill with a saturated accent' % (Ch, f['tag'], f['cls'][:40], f['bg']))
    return out


def e2_display_weights(page, meta):
    out = []
    pair = (meta or {}).get('pairing') or {}
    disp = pair.get('display') or {}
    if disp:
        w = disp.get('weight')
        if not isinstance(w, int) or not (400 <= w <= 600):
            out.append('E2 display weight %s not pinned inside 400-600' % w)
        if disp.get('has_opsz') and 'opsz' not in (disp.get('vars') or ''):
            out.append('E2 display face %s has an opsz axis but no pinned opsz' % disp.get('family'))
    for t in page.get('text', []):
        if t['weight'] <= 200:
            out.append('E2 weight %d text (%s "%s"): weights 100/200 are never allowed' % (t['weight'], t['tag'], t['text'][:40]))
        elif t['weight'] <= 300 and t['on_photo'] and t['size'] >= 24:
            out.append('E2 display weight %d on a photo (%s %.0fpx "%s")' % (t['weight'], t['tag'], t['size'], t['text'][:40]))
    return out


def e3_e4_families(page, html):
    out, seen = [], set()
    imports = re.findall(r'fonts\.googleapis\.com/css2\?([^"\']+)', html or '')
    fams = [f.replace('+', ' ').lower() for imp in imports for f in re.findall(r'family=([^:&]+)', imp)]
    for f in fams:
        if f in BANNED_SCRIPT:
            out.append('E3 script/handwriting/typewriter face loaded: %s' % f)
        if f in BANNED_GENERIC:
            out.append('E4 banned generic face loaded: %s' % f)
    for t in page.get('text', []):
        f = t['family'].lower()
        if f in seen:
            continue
        seen.add(f)
        if f in BANNED_SCRIPT:
            out.append('E3 text set in %s ("%s")' % (t['family'], t['text'][:40]))
        if f in BANNED_GENERIC:
            out.append('E4 text set in %s ("%s"): the generic trio / CMS defaults are banned as display or body' % (t['family'], t['text'][:40]))
    return out


def _is_caps(t):
    letters = re.sub(r'[^A-Za-z]', '', t['text'])
    return t['transform'] == 'uppercase' or (len(letters) >= 8 and letters.upper() == letters)


def e5_tracked_caps(page):
    out = []
    for t in page.get('text', []):
        if t['len'] > 60 and _is_caps(t) and t['size'] and t['ls'] / t['size'] >= 0.05:
            out.append('E5 tracked caps run of %d chars (%s "%s..."): caps only for <= 60 characters' % (t['len'], t['tag'], t['text'][:40]))
    return out


def e6_lead_subject(meta, content):
    lead = (meta or {}).get('lead')
    m = ((content.get('photos') or {}).get('items') or {}).get(lead) or {}
    subj = m.get('subject')
    if subj == 'people':
        return ['E6 lead photo "%s" is tagged subject=people: the lead must be the place (place/building/grounds/interior/detail)' % lead]
    return []


def e7_badges(page, story_id='story'):
    out = []
    for b in page.get('badges_first_screen', []):
        out.append('E7 badge/award/review image in the first screen: %s' % b[:80])
    txt = page.get('first_screen_text', '')
    m = re.search(r'★|☆|\b\d(\.\d)?\s*stars?\b|award[- ]winning|as seen (in|on)|best of 20\d\d', txt, re.I)
    if m:
        out.append('E7 badge / review text in the first screen: "%s"' % m.group(0))
    press = page.get('press')
    if press:
        if press['top'] < page['viewport']['h']:
            out.append('E7 press row above the fold (top %dpx): press only in a row below the story' % press['top'])
        secs = page.get('sections', [])
        if 'featured' in secs and story_id in secs and secs.index('featured') < secs.index(story_id):
            out.append('E7 press row (featured) placed before the story section')
        tall = [h for h in press.get('imgs', []) if h > 24]
        if tall:
            out.append('E7 press logos taller than 24px (%s): plain grey wordmarks from the content file only' % tall[:3])
    return out


def e8_sliders(page):
    out = []
    hero = page.get('hero') or {}
    for h in hero.get('slider_hits', []):
        out.append('E8 slider/carousel markup in the hero: "%s"' % h.strip()[:60])
    for a in hero.get('autoplay', []):
        if str(a).lower() not in ('off', 'false', 'none', '0'):
            out.append('E8 auto-advancing hero (data-autoplay=%s): hero slideshows are user-advanced only' % a)
    for c in page.get('carousels', []):
        out.append('E8 carousel of equal cards: %s' % c[:60])
    if page.get('learn_more_rows', 0) >= 3:
        out.append('E8 a row of %d "Learn more" cards' % page['learn_more_rows'])
    return out


def e9_scrims(page):
    out = []
    for o in page.get('overlays', []):
        c = parse_rgba(o['bg'])
        flat = c and c[3] > 0 and (o['bgimage'] in (None, '', 'none'))
        if flat:
            a = c[3] * (o.get('opacity') if o.get('opacity') is not None else 1)
            lum = (0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]) / 255
            if lum < 0.5 and a > 0.35:
                out.append('E9 flat dark scrim %.0f%% over a photo (%s): gradient to max 35%%' % (a * 100, o['name'][:50]))
            elif lum >= 0.5 and a > 0.20:
                out.append('E9 flat light scrim %.0f%% over a photo (%s): gradient to max 20%% white' % (a * 100, o['name'][:50]))
            else:
                out.append('E9 flat scrim over a photo (%s, %.0f%%): scrims are gradients only' % (o['name'][:50], a * 100))
        for lum, a in gradient_alphas(o.get('bgimage')):
            a *= o.get('opacity') if o.get('opacity') is not None else 1
            if lum < 0.5 and a > 0.35:
                out.append('E9 scrim gradient reaches %.0f%% black (%s): max 35%%' % (a * 100, o['name'][:50])); break
            if lum >= 0.5 and a > 0.20:
                out.append('E9 scrim gradient reaches %.0f%% white (%s): max 20%%' % (a * 100, o['name'][:50])); break
    return out


def e10_popups(page, html):
    out = []
    if page.get('dialogs'):
        out.append('E10 %d open dialog/modal element(s) on arrival' % page['dialogs'])
    for f in page.get('fixed', []):
        if f.get('named'):
            out.append('E10 popup/modal/chat/promo element present: %s' % f['name'][:60])
        elif f['position'] == 'fixed' and f['area'] > 0.04 * page['viewport']['w'] * page['viewport']['h']:
            out.append('E10 fixed overlay outside the header (%s, %d px2): no popups, promo bars or chat widgets' % (f['name'][:60], f['area']))
    if NOTIFY_RE.search(html or ''):
        out.append('E10 notification / push prompt in the page script')
    return out


def _blur_radii(shadow):
    """Blur radius (3rd length) of every layer in a computed box-shadow."""
    out = []
    for layer in re.split(r',(?![^(]*\))', shadow or ''):
        nums = [float(x) for x in re.findall(r'(-?\d+(?:\.\d+)?)px', re.sub(r'rgba?\([^)]*\)', '', layer))]
        if len(nums) >= 3:
            out.append(nums[2])
    return out


def e11_dividers_textures_shadows(page, dialect):
    out = []
    for s in page.get('shadows', []):
        if s.get('wave'):
            out.append('E11 wave/curved divider: %s' % s['name'][:60])
        elif s.get('clip'):
            out.append('E11 clipped section edge (%s on %s): no curved or angled dividers' % (s['clip'][:40], s['name'][:40]))
        else:
            big = [b for b in _blur_radii(s.get('shadow')) if b > 34]
            if big:
                out.append('E11 drop shadow blur %dpx > 34px on %s' % (max(big), s['name'][:50]))
    for g in page.get('gradients', []):
        if g.get('url'):
            if TEXTURE_RE.search(g['bgimage']):
                grain_ok = dialect == 'editorial' and 'noise' in g['bgimage'].lower() and (g.get('opacity') or 1) <= 0.06
                if not grain_ok:
                    out.append('E11 paper/parchment texture background: %s' % g['name'][:50])
            continue
        if g.get('over_image') or g.get('ornament'):
            continue   # scrims are judged by E9; ornament devices (underline-bar) are judged by E13
        stops = gradient_alphas(g['bgimage'])
        wash_ok = dialect == 'botanical' and 'radial-gradient' in g['bgimage'] and all(a <= 0.08 for _, a in stops)
        if not wash_ok:
            out.append('E11 gradient used as a background on %s: gradients only as scrims or the botanical wash (<= 8%%)' % g['name'][:50])
    return out


def e12_video(page, html):
    out = []
    for src in page.get('iframes', []):
        if re.search(r'youtube|vimeo', src, re.I):
            out.append('E12 YouTube/Vimeo iframe: %s' % src[:60])
    if PASTE_IFRAME_RE.search(html or '') and not out:
        out.append('E12 YouTube/Vimeo iframe in the markup')
    for v in page.get('videos', []):
        if v['autoplay'] and not v['poster']:
            out.append('E12 autoplay video without a composed poster frame')
        if v['autoplay'] and not v['reduced']:
            out.append('E12 autoplay video without a reduced-motion fallback (data-reduced-motion)')
    return out


def e13_ornaments(page, meta):
    out = []
    orn = [o for o in page.get('ornaments', []) if o['id'] and o['id'] != 'none']
    ids = sorted({o['id'] for o in orn})
    if len(ids) > 1:
        out.append('E13 %d ornament devices on one page (%s): exactly one per site' % (len(ids), ', '.join(ids)))
    placed = [o for o in orn if not o['body']]
    if len(placed) > 3:
        out.append('E13 ornament "%s" used %d times: at most three instances' % (placed[0]['id'], len(placed)))
    want = ((meta or {}).get('choices') or {}).get('ornament')
    if want and want != 'none' and not orn:
        out.append('E13 build chose ornament "%s" but the page carries no [data-ornament] marker' % want)
    if want and ids and want not in ids:
        out.append('E13 page ornament %s does not match the build choice %s' % (ids, want))
    return out


def e14_nav(page):
    out = []
    nav = page.get('nav') or {}
    if nav.get('links', 0) > 8:
        out.append('E14 header has %d links (> 8): %s' % (nav['links'], ', '.join(nav.get('labels', [])[:10])))
    if nav.get('nested') or nav.get('dropdowns'):
        out.append('E14 dropdown / mega-menu markup in the header (%d nested lists, %d dropdown hooks)' % (nav.get('nested', 0), nav.get('dropdowns', 0)))
    return out


def e15_banned_words(page):
    out = []
    for t in page.get('text', []):
        if t['tag'] in ('h1', 'h2') or t['kicker']:
            m = BANNED_WORDS.search(t['text'])
            if m:
                out.append('E15 banned word "%s" in %s: "%s"' % (m.group(0), 'kicker' if t['kicker'] else t['tag'], t['text'][:60]))
    return out


def e16_body_measure(page):
    out = []
    small, long_ = [], []
    for t in page.get('text', []):
        if t['tag'] in ('h1', 'h2', 'h3'):
            words = len(t['text'].split())
            if t['tag'] in ('h1', 'h2') and words > 14:
                out.append('E16 headline of %d words (> 14): "%s"' % (words, t['text'][:60]))
            continue
        if t['tag'] != 'p' or not t['in_main'] or t['excluded'] or t['len'] < 40:
            continue
        if t['size'] < 16.5:
            small.append(t)
        lines = round(t['h'] / t['lh']) if t['lh'] else 1
        if lines >= 2:
            cpl = t['len'] / lines
            if cpl > 72:
                long_.append((cpl, t))
    for t in small[:4]:
        out.append('E16 body text %.1fpx < 16.5px: "%s"' % (t['size'], t['text'][:50]))
    for cpl, t in sorted(long_, key=lambda x: -x[0])[:4]:
        out.append('E16 line length ~%d characters (> 72): "%s"' % (cpl, t['text'][:50]))
    return out


def e17_corner(meta):
    p = (meta or {}).get('personality') or {}
    dialect = (meta or {}).get('dialect', {}).get('id') if isinstance((meta or {}).get('dialect'), dict) else (meta or {}).get('dialect')
    if p.get('density', 0) >= 85 and p.get('voice', 0) >= 85:
        if dialect != 'modern-luxe':
            return ['E17 density %d with voice %d (the spec-sheet SaaS corner) outside modern-luxe' % (p['density'], p['voice'])]
        tok = (meta or {}).get('axis_tokens') or {}
        if tok.get('section_pad_min', 0) < 160:
            return ['E17 modern-luxe at density/voice >= 85 needs section padding >= 160px (got %s)' % tok.get('section_pad_min')]
        framing = ((meta or {}).get('fingerprint') or {}).get('hero_framing')
        if framing not in ('inset', 'silent'):
            return ['E17 modern-luxe at density/voice >= 85 needs inset photos (hero framing %s)' % framing]
    return []


def e18_sections_before_tour(page):
    secs = [s for s in page.get('sections', []) if s not in ('', '.hero') and not s.startswith('.hero')]
    if 'tour' not in secs:
        return ['E18 no #tour section found'], []
    n = secs.index('tour')
    probs = ['E18 %d sections before the tour (> 6): %s' % (n, ', '.join(secs[:n]))] if n > 6 else []
    warns = ['E18 %d sections before the tour (baseline 3-5)' % n] if (n < 3 or n > 5) and not probs else []
    return probs, warns


def e19_first_screen_facts(page, content):
    toks = _fact_tokens(content)
    txt = ' ' + page.get('first_screen_text', '').lower() + ' '
    found = sorted({k for k, vals in toks.items() for v in vals if re.search(r'(?<![\d.])%s(?![\d])' % re.escape(v.lower()), txt)} | set(page.get('facts_marked', [])))
    nav = page.get('nav') or {}
    warns = []
    if not nav.get('pricing'):
        warns.append('baseline: no price / pricing-guide link visible in the header')
    if not found:
        return ['E19 no fact (guests / acres / year / spaces) in the first screen'], warns
    if len(found) < 2:
        warns.append('baseline: only one fact in the first screen (%s); the baseline asks for two' % ', '.join(found))
    return [], warns


def run_all(page, meta, content, html, dialect_mode=True):
    """Run every exclusion. Returns (problems, warnings, summary). With dialect_mode False all problems become warnings."""
    dialect = None
    if meta and isinstance(meta.get('dialect'), dict):
        dialect = meta['dialect'].get('id')
    fails = []
    warns = []
    fails += e1_paper_and_fills(page, meta, dialect)
    fails += e2_display_weights(page, meta)
    fails += e3_e4_families(page, html)
    fails += e5_tracked_caps(page)
    fails += e6_lead_subject(meta, content or {})
    fails += e7_badges(page)
    fails += e8_sliders(page)
    fails += e9_scrims(page)
    fails += e10_popups(page, html)
    fails += e11_dividers_textures_shadows(page, dialect)
    fails += e12_video(page, html)
    fails += e13_ornaments(page, meta)
    fails += e14_nav(page)
    fails += e15_banned_words(page)
    fails += e16_body_measure(page)
    fails += e17_corner(meta)
    p, w = e18_sections_before_tour(page); fails += p; warns += w
    p, w = e19_first_screen_facts(page, content or {}); fails += p; warns += w
    summary = {}
    for f in fails:
        k = f.split(' ')[0]
        summary[k] = summary.get(k, 0) + 1
    if not dialect_mode:
        return [], ['[pre-dialect] ' + f for f in fails] + warns, summary
    return fails, warns, summary
