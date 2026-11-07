# Defect record

ID: assign a stable bug ID. Link affected claim IDs in the one completion ledger.
Status: open until all closing checks have current evidence.

## Reproduction

Record source/build/reference identities, profile, target/runtime/device, initial
state, exact normal-input sequence, expected result, actual result, and frequency.
Link the failing artifact. Label direct state injection separately from gameplay.
State whether this is a game defect, harness defect, infrastructure failure, or
an unresolved observation. Explain how the smallest case retains the trigger.

## Diagnosis

State one hypothesis and the observation that would reject it. Link the earliest
reference/port state divergence. Record the root cause once evidence establishes
it. Keep assumptions separate from facts.

| Attempt | Hypothesis and decisive check | Result and evidence |
| --- | --- | --- |
| 1 | Record before changing code | Link actual result |
| 2 | Record only if needed | After a second unsuccessful fix, revisit diagnosis |

## Fix and independent verification

Name the minimum fix and exact changed-build identity. Preserve the original
reproduction. Record an independent expected result, comparison, or reviewer.
State what the check actually proves. Do not treat the fix explanation as evidence.

## Regression and closure

List affected neighboring routes, profiles, persistence, performance, and target
gates. Link current results. Keep failed, interrupted, blocked, and untested checks
visible. Close only when the reproduction, independent check, and required
regressions pass. State any pending device gate explicitly.
