"""Wedding-first check: how much of a venue's own site is about weddings versus other uses.

The pipeline is wedding-venue-specific for now (factory/INTAKE.md): weddings are the lead offer on every demo, and other
uses (filming, private, corporate events) are secondary lines only when the venue's own site states them. This check
measures whether the site itself supports that framing, over three units:
  pages     each crawled page's own text (site chrome and text repeated on most pages removed) plus its URL path
  headings  each distinct heading on the site (chrome and repeated headings removed)
  reviews   testimonial blocks on the venue's own pages (a block that opens with a quote mark, or any text block on a
            testimonials/reviews page); third-party review sites are never crawled
A unit is `wedding` when it has more wedding terms than other-use terms, `other` when the reverse, `neutral` when it
has neither (or a tie with zero). share = wedding / (wedding + other), neutral units left out.
Verdict: `primary` when every measured share and the overall term share are >= 0.6; `not primary` when the page share
or the term share is below 0.4; else `mixed`. Anything but `primary` is flagged for a human.

  python3 factory/intake/wedding.py <slug>     # re-run on a past intake's page dumps (content/photos/<slug>/_pages)
"""
import collections, json, os, re, sys
from urllib.parse import urlparse

WEDDING_RE = re.compile(r'\b(weddings?|brides?|bridal|grooms?|groomsmen|bridesmaids?|newlyweds?|elop(?:e|ed|ing|ements?)|'
                        r'vows?|vow renewals?|ceremon(?:y|ies)|marr(?:y|ied|iage)|getting married|engage(?:d|ment)|'
                        r'rehearsal dinners?|wedding receptions?|i do)\b', re.I)
OTHER_RE = re.compile(r'\b(corporate|company (?:events?|parties|party|picnics?)|conferences?|meetings?|retreats?|offsites?|'
                      r'quincea[nñ]eras?|quinces?|birthdays?|anniversar(?:y|ies)|graduations?|baby showers?|bar mitzvahs?|'
                      r'bat mitzvahs?|galas?|fundraisers?|banquets?|proms?|reunions?|memorials?|celebrations? of life|'
                      r'film(?:ing|s)?|movies?|television|tv|commercials?|productions?|photo ?shoots?|film shoots?|'
                      r'private (?:events?|parties|party)|holiday parties|concerts?|festivals?)\b', re.I)
REVIEW_PAGE = re.compile(r'testimonial|review|kind-words|love-notes|what-couples-say|praise', re.I)
QUOTE_OPEN = re.compile(r'^\s*["“”\'‘]')
PRIMARY, FLOOR = 0.6, 0.4


def counts(text):
    return len(WEDDING_RE.findall(text or '')), len(OTHER_RE.findall(text or ''))


def classify(w, o):
    return 'wedding' if w > o else ('other' if o > w else ('neutral' if w == 0 else 'tie'))


def share(c):
    d = c['wedding'] + c['other']
    return round(c['wedding'] / d, 2) if d else None


def repeated(pages):
    """Text blocks on at least half the pages (and 3+): footers/sidebars outside <footer>, not the page's own text."""
    c = collections.Counter()
    for pg in pages:
        c.update({b['text'] for b in pg['blocks']})
    need = max(3, (len(pages) + 1) // 2)
    return {t for t, n in c.items() if n >= need}


def check(pages):
    """pages: [{'url', 'blocks': [{'text', 'heading', 'chrome'}]}] (intake's page['info']['blocks'] shape)."""
    boiler = repeated(pages)
    own = lambda b: not b['chrome'] and b['text'] not in boiler
    page_rows, head_rows, review_rows, seen_heads = [], [], [], set()
    total_w = total_o = 0
    other_terms = collections.Counter()
    for pg in pages:
        path = urlparse(pg['url']).path or '/'
        blocks = [b for b in pg['blocks'] if own(b)]
        text = ' '.join(b['text'] for b in blocks)
        w, o = counts(text + ' ' + path.replace('-', ' ').replace('/', ' '))
        total_w, total_o = total_w + w, total_o + o
        other_terms.update(m.lower() for m in OTHER_RE.findall(text))
        page_rows.append({'url': pg['url'], 'wedding_terms': w, 'other_terms': o, 'class': classify(w, o)})
        review_page = bool(REVIEW_PAGE.search(path))
        for b in blocks:
            if b['heading']:
                k = b['text'].strip().lower()
                if k and k not in seen_heads:
                    seen_heads.add(k)
                    hw, ho = counts(b['text'])
                    head_rows.append({'text': b['text'][:100], 'class': classify(hw, ho), 'url': pg['url']})
            if len(b['text']) >= 60 and (QUOTE_OPEN.match(b['text']) or (review_page and not b['heading'])):
                rw, ro = counts(b['text'])
                review_rows.append({'text': b['text'][:100], 'class': classify(rw, ro), 'url': pg['url']})
    out = {'pages': page_rows, 'headings': head_rows, 'reviews': review_rows,
           'terms': {'wedding': total_w, 'other': total_o, 'share': round(total_w / (total_w + total_o), 2) if total_w + total_o else None},
           'other_terms_top': other_terms.most_common(8)}
    shares = {}
    for unit in ('pages', 'headings', 'reviews'):
        c = collections.Counter(r['class'] for r in out[unit])
        out[unit + '_counts'] = dict(c)
        shares[unit] = share(c)
    shares['terms'] = out['terms']['share']
    out['shares'] = shares
    measured = [v for v in shares.values() if v is not None]
    if not measured:
        verdict = 'not primary'
    elif (shares['pages'] is not None and shares['pages'] < FLOOR) or (shares['terms'] is not None and shares['terms'] < FLOOR):
        verdict = 'not primary'
    elif all(v >= PRIMARY for v in measured):
        verdict = 'primary'
    else:
        verdict = 'mixed'
    out['verdict'] = verdict
    out['flag'] = verdict != 'primary'
    return out


def report_md(r):
    pct = lambda v: '-' if v is None else '%d%%' % round(v * 100)
    cnt = lambda unit: ', '.join('%s %d' % kv for kv in sorted(r[unit + '_counts'].items())) or 'none found'
    L = ['## Wedding-first check', '',
         'Weddings are the lead offer on every demo (factory/INTAKE.md). Share = wedding units / (wedding + other-use units).', '',
         '| unit | wedding share | counts |', '|---|---|---|',
         '| pages | %s | %s |' % (pct(r['shares']['pages']), cnt('pages')),
         '| headings | %s | %s |' % (pct(r['shares']['headings']), cnt('headings')),
         '| reviews on the venue\'s own pages | %s | %s |' % (pct(r['shares']['reviews']), cnt('reviews')),
         '| all term mentions | %s | wedding %d, other %d |' % (pct(r['shares']['terms']), r['terms']['wedding'], r['terms']['other']), '',
         '**Verdict: %s.**%s' % (r['verdict'], ' FLAG: weddings are not clearly primary on this site; confirm the venue fits the wedding-first pipeline before building.' if r['flag'] else ''), '']
    if r['other_terms_top']:
        L += ['Other uses the site mentions (candidates for a secondary line only): ' + ', '.join('%s %d' % kv for kv in r['other_terms_top']), '']
    others = [p for p in r['pages'] if p['class'] == 'other']
    if others:
        L += ['Pages led by other uses: ' + ', '.join('%s (w%d/o%d)' % (urlparse(p['url']).path or '/', p['wedding_terms'], p['other_terms']) for p in others), '']
    return L


def pages_from_dump(d):
    """Rebuild the page/blocks shape from intake's _pages/*.txt dumps ('## ' = heading, '[chrome] ' = chrome)."""
    pages = []
    for name in sorted(os.listdir(d)):
        if not name.endswith('.txt'):
            continue
        lines = open(os.path.join(d, name), encoding='utf-8').read().split('\n')
        blocks = []
        for ln in lines[2:]:
            if not ln.strip():
                continue
            h = ln.startswith('## ')
            ln = ln[3:] if h else ln
            c = ln.startswith('[chrome] ')
            blocks.append({'text': ln[9:] if c else ln, 'heading': h, 'chrome': c})
        pages.append({'url': lines[0].strip(), 'blocks': blocks})
    return pages


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        print(__doc__)
        return 2
    here = os.path.dirname(os.path.abspath(__file__))
    d = os.path.join(os.path.dirname(here), 'content', 'photos', argv[0], '_pages')
    if not os.path.isdir(d):
        print('no page dumps at %s (run intake first)' % d)
        return 2
    r = check(pages_from_dump(d))
    print('\n'.join(report_md(r)))
    print(json.dumps({'shares': r['shares'], 'verdict': r['verdict']}))
    return 1 if r['flag'] else 0


if __name__ == '__main__':
    sys.exit(main())
