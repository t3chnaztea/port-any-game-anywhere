# Skill evaluation pack

This pack tests decisions and evidence handling. It is separate from helper unit tests, the complete Switchboard recovery trial, the Fifteen reproduction, and physical-device acceptance.

**Current state: unrun.** `results.json` contains no live agent results. An empty suite has 32 pending slots. Passing the validator's unit tests does not validate the skill.

## What is evaluated

The frozen denominator is eight cases, two conditions, and two repetitions: **32 required runs**. Each condition has 16 runs. The skill condition loads the versioned skill. The baseline performs the same task without the skill. Both receive the same case files, output contract, tools, model settings, permissions, initial state, and resource limits.

| Case | Task presented to the agent |
| --- | --- |
| normal-intake | Assess an original puzzle for a browser port |
| source-recovery | Plan a recovery milestone from limited compiled-program material |
| absent-tools-device | Assess gates with missing tools and no target console |
| boot-missing-path | Review a passing startup check against the game requirements |
| misleading-save-test | Assess what a green save test establishes |
| ineffective-harness | Assess whether requested input was actually exercised |
| stale-interruption | Assess recovery after interrupted work and changed inputs |
| missing-assets-crash | Assess a zero-return wrapper with conflicting underlying records |

The public pack is a regression suite, not a claim that future models have never seen its cases. Use fresh undisclosed material for the separate recovery trial. The fixtures are original, synthetic material. Their reports are facts within the case. They are not real game acceptance evidence. The recovery case tests assessment of a function specimen. It does not prove complete binary recovery. The separate Switchboard trial must do that work.

## Isolate the agent envelope

Give the evaluated agent only the files listed for one case in `catalog.json`, plus a copy of `agent-contract.md`. Keep their case-relative paths. Do not copy interpreter caches or unlisted files. Create a fresh writable workspace for each condition and repetition. Preserve the original case directory for fingerprinting. The agent writes its assessment and handoff in its copy.

Keep `evaluator/`, the catalog, result records, validator source, tests, the full skill repository, and earlier transcripts outside the agent's readable environment. In the skill condition, expose only the versioned skill package as an additional read-only input inside the isolated envelope. Do not expose this evaluation directory through a parent checkout or inherited conversation.

Directory names and documentation are **not** an access-control boundary. Use a clean client session plus actual filesystem isolation or a separately provisioned environment. Disable network access and installation. If the client cannot enforce the recorded boundary, mark the run invalid. Do not score a contaminated run.

## Freeze the protocol

Start with the same Codex model and settings for both conditions. Record the exact client version, model identifier, reasoning or sampling settings, tool versions, permissions, wall limit, memory limit, worker count, clean initial-state policy, and tested skill revision. Use one worker. No global skill installation may leak into the baseline.

`result-format.json` describes the machine-readable record. `evaluator/protocol.md` describes the operator procedure. Before starting, capture current identities:

```sh
python3 evaluations/check_results.py --fingerprints
```

The suite identity includes catalog, case envelopes, shared task contract, expected checks, and validator source. A change invalidates earlier comparisons. Copy each printed case identity into its run record. Do not infer an old fingerprint after a run.

Counterbalance order: repetition 1 runs baseline then skill; repetition 2 runs skill then baseline. Start every run fresh. Record order in the retained transcript or operator log. Do not give the second run feedback from the first.

## Record outcomes honestly

The runner's execution state is `completed`, `blocked`, `crashed`, `interrupted`, `invalid`, or `skipped`. Only a completed run can receive a behavioral pass. A good agent may correctly report that the *game task* is blocked; that can be a completed, successful assessment. An agent client that crashes before producing its assessment is a crashed evaluation.

Retain the actual client exit code, transcript, assessment, handoff, timestamps, and measured time. A nonzero or unknown client exit cannot complete a run. Record input tokens, output tokens, and cost when the client exposes them. Use null with an explanation when a metric is unavailable. Do not convert unavailable cost into zero.

An independent reviewer checks grounding, fabricated execution claims, the usefulness of the next action, and possible access to withheld material. The reviewer records each verdict with an evidence location. The validator also checks structured game-path, implementation, verification, input-effect, reuse, and underlying-run states. It does not grade wording.

## Check the recorded results

```sh
python3 evaluations/check_results.py evaluations/results.json
python3 evaluations/check_results.py evaluations/results.json --details
python3 evaluations/check_results.py evaluations/results.json --require-complete
python3 -m unittest discover -s evaluations/tests -v
```

The normal command validates records and reports pending work. `--require-complete` exits one until all 32 slots contain valid completed evaluations and all 16 skill-condition runs pass. Baseline behavior failures remain visible and do not prevent a completed comparison. Invalid records exit two. No supplied or missing run is silently removed from the denominator.

Blocked, crashed, interrupted, skipped, and invalid evaluations never pass. Changed fixtures, evaluator checks, protocol, artifacts, or transcripts invalidate the affected recorded comparison. An older passing summary cannot repair missing current evidence.

## Interpreting the result

Report behavior outcomes for both conditions, each case, and each repetition. Inspect variation rather than averaging away a failed critical case. Compare cost or speed only for matched tasks with comparable outcomes. Two repetitions are a minimum diagnostic sample, not a population-wide efficiency estimate.

A complete pack still does not establish successful recovery of a full game, browser parity, actual iPhone behavior, or a useful first run by five fresh users. Those remain separate release gates. The validator checks recorded structure and file identities. It cannot authenticate a human, a model session, tool isolation, or the truth of a transcript.
