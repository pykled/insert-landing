#!/usr/bin/env python3
"""Full-resolution Playwright verification for previews/stonehurst/index.html.

Expects a static server on http://localhost:4821 serving ~/projects/insert.
Writes screenshots to previews/stonehurst/shots and prints a check report.
"""
import os
import sys
from playwright.sync_api import sync_playwright

BASE = os.environ.get('BASE', 'http://localhost:4821/previews/stonehurst/index.html')
OUT = os.path.join(os.path.dirname(__file__), '..', 'previews', 'stonehurst', 'shots')
os.makedirs(OUT, exist_ok=True)

REVEAL = "document.querySelectorAll('.reveal').forEach(e=>e.classList.add('visible')); document.querySelectorAll('.hero-copy > *, .hero .card, .hero-media img').forEach(e=>{e.style.animation='none'}); document.querySelector('.hero-media img').style.transform='none';"

problems = []

def run(pw, name, width, height, scale, mobile):
    ctx = pw.chromium.launch().new_context(viewport={'width': width, 'height': height}, device_scale_factor=scale, is_mobile=mobile, has_touch=mobile)
    page = ctx.new_page()
    errors = []
    page.on('console', lambda m: errors.append('%s: %s' % (m.type, m.text)) if m.type in ('error', 'warning') else None)
    page.on('pageerror', lambda e: errors.append('pageerror: %s' % e))
    page.on('requestfailed', lambda r: errors.append('requestfailed: %s' % r.url))
    page.goto(BASE, wait_until='load')
    page.wait_for_function('document.fonts.ready.then(()=>true)')
    page.wait_for_timeout(600)
    fonts = page.evaluate("[document.fonts.check('16px \"Bodoni Moda\"'), document.fonts.check('16px Jost')]")
    page.evaluate(REVEAL)
    page.wait_for_timeout(300)
    sw = page.evaluate('document.documentElement.scrollWidth')
    iw = page.evaluate('window.innerWidth')
    if sw > iw:
        problems.append('%s: horizontal overflow scrollWidth=%d innerWidth=%d' % (name, sw, iw))
        wide = page.evaluate("""() => [...document.querySelectorAll('body *')].filter(e => e.getBoundingClientRect().right > window.innerWidth + 1).slice(0, 8).map(e => e.tagName + '.' + e.className + ' right=' + Math.round(e.getBoundingClientRect().right))""")
        problems.append('  offenders: %s' % wide)
    # lazy images: force load for the full-page shot
    page.evaluate("document.querySelectorAll('img[loading=lazy]').forEach(i=>i.loading='eager')")
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    page.wait_for_timeout(800)
    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(400)
    page.wait_for_function("[...document.images].every(i => i.complete)")
    # images: currentSrc vs rendered size
    imgs = page.evaluate("""() => [...document.images].map(i => ({alt: (i.alt||'').slice(0,30), cur: i.currentSrc.split('/').pop(), cw: Math.round(i.getBoundingClientRect().width), nw: i.naturalWidth, complete: i.complete}))""")
    for i in imgs:
        if not i['alt']:
            problems.append('%s: image without alt: %s' % (name, i['cur']))
        if i['nw'] == 0:
            problems.append('%s: image failed to load: %s' % (name, i['cur']))
        else:
            import re
            m = re.search(r'-(\d+)\.webp$', i['cur'])
            src_w = int(m.group(1)) if m else i['nw']
            if src_w < i['cw'] * scale * 0.9:
                problems.append('%s: image soft: %s source=%dpx needed=%dpx' % (name, i['cur'], src_w, i['cw'] * scale))
    shot = os.path.join(OUT, '%s.png' % name)
    page.evaluate("document.querySelector('header').style.position='absolute'")
    page.screenshot(path=shot, full_page=True)
    # crops
    hero_h = page.evaluate("document.querySelector('.hero').getBoundingClientRect().height")
    page.screenshot(path=os.path.join(OUT, '%s-hero.png' % name), full_page=True, clip={'x': 0, 'y': 0, 'width': width, 'height': max(200, hero_h)})
    for sel, label in (('#spaces', 'spaces'), ('#tour', 'tour')):
        box = page.evaluate("s => { const r = document.querySelector(s).getBoundingClientRect(); return {x:0, y: r.top + window.scrollY, w: r.width, h: r.height}; }", sel)
        page.screenshot(path=os.path.join(OUT, '%s-%s.png' % (name, label)), full_page=True, clip={'x': 0, 'y': box['y'], 'width': width, 'height': min(box['h'], 4000)})

    # --- interactions ---
    # date form: invalid then valid
    page.click('#date-form button[type=submit]')
    if page.evaluate("document.getElementById('date-error').hidden"):
        problems.append('%s: date form did not show a validation error on empty submit' % name)
    page.fill('#f-date', '2027-05-15')
    page.fill('#f-guests', '140')
    page.fill('#f-contact', 'sam@example.com')
    page.click('#date-form button[type=submit]')
    page.wait_for_timeout(300)
    if not page.is_visible('#date-confirm'):
        problems.append('%s: date confirmation not shown' % name)
    txt = page.inner_text('#date-confirm')
    if 'Saturday, May 15' not in txt or '140' not in txt or 'Held for 24 hours' not in txt:
        problems.append('%s: date confirmation text wrong: %s' % (name, txt[:120]))
    page.screenshot(path=os.path.join(OUT, '%s-date-confirm.png' % name), full_page=True, clip=page.evaluate("() => { const r = document.getElementById('check').getBoundingClientRect(); return {x: Math.max(0, r.left-12), y: Math.max(0, r.top-12+window.scrollY), width: Math.min(window.innerWidth, r.width+24), height: r.height+24}; }"))
    page.click('#date-again')
    if page.is_visible('#date-confirm'):
        problems.append('%s: date form did not reset' % name)

    # scheduler
    page.evaluate("document.getElementById('tour').scrollIntoView({block:'start'})")
    page.wait_for_timeout(200)
    page.click('#cal-next')
    day = page.query_selector('#cal button[data-date]:not([disabled])')
    if not day:
        problems.append('%s: no available day in next month' % name)
    else:
        day.click()
        slot = page.query_selector('#slots button[data-slot]')
        if not slot:
            problems.append('%s: no slots rendered' % name)
        else:
            slot.click()
            if page.evaluate("document.getElementById('book').disabled"):
                problems.append('%s: book button still disabled after picking day+slot' % name)
            page.click('#book')
            page.wait_for_timeout(300)
            if not page.is_visible('#tour-confirm') or 'on the calendar' not in page.inner_text('#tour-confirm'):
                problems.append('%s: tour confirmation not shown' % name)
            page.screenshot(path=os.path.join(OUT, '%s-tour-confirm.png' % name), full_page=True, clip=page.evaluate("() => { const r = document.getElementById('scheduler').getBoundingClientRect(); return {x: Math.max(0, r.left-12), y: Math.max(0, r.top-12+window.scrollY), width: Math.min(window.innerWidth, r.width+24), height: r.height+24}; }"))
            page.click('#tour-again')
            if page.is_visible('#tour-confirm'):
                problems.append('%s: scheduler did not reset' % name)

    # guide
    page.fill('#g-email', 'not-an-email')
    page.click('#guide-form button[type=submit]')
    if page.evaluate("document.getElementById('guide-error').hidden"):
        problems.append('%s: guide form accepted an invalid email' % name)
    page.fill('#g-email', 'sam@example.com')
    page.click('#guide-form button[type=submit]')
    page.wait_for_timeout(300)
    if not page.is_visible('#guide-confirm') or 'Guide sent' not in page.inner_text('#guide-confirm'):
        problems.append('%s: guide confirmation not shown' % name)

    # keyboard: tab reaches the date input and the first calendar day
    page.evaluate("window.scrollTo(0,0)")
    page.focus('#f-date')
    focused = 'f-date'
    for _ in range(4):
        page.keyboard.press('Tab')
        focused = page.evaluate("document.activeElement.id")
        if focused != 'f-date':
            break
    if focused != 'f-guests':
        problems.append('%s: tab order from date input landed on %r' % (name, focused))

    # mobile nav
    if mobile:
        page.click('.nav-toggle')
        if not page.is_visible('#nav-links'):
            problems.append('%s: mobile nav did not open' % name)
        page.click('.nav-toggle')

    # network: no non-localhost requests other than fonts
    reqs = page.evaluate("performance.getEntriesByType('resource').map(r => r.name).filter(n => !n.startsWith('http://localhost') && !n.includes('fonts.g'))")
    if reqs:
        problems.append('%s: unexpected external requests: %s' % (name, reqs[:5]))
    if errors:
        problems.append('%s: console/page errors: %s' % (name, errors[:6]))
    print('%s: fonts loaded %s, scrollWidth %d/%d, %d images, page height %d, shot %s' % (name, fonts, sw, iw, len(imgs), page.evaluate('document.body.scrollHeight'), shot))
    for i in imgs:
        print('   img %-32s %-26s rendered %4dpx  natural %4dpx' % (i['alt'], i['cur'], i['cw'], i['nw']))
    ctx.close()

with sync_playwright() as pw:
    run(pw, 'desktop', 1440, 900, 1, False)
    run(pw, 'mobile', 390, 844, 2, True)

print()
if problems:
    print('PROBLEMS:')
    for p in problems:
        print(' -', p)
    sys.exit(1)
print('ALL CHECKS PASSED')
