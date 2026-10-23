"""Photo candidates (pure HTML -> URLs grouped per distinct photo, largest variant first) and per-photo analysis
(size, pHash, dialect signals, dominant colours, sharpness, subject/flora guesses, face check when OpenCV exists)."""
import re
from urllib.parse import urljoin, urlparse, urlunparse

IMG_EXT = re.compile(r'\.(jpe?g|png|webp|avif)(?:$|[?#/])', re.I)
SKIP_EXT = re.compile(r'\.(svg|gif|ico)(?:$|[?#])', re.I)
LOGO_LIKE = re.compile(r'logo|icon|favicon|badge|sprite|avatar|award|seal|emblem|signature|button|arrow|theknot|weddingwire|'
                       r'zola|placeholder|blank|spacer|pixel|wordmark|monogram|cropped-', re.I)
STOCK_LIKE = re.compile(r'shutterstock|istock|adobestock|adobe-stock|depositphotos|dreamstime|unsplash|pexels|gettyimages|'
                        r'stock-photo|bigstock|123rf|freepik', re.I)
URL_IN_CSS = re.compile(r'url\(\s*[\'"]?([^\'")]+)[\'"]?\s*\)')
WIX_RE = re.compile(r'https?://static\.wixstatic\.com/media/[A-Za-z0-9_~.\-]+\.(?:jpe?g|png|webp)[^"\'\s)\\]*')
SHOWIT_RE = re.compile(r'(?:https?:)?//static\.showit\.co/v2/[^"\'\s),]+')
SUBJECT_WORDS = [
    ('people', r'\b(bride|groom|couple|newlyweds?|bridesmaids?|groomsmen|wedding party|kiss|portrait|guests? dancing|first dance|mr and mrs|family photo)\b'),
    ('interior', r'\b(interior|inside|ballroom|room|hall|parlou?r|library|kitchen|staircase|foyer|dining room|suite|chandelier)\b'),
    ('building', r'\b(house|home|barn|exterior|facade|fa[cç]ade|mansion|manor|chapel|cottage|building|porch|veranda)\b'),
    ('grounds', r'\b(garden|lawn|grounds|trees?|oaks?|orchard|meadow|field|courtyard|patio|terrace|aisle|ceremony site|arbor|pergola|fountain|pond|path)\b'),
    ('detail', r'\b(detail|table ?scape|place setting|centerpiece|florals?|bouquet|cake|rings?|signage|menu|decor)\b'),
]
FLORA_WORDS = {'olive': r'\bolive', 'fig': r'\bfig\b', 'fern': r'\bferns?\b', 'lavender': r'\blavender', 'oak': r'\boaks?\b',
               'eucalyptus': r'\beucalyptus'}


def _abs(u, base):
    u = (u or '').strip()
    if not u or u.startswith('data:'):
        return None
    return urljoin(base, u)


def parse_srcset(s, base):
    out = []
    for part in re.split(r',\s+(?=\S)', s or ''):
        bits = part.strip().split()
        if not bits:
            continue
        u = _abs(bits[0], base)
        w = None
        if len(bits) > 1 and bits[1].endswith('w') and bits[1][:-1].isdigit():
            w = int(bits[1][:-1])
        if u:
            out.append((u, w))
    return out


def width_hint(u):
    m = re.search(r'/variant/(\d+)/', u) or re.search(r'/w_(\d+)[,/]', u) or re.search(r'-(\d{3,4})x\d{3,4}\.\w+$', urlparse(u).path) \
        or re.search(r'[?&]format=(\d+)w', u) or re.search(r'[?&]w=(\d+)', u)
    return int(m.group(1)) if m else None


def photo_key(u):
    """Group every size variant of one photo under one key."""
    p = urlparse(u)
    host, path = p.netloc.lower(), p.path
    if 'wixstatic.com' in host:
        m = re.match(r'(/media/[^/]+)', path)
        return host + (m.group(1) if m else path)
    if 'showit.co' in host:
        m = re.match(r'(/v2/\d+/[^/]+/[^/]+)', path)
        return host + (m.group(1) if m else path)
    path = re.sub(r'-\d{2,4}x\d{2,4}(?=\.\w+$)', '', path)
    path = re.sub(r'-(scaled|e\d{10,})(?=\.\w+$)', '', path)
    path = re.sub(r'\.(jpe?g|png|webp|avif)\.webp$', r'.\1', path)
    return host + path


def upgrades(u):
    """Larger-variant URLs a CDN is known to serve for this photo (tried before the page's own largest)."""
    p = urlparse(u)
    host, path = p.netloc.lower(), p.path
    out = []
    if 'wixstatic.com' in host:
        m = re.match(r'(/media/[^/]+)', path)
        if m:
            out.append(urlunparse(('https', 'static.wixstatic.com', m.group(1), '', '', '')))
    elif 'showit.co' in host:
        m = re.match(r'(/v2/\d+/[^/]+/[^/]+)', path)
        if m:
            out.append(urlunparse(('https', 'static.showit.co', m.group(1) + '/variant/3200/webp', '', '', '')))
    elif 'squarespace' in host:
        out.append(urlunparse((p.scheme or 'https', p.netloc, path, '', 'format=2500w', '')))
    else:
        orig = re.sub(r'-\d{2,4}x\d{2,4}(?=\.\w+$)', '', path)
        if orig != path:
            out.append(urlunparse((p.scheme or 'https', p.netloc, orig, '', '', '')))
        stripped = re.sub(r'-scaled(?=\.\w+$)', '', orig)
        if stripped != orig:
            out.append(urlunparse((p.scheme or 'https', p.netloc, stripped, '', '', '')))
    return out


def candidates(soup, raw_html, page_url):
    """-> list of {'url','w','alt','ctx','page','how'}"""
    out = []

    def add(u, w, alt, ctx, how):
        if u and not SKIP_EXT.search(u) and (IMG_EXT.search(u) or 'wixstatic.com/media' in u or 'showit.co/v2' in u):
            out.append({'url': u.split('#')[0], 'w': w or width_hint(u), 'alt': (alt or '').strip(), 'ctx': ctx[:200], 'page': page_url, 'how': how})
    for img in soup.find_all('img'):
        alt = img.get('alt') or img.get('title') or ''
        ctx = ' '.join(img.get('class') or []) + ' ' + ' '.join(' '.join(p.get('class') or []) for p in list(img.parents)[:3] if hasattr(p, 'get'))
        for a in ('src', 'data-src', 'data-lazy-src', 'data-original', 'data-orig-file', 'data-large-file', 'data-full', 'data-image'):
            if img.get(a):
                add(_abs(img.get(a), page_url), int(img['width']) if a == 'src' and str(img.get('width', '')).isdigit() else None, alt, ctx, 'img@' + a)
        for a in ('srcset', 'data-srcset', 'data-lazy-srcset'):
            for u, w in parse_srcset(img.get(a), page_url):
                add(u, w, alt, ctx, 'img@' + a)
    for src in soup.find_all('source'):
        for a in ('srcset', 'data-srcset'):
            for u, w in parse_srcset(src.get(a), page_url):
                add(u, w, '', 'picture', 'picture source')
    for k in ('og:image', 'twitter:image'):
        t = soup.find('meta', attrs={'property': k}) or soup.find('meta', attrs={'name': k})
        if t and t.get('content'):
            add(_abs(t['content'], page_url), None, '', k, k)
    for a in soup.find_all('a', href=True):
        if IMG_EXT.search(a['href']):
            add(_abs(a['href'], page_url), None, a.get('title') or a.get('data-caption') or '', 'lightbox link', 'a@href')
    for el in soup.find_all(style=True):
        for u in URL_IN_CSS.findall(el['style']):
            add(_abs(u, page_url), None, el.get('aria-label') or '', 'inline style', 'css background')
    for st in soup.find_all('style'):
        for u in URL_IN_CSS.findall(st.get_text() or ''):
            add(_abs(u, page_url), None, '', 'style block', 'css background')
    for u in WIX_RE.findall(raw_html):
        add(u, None, '', 'wix media', 'wix media url')
    for u in SHOWIT_RE.findall(raw_html):
        add(_abs(u, page_url), None, '', 'showit media', 'showit url')
    return out


def group(cands):
    """-> {key: {'urls': [(url, w)], 'alt': best alt, 'ctx', 'pages': set, 'how'}} with urls largest first."""
    g = {}
    for c in cands:
        k = photo_key(c['url'])
        e = g.setdefault(k, {'urls': {}, 'alts': [], 'ctx': set(), 'pages': [], 'how': set()})
        e['urls'][c['url']] = max(e['urls'].get(c['url']) or 0, c['w'] or 0)
        if c['alt']:
            e['alts'].append(c['alt'])
        e['ctx'].add(c['ctx'])
        if c['page'] not in e['pages']:
            e['pages'].append(c['page'])
        e['how'].add(c['how'])
    out = {}
    for k, e in g.items():
        urls = sorted(e['urls'].items(), key=lambda x: -(x[1] or 0))
        alt = max(e['alts'], key=len) if e['alts'] else ''
        out[k] = {'urls': urls, 'alt': alt, 'ctx': ' '.join(sorted(e['ctx'])), 'pages': e['pages'], 'how': sorted(e['how'])}
    return out


def try_order(entry):
    """Download order for one photo: known CDN upgrades, then the page's variants largest first."""
    seen, out = set(), []
    for u in upgrades(entry['urls'][0][0]) + [u for u, _ in entry['urls']]:
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out


def pre_skip(key, entry):
    """Reason to skip before downloading, or None."""
    text = key + ' ' + entry['alt'] + ' ' + entry['ctx']
    if LOGO_LIKE.search(key) or LOGO_LIKE.search(entry['alt']):
        return 'logo/icon-like name or alt'
    if re.search(r'\.png$', key, re.I) and re.search(r'logo|icon|badge', text, re.I):
        return 'logo-like png'
    known = [w for _, w in entry['urls'] if w]
    if known and max(known) < 800 and not upgrades(entry['urls'][0][0]):
        return 'largest stated variant %dpx < 800' % max(known)
    return None


def guess_subject(text):
    t = text.lower()
    for subj, rx in SUBJECT_WORDS:
        if re.search(rx, t):
            return subj
    return 'unknown'


def guess_flora(text):
    for k, rx in FLORA_WORDS.items():
        if re.search(rx, text, re.I):
            return k
    return None


def possible_stock(key):
    name = urlparse('//' + key).path.rsplit('/', 1)[-1]
    stem = re.sub(r'\.\w+$', '', name)
    words = [w for w in re.split(r'[-_]', stem) if w.isalpha()]
    return bool(STOCK_LIKE.search(key)) or len(words) >= 6


def hamming(a, b):
    return bin(int(a, 16) ^ int(b, 16)).count('1')


_FACE = {'checked': None}


def _face_detector():
    if _FACE['checked'] is None:
        try:
            import cv2
            path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            _FACE['checked'] = cv2.CascadeClassifier(path)
        except Exception:
            _FACE['checked'] = False
    return _FACE['checked']


def faces(path):
    det = _face_detector()
    if not det:
        return 'unchecked', None
    import cv2
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return 'unchecked', None
    scale = 1000.0 / max(img.shape)
    if scale < 1:
        img = cv2.resize(img, None, fx=scale, fy=scale)
    found = det.detectMultiScale(img, 1.1, 6, minSize=(30, 30))
    area = sum(int(w) * int(h) for (x, y, w, h) in found) / float(img.shape[0] * img.shape[1])
    return ('faces' if len(found) else 'none'), {'count': int(len(found)), 'area_share': round(area, 4)}


def analyse(path, palette_mod, phash_mod):
    """Pixel facts + scorer signals for one saved photo."""
    import numpy as np
    from PIL import Image
    im = Image.open(path).convert('RGB')
    w, h = im.size
    small = im.copy()
    small.thumbnail((480, 480))
    g = np.asarray(small.convert('L'), dtype=np.float64)
    lap = g[1:-1, 1:-1] * 4 - g[:-2, 1:-1] - g[2:, 1:-1] - g[1:-1, :-2] - g[1:-1, 2:]
    sharp = float(lap.var())
    sig = palette_mod.photo_signal(path)
    clusters = sorted(palette_mod.photo_clusters(path, k=5), key=lambda c: -c['w'])[:3]
    from lib import color as C
    dom = [{'hex': C.lch_to_hex(c['L'], c['C'], c['h']), 'L': round(c['L'], 3), 'C': round(c['C'], 3), 'h': round(c['h'], 1),
            'share': round(c['w'], 3)} for c in clusters]
    face_state, face_info = faces(path)
    light = 'night' if sig['mean_L'] < 0.32 else ('golden' if sig['earth_share'] >= 0.35 and sig['mean_L'] < 0.6 else 'day')
    return {'size': [w, h], 'orientation': 'landscape' if w > h * 1.05 else ('portrait' if h > w * 1.05 else 'square'),
            'phash': phash_mod.phash_image(im), 'signals': sig, 'dominant': dom, 'sharpness': round(sharp, 1),
            'faces': face_state, 'face_info': face_info, 'light_guess': light}
