# Compatibility and requirements

This is a development snapshot. A described workflow is not a tested platform claim. Support is earned by a recorded evaluation on named tools and devices.

## Agent Skills clients

The core uses the open [Agent Skills format](https://agentskills.io/specification). Installation and invocation belong to the client. They are separate from the porting workflow.

**Codex is the first evaluation target.** Copy the whole `skills/port-any-game-anywhere/` directory into `~/.agents/skills/port-any-game-anywhere/`. A project-local installation can use `.agents/skills/port-any-game-anywhere/`. Invoke `$port-any-game-anywhere`. Optional Codex metadata requests explicit invocation.

These paths follow the current [Codex skills documentation](https://developers.openai.com/codex/skills/), researched on 2026-11-07. The current documentation takes precedence over older local instructions that name `~/.codex/skills/`.

**Claude Code is an optional, untested client route.** Its documented personal-skill directory is `~/.claude/skills/port-any-game-anywhere/`. Its explicit invocation is `/port-any-game-anywhere`. See [Claude Code’s skills documentation](https://code.claude.com/docs/en/skills), researched on 2026-11-07. A passing Codex evaluation would not establish Claude Code support.

Other compatible clients remain untested. The skill needs an agent with access to the project’s files and selected tools. It grants no additional permissions. It requires no model API, account integration, or background service beyond the chosen client. Access to a tool is not permission to publish files or distribute game data.

## Current matrix

| Component or route | Current state | Required evidence before a support claim |
| --- | --- | --- |
| Local development environment | Maintainer records macOS on arm64, Python 3.13, Node 26, Codex CLI 0.165.0, and Claude Code 2.1.319 as available | Record actual checks and their inputs in the release status |
| Packaged Codex installation and live use | Pending | Explicit invocation, intake output, bounded reference loading, and interruption evaluation |
| Claude Code and other clients | Untested | Separate clean installation and live client evaluation |
| Python record/check helpers | Development checks tracked in `STATUS.md` | Clean-checkout helper tests and invalid-record tests |
| Source-led workflow | Designed; external pilot pending | Pinned Fifteen reproduction with required paths mapped to current evidence |
| Binary-to-source recovery | Designed; controlled trial pending | Switchboard original binary, recovered buildable C, and independent behavior comparisons |
| Ghidra on Linux x86-64 | Planned evaluated recovery route | Pinned Ghidra, Java, operating system, compiler, options, and original binary |
| Native C to browser | Planned adapter; pilot pending | Reproducible build plus browser behavior and persistence checks |
| Physical console targets | Guidance only | Named console, loader or firmware, exact artifact, and user-confirmed results |
| Desktop browser and touch input | Device checks pending | Named desktop browser plus an actual named touch device and browser |
| Other agents, decompilers, CPUs, engines, or targets | Untested | A separate bounded evaluation; do not infer support from the universal method |

At the initial environment review, Docker’s daemon, Ghidra, Java, and Emscripten were unavailable. Emscripten is a toolchain that compiles C or C++ for the web. Missing tools leave the relevant pilot pending. They do not justify a simulated pass.

## Dependency policy

Use the game’s existing build system when possible. Pin the selected compiler, debugger, decompiler, emulator, browser, and asset requirements in the port plan. A toolchain is the set of programs that turns source into a runnable build.

Python is for the small evidence helpers. Node and browser tools are specific to the TypeScript example. They are not prerequisites for reading the skill or planning an unrelated port. Ghidra is specific to the planned recovery evaluation. No dependency is bundled merely because an adapter names it.

The first release does not include an installer, a new orchestration framework, a bundled decompiler, remote services, scheduled jobs, or background hooks. Add support through documented, evaluated adapters rather than broad compatibility claims.

## Resource limits

Choose worker, emulator, memory, storage, and timeout limits for the host before expensive work starts. Default to serial game jobs until measured headroom supports more. Preserve partial evidence when a run stops. Resume only after input identities, saved artifacts, and owned-process cleanup are verified.

Sonic’s particular cooling time or storage reserve is evidence about that host. It is not a default requirement for every port.
