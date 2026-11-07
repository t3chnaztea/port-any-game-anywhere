# Actual-device checklist

Status: **not run**. Complete this once for desktop Chrome/macOS and once for Safari
on a real iPhone. A responsive screenshot or phone simulator is not an iPhone result.

Record operator, UTC time, physical device, OS/browser versions, input devices,
viewport/pixel ratio, artifact SHA-256 identities, source snapshot, and configuration.
Preserve captures and save files as evidence. Record actual outcomes, not checkmarks
copied from expected outcomes. Use the canonical ledger's claim IDs.

1. Open the exact locally built artifact. Confirm board, tile labels, status, menus,
   normal input, and a resize. Record errors and load timing.
2. Enter the one-move descriptive ID in fixtures/routes.json. On desktop, check
   default and reversed arrows separately. Use a normal pointer/tap for the pointer
   routes. Confirm tile state, counter, completion, and Undo.
3. Check a multi-tile aligned move and no-effect clicks. On iPhone, observe whether
   tapping or page scrolling interferes. Do not infer touch support from desktop.
4. Follow the save-history route. Save while a redo is pending. Close the game,
   reopen, import the save, redo, then undo to the initial board. Compare the entire
   chain, not only the reloaded board.
5. With a valid board active, cancel a load. Then try invalid-save.txt, a truncated
   valid save, and a save for another puzzle. Record error and retained state.
6. Check New, restart then Undo, branching after Undo, endpoint button states,
   the 4×4 preset, valid custom boards, invalid dimensions and invalid game IDs.
7. Check repeated hints, Solve then Undo, menu cancellation, Help/About links, focus
   loss, background/resume, and preferences after reload. Test denied storage in a
   controlled profile. Preserve the default profile and unrelated user data.
8. Measure the agreed reference-derived performance criteria. Record long-session
   behavior and display/animation differences. Resolve audio applicability.

Compare each outcome with a runnable same-snapshot reference or an independently
derived expected result. Verify that the test harness can reject a wrong board and
lost undo history. If the reference, tool, device, or operator is unavailable,
record the gate as blocked. Never create a passed manual record to fill that gap.
