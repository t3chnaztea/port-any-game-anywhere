# Fifteen: reproduce an existing browser port

This pilot applies the workflow to Simon Tatham's Fifteen puzzle. Upstream already
provides the browser port. This is a source-based reproduction exercise, not a new
port or a source-recovery result. No game acceptance gate has passed here.

The pinned source is `puzzles-20260923.616da16.tar.gz`. Its SHA-256 is
`cc419c8060b4e22be398aa03e30651fbce146eee510645c303fb6f5f1b77b78e`.
The archive is 2,497,958 bytes. [Source lock](source-lock.json) records the named
author URL, retrieval date, and the limits of this checksum's provenance.
The source archive stays in ignored `.work/`. The MIT [notice](UPSTREAM-LICENCE)
is preserved. Do not attribute the game or its existing browser port to this project.

## Current evidence

On 2026-11-07, the named archive was downloaded from the author's HTTPS site.
Its identity and extracted source tree were checked. Relevant source was inspected.
The pilot's safety tests passed. These are tooling results, not gameplay results.

A local Emscripten 6.0.10 SDK was then installed inside ignored `.work/emsdk`.
The browser build succeeded. [Build summary](evidence/build-summary.json) records
the toolchain, flags, logs, and generated file identities. The first link failed
because upstream requests browser versions older than this compiler supports.
The wrapper now selects supported minima through upstream CMake options.
This narrows compilation targets to Firefox 79, Chrome 85, and Safari 15 or newer.
It does not establish that any browser version works.

The SDK remains outside the default environment. No startup files were edited.
Halibut remains absent. No native frontend, browser game route, desktop device,
or iPhone was tested. No VM or background server was started.

See [the plan](port-plan.md), [inventory](inventory.md), and the authoritative
[completion ledger](completion-ledger.json). All game claims remain untested.
[Source review](source-review.md) separates inspected behavior from observations.

## First useful result

Run from the repository root with Python 3.11 or newer:

```sh
python3 examples/fifteen-pilot/pilot.py
```

The default is an offline preflight. It does not fetch, install, build, or start a
server. Expect JSON with `status: "blocked"` if required tools or the archive are
missing. Exit 2 means a blocked prerequisite, not a failed gameplay assertion.
`gameplay_verified` and `device_verified` remain false in preflight output.

Fetch only when wanted:

```sh
python3 examples/fifteen-pilot/pilot.py fetch --allow-network
python3 examples/fifteen-pilot/pilot.py extract
```

The fetch uses the pinned URL once. It has no retry loop. A hash or size mismatch
blocks extraction and build. Extraction rejects traversal paths, links, duplicate
members, and oversized archives. Reuse requires an unchanged extracted tree.
An existing mismatched archive is not overwritten.
The wrapper makes no other network request. Build tools are not network-sandboxed;
use the host's controls if the test requires a fully offline toolchain.

## Reproduce the build when prerequisites are available

Review the pinned upstream CMake and Perl build code before execution.
[Toolchain setup](toolchain-setup.md) gives the locally tested, pinned SDK steps.
The pilot wrapper does not install tools. Freeze its exact version before comparison.

```sh
nice -n 20 python3 examples/fifteen-pilot/pilot.py build-web
```

This executes the upstream browser recipe with one build job. Commands have a
180-second limit each. Logs are capped at 1 MiB per command. A timeout or incomplete
log prevents success. Existing build output is not overwritten. Choose a fresh
`--work-dir` before the action if a previous attempt left output there.

The successful run used a fresh work directory, `.work/fifteen-sdk6`.
Its `site/` contains `fifteen.html`, `fifteen.js`, `fifteen.wasm`, and `LICENCE`.
A default fresh run would write `.work/fifteen/site/`.
Only the generated page's documentation
and home links are adapted to the author's site. Game code stays unchanged.
The wrapper prints `BUILT` only after outputs exist. This does not close game gates.

Serve the output locally only after the build succeeds:

```sh
python3 -m http.server 8000 --bind 127.0.0.1 --directory .work/fifteen-sdk6/site
```

Stop the foreground server with Ctrl+C. This binds only to the local computer.
A real iPhone needs a separately chosen reachable test setup. Do not count a
desktop emulation of a phone as device acceptance.

## Verify behavior

[Route fixtures](fixtures/routes.json) contain source-derived expectations. They
are not recorded passing results. Follow the [device checklist](device-checklist.md).
Use normal game inputs. Save-state injection cannot prove a route is reachable.
Save and reload tests must retain the complete undo and redo history.

Record each check using the skill's evidence format. Include the source archive,
unmodified extracted-tree check, compiler and runtime identities, flags, settings,
route, test harness, generated files, and exact device. Independent review must
check that the harness detects a wrong board or missing history. A command that
exits zero without useful assertions does not establish fidelity.

```sh
python3 -m unittest discover -s examples/fifteen-pilot -p 'test_*.py' -v
```

This command tests the pilot's input handling, not the game. It covers hash
mismatch, unsafe extraction, changed source, missing tools, offline behavior,
nonzero exit, timeout, and output limits. [Handoff](handoff.md) records the boundary.
