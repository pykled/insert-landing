"""Content schema, voice fact rule, pairing rules."""
import copy
from tests import _util
from lib import schema as S, fonts as F

WORDS = _util.data('dialects.json')['vibe_words']


def test_existing_content_is_valid():
    errs, warns = S.validate_content(_util.content('stonehurst'), WORDS)
    assert errs == [], errs


def test_photo_tags_are_checked():
    v = _util.content('stonehurst')
    item = v['photos']['items']['hero']
    item.update({'subject': 'couple', 'mono': 'yes', 'flora': 'rose', 'archival': True})
    errs, _ = S.validate_content(v, WORDS)
    joined = ' | '.join(errs)
    for frag in ('subject "couple"', 'mono must be true/false', 'flora "rose"', 'archival but has no "rights"'):
        assert frag in joined, (frag, errs)


def test_vibe_block_is_checked():
    v = _util.content('stonehurst')
    v['vibe'] = {'type': 'spaceship', 'era': 'old', 'words': ['lush', 'lush', 'shiny']}
    errs, _ = S.validate_content(v, WORDS)
    joined = ' | '.join(errs)
    assert 'vibe.type' in joined and 'vibe.era' in joined and 'exactly three different words' in joined
    v['vibe'] = {'type': 'garden', 'era': 1907, 'words': ['lush', 'garden', 'shiny']}
    errs, warns = S.validate_content(v, WORDS)
    assert any('shiny' in e for e in errs) and any('era_source' in w for w in warns)


def test_missing_required_keys():
    v = _util.content('stonehurst')
    del v['faqs']; del v['tagline_facts']['max_guests']
    errs, _ = S.validate_content(v, WORDS)
    assert any('"faqs"' in e for e in errs) and any('max_guests' in e for e in errs)


def test_lead_must_be_the_place():
    v = _util.content('stonehurst')
    assert S.check_lead(v, 'hero') == ([], [])
    v['photos']['items']['hero']['subject'] = 'people'
    errs, _ = S.check_lead(v, 'hero')
    assert errs and 'exclusion 6' in errs[0]


def test_strict_voices_state_no_facts():
    voices = _util.data('voices.json')
    errs, warns = S.validate_voices(voices)
    assert errs == [], errs
    for vid in ('heritage', 'evening', 'lyric'):
        assert voices[vid]['_meta']['strict_facts'] and len(voices[vid]['cta_sets']) == 3
    bad = copy.deepcopy(voices)
    bad['heritage']['hero_headline'] = ['Twelve acres. {name}.']
    bad['lyric']['spaces_title'] = 'For 200 guests.'
    errs, _ = S.validate_voices(bad)
    assert len(errs) == 2, errs


def test_pairing_rules():
    pairings = _util.data('pairings.json')['pairings']
    assert F.validate_pairings(pairings) == []
    assert len(pairings) == 29   # 2D: three candlelit pairings (brygada, castoro, baskerville)
    p = copy.deepcopy(next(x for x in pairings if x['id'] == 'editorial-didone'))
    p['display']['weight'] = 300; p['risk'] = 'none'; p['display']['vars'] = None
    errs = F.validate_pairings([p])
    assert any('400-600' in e for e in errs) and any('hairline' in e for e in errs) and any('opsz' in e for e in errs)
    q = copy.deepcopy(p); q['display']['family'] = 'Montserrat'
    assert any('banned' in e for e in F.validate_pairings([q]))


if __name__ == '__main__':
    import sys
    sys.exit(_util.run_module(sys.modules[__name__]))
