# Switchboard behavior contract

Version 1, frozen for the source-authored example on 2026-11-07. This is a tiny game specification, not evidence that every path has passed.

## Rules and normal input

Six fixed 7 by 5 boards contain walls (`#`), starting floor (`@`), ordinary floor (`.`), a switch (`S`), a door (`D`), and an exit (`E`). The player moves one square per accepted cardinal action. A wall or closed door rejects movement without changing history or move count. Entering the switch reverses door state. Entering the exit completes the board.

The native interface accepts one command per line. The browser converts buttons, adjacent-square clicks, touch buttons, and arrow keys to the same cardinal actions. It never teleports the player. Invalid commands return an error and leave state intact. `state` observes state without changing it.

| Command | Required result |
|---|---|
| `new campaign` | Start board 1, reset campaign progress; retain sound preference. |
| `new practice N` | Start any board 1 through 6 in practice mode. Invalid board numbers preserve state. |
| `up`, `down`, `left`, `right` | Move while playing. Reject a blocked square or a finished board. |
| `undo` | Restore the prior accepted move, door, count and scene. Completion can be undone. Retain the most recent 128 moves. |
| `restart` | Restart the current board with empty history. Retain mode, campaign progress and sound preference. |
| `next` | Advance only after a non-final campaign board. Practice cannot advance. No seventh board exists. |
| `menu` | Return to title and clear undo history. |
| `mute` | Toggle the sound preference. |
| `save PATH`, `load PATH` | Native/Node storage adapter. Save exact state and bounded history. Failed load preserves current state. Failed save preserves the prior file. |

The native scene is title, playing, board complete, or campaign complete. The final campaign exit enters campaign complete. A final practice exit remains board complete. Movement has a one-million-move safety bound per board. The game has no lives, random board generation, online services, or frame-sensitive physics.

## Persistence

`SB1` is a canonical UTF-8 text format. Its header records mode, board, scene, position, door, moves, campaign progress, sound and history length. History stores the last 128 pre-move states. An FNV-1a checksum detects accidental changes. It is not an authentication mechanism.

Both decoders check canonical encoding, board bounds, passable positions, scene relationships, and history counters. Valid checksums do not override invalid state. No state becomes visible until decoding succeeds.

Native/Node saves create an exclusive sibling `.tmp`, flush it, read it back, then rename it over the destination. They remove only a temporary file they created. They refuse a pre-existing temporary file. This is not a claim of verified power-loss durability on every filesystem.

The browser uses explicit local storage. It validates a pending value before replacing the primary value. A storage exception preserves the last primary record. Browser export/import uses the same text format. Browser storage and file storage are distinct platform adapters.

## Presentation and adaptations

The original terminal displays an ASCII board. The browser presents the same grid with labeled symbols. This is a deliberate presentation adaptation, not a pixel-match claim. All visual state also has text labels. The terminal bell and browser oscillator are distinct sound backends. The event identities (`start`, `switch`, `complete`) are comparable. Exact waveform equivalence is not claimed.

The browser adds pointer/touch input and explicit import/export. These adaptations have separate gates. There is no automatic save. Retain the original behavior contract when adding enhancements.

## Finite acceptance denominator

The ledger enumerates required scenario families across the six boards, two modes, transitions, persistence, input adapters, audio and devices. Routes are finite scenario samples. They do not represent every possible action sequence or damaged byte string. Unknowns and untested adapters remain explicit. A command count is not game coverage.
