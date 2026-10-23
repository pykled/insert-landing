"""Build-time lint for rendered pages (stage 3A): no unset value may leak into what a visitor or a crawler sees.

Scans visible text nodes, attribute values, inline script text and JSON-LD. Python `None`, `NaN`, JS `undefined`/`null`
rendered as text, `mailto:None`, and the punctuation an empty slot leaves behind ("house. .", "()") fail the build.
Inline script *code* may use `null`/`undefined` as literals, so in scripts only `None`/`NaN` and quoted
'null'/'undefined' strings count. JSON-LD must not carry null values at all (omit the key instead).
"""
import json, re
from html.parser import HTMLParser

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


def lint_html(html):
    """Returns a list of problems (empty = clean)."""
    p = _P()
    p.feed(html)
    p.close()
    return p.problems
