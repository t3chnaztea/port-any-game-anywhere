# Contributing

Contributions should help someone finish a port or assess its evidence. A new adapter is useful when a bounded example shows what it adds. A long list of nominally supported platforms is not support evidence.

## Before changing behavior

Read [the release status](STATUS.md), then identify one concrete problem. State the current behavior, the proposed behavior, and the evidence that can distinguish them. Keep the change small. Do not refactor adjacent material just to make a contribution larger.

For skill changes, include the prompt or situation that needs the change. For adapter changes, name the tool versions and target. For helper changes, include an invalid or interrupted case that the current code mishandles.

## Evidence standard

- Separate source inspection, fixture tests, automated gameplay, emulator results, and actual target-device results.
- Pin inputs, commands, tool versions, settings, assets, artifacts, and relevant environment details. Never use an old pass for changed inputs.
- Keep unknown, partial, failed, interrupted, and untested results visible. Explain exclusions without shrinking a required scope silently.
- Record the expected result before changing a baseline. A changed test must have a behavior or source reason.
- Define a finite denominator before reporting coverage. Report counts by evidence type rather than an unsupported percentage of “the game.”

A fixture is a controlled test setup. It can prove behavior from that setup without proving the normal route reaches it. A baseline is the saved expected result used for comparison.

## Checks

Run the repository checks and helper tests from the checkout root:

```sh
python3 tools/check_repository.py
python3 -m unittest discover -s tests -v
```

Review the rendered Markdown and relative links when changing documentation. Check that the installed skill remains self-contained. Its references, templates, and scripts must resolve inside its directory after copying it into a client.

A code or documentation check is not a live skill evaluation. Do not change a pending pilot to passed because these commands succeed.

## New examples and adapters

Start with a written proposal in an issue. Name the game or fixture, its license, the source and target, the specific gap, and an acceptance test. Use an original or freely redistributable example. A proprietary asset requirement must stay external.

Universal rules belong in the skill’s main workflow or a topic reference. Tool commands and platform limits belong in an adapter. Keep the main `SKILL.md` concise. Add a new framework, service, or dependency only when an evaluated use case needs it.

An existing upstream port is a valid reproduction study when disclosed. Do not describe it as a new port or an independent recovery result. Keep expected outputs separate from completed evaluations.

## Issues and pull requests

Include enough information to reproduce the problem: project revision, relevant tool versions, minimal input, expected result, actual result, and safe evidence. Link a retained artifact where practical. Keep logs short in the issue. Retain detailed logs as an artifact with secrets and proprietary data removed.

For a pull request, explain the final change and its validation. Disclose skipped checks and limitations. Use one writer per worktree when agents collaborate. Do not merge or publish on another person’s behalf without authorization.

## Rights and private data

Submit only material you have the right to contribute under its stated license. Original project code and documentation use MIT. Mark original CC0 assets explicitly. Preserve third-party notices and licenses.

Do not submit game discs, ROMs, BIOS files, proprietary assets, credentials, save files containing personal data, or private filesystem paths. A decompiled file does not become freely licensed because a tool produced it. Do not include it without a clear right to redistribute it. See [security guidance](SECURITY.md) and [third-party notices](THIRD-PARTY.md).

Be specific about defects and respectful toward people. Describe the observed problem. Avoid unsupported claims about another project’s quality or motives.
