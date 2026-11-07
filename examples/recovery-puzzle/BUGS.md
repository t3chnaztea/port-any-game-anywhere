# Defect loop evidence

These defects were found during implementation on 2026-11-07. They are not a blinded recovery result.

## SB-001: checksummed impossible final state

An independent agent review constructed an `SB1` save with campaign board 6 at its exit, but the ordinary board-complete scene. Both source-authored implementations accepted it. Advancing could address board 7 or crash. Agreement between two implementations therefore missed a shared defect.

The implementing session reproduced the accepted bad load before changing code. Both decoders now reject the scene inconsistency. Advancement also has its own final-board bound. Regression fixtures recompute a valid checksum around several invalid states. An independent rerun confirmed rejection and state preservation in both programs.

## SB-002: inherited command property

Independent review found that `toString` and `constructor` accessed inherited entries in a JavaScript direction object. Destructuring the function value crashed the TypeScript adapter. The C program returned `unknown_action`.

The direction lookup now requires an own property. Cross-language invalid-command fixtures include both strings. Independent reruns confirmed identical `unknown_action` results and zero process exits.

## Limits

The reviewer ran bounded code reproductions. No physical iPhone test, audible comparison, Ghidra session, Linux recovery, or independent whole-game acceptance was performed. The browser harness also had an `evaluate` callback error during development. That harness failure was corrected; it did not justify changing gameplay.
