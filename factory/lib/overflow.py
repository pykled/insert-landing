"""Per-element horizontal overflow (stage 3A), shared by qa.py and the tests.

documentElement.scrollWidth alone misses text that runs out of its own box (a long tracked-caps word in a band whose
section clips only part of it) and anything a clipping ancestor hides from the page width. This reports, per element:
  - 'past viewport': a visible box whose right edge passes the viewport (or left edge < 0) and that no clipping ancestor
    contains;
  - 'text overflows box': a text-bearing element whose own scrollWidth exceeds its clientWidth while its overflow is
    visible (the word is wider than the column, even if the page width happens to survive).
Each offender comes with a short CSS selector so the fix can be found.
"""

OVERFLOW_JS = r"""() => {
  const iw = window.innerWidth, out = [];
  const sel = (e) => {
    const parts = [];
    for (let n = e; n && n.nodeType === 1 && parts.length < 4; n = n.parentElement) {
      let s = n.tagName.toLowerCase();
      if (n.id) { parts.unshift(s + '#' + n.id); break; }
      const cls = [...n.classList].filter(c => !/^(reveal|visible|d\d|on|active)$/.test(c)).slice(0, 2);
      if (cls.length) s += '.' + cls.join('.');
      parts.unshift(s);
    }
    return parts.join(' > ');
  };
  const visible = (e, cs) => cs.display !== 'none' && cs.visibility !== 'hidden' && +cs.opacity > 0.01 && !e.closest('[hidden]') && !(cs.clip && cs.clip !== 'auto') && cs.clipPath === 'none';
  const clippedBy = (e, r) => {
    for (let a = e.parentElement; a && a !== document.documentElement; a = a.parentElement) {
      const c = getComputedStyle(a);
      if (/(hidden|clip|auto|scroll)/.test(c.overflowX)) {
        const ar = a.getBoundingClientRect();
        if (ar.right <= iw + 1 && ar.left >= -1) return true;
      }
    }
    return false;
  };
  const TEXT = new Set(['H1','H2','H3','H4','H5','H6','P','LI','A','BUTTON','SPAN','B','STRONG','EM','SMALL','DT','DD','TD','TH','LABEL','CITE','FIGCAPTION','BLOCKQUOTE','OUTPUT']);
  for (const e of document.body.querySelectorAll('*')) {
    const cs = getComputedStyle(e);
    if (!visible(e, cs) || cs.position === 'fixed') continue;
    const r = e.getBoundingClientRect();
    if (r.width < 1 || r.height < 1) continue;
    const hasText = TEXT.has(e.tagName) && [...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());
    const past = r.right > iw + 1 || r.left < -1;
    if (past && !clippedBy(e, r))
      out.push({kind: 'past viewport', sel: sel(e), right: Math.round(r.right), left: Math.round(r.left)});
    else if (past && hasText)
      out.push({kind: 'text cut off by a clipping ancestor', sel: sel(e), right: Math.round(r.right), left: Math.round(r.left)});
    else if (hasText && cs.display !== 'inline' && cs.textOverflow !== 'ellipsis' && e.scrollWidth > e.clientWidth + 1)
      out.push({kind: 'text overflows box', sel: sel(e), by: e.scrollWidth - e.clientWidth});
  }
  // report the outermost offender of each chain only
  return out.filter((o, i) => !out.slice(0, i).some(p => p.kind === o.kind && o.sel.startsWith(p.sel + ' > '))).slice(0, 12);
}"""


def element_overflow(page):
    """List of human-readable offender strings (empty = no horizontal overflow anywhere)."""
    rows = page.evaluate(OVERFLOW_JS)
    msgs = []
    for o in rows:
        if 'right' in o:
            msgs.append('%s: %s (left %d, right %d)' % (o['kind'], o['sel'], o['left'], o['right']))
        else:
            msgs.append('%s: %s (+%d px)' % (o['kind'], o['sel'], o['by']))
    return msgs
