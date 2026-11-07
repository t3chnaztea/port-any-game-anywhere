# Reviewed sources

Access date: **2026-11-07**. Live manuals are undated. The pinned archive is
snapshot **20260923.616da16**, with publisher Last-Modified **2026-09-23 05:00:02 UTC**.
The archive's byte identity is recorded in source-lock.json.

## Observations

- The [author's site](https://www.chiark.greenend.org.uk/~sgtatham/puzzles/) describes
  the portable collection and its existing JavaScript/WebAssembly versions. It
  identifies the collection as MIT licensed. The named pinned source URL returned
  the recorded archive. The latest-source alias redirected to that named URL.
- The [Fifteen manual](https://www.chiark.greenend.org.uk/~sgtatham/puzzles/doc/fifteen.html)
  specifies mouse line moves, default tile-direction arrow keys, reversed gap
  preference, `h` suggestions, and configurable width/height.
- The [common manual](https://www.chiark.greenend.org.uk/~sgtatham/puzzles/doc/common.html)
  states that save/load preserves the full history. Restart and Solve add undoable
  actions. Seeds are version-sensitive. Descriptive IDs encode an explicit board.
- In pinned `fifteen.c`, lines 73–80 define the 4×4 preset; lines 147–154 reject
  dimensions below two and an overflowing area. Lines 296–345 validate tile data.
  Lines 756–857 interpret controls and perform moves. The move count increments
  per tile moved, including multi-tile pointer moves.
- Pinned `fifteen.c` lines 459–510 define the arrow-semantics preference. Lines
  1181–1271 supply a standalone solver. It is not a complete frontend test.
- Pinned `emcc.c` lines 734–825 dispatch menu commands. Lines 827–950 expose game
  serialization and preferences. `emccpre.js` lines 457–503 wire save/load UI.
- Pinned `cmake/platforms/emscripten.cmake` selects a `.js` output and WebAssembly
  build. Pinned `html/jspage.pl` generates the surrounding page from a footer and
  the game's HTML instruction fragment. Upstream's macOS CMake requires Halibut.

These are source observations. They are not runtime verification. The source was
not modified. The MIT notice copied here is the pinned archive's `LICENCE` bytes.

## Inferences and unresolved questions

The route fixtures derive expected boards from the inspected move rules. They have
not been compared against a running reference or browser build. Browser-specific
preferences, failed storage, mobile taps, timing, menu focus, and failure recovery
need execution evidence. Source comments about possible touch enhancements do not
establish current touch support. Actual iPhone behavior remains unknown.

This pilot can test the skill's source-based workflow once its gates pass. It
cannot establish that the skill recovers missing source or creates a novel port.

## Build diagnosis and result

The first Emscripten 6.0.10 link rejected `MIN_FIREFOX_VERSION=68`. The installed
official toolchain's [feature matrix](https://github.com/emscripten-core/emscripten/blob/d6c521a7f05449857c76bd99e396895583cf2083/tools/feature_matrix.py)
sets minimum Firefox 79, Chrome 85, and Safari 150000. Its
[linker validation](https://github.com/emscripten-core/emscripten/blob/d6c521a7f05449857c76bd99e396895583cf2083/tools/link.py)
rejects lower nonzero values. Upstream exposes these as CMake cache options.
Using those options allowed the browser build to complete without modifying game
source. This is observed build evidence only. Browser compatibility and behavior
remain untested. The first failed log and successful output identities are recorded
in evidence/build-summary.json. No byte-for-byte rebuild comparison was performed.
