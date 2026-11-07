# Research record

**Research date: 2026-11-07.** This is a selected, best-effort study of reverse engineering, game ports, agent skills, and developer automation. It is not an exhaustive ranking.

The study uses repositories, READMEs, documentation, releases, contribution guides, issue reports, and dated announcements. Undated sources are labeled below. Mutable pages describe the state read on the research date. Future evaluations must pin the revisions they actually use.

“Successful” here means there is evidence of usable distribution, maintained work, or participation beyond a project description. It does not mean every claim is validated. Stars and announcement scores describe attention. They do not establish quality, sustained use, or why a project spread.

## Reverse engineering: REA

The requested project described as “reverse engineer anything” is **[morluto/rea](https://github.com/morluto/rea)**. The exact repository was verified rather than inferred from the phrase. Its README is the primary source for its product description and setup. Publication date: undated; researched 2026-11-07.

**Observation:** the README starts with one Model Context Protocol (MCP) connection for binary, application, and runtime investigation. MCP is a standard way for an agent client to connect to tools. The README supplies a concrete feature-investigation prompt and an `npx rea-agents setup` path that registers tools and instructions for review. The task and first action are clear. **Audience inference:** people using agents to understand unfamiliar compiled software are a likely audience. That is an inference from the stated task, not a measured audience profile.

The [DX-Ball showcase](https://morluto.github.io/rea/showcase/dx-ball/) has a project checkpoint dated 2026-10-07. It reports 3,205 original-x86 cases for a sound-panning function and 63 compiled bytes. This is a focused demonstration of one function. It does not establish complete-game recovery. The [initial commit](https://github.com/morluto/rea/commit/729d3e927cbcf17224e6b988eebcfae0d215c876) is dated 2026-04-14. The [rea-agents 6.8.0 release](https://github.com/morluto/rea/releases/tag/rea-agents-6.8.0) is dated 2026-10-25. These are evidence of development over time. No REA installation or runtime was evaluated here.

The [contribution guide](https://github.com/morluto/rea/blob/main/CONTRIBUTING.md) asks for focused reproductions, versions and environment, and human-owner review. It rejects fabricated human approval. Publication date: undated; researched 2026-11-07.

A [2026-07-14 Show HN submission](https://news.ycombinator.com/item?id=48901763) had 3 points and no comments in the researched snapshot. A [2026-10-10 submission](https://news.ycombinator.com/item?id=50028275) had 814 points and 340 comments. These are two dated attention snapshots. The July item is the earliest located in this study, not proof of the first public appearance. The October response does not establish broad recovery accuracy or demonstrate that the name caused adoption.

**Project decision:** retain a memorable name, then state the access, tooling, target, and verification limits beside the promise. A tool that helps inspect a binary does not by itself inventory or accept a complete game port.

## Game reconstruction: pokeemerald

**Observation:** [pret/pokeemerald](https://github.com/pret/pokeemerald) presents a decompilation project with a concrete matching-build objective and an expected SHA-1 identity. SHA-1 is a file fingerprint used here to identify the expected ROM output. The build instructions give contributors a specific result to reproduce rather than asking them to judge whether the game merely looks plausible. README publication date: undated; researched 2026-11-07.

Its [build workflow](https://github.com/pret/pokeemerald/blob/master/.github/workflows/build.yml) distinguishes an original-compiler checksum comparison from a modern build without that comparison. Its [commit history](https://github.com/pret/pokeemerald/commits/master/) records multiple contributors and save-reporting/source-match fixes in September and October 2026. The workflow is undated; both sources were researched 2026-11-07. This is maintenance and participation evidence, not independent proof of every build.

**Audience inference:** contributors reconstructing game source and developers building modifications are plausible users. The matching objective explains the technical attraction. It is not evidence that every contributor has the same goal.

**Project decision:** make the expected first result concrete and reproducible. Preserve original identities and compare against a pinned reference. Matching one built file is a different claim from testing a port’s routes, input adaptation, persistence, and new target behavior.

## Complete ports: OpenRCT2

**Observation:** [OpenRCT2](https://github.com/OpenRCT2/OpenRCT2) explains its value through a familiar game, supported systems, and practical build and play instructions. It separates its engine work from required original game data. Its [v0.5.7 release](https://github.com/OpenRCT2/OpenRCT2/releases/tag/v0.5.7), dated 2026-11-01, provides evidence of continued release work. The README is undated; researched 2026-11-07.

The README places a screenshot and download route before build detail. It invites translations, code, graphics, audio, and scenarios. The [contribution guide](https://github.com/OpenRCT2/OpenRCT2/blob/develop/CONTRIBUTING.md) asks for reproduction steps, a save where relevant, build, version, and architecture. It is undated; researched 2026-11-07. These are concrete routes into use and participation.

**Audience inference:** players seeking modern-system support and developers extending the game are likely audiences. A maintained release is evidence of delivery activity. It does not prove every route works or establish which presentation choice attracted users.

**Project decision:** explain the familiar user problem before the internal method. Make asset requirements explicit. Provide release notes and reproducible setup. Treat enhancements as an intentional behavior set instead of silently redefining authenticity.

## Engine replacement: DevilutionX

**Observation:** [DevilutionX](https://github.com/diasurgical/DevilutionX) makes its game and modern-platform purpose clear. It documents required game data rather than distributing the original game. Its [release history](https://github.com/diasurgical/DevilutionX/releases) shows versioned delivery. README publication date: undated; researched 2026-11-07.

The README identifies optional enhancements and separate retail/shareware asset setup. The [commit history](https://github.com/diasurgical/DevilutionX/commits/master/) records UI tests, translations, and controller work in March 2026. Those are observed areas of participation, not a count of active users.

Its [timedemo test source](https://github.com/diasurgical/DevilutionX/blob/master/test/timedemo_test.cpp) is a useful example of explicit test scope. The inspected test uses a limited fixture, omits audio, and can skip when required assets are missing. That is evidence about the test’s boundaries. It is not a claim that the project lacks audio testing or is poorly verified. Source publication date: undated; researched 2026-11-07.

**Audience inference:** players who need a maintained way to play and developers improving the engine are likely users. **Project decision:** copy the precision of bounded claims. A skipped asset-dependent test must remain skipped. A timedemo result must not become a claim about every game mode or device.

## Agent skills: anthropics/skills

**Observation:** [anthropics/skills](https://github.com/anthropics/skills) packages specialized workflows as folders of instructions, references, and scripts. Its README provides installation routes and example prompts. The [skill-creator instructions](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md) describe paired skill and baseline evaluations with pass, time, and token information. Both sources are undated; researched 2026-11-07.

The [commit history](https://github.com/anthropics/skills/commits/main/) included licensing work on 2026-11-06 and SDK updates on 2026-10-28. Those are maintenance observations, not proof of skill efficacy.

Two user issues expose evaluation risks. [Issue 518](https://github.com/anthropics/skills/issues/518), dated 2026-03-04, reports real evaluation use plus baseline scoring and schema/path friction. [Issue 1478](https://github.com/anthropics/skills/issues/1478), dated 2026-07-25, reports crashed non-trigger evaluations being scored as passes. These reports were not independently reproduced for this study. They must not be generalized into a claim about the current project.

**Audience inference:** agent users creating repeatable specialist workflows are likely users. **Project decision:** use a concise core with supporting material. Evaluate the actual skill separately from helper tests. A crashed, blocked, or skipped evaluator cannot produce a pass.

## Developer workflow: Superpowers

**Observation:** [obra/superpowers](https://github.com/obra/superpowers) describes an intent-to-plan-to-build-to-review workflow for coding agents. Its README gives client-specific installation and diagnosis routes. Its [testing guide](https://github.com/obra/superpowers/blob/HEAD/docs/testing.md) separates infrastructure checks from behavior in real sessions. Those pages are undated; researched 2026-11-07.

The [v7.0.2 release](https://github.com/obra/superpowers/releases/tag/v7.0.2), dated 2026-11-03, reports tests and named fixes. [Issue 750](https://github.com/obra/superpowers/issues/750), dated 2026-03-15, records user cost friction and a maintainer response. This establishes an instance of use and feedback. It does not establish a current general failure or average cost.

**Audience inference:** developers who want more dependable agent execution are a likely audience. **Project decision:** show the sequence of work clearly, give installation checks, and keep live agent behavior separate from static conformance. Record cost rather than promising savings.

## Developer automation: uv

**Observation:** [uv](https://github.com/astral-sh/uv) presents familiar Python workflows with small runnable commands. Its [feature guide](https://docs.astral.sh/uv/getting-started/features/) supports gradual adoption. Its [contribution guide](https://docs.astral.sh/uv/reference/contributing/) specifies targeted tests and contribution expectations. These pages are undated; researched 2026-11-07.

The [0.13.7 release](https://github.com/astral-sh/uv/releases/tag/0.13.7), dated 2026-11-03, provides linked fixes, platform archives, checksums, and attestations. An attestation records information about how a distributed artifact was produced. These materials show release discipline. They do not prove that speed claims transfer to an unrelated agent workflow.

**Audience inference:** Python developers seeking a simpler and faster tool workflow are likely users. **Project decision:** make the first command useful, keep distribution predictable, and adopt only the small deterministic helpers this skill needs. Do not build a large porting framework before the second case supplies evidence.

## Shared lessons and the gap to serve

The observed projects make their task recognizable, supply a specific first result, and expose some part of their maintenance process. Repositories and user issues provide stronger evidence of actual work than a polished landing page alone. This study does not isolate the effect of names, opening copy, examples, or demonstrations on adoption.

The proposed opportunity is a completion and evidence method across porting contexts. The projects above solve different problems. The claim is not that they all fail to finish games. The skill’s own scope is to connect feasibility, faithful behavior, whole-game inventory, independent checks, target-device acceptance, and safe continuation.

Three hypotheses remain to be tested: that a new user can produce a useful plan quickly; that the method exposes important missing paths; and that bounded context and evidence reuse control cost without losing defects. The pilots and paired evaluations must supply that evidence.

## Related records

The [launch-history study](launch-history.md) distinguishes dated announcements from causal explanations. The [Sonic case study](case-studies/sonic-cd.md) separates implemented work, reported results, current validation, and hardware gates. The [compatibility matrix](compatibility.md) records what has and has not been evaluated here.
