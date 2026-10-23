"""Stage a built, QA-passed venue site as an unlisted private preview (local files only; deploying is a separate step).

  python3 factory/preview.py <build-dir> --name <slug> [--group demos]    stage index.html + the images it references into
                                                                           private-previews/<token>/<group>/<slug>/
  python3 factory/preview.py <build-dir> --mark-qa-strict                 record qa-status.json after `qa.py --strict` exited 0
  python3 factory/preview.py --remove <slug> [--group demos]              delete a staged preview (the venue declined)

Refuses when: the build has no passing QA record (qa-status.json, or qa/qa-report.json with zero problems) newer than its
index.html; an image is over 400 KB; a referenced file is missing or outside the build. Guarantees the noindex meta and the
'Concept preview by Insert' chip in the staged copy (adds them only there when the build lacks them). The token comes from
factory/data/preview.json {"token": ...} or the single 24-hex directory under private-previews/.
"""
import argparse, datetime, hashlib, json, os, re, shutil, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
PREVIEWS = os.path.join(REPO, 'private-previews')
BASE_URL = 'https://insert-landing-production.up.railway.app/private-previews'
MAX_IMG = 400 * 1024
SLUG = re.compile(r'^[a-z0-9][a-z0-9-]{0,60}$')
ROBOTS = '<meta name="robots" content="noindex, nofollow">'
CHIP_TEXT = 'Concept preview by Insert'
CHIP = ('<div data-insert-chip style="position:fixed;left:12px;bottom:12px;z-index:9999;font:12px/1.3 system-ui,sans-serif;'
        'letter-spacing:.02em;color:#2b2b2b;background:rgba(255,255,255,.88);border:1px solid rgba(0,0,0,.12);border-radius:999px;'
        'padding:5px 11px;pointer-events:none">' + CHIP_TEXT + ' · not affiliated with the venue</div>')
REF_PATTERNS = [r'\bsrc="([^"]+)"', r'\bsrcset="([^"]+)"', r'\bdata-src="([^"]+)"', r'\bposter="([^"]+)"',
                r'url\(\s*[\'"]?([^\'")]+)[\'"]?\s*\)', r'<link[^>]+href="([^"]+\.(?:webp|jpe?g|png|avif|svg|ico))"',
                r'<meta[^>]+content="([^"]+\.(?:webp|jpe?g|png|avif))"']
IMG_EXT = re.compile(r'\.(webp|jpe?g|png|avif|gif|svg|ico)$', re.I)


def die(msg, code=2):
    print('preview: REFUSED: ' + msg)
    sys.exit(code)


def token():
    cfg = os.path.join(HERE, 'data', 'preview.json')
    if os.path.exists(cfg):
        t = json.load(open(cfg)).get('token')
        if t and re.fullmatch(r'[a-f0-9]{24}', t):
            return t
        die('factory/data/preview.json has no valid 24-hex "token"')
    found = [d for d in os.listdir(PREVIEWS) if re.fullmatch(r'[a-f0-9]{24}', d)] if os.path.isdir(PREVIEWS) else []
    if len(found) != 1:
        die('expected exactly one 24-hex token directory under private-previews/ (found %d); set factory/data/preview.json' % len(found))
    return found[0]


def sha(path):
    return hashlib.sha256(open(path, 'rb').read()).hexdigest()


def refs(html):
    out = set()
    for rx in REF_PATTERNS:
        for m in re.findall(rx, html, re.I):
            for part in m.split(','):
                u = part.strip().split(' ')[0].strip()
                if u and not re.match(r'^(https?:|//|data:|#|mailto:|tel:)', u) and IMG_EXT.search(u.split('?')[0]):
                    out.add(u.split('?')[0].split('#')[0])
    return sorted(out)


def qa_ok(build):
    idx = os.path.join(build, 'index.html')
    st = os.path.join(build, 'qa-status.json')
    if os.path.exists(st):
        s = json.load(open(st))
        if not s.get('passed'):
            die('qa-status.json says QA did not pass')
        if s.get('index_sha256') != sha(idx):
            die('index.html changed after QA (qa-status.json hash mismatch): re-run qa.py --strict')
        return 'qa-status.json (strict=%s, %s)' % (s.get('strict'), s.get('at'))
    rp = os.path.join(build, 'qa', 'qa-report.json')
    if not os.path.exists(rp):
        die('no QA record: run `python3 factory/qa.py %s --strict` (and --mark-qa-strict) first' % build)
    r = json.load(open(rp))
    if r.get('problems'):
        die('qa-report.json lists %d problem(s), e.g. %s' % (len(r['problems']), str(r['problems'][0])[:160]))
    if os.path.getmtime(rp) < os.path.getmtime(idx):
        die('qa-report.json is older than index.html: re-run qa.py')
    print('preview: warning: qa-report.json passes but strictness is unrecorded (use new-demo.sh or --mark-qa-strict)')
    return 'qa/qa-report.json (0 problems; strictness unrecorded)'


def mark_qa(build):
    rp = os.path.join(build, 'qa', 'qa-report.json')
    if not os.path.exists(rp):
        die('no qa/qa-report.json in %s' % build)
    r = json.load(open(rp))
    if r.get('problems'):
        die('qa-report.json lists problems; not recording a pass')
    s = {'passed': True, 'strict': True, 'at': datetime.datetime.now().isoformat(timespec='seconds'),
         'index_sha256': sha(os.path.join(build, 'index.html')), 'warnings': len(r.get('warnings') or [])}
    json.dump(s, open(os.path.join(build, 'qa-status.json'), 'w'), indent=1)
    print('preview: recorded strict QA pass in %s' % os.path.join(build, 'qa-status.json'))


def guarantee(html):
    added = []
    if not re.search(r'<meta\s+name="robots"\s+content="[^"]*noindex[^"]*nofollow', html, re.I):
        html = re.sub(r'(<head[^>]*>)', r'\1' + ROBOTS, html, count=1, flags=re.I)
        added.append('noindex meta')
    if CHIP_TEXT not in re.sub(r'<[^>]+>', '', html):
        html = re.sub(r'(</body>)', CHIP + r'\1', html, count=1, flags=re.I)
        added.append('preview chip')
    return html, added


def stage(build, slug, group):
    build = os.path.realpath(build)
    idx = os.path.join(build, 'index.html')
    if not os.path.exists(idx):
        die('%s has no index.html' % build)
    how = qa_ok(build)
    html = open(idx, encoding='utf-8').read()
    files, problems = [], []
    for r in refs(html):
        p = os.path.realpath(os.path.join(build, r))
        if not p.startswith(build + os.sep):
            problems.append('%s points outside the build' % r)
        elif not os.path.exists(p):
            problems.append('%s is referenced but missing' % r)
        elif os.path.getsize(p) > MAX_IMG:
            problems.append('%s is %d KB (> 400 KB)' % (r, os.path.getsize(p) // 1024))
        else:
            files.append((r, p))
    if problems:
        die('; '.join(problems[:6]) + (' (+%d more)' % (len(problems) - 6) if len(problems) > 6 else ''))
    html, added = guarantee(html)
    tok = token()
    dest = os.path.join(PREVIEWS, tok, group, slug)
    tmp = tempfile.mkdtemp(prefix='.stage-', dir=os.path.join(PREVIEWS, tok))
    try:
        open(os.path.join(tmp, 'index.html'), 'w', encoding='utf-8').write(html)
        for r, p in files:
            q = os.path.join(tmp, os.path.normpath(r))
            os.makedirs(os.path.dirname(q), exist_ok=True)
            shutil.copyfile(p, q)
        if os.path.exists(dest):
            shutil.rmtree(dest)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        os.rename(tmp, dest)
    finally:
        if os.path.exists(tmp):
            shutil.rmtree(tmp)
    total = sum(os.path.getsize(p) for _, p in files) + len(html.encode())
    print('preview: QA ok via %s' % how)
    print('preview: staged index.html + %d images (%d KB) -> %s%s' % (len(files), total // 1024, os.path.relpath(dest, REPO),
                                                                       ('; added in staged copy: ' + ', '.join(added)) if added else ''))
    print('URL (after deploy): %s/%s/%s/%s/' % (BASE_URL, tok, group, slug))
    print('Reminder: nothing is live yet. Deploying is a separate, approved step (Insert deploy skill); share the link privately only.')


def remove(slug, group):
    tok = token()
    dest = os.path.join(PREVIEWS, tok, group, slug)
    if not os.path.isdir(dest):
        die('no staged preview at %s' % os.path.relpath(dest, REPO), 1)
    shutil.rmtree(dest)
    print('preview: removed %s (redeploy to take it offline)' % os.path.relpath(dest, REPO))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('build', nargs='?')
    ap.add_argument('--name')
    ap.add_argument('--group', default='demos')
    ap.add_argument('--remove', metavar='SLUG')
    ap.add_argument('--mark-qa-strict', action='store_true')
    a = ap.parse_args()
    if not SLUG.match(a.group):
        die('bad --group')
    if a.remove:
        if not SLUG.match(a.remove):
            die('bad slug')
        return remove(a.remove, a.group)
    if not a.build:
        ap.error('build dir required')
    if a.mark_qa_strict:
        return mark_qa(a.build)
    if not a.name or not SLUG.match(a.name):
        die('--name <slug> required (lowercase letters, digits, hyphens)')
    stage(a.build, a.name, a.group)


if __name__ == '__main__':
    main()
