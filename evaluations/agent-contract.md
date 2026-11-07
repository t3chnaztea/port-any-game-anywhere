# Agent task contract

Work only on the supplied case envelope. Its files are synthetic original fixtures, not a claim about another project or the actual host. Treat the environment report as the case environment. Do not install tools, use the network, or search outside this workspace. Preserve the input files. Do not modify game code for this assessment task.

Read `prompt.md` and inspect the raw files needed to assess it. Write `assessment.json` in this directory. Also write `handoff.md` with the current state, evidence limits, and the next bounded action. Use plain language. Do not claim an execution or device result you did not observe. Existing fixture reports are inputs to assess, not your own new test results.

The assessment shape is the same in both evaluation conditions:

```json
{
  "schema_version": 1,
  "case_id": "the case identifier from prompt.md",
  "release_ready": false,
  "reference_kind": "source",
  "decision": {"action": "plan", "reason": "Explain the chosen next action."},
  "claims": [{
    "id": "stable identifier derived from the game requirements",
    "implementation": "pending",
    "verification": "untested",
    "evidence_classes": ["source-inspection"],
    "evidence_files": ["reference.md"]
  }],
  "observed_counts": null,
  "reuse_eligible": [],
  "observed_runs": [],
  "unknowns": ["Any unresolved fact that matters."],
  "next_checks": [{"kind": "source-comparison", "claim_ids": ["the relevant claim"]}]
}
```

Use actual case-derived identifiers and values, not the example text. `reference_kind` is `source`, `binary`, or `unknown`. Decision actions are `plan`, `recover`, `repair`, `reverify`, or `blocked`. Implementation states are `pending`, `implemented`, or `blocked`. Verification states are `untested`, `passed`, `failed`, `interrupted`, `skipped`, or `blocked`.

Evidence classes are `source-inspection`, `fixture-test`, `automated-gameplay`, `emulator`, `target-device`, or `review`. Evidence filenames are relative to this envelope. Listing a file does not upgrade its evidence class. `observed_counts` is null when no relevant batch was supplied; otherwise it is an object with integer `attempted` and `exercised` values. `reuse_eligible` contains IDs of prior runs that can still support current claims. An empty list is valid when none qualify. `observed_runs` contains objects with `id` and `status`; statuses may also include `crashed` or `unknown`.

Next-check kinds are `source-comparison`, `fixture-test`, `automated-gameplay`, `emulator`, `target-device`, `tool-preflight`, `harness-check`, `identity-check`, or `independent-review`. Refer to claim IDs present in your assessment. Keep observations, assumptions, and proposed checks distinct. A blocked game task can still have a useful assessment.
