# Fifteen inventory

Inventory revision: 1, 2026-11-07. This is a finite source/manual-derived set.
It is not an enumeration of every possible board or input sequence.
The canonical claim IDs and denominator are in completion-ledger.json.

The source snapshot and manuals establish candidate behavior. No entry here means
that the reproduced browser game was run. All game claims are untested.

| Area | Required scenarios |
| --- | --- |
| Boot | Load the exact local artifact; board, status and menus become usable |
| Pointer | Adjacent tile; a whole aligned line; gap click; off-row and outside clicks |
| Keyboard on desktop | Default tile motion; inverted gap motion; boundary keys; shortcut preferences |
| Touch on iPhone | Normal tap produces the intended pointer move without unwanted page motion |
| Completion | One-move finish, move count, completion display; continued action and undo |
| New/restart | New board; restart returns to initial state; restart itself can be undone |
| Undo/redo | Complete move history; disabled endpoints; alternate move after undo removes old redo branch |
| Save/load | Save with pending redo, terminate/reload, full undo/redo chain, board and counters retained |
| Invalid save | Non-save text, truncated valid save, wrong-game save, denied/cancelled load; prior valid state preserved where reference requires |
| Board setup | 4×4 preset; valid 2×3 and 3×4 custom boards; invalid width/height and oversized product |
| Game IDs | Same-version seed replay; descriptive ID replay; malformed, duplicate and out-of-range tiles |
| Help/solve | `h` produces the reference suggestion; repeated hints finish; Solve followed by Undo restores prior state |
| Preferences | Tile/gap arrow sense; one-key shortcut setting; reload and storage-denial behavior |
| Menus | Game, Type, Preferences, IDs, load/save, undo/redo, solve, About/help; cancel does not mutate state |
| Presentation | Labels, layout, colors, status, animation sequence, resize and pixel ratio |
| Interruption | Focus loss, background/resume, reload with and without an exported save |
| Performance | Measured reference-derived frame/load/long-session criteria on each device |

## Boundaries

Desktop tests use mouse and keyboard. iPhone tests use actual touch and Safari.
An external iPhone keyboard is not part of revision 1. No audio, printing, native
installer, other puzzle, or enhanced profile is accepted by this inventory.
Audio applicability and performance limits remain explicit unknowns until checked.
The absence of those claims from the current set does not establish completeness.

Do not assume auto-save. The reviewed browser code exposes save-file export/import.
Preference storage is a separate path. Confirm actual storage behavior at runtime.
The common manual states that save files retain the entire undo/redo history.
Checking only the visible board after reload is insufficient.

## Evidence interpretation

Report satisfied required claims over all known required claims separately by
target. Untested, failed, interrupted, skipped and blocked claims stay in the set.
Do not add overlapping evidence-class counts. If a newly discovered path matters,
add a claim, increment this revision, and explain the changed denominator.
