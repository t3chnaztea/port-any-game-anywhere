# Inventory and fidelity

Authentic means that specified player-observable behavior matches the selected
reference under declared conditions and tolerances. It is a set of measurable
claims. It is not a single visual impression or a universal percentage.

## Define the finite known inventory

Use stable path IDs for meaningful sequences and outcomes. Include applicable
game modes, difficulty settings, routes, mechanics, transitions, menus, endings,
save/load, retries, failure states, and required combinations. For a network game,
include connection loss and state synchronization. For a strategy game, include
turn order and campaign branches. For a rhythm game, include timing and latency.

Record where each item came from: source, manual observation, documentation, or
an explicit assumption. Record unknown areas. The inventory cannot enumerate all
possible inputs. Freeze a dated revision for each reported result.

Report coverage as `passed required claims / all known required claims` for that
revision, profile, target, and evidence requirement. Keep untested, blocked, failed,
and skipped claims in the denominator. Report approved exclusions separately.
When new paths are discovered, revise the denominator and retain the old report.
Do not compare percentages across revisions without explaining the changed set.

Implementation counts and evidence-class counts can be useful separately.
Never combine inspected functions, fixtures, emulator routes, and physical-device
tests into an unlabeled total. Avoid a percentage when the set is not defined.

## Set fidelity criteria before changing code

| Dimension | Example measurable criterion |
| --- | --- |
| Behavior | Same state and outcome for a selected input sequence |
| Timing | Same update count for a transition; declared latency tolerance |
| Presentation | Agreed camera, layout, composition, animation, and color differences |
| Audio | Required cues, ordering, duration, channel behavior, and sync tolerance |
| Controls | Action mapping, dead zones, repeat behavior, latency, and disconnect outcome |
| Persistence | Save contents survive restart; corrupt or failed writes preserve valid data |
| Performance | Declared frame-time or turn-time limit under a named worst-case route |

Choose units, conditions, and tolerances from the reference and target. Do not
invent universal thresholds. Average frame rate alone can hide long pauses.
Record update rate separately from display rate. Distinguish a visual difference
caused by scaling from a simulation timing difference.

## Separate enhancements

Give the original behavior a named baseline profile. Give deliberate changes a
different profile and a stated rationale. Record shared-system regression checks.
Do not reclassify a defect as an enhancement after a comparison fails.
If a feature cannot work on the target, record an explicit compatibility decision
and its acceptance authority. Do not claim reference fidelity for that feature.

One completion ledger is authoritative. Coverage reports and handoffs summarize
it and link to it. They must not become competing completion lists.
