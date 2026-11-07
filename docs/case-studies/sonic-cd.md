# Sonic CD Saturn / CD++: separating implementation from acceptance

The Sonic CD Saturn project is the main source of practices used in this skill. It targets a complete fan-made Saturn port with a faithful Classic setting and a separate CD++-style setting.

**Evidence snapshot: 2026-11-07.** This case study comes from a read-only review of internal project documentation and selected source. No game tests were run for this review. No console session was performed. The full port was still unfinished and unaccepted in the reviewed records.

The references below use portable repository-relative filenames and line numbers. They identify the reviewed material, not publicly available evidence. A redacted public evidence export is pending. Private filesystem paths, copyrighted assets, and built game images are omitted.

## What was implemented, reported, and still open

| Area | Reviewed evidence | Claim supported by this review |
| --- | --- | --- |
| Intended scope | `PORT-ROADMAP.md:3-6` | Seven zones, full game flow, and Classic/CD++ settings are the goal. The first zone is a milestone, not the entire project. |
| Implemented features | `PORT-ROADMAP.md:15-23` | The ledger records zone routes, bosses, special stages, menus, saves, endings, and the optional preset as implemented. Source inspection did not independently execute these features. |
| Historical automated results | `PORT-ROADMAP.md:10`, `PORT-ROADMAP.md:23` | The 2026-10-28 entry reports 202/202 full checks, 347/347 matrix cases, and 21 CD++ cases for an identified earlier build. These are historical records. They do not prove the current tree passes. |
| Current validation | `NEXT-SESSION.md:3-36` | Fast QA was active. Full QA and six target batches remained open. The finite game-path inventory was incomplete. No final game-coverage percentage was assigned. |
| Console acceptance | `HARDWARE-ACCEPTANCE.md:20-26` | The last recorded user-confirmed console build was V0.065, dated 2026-09-26. Later emulator passes did not close hardware gates. |
| Current save implementation | `src/time_attack.c:150-168` | Source writes the alternate record, checks its readback, then removes the older record. A full-storage write error leaves the last verified record intact. This is a source observation, not a console result. |
| Reported save checks | `SAVE-SUPPORT.md:81-90` | The document reports 29 emulator cases, including corruption, full storage, retry, cold starts, and unchanged unrelated files. Current acceptance still requires matching current inputs. |
| Performance method | `PERFORMANCE.md:12-23`, `PERFORMANCE.md:46-52` | Comparisons use identical controller paths. Profiling builds are separate from acceptance builds. Emulator timing does not establish console cadence. |

QA means quality assurance: the work used to find defects and check the result. A matrix groups named test cases across selected configurations. Neither the number of QA commands nor the number of matrix rows is a percentage of the game tested.

## Practice 1: use an implementation and evidence ledger

The roadmap keeps separate columns for implemented work, verified work, outstanding work, and evidence. A finished actor or a selectable stage can therefore remain unaccepted until its routes, transitions, failures, presentation, and target-device behavior are checked.

The reusable rule is simple: completion belongs to a requirement and its current evidence. It does not belong to a file import, a test name, or a large passing count.

Internal source review: `PORT-ROADMAP.md:12-26`; `docs/QA-CAMPAIGN-PLAN.md:124-138`.

## Practice 2: distinguish a fixture from earned gameplay

A fixture is a controlled starting state used to test one behavior. It can expose an object, a damaged save, or a transition without playing the route that normally reaches it. That is useful evidence about the selected behavior. It is not proof that the complete route works.

The project separates host fixtures, normal controller input in the emulator, and user-confirmed console results. A source comparison also remains separate. Two programs can agree because they share the same mistaken reference.

Internal source review: `QA-PLAN.md:31-32`; `docs/QA-CAMPAIGN-PLAN.md:134-138`.

## Practice 3: test the test apparatus

A first exploration batch reported 126 runs with no detected failures. Only 105 runs reached the changed inputs. A later batch checked that all 210 runs exercised changed input. The larger count was useful only after the harness’s effect was checked.

Another mismatch came from a wrapper that omitted a three-call arrival sequence. A water-current comparison sampled the original and port at different points in the update. Both required test corrections rather than gameplay changes. A harness is the program that sets up and observes a test. Its bugs can look like game bugs.

These are reported historical findings, not fresh runtime verification performed for this skill.

Internal source review: `docs/QA-CAMPAIGN-PLAN.md:143-149`.

## Practice 4: keep controller paths identical for performance comparisons

A reactive controller script changed its input history when rendering speed changed. That made before-and-after performance comparisons unreliable. Recorded replay through the normal controller interface compared consumed inputs and gameplay state on the same simulation updates.

This matters beyond platform games. A racing comparison needs the same driving inputs. A rhythm game needs the same input timing. A turn-based game needs the same action sequence. If performance work changes the path, it changes the experiment.

Internal source review: `PERFORMANCE.md:48-52`. Original-console timing remained open in `PERFORMANCE.md:63-67`.

## Practice 5: withdraw stale passes when identities are incomplete

The current handoff records an interrupted validation run after missing reference and data inputs were found in cache bookkeeping. Recovery retained old raw evidence. It required reruns where old inputs were unknown. The reviewed source checks reference content, selected environment settings, BIOS identity, logs, and origin records before reuse.

A hash is a compact identity computed from file contents. A recorded hash cannot prove an input that the earlier run never recorded. Current source, a commit name, or a file date cannot fill that gap after the fact.

Internal source review: `NEXT-SESSION.md:10-30`; `tools/qa_resume.py:178-191`; `tools/qa_resume.py:301-306`; `tools/qa_resume.py:614-632`.

## Practice 6: resume within host limits

The reviewed tools implement worker caps, emulator caps, cooling periods, and durable report replacement. The handoff records one game job, one emulator, and explicit storage and cooling limits for that host. It also preserves failed and interrupted states.

These are implemented controls and written practices. This review does not establish a measured reduction in token use, elapsed time, storage writes, or hardware wear.

Internal source review: `tools/qa_limits.py:13-75`; `tools/qa_limits.py:84-115`; `tools/qa_lifecycle.py:141-158`; `NEXT-SESSION.md:41-43`.

## What transfers to other games

Use the same method for a 3D action game, a puzzle game, an engine replacement, or a new input system: inventory player-visible paths, define the reference, build small milestones, keep distinct evidence types, and accept on the actual target.

The Sonic records do not prove the public skill works on a second port. They do not establish general binary recovery, a finished game, or current console acceptance. Those are separate evaluation gates. Public demonstrations use original or explicitly licensed material rather than the Sonic project’s proprietary game data.
