"""Spec 05 section 5 exclusions on small fixture snapshots (the dict qa.py collects with lib/exclusions.COLLECT_JS).

Each test builds a clean page, checks it passes, then breaks exactly one thing and checks the right E-number fires.
Runs under pytest, as `python3 -m tests.test_exclusions`, and as `python3 qa.py --self-test`.
"""
import copy
from tests import _util
from lib import exclusions as EX

CONTENT = {'tagline_facts': {'max_guests': 200, 'acres': 9, 'space_count': 6}, 'photos': {'items': {'hero': {'subject': 'grounds'}, 'couple': {'subject': 'people'}}},
           'story': {'timeline': [{'year': '1907'}]}}
META = {'lead': 'hero', 'dialect': {'id': 'botanical'}, 'choices': {'ornament': 'leaf-rule'}, 'personality': {'density': 50, 'voice': 30},
        'pairing': {'display': {'family': 'Cardo', 'weight': 400, 'has_opsz': False, 'vars': None}}, 'axis_tokens': {}, 'fingerprint': {'hero_framing': 'inset'}}


def T(text, tag='p', **kw):
    t = {'tag': tag, 'cls': '', 'text': text, 'len': len(text), 'size': 18.0, 'weight': 400, 'family': 'Nunito Sans', 'transform': 'none', 'ls': 0.0,
         'lh': 28.0, 'h': 28.0, 'top': 1200, 'w': 600, 'on_photo': False, 'in_main': True, 'in_hero': False, 'kicker': False, 'excluded': False}
    t.update(kw)
    return t


def clean():
    return {
        'viewport': {'w': 1440, 'h': 900}, 'paper': 'rgb(250, 250, 246)', 'html_bg': 'rgba(0, 0, 0, 0)',
        'text': [T('Nine acres of garden in Shadow Hills, for up to 200 guests.', 'h1', size=56, weight=400, family='Cardo', top=300, in_hero=True),
                 T('A walled garden estate with six spaces and one wedding a day, kept by the same family.', h=56.0)],
        'fills': [{'tag': 'a', 'cls': 'btn', 'bg': 'rgb(70, 90, 60)', 'area': 2000, 'ornament': None}],
        'overlays': [{'name': 'div.scrim', 'bg': 'rgba(0, 0, 0, 0)', 'bgimage': 'linear-gradient(rgba(0, 0, 0, 0), rgba(0, 0, 0, 0.3))', 'opacity': 1}],
        'gradients': [{'name': 'div.scrim', 'bgimage': 'linear-gradient(rgba(0, 0, 0, 0), rgba(0, 0, 0, 0.3))', 'over_image': True, 'ornament': None, 'opacity': 1}],
        'shadows': [{'name': 'div.card', 'shadow': 'rgba(0, 0, 0, 0.24) 0px 14px 34px -24px'}], 'fixed': [], 'iframes': [], 'videos': [],
        'ornaments': [{'id': 'leaf-rule', 'body': False, 'tag': 'span'}, {'id': 'leaf-rule', 'body': False, 'tag': 'span'}],
        'sections': ['.hero', 'spaces', 'story', 'day', 'tour', 'guide', 'faq', 'uses'],
        'hero': {'cls': 'hero hero-frame', 'slider_hits': [], 'autoplay': [], 'imgs': 1, 'framing': 'inset'},
        'nav': {'links': 6, 'labels': ['Spaces', 'Pricing'], 'nested': 0, 'dropdowns': 0, 'pricing': True},
        'carousels': [], 'learn_more_rows': 0, 'first_screen_text': 'Nine acres of garden in Shadow Hills, for up to 200 guests. Pricing', 'facts_marked': [],
        'badges_first_screen': [], 'press': None, 'dialogs': 0,
    }


def fires(page, rule, meta=META, content=CONTENT, html=''):
    probs, warns, summary = EX.run_all(page, meta, content, html, dialect_mode=True)
    return [p for p in probs if p.startswith(rule + ' ')]


def test_clean_page_passes():
    probs, warns, summary = EX.run_all(clean(), META, CONTENT, '', dialect_mode=True)
    assert probs == [], probs


def test_pre_dialect_mode_only_warns():
    pg = clean(); pg['paper'] = 'rgb(255, 255, 255)'
    probs, warns, _ = EX.run_all(pg, META, CONTENT, '', dialect_mode=False)
    assert probs == [] and any(w.startswith('[pre-dialect] E1') for w in warns)


def test_e1_white_paper_and_saturated_fill():
    pg = clean(); pg['paper'] = 'rgb(255, 255, 255)'
    assert fires(pg, 'E1')
    pg = clean(); pg['fills'].append({'tag': 'a', 'cls': 'btn', 'bg': 'rgb(255, 80, 0)', 'area': 3000, 'ornament': None})
    assert fires(pg, 'E1')
    deco = dict(META, dialect={'id': 'deco'})
    assert not fires(pg, 'E1', meta=deco)


def test_e2_weights():
    pg = clean(); pg['text'].append(T('Thin', 'span', weight=200))
    assert fires(pg, 'E2')
    pg = clean(); pg['text'][0]['weight'] = 300; pg['text'][0]['on_photo'] = True
    assert fires(pg, 'E2')
    m = copy.deepcopy(META); m['pairing']['display'].update({'has_opsz': True, 'vars': None})
    assert fires(clean(), 'E2', meta=m)


def test_e3_e4_families():
    assert fires(clean(), 'E3', html='<link href="https://fonts.googleapis.com/css2?family=Great+Vibes&display=swap">')
    pg = clean(); pg['text'][1]['family'] = 'Montserrat'
    assert fires(pg, 'E4')
    assert fires(clean(), 'E4', html='<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400&display=swap">')


def test_e5_tracked_caps():
    pg = clean(); pg['text'].append(T('A' * 30 + ' ' + 'B' * 35, 'p', transform='uppercase', ls=2.0, size=14))
    assert fires(pg, 'E5')
    pg = clean(); pg['text'].append(T('SHORT TRACKED KICKER', 'p', transform='uppercase', ls=2.0, size=14))
    assert not fires(pg, 'E5')


def test_e6_lead_subject():
    assert fires(clean(), 'E6', meta=dict(META, lead='couple'))


def test_e7_badges_and_press():
    pg = clean(); pg['badges_first_screen'] = ['Best of Weddings 2024 badge.png']
    assert fires(pg, 'E7')
    pg = clean(); pg['first_screen_text'] += ' Rated 5 stars'
    assert fires(pg, 'E7')
    pg = clean(); pg['press'] = {'top': 3000, 'imgs': []}; pg['sections'] = ['.hero', 'featured', 'spaces', 'story', 'tour']
    assert fires(pg, 'E7')


def test_e8_sliders():
    pg = clean(); pg['hero']['slider_hits'] = [' swiper-container']
    assert fires(pg, 'E8')
    pg = clean(); pg['hero']['autoplay'] = ['6000']
    assert fires(pg, 'E8')
    pg = clean(); pg['carousels'] = ['div.cards']
    assert fires(pg, 'E8')
    pg = clean(); pg['learn_more_rows'] = 3
    assert fires(pg, 'E8')


def test_e9_scrims():
    pg = clean(); pg['overlays'] = [{'name': 'div.wash', 'bg': 'rgba(0, 0, 0, 0.5)', 'bgimage': 'none', 'opacity': 1}]
    assert fires(pg, 'E9')
    pg = clean(); pg['overlays'] = [{'name': 'div.scrim', 'bg': 'rgba(0, 0, 0, 0)', 'bgimage': 'linear-gradient(rgba(0, 0, 0, 0), rgba(0, 0, 0, 0.6))', 'opacity': 1}]
    assert fires(pg, 'E9')
    pg = clean(); pg['overlays'] = [{'name': 'div.scrim', 'bg': 'rgba(0, 0, 0, 0)', 'bgimage': 'linear-gradient(rgba(255, 255, 255, 0), rgba(255, 255, 255, 0.4))', 'opacity': 1}]
    assert fires(pg, 'E9')


def test_e10_popups():
    pg = clean(); pg['dialogs'] = 1
    assert fires(pg, 'E10')
    pg = clean(); pg['fixed'] = [{'name': 'named:div.newsletter-modal', 'area': 100, 'position': 'static', 'named': True}]
    assert fires(pg, 'E10')
    pg = clean(); pg['fixed'] = [{'name': 'div.promo', 'area': 1440 * 80, 'position': 'fixed'}]
    assert fires(pg, 'E10')
    assert fires(clean(), 'E10', html='<script>Notification.requestPermission()</script>')


def test_e11_dividers_textures_shadows_gradients():
    pg = clean(); pg['shadows'].append({'name': 'svg.wave-divider', 'wave': True})
    assert fires(pg, 'E11')
    pg = clean(); pg['shadows'].append({'name': 'div.card', 'shadow': 'rgba(0, 0, 0, 0.3) 0px 30px 60px -10px'})
    assert fires(pg, 'E11')
    pg = clean(); pg['gradients'].append({'name': 'section.band', 'bgimage': 'linear-gradient(rgb(240, 230, 210), rgb(200, 180, 150))', 'over_image': False, 'ornament': None, 'opacity': 1})
    assert fires(pg, 'E11')
    pg = clean(); pg['gradients'].append({'name': 'div.wash', 'bgimage': 'radial-gradient(rgba(100, 140, 90, 0.06), rgba(100, 140, 90, 0))', 'over_image': False, 'ornament': None, 'opacity': 1})
    assert not fires(pg, 'E11')                                   # the botanical wash at <= 8% is allowed
    pg = clean(); pg['gradients'].append({'name': 'body', 'bgimage': 'url("img/parchment.jpg")', 'url': True, 'over_image': False, 'ornament': None, 'opacity': 1})
    assert fires(pg, 'E11')


def test_e12_video():
    pg = clean(); pg['iframes'] = ['https://www.youtube.com/embed/abc']
    assert fires(pg, 'E12')
    pg = clean(); pg['videos'] = [{'autoplay': True, 'poster': '', 'reduced': '', 'in_hero': True}]
    assert len(fires(pg, 'E12')) == 2


def test_e13_ornaments():
    pg = clean(); pg['ornaments'].append({'id': 'rope-rule', 'body': False, 'tag': 'hr'})
    assert fires(pg, 'E13')
    pg = clean(); pg['ornaments'] = [{'id': 'leaf-rule', 'body': False, 'tag': 'span'}] * 4
    assert fires(pg, 'E13')
    pg = clean(); pg['ornaments'] = []
    assert fires(pg, 'E13')                                       # build chose leaf-rule, page carries none


def test_e14_nav():
    pg = clean(); pg['nav']['links'] = 9
    assert fires(pg, 'E14')
    pg = clean(); pg['nav']['dropdowns'] = 1
    assert fires(pg, 'E14')


def test_e15_banned_words():
    pg = clean(); pg['text'][0]['text'] = 'Your dream garden wedding'
    assert fires(pg, 'E15')
    pg = clean(); pg['text'].append(T('STUNNING VIEWS', 'p', kicker=True))
    assert fires(pg, 'E15')


def test_e16_body_measure_and_headline_length():
    pg = clean(); pg['text'][1]['size'] = 15.0
    assert fires(pg, 'E16')
    pg = clean(); pg['text'][1].update({'text': 'x' * 300, 'len': 300, 'h': 84.0})   # 3 lines -> 100 chars per line
    assert fires(pg, 'E16')
    pg = clean(); pg['text'][0]['text'] = ' '.join(['word'] * 15)
    assert fires(pg, 'E16')


def test_e17_corner():
    m = dict(META, personality={'density': 90, 'voice': 90})
    assert fires(clean(), 'E17', meta=m)
    luxe = dict(m, dialect={'id': 'modern-luxe'}, axis_tokens={'section_pad_min': 160}, fingerprint={'hero_framing': 'inset'})
    assert not fires(clean(), 'E17', meta=luxe)
    assert fires(clean(), 'E17', meta=dict(luxe, axis_tokens={'section_pad_min': 120}))


def test_e18_sections_before_tour():
    pg = clean(); pg['sections'] = ['.hero', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'tour']
    assert fires(pg, 'E18')


def test_e19_first_screen_fact():
    pg = clean(); pg['first_screen_text'] = 'A garden in the hills. Pricing'
    assert fires(pg, 'E19')
    pg['facts_marked'] = ['guests']
    assert not fires(pg, 'E19')
    pg = clean(); pg['first_screen_text'] = 'Nine acres in Shadow Hills, 1907 barn'
    probs, warns, _ = EX.run_all(pg, META, CONTENT, '', True)
    assert not [p for p in probs if p.startswith('E19')] and not any('only one fact' in w for w in warns)


def test_collect_js_is_valid_javascript_shape():
    js = EX.COLLECT_JS
    assert 'POPUP_TEST' not in js and 'SLIDER_TEST' not in js and 'BADGE_TEST' not in js and 'WAVE_TEST' not in js
    assert js.count('{') == js.count('}')


def main():
    import sys
    return _util.run_module(sys.modules[__name__])


if __name__ == '__main__':
    import sys
    sys.exit(main())
