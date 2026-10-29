"""Venue intake: homepage URL -> draft content file + photos + review report.

  python3 factory/intake/intake.py <homepage-url> --slug <slug> [--max-pages 30] [--max-photos 120]

Writes (factory/content/):
  <slug>.draft.json          lib/schema.md shape; unknown fields null; every fact with its source URL; `review` flags
  <slug>.intake-report.md    facts table, photos table, fields needing a human, suggested vibe, dialect shortlist, crawl log
  photos/<slug>/pNN.jpg      largest copy of each distinct photo (gitignored; private use only) + manifest.json
Never guesses: a field the venue's own pages do not state stays null. See factory/INTAKE.md.
"""
import argparse, collections, datetime, io, json, os, re, shutil, sys, time
from urllib.parse import urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
FACTORY = os.path.dirname(HERE)
if sys.path[0] != FACTORY:
    sys.path.insert(0, FACTORY)
from intake import extract as X, photos as PH, crawl as CR, wedding as W  # noqa: E402

MIN_WIDTH = 800
MAX_KEEP_WIDTH = 4000
DUP_BITS = 26          # pHash Hamming distance (of 256) at or below which two downloads are the same photo


def slugify(s):
    return re.sub(r'[^a-z0-9]+', '-', (s or '').lower()).strip('-')[:40] or 'x'


def crawl_site(start, max_pages, fetcher):
    root = CR.normalise(start)
    pages, queue, seen = [], [root], {root.rstrip('/')}
    nav = set()
    first = True
    sm_added = False
    while queue and len(pages) < max_pages:
        url = queue.pop(0)
        st, ct, body, final = fetcher.get(url)
        entry = {'url': url, 'status': st, 'note': ''}
        fetcher.log.append(entry)
        if st != 200 or 'html' not in (ct or '').lower():
            entry['note'] = 'skipped (status %s, %s)' % (st, (ct or '')[:40])
            continue
        if not CR.same_site(final, root):
            entry['note'] = 'redirected off-site to %s' % final
            continue
        html = body.decode('utf-8', 'replace')
        facts, info = X.extract_page(html, url)
        pages.append({'url': url, 'html': html, 'facts': facts, 'info': info})
        entry['note'] = 'ok, %d facts' % len(facts)
        new = []
        for l in info['links']:
            n = CR.normalise(l['url'])
            if n and CR.page_ok(n, root) and n.rstrip('/') not in seen:
                seen.add(n.rstrip('/'))
                new.append(n)
                if first and l['nav']:
                    nav.add(n)
        if first:
            nav.update(new[:25])
        if not sm_added:
            sm_added = True
            for u in CR.sitemap_urls(fetcher, root):
                n = CR.normalise(u)
                if n and CR.page_ok(n, root) and n.rstrip('/') not in seen:
                    seen.add(n.rstrip('/'))
                    new.append(n)
        queue.extend(new)
        queue.sort(key=lambda u: CR.priority(u, nav))
        first = False
    return pages


def dump_pages(pages, d):
    """Each crawled page's text blocks as <d>/_pages/NN-<path>.txt (gitignored, local review aid; never committed)."""
    pd = os.path.join(d, '_pages')
    os.makedirs(pd, exist_ok=True)
    for i, pg in enumerate(pages):
        name = '%02d-%s.txt' % (i + 1, slugify(urlparse(pg['url']).path) if urlparse(pg['url']).path.strip('/') else 'home')
        with open(os.path.join(pd, name), 'w') as f:
            f.write(pg['url'] + '\n\n')
            for b in pg['info']['blocks']:
                f.write(('## ' if b['heading'] else '') + ('[chrome] ' if b['chrome'] else '') + b['text'] + '\n')


def fetch_photos(pages, fetcher, out_dir, max_photos, P, PHASH, log):
    from PIL import Image
    import hashlib
    os.makedirs(out_dir, exist_ok=True)
    # re-runs: previous pNN downloads move to _cache/ keyed by photo key (no second download); curated names survive
    mpath = os.path.join(out_dir, 'manifest.json')
    old = json.load(open(mpath)) if os.path.exists(mpath) else []
    curated = [m for m in old if m.get('named_from')]
    cache_dir = os.path.join(out_dir, '_cache')
    os.makedirs(cache_dir, exist_ok=True)
    ck = lambda key: os.path.join(cache_dir, hashlib.sha1(key.encode()).hexdigest()[:16] + '.jpg')
    for m in old:
        f = os.path.join(out_dir, m['name'] + '.jpg')
        if not m.get('named_from') and m.get('key') and os.path.exists(f):
            os.replace(f, ck(m['key']))
    cands = []
    for pg in pages:
        cands += PH.candidates(X.soup_of(pg['html']), pg['html'], pg['url'])
    groups = PH.group(cands)
    kept, skipped = [], collections.Counter()
    skipped_detail = []
    n = 0
    for key, e in groups.items():
        why = PH.pre_skip(key, e)
        if why:
            skipped[why.split(' ')[0] if 'px' not in why else '< 800 px (stated)'] += 1
            skipped_detail.append((key, why))
            continue
        if n >= max_photos:
            skipped['over --max-photos'] += 1
            continue
        got, native = None, None
        cached = next((m for m in old if m.get('key') == key and not m.get('named_from')), None)
        if cached and os.path.exists(ck(key)):
            im = Image.open(ck(key))
            im.load()
            got, native = (cached['source_url'], im), cached['native']
        for u in ([] if got else PH.try_order(e)[:3]):
            same = CR.same_site(u, pages[0]['url'])
            st, ct, body, final = fetcher.get(u, check_robots=same)
            log.append({'url': u, 'status': st, 'note': 'photo'})
            if st == 200 and body:
                try:
                    im = Image.open(io.BytesIO(body))
                    im.load()
                    got = (u, im)
                    break
                except Exception:
                    continue
        if not got:
            skipped['download failed'] += 1
            skipped_detail.append((key, 'download failed'))
            continue
        u, im = got
        w, h = native or im.size
        if w < MIN_WIDTH:
            skipped['< 800 px (downloaded)'] += 1
            skipped_detail.append((key, '%dx%d < 800 px wide' % (w, h)))
            continue
        n += 1
        rgb = im.convert('RGB')
        keep = rgb
        if w > MAX_KEEP_WIDTH:
            keep = rgb.resize((MAX_KEEP_WIDTH, round(h * MAX_KEEP_WIDTH / w)), Image.LANCZOS)
        ph = PHASH.phash_image(rgb)
        dup = next((k for k in kept if PH.hamming(k['phash'], ph) <= DUP_BITS), None)
        if dup:
            if w * h > dup['native'][0] * dup['native'][1]:   # keep the larger copy under the first name
                keep.save(os.path.join(out_dir, dup['name'] + '.jpg'), quality=92)
                dup.update({'native': [w, h], 'source_url': u, 'kept_copy_size': list(keep.size), 'phash': ph})
            dup['duplicates'].append(u)
            skipped['duplicate (pHash)'] += 1
            continue
        name = 'p%02d' % (len(kept) + 1)
        keep.save(os.path.join(out_dir, name + '.jpg'), quality=92)
        kept.append({'name': name, 'source_url': u, 'source_page': e['pages'][0], 'pages': e['pages'], 'native': [w, h],
                     'crop': [w, h], 'kept_copy': name + '.jpg', 'kept_copy_size': list(keep.size), 'phash': ph,
                     'alt_on_site': e['alt'], 'ctx': e['ctx'][:120], 'key': key, 'duplicates': [],
                     'possible_stock': PH.possible_stock(key)})
    for k in kept:
        path = os.path.join(out_dir, k['name'] + '.jpg')
        a = PH.analyse(path, P, PHASH)
        a['crop'] = k['native']
        k.update({kk: v for kk, v in a.items() if kk not in ('size', 'phash')})
        text = ' '.join([k['alt_on_site'], k['key']])
        k['subject_guess'] = 'people' if a['faces'] == 'faces' else PH.guess_subject(text)
        k['flora_guess'] = PH.guess_flora(text)
    names = {k['name'] for k in kept}
    json.dump(kept + [m for m in curated if m['name'] not in names], open(mpath, 'w'), indent=1)
    shutil.rmtree(cache_dir, ignore_errors=True)
    return kept, skipped, skipped_detail, len(groups)


GENERIC_TITLE = re.compile(r'^(home|about( us)?|contact( us)?|gallery|galleries|faq|blog|pricing|information|info|guests|'
                           r'weddings?|events?|services|testimonials|welcome|sample page|page not found)$', re.I)


def title_name(allf):
    """No structured name and no og:site_name: the <title> segment repeated across most pages, never a generic word."""
    c, src = collections.Counter(), {}
    for f in allf:
        if f['field'] == 'name_hint':
            for part in re.split(r'\s+[|–—-]\s+', f['value']):
                part = part.strip()
                if part and not GENERIC_TITLE.match(part):
                    c[part] += 1
                    src.setdefault(part, f)
    if not c:
        return None
    part = c.most_common(1)[0][0]
    return dict(src[part], value=part, how='most repeated <title> segment')


def boilerplate(pages):
    """Text blocks repeated on at least half the pages (and 3+): site chrome that is not inside nav/header/footer."""
    c = collections.Counter()
    for pg in pages:
        c.update({b['text'] for b in pg['info']['blocks']})
    need = max(3, (len(pages) + 1) // 2)
    return {t for t, n in c.items() if n >= need}


def best(facts, field, prefer=None):
    fs = [f for f in facts if f['field'] == field]
    if not fs:
        return None
    rank = {'high': 0, 'medium': 1, 'low': 2}
    cnt = collections.Counter(json.dumps(f['value'], sort_keys=True) for f in fs)
    fs.sort(key=lambda f: (0 if prefer and prefer(f) else 1, rank[f['confidence']], -cnt[json.dumps(f['value'], sort_keys=True)]))
    return fs[0]


def dedupe(facts, keyf):
    out, seen = [], set()
    for f in facts:
        k = keyf(f)
        if k not in seen:
            seen.add(k)
            out.append(f)
    return out


def suggest_vibe(pages, vibe_words, signal_rows, history_facts):
    counts = collections.Counter()
    tcounts = collections.Counter()
    for pg in pages:
        counts.update(pg['info']['vibe_counts'])
        tcounts.update(pg['info']['type_counts'])
    top_dialects = [r['id'] for r in signal_rows[:3]] if signal_rows else []
    words = sorted([w for w in vibe_words if counts.get(w)], key=lambda w: (-counts[w], 0 if vibe_words[w] in top_dialects else 1, w))[:3]
    vtype = tcounts.most_common(1)[0][0] if tcounts and tcounts.most_common(1)[0][1] else None
    era, era_src = None, None
    for f in history_facts:
        m = re.search(r'\b(built|constructed|completed|erected)\b[^.]{0,30}?\b(1[6-9]\d\d|20[0-2]\d)\b', f['value'], re.I)
        if m:
            era, era_src = int(m.group(2)), f['source']
            break
    return {'type': vtype, 'era': era, 'era_source': era_src, 'words': words,
            'evidence': {w: counts[w] for w in words}, 'type_evidence': dict(tcounts.most_common(4))}


def score(draft, kept, photo_dir, P, PERS, dialects_doc, registry):
    """Mirror build.py: lead + next three photos -> signals; derive() meta; score with and without the vibe block."""
    usable = [k for k in kept if k['subject_guess'] != 'people' and not k['possible_stock']] or kept
    if not usable:
        return None
    lead = max(usable, key=lambda k: (k['orientation'] == 'landscape', k['native'][0] * k['native'][1]))
    others = sorted([k for k in usable if k is not lead], key=lambda k: -k['sharpness'])[:3]
    paths = {k['name']: os.path.join(photo_dir, k['name'] + '.jpg') for k in [lead] + others}
    signals = P.photo_signals(paths, lead['name'])
    p = {a: 50.0 for a in PERS.AXES}
    _, _, meta = P.derive(paths, p, lead=lead['name'])
    _, rows_sig = PERS.score_dialects(dialects_doc, signals, {}, meta, registry)
    _, rows = PERS.score_dialects(dialects_doc, signals, draft, meta, registry)
    return {'lead': lead['name'], 'palette_photos': list(paths), 'signals': {k: v for k, v in signals.items() if k != 'per_photo'},
            'signals_only': rows_sig, 'with_vibe': rows}


def build_draft(slug, url, pages, kept, vibe, photo_rel):
    allf = [f for pg in pages for f in pg['facts']]
    host = urlparse(url).netloc.replace('www.', '')
    review = []
    name_f = best(allf, 'name')
    if not name_f:
        og = [f for f in allf if f['field'] == 'name_hint' and f['how'] == 'og:site_name']
        name_f = best(og, 'name_hint') if og else title_name(allf)
    name = None
    if name_f:
        name = re.split(r'\s+[|–—-]\s+', name_f['value'])[0].strip()
        if name_f['field'] == 'name_hint' or name != name_f['value']:
            review.append({'field': 'name', 'reason': 'from %s "%s" (trimmed at the first separator); confirm the venue name' % (name_f['how'], name_f['value'][:80])})
    email_f = best(allf, 'email', prefer=lambda f: f['value'].endswith('@' + host))
    phone_f = best(allf, 'phone')
    addr_f = best(allf, 'address')
    parts = (addr_f or {}).get('parts') or {}
    caps = sorted([f for f in allf if f['field'] == 'capacity'], key=lambda f: -f['value'])
    uses_c = collections.Counter()
    uses_src = {}
    for f in allf:
        if f['field'] == 'use':
            uses_c[f['value']] += f.get('count', 1)
            uses_src.setdefault(f['value'], f['source'])
    uses = [u for u, _ in uses_c.most_common(4)]
    # wedding-first pipeline: Weddings always lead when the site says weddings at all; other uses are secondary lines
    if uses_c.get('Weddings'):
        uses = ['Weddings'] + [u for u, _ in uses_c.most_common() if u != 'Weddings'][:3]
    socials = dedupe([f for f in allf if f['field'] == 'social'], lambda f: f['value']['url'].lower())
    tools = dedupe([f for f in allf if f['field'] == 'tool'], lambda f: f['value']['name'])
    faq_f = dedupe([f for f in allf if f['field'] == 'faq'], lambda f: f['value']['q'].lower())
    boiler = boilerplate(pages)
    for f in faq_f:   # an answer that ran into a theme footer (not a <footer>) is cut where the repeated block starts
        a = f['value']['a']
        cut = min([a.find(b) for b in boiler if len(b) >= 20 and a.find(b) > 0] or [len(a)])
        f['value'] = dict(f['value'], a=a[:cut].strip())
    space_f = dedupe([f for f in allf if f['field'] == 'space'], lambda f: f['value']['name'].lower())
    hist = dedupe([f for f in allf if f['field'] == 'history'], lambda f: f['value'][:80])
    feat = dedupe([f for f in allf if f['field'] == 'featured'], lambda f: json.dumps(f['value'], sort_keys=True))
    rules = dedupe([f for f in allf if f['field'] == 'rule'], lambda f: f['value'])
    prices = dedupe([f for f in allf if f['field'] == 'price'], lambda f: f['value'])
    hours = dedupe([f for f in allf if f['field'] == 'hours'], lambda f: f['value'])
    metad = best(allf, 'meta_description')

    def src(f):
        return f['source'] if f else None
    ledger = []
    for f in [name_f, email_f, phone_f, addr_f, metad] + caps[:5] + rules + prices + hours:
        if f:
            ledger.append({'id': '%s-%d' % (f['field'], len(ledger) + 1), 'text': f['value'] if isinstance(f['value'], str) else json.dumps(f['value']),
                           'source': f['source'], 'confidence': f['confidence'], 'how': f['how'], 'review': True})
    spaces = []
    for f in space_f:
        v = f['value']
        cs = v['capacities']
        cap = cs[0]['n'] if len(cs) == 1 else None
        spaces.append({'id': slugify(v['name']), 'name': v['name'], 'photo': None, 'capacity': cap,
                       'capacity_label': ('Up to %d' % cap) if cap and 'up to' in cs[0]['phrase'].lower() else None,
                       'capacity_kind': None, 'use': None, 'blurb': None, 'features': [], 'journey_step': None,
                       'source': f['source'], '_excerpt': v['excerpt'][:240], '_capacities_stated': [c['phrase'] for c in cs],
                       '_confidence': f['confidence']})
    if spaces:
        review.append({'field': 'spaces', 'reason': '%d candidate spaces from headings; keep only real spaces, write use/blurb as short paraphrases, assign photos' % len(spaces)})
    else:
        review.append({'field': 'spaces', 'reason': 'no spaces detected; add them by hand from the site'})
    items = {}
    for k in kept:
        items[k['name']] = {'alt': k['alt_on_site'] or None, 'caption': None, 'focal': '50% 50%', 'light': k['light_guess'],
                            'tags': [], 'subject': k['subject_guess'] if k['subject_guess'] != 'unknown' else None,
                            'flora': k['flora_guess'], '_faces': k['faces'], '_possible_stock': k['possible_stock'],
                            '_source_page': k['source_page']}
    review.append({'field': 'photos.items', 'reason': 'choose 8-14, rename (curate.py), write alt + caption from what is shown, confirm subject/light; never a people photo as lead'})
    for fld, val in (('contact.email', email_f), ('contact.phone', phone_f), ('contact.address_line', addr_f)):
        if not val:
            review.append({'field': fld, 'reason': 'not stated on any crawled page; leave null unless found by hand'})
    review.append({'field': 'tagline_facts.region', 'reason': 'county/region is never inferred; fill only if the site states it'})
    if not caps:
        review.append({'field': 'tagline_facts.max_guests', 'reason': 'no capacity stated; leave null'})
    else:
        review.append({'field': 'tagline_facts.max_guests', 'reason': 'largest stated figure %d ("%s"); confirm it is the venue maximum' % (caps[0]['value'], caps[0]['phrase'])})
    review.append({'field': 'tagline_facts.uses', 'reason': 'wedding-first: Weddings leads (uses[0] is the headline offer); keep other uses only as secondary lines the site itself states%s' % ('' if uses_c.get('Weddings') else '. NO wedding wording found on any page')})
    review.append({'field': 'copy_overrides', 'reason': 'write hero_kicker / hero_headline / hero_lede and spaces_title as wedding-first lines from stated facts; never lead with filming, corporate or private events'})
    review.append({'field': 'story', 'reason': 'write lead + paragraphs as short paraphrases of the history excerpts (never copy)'})
    review.append({'field': 'vibe', 'reason': 'suggested from word counts; a human confirms the three words'})
    draft = {
        '$schema': '../lib/schema.md', 'slug': slug, 'name': name, 'short_name': name, 'legal_name': None,
        'tagline_facts': {'locality': parts.get('locality'), 'region': None, 'state': parts.get('state'), 'acres': None,
                          'space_count': len(spaces) or None, 'max_guests': caps[0]['value'] if caps else None,
                          'events_per_day': None, 'uses': uses},
        'vibe': {'type': vibe['type'], 'era': vibe['era'], 'words': vibe['words'], 'era_source': vibe['era_source'],
                 '_note': 'SUGGESTED by intake from word counts on the site (%s); a human must confirm' % vibe['evidence']},
        'website': url,
        'contact': {'email': email_f['value'] if email_f else None, 'email_note': None,
                    'phone': phone_f['value'] if phone_f else None, 'phone_note': None,
                    'address_line': addr_f['value'] if addr_f else None, 'address_note': None,
                    'hours': hours[0]['value'] if hours else None, 'source': src(addr_f) or src(email_f) or src(phone_f)},
        'facts': ledger,
        'story': {'kicker': None, 'lead': None, 'paragraphs': [], 'credit': None, 'timeline': [], 'photo': None, 'source': src(hist[0]) if hist else None},
        'numbers': [],
        'spaces': spaces,
        'journey': {'note': None, 'steps': []},
        'day': {'source': None},
        'faqs': [{'q': f['value']['q'], 'a': f['value']['a'], 'source': f['source'], '_confidence': f['confidence']} for f in faq_f],
        'featured_in': [],
        'photos': {'source_dir': photo_rel, 'manifest': photo_rel + '/manifest.json', 'credit': ('photography © %s' % name) if name else None, 'items': items},
        'preview': {'private': True, 'disclaimer': 'Unsolicited concept by Insert · photography © %s · not affiliated with %s' % (name or slug, name or slug),
                    'meta_description': None},
        'review': review,
        '_intake': {'crawled_at': datetime.datetime.now().isoformat(timespec='seconds'), 'start_url': url,
                    'pages': [p['url'] for p in pages], 'meta_description': metad['value'] if metad else None,
                    'socials': [f['value'] for f in socials], 'tools': [f['value'] for f in tools],
                    'history_excerpts': [{'text': f['value'][:300], 'years': f.get('years'), 'source': f['source']} for f in hist[:12]],
                    'featured_raw': [dict(f['value'], source=f['source']) for f in feat[:10]],
                    'uses_sources': uses_src, 'capacities': [{'n': f['value'], 'phrase': f['phrase'], 'source': f['source']} for f in caps[:12]],
                    'jsonld_types': sorted({t for p in pages for d in p['info']['jsonld'] for t in X._types(d)})},
    }
    return draft, {'socials': socials, 'tools': tools, 'faqs': faq_f, 'spaces': space_f, 'history': hist, 'featured': feat,
                   'rules': rules, 'prices': prices, 'hours': hours, 'caps': caps, 'name': name_f, 'email': email_f,
                   'phone': phone_f, 'address': addr_f, 'meta': metad}


def _c(s, n=140):
    s = s if isinstance(s, str) else json.dumps(s, ensure_ascii=False)
    s = re.sub(r'\s+', ' ', s).replace('|', '\\|')
    return s if len(s) <= n else s[:n - 1] + '…'


def score_table_md(rows, n=8):
    out = ['| dialect | score | reasons |', '|---|---|---|']
    for r in rows[:n]:
        out.append('| %s | %d | %s |' % (r['id'], r['score'], _c('; '.join('%s (+%d)' % (w, p) for w, p in r['reasons']) or '-', 220)))
    return out


def report(slug, url, draft, F, kept, skipped, skipped_detail, ngroups, sc, vibe, log, timings, fetcher, wf=None):
    L = ['# Intake report: %s' % (draft['name'] or slug), '',
         'Start URL: %s · crawled %s · %d pages · %d requests · %d distinct images seen, %d photos kept' %
         (url, draft['_intake']['crawled_at'], len(draft['_intake']['pages']), fetcher.requests, ngroups, len(kept)), '',
         'Timings (automated): ' + ', '.join('%s %.0fs' % kv for kv in timings.items()), '',
         'Everything below was extracted from the pages listed in the crawl log. Nothing is inferred. `confidence` is how the',
         'value was found (structured data / link = high, pattern on page = medium, heading heuristics = low).', '']
    if wf:
        L += W.report_md(wf)
    L += ['## Facts', '', '| field | value | source | confidence | how |', '|---|---|---|---|---|']
    rows = []
    for k in ('name', 'email', 'phone', 'address', 'meta'):
        if F[k]:
            rows.append(F[k])
    rows += F['socials'] + F['tools'] + [dict(f, value='%d — "%s"' % (f['value'], f['phrase'])) for f in F['caps'][:10]]
    rows += F['hours'] + F['prices'] + F['rules'][:20] + F['featured'][:8]
    rows += [dict(f, value='%s → %s' % (f['value']['name'], f['value']['excerpt'][:80])) for f in F['spaces']]
    rows += [dict(f, value='Q: %s' % f['value']['q']) for f in F['faqs']]
    rows += [dict(f, value=f['value'][:120]) for f in F['history'][:10]]
    for f in rows:
        L.append('| %s | %s | %s | %s | %s |' % (f['field'], _c(f['value']), f['source'], f['confidence'], _c(f['how'], 40)))
    L += ['', '## Photos (%d kept)' % len(kept), '',
          'Signals are lib/palette.py photo_signal() values. faces: OpenCV Haar result, or `unchecked` when OpenCV is not installed.', '',
          '| name | size | orient | subject? | faces | sharp | L | foliage | earth | dark | water | mono | dominant | stock? | alt on site | page |',
          '|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|']
    for k in kept:
        s = k['signals']
        L.append('| %s | %dx%d | %s | %s | %s | %.0f | %.2f | %.2f | %.2f | %.2f | %.2f | %.2f | %s | %s | %s | %s |' % (
            k['name'], k['native'][0], k['native'][1], k['orientation'][0], k['subject_guess'], k['faces'], k['sharpness'],
            s['mean_L'], s['foliage_share'], s['earth_share'], s['dark_share'], s['water_share'], s['mono_share'],
            ' '.join(d['hex'] for d in k['dominant']), 'yes' if k['possible_stock'] else '', _c(k['alt_on_site'], 50), urlparse(k['source_page']).path))
    L += ['', 'Discarded: ' + (', '.join('%s %d' % kv for kv in skipped.most_common()) or 'none'), '']
    if skipped_detail:
        L += ['<details><summary>Discarded detail</summary>', '']
        L += ['- %s: %s' % (_c(k, 90), why) for k, why in skipped_detail[:80]]
        L += ['', '</details>', '']
    L += ['## Needs a human', '']
    L += ['- **%s**: %s' % (r['field'], r['reason']) for r in draft['review']]
    L += ['', '## Suggested vibe (confirm)', '',
          '- type: `%s` (word counts %s)' % (vibe['type'], vibe['type_evidence']),
          '- words: %s (counts %s)' % (', '.join('`%s`' % w for w in vibe['words']), vibe['evidence']),
          '- era: %s%s' % (vibe['era'], (' (%s)' % vibe['era_source']) if vibe['era_source'] else ' (no "built in YYYY" sentence found)'), '']
    L += ['## Dialect shortlist (lib/personality.score_dialects)', '']
    if sc:
        L += ['Palette photos (as build.py): lead `%s` + %s. Signals: %s' % (sc['lead'], ', '.join(sc['palette_photos'][1:]), _c(sc['signals'], 300)), '',
              '**Photos only:**', ''] + score_table_md(sc['signals_only'], 4) + ['', '**Photos + suggested vibe:**', ''] + score_table_md(sc['with_vibe'], 4)
        L += ['', 'Shortlist: ' + ', '.join('%s (%d)' % (r['id'], r['score']) for r in sc['with_vibe'][:3])]
    else:
        L += ['No usable photos: scorer not run.']
    L += ['', '## Crawl log', '', '| # | url | status | note |', '|---|---|---|---|']
    for i, e in enumerate([e for e in log if e.get('note') != 'photo']):
        L.append('| %d | %s | %s | %s |' % (i + 1, _c(e['url'], 110), e['status'], _c(e.get('note', ''), 60)))
    nph = [e for e in log if e.get('note') == 'photo']
    L += ['', 'Photo requests: %d (%d failed)' % (len(nph), sum(1 for e in nph if e['status'] != 200)), '']
    return '\n'.join(L) + '\n'


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('url')
    ap.add_argument('--slug', required=True)
    ap.add_argument('--max-pages', type=int, default=30)
    ap.add_argument('--max-photos', type=int, default=120)
    ap.add_argument('--out', default=os.path.join(FACTORY, 'content'))
    a = ap.parse_args(argv)
    from lib import palette as P, personality as PERS, phash as PHASH
    dialects_doc = json.load(open(os.path.join(FACTORY, 'data', 'dialects.json')))
    registry = json.load(open(os.path.join(FACTORY, 'data', 'registry.json')))
    timings = collections.OrderedDict()
    log = []
    fetcher = CR.Fetcher(log=log)
    t = time.time()
    pages = crawl_site(a.url, a.max_pages, fetcher)
    timings['crawl'] = time.time() - t
    if not pages:
        print('intake: no pages fetched from %s (see log)' % a.url)
        for e in log[-5:]:
            print('  ', e)
        return 2
    print('crawl: %d pages in %.0fs' % (len(pages), timings['crawl']))
    t = time.time()
    photo_rel = 'photos/' + a.slug
    photo_dir = os.path.join(a.out, photo_rel)
    dump_pages(pages, photo_dir)
    kept, skipped, skipped_detail, ngroups = fetch_photos(pages, fetcher, photo_dir, a.max_photos, P, PHASH, log)
    timings['photos'] = time.time() - t
    print('photos: %d kept of %d distinct in %.0fs (%s)' % (len(kept), ngroups, timings['photos'], dict(skipped)))
    t = time.time()
    allf = [f for pg in pages for f in pg['facts']]
    pre = None
    try:
        pre = score({}, kept, photo_dir, P, PERS, dialects_doc, registry)
    except Exception as e:  # scorer problems never block the draft
        print('scorer (signals only) failed:', e)
    vibe = suggest_vibe(pages, dialects_doc['vibe_words'], pre['signals_only'] if pre else [], [f for f in allf if f['field'] == 'history'])
    draft, F = build_draft(a.slug, CR.normalise(a.url), pages, kept, vibe, photo_rel)
    wf = W.check([{'url': pg['url'], 'blocks': pg['info']['blocks']} for pg in pages])
    draft['_intake']['wedding_first'] = {'verdict': wf['verdict'], 'shares': wf['shares'], 'other_terms_top': wf['other_terms_top']}
    if wf['flag']:
        draft['review'].insert(0, {'field': 'wedding_first', 'reason': 'FLAG: weddings are %s on this site (shares %s); confirm the venue fits the wedding-first pipeline before building' % (wf['verdict'], wf['shares'])})
    sc = None
    try:
        sc = score(draft, kept, photo_dir, P, PERS, dialects_doc, registry)
    except Exception as e:
        print('scorer failed:', e)
    timings['extract+score'] = time.time() - t
    draft['_intake']['dialect_shortlist'] = [{'id': r['id'], 'score': r['score']} for r in (sc['with_vibe'][:3] if sc else [])]
    draft['_intake']['timings_s'] = {k: round(v, 1) for k, v in timings.items()}
    dpath = os.path.join(a.out, a.slug + '.draft.json')
    json.dump(draft, open(dpath, 'w'), indent=1, ensure_ascii=False)
    rpath = os.path.join(a.out, a.slug + '.intake-report.md')
    open(rpath, 'w').write(report(a.slug, a.url, draft, F, kept, skipped, skipped_detail, ngroups, sc, vibe, log, timings, fetcher, wf))
    from lib import schema as S
    errs, warns = S.validate_content(draft, dialects_doc['vibe_words'])
    print('draft: %s (%d schema errors, %d warnings; drafts are expected to need review)' % (os.path.relpath(dpath), len(errs), len(warns)))
    print('report: %s' % os.path.relpath(rpath))
    print('wedding-first: %s %s%s' % (wf['verdict'], wf['shares'], '  <- FLAG' if wf['flag'] else ''))
    if sc:
        print('dialect shortlist: ' + ', '.join('%s %d' % (r['id'], r['score']) for r in sc['with_vibe'][:3]))
    print('total automated: %.0fs, %d requests' % (sum(timings.values()), fetcher.requests))
    return 0


if __name__ == '__main__':
    sys.exit(main())
