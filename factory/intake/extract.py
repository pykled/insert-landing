"""Pure HTML -> stated facts. No network. Every fact is a dict:
   {'field', 'value', 'source', 'confidence': high|medium|low, 'how'}
and is only produced when the page itself states it. Nothing here guesses a value."""
import json, re
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup, Comment

BLOCK_TAGS = {'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'dt', 'dd', 'td', 'th', 'summary', 'blockquote',
              'figcaption', 'div', 'section', 'article', 'header', 'footer', 'main', 'aside', 'address', 'button', 'label'}
SKIP_TAGS = {'script', 'style', 'noscript', 'template', 'svg', 'head', 'iframe', 'select', 'option', 'title'}
HEADING_CLASS = re.compile(r'(title|heading|headline)', re.I)
EMAIL_RE = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b')
EMAIL_JUNK = re.compile(r'\.(png|jpe?g|gif|webp|svg)$|@(sentry|wixpress|example|domain|email|yourdomain|yoursite|godaddy)\.', re.I)
PHONE_RE = re.compile(r'(?<![\d/])\(?\b(\d{3})\)?[-.\s]{0,2}(\d{3})[-.\s](\d{4})\b(?![\d/])')
STREET = r'(?:Road|Rd|Street|St|Avenue|Ave|Boulevard|Blvd|Drive|Dr|Lane|Ln|Way|Highway|Hwy|Place|Pl|Court|Ct|Parkway|Pkwy|Circle|Cir|Trail|Trl|Canyon)'
ADDRESS_RE = re.compile(r'\b(\d{2,6}\s+(?:[NSEW]\.?\s+)?[A-Z][\w.\' ]{1,40}?\s' + STREET + r'\.?(?:\s*(?:#|Suite|Ste\.?|Unit)\s*\w+)?)\s*,?\s*'
                        r'([A-Z][A-Za-z .]{1,30}?)\s*,\s*(CA|California|[A-Z]{2})\.?\s+(\d{5})\b')
SOCIAL = {'instagram.com': 'instagram', 'facebook.com': 'facebook', 'pinterest.com': 'pinterest', 'tiktok.com': 'tiktok',
          'youtube.com': 'youtube', 'theknot.com': 'theknot', 'weddingwire.com': 'weddingwire', 'twitter.com': 'x', 'x.com': 'x',
          'yelp.com': 'yelp', 'linkedin.com': 'linkedin', 'vimeo.com': 'vimeo'}
TOOLS = [  # (name, kind, regex over raw HTML)
    ('HoneyBook', 'crm', r'honeybook\.com|hb-widget|hbcdn|HoneyBook'),
    ('Dubsado', 'crm', r'dubsado\.com'),
    ('Calendly', 'scheduling', r'calendly\.com'),
    ('Acuity', 'scheduling', r'acuityscheduling\.com|as\.me/'),
    ('Planning Pod', 'crm', r'planningpod\.com'),
    ('Tripleseat', 'crm', r'tripleseat\.com'),
    ('Aisle Planner', 'crm', r'aisleplanner\.com'),
    ('17hats', 'crm', r'17hats\.com'),
    ('Tave', 'crm', r'tave\.com|tave\.io'),
    ('Typeform', 'forms', r'typeform\.com'),
    ('Jotform', 'forms', r'jotform\.com'),
    ('Wix', 'builder', r'static\.wixstatic\.com|wix\.com/|X-Wix'),
    ('Squarespace', 'builder', r'static1\.squarespace\.com|squarespace\.com'),
    ('Showit', 'builder', r'static\.showit\.co|showit\.com'),
    ('WordPress', 'builder', r'/wp-content/|/wp-includes/'),
    ('Webflow', 'builder', r'webflow\.(com|io)|data-wf-page'),
    ('GoDaddy Website Builder', 'builder', r'img1\.wsimg\.com|godaddy'),
    ('Weebly', 'builder', r'weebly\.com|editmysite\.com'),
    ('Google Analytics', 'analytics', r'googletagmanager\.com|google-analytics\.com'),
    ('Meta Pixel', 'analytics', r'connect\.facebook\.net|facebook\.com/tr\?'),
]
SPACE_NOUNS = re.compile(r'\b(garden|gardens|barn|hall|room|terrace|lawn|courtyard|ballroom|patio|pavilion|chapel|greenhouse|'
                         r'suite|library|parlou?r|grove|meadow|deck|loft|veranda|porch|orchard|vineyard|cellar|gazebo|'
                         r'conservatory|salon|lounge|bridal|groom|cottage|house|manor|estate|field|arbor|pergola|fountain|'
                         r'pond|lake|knoll|overlook|hill|tent|atrium|foyer|dining)s?\b', re.I)
CAPACITY_RE = re.compile(r'(?:up to|accommodat\w*|seats?|seating(?: for)?|capacity(?: of| for)?|holds?|hosts?|max(?:imum)?(?: capacity)?(?: of)?)'
                         r'\s*(?:up to\s*)?(?:approximately\s*|about\s*)?(\d{2,4})\s*(\+|plus)?\s*(guests|people|persons|seated|standing|attendees|cocktail)?'
                         r'|(\d{2,4})\s*(\+|plus)?\s*(guests|people|persons|seated|attendees)\b', re.I)
PRICE_RE = re.compile(r'\$\s?\d[\d,]*(?:\.\d\d)?(?:\s?[kK])?')
RULE_RE = re.compile(r'\b(must|required|requires?|not permitted|not allowed|prohibited|no outside|in-house|exclusive(?:ly)?|curfew|'
                     r'end by|minimum|approved vendors?|preferred vendors?|insurance|deposit|security guards?|amplified|noise|'
                     r'sparklers?|confetti|smoking|pets?|dogs?|alcohol|bartender|catering|caterers?)\b', re.I)
HOURS_RE = re.compile(r'\b(?:(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)[a-z]*\.?\s*(?:[-–to]+\s*(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)[a-z]*\.?)?\s*:?\s*'
                      r'\d{1,2}(?::\d\d)?\s*(?:am|pm|a\.m\.|p\.m\.)|by appointment(?: only)?|office hours?|tours? (?:are )?(?:available|by))', re.I)
HISTORY_RE = re.compile(r'\b(18\d\d|19\d\d|20[0-2]\d)\b')
HISTORY_WORDS = re.compile(r'\b(built|founded|established|constructed|history|historic|original(?:ly)?|family|since|generations?|'
                           r'restored|heritage|homestead|century)\b', re.I)
FEATURED_RE = re.compile(r'\b(as (?:featured|seen) (?:in|on)|featured (?:in|on)|awards?|best of|couples\'? choice|winner|voted)\b', re.I)
USES = [('Weddings', r'\bweddings?\b'), ('Elopements', r'\belop(?:e|ement)s?\b'), ('Receptions', r'\breceptions?\b'),
        ('Ceremonies', r'\bceremon(?:y|ies)\b'), ('Corporate events', r'\bcorporate\b'), ('Quinceañeras', r'\bquincea[nñ]eras?\b'),
        ('Showers', r'\b(?:bridal|baby) showers?\b'), ('Celebrations of life', r'\bcelebrations? of life\b|\bmemorials?\b'),
        ('Filming', r'\bfilm(?:ing)?\b|\bphoto ?shoots?\b'), ('Private events', r'\bprivate (?:events?|parties|party)\b'),
        ('Birthdays', r'\bbirthdays?\b'), ('Retreats', r'\bretreats?\b'), ('Rehearsal dinners', r'\brehearsal dinners?\b'),
        ('Galas', r'\bgalas?\b'), ('Anniversaries', r'\banniversar(?:y|ies)\b'), ('Vow renewals', r'\bvow renewals?\b')]
VENUE_TYPES = ['estate', 'mansion', 'castle', 'villa', 'hacienda', 'barn', 'ranch', 'vineyard', 'garden', 'glasshouse', 'coastal',
               'lake', 'desert', 'resort', 'hotel', 'loft', 'clubhouse', 'theatre']
TYPE_WORDS = {'glasshouse': r'\b(greenhouse|glasshouse|conservatory)\b', 'theatre': r'\b(theatre|theater)\b',
              'coastal': r'\b(ocean|beach|coastal|seaside)\b', 'garden': r'\bgardens?\b', 'ranch': r'\branch(?:es)?\b|\bfarm\b',
              'barn': r'\bbarns?\b', 'estate': r'\bestates?\b', 'mansion': r'\bmansions?\b', 'vineyard': r'\b(vineyards?|winery)\b'}
# vibe words (data/dialects.json vibe_words) and what on a page counts as the venue stating them
VIBE_EVIDENCE = {
    'heritage': r'\b(historic(?:al)?|heritage|landmark|registry|18\d\d|19[0-4]\d)\b', 'grand': r'\b(grand|grandeur|majestic|stately)\b',
    'formal': r'\b(formal|elegan(?:t|ce)|black[- ]tie|refined)\b', 'romantic': r'\b(romantic|romance)\b',
    'soft': r'\b(soft|airy|delicate)\b', 'floral': r'\b(floral|blooms?|flowers?|roses?)\b', 'editorial': r'\b(editorial)\b',
    'evening': r'\b(evening|night|starlit|starry|twinkl\w*)\b', 'candlelit': r'\b(candle\w*)\b', 'moody': r'\b(moody|intimate)\b',
    'brass': r'\b(brass)\b', 'minimal': r'\b(minimal\w*|clean lines)\b', 'architectural': r'\b(architect\w*)\b',
    'serene': r'\b(serene|serenity|peaceful|tranquil\w*|quiet)\b', 'modern': r'\b(modern|contemporary)\b',
    'bright': r'\b(bright|light-filled|sunlit|natural light)\b', 'breezy': r'\b(breez\w*)\b', 'water': r'\b(water|lake|pond|ocean|fountain|creek)\b',
    'nautical': r'\b(nautical|marina|yacht)\b', 'lush': r'\b(lush)\b', 'garden': r'\b(gardens?)\b', 'green': r'\b(green(?:ery)?)\b',
    'dappled': r'\b(shade|shaded|canopy|dappled)\b', 'rustic': r'\b(rustic|barn|farm\w*|ranch|homestead)\b',
    'land': r'\b(acres?|land|countryside|mountains?|meadows?|orchards?)\b', 'golden': r'\b(golden|sunset|golden hour)\b',
    'timber': r'\b(wood(?:en)?|timber|oak beams?)\b', 'glam': r'\b(glam\w*)\b', 'period': r'\b(victorian|craftsman|edwardian|art deco|period)\b',
    'graphic': r'\b(graphic)\b', 'monochrome': r'\b(monochrom\w*|black and white)\b'}


def soup_of(html):
    return BeautifulSoup(html, 'html.parser')


def _norm(s):
    return re.sub(r'\s+', ' ', s or '').strip()


def text_blocks(soup):
    """Document-order list of {'tag','text','heading','chrome'}: strings grouped by their nearest block ancestor.
    chrome = inside nav/header/footer (kept for contact details, skipped for content facts)."""
    out, cur, cur_el = [], [], None

    def flush():
        if cur_el is not None and cur:
            t = _norm(' '.join(cur))
            if t:
                tag = cur_el.name
                heading = tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6') or bool(HEADING_CLASS.search(' '.join(cur_el.get('class') or [])))
                chrome = any(p.name in ('nav', 'header', 'footer') for p in cur_el.parents) or tag in ('nav', 'header', 'footer')
                out.append({'tag': tag, 'text': t, 'heading': heading, 'chrome': chrome})
    for s in soup.find_all(string=True):
        if isinstance(s, Comment) or not s.strip():
            continue
        par = s.parent
        if par is None or any(p.name in SKIP_TAGS for p in [par] + list(par.parents)):
            continue
        el = par
        while el is not None and el.name not in BLOCK_TAGS and el.name != '[document]':
            el = el.parent
        if el is not cur_el:
            flush()
            cur, cur_el = [], el
        cur.append(str(s))
    flush()
    return out


def sentences(text):
    return [x.strip() for x in re.split(r'(?<=[.!?])\s+(?=[A-Z"“(])', text) if x.strip()]


def jsonld(soup):
    out = []
    for tag in soup.find_all('script', type=re.compile('ld\\+json', re.I)):
        try:
            data = json.loads(tag.string or tag.get_text() or 'null')
        except (ValueError, TypeError):
            continue
        stack = data if isinstance(data, list) else [data]
        while stack:
            d = stack.pop(0)
            if isinstance(d, dict):
                if '@graph' in d:
                    stack.extend(d['@graph'] if isinstance(d['@graph'], list) else [d['@graph']])
                out.append(d)
            elif isinstance(d, list):
                stack.extend(d)
    return out


def _types(d):
    t = d.get('@type')
    return [x.lower() for x in (t if isinstance(t, list) else [t]) if isinstance(x, str)]


BUSINESS_TYPES = ('localbusiness', 'eventvenue', 'organization', 'place', 'weddingvenue', 'lodgingbusiness', 'touristattraction',
                  'restaurant', 'store', 'professionalservice', 'homeandconstructionbusiness')


def meta_tags(soup):
    m = {}
    t = soup.find('title')
    m['title'] = _norm(t.get_text()) if t else None
    for k in ('description', 'og:description', 'og:site_name', 'og:title', 'og:image', 'twitter:image', 'robots'):
        tag = soup.find('meta', attrs={'name': k}) or soup.find('meta', attrs={'property': k})
        m[k] = _norm(tag.get('content')) if tag and tag.get('content') else None
    return m


def links(soup, base):
    out = []
    for a in soup.find_all('a', href=True):
        href = a['href'].strip()
        if href.startswith(('javascript:', '#')):
            continue
        u = urljoin(base, href)
        nav = any(p.name in ('nav', 'header') for p in a.parents)
        out.append({'url': u, 'text': _norm(a.get_text()), 'nav': nav, 'raw': href})
    return out


def F(field, value, source, confidence, how, **kw):
    d = {'field': field, 'value': value, 'source': source, 'confidence': confidence, 'how': how}
    d.update(kw)
    return d


def fmt_phone(a, b, c):
    return '(%s) %s-%s' % (a, b, c)


def contacts(soup, blocks, url, lks):
    facts = []
    for l in lks:
        r = l['raw']
        if r.lower().startswith('mailto:'):
            e = r[7:].split('?')[0].strip()
            if EMAIL_RE.fullmatch(e) and not EMAIL_JUNK.search(e):
                facts.append(F('email', e.lower(), url, 'high', 'mailto link'))
        elif r.lower().startswith('tel:'):
            d = re.sub(r'\D', '', r[4:])
            if len(d) == 11 and d[0] == '1':
                d = d[1:]
            if len(d) == 10:
                facts.append(F('phone', fmt_phone(d[:3], d[3:6], d[6:]), url, 'high', 'tel link'))
    text = ' \n '.join(b['text'] for b in blocks)
    for e in EMAIL_RE.findall(text):
        if not EMAIL_JUNK.search(e):
            facts.append(F('email', e.lower(), url, 'medium', 'printed on page'))
    for m in PHONE_RE.finditer(text):
        facts.append(F('phone', fmt_phone(*m.groups()), url, 'medium', 'printed on page'))
    for b in blocks:
        for m in ADDRESS_RE.finditer(b['text']):
            street, city, state, z = m.groups()
            state = 'CA' if state == 'California' else state
            facts.append(F('address', '%s, %s, %s %s' % (_norm(street), _norm(city), state, z), url, 'medium', 'printed address',
                           parts={'street': _norm(street), 'locality': _norm(city), 'state': state, 'postal': z}))
    for l in lks:
        host = urlparse(l['url']).netloc.lower().replace('www.', '')
        for dom, name in SOCIAL.items():
            if host == dom or host.endswith('.' + dom):
                path = urlparse(l['url']).path.rstrip('/')
                if path and not re.search(r'/(sharer|share|intent|tr|dialog|plugins)\b', path):
                    facts.append(F('social', {'network': name, 'url': l['url'].split('?')[0].rstrip('/')}, url, 'high', 'link'))
    return facts


def ld_facts(lds, url):
    facts = []
    for d in lds:
        types = _types(d)
        if not any(t in BUSINESS_TYPES for t in types):
            if 'faqpage' in types:
                for q in d.get('mainEntity') or []:
                    if isinstance(q, dict) and q.get('name'):
                        a = (q.get('acceptedAnswer') or {}).get('text') if isinstance(q.get('acceptedAnswer'), dict) else None
                        if a:
                            facts.append(F('faq', {'q': _norm(q['name']), 'a': _norm(BeautifulSoup(a, 'html.parser').get_text(' '))}, url, 'high', 'JSON-LD FAQPage'))
            continue
        how = 'JSON-LD %s' % '/'.join(types)
        if d.get('name'):
            facts.append(F('name', _norm(d['name']), url, 'high', how))
        if d.get('telephone'):
            dg = re.sub(r'\D', '', d['telephone'])[-10:]
            if len(dg) == 10:
                facts.append(F('phone', fmt_phone(dg[:3], dg[3:6], dg[6:]), url, 'high', how))
        if d.get('email'):
            facts.append(F('email', d['email'].replace('mailto:', '').lower(), url, 'high', how))
        a = d.get('address')
        if isinstance(a, dict) and (a.get('streetAddress') or a.get('addressLocality')):
            parts = {'street': a.get('streetAddress'), 'locality': a.get('addressLocality'), 'state': a.get('addressRegion'),
                     'postal': a.get('postalCode')}
            facts.append(F('address', ', '.join(x for x in (parts['street'], parts['locality'], ' '.join(y for y in (parts['state'], parts['postal']) if y)) if x),
                           url, 'high', how, parts=parts))
        for k in ('description', 'priceRange', 'openingHours', 'maximumAttendeeCapacity', 'foundingDate', 'sameAs', 'url'):
            if d.get(k):
                facts.append(F('ld_' + k, d[k], url, 'high', how))
    return facts


def faqs(soup, blocks, url, page_hint=''):
    out = []
    for det in soup.find_all('details'):
        s = det.find('summary')
        if s:
            q = _norm(s.get_text())
            a = _norm(det.get_text(' ').replace(s.get_text(' '), '', 1))
            if q and a:
                out.append(F('faq', {'q': q, 'a': a[:700]}, url, 'high', '<details> block'))
    if out:
        return out
    qs = [i for i, b in enumerate(blocks) if not b['chrome'] and b['text'].endswith('?') and 10 <= len(b['text']) <= 200]
    if len(qs) < 3 and not re.search(r'faq|question|info|detail|pricing|package', page_hint, re.I):
        return out
    for n, i in enumerate(qs):
        end = qs[n + 1] if n + 1 < len(qs) else len(blocks)
        ans = []
        for b in blocks[i + 1:end]:
            if b['chrome'] or (b['heading'] and ans):
                break
            ans.append(b['text'])
            if sum(len(x) for x in ans) > 700:
                break
        a = _norm(' '.join(ans))[:700]
        if a and not a.endswith('?'):
            out.append(F('faq', {'q': blocks[i]['text'], 'a': a}, url, 'medium', 'question block + following text'))
    return out


def capacity_mentions(text):
    out = []
    for m in CAPACITY_RE.finditer(text):
        n = int(m.group(1) or m.group(4))
        unit = (m.group(3) or m.group(6) or '').lower()
        kw = m.group(0).lower()
        if not unit and not re.search(r'capacity|seat|accommodat|up to|max', kw):
            continue
        if 10 <= n <= 5000:
            out.append({'n': n, 'phrase': _norm(m.group(0)), 'plus': bool(m.group(2) or m.group(5))})
    return out


def spaces(blocks, url):
    out, seen = [], set()
    for i, b in enumerate(blocks):
        if b['chrome'] or not b['heading'] or len(b['text']) > 60 or not SPACE_NOUNS.search(b['text']):
            continue
        name = b['text'].strip(' :-–')
        key = name.lower()
        if key in seen or name.endswith('?'):
            continue
        desc = []
        for nb in blocks[i + 1:i + 6]:
            if nb['heading'] or nb['chrome']:
                break
            desc.append(nb['text'])
        text = _norm(' '.join(desc))
        caps = capacity_mentions(text)
        if not text:
            continue
        seen.add(key)
        out.append(F('space', {'name': name, 'excerpt': text[:400], 'capacities': caps}, url, 'medium' if caps else 'low',
                     'heading with a space noun + following text'))
    return out


def _sent_facts(blocks, url, rx, field, limit, maxlen=240):
    out = []
    for b in blocks:
        if b['chrome'] or b['heading']:
            continue
        for s in sentences(b['text']):
            if rx.search(s) and 15 <= len(s) <= maxlen:
                out.append(F(field, s, url, 'medium', 'sentence match'))
                if len(out) >= limit:
                    return out
    return out


def history(blocks, url, page_hint=''):
    out = []
    about_page = bool(re.search(r'about|history|story|heritage|our-', page_hint, re.I))
    for b in blocks:
        if b['chrome'] or b['heading'] or len(b['text']) < 120:
            continue
        yr = HISTORY_RE.search(b['text'])
        words = HISTORY_WORDS.search(b['text'])
        if (yr and words) or (about_page and words):
            out.append(F('history', b['text'][:600], url, 'medium' if yr else 'low', 'history paragraph (paraphrase before use)',
                         years=sorted(set(HISTORY_RE.findall(b['text'])))))
    return out


def featured(soup, blocks, url):
    out = []
    for i, b in enumerate(blocks):
        if b['chrome'] or len(b['text']) > 90 or not FEATURED_RE.search(b['text']):
            continue
        names = []
        for nb in blocks[i + 1:i + 14]:
            if nb['heading'] or len(nb['text']) > 60:
                break
            names.append(nb['text'])
        out.append(F('featured', {'heading': b['text'], 'names': names}, url, 'low', 'featured/awards block text'))
    for img in soup.find_all('img'):
        alt = _norm(img.get('alt'))
        ctx = ' '.join(img.get('class') or []) + ' ' + (img.get('src') or '')
        if alt and re.search(r'award|badge|featured|as seen|couples.?choice|best of', alt + ' ' + ctx, re.I):
            out.append(F('featured', {'heading': 'image alt', 'names': [alt]}, url, 'low', 'award/badge image alt text'))
    return out


def tools(raw_html, url):
    out = []
    for name, kind, rx in TOOLS:
        m = re.search(rx, raw_html)
        if m:
            out.append(F('tool', {'name': name, 'kind': kind, 'evidence': m.group(0)[:60]}, url, 'high', 'signature in page HTML'))
    return out


def uses(blocks, url):
    text = ' '.join(b['text'] for b in blocks if not b['chrome'])
    out = []
    for label, rx in USES:
        n = len(re.findall(rx, text, re.I))
        if n:
            out.append(F('use', label, url, 'medium', 'word on page', count=n))
    return out


def word_counts(blocks, table):
    text = ' '.join(b['text'] for b in blocks if not b['chrome'])
    return {k: len(re.findall(rx, text, re.I)) for k, rx in table.items()}


def extract_page(html, url):
    """All facts one page states. Returns (facts, info) with info = {'title','meta','links','blocks','jsonld'}."""
    soup = soup_of(html)
    blocks = text_blocks(soup)
    meta = meta_tags(soup)
    lks = links(soup, url)
    lds = jsonld(soup)
    hint = url + ' ' + (meta.get('title') or '')
    facts = []
    facts += ld_facts(lds, url)
    facts += contacts(soup, blocks, url, lks)
    facts += faqs(soup, blocks, url, hint)
    facts += spaces(blocks, url)
    facts += _sent_facts(blocks, url, PRICE_RE, 'price', 15)
    facts += _sent_facts(blocks, url, RULE_RE, 'rule', 20)
    facts += _sent_facts(blocks, url, HOURS_RE, 'hours', 6)
    for b in blocks:
        if not b['chrome']:
            for c in capacity_mentions(b['text']):
                facts.append(F('capacity', c['n'], url, 'medium', 'capacity phrase', phrase=c['phrase'], context=b['text'][:200]))
    facts += history(blocks, url, hint)
    facts += featured(soup, blocks, url)
    facts += tools(html, url)
    facts += uses(blocks, url)
    if meta.get('description') or meta.get('og:description'):
        facts.append(F('meta_description', meta.get('description') or meta.get('og:description'), url, 'high', 'meta tag'))
    for k in ('og:site_name', 'og:title'):
        if meta.get(k):
            facts.append(F('name_hint', meta[k], url, 'low', k))
    if meta.get('title'):
        facts.append(F('name_hint', meta['title'], url, 'low', '<title>'))
    return facts, {'title': meta.get('title'), 'meta': meta, 'links': lks, 'blocks': blocks, 'jsonld': lds,
                   'vibe_counts': word_counts(blocks, VIBE_EVIDENCE), 'type_counts': word_counts(blocks, TYPE_WORDS)}
