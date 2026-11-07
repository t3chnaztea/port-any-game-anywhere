# Efficient agent work

Reduce repeated work, not fidelity or verification. Use the existing project's
tools when they already meet the gate. Avoid building a general framework to
solve one port's local problem.

## Investigate one uncertainty

Write the question and the evidence needed to decide it. Search for exact symbols,
files, and records before reading. Read bounded ranges. Widen only when the first
pass cannot answer the question. Do not load whole archives, generated assets,
large binaries, or every reference as session background.

Run the smallest decisive comparison first. A controlled source/native check can
find a logic error before an expensive emulator route. Use full gates at milestone
boundaries or after shared-system changes. Do not repeat a passing broad suite
unless new changes or unresolved concerns make that useful.

Keep tool output short. Store logs, traces, captures, and search results in local
artifacts. Report the exact result, identity, and artifact path. Do not replace
evidence with a long narrative of attempted commands.

## Keep one ledger and a compact handoff

The completion ledger owns claim status. Update only affected entries. The handoff
records current work, exact last results, open failures, relevant identities, and
the next command. Keep it within 45 lines and 3.5 KB. Link longer evidence.
Check the actual workspace before trusting an old handoff.

## Reuse only matching work

Build cache keys from every relevant input: source, dirty files, references, assets,
fixtures, tools, tool versions, flags, configuration, selected environment settings,
runtime, and route. Do not assume an unspecified setting is irrelevant.
Revalidate inputs before using a previous result. If its conditions cannot be
reconstructed, rerun the affected gate or keep it unverified.

Content hashes identify files. They do not prove semantic equivalence, completeness,
or rights. A matching build does not make a test result applicable to another
device. Never use an old pass as proof for changed code.

Use deterministic scripts for status, hashes, routing, transforms, and aggregation.
Keep pending, running, failed, interrupted, blocked, skipped, and passed outcomes
distinct. Make invalid records fail visibly rather than silently disappearing.

## Bound delegation and resources

Delegate only an independent question with a clear deliverable and enough benefit
to justify duplicated context. Give it exact paths, constraints, and evidence
requirements. Keep one writer per checkout. The integrating agent owns shared
manifests and lockfiles. Do not expand a child's permissions or spending authority.

Default to one heavy job. Before expensive runs, set concurrency, CPU/memory,
disk, time, and output limits.
Respect host power and temperature controls. Leave capacity for active work.
Track processes started by this run. Stop those processes on cancellation or timeout.
Never kill processes by broad name or interfere with another session.

## Resume after interruption

Preserve partial logs and terminal status. Write the checkpoint before starting a
long phase. Use atomic record writes where tools support them. On resume, inspect
repository changes, process state, and input identities. Reuse only completed,
matching evidence. Restart interrupted checks as new runs; do not label them passes.
If resource limits caused interruption, adjust the plan before repeating the run.
If required storage disappears, stop owned work safely. Do not write replacement
records to an unexpected mount point or continue with silently missing assets.
