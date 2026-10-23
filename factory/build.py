#!/usr/bin/env python3
"""Insert venue site factory: content JSON + personality -> static homepage.

Usage
  build.py content/stonehurst.json --variant a --out ../previews/stonehurst-variants/a \
      --personality formality=85,scale=70,era=55,density=70,temperature=65,voice=80 \
      [--force hero=masthead --force pairing=coastal-newsreader ...] [--lead greenhouse] \
      [--palette-photos greenhouse,reception,bamboo] [--accent-hue 247] [--copy hero_headline="..."] \
      [--dialect auto|<id>|none] [--register] [--allow-close "<reason>"] [--offline-fonts] [--strict-fonts]

Steps: validate content/voices/pairings -> photo signals + dialect score table (lib/personality.py) -> clamp axes ->
derive palette (dialect paper tone; charcoal set for dark dialects) -> select archetypes among the dialect's ids
(fit + diversity guard) -> resolve templates (nearest existing fallback, recorded) -> verify the Google Fonts import ->
optimise images -> render -> write index.html + build-meta.json -> fingerprint guard -> optional register.
--dialect none is the pre-dialect path (no clamping, full library minus dialect-only items): the three Stonehurst
proof variants use it so they keep their original choices.
"""
import argparse, copy, json, os, re, sys, time, shutil, hashlib, datetime
from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from lib import palette as P, images as I, personality as PERS, fingerprint as FP, templates as TPL, schema as SCHEMA, fonts as FONTS

VERSION = '0.1'
WORDS = {1: 'one', 2: 'two', 3: 'three', 4: 'four', 5: 'five', 6: 'six', 7: 'seven', 8: 'eight', 9: 'nine', 10: 'ten', 12: 'twelve'}


# Preload `imagesizes` per hero: must equal the lead <img sizes> in templates/heroes/<id>.j2, or Chrome preloads one
# width and then fetches another. Dialect builds only; pre-dialect builds keep the original three-way rule (byte-identical).
HERO_SIZES = {
    'masthead': '100vw', 'frame': '(min-width: 1140px) 1040px, 92vw', 'cover-type': '(min-width: 861px) 46vw, 100vw',
    'cinematic': '(max-width: 860px) 140vw, 100vw', 'crest-centred': '(max-width: 860px) 180vw, 100vw',
    'silent': '(max-width: 860px) 180vw, 100vw', 'landscape-silent': '(max-width: 860px) 160vw, 100vw',
    'slideshow': '(max-width: 860px) 160vw, 100vw', 'panel': '(min-width: 861px) 50vw, 100vw',
    'inset-caption': '(min-width: 1400px) calc(100vw - 160px), (min-width: 861px) calc(100vw - 11vw), calc(100vw - 48px)',
    'inset-wide': '(min-width: 1200px) 1120px, 92vw',
    'arch-split': '(min-width: 1140px) 520px, (min-width: 861px) 46vw, 100vw',
    'pair-split': '(min-width: 1140px) 540px, (min-width: 861px) 46vw, 100vw',
}


def wordnum(n):
    try:
        return WORDS.get(int(n), str(n))
    except Exception:
        return str(n)


def load(p):
    return json.load(open(p))


def caption_from_alt(alt):
    c = alt.split(':')[0].split('. ')[0].strip()
    return (c[:1].upper() + c[1:]).rstrip('.') + '.'


TYPE_NOUNS = {'estate': 'estate', 'mansion': 'mansion', 'castle': 'castle', 'villa': 'villa', 'hacienda': 'hacienda', 'barn': 'barn',
              'ranch': 'ranch', 'vineyard': 'vineyard', 'garden': 'garden', 'glasshouse': 'glasshouse', 'resort': 'resort', 'hotel': 'hotel',
              'loft': 'loft', 'clubhouse': 'clubhouse', 'theatre': 'theatre'}   # coastal / lake / desert are settings, not nouns
SLOT_RE = re.compile(r'\{([a-z_]+)\}')


def copy_slots(v):
    """Every {slot} a voice may use. Values come only from the content file; a missing fact is None (never invented)."""
    tf = v['tagline_facts']
    spaces = v['spaces']
    names = [s['name'].replace('The ', '').lower() for s in spaces]
    space_list = ', '.join(names[:-1]) + ' and ' + names[-1]
    uses = tf['uses']
    slots = {
        'name': v['name'], 'short_name': v['short_name'], 'locality': tf['locality'], 'region': tf['region'], 'state': tf['state'],
        'acres': tf['acres'], 'acres_words': wordnum(tf['acres']).capitalize(), 'acres_words_lc': wordnum(tf['acres']), 'space_count': tf['space_count'], 'space_count_words': wordnum(tf['space_count']).capitalize(), 'space_count_words_lc': wordnum(tf['space_count']),
        'max_guests': tf['max_guests'], 'space_list': space_list, 'space_list_cap': space_list[:1].upper() + space_list[1:],
        'uses_sentence': ', '.join(uses[:-1]) + ' and ' + uses[-1].lower(), 'uses_sentence_lc': (', '.join(uses[:-1]) + ' and ' + uses[-1]).lower(),
        'rental_hours': v['day']['rental_hours'], 'spaces_per_event': v['day']['spaces_per_event'], 'spaces_per_event_lc': v['day']['spaces_per_event'][:1].lower() + v['day']['spaces_per_event'][1:],
    }
    vibe = v.get('vibe') or {}
    noun = TYPE_NOUNS.get(vibe.get('type'))
    epd = tf.get('events_per_day')
    slots.update({
        'era': vibe.get('era'),
        'type_noun_lc': noun,
        'type_noun_cap': (('An ' if noun[0] in 'aeiou' else 'A ') + noun) if noun else None,
        'events_per_day_words': wordnum(epd).capitalize() if epd else None,
    })
    if tf.get('acres') is None:
        for k in ('acres', 'acres_words', 'acres_words_lc'):
            slots[k] = None
    return slots


def _fill(tpl, slots):
    """First candidate whose slots all resolve to non-null content values; None if no candidate can be filled."""
    for cand in (tpl if isinstance(tpl, list) else [tpl]):
        need = SLOT_RE.findall(cand)
        if all(slots.get(k) is not None for k in need):
            return cand.format(**{k: slots[k] for k in need})
    return None


def resolve_copy(voice, v, overrides, cta_set=None):
    """Voice preset + CTA set + human overrides -> copy. Plain-string slots in pre-dialect voices behave exactly as
    before; list candidates (stage 2A voices) take the first fillable one, and an unfillable or leftover {slot} stops
    the build: copy never ships with a placeholder or an invented fact."""
    slots = copy_slots(v)
    strict = (voice.get('_meta') or {}).get('strict_facts', False)
    out = {}
    for k, tpl in voice.items():
        if k.startswith('_') or k == 'cta_sets':
            continue
        if k in overrides:
            tpl = overrides[k]
        elif cta_set and k in cta_set:
            tpl = cta_set[k]
        if isinstance(tpl, list) or strict:
            s = _fill(tpl, slots)
            if s is None:
                raise ValueError('copy slot %s: no candidate can be filled from the content file (%s)' % (k, tpl))
        else:
            s = tpl
            try:
                s = s.format(**slots)
            except (KeyError, IndexError):
                pass
        out[k] = Markup(s)
    return out


def section_plan(p, ch, v):
    """Ordered sections. Three rhythms; which one is a function of the axes, not a hard-coded per-variant list."""
    d, vo = p['density'], p['voice']
    moment = ch['moment']['id']
    moment_nav = {'guest-journey': 'A guest\'s day', 'light-shift': 'A day here', 'seat-picker': 'Capacity'}[moment]
    S = lambda id_, tpl, nav=None: {'id': id_, 'template': tpl, 'nav': nav}
    spaces = S('spaces', 'sections/spaces-' + ch['spaces']['id'], 'Spaces')
    story = S('story', 'sections/story-' + ch['story']['id'], 'History' if vo >= 60 else 'The property')
    tour = S('tour', 'sections/tour-' + ch['tour']['id'], 'Tours')
    guide = S('guide', 'sections/guide', 'Pricing')
    faq = S('faq', 'sections/faq-' + ch['faq']['id'], 'FAQ')
    mom = S({'guest-journey': 'journey', 'light-shift': 'day', 'seat-picker': 'fit'}[moment], 'moments/' + moment, moment_nav)
    glance = S('glance', 'sections/glance')
    uses = S('uses', 'sections/uses')
    featured = S('featured', 'sections/featured')
    if d >= 80:
        order = [spaces, mom, tour, guide, story, faq, uses, featured]
        rhythm = 'modern: spaces and the moment first, history late, no glance strip'
    elif vo >= 65:
        order = [featured, story, spaces, mom, tour, guide, glance, faq, uses]
        rhythm = 'editorial: credentials, then history before the spaces'
    else:
        order = [featured, spaces, mom, story, tour, guide, glance, faq, uses]
        rhythm = 'warm: straight to the grounds, history after'
    return order, rhythm


def jsonld(v, out_url):
    tf = v['tagline_facts']
    places = []
    for s in v['spaces']:
        pl = {'@type': 'Place', 'name': s['name'], 'description': s['use']}
        if s.get('capacity'):
            pl['maximumAttendeeCapacity'] = s['capacity']
        places.append(pl)
    data = {
        '@context': 'https://schema.org',
        '@graph': [
            {
                '@type': ['EventVenue', 'LocalBusiness'], '@id': v['website'] + '#venue', 'name': v['name'], 'url': v['website'],
                'description': 'A %s-acre garden wedding and event venue in %s, %s.' % (tf['acres'], tf['locality'], tf['region']),
                'email': v['contact']['email'],
                'address': {'@type': 'PostalAddress', 'streetAddress': v['contact']['address_line'], 'addressLocality': tf['locality'], 'addressRegion': tf['state'], 'addressCountry': 'US'},
                'maximumAttendeeCapacity': tf['max_guests'],
                'amenityFeature': [{'@type': 'LocationFeatureSpecification', 'name': n, 'value': True} for n in v['day']['included']],
                'containsPlace': places,
                'openingHoursSpecification': {'@type': 'OpeningHoursSpecification', 'description': v['contact']['hours']},
            },
            {'@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': f['q'], 'acceptedAnswer': {'@type': 'Answer', 'text': f['a']}} for f in v['faqs']]},
        ],
    }
    if v['contact'].get('phone'):
        data['@graph'][0]['telephone'] = v['contact']['phone']
    return json.dumps(data, indent=0).replace('</', '<\\/')


MOMENT_SECTION = {'guest-journey': 'journey', 'light-shift': 'day', 'seat-picker': 'fit'}
MOMENT_NAV = {'guest-journey': 'A guest\'s day', 'light-shift': 'A day here', 'seat-picker': 'Capacity'}


def dialect_section_plan(rhythm_variant, used, v, voice_axis, resolve_section):
    """Ordered sections for a dialect build, from the dialect's rhythm variant. `used` holds the resolved (rendered)
    archetype ids. Section blocks that do not exist yet go through resolve_section(id) -> id or None (omitted).
    The press row (featured) goes right after the story and only when the content names press; uses closes the page."""
    S = lambda id_, tpl, nav=None: {'id': id_, 'template': tpl, 'nav': nav}
    roles = {
        'spaces': S('spaces', 'sections/spaces-' + used['spaces'], 'Spaces'),
        'story': S('story', 'sections/story-' + used['story'], 'History' if voice_axis >= 60 else 'The property'),
        'tour': S('tour', 'sections/tour-' + used['tour'], 'Tours'),
        'guide': S('guide', 'sections/guide', 'Pricing'),
        'faq': S('faq', 'sections/faq-' + used['faq'], 'FAQ'),
    }
    m = used['moment']
    roles['moment'] = None if m == 'none' else S(MOMENT_SECTION.get(m, m), 'moments/' + m, MOMENT_NAV.get(m, 'A day here'))
    order = []
    for blk in rhythm_variant['blocks']:
        if blk['kind'] == 'role':
            sec = roles[blk['id']]
            if sec:
                order.append(sec)
            if blk['id'] == 'story' and v.get('featured_in'):
                order.append(S('featured', 'sections/featured'))
            if blk['id'] == 'spaces' and used.get('gallery', 'none') != 'none':
                order.append(S('gallery', 'sections/gallery-' + used['gallery']))
        else:
            sid = resolve_section(blk['id'])
            if sid:
                order.append(S(sid, 'sections/' + sid))
    order.append(S('uses', 'sections/uses'))
    return order, 'dialect %s: %s' % (rhythm_variant['id'], rhythm_variant['label'])


def parse_personality(s):
    p = {}
    if s:
        for kv in s.split(','):
            k, val = kv.split('='); p[k.strip()] = float(val)
    return p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('content')
    ap.add_argument('--variant', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--personality', help='formality=..,scale=..,era=..,density=..,temperature=..,voice=.. (dialect builds: optional, defaults to the dialect centre, always clamped)')
    ap.add_argument('--dialect', default='auto', help='auto (score photos + vibe), a dialect id (human override), or none (pre-dialect build, no clamping)')
    ap.add_argument('--force', action='append', default=[], help='dim=id (pairing, hero, spaces, story, faq, tour, gallery, moment, voice, ornament, rhythm, tone, nav)')
    ap.add_argument('--lead', help='lead photo name')
    ap.add_argument('--palette-photos', help='comma list of photo names used for palette extraction')
    ap.add_argument('--accent-hue', type=float, help='human override: force the accent hue (degrees, OKLCH)')
    ap.add_argument('--copy', action='append', default=[], help='key=value copy override (voice slot)')
    ap.add_argument('--register', action='store_true')
    ap.add_argument('--allow-close', nargs='?', const='(no reason given)', default=None, metavar='REASON', help='register even if the guard refuses; the reason is stored with the registration')
    ap.add_argument('--offline-fonts', action='store_true', help='skip the Google Fonts network check (cached verification only)')
    ap.add_argument('--strict-fonts', action='store_true', help='fail when the pairing import cannot be verified (offline and never cached)')
    ap.add_argument('--registry', default=os.path.join(HERE, 'data', 'registry.json'))
    a = ap.parse_args()
    t0 = time.time()
    timings = {}

    v = load(a.content)
    cdir = os.path.dirname(os.path.abspath(a.content))
    dialects_doc = load(os.path.join(HERE, 'data', 'dialects.json'))
    pairings_all = load(os.path.join(HERE, 'data', 'pairings.json'))['pairings']
    arch = load(os.path.join(HERE, 'data', 'archetypes.json'))
    voices = load(os.path.join(HERE, 'data', 'voices.json'))
    registry = FP.load_registry(a.registry)

    # 0. validation: content schema, voices, pairings (stop on errors)
    errs, schema_warnings = SCHEMA.validate_content(v, dialects_doc['vibe_words'])
    verrs, vwarn = SCHEMA.validate_voices(voices)
    perrs = FONTS.validate_pairings(pairings_all)
    for w in schema_warnings:
        print('  schema warning:', w)
    if errs or verrs or perrs:
        for e in errs + verrs + perrs:
            print('  ERROR:', e)
        sys.exit(3)

    p_in = parse_personality(a.personality)
    if a.dialect == 'none' and not a.personality:
        ap.error('--personality is required for --dialect none')
    forced = dict(kv.split('=') for kv in a.force)
    copy_over = {}
    for kv in a.copy:
        k, val = kv.split('=', 1); copy_over[k] = val

    # photos + manifest
    src_dir = os.path.normpath(os.path.join(cdir, v['photos']['source_dir']))
    manifest = {m['name']: m for m in load(os.path.normpath(os.path.join(cdir, v['photos']['manifest'])))}
    items = v['photos']['items']
    paths = {n: os.path.join(src_dir, n + '.jpg') for n in items}
    lead = a.lead or 'hero'
    v['_lead_width'] = manifest[lead]['kept_copy_size'][0] if lead in manifest else 0
    v['_lead'] = lead
    pal_names = a.palette_photos.split(',') if a.palette_photos else [lead] + [n for n in items if n != lead][:3]
    pal_paths = {n: paths[n] for n in pal_names}
    lead_errs, lead_warn = SCHEMA.check_lead(v, lead)
    schema_warnings += lead_warn
    if lead_errs and a.dialect != 'none':
        for e in lead_errs:
            print('  ERROR:', e)
        sys.exit(3)
    copy_zone = {}
    if a.dialect != 'none':
        # stage 2C: can the lead carry copy on the photo under the 35% scrim cap? (heroes' needs.copy_zone reads this)
        copy_zone = {n: P.copy_zone_contrast(paths[n], items[n].get('focal', '50% 50%')) for n in items}
        v['_copy_zone'] = copy_zone[lead]
        v['_copy_zone_min'] = P.COPY_ZONE_MIN

    # 1. dialect: score (photo signals + vibe + type prior), pick, clamp the axes
    t1 = time.time()
    dialect = None
    dialect_meta = {'id': 'none', 'source': 'pre-dialect build (--dialect none)'}
    clamp_changes = []
    p = {k: 50.0 for k in PERS.AXES}
    p.update(p_in)
    if a.dialect != 'none':
        signals = P.photo_signals(pal_paths, lead)
        _, _, pre_meta = P.derive(pal_paths, p, lead=lead)
        winner, table = PERS.score_dialects(dialects_doc, signals, v, pre_meta, registry)
        by_id = {d['id']: d for d in dialects_doc['dialects']}
        if a.dialect == 'auto':
            chosen, source = winner, 'scored (top of the table; ties -> fewer registered sites)'
        elif a.dialect in by_id:
            chosen, source = a.dialect, 'human override (--dialect %s; the scorer picked %s)' % (a.dialect, winner)
        else:
            ap.error('--dialect must be auto, none or one of: %s' % ', '.join(by_id))
        dialect = by_id[chosen]
        base = PERS.axes_centre(dialect)
        base.update(p_in)
        p, clamp_changes = PERS.clamp_axes(base, dialect)
        dialect_meta = {'id': chosen, 'source': source, 'scored_winner': winner, 'scores': table, 'clamped': clamp_changes,
                        'personality_in': p_in or 'none (dialect centre)', 'signals': {k: val for k, val in signals.items() if k != 'per_photo'},
                        'signals_per_photo': signals['per_photo']}

    # 2. palette (dialect paper + tone for dialect builds)
    tone = None
    if dialect:
        tone = forced.pop('tone', None) or PERS.paper_tone(dialect, p, dialect_meta['signals'])
    tokens, pal_report, pal_meta = P.derive(pal_paths, p, lead=lead, dialect=dialect, tone=tone)
    if a.accent_hue is not None:
        if pal_meta.get('mode') == 'dark':
            ap.error('--accent-hue is not supported on a dark (charcoal) palette yet')
        # rebuild the accent tokens at the human-chosen hue, keep everything else
        from lib import color as C
        h = a.accent_hue; Ca = max(0.06, pal_meta['accent_chroma'])
        L, tokens['accent-text'] = C.fit_lightness(min(Ca, 0.12), h, tokens['paper-2'], 7.0, True, 0.50)
        L, tokens['accent'] = C.fit_lightness(Ca, h, '#ffffff', 5.0, True, 0.62)
        L, tokens['accent-fill'] = C.fit_lightness(Ca, h, '#ffffff', 7.0, True, 0.55)
        tokens['accent-tint'] = C.lch_to_hex(pal_meta['paper_L'] - 0.045, 0.04, h)
        L, tokens['accent-text'] = C.fit_lightness(min(Ca, 0.12), h, tokens['accent-tint'], 7.0, True, 0.50)
        tokens['focus'] = tokens['accent']
        pal_meta['accent_hue'] = h; pal_meta['accent_from_photo'] = 'human override'
        pal_meta['temperature'] = 'warm' if C.is_warm(h) else 'cool'
    timings['palette_s'] = round(time.time() - t1, 2)

    # 3. libraries: everything for pre-dialect builds, only the dialect's ids for dialect builds
    libs = {'pairings': pairings_all}
    for k in ('heroes', 'spaces', 'story', 'faq', 'tour', 'gallery', 'moments', 'voices'):
        libs[k] = arch[k]
    fallbacks = []
    exists = lambda kind, i: TPL.exists(kind, i)
    used_ornament, rhythm_variant, cta_index, last_pairing = 'none', None, None, None
    if dialect:
        same = [s for s in registry['sites'] if s['fingerprint'].get('dialect') == dialect['id'] and s['id'] != '%s-%s' % (v['slug'], a.variant)]
        last_pairing = same[-1]['fingerprint'].get('pairing') if same else None
        allowed = {key: [it['id'] for it in dialect[key]] for key in TPL.LIST_KINDS}
        libs['pairings'] = [x for x in pairings_all if x['id'] in allowed['pairings'] and (x['id'] != last_pairing or len(allowed['pairings']) == 1 or 'pairing' in forced)]
        pair_counts = {}
        for s_ in same:
            pair_counts[s_['fingerprint'].get('pairing')] = pair_counts.get(s_['fingerprint'].get('pairing'), 0) + 1
        libs['pairings'] = PERS.usage_penalised(libs['pairings'], pair_counts)
        for key in ('heroes', 'spaces', 'story', 'faq', 'tour', 'gallery', 'moments', 'voices'):
            libs[key] = [x for x in arch[key] if x['id'] in allowed[key]]
        for dim, key in (('pairing', 'pairings'), ('hero', 'heroes'), ('spaces', 'spaces'), ('story', 'story'), ('faq', 'faq'), ('tour', 'tour'),
                         ('gallery', 'gallery'), ('moment', 'moments'), ('voice', 'voices'), ('ornament', 'ornaments')):
            if dim in forced and forced[dim] not in allowed[key]:
                ap.error('--force %s=%s is not in dialect %s (allowed: %s)' % (dim, forced[dim], dialect['id'], ', '.join(allowed[key])))
        orn_counts = {}
        for s in same:
            o = s['fingerprint'].get('ornament_wanted') or s['fingerprint'].get('ornament')
            orn_counts[o] = orn_counts.get(o, 0) + 1
        ornament_wanted = forced.pop('ornament', None) or PERS.rotate_pick(allowed['ornaments'], orn_counts)
        used_ornament, rec = TPL.resolve('ornament', ornament_wanted, allowed['ornaments'], dialects_doc['fallbacks'], exists)
        used_ornament = used_ornament or 'none'
        if rec:
            fallbacks.append(rec)
        nav_forced = forced.pop('nav', None)
        if nav_forced and nav_forced not in dialect['nav']:
            ap.error('--force nav=%s is not in dialect %s (allowed: %s)' % (nav_forced, dialect['id'], ', '.join(dialect['nav'])))
        rv_ids = [r['id'] for r in dialect['rhythm_variants']]
        rv_id = forced.pop('rhythm', None) or rv_ids[len(same) % len(rv_ids)]
        rhythm_variant = next(r for r in dialect['rhythm_variants'] if r['id'] == rv_id)

    arch_by = {key: {x['id']: x for x in arch[key]} for key in ('heroes', 'spaces', 'story', 'moments')}
    kind_of = {'hero': ('hero', 'heroes'), 'spaces': ('spaces', 'spaces'), 'story': ('story', 'story'), 'moment': ('moment', 'moments')}

    def resolve_item(dim, item):
        """The archetype record that will actually render for a selected item (fallback when the template is missing)."""
        if not dialect or item['id'] == 'none':
            return item
        kind, key = kind_of[dim]
        used, _ = TPL.resolve(kind, item['id'], [x['id'] for x in libs[key]], dialects_doc['fallbacks'], exists)
        if used is None or used == 'none':
            return {'id': 'none', 'fingerprint': {}}
        return arch_by[key][used]

    # 4. selection with the diversity guard inside the loop
    axis_tokens = PERS.tokens_from_axes(p)

    def reg_check(partial_fp):
        fp = dict(partial_fp)
        fp.update({'accent_hue': pal_meta['accent_hue'], 'paper_temperature': pal_meta['temperature'], 'button_style': axis_tokens['button_style'], 'radius': axis_tokens['radius'], 'section_order': [], 'faq': '', 'tour': ''})
        if dialect:
            fp.update({'dialect': dialect['id'], 'paper_tone': tone, 'ornament': used_ornament})
        status, nid, dist, _ = FP.check(fp, registry, exclude_id='%s-%s' % (v['slug'], a.variant))
        return status, nid, dist

    t1 = time.time()
    ch, sel_report = PERS.select(libs, p, reg_check, forced=forced, content=v, dialect_mode=bool(dialect), resolve=resolve_item)
    timings['select_s'] = round(time.time() - t1, 2)
    pair = ch['pairing']

    # 5. template resolution: render what exists, record every fallback
    used = {}
    for dim, kind in (('hero', 'hero'), ('spaces', 'spaces'), ('story', 'story'), ('faq', 'faq'), ('tour', 'tour'), ('gallery', 'gallery'), ('moment', 'moment')):
        want = ch[dim]['id']
        if dialect:
            key = {'hero': 'heroes', 'moment': 'moments'}.get(dim, dim)
            got, rec = TPL.resolve(kind, want, [x['id'] for x in libs[key]], dialects_doc['fallbacks'], exists)
            if rec:
                fallbacks.append(rec)
            used[dim] = got or 'none'
        else:
            used[dim] = want
    if used['hero'] == 'none':
        print('  ERROR: no renderable hero for this build'); sys.exit(3)
    hero_rec = arch_by['heroes'][used['hero']]
    hero_copy_on = 'photo'
    zone = hero_rec.get('needs', {}).get('copy_zone')
    if dialect and zone and copy_zone[lead][zone] < P.COPY_ZONE_MIN:
        darker = sorted((n for n in items if copy_zone[n][zone] >= P.COPY_ZONE_MIN), key=lambda n: -copy_zone[n][zone])
        if hero_rec['needs'].get('paper_mode_ok'):
            hero_copy_on = 'paper'
            print('  hero %s: lead %s measures %.2f:1 in the copy zone under a 35%% scrim (< %.1f); copy set on paper' % (used['hero'], lead, copy_zone[lead][zone], P.COPY_ZONE_MIN))
        else:
            print('  WARNING: hero %s forced on lead %s (copy zone %.2f:1 < %.1f); darker leads: %s' % (used['hero'], lead, copy_zone[lead][zone], P.COPY_ZONE_MIN, ', '.join(darker) or 'none'))
    nav_style = 'minimal' if p['era'] >= 85 else ('centered' if (p['formality'] >= 75 and p['voice'] >= 60) else 'bar')
    if dialect:
        # nav is a variation knob (spec 4.14): the axis formula's style first, then rotate through the dialect's list by
        # the number of registered same-dialect sites (like the rhythm variant); --force nav=<id> overrides
        navs = dialect['nav']
        start = navs.index(nav_style) if nav_style in navs else 0
        nav_style = navs[(start + len(same)) % len(navs)]
        if nav_forced:
            nav_style = nav_forced
        if nav_style == 'two-row':
            nav_used = next((n for n in dialects_doc['fallbacks']['nav']['two-row'] if os.path.exists(os.path.join(HERE, 'templates', 'partials', 'nav-%s.j2' % n))), 'bar')
            if not os.path.exists(os.path.join(HERE, 'templates', 'partials', 'nav-two-row.j2')):
                fallbacks.append({'kind': 'nav', 'wanted': 'two-row', 'used': nav_used, 'chain': dialects_doc['fallbacks']['nav']['two-row'], 'reason': 'template for nav "two-row" does not exist yet (owed by stage 2B)'})
                nav_style = nav_used

    # 6. dialect tokens and the section rhythm
    dial_tokens = {}
    if dialect:
        def resolve_section(sid):
            got, rec = TPL.resolve('section', sid, [], dialects_doc['fallbacks'], exists)
            if rec:
                fallbacks.append(rec)
            return got
        sections, rhythm = dialect_section_plan(rhythm_variant, used, v, p['voice'], resolve_section)
        dial_tokens = PERS.dialect_tokens(dialect, p, pair)
        axis_tokens.update(dialect.get('tokens', {}))
        m = dialect['motion']
        axis_tokens.update({'reveal': m['reveal'], 'reveal_ms': m['reveal_ms'], 'reveal_offset_px': m['offset_px'], 'ease': 'cubic-bezier(.2,.7,.2,1)',
                            'motion_device': m['device'], 'motion_device_ms': m['device_ms'], 'kicker_style': dial_tokens['kicker_style'],
                            'photo_edge': dial_tokens['photo_edge'], 'body_px': dial_tokens['body_px'], 'display_case': dial_tokens['display_case'],
                            'paper_mode': pal_meta.get('mode', 'light'), 'paper_tone': tone})
        # pre-2B templates only know flush / keyline / rounded image edges
        axis_tokens['image_edge'] = {'keyline': 'keyline', 'rounded': 'rounded', 'arch': 'flush'}.get(dial_tokens['photo_edge'], 'flush')
        if axis_tokens['image_edge'] == 'rounded' and axis_tokens['radius'] == 0:
            axis_tokens['radius'] = 0
        pair = copy.deepcopy(pair)
        pair['body']['size_px'] = dial_tokens['body_px']   # body size knob (17/19/21): base.css reads pair.body.size_px
        same_voice = [s for s in registry['sites'] if s['fingerprint'].get('voice') == ch['voice']['id'] and s['id'] != '%s-%s' % (v['slug'], a.variant)]
        sets = voices[ch['voice']['id']].get('cta_sets')
        if sets:
            cta_index = len(same_voice) % len(sets)
    else:
        sections, rhythm = section_plan(p, ch, v)

    # 7. fonts: the chosen pairing's import must resolve on fonts.googleapis.com (cached verification when offline)
    if a.offline_fonts:
        when = FONTS.load_cache()['verified'].get(pair['import'])
        fonts_ok, fonts_msg = (True, 'offline flag; cached verification from %s' % when) if when else ((not a.strict_fonts), 'offline flag and never verified')
    else:
        fonts_ok, fonts_msg = FONTS.verify_import(pair['import'], strict=a.strict_fonts)
    print('  fonts: %s: %s' % (pair['id'], fonts_msg))
    if not fonts_ok:
        print('  ERROR: Google Fonts import for pairing %s did not verify: %s' % (pair['id'], fonts_msg))
        sys.exit(4)

    # 8. images
    t1 = time.time()
    out_dir = os.path.abspath(a.out)
    os.makedirs(os.path.join(out_dir, 'img'), exist_ok=True)
    photos = {}
    for n, meta in items.items():
        role = 'hero' if n == lead else ('portrait' if 'portrait' in meta.get('tags', []) else 'large')
        extra = (400,) if used['spaces'] == 'spec-sheet' or used['moment'] == 'seat-picker' else ()
        info = I.build_set(paths[n], n, role, os.path.join(out_dir, 'img'), extra_widths=extra)
        default_w = I.pick_default(info['variants'], 1800 if n == lead else 1200)
        photos[n] = {'src': 'img/%s-%d.webp' % (n, default_w), 'srcset': I.srcset(n, info['variants']), 'width': info['variants'][-1][0], 'height': info['variants'][-1][1],
                     'alt': meta['alt'], 'focal': meta.get('focal', '50% 50%'), 'caption': caption_from_alt(meta['alt']), 'native': info['native'], 'variants': info['variants'],
                     'subject': meta.get('subject'), 'mono': bool(meta.get('mono')), 'flora': meta.get('flora'), 'archival': bool(meta.get('archival'))}
    # manifest for QA (native = crop size of the original, from the source manifest)
    qa_manifest = [{'name': n, 'crop': manifest[n]['crop'] if n in manifest else photos[n]['native'], 'kept_copy_size': photos[n]['native'], 'variants': photos[n]['variants'], 'source_url': manifest.get(n, {}).get('source_url')} for n in photos]
    json.dump(qa_manifest, open(os.path.join(out_dir, 'img', 'manifest.json'), 'w'), indent=0)
    timings['images_s'] = round(time.time() - t1, 2)

    # 9. render
    t1 = time.time()
    env = Environment(loader=FileSystemLoader(os.path.join(HERE, 'templates')), autoescape=select_autoescape(['html', 'j2']), trim_blocks=True, lstrip_blocks=True)
    env.filters['wordnum'] = wordnum
    voice = voices[ch['voice']['id']]
    cta_set = voice['cta_sets'][cta_index] if cta_index is not None else None
    try:
        copy_ = resolve_copy(voice, v, copy_over, cta_set)
    except ValueError as e:
        print('  ERROR:', e); sys.exit(3)
    guide_layout = 'plain' if p['density'] >= 80 else ('photo' if p['density'] <= 40 else 'band')
    light_photos = {'noon': next((n for n, m in items.items() if m.get('light') == 'day' and 'ceremony' in m.get('tags', []) and n != lead), 'flower'),
                    'golden': next((n for n, m in items.items() if m.get('light') == 'golden'), 'terrace'),
                    'night': next((n for n, m in items.items() if m.get('light') == 'night'), 'greenhouse')}
    looks = [s['name'].replace('The ', '').lower() for s in v['spaces']]
    ch_ids = {k: (val['id'] if isinstance(val, dict) else val) for k, val in ch.items()}
    ch_ids.update(used)
    ch_ids['ornament'] = used_ornament
    hid = used['hero']
    dialect_ctx = None
    if dialect:
        dialect_ctx = {'id': dialect['id'], 'label': dialect['label'], 'ornament': used_ornament, 'motion': dialect['motion'], 'tone': tone,
                       'paper_mode': pal_meta.get('mode', 'light'), 'rhythm': rhythm_variant['id'], 'photo': dialect['photo'],
                       'display_case': dial_tokens['display_case'], 'photo_edge': dial_tokens['photo_edge'], 'body_px': dial_tokens['body_px'],
                       'kicker_style': dial_tokens['kicker_style'], 'hero_framing': hero_rec['fingerprint'].get('hero_framing'),
                       'light_shift_default': dialect.get('light_shift_default', 'noon'), 'fallbacks': fallbacks}
    ctx = dict(v=v, t=axis_tokens, pair=pair, ch=ch_ids, copy=copy_, photos=photos, lead=lead,
               sections=sections, p=p, css_vars=P.css_vars(tokens), nav_style=nav_style, guide_layout=guide_layout, guide_photo='reception' if 'reception' in photos else lead,
               hero_sizes=(HERO_SIZES.get(hid) if dialect else None) or ('100vw' if hid in ('masthead', 'cinematic') else ('(min-width: 1140px) 1040px, 92vw' if hid == 'frame' else '(min-width: 861px) 46vw, 100vw')),
               spaces_by_id={s['id']: s for s in v['spaces']}, story_second='bungalow' if 'bungalow' in photos else lead, light_photos=light_photos,
               uses_band='ink' if p['density'] >= 80 else 'deep', looks_sentence=', '.join(looks[:-1]) + ' and ' + looks[-1],
               seo={'title_tail': 'Garden Wedding Estate in %s' % v['tagline_facts']['locality'], 'description': ''},
               jsonld=jsonld(v, ''), build={'variant': a.variant, 'version': VERSION, 'fingerprint_short': ''},
               dialect=dialect_ctx, ornament=used_ornament, palette_mode=pal_meta.get('mode', 'light'), hero_copy_on=hero_copy_on)
    fp = {
        'display_family': pair['display']['family'], 'display_class': pair['display']['class'], 'body_family': pair['body']['family'],
        'accent_hue': pal_meta['accent_hue'], 'paper_temperature': pal_meta['temperature'],
        'hero': hid, 'hero_family': hero_rec['fingerprint']['hero_family'],
        'spaces': used['spaces'], 'story': used['story'], 'faq': used['faq'], 'tour': used['tour'],
        'section_order': ['hero'] + [s['id'] for s in sections], 'moment': used['moment'],
        'button_style': axis_tokens['button_style'], 'radius': axis_tokens['radius'], 'lead_photo': lead,
    }
    # schema-2 dimensions (spec 6.1); for pre-dialect builds they are measured from what was rendered
    fp.update({
        'dialect': dialect['id'] if dialect else 'none', 'pairing': pair['id'], 'voice': ch['voice']['id'],
        'paper_tone': tone or FP.paper_tone_of(tokens['paper']), 'hero_framing': hero_rec['fingerprint'].get('hero_framing'),
        'display_case': dial_tokens.get('display_case') or pair['display'].get('case', 'sentence'), 'ornament': used_ornament,
        'body_px': FP.body_bucket(pair['body']['size_px']), 'photo_edge': dial_tokens.get('photo_edge') or axis_tokens['image_edge'],
        'motion_device': axis_tokens.get('motion_device', 'none') if dialect else 'none', 'nav_style': nav_style,
    })
    if dialect:
        fp['ornament_wanted'] = ornament_wanted
    ctx['build']['fingerprint_short'] = hashlib.sha1(json.dumps(fp, sort_keys=True).encode()).hexdigest()[:8]
    html = env.get_template('base.html.j2').render(**ctx)
    open(os.path.join(out_dir, 'index.html'), 'w').write(html)
    timings['render_s'] = round(time.time() - t1, 2)

    # 10. fingerprint check
    site_id = '%s-%s' % (v['slug'], a.variant)
    g = FP.guard(fp, registry, exclude_id=site_id)
    status, nid, dist, rows = g['status'], g['driver'], g['distance'], g['rows']
    timings['total_s'] = round(time.time() - t0, 2)
    meta = {'id': site_id, 'built': datetime.datetime.now().isoformat(timespec='seconds'), 'content_path': os.path.relpath(os.path.abspath(a.content), os.path.dirname(HERE)), 'personality': p, 'axis_tokens': axis_tokens, 'choices': ch_ids,
            'wanted': {k: (val['id'] if isinstance(val, dict) else val) for k, val in ch.items()},
            'selection': sel_report, 'rhythm': rhythm, 'nav_style': nav_style, 'guide_layout': guide_layout, 'pairing': {'display': pair['display'], 'body': pair['body'], 'id': pair['id']},
            'palette': {'tokens': tokens, 'report': pal_report, 'meta': pal_meta, 'photos': pal_names}, 'lead': lead, 'fingerprint': fp,
            'dialect': dialect_meta, 'fallbacks': fallbacks, 'copy_zone': {'lead': copy_zone.get(lead), 'min': P.COPY_ZONE_MIN, 'hero_copy_on': hero_copy_on, 'per_photo': copy_zone}, 'cta_set': cta_index, 'schema_warnings': schema_warnings, 'fonts': {'ok': fonts_ok, 'message': fonts_msg},
            'guard': {'status': status, 'nearest': g['nearest'], 'driver': nid, 'distance': round(dist, 3), 'quota': g['quota'], 'all': rows},
            'timings': timings, 'html_bytes': len(html.encode())}
    json.dump(meta, open(os.path.join(out_dir, 'build-meta.json'), 'w'), indent=1, default=str)
    print('built %s -> %s (%d KB html) in %.1fs  [palette %.1fs, select %.1fs, images %.1fs, render %.2fs]' % (site_id, out_dir, len(html) // 1024, timings['total_s'], timings['palette_s'], timings['select_s'], timings['images_s'], timings['render_s']))
    if dialect:
        top = ', '.join('%s %d' % (r['id'], r['score']) for r in dialect_meta['scores'][:4])
        print('  dialect: %s (%s) | scores: %s | clamped: %s' % (dialect['id'], dialect_meta['source'], top, ', '.join('%s %s->%s' % tuple(c) for c in clamp_changes) or '-'))
        print('  tone %s | ornament %s | rhythm %s | body %spx | case %s | edge %s' % (tone, used_ornament, rhythm_variant['id'], dial_tokens['body_px'], dial_tokens['display_case'], dial_tokens['photo_edge']))
        for f in fallbacks:
            print('  FALLBACK %s: %s -> %s' % (f['kind'], f['wanted'], f['used'] or '(omitted)'))
    print('  choices:', ', '.join('%s=%s' % (k, val) for k, val in meta['choices'].items()), '| nav', nav_style, '| guide', guide_layout)
    print('  palette: accent %s (hue %.0f from %s), deep %s, paper %s; all pairs pass: %s' % (tokens['accent'], pal_meta['accent_hue'], pal_meta['accent_from_photo'], tokens['deep'], tokens['paper'], pal_meta['all_pairs_pass']))
    print('  rhythm:', rhythm)
    for r in rows:
        print('  distance to %-24s %.3f %-6s shared: %s' % (r['id'], r['distance'], r['status'], ', '.join(r['shared'][:8]) or '-'))
    if g['quota']['sharing']:
        print('  quota: %s (%s)' % (g['quota']['status'], ', '.join(g['quota']['sharing'])))
    print('  guard: %s (driver %s; nearest %s at %.3f)' % (status.upper(), nid, g['nearest'], dist))
    if a.register and (status != 'refuse' or a.allow_close):
        FP.register(a.registry, site_id, fp, {'path': os.path.relpath(out_dir, os.path.dirname(HERE)), 'built': meta['built'], 'personality': p}, allow_close=a.allow_close if status == 'refuse' else None)
        print('  registered as', site_id)
    if status == 'refuse' and not a.allow_close:
        print('  REFUSED: too close to %s. Change a forced dimension or pass --allow-close "<reason>".' % nid)
        sys.exit(2)


if __name__ == '__main__':
    main()
