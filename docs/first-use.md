# First use: get a reviewable port plan

The first result should be a plan that tells you what the game must do, what can be checked, and what blocks progress. It should not be a new pile of code before the target and acceptance rules are clear.

This guide assumes you can inspect a project and run its development tools. You do not need Sonic knowledge. You do need lawful access to the reference material and a real target for final acceptance.

## 1. Install the complete skill

From a local checkout or extracted GitHub source archive, copy the entire directory:

```sh
mkdir -p ~/.agents/skills
cp -R skills/port-any-game-anywhere ~/.agents/skills/port-any-game-anywhere
```

For the generated skill ZIP, extract it first. Its top-level folder is already the skill:

```sh
mkdir -p ~/.agents/skills
cp -R port-any-game-anywhere ~/.agents/skills/port-any-game-anywhere
```

Move an existing destination aside first. Copying only `SKILL.md` omits the references, templates, and scripts. Keep the source revision or archive version with the project’s evaluation record.

This is the Codex user-skill location in the [current official documentation](https://developers.openai.com/codex/skills/), researched on 2026-11-07. For a project-only installation, use `.agents/skills/port-any-game-anywhere/`. Restart or refresh the client if its skill list does not show the new package. A client finding the skill is an installation check, not a porting evaluation.

For Claude Code, its documented optional route is a full copy to `~/.claude/skills/port-any-game-anywhere/`, followed by `/port-any-game-anywhere`. This client route is untested here. See [the compatibility matrix](compatibility.md).

## 2. Open a separate working copy of the game

Keep original game data outside public source control. Preserve the current project state. Do not stop someone else’s build, emulator, or port work. Start with one bounded task and one authoritative completion ledger.

Invoke the skill in Codex:

```text
$port-any-game-anywhere

Assess this game for a faithful port to my target.
Use available project evidence before asking questions.
Produce the plan and acceptance criteria first.
Do not install missing tools or change game code yet.
```

Add facts you already know: the game or fixture, source and reference access, target device, supported inputs, desired original or enhanced behavior, time or cost limits, and available build tools. The agent should discover facts from the project before asking you to repeat them.

## 3. Review the intake outputs

A useful intake produces these linked records:

- A feasibility decision with rights and access records, dependencies, target limits, required tools, device availability, and unresolved questions.
- A reference identity and an inventory of modes, routes, mechanics, transitions, saves, failures, and endings.
- A canonical completion ledger with stable required-path IDs and distinct evidence requirements.
- Small milestones with acceptance gates, the next decisive test, and a compact handoff.

The skill’s [templates](../skills/port-any-game-anywhere/templates/) provide starting shapes. They are not passing evidence. Replace example entries with actual project requirements. List missing information explicitly. An unavailable compiler, an unreadable reference, or no access to the target device can block a later gate without blocking all useful planning.

For a source-led port, pin the source revision and dependencies. For recovery from a compiled program, pin the binary and selected analysis tools. Recover one behavior at a time. Preserve uncertainty in the source map. Decompiled code is an interpretation, not the original source. Recovery is accepted when independent evidence supports buildable behavior-equivalent source. Matching original variable names or file structure is not required.

## 4. Define what faithful means for this game

Compare behavior, timing, presentation, audio, controls, persistence, and target performance where relevant. A turn-based puzzle needs a different timing contract from a rhythm game. Set justified tolerances before running a comparison. There is no universal 60 frames-per-second gate.

Keep deliberate enhancements in a separate profile. A profile names one intended behavior set, such as original play or an enhanced input mode. Define how a target’s keyboard, controller, pointer, or touch input preserves the game’s actions. Record differences that the target requires.

Do not call a fixture an earned gameplay route. A fixture starts from a controlled state. A normal-input route must show its trigger, transitions, and outcome. Emulator evidence and actual-device evidence also remain separate.

## 5. Record the smallest decisive check

The helpers are optional deterministic bookkeeping. They do not discover tests, repair a game, judge test quality, schedule work, or run a decompiler. Python 3.11 or newer is required. The recorder currently targets Linux and macOS.

Prepare a manifest from the installed `templates/run-manifest.json`. Give it an explicit command, working directory, timeout, output limit, claim IDs, and every relevant input. Include source, reference, fixture, required assets, configuration, tool identities, flags, and environment settings. Paths resolve relative to the JSON file that contains them. The helper cannot fingerprint a dependency you did not declare.

Run the check with a new evidence path:

```sh
mkdir -p port/evidence
python3 ~/.agents/skills/port-any-game-anywhere/scripts/record_run.py port/run-manifest.json --output port/evidence/run-001.json
```

The recorder preserves a combined log beside the record. It never overwrites an existing record or log. Timeout, interruption, changed inputs, missing outputs, and truncated logs prevent a pass. Exit zero means the declared command completed with unchanged declared inputs. It does not mean the assertions prove a faithful game.

Map the record to its claim in `port/completion-ledger.json`, then check the ledger:

```sh
python3 ~/.agents/skills/port-any-game-anywhere/scripts/check_port.py port/completion-ledger.json
python3 ~/.agents/skills/port-any-game-anywhere/scripts/check_port.py port/completion-ledger.json --require-complete
```

The normal check can succeed with honest gaps. `--require-complete` exits one when required claims remain incomplete. Malformed records exit two. The checker reports finite required-claim counts. It does not report a global percentage of the game.

See [the record contract](../skills/port-any-game-anywhere/references/record-format.md) for exact fields, evidence classes, exit behavior, and freshness checks.

## 6. Fix a defect without changing the claim

Reproduce it with retained input. Reduce it to a specific uncertainty. Check the reference, harness, and observation timing before changing game behavior. Fix the cause, verify independently, then run the affected regression checks. A regression is a previously working behavior that a change breaks.

After two failed fixes to the same failure, stop patching and revisit the diagnosis. Do not weaken an assertion just to accept new output. Do not repeat a passing full suite without a relevant reason.

## 7. Resume safely or close the milestone

Preserve interrupted records. A still-pending or running record is not a pass. Recheck storage, current input identities, saved artifacts, and owned-process cleanup before continuing. The helpers do not automatically reuse results or stop unrelated host jobs.

Keep the handoff within 45 lines and 3.5 KB. Link the canonical ledger. Include exact last results, current failures, required devices, and the next command. Preserve unknown exit states as unknown. Never infer old inputs from a new hash, commit, or file date.

A milestone closes when its required current evidence passes and independent review supports the claims. A release also requires the final comparison against all required known paths and actual target acceptance. The example gates require desktop Chrome on macOS plus an actual iPhone running Safari. Those are evaluation targets, not a claim of broad browser support.

Do not publish a release, upload assets, or write to someone’s device merely because the local ledger is complete. Those actions require their own authorization.
