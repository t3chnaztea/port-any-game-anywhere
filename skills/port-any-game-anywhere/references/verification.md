# Verification and release

Choose the smallest test that can decide the current question. Expand verification
when the changed system has wider effects. Passing a command establishes only
the assertions that command actually checked.

## Build a chain of different evidence

- Source inspection explains a suspected rule and identifies its reference.
- A deterministic fixture checks controlled inputs and expected state. Record the
  random seed and virtual clock when either affects the result.
- Controller-driven gameplay checks an end-to-end route using normal inputs.
  Direct state injection must be labeled and cannot prove that route is reachable.
- Emulator runs name the emulator version, settings, BIOS identity when required,
  input recording, and output captures. Keep restricted files private.
- Target-device runs name the physical device, OS or firmware, build identity,
  controls, display/audio path when relevant, operator, and observed result.
- Review checks whether the evidence supports the stated acceptance criterion.

Use both reached state and player-visible behavior where a route needs both.
A screenshot can support presentation. It cannot establish correct saves or
simulation state. A memory assertion can support state. It cannot establish audio.
Verify that a test is capable of failing on a known bad or injected fault case.
Do not derive the expected result solely from the implementation under test.

## Record reproducible identities

A reproducible build produces the same artifact bytes from the same declared
inputs and build environment. A deterministic check repeats the same result for
the same declared inputs and conditions.

Record the working tree contents, reference files, assets, fixture data, tool
executables and versions, compiler/linker flags, environment settings, runtime
configuration, commands, inputs, and artifacts. A commit ID alone misses dirty
files. A version label alone can miss a locally modified tool.

Separate reproducible build identity from deterministic gameplay. A fixed test
seed does not make a build reproducible. A reproducible build does not establish
that gameplay is correct. Explain nondeterminism that cannot be removed.

Use the record-format reference for helper contracts. Keep complete logs and
captures locally. Public summaries contain redistributable material only.
Record start and terminal status. A timeout, crash, missing dependency, absent
artifact, or interrupted process cannot pass. Diagnose infrastructure failures
separately from game defects. Do not silently omit either from reported results.

## Independently verify fixes

Use a reference comparison, an independently derived expected result, another
test surface, or a separate reviewer. A second model repeating the fix explanation
is not independent evidence. Re-run the reproduction against the changed build.
Then test adjacent routes and profiles affected by the shared system.

## Close a release gate

Reconcile the release against every required claim in the dated inventory. Include
all modes, required routes, transitions, persistence, failure states, and endings.
Check stated performance limits and target-device gates. Record exclusions,
unsupported targets, remaining unknowns, and who accepted deliberate differences.

A release candidate can be useful with open gates. Label it as a candidate.
Do not call the game complete when a required gate remains open. Do not convert
emulator results into console acceptance. Never invent a device operator or test.
The final report names the exact artifact tested and the scope its evidence covers.
