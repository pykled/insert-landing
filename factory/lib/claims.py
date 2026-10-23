"""Invented-content checks (stage 3A), shared by qa.py and the tests. Pure HTML + content JSON, no browser.

1. deny_list(html, content): service promises, holds, response times and preset venue words (the hall, the long table,
   at dinner, by appointment...) may appear only when the venue's own content file says the same thing. Every page
   string is scanned, hidden confirmations included.
2. untraced_numbers(html, content): every number in a heading, lead, stat block or fact list must be a number the content
   file states (any numeric value, or digits inside any content string), or the sum / difference / product of two of
   them. Sequence labels (01, 02 ...) and the build's own controls are exempt by class.
3. preview_labels(html): every date-check, tour-scheduler and pricing-guide surface carries the
   'Preview of how inquiries could work' micro-label (Insert's proposed automations, not the venue's policy).
"""
import itertools, json, re
from html.parser import HTMLParser

PREVIEW_PHRASE = 'Preview of how inquiries could work'

DENY = [
    r'in under (a|one) minute', r'reply in (a|one|\d+) (minute|hour)', r'within (a|one|\d+) (minute|hour|day)s?',
    r'courtesy hold', r'held for \d+', r'\d+[- ]hours? hold', r'hold (releases|expires)', r"we've placed", r'placed a hold',
    r"we'll text", r'text(ed)? you', r'(a )?text confirm', r'confirmation (is )?(sent|arrives|follows)', r'confirms it',
    r'reminder (follows|the day before)', r'reschedul', r'no drip', r'spam folder', r'right away', r'at once', r'straight away',
    r"you're on the calendar", r'guide sent', r"it's on its way", r'a person replies', r'not a bot', r'replies within',
    r'\bthe hall\b', r'long table', r'at dinner', r'by appointment', r'one (event|wedding) a day', r'weekends go fast',
    r'distinct looks', r'private property', r'including breakdown', r'planner required', r'directions (to the gate|arrive)',
]
DENY_RE = re.compile('|'.join('(?:%s)' % p for p in DENY), re.I)

# classes whose numbers are sequence labels or UI, not venue facts
EXEMPT_CLASS = re.compile(r'(-n\b|\bjnum\b|\bnum\b|\bidx\b|counter|\bslot|\bcal\b|fit-scale|pager)')
FACT_CLASS = re.compile(r'lede|deck|stat|fact|number|ledger|mast-facts|glance|light-time|light-sched|count|capn|cap\b|td-cap|lp-label|mq-count|al-ledger|figure')
FACT_TAGS = {'h1', 'h2', 'h3', 'h4', 'dt', 'dd'}
NUM_RE = re.compile(r'(?<![\w.])(\d{1,3}(?:,\d{3})+|\d+(?:\.\d+)?)(?![\w])')
VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'source', 'track', 'wbr'}


def _content_text(content):
    out = []

    def walk(x):
        if isinstance(x, dict):
            for k, v in x.items():
                if not str(k).startswith('_'):
                    walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
        elif isinstance(x, str):
            out.append(x)
        elif isinstance(x, (int, float)) and not isinstance(x, bool):
            out.append(str(x))
    walk(content)
    return out


SKIP_KEYS = re.compile(r'^(_.*|phone.*|address.*|website|url|.*_url|source.*|email.*|photos|preview|facts|slug|\$schema)$')


def _fact_values(content):
    """(strings, numbers) from fact fields only: contact numbers, URLs, sources, photo metadata are not venue facts."""
    strs, nums = [], []

    def walk(x):
        if isinstance(x, dict):
            for k, v in x.items():
                if not SKIP_KEYS.match(str(k)):
                    walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
        elif isinstance(x, str):
            strs.append(x)
        elif isinstance(x, (int, float)) and not isinstance(x, bool):
            nums.append(float(x))
    walk(content)
    return strs, nums


def content_numbers(content):
    """Direct matches may come from any content string (an address or phone in the footer is the venue's own)."""
    out = set(_fact_values(content)[1])
    for s in _content_text(content):
        for m in NUM_RE.finditer(s):
            out.add(float(m.group(1).replace(',', '')))
    return out


def _traces(n, nums, pair_cache, content=None):
    if n in nums:
        return True
    if pair_cache[0] is None:
        small = sorted(set(_fact_values(content)[1]))[:200] if content is not None else sorted(nums)[:200]
        s = set()
        for a, b in itertools.combinations_with_replacement(small, 2):
            s.update((a + b, abs(a - b), a * b))
        pair_cache[0] = s
    return n in pair_cache[0]


class _Collect(HTMLParser):
    """Visible-ish text per element with its tag/class chain; script/style skipped."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.texts, self.skip = [], [], 0

    def handle_starttag(self, tag, attrs):
        if tag in VOID:
            return
        d = dict(attrs)
        self.stack.append((tag, d.get('class') or '', d))
        if tag in ('script', 'style', 'template', 'noscript'):
            self.skip += 1

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        while self.stack:
            t, _, _ = self.stack.pop()
            if t in ('script', 'style', 'template', 'noscript'):
                self.skip -= 1
            if t == tag:
                break

    def handle_data(self, data):
        if self.skip or not data.strip():
            return
        self.texts.append((list(self.stack), ' '.join(data.split())))


def _texts(html):
    c = _Collect()
    c.feed(html)
    c.close()
    return c.texts


def _sel(stack):
    return ' > '.join(t + ('.' + c.split()[0] if c.split() else '') for t, c, _ in stack[-3:])


def deny_list(html, content):
    blob = ' '.join(_content_text(content)).lower()
    probs, seen = [], set()
    for stack, text in _texts(html):
        for m in DENY_RE.finditer(text):
            phrase = m.group(0).lower()
            if re.match(r'one (event|wedding) a day', phrase) and ((content.get('tagline_facts') or {}).get('events_per_day') == 1):
                continue   # the venue states one event per day
            if phrase in blob or (phrase, text) in seen:
                continue
            seen.add((phrase, text))
            probs.append('invented claim "%s" not in the content file: %s: "%s"' % (m.group(0), _sel(stack), text[:90]))
    return probs


def untraced_numbers(html, content):
    nums = content_numbers(content)
    cache = [None]
    probs = []
    for stack, text in _texts(html):
        if any(EXEMPT_CLASS.search(c) for _, c, _ in stack) or any(t in ('form', 'button', 'label', 'select', 'option') for t, _, _ in stack):
            continue
        is_fact = any(t in FACT_TAGS for t, _, _ in stack) or any(FACT_CLASS.search(c) for _, c, _ in stack)
        if not is_fact:
            continue
        for m in NUM_RE.finditer(text):
            n = float(m.group(1).replace(',', ''))
            if not _traces(n, nums, cache, content):
                probs.append('number %s does not trace to the content file: %s: "%s"' % (m.group(1), _sel(stack), text[:90]))
    return probs


def preview_labels(html):
    """Each automation surface (date form, scheduler, guide form) must contain the preview micro-label."""
    probs = []
    for sid, what in (('check', 'date check'), ('scheduler', 'tour scheduler'), ('guide-wrap', 'pricing guide')):
        m = re.search(r'<div[^>]*\bid="%s"[^>]*>' % sid, html)
        if not m:
            continue
        # the label is the first element inside the surface
        tail = html[m.end():m.end() + 1500]
        if PREVIEW_PHRASE not in tail:
            probs.append('%s has no "%s" label' % (what, PREVIEW_PHRASE))
    return probs


def check(html, content):
    return deny_list(html, content) + untraced_numbers(html, content) + preview_labels(html)


if __name__ == '__main__':
    import sys
    h = open(sys.argv[1]).read()
    c = json.load(open(sys.argv[2]))
    for p in check(h, c)[:40]:
        print(p)
