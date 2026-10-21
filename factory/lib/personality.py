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


def rank(items, p, needs_ok=lambda it: True):
    rows = [(fit(it.get('axes', {}), p), it) for it in items if it.get('status', 'built') == 'built' and needs_ok(it)]
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


def select(libs, p, registry_check, forced=None, content=None, top=3):
    """libs: dict name -> list of items (pairings, heroes, spaces, story, faq, tour, moments, voices, gallery).
    registry_check: fn(fingerprint_dict) -> (status, nearest_id, distance).
    Returns (choices, candidates_report)."""
    forced = forced or {}
    content = content or {}

    def hero_needs_ok(h):
        n = h.get('needs', {})
        lead = content.get('_lead_width', 99999)
        return lead >= n.get('lead_min_width', 0)

    def moment_needs_ok(m):
        n = m.get('needs', {})
        if n.get('journey') and not content.get('journey'):
            return False
        if n.get('photos_by_light'):
            lights = {v.get('light') for v in content.get('photos', {}).get('items', {}).values()}
            if not set(n['photos_by_light']).issubset(lights):
                return False
        if n.get('day') and not content.get('day'):
            return False
        return True

    ranked = {
        'pairing': rank(libs['pairings'], p),
        'hero': rank(libs['heroes'], p, hero_needs_ok),
        'spaces': rank(libs['spaces'], p),
        'story': rank(libs['story'], p),
        'faq': rank(libs['faq'], p),
        'tour': rank(libs['tour'], p),
        'gallery': rank(libs['gallery'], p),
        'moment': rank(libs['moments'], p, moment_needs_ok),
        'voice': rank(libs['voices'], p),
    }
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
        fp = {
            'display_family': choice['pairing']['display']['family'], 'display_class': choice['pairing']['display']['class'],
            'body_family': choice['pairing']['body']['family'],
            'hero': choice['hero']['id'], 'hero_family': choice['hero']['fingerprint']['hero_family'],
            'spaces': choice['spaces']['id'], 'story': choice['story']['id'], 'moment': choice['moment']['id'],
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
              'guard': {'status': best[2], 'nearest': best[3], 'distance': round(best[4], 3)}}
    return choices, report
