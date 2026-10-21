"""Run every test module without pytest: python3 -m tests.run_all (from factory/)."""
import importlib, sys
from tests import _util

MODULES = ['test_palette', 'test_dialects', 'test_fingerprint', 'test_schema', 'test_exclusions', 'test_templates']

if __name__ == '__main__':
    bad = 0
    for name in MODULES:
        print('== %s' % name)
        bad += _util.run_module(importlib.import_module('tests.' + name))
    print('ALL PASSED' if not bad else '%d module(s) failed' % bad)
    sys.exit(1 if bad else 0)
