# Approved implementation contract

Approved in chat on 2026-11-07. This file records decisions, not test results.

## Product

Port Any Game Anywhere is an agent-agnostic skill for finishing faithful ports and supporting completion claims with evidence. User steering on 2026-11-07 supersedes the earlier Claude-first choice: use the open Agent Skills format, validate Codex first, and keep client installation/invocation outside the universal workflow. Support both source-based ports and full source recovery from compiled programs. Do not promise automatic conversion of every game. Some assessments stop at a documented feasibility limit.

The first public release is v0.1.0 beta. Publication is not authorized by the implementation task. Keep the local development state separate from released or device-accepted status.

## Method

1. Assess source, reference, permission/license records, dependencies, assets, target resources, available tools and devices.
2. Pin original behavior. Inventory every supported mode, route, transition, save, control, ending and failure state. Give each required scenario a stable ID. Define a finite denominator before percentages.
3. Recover missing source one behavior at a time. Preserve binary identity, addresses, types, data layouts, uncertainty and comparison evidence. Decompiled code is an interpretation. Buildable behavior-equivalent source is the goal; original names and file structure are not required.
4. Use small milestones with explicit gates. Track original behavior and deliberate enhancements separately.
5. Record source, reference, fixture, asset, tool, flags, environment, command, configuration and artifact identities. Reuse only with complete matching identities. Never reuse an old pass for changed code.
6. Separate source inspection, controlled fixtures, normal-input gameplay, emulator evidence, real-device evidence and human review.
7. Reproduce, reduce, diagnose, fix, independently verify, then check regressions. Revisit the diagnosis after two unsuccessful fixes.
8. Preserve interrupted reports. Resume from one authoritative ledger and a compact handoff. Recheck inputs, outputs and storage before reuse.
9. Compare all required known paths with current evidence before release. Unknown or untested behavior remains visible.

Authenticity includes behavior, timing, presentation, audio, controls, persistence and target performance. Exact comparison is preferred for deterministic behavior. Justify tolerances before testing. There is no universal 60 fps requirement.

## Agent efficiency

Investigate one uncertainty. Search before bounded reads. Run the smallest decisive check. Keep output short and detailed evidence in artifacts. One ledger, one handoff (45 lines/3.5 KB maximum). Use deterministic bookkeeping. Delegate only bounded independent tasks. Default to one heavy job. Set host-specific bounds before long work. Stop safely on storage loss. Measure cost rather than claiming token savings.

## Skill and helpers

Use standard Agent Skills frontmatter only. Omit client-specific invocation fields and permission-expanding tool lists. Optional Codex UI metadata may request explicit invocation. Document client-specific setup separately. Keep SKILL.md near 200 lines. Load references and adapters only when needed. Do not imply that one client's installation or evaluation verifies other clients.

Bundle intake, recovery, fidelity/inventory, verification/defects, evidence/resume, and efficiency guidance. Provide Ghidra Linux x86-64, native-to-browser and console-acceptance adapters. REA is optional guidance, not a required service or tested integration.

Provide templates for a port plan, canonical JSON ledger, run record, bug, handoff and release audit. Detailed record contracts live inside the skill.

Only two Python helpers: record an explicit command with input identities and terminal outcome; validate records and summarize inventory-to-evidence joins. No scheduler, test discovery, generalized cache, plugin system, daemon or background hook. Python standard library only.

## Pilots

The main process case is Sonic CD Saturn/CD++. Use only the reviewed 2026-11-07 snapshot. Older reported passes are not current acceptance. Last recorded user-confirmed console build is V0.065 (2026-09-26). Current whole-game coverage and newer hardware acceptance are open. No proprietary assets or local artifact paths in public deliverables.

Controlled recovery: an original six-board puzzle design with campaign/practice, switches, doors, undo, restart, completion, generated effects, saves and invalid-save handling. Current Switchboard source is public regression material. Following the user's authorization to publish the development repository, any future blind trial must use a fresh unpublished variant or fixture. An independent evaluator holds its source and hidden tests. An unexposed agent receives a stripped Clang/Linux x86-64 binary and recovers buildable C, then ports to TypeScript/browser keyboard, pointer and touch. Require enforced access boundaries, independent comparisons, desktop Chrome/macOS and actual iPhone/Safari checks. Freeze blind results before disclosing the new fixture. A source-authored port is not a recovery trial.

External source pilot: pinned Simon Tatham Fifteen only, MIT. Reproduce its existing browser target. Inventory actual controls, configuration, save and complete undo history before tests. Disclose that upstream already has a web port. This pilot supports source workflow/onboarding, not novel recovery.

## Validation and release

Static checks and meaningful helper tests run locally and in CI. Live agent evaluations are separate. Cover normal intake, source recovery, absent tools/device, missing path despite boot, misleading save tests, ineffective harness, interrupted run with changed inputs, missing assets/crashed evaluator. Compare bounded tasks with matched baselines twice each. Record model, tools, permissions, initial state, costs, variation and invalid comparisons. No crash/skip/blocked state is a pass.

Release gates: both pilots satisfy frozen inventories; recovered C builds without original source; browser comparisons and required devices pass; all seeded critical defects detected or block acceptance; no false completion; stale identity invalidation works; fresh installation resolves links; at least 4/5 fresh testers produce a useful plan within 20 minutes after prerequisites; independent public-claim audit; license, asset, secret and archive checks pass.

## Public product

README: promise/pain, short captioned demo, first result, installation/invocation, workflows, evidence, examples/case, compatibility, participation/licenses/research. Accessible diagrams need a text equivalent. No color-only status.

MIT original code/docs. CC0 newly authored assets. Preserve third-party notices. Proprietary game data remains external. Deliver CONTRIBUTING, SECURITY, THIRD-PARTY, CHANGELOG, issue templates, compatibility, research and launch history.

Research reviewed REA, pokeemerald, OpenRCT2, DevilutionX, anthropics/skills, superpowers and uv. Separate observed source facts, audience inference and proposed practices. Stars and post counts measure attention, not quality or causes.

Launch after gates: tagged beta plus technical defect case study; direct practitioner reproduction/review; one runnable Show HN; community posts only after current rule checks. No upvote requests. Use external verified milestones for follow-up stories. No publishing or outreach during implementation.

## Sequence

Contract -> skill/templates -> source pilot and recovery pilot -> helpers informed by observed outputs -> evaluation/polish -> authorized release. Missing prerequisites must leave honest open gates. Do not fabricate a pass to fit the schedule.
