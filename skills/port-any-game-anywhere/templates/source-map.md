# Source recovery map

Status: analysis template. No recovered behavior is verified by this document alone.
Record the reference identity, analysis tool/version/settings, and lawful access.

| System or behavior | Reference location | Recovered source | Confidence | Decisive comparison |
| --- | --- | --- | --- | --- |
| Example: save checksum | Record symbol/address and input version | Link reviewed source when available | Unknown until inspected | Controlled valid/corrupt-save inputs |

Use `observed`, `inferred`, or `unknown` for confidence. Explain each inference.
Keep tool-generated output separate from reviewed reconstruction.

## Data and execution rules

Record integer widths, signedness, byte order, structures, file layouts, timing,
update order, platform dependencies, and unresolved code paths. Link instructions
or source ranges that establish each rule. Do not turn inferred names into facts.

## Build and equivalence

Record the recovered-source build recipe and exact inputs. Link deterministic
comparisons, normal-input routes, and target tests separately. Explain differences.
Full recovery means buildable behavior-equivalent source for the declared scope.
Original variable names and file layout are not required. Untested paths stay open.

## Missing material

List unavailable code, data, tools, assets, or services. State the effect on scope.
If an unresolved dependency blocks the port, keep the relevant ledger gate blocked.
