# Evidence record contract

Schema version: `1`. Helpers use Python 3.11 or newer and its standard library.
The recorder runs on Linux and macOS. The checker does not run recorded commands.
Run both from any directory. JSON paths resolve relative to the JSON file that
contains them. Generated records keep relative paths, not host-specific roots.

## Commands

```sh
python3 skills/port-any-game-anywhere/scripts/record_run.py run-manifest.json --output evidence/run-id.json
python3 skills/port-any-game-anywhere/scripts/check_port.py completion-ledger.json
python3 skills/port-any-game-anywhere/scripts/check_port.py completion-ledger.json --require-complete
```

The recorder never invokes a shell, retries, discovers tests, or reuses a result.
Copy the packaged JSON templates into the port workspace. Replace example paths,
commands, identifiers, dates and hashes with current actual values before use.
The templates are not ready-made passing evidence. Do not run them blindly.
Use a new output path per run. An existing record or log is never overwritten.
The record moves from `pending` to `running` to a terminal status. Terminal
statuses are `passed`, `failed`, `interrupted`, `blocked`, and `skipped`.
Timeout and caught SIGINT/SIGTERM produce `interrupted`, never `passed`.
Exit code zero means the command completed with its declared inputs unchanged.
It does not establish that its assertions are useful or that a game is faithful.

## Explicit command manifest

All listed keys are required. Lists may be empty except `claim_ids` and `argv`.

```json
{
  "schema_version": 1,
  "id": "save-reload-001",
  "claim_ids": ["save.reload"],
  "profile": "original",
  "target": "browser",
  "evidence_class": "fixture-test",
  "command": {
    "argv": ["python3", "tests/save_reload.py"],
    "cwd": ".",
    "timeout_seconds": 30,
    "output_limit_bytes": 1048576
  },
  "inputs": [
    {"role": "source", "path": "src/save.py"},
    {"role": "reference", "path": "reference/save-contract.txt"},
    {"role": "fixture", "path": "tests/save_reload.py"}
  ],
  "tools": [
    {"path": "python3", "version_argv": ["python3", "--version"], "flags": []}
  ],
  "environment": ["LANG"],
  "artifacts": ["results/save-reload.json"]
}
```

Input roles are `source`, `reference`, `asset`, `fixture`, and `config`. List
every file read by the check, including dependencies, reference data, scripts,
required assets, and configuration. Enumerate directory contents as files.
The helper cannot discover undeclared dependencies. It always fingerprints its
own recording source, the manifest and the invoked executable. A changed recorder
invalidates old passes. Tool paths may be executable names on PATH
or file paths. Explicit `version_argv` must start with the declared tool path.
Tool flags must describe the actual invocation. The manifest fingerprint detects
later edits to command arguments, flags, configuration, and selected variables.

The recorder captures file sizes and SHA-256 hashes before and after the command.
SHA-256 is a fingerprint of file contents. It captures selected environment
variables as presence plus a value hash. It does not store their raw values.
Tool version probes run once with a 5-second limit and a 4096-byte output limit.
List all environment settings that affect results. Keep secrets out of argv and
tracked records. An unlisted input or environment variable is not covered.

Artifacts are files expected after successful execution. A missing artifact,
input, tool, failed version probe, changed identity, or truncated log prevents a
pass. The durable combined stdout/stderr log is `RECORD.log`. Its maximum size
is `output_limit_bytes`. Further output is drained and discarded. The command
still has a time limit. Console output contains only a short status summary.
SIGINT/SIGTERM and timeout terminate only the recorder's own child process group.
The recorder does not stop other host jobs. SIGKILL or storage loss can leave a
pending/running record; the checker refuses to count it. Do not relabel it passed.

## Canonical completion ledger

```json
{
  "schema_version": 1,
  "profiles": ["original", "enhanced"],
  "targets": ["browser"],
  "unknowns": [],
  "claims": [{
    "id": "save.reload",
    "path": "Campaign: save, restart the process, reload, continue",
    "profile": "original",
    "target": "browser",
    "required": true,
    "implementation": "implemented",
    "verification": "untested",
    "required_evidence": ["fixture-test", "target-device"],
    "evidence": ["evidence/save-reload-001.json"],
    "unknowns": []
  }]
}
```

Claim IDs are stable and unique. `path` names the game scenario, not a file.
Profiles distinguish original behavior from deliberate enhancements. Every claim
must name a declared profile and target. Implementation values are `pending`,
`implemented`, and `blocked`. Verification values are `untested`, `passed`,
`failed`, `interrupted`, `skipped`, and `blocked`.

Evidence classes are `source-inspection`, `fixture-test`, `automated-gameplay`,
`emulator`, `target-device`, and `review`. The first four may use machine records.
An emulator cannot satisfy `target-device`. A fixture cannot satisfy normal-input
gameplay. A reviewer must assess test quality and independence outside this helper.

A claim counts as satisfied only when it is implemented, marked verified passed,
has no unknowns, and has current passed evidence for every required class. Each
record must include the claim ID and match its profile and target. Missing,
malformed, interrupted, stale, skipped, and blocked evidence remains visible.
One invalid listed record makes its claim incomplete, even if another passes.

The denominator is all claims with `required: true`, with separate counts by
profile/target and evidence class. Optional claims stay visible. No global
percentage is reported. Zero required claims is not completion. Top-level
unknowns prevent release completion. The checker normally exits zero for a valid
but incomplete ledger; `--require-complete` exits one for gaps. Malformed data
exits two. The recorder exits zero only for a passed record.

## Human device and review records

Use `record_type: "manual"`. Required fields are `schema_version`, `id`,
`claim_ids`, `profile`, `target`, `evidence_class`, `status`, `operator`, `device`,
`observed_at`, `procedure`, `observations`, `inputs`, and `artifacts`.

`device` is an object with `kind`, `model`, `identifier`, and `configuration`.
For `target-device`, kind must be `physical`. For `review`, use kind `review`.
`observed_at` is an ISO 8601 timestamp with a timezone. `procedure` describes the
steps. `observations` is a nonempty list of actual observations. Do not fill it
with expected outcomes. Inputs use `{role, path, sha256, size}`. Artifacts use
`{path, sha256, size}`. At least one input and exact build artifact are required.
Input roles use the manifest role list. Hashes must be 64 lowercase hex digits.
Only terminal statuses are valid. Empty placeholder identity fields are invalid.

The checker verifies shape and present file fingerprints. It cannot establish
that a named human performed a test, that the device is real, or that observations
are true. Device acceptance still needs the project's designated human review.
Do not fabricate a manual record to close an unavailable-device gate.

## Freshness and resume

The checker hashes the original manifest, every before/after input, executable,
tool, artifact and log against files available now. It checks selected environment
presence and value hashes. It never executes version probes or recorded argv.
It rejects a pass if an identity changed during the run or since the run. Old
results remain historical evidence. There is no automatic cache or reuse action.
Preserve records after failed and interrupted attempts. Start a new run after a
fix. The ledger remains the single completion source; a handoff only links it.
