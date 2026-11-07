# Fifteen reproduction plan

Status: browser build produced with locally scoped Emscripten 6.0.10. Gameplay,
reference execution, and device acceptance are untested. Reviewed on 2026-11-07.

## Goal and boundary

Build Fifteen's existing upstream browser target from the pinned MIT source.
Use this to test source-based intake, inventory, evidence, and interrupted work.
Do not advertise a new port. Do not treat this as the blinded recovery trial.
Only Fifteen is in scope. The other games in the source bundle are excluded.

The reference is snapshot `20260923.616da16`, identified in source-lock.json.
Original behavior is the only profile. No enhancements or bug fixes are planned.
The intended device gates are desktop Chrome on macOS and Safari on a real iPhone.
Exact OS, browser, device, input, and display settings must be recorded at test time.
Neither target is accepted by this document.

## Source and rights

Upstream supplies C source, an Emscripten browser frontend, a page generator, and
MIT terms. Keep the copyright and permission notice with distributed outputs.
No proprietary assets are required. Keep the large source archive and build output
outside tracked files. The observed source hash is not a publisher signature.

## Dependencies and implementation

The browser recipe needs Python 3.11+, CMake, Make, Perl, `emcc`, and `emcmake`.
`pilot.py` verifies the archive, extracts safely, checks unchanged source, configures
the upstream build, builds target `fifteen`, and generates the upstream page.
It adds local attribution and changes navigation links only. Its CMake cache options
set Firefox 79, Chrome 85, and Safari 15 as compilation minima because Emscripten
6.0.10 rejects upstream's older Firefox/Chrome settings. Game code stays unchanged.
These are compilation settings, not verified browser support. It does not install
tools, discover tests, retry failures, patch game code, or start a server.

Upstream macOS CMake requires Halibut, which is absent. A native reference build
has not been made. Establish a runnable same-snapshot reference or an independent
state-comparison harness before claiming reference execution parity.

## Milestones and gates

| Milestone | Completion gate | Current result |
| --- | --- | --- |
| Pin source | Named archive, size/hash, notice, safe extraction verified | Source tooling checked; no game claim |
| Build browser | Frozen toolchain; generated HTML, JS and WASM identities | Built with 6.0.10; see evidence/build-summary.json |
| Compare state | Controlled boards, input mapping, completion, hint/solve, full history | Untested |
| Follow game routes | Normal inputs cover every required inventory claim | Untested |
| Verify devices | Same artifact on named desktop and actual iPhone | Untested |
| Close pilot | All required known claims have current evidence; independent audit | Open |

## Authenticity criteria

Compare exact board state, gap location, move count, completion state, new/restart,
undo/redo, saves, IDs, and control preferences against the same-snapshot reference.
Use exact equality for deterministic state. Pin seeded generation to this version.
Use descriptive game IDs for portable route setup. The author warns that seeds
can generate different boards between versions.

Compare layout, tile labels, highlighting, animation sequence, menu behavior, and
resize behavior under named display conditions. Define timing and load/frame-time
budgets from a measured reference before performance tests. No budget is invented
here. Audio is not claimed: inspect whether this target has any audio requirement
before recording it inapplicable. Do not silently omit it from the final audit.

## Evidence and recovery

The JSON ledger is authoritative. Its required known claims define the finite
denominator. All stay untested until checked. A source-inspection note cannot
satisfy normal-input or device evidence. Keep failures and unknowns visible.
Record all source/reference/fixture/configuration/tool/environment identities.
Re-run affected checks after changes. A source archive hash alone does not identify
a modified compiler, browser, or generated game artifact.

Use one heavy job. Preserve incomplete logs. Stop owned children on interruption.
After two failed fixes, revisit diagnosis. Resume from handoff.md after checking
storage, workspace, input identities, and the ledger. No old pass covers new code.
