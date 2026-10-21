"""Template availability + nearest-existing fallback for dialect builds.

Dialects (data/dialects.json) name template ids from docs/research/05-luxury-dialects-spec.md. Some of them do not
exist yet (stage 2B builds them). This module answers two questions, from the filesystem, never from labels:

  exists(kind, id)                       is there a template (or data record) for this id right now?
  resolve(kind, wanted, allowed, ...)    which id do we actually render, and was it a fallback?

Path convention per kind (relative to factory/templates):
  hero      heroes/<id>.j2 + heroes/<id>.css.j2      (base.html.j2 includes the css without `ignore missing`)
  spaces    sections/spaces-<id>.j2
  story     sections/story-<id>.j2
  faq       sections/faq-<id>.j2
  tour      sections/tour-<id>.j2
  gallery   sections/gallery-<id>.j2                 ('none' always exists: no gallery)
  moment    moments/<id>.j2
  ornament  ornaments/<id>.j2 + ornaments/<id>.css.j2 ('none' always exists: no ornament)
  section   sections/<id>.j2                         (rhythm blocks: statement, facts-strip, daylight-band, ...)
  pairing   an id in data/pairings.json
  voice     a key in data/voices.json

CLI:
  python3 lib/templates.py --refresh   rewrite every "status" in data/dialects.json from the filesystem
  python3 lib/templates.py --missing   list the ids still owed (planned-2B / deferred)
"""
import json, os, sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES = os.path.join(HERE, 'templates')
DATA = os.path.join(HERE, 'data')

KIND_PATHS = {
    'hero': ['heroes/{id}.j2', 'heroes/{id}.css.j2'],
    'spaces': ['sections/spaces-{id}.j2'],
    'story': ['sections/story-{id}.j2'],
    'faq': ['sections/faq-{id}.j2'],
    'tour': ['sections/tour-{id}.j2'],
    'gallery': ['sections/gallery-{id}.j2'],
    'moment': ['moments/{id}.j2'],
    'ornament': ['ornaments/{id}.j2', 'ornaments/{id}.css.j2'],
    'section': ['sections/{id}.j2'],
}
ALWAYS = {('gallery', 'none'), ('ornament', 'none'), ('moment', 'none')}
# dialects.json list key -> resolver kind
LIST_KINDS = {'pairings': 'pairing', 'heroes': 'hero', 'spaces': 'spaces', 'story': 'story', 'faq': 'faq', 'tour': 'tour',
              'gallery': 'gallery', 'moments': 'moment', 'ornaments': 'ornament', 'voices': 'voice'}


def _data_ids(kind, data_dir=DATA):
    if kind == 'pairing':
        return {p['id'] for p in json.load(open(os.path.join(data_dir, 'pairings.json')))['pairings']}
    if kind == 'voice':
        return {k for k in json.load(open(os.path.join(data_dir, 'voices.json'))) if not k.startswith('_')}
    raise KeyError(kind)


def template_paths(kind, id_):
    return [p.format(id=id_) for p in KIND_PATHS[kind]]


def exists(kind, id_, templates_dir=TEMPLATES, data_dir=DATA):
    if (kind, id_) in ALWAYS:
        return True
    if kind in ('pairing', 'voice'):
        return id_ in _data_ids(kind, data_dir)
    return all(os.path.exists(os.path.join(templates_dir, p)) for p in template_paths(kind, id_))


def status(kind, id_, deferred=(), templates_dir=TEMPLATES, data_dir=DATA):
    if exists(kind, id_, templates_dir, data_dir):
        return 'exists'
    return 'deferred' if id_ in deferred else 'planned-2B'


def resolve(kind, wanted, allowed=(), fallbacks=None, exists_fn=None):
    """Return (used_id, fallback_record). used_id is None when nothing in the chain exists (the caller omits the block).
    Order tried: wanted, then fallbacks[kind][wanted] in order, preferring ids the dialect allows, then any existing id
    in that chain. fallback_record is None when wanted itself exists."""
    exists_fn = exists_fn or (lambda k, i: exists(k, i))
    if exists_fn(kind, wanted):
        return wanted, None
    chain = list((fallbacks or {}).get(kind, {}).get(wanted, []))
    ordered = [c for c in chain if c in allowed] + [c for c in chain if c not in allowed]
    used = next((c for c in ordered if exists_fn(kind, c)), None)
    rec = {'kind': kind, 'wanted': wanted, 'used': used, 'chain': chain,
           'reason': 'template for %s "%s" does not exist yet (owed by stage 2B)' % (kind, wanted)}
    if used is None:
        rec['reason'] += '; no existing template in the fallback chain, block omitted'
    return used, rec


def refresh(path=os.path.join(DATA, 'dialects.json')):
    d = json.load(open(path))
    deferred = set(d.get('deferred', []))
    changed = 0
    for dia in d['dialects']:
        for key, kind in LIST_KINDS.items():
            for item in dia.get(key, []):
                s = status(kind, item['id'], deferred)
                if item.get('status') != s:
                    item['status'] = s; changed += 1
        for rv in dia.get('rhythm_variants', []):
            for blk in rv['blocks']:
                if blk['kind'] == 'section':
                    s = status('section', blk['id'], deferred)
                    if blk.get('status') != s:
                        blk['status'] = s; changed += 1
    json.dump(d, open(path, 'w'), indent=1, ensure_ascii=False)
    open(path, 'a').write('\n')
    return changed


def missing(path=os.path.join(DATA, 'dialects.json')):
    d = json.load(open(path))
    deferred = set(d.get('deferred', []))
    out = {}
    for dia in d['dialects']:
        for key, kind in LIST_KINDS.items():
            for item in dia.get(key, []):
                s = status(kind, item['id'], deferred)
                if s != 'exists':
                    out.setdefault((kind, item['id'], s), []).append(dia['id'])
        for rv in dia.get('rhythm_variants', []):
            for blk in rv['blocks']:
                if blk['kind'] == 'section':
                    s = status('section', blk['id'], deferred)
                    if s != 'exists':
                        out.setdefault(('section', blk['id'], s), []).append(dia['id'])
    return out


if __name__ == '__main__':
    if '--refresh' in sys.argv:
        print('statuses changed:', refresh())
    elif '--missing' in sys.argv:
        rows = missing()
        for (kind, id_, s), ds in sorted(rows.items()):
            print('%-9s %-24s %-11s %s' % (kind, id_, s, ','.join(sorted(set(ds)))))
        print('%d ids not yet available' % len(rows))
    else:
        print(__doc__)
