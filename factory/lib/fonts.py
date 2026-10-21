"""Google Fonts checks for data/pairings.json.

validate_pairings(pairings)  static rules (no network):
  - display weight pinned and inside 400-600; never 100/200/300 (spec section 1 + exclusion 2); same for any secondary face
  - has_opsz => `vars` pins "opsz" (the page also sets font-optical-sizing: none)
  - class didone => `risk` names the hairline caution (Bodoni-style faces thin out at display sizes)
  - no banned family as display or body (exclusions 3 and 4)
  - import string uses the css2 `family=` syntax and names the display and body families

verify_import(import_str)  network check at build time: GET https://fonts.googleapis.com/css2?<import>&display=swap must
return 200 with an @font-face. Results are cached in data/fonts-verified.json (committed). Offline (DNS/timeout), a
cached pass is accepted and reported as such; an import never verified is a warning, unless strict=True. An HTTP 4xx
from Google (bad family / axis range) is always a hard failure.

  python3 lib/fonts.py --verify-all     check every pairing online and refresh the cache
"""
import datetime, json, os, re, socket, sys, urllib.error, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(HERE, 'data', 'fonts-verified.json')
BANNED_SCRIPT = ('Beloved', 'Great Vibes', 'Allura', 'Special Elite', 'Pacifico', 'Dancing Script', 'Parisienne', 'Sacramento',
                 'Alex Brush', 'Pinyon Script', 'Tangerine', 'Satisfy', 'Kaushan Script', 'Courier Prime', 'Cutive Mono', 'Homemade Apple')
BANNED_GENERIC = ('Playfair Display', 'Montserrat', 'Raleway', 'Poppins', 'Arial', 'Open Sans')
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36'


def import_families(import_str):
    return [urllib.parse.unquote_plus(m) for m in re.findall(r'family=([^:&]+)', import_str)]


def _faces(p):
    out = [('display', p['display'])]
    if p.get('secondary'):
        out.append(('secondary', p['secondary']))
    return out


def validate_pairings(pairings):
    errors = []
    for p in pairings:
        pid = p['id']
        for role, d in _faces(p):
            w = d.get('weight')
            if not isinstance(w, int) or not (400 <= w <= 600):
                errors.append('%s: %s weight %s outside the pinned 400-600 range' % (pid, role, w))
            if d.get('has_opsz') and 'opsz' not in (d.get('vars') or ''):
                errors.append('%s: %s %s has an opsz axis but vars does not pin it' % (pid, role, d['family']))
            if d.get('class') == 'didone' and 'hairline' not in (p.get('risk') or '').lower():
                errors.append('%s: didone display face without the hairline caution in risk' % pid)
        fams = [p['display']['family'], p['body']['family']] + ([p['secondary']['family']] if p.get('secondary') else [])
        for f in fams:
            if f in BANNED_SCRIPT or f in BANNED_GENERIC:
                errors.append('%s: banned family %s (exclusions 3/4)' % (pid, f))
        imp = p.get('import', '')
        if not imp.startswith('family='):
            errors.append('%s: import must use the css2 family= syntax' % pid)
        got = import_families(imp)
        for f in fams:
            if f not in got:
                errors.append('%s: import string does not load %s' % (pid, f))
        if p['body'].get('size_px', 17) < 16.5:
            errors.append('%s: body size %s < 16.5px' % (pid, p['body'].get('size_px')))
    return errors


def load_cache():
    if os.path.exists(CACHE):
        return json.load(open(CACHE))
    return {'_notes': 'import string -> last successful fetch from fonts.googleapis.com/css2 (lib/fonts.py)', 'verified': {}}


def save_cache(c):
    json.dump(c, open(CACHE, 'w'), indent=1, sort_keys=True)
    open(CACHE, 'a').write('\n')


def verify_import(import_str, strict=False, timeout=8, use_cache=True):
    """Return (ok, message). ok False means the build must stop."""
    url = 'https://fonts.googleapis.com/css2?%s&display=swap' % import_str
    cache = load_cache()
    try:
        req = urllib.request.Request(url, headers={'User-Agent': UA})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read().decode('utf-8', 'replace')
        if '@font-face' not in body:
            return False, 'fonts.googleapis.com returned 200 but no @font-face for %s' % import_str
        cache['verified'][import_str] = datetime.date.today().isoformat()
        if use_cache:
            save_cache(cache)
        return True, 'verified online (%d families)' % len(import_families(import_str))
    except urllib.error.HTTPError as e:
        return False, 'fonts.googleapis.com rejected the import (HTTP %d): %s' % (e.code, import_str)
    except (urllib.error.URLError, socket.timeout, OSError) as e:
        when = cache['verified'].get(import_str)
        if when:
            return True, 'offline (%s); using the cached verification from %s' % (getattr(e, 'reason', e), when)
        msg = 'offline (%s) and this import was never verified: %s' % (getattr(e, 'reason', e), import_str)
        return (not strict), msg


if __name__ == '__main__':
    pairings = json.load(open(os.path.join(HERE, 'data', 'pairings.json')))['pairings']
    errs = validate_pairings(pairings)
    for e in errs:
        print('RULE:', e)
    bad = 0
    if '--verify-all' in sys.argv:
        for p in pairings:
            ok, msg = verify_import(p['import'], strict=True)
            bad += 0 if ok else 1
            print('%-26s %s %s' % (p['id'], 'ok ' if ok else 'BAD', msg))
    print('%d pairings, %d rule errors, %d import failures' % (len(pairings), len(errs), bad))
    sys.exit(1 if (errs or bad) else 0)
