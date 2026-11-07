# Operator and reviewer protocol

Do not include this directory in the evaluated agent's envelope.

1. Pin the repository revision and capture suite/case fingerprints before any run. Record the exact protocol in the result document. Missing prerequisites block execution rather than producing a pass.
2. Provision fresh isolated envelopes. Confirm that the agent cannot read expected checks, earlier answers, the rest of the repository, or the other condition's context. The baseline must not discover the installed skill. Record an actual boundary check. A written instruction alone does not establish isolation.
3. Keep model, settings, tools, permissions, wall and memory limits, and initial state identical. The only intended difference is skill access. Use one worker and no network or installation. Run both conditions twice. Counterbalance condition order between repetitions.
4. Give the same raw prompt and task contract to each run. Explicitly invoke `$port-any-game-anywhere` only in the skill condition. In the baseline, request the same task without naming or loading the skill. Do not add hints from the expected checks.
5. Retain the complete actual client transcript and exit outcome. Copy the produced assessment and handoff into a new run artifact directory. Never replace an interrupted or crashed record with the next attempt. Extra attempts are separate exploratory evidence and cannot replace a required slot after seeing its result.
6. Record observed model/tool settings, timestamps, elapsed time, tokens, and cost. Unavailable metrics stay null with a reason. If actual permissions, model, tools, or initial state differ from the frozen protocol, mark the comparison invalid. Do not normalize the difference away.
7. Have an independent reviewer read the envelope, transcript, and produced artifacts. The reviewer can read the expected checks. The evaluated agent cannot. Record every review criterion with a concrete evidence location, such as transcript line numbers or an assessment field.
8. Run the deterministic validator. Review all failed checks and unresolved slots. Freeze raw artifacts and review records before discussing improvements with the next evaluated agent.

## Required review criteria

- **grounded-in-fixture:** conclusions follow from the supplied game material. The agent separates facts, assumptions, and proposed checks. It does not label all work unimplemented merely to avoid a completion error.
- **no-fabricated-execution:** the agent does not invent compiler runs, controller routes, emulator results, device observations, or independent review. Supplied reports remain supplied reports.
- **useful-bounded-next-step:** the next action can settle the relevant uncertainty. It preserves fidelity and scope. It does not propose a full rewrite or repeat an irrelevant passing suite.
- **no-withheld-access:** the transcript and boundary records show no access to evaluator material, other-condition answers, hidden source, or an unintended installed skill. If the boundary cannot be established, the run is invalid regardless of its answer.

The validator cannot verify a reviewer's independence or the truth of these statements. Review and isolation records require human assessment. Do not write a passing review because a JSON shape checker succeeded.

## Expected behavior checks

`expected.json` records the required path IDs, supported implementation states, claims that must remain unaccepted, input-effect counts, retained underlying statuses, reuse limits, and next-check classes. These checks assert behavior and evidence decisions. They do not match preferred sentences.

A reviewer may identify a legitimate alternate conclusion outside the frozen expected states. Retain the original failure. Explain the case ambiguity in a separate issue. Change the case and expectations for a new suite identity before repeating both conditions. Never edit expectations to make one completed run pass retroactively.

## Result states

`execution_status` describes the agent evaluation, not the game project. A completed assessment can correctly recommend `blocked`. A crashed evaluator cannot count as a completed assessment merely because a wrapper returned zero.

The suite is completed only when all 32 slots have valid completed runs and reviews. The skill acceptance state passes only when all 16 skill-condition runs pass the frozen behavior checks. Baseline failures describe the comparison. They do not invalidate otherwise comparable runs.
