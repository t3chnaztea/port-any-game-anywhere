# Validation commands and limits

From a clean checkout, run:

```sh
python3 tools/check_repository.py
python3 -m unittest discover -s tests -v
python3 -m unittest discover -s evaluations/tests -v
python3 -m unittest discover -s examples/fifteen-pilot -p 'test_*.py' -v
```

Python 3.11 or newer is required. Cross-language tests also need Clang and Node 22.18 or newer. A skipped dependency test is not port acceptance. GitHub Actions checks Python 3.11/3.13 with Node 26; that configured workflow is not a claim that remote CI has run.

Build and test the browser example:

```sh
npm --prefix examples/recovery-puzzle ci --ignore-scripts --no-audit --no-fund
npm --prefix examples/recovery-puzzle test
python3 tools/build_example.py
```

Optional browser automation uses the versions in `requirements-dev.txt` and an installed browser. See [Switchboard](../examples/recovery-puzzle/README.md). Do not infer real-device acceptance from touch emulation.

Inspect a portable development archive:

```sh
python3 tools/build_release.py --development
```

The archive has a fixed file order, timestamps, checksums and an explicit development status. An existing archive is never overwritten. Normal release mode refuses a development version and requires all [release gates](../release-ledger.json).

The [evaluation pack](../evaluations/README.md) separates deterministic validator checks, client installation smoke checks, and paired live agent trials. Synthetic validator fixtures are not real benchmark results. A same-host installation smoke run does not establish isolation from evaluator material.

Repository pattern checks cannot prove licensing, absence of all secrets, test quality, or human observations. Those remain independent review responsibilities.
