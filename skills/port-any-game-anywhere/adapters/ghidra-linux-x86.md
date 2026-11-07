# Ghidra: Linux x86-64 reference

**Status: untested adapter.** This is guidance, not evidence of a recovered game.
Use only when the reference executable is a Linux x86-64 program and Ghidra is an
appropriate, available analysis tool. Ghidra is a program-analysis suite that can
show disassembly and inferred source. It does not produce verified original source.

## Establish the analysis environment

Identify ELF format, 64-bit architecture, byte order, linking, libraries,
symbols, compiler clues, and required assets. Hash every reference input. Record
Ghidra version, processor/language selection, loader, analysis options, and scripts.
Keep analysis databases and proprietary inputs outside the public repository.
Inspect statically before considering execution in an isolated runtime.

## Recover a useful slice

Map startup, input, simulation update, drawing, audio, file access, and shutdown.
Record unknowns instead of naming an inferred function as certain. Trace a small
behavior through its callers and data. Check inferred types against instructions.
Pay attention to x86 integer widths, signed comparisons, overflow, floating-point
precision, calling conventions, structure layout, and update order.

Recover readable source with references back to addresses or symbols. Separate
platform calls from game logic only where the reference supports that boundary.
Build a controlled comparison with known inputs and expected state. Then exercise
the same behavior through normal game controls. Expand after this comparison works.

## Acceptance reminders

Successful analysis is not a rebuilt game. A rebuilt game is not a faithful port.
Check every recovered claim using the universal inventory and evidence classes.
Mark unresolved paths and dependencies. Never describe a fixture pass as physical
target acceptance. Do not install Ghidra or run discovered binaries automatically.

Primary tool documentation: [Ghidra documentation](https://ghidra-sre.org/).
Check the documentation matching the installed release before unfamiliar operations.
