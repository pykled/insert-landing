"""Hostile content variants of a real content file (stage 3A): every optional field null/empty, a long unbroken word,
a single photo. Written next to nothing in content/: photo paths are made absolute so the copy builds from anywhere."""
import copy, json, os

FACTORY = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _abs_photos(v, src):
    cdir = os.path.dirname(os.path.abspath(src))
    for k in ('source_dir', 'manifest'):
        v['photos'][k] = os.path.normpath(os.path.join(cdir, v['photos'][k]))
    return v


def nulls(src):
    v = _abs_photos(json.load(open(src)), src)
    tf = v['tagline_facts']
    for k in ('acres', 'space_count', 'max_guests', 'events_per_day', 'region', 'founded'):
        if k in tf:
            tf[k] = None
    for k in list(v.get('day') or {}):
        if k not in ('source', '_note'):
            v['day'][k] = None
    v['numbers'] = []
    v['featured_in'] = []
    v['hours'] = None
    v['copy_overrides'] = {}
    for s in v['spaces']:
        for k in ('capacity', 'capacity_label', 'capacity_kind', 'features', 'journey_step'):
            s[k] = None
    st = v.get('story') or {}
    for k in ('credit', 'quote', 'era_label'):
        if k in st:
            st[k] = None
    c = v.get('contact') or {}
    for k in ('phone', 'hours', 'email'):
        if k in c:
            c[k] = None
    if 'vibe' in v:
        v['vibe']['era'] = None
    v['faqs'] = []
    v['journey'] = []
    st['timeline'] = []
    return v


def _unused():
    v = {}
    return v


def longword(src):
    v = _abs_photos(json.load(open(src)), src)
    v['tagline_facts']['uses'] = ['Weddings', 'Quinceañeras', 'Extraordinarycelebrationsandfilmproductions']
    return v


def single_photo(src):
    v = _abs_photos(json.load(open(src)), src)
    items = v['photos']['items']
    keep = next(n for n, m in items.items() if m.get('subject') in ('grounds', 'building'))
    v['photos']['items'] = {keep: items[keep]}
    for s in v['spaces']:
        s['photo'] = keep
    return v


def write(v, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(v, open(path, 'w'), indent=1, ensure_ascii=False)
    return path
