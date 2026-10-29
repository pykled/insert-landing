# Insert Landing

## Venue site factory

`factory/` builds the venue demo sites (see `factory/README.md`). Run its tests from inside `factory/`, not the repo root:

```
cd factory && python3 -m pytest -q tests      # ~9 min
cd factory && python3 -m tests.run_all        # same tests without pytest
```

`python3 factory/tests/run_all.py` from the repo root fails with `No module named tests`.
