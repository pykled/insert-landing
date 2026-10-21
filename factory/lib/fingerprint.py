"""Site fingerprint + diversity guard.

A fingerprint is the small set of choices a visitor actually perceives as 'the look':
  pairing (display family + class), accent hue family + paper temperature, hero archetype family,
  section archetypes + order, signature moment, nav style, corner radius, button style, lead photo.

distance(a, b) in [0, 1]:
  weighted sum of per-dimension distances. Categorical dims are 0/1; hue is angular distance / 180;
  section order is 1 - (normalised longest-common-subsequence of the archetype sequence).

Thresholds (tuned on the two existing mocks + the three variants, see docs/venue-site-factory.md):
  < 0.35  REFUSE  (reads as the same site with new photos)
  < 0.50  WARN    (a repeat visitor would notice the family resemblance)
  >= 0.50 OK
"""
import json, os, sys

WEIGHTS = {
    'display_family': 0.16,
    'display_class': 0.06,
    'body_family': 0.06,
    'accent_hue': 0.12,
    'paper_temperature': 0.04,
    'hero': 0.14,
    'hero_family': 0.06,
    'spaces': 0.08,
    'story': 0.04,
    'faq': 0.02,
    'tour': 0.03,
    'section_order': 0.07,
    'moment': 0.08,
    'button_style': 0.02,
    'radius_bucket': 0.02,
}
assert abs(sum(WEIGHTS.values()) - 1.0) < 1e-9

REFUSE, WARN = 0.35, 0.50


def _lcs(a, b):
    m, n = len(a), len(b)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m):
        for j in range(n):
            dp[i + 1][j + 1] = dp[i][j] + 1 if a[i] == b[j] else max(dp[i][j + 1], dp[i + 1][j])
    return dp[m][n]


def radius_bucket(px):
    return 'square' if px <= 2 else ('soft' if px <= 8 else 'round')


def distance(a, b, explain=False):
    parts = {}
    for k in ('display_family', 'display_class', 'body_family', 'hero', 'hero_family', 'spaces', 'story', 'faq', 'tour', 'moment', 'button_style', 'paper_temperature'):
        parts[k] = 0.0 if a.get(k) == b.get(k) else 1.0
    d = abs(a['accent_hue'] - b['accent_hue']) % 360
    parts['accent_hue'] = min(d, 360 - d) / 180
    parts['radius_bucket'] = 0.0 if radius_bucket(a.get('radius', 0)) == radius_bucket(b.get('radius', 0)) else 1.0
    sa, sb = a.get('section_order', []), b.get('section_order', [])
    parts['section_order'] = 1 - (_lcs(sa, sb) / max(len(sa), len(sb), 1))
    total = sum(WEIGHTS[k] * v for k, v in parts.items())
    if explain:
        return total, {k: round(WEIGHTS[k] * v, 3) for k, v in sorted(parts.items(), key=lambda kv: -WEIGHTS[kv[0]] * kv[1]) if v > 0}
    return total


def load_registry(path):
    if not os.path.exists(path):
        return {'sites': []}
    return json.load(open(path))


def check(fp, registry, exclude_id=None):
    """Return (status, nearest_id, nearest_distance, all_distances)."""
    rows = []
    for s in registry['sites']:
        if s['id'] == exclude_id:
            continue
        d, why = distance(fp, s['fingerprint'], explain=True)
        rows.append({'id': s['id'], 'distance': round(d, 3), 'shared': [k for k in WEIGHTS if fp.get(k) == s['fingerprint'].get(k) and k not in ('accent_hue', 'section_order', 'radius_bucket')], 'drivers': why})
    rows.sort(key=lambda r: r['distance'])
    if not rows:
        return 'ok', None, 1.0, rows
    n = rows[0]
    status = 'refuse' if n['distance'] < REFUSE else ('warn' if n['distance'] < WARN else 'ok')
    return status, n['id'], n['distance'], rows


def register(registry_path, site_id, fp, meta):
    reg = load_registry(registry_path)
    reg['sites'] = [s for s in reg['sites'] if s['id'] != site_id]
    reg['sites'].append({'id': site_id, 'fingerprint': fp, 'meta': meta})
    json.dump(reg, open(registry_path, 'w'), indent=1)


if __name__ == '__main__':
    # usage: fingerprint.py <registry.json> <build-meta.json or site id> [--matrix]
    reg = load_registry(sys.argv[1])
    if '--matrix' in sys.argv:
        ids = [s['id'] for s in reg['sites']]
        print('%-26s' % '' + ''.join('%-14s' % i[:13] for i in ids))
        for s in reg['sites']:
            print('%-26s' % s['id'][:25] + ''.join('%-14.3f' % distance(s['fingerprint'], t['fingerprint']) for t in reg['sites']))
        sys.exit(0)
    arg = sys.argv[2]
    if os.path.exists(arg):
        meta = json.load(open(arg)); fp = meta['fingerprint']; sid = meta.get('id')
    else:
        sid = arg; fp = next(s['fingerprint'] for s in reg['sites'] if s['id'] == sid)
    status, nid, nd, rows = check(fp, reg, exclude_id=sid)
    for r in rows:
        print('%-26s %.3f  shared=%s  drivers=%s' % (r['id'], r['distance'], ','.join(r['shared']) or '-', r['drivers']))
    print('\nnearest: %s at %.3f -> %s' % (nid, nd, status.upper()))
    sys.exit({'ok': 0, 'warn': 0, 'refuse': 2}[status])
