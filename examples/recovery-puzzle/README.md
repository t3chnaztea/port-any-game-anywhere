# Switchboard

An original six-board puzzle for testing a port workflow. The C reference and TypeScript port are **source-authored**. No blinded source recovery has been completed.

All code uses the repository's MIT license. The boards use text shapes and generated sounds. See [asset handling](ASSETS.md), [the frozen behavior contract](CONTRACT.md), [defects and independent checks](BUGS.md), and [the completion ledger](completion-ledger.json).

## Run the example

From the repository root, with Clang, Node.js 22.18 or newer, and npm available:

```sh
npm --prefix examples/recovery-puzzle ci --ignore-scripts --no-audit --no-fund
python3 tools/build_example.py
.work/switchboard/switchboard
```

The native game prints its commands. Enter `new campaign`, then directions such as `right`. Use `save PATH` and `load PATH` for explicit persistence. Enter `quit` to exit.

Serve the browser build locally:

```sh
python3 -m http.server 8000 --bind 127.0.0.1 --directory .work/switchboard/site
```

Open `http://127.0.0.1:8000`. Stop the server with Ctrl+C. No game assets, service account, or API key are needed.

## Check the port

```sh
python3 -m unittest discover -s tests -p test_switchboard.py -v
npm --prefix examples/recovery-puzzle test
```

Expected output is `OK` for the Python fixtures and zero failed Node tests. The checks cover both modes, all boards, the final transition, undo boundaries, cold loads, corruption, and failed writes. The normal action interface drives both programs. An independent route search generates completion routes. This is stronger than a boot check. Shared authorship and a shared contract limit comparison independence.

The optional browser check needs Playwright. It uses an installed Chrome when available. It never downloads a browser:

```sh
python3 -m venv .work/venv
.work/venv/bin/python -m pip install -r requirements-dev.txt
.work/venv/bin/python tools/check_browser.py
```

The script tests real DOM buttons and keyboard actions. Quota and damaged-save tests are separately labeled controlled fixtures. Touch emulation does not establish actual iPhone acceptance. Sound still requires a listener.

## Record inspectable evidence

Use a new record name for each run:

```sh
mkdir -p examples/recovery-puzzle/evidence/local
python3 skills/port-any-game-anywhere/scripts/record_run.py examples/recovery-puzzle/evidence/fixture-producer.manifest.json --output examples/recovery-puzzle/evidence/local/fresh-001.json
python3 skills/port-any-game-anywhere/scripts/check_port.py examples/recovery-puzzle/completion-ledger.json
```

The recorder refuses to overwrite an existing result. Move a new result into the ledger only after reviewing what ran. A command pass alone does not establish complete game coverage. Current records are bound to their recorded files and host tools. A different checkout may report them stale. Rerun there instead of editing fingerprints.

## Prepare a future recovery trial

Build the reference on Linux x86-64 with Clang. Strip symbols in a copy. Give a new recovery agent only that executable, the public game instructions, and permitted tools in an isolated workspace. Withhold this repository's reference and TypeScript source, hidden checks, and evaluator notes. Disable source lookup in both trial and baseline. Freeze results before source disclosure.

The Linux/Ghidra adapter, recovered-C build, matched agent trials, independent final audit, actual iPhone/Safari, and audible results remain required. This source-authored demonstration does not close them.
