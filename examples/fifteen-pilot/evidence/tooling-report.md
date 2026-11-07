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
| Initial browser preflight | `BLOCKED: missing tools: emcc, emcmake`; compilation did not start |
| Local SDK setup | Emscripten 6.0.10 installed in ignored `.work/emsdk`; pinned commit and packages in build-summary.json |
| First real link | Failed: upstream Firefox minimum 68 is below compiler minimum 79; failed log preserved |
| Corrected browser build | Built using upstream CMake minima Firefox79/Chrome85/Safari15; game source unchanged |
| Generated files | HTML 11,078 bytes; JS 40,682 bytes; WASM 94,568 bytes; exact hashes in build-summary.json |
| JavaScript syntax | `node --check` passed; this did not execute the game |
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

SDK packages total 373,326,182 compressed bytes. The SDK including retained archives
used about 2.1 GiB. Installation and compilation used one job at priority 20.
SDK configuration stayed inside the SDK. Monitored user configuration/startup
identities were unchanged after activation and build. No VM, Java, or server was started.

The download hash was computed from retrieved bytes. It was not compared with an
independent publisher-signed checksum. Upstream CMake and its page generator were
executed. The game runtime was not. Route fixture expectations remain unverified. All 51 known
required game claims stay untested: 26 desktop claims and 25 iPhone claims.
