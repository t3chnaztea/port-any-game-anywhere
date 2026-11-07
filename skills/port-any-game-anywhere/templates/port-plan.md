# Port plan

Status: intake. This document is a template, not accepted port evidence.
Replace the example claims with the project's inspected inventory.

## Goal and reference

Record the game, exact edition/revision/region, reference file identities, source
availability, asset availability, and permitted use. Name unresolved rights or
access questions. Identify what the developer can inspect, run, and distribute.

## Target and constraints

Name the physical target, OS/firmware/runtime, build tools, dependencies, controls,
memory/storage budget, timing constraints, and available test operator. Record a
measured feasibility result or the smallest experiment needed to decide it.

## Scope and authentic behavior

Name original behavior as the baseline profile. Describe deliberate enhancements
under a separate profile. Link the dated inventory and authoritative ledger.
State unknown paths and approved exclusions. Do not omit failure states.

| Dimension | Reference and method | Acceptance criterion |
| --- | --- | --- |
| Behavior | Same initial state and recorded inputs | Define compared state and outcome |
| Timing | Reference updates and declared clock | Define units and justified tolerance |
| Presentation | Named capture conditions | Define allowed composition/scaling differences |
| Audio | Required cue sequence and capture | Define ordering and sync tolerance |
| Controls | Declared device mappings | Define repeat, latency, and disconnect behavior |
| Persistence | Save, terminate, restart, reload | Define retained state and failure recovery |
| Performance | Named hard route on target | Define frame/turn/load budget before testing |

Mark inapplicable dimensions with a reason. Do not invent a universal threshold.

## First milestone

Choose the highest-risk useful transition. State input conditions, the observable
result, evidence classes, regressions, and who accepts the gate. Example shape:
save after a meaningful state change, restart the process, reload, continue play,
then verify that invalid data preserves the last valid state.

## Build and evidence

Record commands, source/reference/assets/configuration, tools and flags, selected
environment settings, artifact destinations, and exact input route identities.
Keep proprietary inputs and unrestricted logs outside the public repository.

## Working limits and checkpoints

Default to one heavy job. Set time/output/concurrency/resource limits. Name the
ledger, handoff, next decisive command, and recovery behavior if storage disappears.

## Release decision

Require every known required claim for each supported profile/target. Require
independent verification and declared device gates. Name any missing prerequisites.
A blocked device or unresolved inventory keeps release acceptance open.
