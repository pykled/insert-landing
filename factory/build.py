#!/usr/bin/env python3
"""Insert venue site factory: content JSON + personality -> static homepage.

Usage
  build.py content/stonehurst.json --variant a --out ../previews/stonehurst-variants/a \
      --personality formality=85,scale=70,era=55,density=70,temperature=65,voice=80 \
      [--force hero=masthead --force pairing=coastal-newsreader ...] [--lead greenhouse] \
      [--palette-photos greenhouse,reception,bamboo] [--accent-hue 247] [--copy hero_headline="..."] \
      [--register] [--allow-close]

Steps: load libraries -> derive palette from photos -> select archetypes (fit + diversity guard) ->
optimise images -> render -> write index.html + build-meta.json -> fingerprint check -> optional register.
"""
import argparse, json, os, sys, time, shutil, hashlib, datetime
from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from lib import palette as P, images as I, personality as PERS, fingerprint as FP

VERSION = '0.1'
WORDS = {1: 'one', 2: 'two', 3: 'three', 4: 'four', 5: 'five', 6: 'six', 7: 'seven', 8: 'eight', 9: 'nine', 10: 'ten', 12: 'twelve'}


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


def resolve_copy(voice, v, overrides):
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
    out = {}
    for k, tpl in voice.items():
        s = overrides.get(k, tpl)
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('content')
    ap.add_argument('--variant', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--personality', required=True, help='formality=..,scale=..,era=..,density=..,temperature=..,voice=..')
    ap.add_argument('--force', action='append', default=[], help='dim=id (pairing, hero, spaces, story, faq, tour, gallery, moment, voice)')
    ap.add_argument('--lead', help='lead photo name')
    ap.add_argument('--palette-photos', help='comma list of photo names used for palette extraction')
    ap.add_argument('--accent-hue', type=float, help='human override: force the accent hue (degrees, OKLCH)')
    ap.add_argument('--copy', action='append', default=[], help='key=value copy override (voice slot)')
    ap.add_argument('--register', action='store_true')
    ap.add_argument('--allow-close', action='store_true')
    ap.add_argument('--registry', default=os.path.join(HERE, 'data', 'registry.json'))
    a = ap.parse_args()
    t0 = time.time()
    timings = {}

    v = load(a.content)
    cdir = os.path.dirname(os.path.abspath(a.content))
    libs = {'pairings': load(os.path.join(HERE, 'data', 'pairings.json'))['pairings']}
    arch = load(os.path.join(HERE, 'data', 'archetypes.json'))
    for k in ('heroes', 'spaces', 'story', 'faq', 'tour', 'gallery', 'moments', 'voices'):
        libs[k] = arch[k]
    voices = load(os.path.join(HERE, 'data', 'voices.json'))
    registry = FP.load_registry(a.registry)

    p = {k: 50 for k in PERS.AXES}
    for kv in a.personality.split(','):
        k, val = kv.split('='); p[k.strip()] = float(val)
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

    # 1. palette
    t1 = time.time()
    pal_names = a.palette_photos.split(',') if a.palette_photos else [lead] + [n for n in items if n != lead][:3]
    overrides = None
    tokens, pal_report, pal_meta = P.derive({n: paths[n] for n in pal_names}, p, lead=lead)
    if a.accent_hue is not None:
        # re-derive with the human-chosen hue by pretending the top candidate had that hue
        from lib import color as C
        acc = [c for c in pal_meta['candidates']]
        tokens2, rep2, meta2 = P.derive({n: paths[n] for n in pal_names}, p, lead=lead)
        # simplest honest approach: rebuild the accent tokens at the forced hue, keep everything else
        h = a.accent_hue; Ca = max(0.06, pal_meta['accent_chroma'])
        L, tokens['accent-text'] = C.fit_lightness(min(Ca, 0.12), h, tokens['paper-2'], 7.0, True, 0.50)
        L, tokens['accent'] = C.fit_lightness(Ca, h, '#ffffff', 5.0, True, 0.62)
        L, tokens['accent-fill'] = C.fit_lightness(Ca, h, '#ffffff', 7.0, True, 0.55)
        tokens['accent-tint'] = C.lch_to_hex(pal_meta['paper_L'] - 0.045, 0.04, h)
        L, tokens['accent-text'] = C.fit_lightness(min(Ca, 0.12), h, tokens['accent-tint'], 7.0, True, 0.50)
        tokens['focus'] = tokens['accent']
        pal_meta['accent_hue'] = h; pal_meta['accent_from_photo'] = 'human override'
        pal_meta['temperature'] = 'warm' if C.is_warm(h) else 'cool'
        pal_report = [r for r in pal_report]  # contrast re-verified by the QA walker regardless
    timings['palette_s'] = round(time.time() - t1, 2)

    # 2. selection with the diversity guard inside the loop
    axis_tokens = PERS.tokens_from_axes(p)

    def reg_check(partial_fp):
        fp = dict(partial_fp)
        fp.update({'accent_hue': pal_meta['accent_hue'], 'paper_temperature': pal_meta['temperature'], 'button_style': axis_tokens['button_style'], 'radius': axis_tokens['radius'], 'section_order': [], 'faq': '', 'tour': ''})
        status, nid, dist, _ = FP.check(fp, registry, exclude_id='%s-%s' % (v['slug'], a.variant))
        return status, nid, dist

    t1 = time.time()
    ch, sel_report = PERS.select(libs, p, reg_check, forced=forced, content=v)
    timings['select_s'] = round(time.time() - t1, 2)
    pair = ch['pairing']
    sections, rhythm = section_plan(p, ch, v)

    # 3. images
    t1 = time.time()
    out_dir = os.path.abspath(a.out)
    os.makedirs(os.path.join(out_dir, 'img'), exist_ok=True)
    photos = {}
    for n, meta in items.items():
        role = 'hero' if n == lead else ('portrait' if 'portrait' in meta.get('tags', []) else 'large')
        extra = (400,) if ch['spaces']['id'] == 'spec-sheet' or ch['moment']['id'] == 'seat-picker' else ()
        info = I.build_set(paths[n], n, role, os.path.join(out_dir, 'img'), extra_widths=extra)
        default_w = I.pick_default(info['variants'], 1800 if n == lead else 1200)
        photos[n] = {'src': 'img/%s-%d.webp' % (n, default_w), 'srcset': I.srcset(n, info['variants']), 'width': info['variants'][-1][0], 'height': info['variants'][-1][1],
                     'alt': meta['alt'], 'focal': meta.get('focal', '50% 50%'), 'caption': caption_from_alt(meta['alt']), 'native': info['native'], 'variants': info['variants']}
    # manifest for QA (native = crop size of the original, from the source manifest)
    qa_manifest = [{'name': n, 'crop': manifest[n]['crop'] if n in manifest else photos[n]['native'], 'kept_copy_size': photos[n]['native'], 'variants': photos[n]['variants'], 'source_url': manifest.get(n, {}).get('source_url')} for n in photos]
    json.dump(qa_manifest, open(os.path.join(out_dir, 'img', 'manifest.json'), 'w'), indent=0)
    timings['images_s'] = round(time.time() - t1, 2)

    # 4. render
    t1 = time.time()
    env = Environment(loader=FileSystemLoader(os.path.join(HERE, 'templates')), autoescape=select_autoescape(['html', 'j2']), trim_blocks=True, lstrip_blocks=True)
    env.filters['wordnum'] = wordnum
    copy = resolve_copy(voices[ch['voice']['id']], v, copy_over)
    nav_style = 'minimal' if p['era'] >= 85 else ('centered' if (p['formality'] >= 75 and p['voice'] >= 60) else 'bar')
    guide_layout = 'plain' if p['density'] >= 80 else ('photo' if p['density'] <= 40 else 'band')
    light_photos = {'noon': next((n for n, m in items.items() if m.get('light') == 'day' and 'ceremony' in m.get('tags', []) and n != lead), 'flower'),
                    'golden': next((n for n, m in items.items() if m.get('light') == 'golden'), 'terrace'),
                    'night': next((n for n, m in items.items() if m.get('light') == 'night'), 'greenhouse')}
    looks = [s['name'].replace('The ', '').lower() for s in v['spaces']]
    ctx = dict(v=v, t=axis_tokens, pair=pair, ch={k: (val['id'] if isinstance(val, dict) else val) for k, val in ch.items()}, copy=copy, photos=photos, lead=lead,
               sections=sections, p=p, css_vars=P.css_vars(tokens), nav_style=nav_style, guide_layout=guide_layout, guide_photo='reception' if 'reception' in photos else lead,
               hero_sizes='100vw' if ch['hero']['id'] in ('masthead', 'cinematic') else ('(min-width: 1140px) 1040px, 92vw' if ch['hero']['id'] == 'frame' else '(min-width: 861px) 46vw, 100vw'),
               spaces_by_id={s['id']: s for s in v['spaces']}, story_second='bungalow' if 'bungalow' in photos else lead, light_photos=light_photos,
               uses_band='ink' if p['density'] >= 80 else 'deep', looks_sentence=', '.join(looks[:-1]) + ' and ' + looks[-1],
               seo={'title_tail': 'Garden Wedding Estate in %s' % v['tagline_facts']['locality'], 'description': ''},
               jsonld=jsonld(v, ''), build={'variant': a.variant, 'version': VERSION, 'fingerprint_short': ''})
    fp = {
        'display_family': pair['display']['family'], 'display_class': pair['display']['class'], 'body_family': pair['body']['family'],
        'accent_hue': pal_meta['accent_hue'], 'paper_temperature': pal_meta['temperature'],
        'hero': ch['hero']['id'], 'hero_family': ch['hero']['fingerprint']['hero_family'],
        'spaces': ch['spaces']['id'], 'story': ch['story']['id'], 'faq': ch['faq']['id'], 'tour': ch['tour']['id'],
        'section_order': ['hero'] + [s['id'] for s in sections], 'moment': ch['moment']['id'],
        'button_style': axis_tokens['button_style'], 'radius': axis_tokens['radius'], 'lead_photo': lead,
    }
    ctx['build']['fingerprint_short'] = hashlib.sha1(json.dumps(fp, sort_keys=True).encode()).hexdigest()[:8]
    html = env.get_template('base.html.j2').render(**ctx)
    open(os.path.join(out_dir, 'index.html'), 'w').write(html)
    timings['render_s'] = round(time.time() - t1, 2)

    # 5. fingerprint check
    site_id = '%s-%s' % (v['slug'], a.variant)
    status, nid, dist, rows = FP.check(fp, registry, exclude_id=site_id)
    timings['total_s'] = round(time.time() - t0, 2)
    meta = {'id': site_id, 'built': datetime.datetime.now().isoformat(timespec='seconds'), 'personality': p, 'axis_tokens': axis_tokens, 'choices': {k: (val['id'] if isinstance(val, dict) else val) for k, val in ch.items()},
            'selection': sel_report, 'rhythm': rhythm, 'nav_style': nav_style, 'guide_layout': guide_layout, 'pairing': {'display': pair['display'], 'body': pair['body'], 'id': pair['id']},
            'palette': {'tokens': tokens, 'report': pal_report, 'meta': pal_meta, 'photos': pal_names}, 'lead': lead, 'fingerprint': fp,
            'guard': {'status': status, 'nearest': nid, 'distance': round(dist, 3), 'all': rows}, 'timings': timings, 'html_bytes': len(html.encode())}
    json.dump(meta, open(os.path.join(out_dir, 'build-meta.json'), 'w'), indent=1, default=str)
    print('built %s -> %s (%d KB html) in %.1fs  [palette %.1fs, select %.1fs, images %.1fs, render %.2fs]' % (site_id, out_dir, len(html) // 1024, timings['total_s'], timings['palette_s'], timings['select_s'], timings['images_s'], timings['render_s']))
    print('  choices:', ', '.join('%s=%s' % (k, val) for k, val in meta['choices'].items()), '| nav', nav_style, '| guide', guide_layout)
    print('  palette: accent %s (hue %.0f from %s), deep %s, paper %s; all pairs pass: %s' % (tokens['accent'], pal_meta['accent_hue'], pal_meta['accent_from_photo'], tokens['deep'], tokens['paper'], pal_meta['all_pairs_pass']))
    print('  rhythm:', rhythm)
    for r in rows:
        print('  distance to %-24s %.3f  shared: %s' % (r['id'], r['distance'], ', '.join(r['shared']) or '-'))
    print('  guard: %s (nearest %s at %.3f)' % (status.upper(), nid, dist))
    if a.register and (status != 'refuse' or a.allow_close):
        FP.register(a.registry, site_id, fp, {'path': os.path.relpath(out_dir, os.path.dirname(HERE)), 'built': meta['built'], 'personality': p})
        print('  registered as', site_id)
    if status == 'refuse' and not a.allow_close:
        print('  REFUSED: too close to %s. Change a forced dimension or pass --allow-close.' % nid)
        sys.exit(2)


if __name__ == '__main__':
    main()
