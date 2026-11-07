# Complete defect loop

Keep one bug record per distinct failure. Link its affected ledger claims.
Use the bug template to preserve the reproduction and closing evidence.

## Reproduce

Record exact reference and port identities, profile, target, initial state, input
route, expected behavior, actual behavior, and frequency. Preserve a failing save
or recording privately if redistribution is restricted. Reduce the case without
removing the trigger. Label direct state setup separately from normal gameplay.

Confirm whether the issue is a game defect, test defect, tool failure, missing
dependency, or uncertain observation. An infrastructure error is not a passing
game result. If the problem cannot be reproduced, record the uncertainty.

## Diagnose

Ask one specific question. State a hypothesis and the observation that would
reject it. Inspect the reference before inventing a behavioral rule. Trace the
earliest state divergence rather than patching the last visible symptom.
Measure before changing performance-sensitive code.

After two unsuccessful fixes to the same failure, stop changing code. Reduce the
case again. Revisit the reference, test assumptions, and exact tool documentation.
Do not make a third guess under the same diagnosis.

## Fix

Make the minimum change that addresses the diagnosed cause. Add or improve the
smallest meaningful regression check. Preserve original-profile behavior unless
an approved enhancement specifies the difference. Regenerate derived fixtures
through the documented process. Never hand-adjust reference traces to accept a fix.

## Independently verify

Re-run the original reproduction against the changed build. Check it using evidence
separate from the fix's own reasoning: reference execution, an independently
derived fixture, a second observation surface, or a reviewer with actual artifacts.
Confirm that the expected result did not simply copy the port's output.

The verifier records exact inputs and result. Another agent is optional. Human
target-device observations remain necessary when the gate requires them.

## Check regressions and close

Select neighboring routes, failure states, profiles, and targets touched by the
shared system. Run wider gates only where those dependencies justify them.
If any required check fails, the defect stays open. Link the failure to the ledger.

Close only with reproduction evidence, cause, fix identity, independent verification,
and required regression results. If a device check is pending, say so. A useful
partial fix does not close a device-specific failure without device evidence.
