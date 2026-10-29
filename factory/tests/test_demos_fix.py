"""demos-CHECK fix round: unsolicited disclosure, Insert privacy link, press gating, preview JSON-LD."""
import glob, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
FACTORY = os.path.dirname(HERE)
sys.path.insert(0, FACTORY)
import build  # noqa: E402


def _v(**kw):
    v = json.load(open(os.path.join(FACTORY, 'content', 'stonehurst.json')))
    v.update(kw)
    return v


def test_notice_and_chip_say_unsolicited_and_name_the_venue():
    v = _v()
    assert build.preview_notice(v) == 'An unsolicited concept by Insert, not made by or affiliated with The Stonehurst.'
    chip = build.preview_chip(v)
    assert chip.startswith('Unsolicited concept by Insert') and 'not affiliated with The Stonehurst' in chip
    tpl = open(os.path.join(FACTORY, 'templates', 'base.html.j2')).read()
    assert "partials/preview-notice.j2" in tpl.split('<main', 1)[0]      # before the nav and the hero


def test_no_footer_links_to_hash_and_privacy_is_inserts():
    for f in glob.glob(os.path.join(FACTORY, 'templates', '**', '*.j2'), recursive=True):
        t = open(f).read()
        assert 'href="#"' not in t, f
        if 'Privacy' in t:
            assert '{{ insert_privacy_url }}' in t, f
    assert build.INSERT_PRIVACY_URL == 'https://insert-landing-production.up.railway.app/privacy.html'


def test_press_row_needs_every_outlet_confirmed():
    assert build.confirmed_press(_v(featured_in=['Vogue', 'Zola'])) == []
    ok = {'name': 'Zola', 'source': 'https://example.com', 'confirmed': True}
    assert build.confirmed_press(_v(featured_in=[ok])) == ['Zola']
    assert build.confirmed_press(_v(featured_in=[ok, {'name': 'Vogue', 'source': 'https://example.com'}])) == []
    assert build.confirmed_press(_v(featured_in=[ok, 'Junebug'])) == []
    assert build.confirmed_press(_v(featured_in=[])) == []


def test_private_jsonld_never_claims_the_venue_business():
    v = _v()
    v['preview'] = dict(v['preview'], private=True)
    ld = build.jsonld(v, '')
    d = json.loads(ld.replace('<\\/', '</'))
    assert d['@type'] == 'WebPage' and d['creator']['name'] == 'Insert'
    assert not re.search(r'LocalBusiness|EventVenue|telephone|"email"|"@id"|FAQPage', ld)
    assert v['website'] not in ld and v['contact']['email'] not in ld
    pub = dict(v, preview=dict(v['preview'], private=False))
    assert 'EventVenue' in build.jsonld(pub, '')                          # an engaged (public) site keeps its own graph
