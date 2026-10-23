"""3A item 1: focus probe across every dialect x two venues, desktop 1440 + mobile 390 (2x). One line per build."""
import os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
R = os.path.expanduser('~/projects/insert'); sys.path.insert(0, R + '/factory')
from playwright.sync_api import sync_playwright
from lib import focus as FO
DIAL = ['estate', 'editorial', 'candlelit', 'modern-luxe', 'coastal', 'botanical', 'ranch', 'deco']
CON = {'hs': 'homestead', 'lsh': 'lindley-scott', 'sh': 'stonehurst'}
jobs = [(c, d) for c in CON for d in DIAL if not sys.argv[1:] or '%s-%s' % (c, d) in sys.argv[1:]]
def build(j):
    c, d = j; out = '%s/.factory-check/3b/fs/%s-%s' % (R, c, d)
    p = subprocess.run(['python3', 'factory/build.py', 'factory/content/%s.json' % CON[c], '--variant', 'fs', '--dialect', d, '--out', out, '--offline-fonts', '--registry', '/tmp/empty-reg.json'], cwd=R, capture_output=True, text=True)
    return j, out, p.returncode
with ThreadPoolExecutor(6) as ex: built = list(ex.map(build, jobs))
with sync_playwright() as pw:
    br = pw.chromium.launch()
    for (c, d), out, rc in built:
        if rc: print(c, d, 'BUILD FAIL'); continue
        res = []
        for w, h, mob in ((1440, 900, False), (390, 844, True)):
            ctx = br.new_context(viewport={'width': w, 'height': h}, device_scale_factor=2, is_mobile=mob, has_touch=mob)
            pg = ctx.new_page(); pg.goto('http://127.0.0.1:8931/' + os.path.relpath(out, R) + '/index.html'); pg.wait_for_timeout(400)
            pg.evaluate("document.querySelectorAll('.reveal').forEach(e=>e.classList.add('visible')); document.querySelector('header').style.position='relative'")
            pg.add_style_tag(content="*,*::before,*::after{transition:none!important;animation:none!important}")
            probs, rows = FO.check(pg, str(w), 2)
            res.append('%d:%d ctl %d bad min %.2f' % (w, len(rows), len(probs), min((r['changed'] / max(1, r['need']) for r in rows), default=0)))
            for p in probs[:3]: print('   ', c, d, p[:170])
            ctx.close()
        print(c, d, ' | '.join(res))
