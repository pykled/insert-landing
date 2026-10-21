"""Shared helpers: put factory/ on sys.path, load data files, and run a module's test_* functions without pytest."""
import json, os, sys, traceback

FACTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if FACTORY not in sys.path:
    sys.path.insert(0, FACTORY)


def data(name):
    return json.load(open(os.path.join(FACTORY, 'data', name)))


def content(slug='stonehurst'):
    return json.load(open(os.path.join(FACTORY, 'content', slug + '.json')))


def run_module(mod):
    """python3 -m tests.<module> runs every test_* function; exit code 1 on any failure."""
    names = sorted(n for n in dir(mod) if n.startswith('test_') and callable(getattr(mod, n)))
    failed = 0
    for n in names:
        try:
            fn = getattr(mod, n)
            if fn.__code__.co_argcount:
                import tempfile
                with tempfile.TemporaryDirectory() as d:
                    fn(d)
            else:
                fn()
            print('ok    %s.%s' % (mod.__name__, n))
        except Exception:
            failed += 1
            print('FAIL  %s.%s' % (mod.__name__, n))
            traceback.print_exc(limit=3)
    print('%d passed, %d failed' % (len(names) - failed, failed))
    return 1 if failed else 0
