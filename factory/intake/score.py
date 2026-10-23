"""Dialect score table for a (reviewed) content file, computed exactly as build.py does it: lead + the next three photo
items -> lib.palette signals, derive() meta, lib.personality.score_dialects (with the content's vibe block and the
registry's per-dialect counts). Also the photos-only table, so the vibe block's pull is visible. No build, no writes.

  python3 factory/intake/score.py factory/content/<slug>.json [--lead <photo>] [--palette-photos a,b,c] [--md]
"""
import argparse, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
FACTORY = os.path.dirname(HERE)
if sys.path[0] != FACTORY:
    sys.path.insert(0, FACTORY)
from lib import palette as P, personality as PERS  # noqa: E402


def score_content(path, lead=None, palette_photos=None):
    v = json.load(open(path))
    cdir = os.path.dirname(os.path.abspath(path))
    items = v['photos']['items']
    src = os.path.normpath(os.path.join(cdir, v['photos']['source_dir']))
    lead = lead or ('hero' if 'hero' in items else next(iter(items)))
    names = palette_photos.split(',') if palette_photos else [lead] + [n for n in items if n != lead][:3]
    paths = {n: os.path.join(src, n + '.jpg') for n in names}
    doc = json.load(open(os.path.join(FACTORY, 'data', 'dialects.json')))
    reg = json.load(open(os.path.join(FACTORY, 'data', 'registry.json')))
    sig = P.photo_signals(paths, lead)
    _, _, meta = P.derive(paths, {a: 50.0 for a in PERS.AXES}, lead=lead)
    win, rows = PERS.score_dialects(doc, sig, v, meta, reg)
    _, rows_photos = PERS.score_dialects(doc, sig, {}, meta, reg)
    return {'lead': lead, 'palette_photos': names, 'signals': {k: x for k, x in sig.items() if k != 'per_photo'},
            'winner': win, 'rows': rows, 'rows_photos_only': rows_photos, 'temperature': meta.get('temperature')}


def md(r):
    def table(rows):
        out = ['| dialect | score | registered | reasons |', '|---|---|---|---|']
        for x in rows:
            out.append('| %s | %d | %d | %s |' % (x['id'], x['score'], x['registered'], '; '.join('%s (+%d)' % (w, p) for w, p in x['reasons']) or '-'))
        return out
    s = r['signals']
    L = ['Palette photos (build.py default order): lead `%s` + %s; paper temperature %s.' % (r['lead'], ', '.join('`%s`' % n for n in r['palette_photos'][1:]), r['temperature']),
         'Signals: mean L %.2f, foliage %.2f, earth %.2f, dark %.2f, water %.2f, mono %.2f, warm shadows %s.' % (
             s['mean_L'], s['foliage_share'], s['earth_share'], s['dark_share'], s['water_share'], s['mono_share'], s['warm_shadows']),
         '', '**With the vibe block (what `build.py --dialect auto` picks: `%s`):**' % r['winner'], ''] + table(r['rows']) + \
        ['', '**Photos only (no vibe, no type prior):**', ''] + table(r['rows_photos_only'][:4])
    return '\n'.join(L)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('content')
    ap.add_argument('--lead')
    ap.add_argument('--palette-photos')
    ap.add_argument('--md', action='store_true')
    a = ap.parse_args()
    r = score_content(a.content, a.lead, a.palette_photos)
    if a.md:
        print(md(r))
    else:
        print('winner: %s (lead %s)' % (r['winner'], r['lead']))
        for x in r['rows']:
            print('  %-12s %3d' % (x['id'], x['score']))
