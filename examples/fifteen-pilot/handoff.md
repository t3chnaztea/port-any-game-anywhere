# Fifteen pilot handoff

Date: 2026-11-07.
Phase: browser build produced; runtime comparison and device gates open.
Reference: snapshot 20260923.616da16 in source-lock.json.
Ledger: completion-ledger.json is authoritative; game claims are untested.

## Evidence boundary

Named archive fetched, hash/size checked, source inspected, MIT notice preserved.
Pilot safety tests cover offline behavior, hash mismatch, unsafe extraction,
changed source, missing tools, nonzero exit, timeout, and output limits.
These are tooling checks. They do not prove game behavior or device acceptance.
Browser files: `.work/fifteen-sdk6/site/`; identities: evidence/build-summary.json.
SDK 6.0.10 is local to ignored `.work/emsdk`; no global startup edits.

## Open gates

Halibut absent for upstream macOS CMake.
No native reference execution, game route, browser runtime, or iPhone observation.
Performance criteria and audio applicability need reference evidence.
No VM or background server started.

## Resume

Check storage, repository changes, source identities, tools, and ledger first.
Next command: `python3 examples/fifteen-pilot/pilot.py preflight`.
Use toolchain-setup.md for the scoped SDK environment. Preserve the first failed
link log in `.work/fifteen/build-web/compile.log`; its browser minima are obsolete.
The successful recipe overrides those minima through upstream CMake options.
Preserve failed logs. An interrupted build remains incomplete.
