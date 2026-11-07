# Tooling report

Run date: 2026-11-07. Host: macOS on ARM64. This report covers pilot tooling only.
It is not game acceptance evidence and cannot close a game claim in the ledger.

| Check | Observed result |
| --- | --- |
| Named official HTTPS source | Downloaded 2,497,958 bytes; archive identity in source-lock.json |
| Archive root | `puzzles-20260923.616da16` |
| Source extraction | 326 members; 11,399,452 declared unpacked bytes; no links |
| Source-tree check | `VERIFIED: source tree matches pinned archive; no game test performed` |
| Default preflight | `blocked`; archive verified; emcc/emcmake absent; no network used |
| Browser build attempt | `BLOCKED: missing tools: emcc, emcmake`; compilation did not start |
| Native macOS source check | CMake requires absent Halibut; native build not attempted |
| Safety tests | 15 tests passed; controlled fixtures only |
| Gameplay, native reference, devices | Not run |

Commands from repository root:

```sh
python3 examples/fifteen-pilot/pilot.py extract
python3 examples/fifteen-pilot/pilot.py preflight
python3 examples/fifteen-pilot/pilot.py build-web
python3 -m unittest discover -s examples/fifteen-pilot -p 'test_*.py' -v
```

The download hash was computed from retrieved bytes. It was not compared with an
independent publisher-signed checksum. Upstream code and the frontend were inspected
but not executed. Route fixture expectations remain unverified. All 51 known
required game claims stay untested: 26 desktop claims and 25 iPhone claims.
