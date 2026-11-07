---
name: port-any-game-anywhere
description: Guide complete, faithful game ports across hardware, operating systems, engines, languages, and controls. Use for port feasibility, source recovery, implementation plans, fidelity audits, stalled demos, regression repair, and release acceptance.
license: MIT
compatibility: Requires an agent with local file and command access. Python 3.11+ runs optional bookkeeping helpers on Linux or macOS. Each port requires its own lawful reference, build tools, assets, and access to the declared target.
---

# Port Any Game Anywhere

Help the developer finish a port and support each completion claim with evidence.
Start this workflow when the developer explicitly invokes or selects the skill.
The name describes the range of projects this method can guide.
It does not promise that every game can run on every target.
Source access, rights, target limits, time, and test access can prevent a port.

## Start here

1. Read the project's agent instructions and documentation index, if present.
2. Inspect repository status and the compact handoff before selecting files.
3. State the current goal, consequential assumptions, and completion gates.
   A gate is an explicit condition that must pass before work advances.
4. Preserve active work. Use an isolated checkout for conflicting implementation.
5. Honor the requested mode. Planning does not authorize edits or publication.
6. Ask only about material decisions that available evidence cannot resolve.

Read [the reference index](references/INDEX.md) before choosing a detailed guide.
Load only the guide needed for the current uncertainty.
Use the project's existing tools before adding a new dependency or abstraction.

## Choose the current phase

| Phase | Required result | Read when needed |
| --- | --- | --- |
| Intake | Feasible scope, constraints, reference, acceptance criteria | [Intake](references/intake-feasibility.md) |
| Recovery | Traceable source or behavior model sufficient for the port | [Source recovery](references/source-recovery.md) |
| Inventory | Known game paths, fidelity rules, separate enhancements | [Inventory](references/inventory-fidelity.md) |
| Build | Small working slice with reproducible inputs | [Verification](references/verification.md) |
| Repair | Reproduced defect, diagnosed cause, independent verification | [Defect loop](references/defect-loop.md) |
| Resume | Validated checkpoint, current identities, next decisive test | [Efficient work](references/efficient-agent-work.md) |
| Release | Tested paths reconciled with the full known inventory | [Verification](references/verification.md) |

Enter at the phase supported by current evidence. Do not repeat completed intake.
Return to an earlier phase when a new fact invalidates its assumptions.

Choose an adapter only for a matching project. All bundled adapters are untested.

| Situation | Adapter |
| --- | --- |
| Recover a Linux x86-64 executable | [Ghidra](adapters/ghidra-linux-x86.md) |
| Move a native game to a browser | [Native to browser](adapters/native-to-browser.md) |
| Build and accept a console port | [Console](adapters/console.md) |

## 1. Establish feasibility and acceptance

Identify the source game, exact reference version, target, available source,
required assets, toolchain, dependencies, controls, and target test access.
Check architecture, memory, storage, graphics, audio, timing, and operating limits.
Record rights and redistribution constraints. Unclear permission stays unresolved.
Do not fetch proprietary game data or bypass access controls.

Create a [port plan](templates/port-plan.md) with the smallest useful first slice.
Its gate must include a meaningful game transition, not only a boot screen.
For a source rewrite, prove access to enough reference behavior before expanding.
For binary-only work, follow source recovery before treating guesses as a design.
If a constraint prevents the requested result, state the constraint with evidence.
Propose a bounded change to scope. Do not silently weaken acceptance.

## 2. Recover the reference when necessary

Preserve the reference and its identity before analysis.
Map entry points, systems, formats, state changes, and external dependencies.
Distinguish observed facts, inferred behavior, and unknown code paths.
Reconstruct readable source where needed. Keep links back to reference locations.
For full recovery, produce buildable behavior-equivalent source. Recovering the
original names and file layout is not required. Do not claim that result before comparison.
Use small comparisons to validate recovery before building large replacements.
A decompiler translates executable instructions into inferred source.
Decompiler output is a hypothesis. Compilation does not establish equivalence.

Record recovery in a [source map](templates/source-map.md).
Use the [Ghidra adapter](adapters/ghidra-linux-x86.md) only for a matching target.
An adapter supplies platform questions. It does not supply a verified port.
Do not install or execute unfamiliar binaries merely because analysis found them.

## 3. Inventory the whole game before reporting coverage

List modes, routes, mechanics, transitions, persistence, failure states, endings,
and required combinations. Include menus, retries, device loss, and corrupted saves.
Use stable claim IDs in one [completion ledger](templates/completion-ledger.json).
Each claim needs a path, profile, target, gate, and required evidence classes.
Keep planned implementation separate from verification status.
Mark unknown, untested, skipped, blocked, failed, and passed work explicitly.

Define each denominator before using a percentage.
Report counts for the frozen known inventory, its date, and its exclusions.
Do not imply that all possible input sequences have been enumerated.
Do not use object counts or source coverage as complete-game coverage.
Use a [coverage report](templates/coverage.md) to explain the ledger's boundaries.

## 4. Define authentic behavior

Treat the original reference as the default specification.
Set measurable criteria before implementation for behavior, timing, presentation,
audio, controls, persistence, and performance where they apply.
Specify units, test conditions, comparison method, and allowed differences.
An exact match is appropriate only where the reference and target permit it.

Track intentional enhancements under a separate named profile.
Record each changed behavior and its rationale before claiming it is deliberate.
Keep original-profile checks active. A better-feeling change can still be a defect.
Test shared systems for both profiles and test profile switches when supported.

## 5. Implement small milestones

Choose one uncertainty or observable behavior per slice.
Write its completion gate before changing code.
Start with the smallest decisive reference comparison or fixture test.
A fixture is a controlled input with an expected result.
Then check its real game route and affected target behavior.
Keep the build recipe reproducible. Record tools, flags, settings, and assets.
Do not replace a failing expected result to accept unexplained new behavior.

## 6. Keep evidence classes distinct

| Class | What it can support |
| --- | --- |
| `source-inspection` | What inspected source or recovered code appears to do |
| `fixture-test` | A result for controlled inputs in the tested component |
| `automated-gameplay` | A recorded input route in the named runtime |
| `emulator` | Behavior in named software that imitates hardware, with its configuration |
| `target-device` | Observed behavior on the declared physical target |
| `review` | A named review of specified evidence and acceptance criteria |

Inspection is not execution. A fixture is not an end-to-end route.
A scripted route is not proof of every route. Emulator output is not console proof.
For desktop or browser ports, record the actual OS, browser, device, and controls.
Use target-device evidence for the declared device gate, even without a console.
Record human-operated tests honestly when automation cannot drive the device.

Use [run manifests](templates/run-manifest.json) for machine-run evidence.
Use [manual records](templates/manual-evidence.json) for observations and review.
Read [record format](references/record-format.md) before using the helper scripts.
A command's successful exit is not a fidelity judgment. Check its actual assertions.
Keep raw logs and detailed captures in artifacts. Link concise results in the ledger.

## 7. Identify every run and invalidate stale results

Record source, reference, fixtures, assets, tools, flags, environment settings,
configuration, output identities, runtime, and test route for each result.
Record an identity as a cryptographic content hash when a file can be hashed.
A hash identifies bytes. It does not show that the bytes are correct.

Use `pending` or `running` before execution. End with a truthful terminal state.
Failed, interrupted, skipped, or blocked runs never become passing evidence.
Reuse a result only when every relevant input and condition still matches.
Never carry an old pass forward as proof for changed code.
When identity cannot be checked, rerun the affected check or mark it unverified.
Do not assume a bookkeeping helper detects every external dependency.

## 8. Repair defects completely

Follow reproduce, diagnose, fix, independently verify, then regress.
Independent verification uses a check or reviewer separate from the fix's reasoning.
It can use a separate reference comparison without requiring another agent.
Record expected and actual behavior in a [bug report](templates/bug.md).
After two failed fixes of the same failure, stop patching and revisit diagnosis.
Reduce the reproduction, inspect the original, and consult primary documentation.
Verify the affected route and shared-system regressions before closing the defect.

## 9. Control agent and host cost

Search before reading. Read bounded sections and investigate one uncertainty.
Run the smallest decisive test first. Expand tests when shared behavior warrants it.
Keep output short. Preserve detail in named local artifacts.
Use deterministic scripts for routing, status, hashes, and transforms.
Delegate only bounded independent work when its benefit exceeds duplicated context.
Use one writer per checkout. Keep shared manifest edits with the integrating agent.
Respect CPU, memory, disk, power, temperature, concurrency, and time limits.
Default to one heavy job. Stop safely if required storage disappears.
Stop owned child processes on interruption. Never kill unrelated work.

## 10. Checkpoint and release

Update the one ledger and a [compact handoff](templates/handoff.md).
Keep the handoff within 45 lines and 3.5 KB. Link detailed evidence instead.
Include current identities, last exact results, failures, unknowns, and next command.
On resume, check the workspace and input identities before accepting prior evidence.
An interrupted result stays interrupted. Run it again under a new identity.

Before release, compare tested claims against every required known game path.
Use the [release audit](templates/release-audit.md) to record that comparison.
Account for every exclusion and every unsupported condition.
Meet fidelity, persistence, performance, and declared target-device gates.
Publish a truthful supported-target statement and known limitations.
Never call an incomplete inventory or missing device test complete.
Publishing, distribution, and destructive actions require the user's authorization.
