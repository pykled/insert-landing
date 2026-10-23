"""Polite fetcher + crawl frontier. robots.txt respected (its Crawl-delay too), >= 1 s between requests to any one host,
same registrable domain only, public HTML pages only (no PDFs, admin, carts, feeds, booking portals)."""
import re, time, urllib.request, urllib.error, urllib.robotparser, gzip
from urllib.parse import urlparse, urlunparse, urljoin
import xml.etree.ElementTree as ET

UA = 'InsertIntake/1.0 (+https://insert-landing-production.up.railway.app; one-off venue research, 1 req/s)'
TWO_LEVEL = ('co.uk', 'org.uk', 'com.au', 'co.nz', 'co.za', 'com.br', 'co.jp')
SKIP_PATH = re.compile(r'\.(pdf|docx?|xlsx?|pptx?|zip|jpe?g|png|gif|webp|svg|mp4|mov|mp3|ics|xml|json|css|js|txt)$|'
                       r'/(wp-admin|wp-login|wp-json|feed|cart|checkout|my-account|account|login|signin|sign-in|register|'
                       r'tag|author|category|comments?|xmlrpc|cdn-cgi|portal|client-portal|booking|book-online|search)(/|$)|'
                       r'/page/\d+/?$', re.I)
BLOGGY = re.compile(r'/(blog|news|post|posts|journal|real-weddings?|featured-weddings?)(/|$)|/\d{4}/\d{2}/', re.I)


def registrable(host):
    host = (host or '').lower().split(':')[0]
    if host.startswith('www.'):
        host = host[4:]
    parts = host.split('.')
    n = 3 if '.'.join(parts[-2:]) in TWO_LEVEL else 2
    return '.'.join(parts[-n:])


def normalise(u):
    p = urlparse(u)
    if p.scheme not in ('http', 'https'):
        return None
    path = re.sub(r'/{2,}', '/', p.path or '/')
    return urlunparse((p.scheme, p.netloc.lower(), path, '', '', ''))


def same_site(u, root):
    return registrable(urlparse(u).netloc) == registrable(urlparse(root).netloc)


def page_ok(u, root):
    n = normalise(u)
    return bool(n) and same_site(n, root) and not SKIP_PATH.search(urlparse(n).path)


class Fetcher:
    def __init__(self, min_delay=1.0, log=None, timeout=25):
        self.min_delay, self.timeout = min_delay, timeout
        self.last, self.robots, self.delays = {}, {}, {}
        self.log = log if log is not None else []
        self.requests = 0

    def _robots(self, host, scheme):
        if host not in self.robots:
            rp = urllib.robotparser.RobotFileParser()
            url = '%s://%s/robots.txt' % (scheme, host)
            st, _, body, _ = self._raw(url, host)
            if st == 200 and body:
                rp.parse(body.decode('utf-8', 'replace').splitlines())
            else:
                rp.parse([])
            cd = rp.crawl_delay(UA) or rp.crawl_delay('*')
            self.delays[host] = max(self.min_delay, float(cd or 0))
            self.robots[host] = rp
            self.log.append({'url': url, 'status': st, 'note': 'robots.txt; delay %.1fs' % self.delays[host]})
        return self.robots[host]

    def sitemaps(self, root):
        p = urlparse(root)
        rp = self._robots(p.netloc, p.scheme)
        return list(getattr(rp, 'site_maps', lambda: None)() or [])

    def _raw(self, url, host, max_bytes=30_000_000):
        wait = self.delays.get(host, self.min_delay) - (time.time() - self.last.get(host, 0))
        if wait > 0:
            time.sleep(wait)
        self.last[host] = time.time()
        self.requests += 1
        req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept-Encoding': 'gzip'})
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as r:
                body = r.read(max_bytes)
                if r.headers.get('Content-Encoding') == 'gzip':
                    body = gzip.decompress(body)
                return r.status, r.headers.get('Content-Type', ''), body, r.geturl()
        except urllib.error.HTTPError as e:
            return e.code, '', b'', url
        except Exception as e:  # network errors are logged, never fatal
            return 0, str(e)[:120], b'', url

    def get(self, url, check_robots=True):
        p = urlparse(url)
        if check_robots:
            rp = self._robots(p.netloc, p.scheme)
            if not (rp.can_fetch(UA, url) and rp.can_fetch('*', url)):
                self.log.append({'url': url, 'status': None, 'note': 'disallowed by robots.txt'})
                return None, '', b'', url
        st, ct, body, final = self._raw(url, p.netloc)
        return st, ct, body, final


def sitemap_urls(fetcher, root, limit=400):
    """Page URLs from robots Sitemap: lines or /sitemap.xml; nested indexes followed (page sitemaps before posts)."""
    todo = fetcher.sitemaps(root) or [urljoin(root, '/sitemap.xml')]
    seen, out = set(), []
    while todo and len(seen) < 8:
        sm = todo.pop(0)
        if sm in seen:
            continue
        seen.add(sm)
        st, ct, body, _ = fetcher.get(sm)
        fetcher.log.append({'url': sm, 'status': st, 'note': 'sitemap'})
        if st != 200 or not body:
            continue
        try:
            tree = ET.fromstring(body)
        except ET.ParseError:
            continue
        locs = [e.text.strip() for e in tree.iter() if e.tag.endswith('loc') and e.text]
        if tree.tag.endswith('sitemapindex'):
            subs = sorted(locs, key=lambda u: (bool(re.search(r'post|blog|tag|categor|author|attachment|product', u)), u))
            todo.extend(subs)
        else:
            out.extend(locs)
        if len(out) >= limit:
            break
    return out[:limit]


def priority(u, nav_set):
    path = urlparse(u).path
    depth = len([x for x in path.split('/') if x])
    return (0 if u in nav_set else 1, 1 if BLOGGY.search(path) else 0, depth, len(path))
