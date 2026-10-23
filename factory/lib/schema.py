"""Content-file, voice and pairing validation (see lib/schema.md). Pure functions; build.py calls them before anything
else and stops on errors. Warnings are printed and recorded in build-meta.json.

  python3 lib/schema.py content/<slug>.json      validate one content file (exit 1 on errors)
"""
import json, os, re, sys

REQUIRED = ('slug', 'name', 'short_name', 'legal_name', 'tagline_facts', 'website', 'contact', 'story', 'spaces', 'day', 'faqs', 'photos', 'preview')
TAGLINE_REQUIRED = ('locality', 'region', 'state', 'space_count', 'max_guests', 'uses')
SUBJECTS = ('place', 'building', 'grounds', 'interior', 'detail', 'people')
LEAD_SUBJECTS = ('place', 'building', 'grounds', 'interior', 'detail')
FLORA = ('olive', 'fig', 'fern', 'lavender', 'oak', 'eucalyptus')
VENUE_TYPES = ('estate', 'mansion', 'castle', 'villa', 'hacienda', 'barn', 'ranch', 'vineyard', 'garden', 'glasshouse', 'coastal',
               'lake', 'desert', 'resort', 'hotel', 'loft', 'clubhouse', 'theatre')
LIGHTS = ('day', 'golden', 'night', 'overcast', 'dusk')
NUMBER_WORDS = r'\b(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|twenty|thirty|forty|fifty|hundred|thousand|dozen)\b'


def validate_content(v, vibe_words=None):
    """Return (errors, warnings). vibe_words: the controlled list (data/dialects.json vibe_words keys)."""
    errors, warnings = [], []
    for k in REQUIRED:
        if k not in v:
            errors.append('missing top-level key "%s"' % k)
    tf = v.get('tagline_facts') or {}
    for k in TAGLINE_REQUIRED:
        if k not in tf:
            errors.append('tagline_facts.%s missing (use null when unknown)' % k)
    if not isinstance(tf.get('uses', []), list) or not tf.get('uses'):
        errors.append('tagline_facts.uses must be a non-empty list')
    for i, s in enumerate(v.get('spaces') or []):
        for k in ('id', 'name', 'photo', 'use'):
            if k not in s:
                errors.append('spaces[%d].%s missing' % (i, k))
        if 'capacity' in s and s['capacity'] is not None and not isinstance(s['capacity'], int):
            errors.append('spaces[%d].capacity must be an integer or null' % i)
        if not s.get('source'):
            warnings.append('spaces[%d] (%s) has no source URL' % (i, s.get('id')))
    for i, f in enumerate(v.get('faqs') or []):
        if not f.get('q') or not f.get('a'):
            errors.append('faqs[%d] needs q and a' % i)
    photos = v.get('photos') or {}
    items = photos.get('items')
    if not isinstance(items, dict) or not items:
        errors.append('photos.items must be a non-empty object')
        items = {}
    for k in ('source_dir', 'manifest'):
        if k not in photos:
            errors.append('photos.%s missing' % k)
    for name, m in items.items():
        if not m.get('alt'):
            errors.append('photos.items.%s.alt missing' % name)
        if 'subject' in m and m['subject'] not in SUBJECTS:
            errors.append('photos.items.%s.subject "%s" not in %s' % (name, m['subject'], '/'.join(SUBJECTS)))
        for b in ('mono', 'archival'):
            if b in m and not isinstance(m[b], bool):
                errors.append('photos.items.%s.%s must be true/false' % (name, b))
        if 'flora' in m and m['flora'] is not None and m['flora'] not in FLORA:
            errors.append('photos.items.%s.flora "%s" not in %s' % (name, m['flora'], '/'.join(FLORA)))
        if m.get('archival') and not m.get('rights'):
            errors.append('photos.items.%s is archival but has no "rights" note (then-now needs rights)' % name)
        if 'light' in m and m['light'] not in LIGHTS:
            warnings.append('photos.items.%s.light "%s" not in %s' % (name, m['light'], '/'.join(LIGHTS)))
    if items and not any('subject' in m for m in items.values()):
        warnings.append('no photo carries a "subject" tag: the lead-photo rule (exclusion 6) cannot be checked')
    vibe = v.get('vibe')
    if vibe is not None:
        if not isinstance(vibe, dict):
            errors.append('vibe must be an object')
        else:
            if vibe.get('type') not in VENUE_TYPES:
                errors.append('vibe.type "%s" not in the controlled list' % vibe.get('type'))
            era = vibe.get('era')
            if era is not None and not (isinstance(era, int) and 1600 <= era <= 2100):
                errors.append('vibe.era must be a build year (integer) or null')
            words = vibe.get('words')
            if not isinstance(words, list) or len(words) != 3 or len(set(words)) != 3:
                errors.append('vibe.words must be exactly three different words')
            elif vibe_words is not None:
                bad = [w for w in words if w not in vibe_words]
                if bad:
                    errors.append('vibe.words not in the controlled list: %s' % ', '.join(bad))
            if era is not None and not vibe.get('era_source'):
                warnings.append('vibe.era has no era_source URL (it renders as a fact in some voices)')
    return errors, warnings


def check_lead(v, lead):
    """Exclusion 6: the lead photo is the place, never a couple close-up. Returns (errors, warnings)."""
    m = ((v.get('photos') or {}).get('items') or {}).get(lead)
    if m is None:
        return ['lead photo "%s" is not in photos.items' % lead], []
    subj = m.get('subject')
    if subj is None:
        return [], ['lead photo "%s" has no subject tag (exclusion 6 unchecked)' % lead]
    if subj not in LEAD_SUBJECTS:
        return ['lead photo "%s" has subject "%s"; the lead must be one of %s (exclusion 6)' % (lead, subj, '/'.join(LEAD_SUBJECTS))], []
    return [], []


def _strip_slots(s):
    return re.sub(r'\{[a-z_]+\}', '', s)


def validate_voices(voices):
    """Strict voices (_meta.strict_facts) may not state a number outside a {slot}: facts only come from content.
    Returns (errors, warnings); non-strict (legacy) voices only produce warnings."""
    errors, warnings = [], []
    for vid, voice in voices.items():
        if vid.startswith('_'):
            continue
        strict = (voice.get('_meta') or {}).get('strict_facts', False)
        entries = [(key, val, strict) for key, val in voice.items()] + [('_dialect.' + key, val, True) for key, val in (voice.get('_dialect') or {}).items()]
        for key, val, strict_k in entries:
            if key.startswith('_') and not key.startswith('_dialect.') or key == 'cta_sets' or key.startswith('_dialect._'):
                continue
            for s in (val if isinstance(val, list) else [val]):
                bare = _strip_slots(re.sub(r'<[^>]+>', '', s))
                hit = re.search(r'\d', bare) or re.search(NUMBER_WORDS, bare, re.I)
                if hit:
                    msg = 'voice %s.%s states "%s" outside a {slot}: "%s"' % (vid, key, hit.group(0), s)
                    (errors if strict_k else warnings).append(msg)
        sets = voice.get('cta_sets')
        if strict and (not isinstance(sets, list) or len(sets) != 3):
            errors.append('voice %s needs exactly three cta_sets' % vid)
    return errors, warnings


if __name__ == '__main__':
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    words = json.load(open(os.path.join(here, 'data', 'dialects.json')))['vibe_words']
    e, w = validate_content(json.load(open(sys.argv[1])), words)
    for x in w:
        print('warning:', x)
    for x in e:
        print('ERROR:', x)
    print('%d errors, %d warnings' % (len(e), len(w)))
    sys.exit(1 if e else 0)
