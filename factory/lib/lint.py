"""Build-time lint for rendered pages (stage 3A): no unset value may leak into what a visitor or a crawler sees.

Scans visible text nodes, attribute values, inline script text and JSON-LD. Python `None`, `NaN`, JS `undefined`/`null`
rendered as text, `mailto:None`, and the punctuation an empty slot leaves behind ("house. .", "()") fail the build.
Inline script *code* may use `null`/`undefined` as literals, so in scripts only `None`/`NaN` and quoted
'null'/'undefined' strings count. JSON-LD must not carry null values at all (omit the key instead).
"""
import json, re
from html.parser import HTMLParser
from html import unescape as _unescape

TEXT_TOKENS = re.compile(r'\b(None|NaN|undefined|null)\b')
SCRIPT_TOKENS = re.compile(r'\b(None|NaN)\b|([\'"])(null|undefined|None)\2')
EMPTY_SLOT = re.compile(r'\w\s*\.\s+\.(?!\.)|\(\s*\)|\s,\s*[.,]|:\s*\.(\s|$)')
VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'source', 'track', 'wbr'}


class _P(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.problems, self.stack, self.script_type = [], [], None

    def _where(self):
        return '/'.join(self.stack[-3:]) or 'document'

    def handle_starttag(self, tag, attrs):
        for k, val in attrs:
            if val is None:
                continue
            m = TEXT_TOKENS.search(val)
            if m or 'mailto:None' in val:
                self.problems.append('attribute %s="%s" on <%s> contains %r' % (k, val[:60], tag, m.group(1) if m else 'mailto:None'))
        if tag == 'script':
            self.script_type = dict(attrs).get('type') or 'text/javascript'
        if tag not in VOID:
            self.stack.append(tag)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID and self.stack and self.stack[-1] == tag:
            self.stack.pop()

    def handle_endtag(self, tag):
        if tag in self.stack:
            while self.stack and self.stack.pop() != tag:
                pass
        if tag == 'script':
            self.script_type = None

    def handle_data(self, data):
        if not data.strip():
            return
        if self.script_type == 'application/ld+json':
            try:
                doc = json.loads(data)
            except ValueError as e:
                self.problems.append('JSON-LD does not parse: %s' % e)
                return
            for path, val in _walk(doc):
                if val is None:
                    self.problems.append('JSON-LD %s is null (omit the key)' % path)
                elif isinstance(val, str) and (TEXT_TOKENS.search(val) or EMPTY_SLOT.search(val)):
                    self.problems.append('JSON-LD %s = %r' % (path, val[:80]))
            return
        if self.script_type:
            for m in SCRIPT_TOKENS.finditer(data):
                self.problems.append('inline script: %r near %r' % (m.group(0), data[max(0, m.start() - 40):m.end() + 20].replace('\n', ' ')))
            return
        if self.stack and self.stack[-1] == 'style':
            return
        text = ' '.join(data.split())
        m = TEXT_TOKENS.search(text)
        if m:
            self.problems.append('text in %s contains %r: %r' % (self._where(), m.group(1), text[:90]))
        m = EMPTY_SLOT.search(text)
        if m:
            self.problems.append('text in %s has an empty-slot gap %r: %r' % (self._where(), m.group(0), text[:90]))


def _walk(doc, path='$'):
    if isinstance(doc, dict):
        for k, val in doc.items():
            yield from _walk(val, '%s.%s' % (path, k))
    elif isinstance(doc, list):
        for i, val in enumerate(doc):
            yield from _walk(val, '%s[%d]' % (path, i))
    else:
        yield path, doc


class _Blocks(HTMLParser):
    """Text of each reading block (p, headings, blockquote, figcaption, li), skipping scripts, templates, aria-hidden."""
    BLOCK = ('p', 'h1', 'h2', 'h3', 'h4', 'blockquote', 'figcaption', 'li')
    VOID = ('br', 'img', 'input', 'meta', 'link', 'hr', 'source', 'wbr', 'area', 'col', 'embed', 'track')

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.open, self.blocks = [], [], []

    def handle_starttag(self, tag, attrs):
        if tag in self.VOID: return
        a = dict(attrs)
        hidden = tag in ('script', 'style', 'template', 'noscript') or a.get('aria-hidden') == 'true' or 'hidden' in a or 'sr-only' in (a.get('class') or '').split()
        self.stack.append((tag, bool(hidden or (self.stack and self.stack[-1][1]))))
        if tag in self.BLOCK:
            for b in self.open: b[3] = True   # outer blocks with inner blocks are not counted (li > p)
            self.open.append([tag, len(self.stack), [], False])

    def handle_endtag(self, tag):
        if tag in self.VOID: return
        while self.stack:
            t, _ = self.stack.pop()
            if self.open and self.open[-1][1] == len(self.stack) + 1:
                b = self.open.pop()
                if not b[3]: self.blocks.append((b[0], ' '.join(''.join(b[2]).split())))
            if t == tag: break

    def handle_data(self, data):
        if self.stack and self.stack[-1][1]: return
        for b in self.open: b[2].append(data)


_CONTACT = re.compile(r'@|^\s*\d{1,6} [A-Z][a-z]+.*\b(CA|[A-Z]{2}) \d{5}|\(\d{3}\) \d{3}-\d{4}')


def duplicate_sentences(html, min_len=40):
    """3A F10: a reading block printed twice (e.g. the hero deck repeated by the statement section)."""
    p = _Blocks(); p.feed(html); p.close()
    seen, out = {}, []
    for tag, text in p.blocks:
        key = re.sub(r'[^a-z0-9 ]', '', text.lower())
        if len(key) < min_len or _CONTACT.search(text): continue   # addresses, emails and phones may repeat (contact, footer)
        if key in seen:
            out.append('the same sentence is printed twice (<%s> and <%s>): %r' % (seen[key], tag, text[:90]))
        seen.setdefault(key, tag)
    return out


_OPT = re.compile(r'<(p|li|h2|h3)\b([^>]*\sdata-optional-copy\b[^>]*)>(.*?)</\1>\s*', re.S)


_OSEC = re.compile(r'<section\b[^>]*\sdata-optional-section\b[^>]*>.*?</section>\s*', re.S)


def _key(text):
    return re.sub(r'[^a-z0-9 ]', '', ' '.join(_unescape(re.sub(r'<[^>]+>', ' ', text)).split()).lower())


def drop_repeated_optional(html):
    """3A F10: secondary copy (marked data-optional-copy: the statement sentence, moment lines) is removed when the same
    sentence is already printed elsewhere on the page, so the hero deck or a story line never appears twice."""
    p = _Blocks(); p.feed(html); p.close()
    counts = {}
    for _, text in p.blocks:
        k = _key(text); counts[k] = counts.get(k, 0) + 1
    def sub(m):
        k = _key(m.group(3))
        if counts.get(k, 0) >= 2:
            counts[k] -= 1
            return ''
        return m.group(0)
    html = _OPT.sub(sub, html)
    # a section that exists only to carry that copy (data-optional-section) goes too when none of its copy is left
    return _OSEC.sub(lambda m: m.group(0) if 'data-optional-copy' in m.group(0) else '', html)


def lint_html(html):
    """Returns a list of problems (empty = clean)."""
    p = _P()
    p.feed(html)
    p.close()
    return p.problems + duplicate_sentences(html)
