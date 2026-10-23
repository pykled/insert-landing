"""Photo review helpers for an intake (factory/content/photos/<slug>/).

  python3 factory/intake/curate.py <slug> --sheet [--only p01,p02]   contact sheet(s) <slug>/_sheet-N.jpg (24 per sheet, labelled)
  python3 factory/intake/curate.py <slug> lawn=p07 barn=p12 ...      name the chosen photos: copies pNN.jpg -> <name>.jpg and adds
                                                                       manifest entries for build.py (photos.items keys = names)
  python3 factory/intake/curate.py <slug> --refetch                   re-download every manifest entry from its source_url (1 req/s),
                                                                       e.g. on a machine without the gitignored photos
"""
import argparse, io, json, os, shutil, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
FACTORY = os.path.dirname(HERE)
if sys.path[0] != FACTORY:
    sys.path.insert(0, FACTORY)


def photo_dir(slug):
    return os.path.join(FACTORY, 'content', 'photos', slug)


def sheet(slug, only=None, per=24, cols=6, cell=300):
    from PIL import Image, ImageDraw
    d = photo_dir(slug)
    man = json.load(open(os.path.join(d, 'manifest.json')))
    names = [m['name'] for m in man if not only or m['name'] in only]
    out = []
    for s in range(0, len(names), per):
        chunk = names[s:s + per]
        rows = (len(chunk) + cols - 1) // cols
        canvas = Image.new('RGB', (cols * cell, rows * (cell + 22)), 'white')
        dr = ImageDraw.Draw(canvas)
        for i, n in enumerate(chunk):
            im = Image.open(os.path.join(d, n + '.jpg')).convert('RGB')
            w, h = im.size
            im.thumbnail((cell - 6, cell - 6))
            x, y = (i % cols) * cell, (i // cols) * (cell + 22)
            canvas.paste(im, (x + 3, y + 3))
            dr.text((x + 4, y + cell + 4), '%s %dx%d' % (n, w, h), fill='black')
        p = os.path.join(d, '_sheet-%d.jpg' % (s // per + 1))
        canvas.save(p, quality=80)
        out.append(p)
    return out


def name_photos(slug, pairs):
    d = photo_dir(slug)
    mp = os.path.join(d, 'manifest.json')
    man = json.load(open(mp))
    by = {m['name']: m for m in man}
    for pair in pairs:
        new, old = pair.split('=', 1)
        if old not in by:
            sys.exit('curate: %s not in manifest' % old)
        shutil.copyfile(os.path.join(d, old + '.jpg'), os.path.join(d, new + '.jpg'))
        e = dict(by[old], name=new, kept_copy=new + '.jpg', named_from=old)
        man = [m for m in man if m['name'] != new] + [e]
        by[new] = e
        print('%s <- %s (%dx%d)' % (new, old, e['native'][0], e['native'][1]))
    json.dump(man, open(mp, 'w'), indent=1)


def refetch(slug):
    from PIL import Image
    from intake import crawl as CR
    d = photo_dir(slug)
    os.makedirs(d, exist_ok=True)
    man = json.load(open(os.path.join(d, 'manifest.json')))
    f = CR.Fetcher()
    for m in man:
        st, ct, body, _ = f.get(m['source_url'], check_robots=False)
        if st != 200:
            print('refetch failed %s: %s' % (m['name'], st))
            continue
        im = Image.open(io.BytesIO(body)).convert('RGB')
        if im.size[0] > m['kept_copy_size'][0]:
            im = im.resize(tuple(m['kept_copy_size']), Image.LANCZOS)
        im.save(os.path.join(d, m['name'] + '.jpg'), quality=92)
    print('refetched %d photos' % len(man))


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('slug')
    ap.add_argument('pairs', nargs='*')
    ap.add_argument('--sheet', action='store_true')
    ap.add_argument('--only')
    ap.add_argument('--refetch', action='store_true')
    a = ap.parse_args()
    if a.refetch:
        refetch(a.slug)
    if a.sheet:
        for p in sheet(a.slug, set(a.only.split(',')) if a.only else None):
            print(p)
    if a.pairs:
        name_photos(a.slug, a.pairs)
