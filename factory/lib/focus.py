"""Focus visibility probe (3A F5): every keyboard-reachable control must show a focus indicator.

Walks the page with real Tab presses (so :focus-visible matches as it would for a keyboard user). For each control:
  - computed style: outline-style / box-shadow while focused (recorded; 'none' on both is a failure)
  - pixel diff: a viewport shot focused vs the same box after blur(). A pixel counts as indicator when its colour
    changed by >= 3:1 (WCAG 2.2 2.4.13 'change of contrast'). The indicator area must be at least a 2 CSS px thick
    perimeter of the control (x DPR^2), with a 15% allowance for rounded corners and anti-aliasing.
Returns (problems, rows). Pure-numpy helpers are separate so tests can run them without a browser.
"""
import io
import numpy as np
from PIL import Image

PAD = 8          # css px around the control included in both shots (the ring sits up to 5 px outside)
MIN_CHANGE = 3.0
AREA_SHARE = 0.85


def _lum(arr):
    c = arr[..., :3].astype(np.float64) / 255.0
    c = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    return 0.2126 * c[..., 0] + 0.7152 * c[..., 1] + 0.0722 * c[..., 2]


def changed_pixels(before, after, min_ratio=MIN_CHANGE):
    """Count pixels whose colour changed by at least min_ratio (contrast ratio between the two states)."""
    a, b = _lum(before), _lum(after)
    hi, lo = np.maximum(a, b), np.minimum(a, b)
    return int(((hi + 0.05) / (lo + 0.05) >= min_ratio).sum())


def required_area(w, h, scale, thick=2.0, radius=0.0):
    """Device px of a `thick` CSS px ring along the perimeter of a w x h CSS px box with corner radius (WCAG 2.4.13 uses
    the perimeter of the unfocused component, so a pill's is 2(w+h) - (8 - 2 pi) r)."""
    r = min(radius, w / 2, h / 2)
    return (2 * (w + h) - (8 - 2 * 3.14159265) * r) * thick * scale * scale * AREA_SHARE


TAG_JS = """() => { const e = document.activeElement; if (!e || e === document.body) return null;
  if (!e.hasAttribute('data-fq')) e.setAttribute('data-fq', String(window.__fq = (window.__fq || 0) + 1));
  e.scrollIntoView({block: 'center', inline: 'nearest', behavior: 'instant'});
  const r = e.getBoundingClientRect(), cs = getComputedStyle(e);
  return {id: e.getAttribute('data-fq'), tag: e.tagName.toLowerCase(), cls: (e.className && e.className.baseVal === undefined ? e.className : '').toString().slice(0, 40),
    label: (e.getAttribute('aria-label') || e.textContent || e.getAttribute('name') || '').trim().slice(0, 30),
    x: r.left, y: r.top, radius: parseFloat(cs.borderTopLeftRadius) || 0, w: r.width, h: r.height, outline: cs.outlineStyle + ' ' + cs.outlineWidth + ' off ' + cs.outlineOffset, shadow: cs.boxShadow,
    visible: r.width > 0 && r.height > 0 && cs.visibility !== 'hidden' && parseFloat(cs.opacity) > 0.05}; }"""


def _shot(page, box):
    return np.array(Image.open(io.BytesIO(page.screenshot(clip=box, animations='disabled'))).convert('RGB'))


def check(page, name, scale, limit=250):
    problems, rows = [], []
    vw, vh = page.evaluate('[innerWidth, innerHeight]')
    page.mouse.move(vw - 2, vh - 2)
    # smooth scrolling (dialect CSS) keeps moving the page between the two shots and misaligns the diff
    page.add_style_tag(content='html, body, * { scroll-behavior: auto !important; }')
    page.evaluate("document.activeElement && document.activeElement.blur(); window.scrollTo(0, 0)")
    seen, first, repeats = set(), None, 0
    for _ in range(limit):
        page.keyboard.press('Tab'); page.wait_for_timeout(30)
        r = page.evaluate(TAG_JS)
        if r is None:   # focus left the document (past the last control)
            if seen: break
            continue
        if r['id'] == first: break   # wrapped around
        if r['id'] in seen:   # date inputs keep focus across their month/day/year segments
            repeats += 1
            if repeats > 12: break
            continue
        first = first or r['id']; repeats = 0
        seen.add(r['id'])
        if not r['visible']: continue
        x0, y0 = max(0, r['x'] - PAD), max(0, r['y'] - PAD)
        x1, y1 = min(vw, r['x'] + r['w'] + PAD), min(vh, r['y'] + r['h'] + PAD)
        if x1 - x0 < 4 or y1 - y0 < 4: continue
        box = {'x': x0, 'y': y0, 'width': x1 - x0, 'height': y1 - y0}
        after = _shot(page, box)
        page.evaluate("document.activeElement.blur()"); page.wait_for_timeout(30)
        before = _shot(page, box)
        page.evaluate("id => { const e = document.querySelector('[data-fq=\"' + id + '\"]'); e && e.focus({preventScroll: true}); }", r['id'])
        n = changed_pixels(before, after)
        need = required_area(min(r['w'], vw), min(r['h'], vh), scale, radius=r['radius'])
        row = {'id': r['id'], 'el': '%s.%s "%s"' % (r['tag'], r['cls'].split(' ')[0], r['label']), 'changed': n, 'need': int(need), 'outline': r['outline'], 'shadow': r['shadow'][:60]}
        rows.append(row)
        no_style = r['outline'].startswith('none') and r['shadow'] in ('none', '')
        if no_style or n < need:
            problems.append('%s: focus not visible on %s (%d px changed >= 3:1, need %d; outline %s, shadow %s)' % (name, row['el'], n, need, r['outline'], row['shadow']))
    page.evaluate("document.querySelectorAll('[data-fq]').forEach(e => e.removeAttribute('data-fq')); document.activeElement && document.activeElement.blur()")
    if not rows: problems.append('%s: focus walk reached no visible control' % name)
    return problems, rows
