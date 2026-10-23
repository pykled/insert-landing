"""Personality model -> design choices.

Six axes, each 0..100:
  formality   0 rustic ............ 100 refined
  scale       0 intimate .......... 100 grand
  era         0 heritage .......... 100 modern
  density     0 lush / layered .... 100 minimal / airy
  temperature 0 warm .............. 100 cool
  voice       0 romantic .......... 100 editorial / plainspoken

Every library item (pairing, hero, section archetype, moment, voice) carries an `axes` position on the
same scale. Fit = RMS distance over the axes the item declares. The selector takes the top-3 per
dimension and scores every combination by fit PLUS a penalty when the resulting fingerprint is too
close to a site already in the registry (the diversity guard is inside the selector, not bolted on
after). Explicit choices passed on the command line always win and are reported as 'forced'.

Continuous tokens (radius, tracking, spacing, button style, image edge) are direct functions of the
axes; see tokens_from_axes().
"""
import itertools, math

AXES = ('formality', 'scale', 'era', 'density', 'temperature', 'voice')


def fit(item_axes, p):
    ks = [k for k in item_axes if k in p]
    if not ks:
        return 0.5
    return math.sqrt(sum(((item_axes[k] - p[k]) / 100) ** 2 for k in ks) / len(ks))


PLANNED = ('built', 'mock-only', 'spec', 'planned-2B')


def rank(items, p, needs_ok=lambda it: True, dialect_mode=False):
    """Pre-dialect builds: only built items that are not dialect_only (so the three proof variants are unchanged).
    Dialect builds: the caller has already narrowed items to the dialect's ids; anything specified may be chosen and
    build.py resolves a not-yet-built template to the nearest existing one (lib/templates.py), recording the fallback."""
    if dialect_mode:
        ok_status = lambda it: it.get('status', 'built') in PLANNED
    else:
        ok_status = lambda it: it.get('status', 'built') == 'built' and not it.get('dialect_only')
    # `_use_penalty` (dialect builds only, set by build.py): spreads registered sites of one dialect over its pairings
    rows = [(fit(it.get('axes', {}), p) + it.get('_use_penalty', 0.0), it) for it in items if ok_status(it) and needs_ok(it)]
    rows.sort(key=lambda r: r[0])
    return rows


def tokens_from_axes(p):
    f, s, e, d, t, v = (p[k] for k in AXES)
    radius = round(10 * (1 - f / 100) * (1 - e / 100 * 0.5))  # rustic + heritage -> rounder
    if e >= 85:
        radius = 0
    pill = (f < 45 and t < 45)
    button_style = 'pill-solid' if pill else ('square-solid' if e >= 80 else ('square-outline-caps' if f >= 60 else 'soft-solid'))
    caps = f >= 55 and e < 85          # uppercase tracked kickers for refined-classic; sentence-case labels for modern/rustic
    kicker_style = 'caps-rule' if caps else ('italic' if (v < 40) else 'label')
    section_pad = [72 + int(0.6 * d), 130 + int(0.9 * d)]  # minimal personalities breathe more
    container = 1120 + int(1.8 * s)   # grand -> wider measure
    gutter = 'clamp(20px, 4vw, %dpx)' % (40 + int(0.3 * d))
    image_edge = 'rounded' if radius >= 6 else ('keyline' if (f >= 70 and e < 70) else 'flush')
    shadow = 'warm' if t < 40 and f < 60 else ('none' if d >= 80 else 'soft')
    reveal = 'none' if d >= 85 else ('slide' if d < 40 else 'fade')
    display_scale = 1.0 + 0.25 * (s / 100) + (0.08 if v >= 70 else 0)  # grand + editorial -> bigger display sizes
    rule_style = 'hairline' if f >= 55 else 'none'
    return {
        'radius': radius, 'radius_card': max(radius, 2 if e < 85 else 0), 'button_style': button_style, 'kicker_style': kicker_style,
        'section_pad_min': section_pad[0], 'section_pad_max': section_pad[1], 'container': container, 'gutter': gutter,
        'image_edge': image_edge, 'shadow': shadow, 'reveal': reveal, 'display_scale': round(display_scale, 2), 'rule_style': rule_style,
        'caps': caps,
    }


def moment_needs_ok_for(m, content):
    """Can this content feed the moment? (also used for template fallbacks: a fallback must meet its own needs)"""
    items = (content.get('photos') or {}).get('items', {})
    n = m.get('needs', {})
    if n.get('journey') and not content.get('journey'):
        return False
    if n.get('photos_by_light'):
        lights = {v.get('light') for v in content.get('photos', {}).get('items', {}).values()}
        if not set(n['photos_by_light']).issubset(lights):
            return False
    if n.get('day') and not any((content.get('day') or {}).get(k) for k in ('gates_open', 'event_end', 'rental_hours')):
        return False
    if n.get('max_guests') and not (content.get('tagline_facts') or {}).get('max_guests'):
        return False
    if n.get('capacities') and sum(1 for s in content.get('spaces') or [] if s.get('capacity')) < 2:
        return False
    if n.get('photos') and len(items) < n['photos']:
        return False
    if n.get('numbers') and len(content.get('numbers') or []) < n['numbers']:
        return False
    if n.get('flora') and not any(m.get('flora') for m in items.values()):
        return False
    if n.get('archival') and not any(m.get('archival') for m in items.values()):
        return False
    return True


def select(libs, p, registry_check, forced=None, content=None, top=3, dialect_mode=False, resolve=None):
    """libs: dict name -> list of items (pairings, heroes, spaces, story, faq, tour, moments, voices, gallery).
    registry_check: fn(fingerprint_dict) -> (status, nearest_id, distance).
    dialect_mode: libs are already narrowed to one dialect's ids (see rank()).
    resolve: fn(dim, item) -> the item that will actually render (template fallback); the guard scores that one.
    Returns (choices, candidates_report)."""
    forced = forced or {}
    content = content or {}
    resolve = resolve or (lambda dim, it: it)
    items = (content.get('photos') or {}).get('items', {})

    def hero_needs_ok(h):
        n = h.get('needs', {})
        lead = content.get('_lead_width', 99999)
        if lead < n.get('lead_min_width', 0):
            return False
        if n.get('photos') and len(items) < n['photos']:
            return False
        if n.get('lead_subject') and (items.get(content.get('_lead')) or {}).get('subject') not in n['lead_subject']:
            return False
        # copy on the photo: the lead must be dark enough in the copy zone (lib/palette.copy_zone_contrast), unless the
        # hero can set its copy on paper instead (crest-centred paper mode); build.py renders that mode
        z = n.get('copy_zone')
        cz, zmin = content.get('_copy_zone') or {}, content.get('_copy_zone_min', 4.5)
        if z and not n.get('paper_mode_ok') and cz.get(z, 99) < zmin:
            # 2D: a hero that can lay a blur veil under its copy (cinematic) stays eligible when the veiled estimate passes
            if not (n.get('veil_zone') and cz.get(n['veil_zone'], 0) >= zmin):
                return False
        return True

    moment_needs_ok = lambda m: moment_needs_ok_for(m, content)

    dm = dialect_mode
    ranked = {
        'pairing': rank(libs['pairings'], p, dialect_mode=dm),
        'hero': rank(libs['heroes'], p, hero_needs_ok, dialect_mode=dm),
        'spaces': rank(libs['spaces'], p, dialect_mode=dm),
        'story': rank(libs['story'], p, dialect_mode=dm),
        'faq': rank(libs['faq'], p, dialect_mode=dm),
        'tour': rank(libs['tour'], p, dialect_mode=dm),
        'gallery': rank(libs['gallery'], p, dialect_mode=dm),
        'moment': rank(libs['moments'], p, moment_needs_ok, dialect_mode=dm),
        'voice': rank(libs['voices'], p, dialect_mode=dm),
    }
    relaxed = []
    if dm:
        # a dialect may list nothing the content can feed (e.g. every hero wants a 2400px lead): relax needs, record it,
        # and let template resolution pick the nearest buildable fallback; a dialect with no moment gets 'none'.
        if not ranked['hero']:
            ranked['hero'] = rank(libs['heroes'], p, dialect_mode=dm); relaxed.append('hero')
        if not ranked['moment']:
            ranked['moment'] = [(0.5, {'id': 'none', 'status': 'built', 'fingerprint': {}})]; relaxed.append('moment')
    pools = {}
    for dim, rows in ranked.items():
        if dim in forced:
            pools[dim] = [(0.0, next(it for it in libs[{'pairing': 'pairings', 'hero': 'heroes', 'moment': 'moments', 'voice': 'voices'}.get(dim, dim)] if it['id'] == forced[dim]))]
        else:
            pools[dim] = rows[:top]
    # Only the dims that matter to the fingerprint get combined; the rest take their best fit.
    combo_dims = ['pairing', 'hero', 'spaces', 'moment', 'story']
    best = None
    tried = []
    for combo in itertools.product(*[pools[d] for d in combo_dims]):
        choice = {d: c[1] for d, c in zip(combo_dims, combo)}
        fitsum = sum(c[0] for c in combo)
        rh = resolve('hero', choice['hero'])
        fp = {
            'display_family': choice['pairing']['display']['family'], 'display_class': choice['pairing']['display']['class'],
            'body_family': choice['pairing']['body']['family'], 'pairing': choice['pairing']['id'],
            'hero': rh['id'], 'hero_family': rh['fingerprint']['hero_family'], 'hero_framing': rh['fingerprint'].get('hero_framing'),
            'spaces': resolve('spaces', choice['spaces'])['id'], 'story': resolve('story', choice['story'])['id'],
            'moment': resolve('moment', choice['moment'])['id'],
        }
        status, nid, dist = registry_check(fp)
        penalty = 0.0 if status == 'ok' else (0.35 if status == 'warn' else 1.5)
        score = fitsum + penalty
        tried.append((round(score, 3), round(fitsum, 3), status, nid, round(dist, 3), {d: choice[d]['id'] for d in combo_dims}))
        if best is None or score < best[0]:
            best = (score, choice, status, nid, dist)
    tried.sort(key=lambda r: r[0])
    choices = dict(best[1])
    for dim in ('faq', 'tour', 'gallery', 'voice'):
        choices[dim] = pools[dim][0][1]
    report = {'ranked': {d: [(round(f, 3), it['id']) for f, it in rows] for d, rows in ranked.items()}, 'top_combos': tried[:6], 'forced': forced,
              'guard': {'status': best[2], 'nearest': best[3], 'distance': round(best[4], 3)}, 'needs_relaxed': relaxed}
    return choices, report


# ---------------------------------------------------------------------------------------------------------------
# Dialect layer (docs/research/05-luxury-dialects-spec.md section 3). A dialect is chosen BEFORE fit-ranked selection:
# score every dialect from the photo signals + the content vibe block + a venue-type prior, take the top score
# (ties: the dialect with fewer registered sites, then the order in data/dialects.json), clamp the six axes to the
# dialect's region, then let select() run unchanged over the dialect's allowed ids. Pure functions, no randomness:
# the same inputs always give the same table.

def _rule(table, dialect, pts, why):
    table.setdefault(dialect, []).append((why, pts))


def score_dialects(dialects_doc, signals, content=None, palette_meta=None, registry=None):
    """Return (winner_id, rows). rows: one dict per dialect, sorted best first:
       {'id', 'score', 'reasons': [[why, points], ...], 'registered': n}
    signals: lib.palette.photo_signals() output. palette_meta: lib.palette.derive() meta (candidates, temperature).
    content: the venue content dict (vibe block, photo tags)."""
    content = content or {}
    pm = palette_meta or {}
    ids = [d['id'] for d in dialects_doc['dialects']]
    t = {}
    s = signals or {}
    if s.get('dark_share', 0) >= 0.45 and s.get('warm_shadows'):
        _rule(t, 'candlelit', 3, 'dark share %.2f >= 0.45 with warm shadows' % s['dark_share'])
    if s.get('mean_L', 0) >= 0.62 and s.get('water_share', 0) >= 0.25:
        _rule(t, 'coastal', 3, 'mean L %.2f >= 0.62 and water/sky share %.2f >= 0.25' % (s['mean_L'], s['water_share']))
    if s.get('foliage_share', 0) >= 0.40:
        _rule(t, 'botanical', 3, 'foliage share %.2f >= 0.40' % s['foliage_share'])
        _rule(t, 'ranch', 1, 'foliage share %.2f >= 0.40' % s['foliage_share'])
    if s.get('earth_share', 0) >= 0.35 and s.get('foliage_share', 0) < 0.30:
        _rule(t, 'estate', 2, 'stone/earth share %.2f >= 0.35, foliage < 0.30' % s['earth_share'])
        _rule(t, 'ranch', 1, 'stone/earth share %.2f >= 0.35, foliage < 0.30' % s['earth_share'])
    if s.get('mono_share', 0) >= 0.70 and s.get('mean_L', 0) >= 0.55:
        _rule(t, 'modern-luxe', 2, 'mono share %.2f >= 0.70 and mean L >= 0.55' % s['mono_share'])
        _rule(t, 'deco', 1, 'mono share %.2f >= 0.70 and mean L >= 0.55' % s['mono_share'])
    items = (content.get('photos') or {}).get('items', {})
    if any(m.get('mono') or m.get('archival') for m in items.values()):
        _rule(t, 'deco', 2, 'a photo is tagged mono or archival')
    cands = pm.get('candidates') or []
    max_c = max([c.get('C', 0) for c in cands] or [0])
    if max_c >= 0.12:
        _rule(t, 'deco', 1, 'accent candidate chroma %.3f >= 0.12' % max_c)
        _rule(t, 'candlelit', 1, 'accent candidate chroma %.3f >= 0.12' % max_c)
    if cands:
        top = cands[0]
        if 60 <= top.get('h', -1) <= 90 and top.get('C', 0) >= 0.07 and s.get('foliage_share', 0) >= 0.2:
            _rule(t, 'ranch', 2, 'warm ochre accent (H %.0f, C %.3f) with foliage >= 0.2' % (top['h'], top['C']))
    temp = pm.get('temperature')
    if temp == 'warm':
        for d in ('estate', 'ranch', 'botanical'):
            _rule(t, d, 1, 'paper temperature warm')
    elif temp == 'cool':
        for d in ('coastal', 'modern-luxe'):
            _rule(t, d, 1, 'paper temperature cool')
    vibe = content.get('vibe') or {}
    for d, pts in (dialects_doc.get('type_priors', {}).get(vibe.get('type') or '', {}) or {}).items():
        _rule(t, d, pts, 'type prior: %s' % vibe.get('type'))
    era = vibe.get('era')
    if isinstance(era, int):
        if 1920 <= era <= 1945:
            _rule(t, 'deco', 2, 'era %d in 1920-1945' % era)
        if era <= 1930:
            _rule(t, 'estate', 1, 'era %d <= 1930' % era)
            if not (1920 <= era <= 1945):
                _rule(t, 'deco', 1, 'era %d <= 1930' % era)
        if era >= 2005:
            _rule(t, 'modern-luxe', 1, 'era %d >= 2005' % era)
    pts = dialects_doc.get('vibe_word_points', 2)
    for w in vibe.get('words') or []:
        d = dialects_doc.get('vibe_words', {}).get(w)
        if d:
            _rule(t, d, pts, 'vibe word "%s"' % w)
    counts = {}
    for site in (registry or {}).get('sites', []):
        dd = site.get('fingerprint', {}).get('dialect')
        if dd:
            counts[dd] = counts.get(dd, 0) + 1
    rows = [{'id': d, 'score': sum(p for _, p in t.get(d, [])), 'reasons': [[w, p] for w, p in t.get(d, [])], 'registered': counts.get(d, 0)} for d in ids]
    order = {d: i for i, d in enumerate(ids)}
    rows.sort(key=lambda r: (-r['score'], r['registered'], order[r['id']]))
    return rows[0]['id'], rows


def clamp_axes(p, dialect):
    """Clamp each axis into the dialect's [lo, hi] range. Returns (clamped, changes) where changes lists
    [axis, before, after] for every axis that moved. Also keeps the spec-sheet SaaS corner (density >= 85 with
    voice >= 85, exclusion 17) out of every dialect except modern-luxe."""
    out, changes = dict(p), []
    for k in AXES:
        lo, hi = dialect['axes'][k]
        v = min(max(float(p.get(k, 50)), lo), hi)
        if v != p.get(k):
            changes.append([k, p.get(k), v])
        out[k] = v
    if dialect['id'] != 'modern-luxe' and out['density'] >= 85 and out['voice'] >= 85:
        changes.append(['voice', out['voice'], 84.0])
        out['voice'] = 84.0
    return out, changes


def axes_centre(dialect):
    return {k: (lo + hi) / 2.0 for k, (lo, hi) in dialect['axes'].items()}


def pick_in_range(options, axis_value, lo, hi):
    """Deterministic pick from an ordered list by where axis_value sits inside [lo, hi] (first = lo end)."""
    if not options:
        return None
    if len(options) == 1 or hi <= lo:
        return options[0]
    pos = (axis_value - lo) / float(hi - lo)
    return options[min(int(pos * len(options)), len(options) - 1)]


def paper_tone(dialect, p, signals):
    """light / mid / tinted for light dialects (dense, lush personalities get tinted stock); dark-warm / dark-cool for
    dark grounds (from the shadows). A light dialect with a charcoal variant (estate castle, deco) switches to it when
    the photos are dark (dark share >= 0.45, or mean L < 0.45 for deco)."""
    s = signals or {}
    dark_tone = 'dark-warm' if s.get('warm_shadows', True) else 'dark-cool'
    if dialect['paper']['mode'] == 'dark':
        return dark_tone if dark_tone in dialect['paper']['tones'] else dialect['paper']['tones'][0]
    pd = dialect.get('paper_dark')
    if pd and (s.get('dark_share', 0) >= 0.45 or (dialect['id'] == 'deco' and s.get('mean_L', 1) < 0.45)):
        return dark_tone if dark_tone in pd['tones'] else pd['tones'][0]
    tones = dialect['paper']['tones']
    lo, hi = dialect['axes']['density']
    # density high (airy) -> light; low (lush) -> the most tinted tone the dialect allows
    return pick_in_range(list(reversed(tones)), p['density'], lo, hi)


def dialect_tokens(dialect, p, pairing, registry=None):
    """Within-dialect knobs that are not archetypes (spec section 4): body size, headline case, photo edge, kicker style."""
    lo, hi = dialect['axes']['density']
    body_px = pick_in_range(dialect['type']['body_px'], p['density'], lo, hi)
    allowed_case = dialect['type']['headline_case']
    pc = (pairing.get('display') or {}).get('case', 'sentence')
    case = pc if pc in allowed_case else allowed_case[0]
    flo, fhi = dialect['axes']['formality']
    edge = pick_in_range(dialect['photo']['edges'], p['formality'], flo, fhi)
    kicker = pick_in_range(dialect['type']['kicker_styles'], p['voice'], *dialect['axes']['voice'])
    return {'body_px': body_px, 'display_case': case, 'photo_edge': edge, 'kicker_style': kicker}


USE_PENALTY = 0.04   # per registered same-dialect site already on a pairing; about a third of the fit spread inside a dialect


def usage_penalised(items, used_counts, per_use=USE_PENALTY):
    """Copies of `items` with `_use_penalty` = per_use x the number of registered same-dialect sites that use each id,
    so rank() prefers the least-used option when fits are close (spec 4.3: vary the pairing inside a dialect)."""
    out = []
    for it in items:
        n = used_counts.get(it['id'], 0)
        out.append(dict(it, _use_penalty=per_use * n) if n else it)
    return out


def rotate_pick(options, used_counts, last=None):
    """Least-used option among registered sites of the same dialect; never repeat `last` when another option exists;
    ties go to list order. Deterministic."""
    pool = [o for o in options if o != last] or list(options)
    return sorted(pool, key=lambda o: (used_counts.get(o, 0), options.index(o)))[0]
