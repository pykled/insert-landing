"""Site fingerprint + diversity guard (registry schema 2, spec 05 section 6).

A fingerprint is the small set of choices a visitor actually perceives as 'the look':
  pairing (display family + class), accent hue + paper temperature, hero archetype + family, section archetypes +
  order, signature moment, button style, corner radius, and (schema 2) paper tone, hero framing, display case,
  ornament, body size bucket, photo edge, motion device, nav style. `dialect` and `pairing` are stored but carry no
  weight: sharing a dialect is expected; they drive the same-dialect rule and the quota below.

distance(a, b) in [0, 1]:
  weighted sum of per-dimension distances. Categorical dims are 0/1; hue is angular distance / 180; section order is
  1 - (normalised longest common subsequence). Schema-2 weights = the schema-1 weights x 0.66 plus 0.34 for the new
  dimensions (spec 6.2 item 1), so the total stays 1.0.

Rules, per registered site:
  different (or no) dialect   < 0.35 REFUSE, < 0.50 WARN
  same dialect                < 0.32 REFUSE, < 0.45 WARN, and REFUSE unless at least 4 of the 7 key dimensions differ
                              (pairing, hero framing, ornament, paper tone, spaces, moment, body size)
Quota: the 2nd registered site sharing dialect + pairing + hero framing WARNS, the 3rd REFUSES.
Screenshot pHash (lib/phash.py, captured by qa.py): Hamming <= 18/256 WARN, <= 12 REFUSE on the fold or strip hash.

CLI
  fingerprint.py <registry.json> --matrix                        distance matrix (same-dialect pairs marked *)
  fingerprint.py <registry.json> <build-meta.json | site id>      distances + rule verdicts for one site
  fingerprint.py <registry.json> --set-phash <site id> <qa-report.json>   store a site's pHash from a QA run
"""
import datetime, json, os, sys

SCHEMA_VERSION = 2

WEIGHTS_V1 = {
    'display_family': 0.16, 'display_class': 0.06, 'body_family': 0.06, 'accent_hue': 0.12, 'paper_temperature': 0.04,
    'hero': 0.14, 'hero_family': 0.06, 'spaces': 0.08, 'story': 0.04, 'faq': 0.02, 'tour': 0.03, 'section_order': 0.07,
    'moment': 0.08, 'button_style': 0.02, 'radius_bucket': 0.02,
}
NEW_WEIGHTS = {
    'paper_tone': 0.06, 'hero_framing': 0.06, 'display_case': 0.04, 'ornament': 0.06,
    'body_px': 0.03, 'photo_edge': 0.03, 'motion_device': 0.03, 'nav_style': 0.03,
}
WEIGHTS = {k: round(v * 0.66, 6) for k, v in WEIGHTS_V1.items()}
WEIGHTS.update(NEW_WEIGHTS)
assert abs(sum(WEIGHTS.values()) - 1.0) < 1e-6

CATEGORICAL = ('display_family', 'display_class', 'body_family', 'hero', 'hero_family', 'spaces', 'story', 'faq', 'tour', 'moment',
               'button_style', 'paper_temperature', 'paper_tone', 'hero_framing', 'display_case', 'ornament', 'photo_edge',
               'motion_device', 'nav_style')
SAME_DIALECT_KEYS = ('pairing', 'hero_framing', 'ornament', 'paper_tone', 'spaces', 'moment', 'body_px')
SAME_DIALECT_MIN_DIFF = 4
REFUSE, WARN = 0.35, 0.50
SAME_REFUSE, SAME_WARN = 0.32, 0.45
QUOTA_WARN, QUOTA_REFUSE = 1, 2   # number of existing sites sharing dialect + pairing + hero framing
DEFAULTS = {'dialect': None, 'pairing': None, 'paper_tone': None, 'hero_framing': None, 'display_case': 'sentence', 'ornament': 'none',
            'body_px': 17, 'photo_edge': 'flush', 'motion_device': 'none', 'nav_style': None}
ORDER = {'ok': 0, 'warn': 1, 'refuse': 2}


def _lcs(a, b):
    m, n = len(a), len(b)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m):
        for j in range(n):
            dp[i + 1][j + 1] = dp[i][j] + 1 if a[i] == b[j] else max(dp[i][j + 1], dp[i + 1][j])
    return dp[m][n]


def radius_bucket(px):
    return 'square' if px <= 2 else ('soft' if px <= 8 else 'round')


def body_bucket(px):
    """17 / 19 / 21 (spec section 4 item 7)."""
    px = float(px or 17)
    return 17 if px < 18 else (19 if px < 20 else 21)


def paper_tone_of(hex_):
    """Classify a paper colour into light / mid / tinted / dark-warm / dark-cool (sites built without a dialect)."""
    from . import color as C
    L, Ch, h = (float(x) for x in C.hex_to_lch(hex_))
    if L < 0.35:
        return 'dark-warm' if C.is_warm(h) else 'dark-cool'
    if Ch >= 0.010:   # B's lush cream (C 0.011) reads tinted; A/C near-white and the v2 mock cream (C 0.009) do not
        return 'tinted'
    return 'light' if L >= 0.965 else 'mid'


def _norm(fp, k):
    v = fp.get(k, DEFAULTS.get(k))
    return body_bucket(v) if k == 'body_px' else v


def distance(a, b, explain=False):
    parts = {}
    for k in CATEGORICAL:
        parts[k] = 0.0 if _norm(a, k) == _norm(b, k) else 1.0
    d = abs(a['accent_hue'] - b['accent_hue']) % 360
    parts['accent_hue'] = min(d, 360 - d) / 180
    parts['radius_bucket'] = 0.0 if radius_bucket(a.get('radius', 0)) == radius_bucket(b.get('radius', 0)) else 1.0
    parts['body_px'] = 0.0 if _norm(a, 'body_px') == _norm(b, 'body_px') else 1.0
    sa, sb = a.get('section_order', []), b.get('section_order', [])
    parts['section_order'] = 1 - (_lcs(sa, sb) / max(len(sa), len(sb), 1))
    total = sum(WEIGHTS[k] * v for k, v in parts.items())
    if explain:
        return total, {k: round(WEIGHTS[k] * v, 3) for k, v in sorted(parts.items(), key=lambda kv: -WEIGHTS[kv[0]] * kv[1]) if v > 0}
    return total


def same_dialect(a, b):
    da, db = a.get('dialect'), b.get('dialect')
    return bool(da) and da != 'none' and da == db


def key_differences(a, b):
    return [k for k in SAME_DIALECT_KEYS if _norm(a, k) != _norm(b, k)]


def pair_verdict(a, b):
    """(status, distance, why, drivers) for one pair of fingerprints."""
    d, drivers = distance(a, b, explain=True)
    if same_dialect(a, b):
        diff = key_differences(a, b)
        status = 'refuse' if d < SAME_REFUSE else ('warn' if d < SAME_WARN else 'ok')
        why = 'same dialect %s: %.3f vs %.2f/%.2f; %d of 7 key dims differ (%s)' % (a['dialect'], d, SAME_REFUSE, SAME_WARN, len(diff), ', '.join(diff) or '-')
        if len(diff) < SAME_DIALECT_MIN_DIFF:
            status = 'refuse'
            why += ' < %d required' % SAME_DIALECT_MIN_DIFF
    else:
        status = 'refuse' if d < REFUSE else ('warn' if d < WARN else 'ok')
        why = '%.3f vs %.2f/%.2f' % (d, REFUSE, WARN)
    return status, d, why, drivers


def quota(fp, registry, exclude_id=None):
    """(status, ids) for the dialect + pairing + hero framing quota."""
    if not fp.get('dialect') or fp.get('dialect') == 'none':
        return 'ok', []
    key = (fp.get('dialect'), fp.get('pairing'), fp.get('hero_framing'))
    ids = [s['id'] for s in registry.get('sites', []) if s['id'] != exclude_id and
           (s['fingerprint'].get('dialect'), s['fingerprint'].get('pairing'), s['fingerprint'].get('hero_framing')) == key]
    status = 'refuse' if len(ids) >= QUOTA_REFUSE else ('warn' if len(ids) >= QUOTA_WARN else 'ok')
    return status, ids


def load_registry(path):
    if not os.path.exists(path):
        return {'schema_version': SCHEMA_VERSION, 'sites': []}
    return json.load(open(path))


def guard(fp, registry, exclude_id=None):
    """Full verdict: {'status', 'nearest', 'distance', 'driver', 'rows', 'quota'}. status is the worst of every rule;
    `driver` is the site (or quota) that set it, the nearest site when everything is ok."""
    rows = []
    for s in registry.get('sites', []):
        if s['id'] == exclude_id:
            continue
        st, d, why, drivers = pair_verdict(fp, s['fingerprint'])
        shared = [k for k in WEIGHTS if k not in ('accent_hue', 'section_order', 'radius_bucket') and _norm(fp, k) == _norm(s['fingerprint'], k)]
        rows.append({'id': s['id'], 'distance': round(d, 3), 'status': st, 'rule': why, 'shared': shared, 'drivers': drivers,
                     'same_dialect': same_dialect(fp, s['fingerprint'])})
    rows.sort(key=lambda r: r['distance'])
    q_status, q_ids = quota(fp, registry, exclude_id)
    out = {'status': 'ok', 'nearest': rows[0]['id'] if rows else None, 'distance': rows[0]['distance'] if rows else 1.0,
           'driver': None, 'rows': rows,
           'quota': {'status': q_status, 'sharing': q_ids, 'key': [fp.get('dialect'), fp.get('pairing'), fp.get('hero_framing')]}}
    for r in rows:
        if ORDER[r['status']] > ORDER[out['status']]:
            out['status'], out['driver'] = r['status'], r['id']
    if ORDER[q_status] > ORDER[out['status']]:
        out['status'], out['driver'] = q_status, 'quota:' + ','.join(q_ids)
    out['driver'] = out['driver'] or out['nearest']
    return out


def check(fp, registry, exclude_id=None):
    """(status, driver_id, nearest_distance, rows), the schema-1 call signature."""
    g = guard(fp, registry, exclude_id)
    return g['status'], g['driver'], g['distance'], g['rows']


def register(registry_path, site_id, fp, meta, allow_close=None, phash=None):
    """Add or replace a site. allow_close: the human's reason when registering a site the guard refused.
    A stored pHash survives re-registration unless a new one is passed."""
    reg = load_registry(registry_path)
    old = next((s for s in reg['sites'] if s['id'] == site_id), None)
    reg['sites'] = [s for s in reg['sites'] if s['id'] != site_id]
    entry = {'id': site_id, 'fingerprint': fp, 'meta': meta}
    if allow_close:
        entry['allow_close'] = allow_close
    if phash or (old and old.get('phash')):
        entry['phash'] = phash or old['phash']
    reg['sites'].append(entry)
    reg['schema_version'] = SCHEMA_VERSION
    json.dump(reg, open(registry_path, 'w'), indent=1)


def set_phash(registry_path, site_id, hashes):
    reg = load_registry(registry_path)
    site = next(s for s in reg['sites'] if s['id'] == site_id)
    site['phash'] = {'fold': hashes['fold'], 'strip': hashes['strip'], 'captured': hashes.get('captured') or datetime.date.today().isoformat()}
    json.dump(reg, open(registry_path, 'w'), indent=1)


def matrix_lines(reg):
    ids = [s['id'] for s in reg['sites']]
    lines = ['%-26s' % '' + ''.join('%-14s' % i[:13] for i in ids)]
    for s in reg['sites']:
        cells = []
        for t in reg['sites']:
            d = distance(s['fingerprint'], t['fingerprint'])
            mark = '*' if (s is not t and same_dialect(s['fingerprint'], t['fingerprint'])) else ' '
            cells.append('%-14s' % ('%.3f%s' % (d, mark)))
        lines.append('%-26s' % s['id'][:25] + ''.join(cells))
    lines.append('(* same dialect: refuse < %.2f, warn < %.2f, and >= %d of 7 key dims must differ; otherwise refuse < %.2f, warn < %.2f)'
                 % (SAME_REFUSE, SAME_WARN, SAME_DIALECT_MIN_DIFF, REFUSE, WARN))
    return lines


if __name__ == '__main__':
    reg = load_registry(sys.argv[1])
    if '--matrix' in sys.argv:
        print('\n'.join(matrix_lines(reg)))
        sys.exit(0)
    if '--set-phash' in sys.argv:
        i = sys.argv.index('--set-phash')
        sid, rep = sys.argv[i + 1], json.load(open(sys.argv[i + 2]))
        set_phash(sys.argv[1], sid, rep['info']['phash'])
        print('stored phash for', sid)
        sys.exit(0)
    arg = sys.argv[2]
    if os.path.exists(arg):
        meta = json.load(open(arg)); fp = meta['fingerprint']; sid = meta.get('id')
    else:
        sid = arg; fp = next(s['fingerprint'] for s in reg['sites'] if s['id'] == sid)
    g = guard(fp, reg, exclude_id=sid)
    for r in g['rows']:
        print('%-26s %.3f %-6s %s  drivers=%s' % (r['id'], r['distance'], r['status'], r['rule'], r['drivers']))
    print('quota %s %s' % (g['quota']['status'], g['quota']['sharing'] or '-'))
    print('\nnearest: %s at %.3f -> %s (driver %s)' % (g['nearest'], g['distance'], g['status'].upper(), g['driver']))
    sys.exit({'ok': 0, 'warn': 0, 'refuse': 2}[g['status']])
