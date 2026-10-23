"""factory/intake: extraction, photo candidates, crawl filters, draft shape. Offline: fixtures + a fake fetcher, and any
real network call fails the test.  python3 -m pytest -q factory/tests/test_intake.py"""
import io, json, os, urllib.request
import pytest
from tests import _util  # noqa: F401  (puts factory/ on sys.path)
from intake import extract as X, photos as PH, crawl as CR, intake as I
from lib import schema as S, palette as P, phash as PHASH

FX = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures', 'intake')
ROOT = 'https://example-venue.test/'


def fx(name):
    return open(os.path.join(FX, name), encoding='utf-8').read()


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def boom(*a, **k):
        raise AssertionError('test tried to use the network')
    monkeypatch.setattr(urllib.request, 'urlopen', boom)


def facts_of(name, url):
    return X.extract_page(fx(name), url)


def field(facts, f):
    return [x for x in facts if x['field'] == f]


def test_contacts_jsonld_links_and_address():
    facts, info = facts_of('home.html', ROOT)
    assert {'Willow Test Farm'} == {f['value'] for f in field(facts, 'name')}
    phones = {f['value'] for f in field(facts, 'phone')}
    assert phones == {'(555) 010-0199'}
    assert any(f['how'] == 'tel link' for f in field(facts, 'phone'))
    assert {f['value'] for f in field(facts, 'email')} == {'hello@willowtestfarm.test'}
    addr = [f for f in field(facts, 'address') if f['confidence'] == 'high'][0]
    assert addr['parts'] == {'street': '100 Test Orchard Rd', 'locality': 'Testville', 'state': 'CA', 'postal': '90000'}
    assert any(f['how'] == 'printed address' for f in field(facts, 'address'))
    socials = [f['value'] for f in field(facts, 'social')]
    assert socials == [{'network': 'instagram', 'url': 'https://www.instagram.com/willowtestfarm'}]  # sharer link dropped
    assert all(f['source'] == ROOT for f in facts)


def test_tools_featured_uses_meta():
    facts, _ = facts_of('home.html', ROOT)
    tools = {f['value']['name'] for f in field(facts, 'tool')}
    assert {'HoneyBook', 'WordPress'} <= tools and 'Wix' in tools   # wix media URL in the page
    feat = field(facts, 'featured')[0]['value']
    assert feat['names'] == ['Test Weddings Magazine', 'Example Bride Blog']
    uses = {f['value'] for f in field(facts, 'use')}
    assert {'Weddings', 'Receptions', 'Private events'} <= uses
    assert field(facts, 'meta_description')[0]['value'].startswith('A synthetic test venue')
    assert max(f['value'] for f in field(facts, 'capacity')) == 180


def test_nothing_guessed_when_absent():
    facts, _ = facts_of('faq.html', ROOT + 'faq/')
    for f in ('phone', 'email', 'address', 'name', 'capacity', 'social', 'history'):
        assert field(facts, f) == [], f


def test_faq_details_and_question_blocks():
    facts, _ = facts_of('faq.html', ROOT + 'faq/')
    q = [f['value'] for f in field(facts, 'faq')]
    assert q[0] == {'q': 'Do you allow outside catering?', 'a': 'No. Catering is provided by our in-house kitchen only.'}
    assert len(q) == 2 and all(f['confidence'] == 'high' for f in field(facts, 'faq'))
    assert any('$4,500' in f['value'] for f in field(facts, 'price'))
    facts2, _ = facts_of('questions.html', ROOT + 'info/')
    q2 = [f['value'] for f in field(facts2, 'faq')]
    assert [x['q'] for x in q2] == ['Is there parking on site?', 'Can we bring our dog?', 'Is there a rain plan?']
    assert q2[2]['a'] == 'The barn serves as the rain plan.'


def test_spaces_history_hours_rules():
    facts, _ = facts_of('about.html', ROOT + 'about/')
    sp = {f['value']['name']: f['value'] for f in field(facts, 'space')}
    assert set(sp) == {'The Orchard Lawn', 'The Red Barn'}
    assert [c['n'] for c in sp['The Orchard Lawn']['capacities']] == [180]
    assert [c['n'] for c in sp['The Red Barn']['capacities']] == [150]
    hist = field(facts, 'history')
    assert hist and hist[0]['years'] == ['1911']
    assert any('appointment' in f['value'] for f in field(facts, 'hours'))
    rules, _ = facts_of('faq.html', ROOT + 'faq/')
    assert any(f['value'] == 'Amplified music must end by 10 PM.' for f in field(rules, 'rule'))
    vibe = I.suggest_vibe([{'info': X.extract_page(fx('about.html'), ROOT)[1]}], {'heritage': 'estate', 'rustic': 'ranch', 'timber': 'ranch'}, [], hist)
    assert vibe['era'] == 1911 and vibe['era_source'] == ROOT + 'about/'


def test_photo_candidates_grouped_largest_first():
    soup = X.soup_of(fx('home.html'))
    groups = PH.group(PH.candidates(soup, fx('home.html'), ROOT))
    barn = groups['example-venue.test/wp-content/uploads/2024/01/barn-at-dusk.jpg']
    assert barn['urls'][0] == ('https://example-venue.test/wp-content/uploads/2024/01/barn-at-dusk-2048x1365.jpg', 2048)
    assert barn['alt'] == 'The red barn at dusk'
    assert PH.try_order(barn)[0] == 'https://example-venue.test/wp-content/uploads/2024/01/barn-at-dusk.jpg'   # WP original first
    show = groups['static.showit.co/v2/1/abc/photo-one.jpg']
    assert PH.try_order(show)[0] == 'https://static.showit.co/v2/1/abc/photo-one.jpg/variant/3200/webp'
    wix = groups['static.wixstatic.com/media/aa11_bb22~mv2.jpg']
    assert PH.try_order(wix)[0] == 'https://static.wixstatic.com/media/aa11_bb22~mv2.jpg'
    assert 'example-venue.test/wp-content/uploads/2024/01/lawn-full.jpg' in groups          # lightbox link
    assert 'example-venue.test/wp-content/uploads/2024/01/hero-bg.jpg' in groups            # CSS background
    assert 'example-venue.test/wp-content/uploads/2024/01/og-share.jpg' in groups           # og:image
    logo = groups['example-venue.test/wp-content/uploads/2024/01/logo.png']
    assert PH.pre_skip('example-venue.test/wp-content/uploads/2024/01/logo.png', logo)
    assert PH.pre_skip('example-venue.test/wp-content/uploads/2024/01/barn-at-dusk.jpg', barn) is None


def test_photo_guesses_and_stock_flag():
    assert PH.guess_subject('bride and groom under the oak') == 'people'
    assert PH.guess_subject('The red barn at dusk') == 'building'
    assert PH.guess_subject('IMG_2041') == 'unknown'
    assert PH.guess_flora('olive grove') == 'olive'
    assert PH.possible_stock('x.test/wp-content/uploads/2024/03/interior-romantic-restaurant-modern-design-classic-style-1.webp')
    assert not PH.possible_stock('x.test/wp-content/uploads/2024/05/ceremony2.jpg')


def test_crawl_filters():
    assert CR.registrable('www.Example-Venue.test') == 'example-venue.test'
    assert CR.registrable('shop.venue.co.uk') == 'venue.co.uk'
    assert CR.page_ok('https://www.example-venue.test/faq/#q1', ROOT)
    for bad in ('https://example-venue.test/brochure.pdf', 'https://example-venue.test/wp-admin/', 'https://other.test/x',
                'https://example-venue.test/tag/barn/', 'https://example-venue.test/blog/page/2/'):
        assert not CR.page_ok(bad, ROOT), bad
    nav = {'https://example-venue.test/faq'}
    order = sorted(['https://example-venue.test/blog/a-wedding', 'https://example-venue.test/about', 'https://example-venue.test/faq'],
                   key=lambda u: CR.priority(u, nav))
    assert order == ['https://example-venue.test/faq', 'https://example-venue.test/about', 'https://example-venue.test/blog/a-wedding']


class FakeFetcher:
    """Serves fixtures/generated images; records calls like CR.Fetcher."""
    def __init__(self, routes):
        self.routes, self.log, self.requests, self.calls = routes, [], 0, []

    def sitemaps(self, root):
        return [ROOT + 'sitemap_index.xml']

    def get(self, url, check_robots=True):
        self.requests += 1
        self.calls.append(url)
        r = self.routes.get(url.rstrip('/')) or self.routes.get(url)
        if r is None:
            return 404, '', b'', url
        ct, body = r
        return 200, ct, body, url


def _jpeg(w, h, seed):
    from PIL import Image
    import numpy as np
    rng = np.random.RandomState(seed)
    arr = (rng.rand(h // 8, w // 8, 3) * 255).astype('uint8')
    im = Image.fromarray(arr).resize((w, h), Image.BILINEAR)
    b = io.BytesIO()
    im.save(b, 'JPEG', quality=85)
    return b.getvalue()


def test_sitemap_index_pages_before_posts():
    f = FakeFetcher({ROOT + 'sitemap_index.xml': ('application/xml', fx('sitemap_index.xml').encode()),
                     'https://example-venue.test/page-sitemap.xml': ('application/xml', fx('page_sitemap.xml').encode())})
    urls = CR.sitemap_urls(f, ROOT)
    assert urls == ['https://example-venue.test/about/', 'https://example-venue.test/faq/']
    assert f.calls.index('https://example-venue.test/page-sitemap.xml') < f.calls.index('https://example-venue.test/post-sitemap.xml')


def test_crawl_and_photos_end_to_end(tmp_path):
    big = _jpeg(1600, 1067, 1)
    routes = {
        'https://example-venue.test': ('text/html', fx('home.html').encode()),
        'https://example-venue.test/faq': ('text/html', fx('faq.html').encode()),
        'https://example-venue.test/about': ('text/html', fx('about.html').encode()),
        'https://example-venue.test/spaces': ('text/html', fx('questions.html').encode()),
        ROOT + 'sitemap_index.xml': ('application/xml', fx('sitemap_index.xml').encode()),
        'https://example-venue.test/page-sitemap.xml': ('application/xml', fx('page_sitemap.xml').encode()),
        'https://example-venue.test/wp-content/uploads/2024/01/barn-at-dusk.jpg': ('image/jpeg', big),
        'https://static.showit.co/v2/1/abc/photo-one.jpg/variant/3200/webp': ('image/jpeg', _jpeg(2000, 1333, 2)),
        'https://example-venue.test/wp-content/uploads/2024/01/lawn-full.jpg': ('image/jpeg', big),          # same photo again
        'https://example-venue.test/wp-content/uploads/2024/01/hero-bg.jpg': ('image/jpeg', _jpeg(640, 427, 3)),  # too small
    }
    f = FakeFetcher(routes)
    pages = I.crawl_site(ROOT, 10, f)
    urls = [p['url'] for p in pages]
    assert urls[0] == ROOT and 'https://example-venue.test/faq/' in urls and len(urls) == 4
    assert not any(u.endswith('.pdf') or 'portal' in u for u in f.calls)
    kept, skipped, detail, n = I.fetch_photos(pages, f, str(tmp_path / 'ph'), 20, P, PHASH, f.log)
    assert [k['native'] for k in kept] == [[1600, 1067], [2000, 1333]]
    assert skipped['duplicate (pHash)'] == 1 and skipped['< 800 px (downloaded)'] == 1
    assert kept[0]['duplicates'] and set(kept[0]['signals']) >= {'mean_L', 'foliage_share', 'earth_share', 'dark_share', 'water_share', 'mono_share'}
    assert kept[0]['faces'] in ('unchecked', 'none', 'faces')
    man = json.load(open(str(tmp_path / 'ph' / 'manifest.json')))
    assert {m['name'] for m in man} == {'p01', 'p02'} and all(os.path.exists(str(tmp_path / 'ph' / (m['name'] + '.jpg'))) for m in man)
    vibe = I.suggest_vibe(pages, {'rustic': 'ranch', 'heritage': 'estate', 'garden': 'botanical', 'timber': 'ranch'}, [], [])
    draft, F = I.build_draft('willow', ROOT, pages, kept, vibe, 'photos/willow')
    errs, _ = S.validate_content(draft)
    assert not [e for e in errs if 'missing top-level' in e]
    assert draft['contact']['phone'] == '(555) 010-0199' and draft['tagline_facts']['locality'] == 'Testville'
    assert draft['tagline_facts']['region'] is None and draft['legal_name'] is None
    assert draft['tagline_facts']['max_guests'] == 180
    assert all(fct['source'].startswith(ROOT) for fct in draft['facts'])
    assert all(s['source'] for s in draft['spaces']) and all(q['source'] for q in draft['faqs'])
    assert draft['preview']['private'] is True and any(r['field'] == 'vibe' for r in draft['review'])
    assert draft['story']['paragraphs'] == []   # history is never copied into rendered slots


def test_rerun_reuses_downloads_and_keeps_curated_names(tmp_path):
    routes = {'https://example-venue.test/wp-content/uploads/2024/01/barn-at-dusk.jpg': ('image/jpeg', _jpeg(1600, 1067, 1)),
              'https://static.showit.co/v2/1/abc/photo-one.jpg/variant/3200/webp': ('image/jpeg', _jpeg(2000, 1333, 2))}
    page = {'url': ROOT, 'html': fx('home.html'), 'facts': [], 'info': X.extract_page(fx('home.html'), ROOT)[1]}
    d = str(tmp_path / 'ph')
    f1 = FakeFetcher(routes)
    I.fetch_photos([page], f1, d, 20, P, PHASH, f1.log)
    man = json.load(open(os.path.join(d, 'manifest.json')))
    named = dict(man[0], name='barn', kept_copy='barn.jpg', named_from=man[0]['name'])
    json.dump(man + [named], open(os.path.join(d, 'manifest.json'), 'w'))
    open(os.path.join(d, 'barn.jpg'), 'wb').write(open(os.path.join(d, man[0]['name'] + '.jpg'), 'rb').read())
    f2 = FakeFetcher(routes)
    kept, _, _, _ = I.fetch_photos([page], f2, d, 20, P, PHASH, f2.log)
    assert not [c for c in f2.calls if c in routes]                       # nothing downloaded twice
    assert [k['native'] for k in kept] == [[1600, 1067], [2000, 1333]]
    man2 = json.load(open(os.path.join(d, 'manifest.json')))
    assert 'barn' in {m['name'] for m in man2} and os.path.exists(os.path.join(d, 'barn.jpg'))
    assert not os.path.exists(os.path.join(d, '_cache'))


def test_faq_answer_cut_at_repeated_theme_footer():
    footer = '<div class="ft"><p>Serving the whole valley with weddings since 1978, call us any time.</p></div>'
    q = '<h3>Can we use the lawn?</h3><p>No.</p>' + footer
    other = '<h3>A</h3><p>x</p>' + footer
    pages = []
    for i, body in enumerate([q, other, other]):
        html = '<html><head><title>FAQ</title></head><body>%s</body></html>' % body
        facts, info = X.extract_page(html, ROOT + 'faq%d/' % i)
        pages.append({'url': ROOT + 'faq%d/' % i, 'html': html, 'facts': facts, 'info': info})
    pages[0]['facts'].append(X.F('faq', {'q': 'Can we use the lawn?', 'a': 'No. Serving the whole valley with weddings since 1978, call us any time.'}, ROOT, 'medium', 't'))
    vibe = {'type': None, 'era': None, 'era_source': None, 'words': [], 'evidence': {}, 'type_evidence': {}}
    draft, _ = I.build_draft('t', ROOT, pages, [], vibe, 'photos/t')
    assert [f['a'] for f in draft['faqs'] if f['q'] == 'Can we use the lawn?'] == ['No.']


def _wf_pages(bodies):
    out = []
    for path, body in bodies:
        html = '<html><head><title>T</title></head><body>%s</body></html>' % body
        out.append({'url': ROOT + path, 'blocks': X.extract_page(html, ROOT + path)[1]['blocks']})
    return out


def test_wedding_first_primary_and_flag():
    from intake import wedding as W
    wed = _wf_pages([('', '<h1>Garden weddings</h1><p>Your wedding ceremony on the lawn, then the reception.</p>'),
                     ('weddings/', '<h2>Ceremonies</h2><p>Vows under the oak for the bride and groom.</p>'),
                     ('testimonials/', '<p>"We got married here and our wedding day was perfect, thank you all so much."</p>'),
                     ('film/', '<h2>Filming</h2><p>Film shoots and photo shoots by arrangement.</p>')])
    r = W.check(wed)
    assert r['verdict'] == 'primary' and not r['flag']
    assert r['shares']['pages'] == 0.75 and r['shares']['reviews'] == 1.0
    corp = _wf_pages([('', '<h1>Meetings and retreats</h1><p>Corporate offsites, conferences and galas.</p>'),
                      ('events/', '<h2>Private events</h2><p>Birthdays, fundraisers and holiday parties.</p>'),
                      ('weddings/', '<h2>Weddings</h2><p>We also host the occasional wedding.</p>')])
    r2 = W.check(corp)
    assert r2['verdict'] == 'not primary' and r2['flag']
    assert '## Wedding-first check' in W.report_md(r2)[0]


def test_draft_puts_weddings_first():
    html = '<html><body><p>Corporate events, corporate retreats, corporate meetings and corporate dinners. We host weddings.</p></body></html>'
    facts, info = X.extract_page(html, ROOT)
    vibe = {'type': None, 'era': None, 'era_source': None, 'words': [], 'evidence': {}, 'type_evidence': {}}
    draft, _ = I.build_draft('t', ROOT, [{'url': ROOT, 'html': html, 'facts': facts, 'info': info}], [], vibe, 'photos/t')
    assert draft['tagline_facts']['uses'][0] == 'Weddings'
