# Console target

**Status: untested adapter.** This describes recurring console questions. Each
console needs a specific toolchain and device acceptance plan.

## Establish target limits

Record CPU architecture, memory regions, video/audio limits, storage, loading,
controllers, timing, synchronization, and permitted development tools. Record the
device model, firmware, region, display, loader, and required private input hashes.
Do not distribute BIOS files, ROMs, disc images, keys, or proprietary game assets.

## Build within measured budgets

Measure a representative hard route before optimizing. Watch memory peaks, frame
times, loading pauses, input response, audio underruns, and long-session stability.
Pin compiler/linker tools and flags. Preserve exact build and packaged artifact
identities. Test the package that the operator will run, not an earlier local build.

## Check real-device risks

Use emulator routes for fast diagnosis. Keep device-specific risks open: graphics
ordering, synchronization, audio, storage writes, timing, peripheral behavior,
loader assumptions, and media access. Run cold boot, save/restart, retries, complete
routes, and sustained load on the declared hardware where required.

Give the operator short steps, expected outcomes, exact artifact identity, and a
place to record failures. Ask for observations rather than suggesting a pass.
Record the operator, device configuration, date, captures, and limitations.
An unreported device test remains untested. Never infer a hardware pass from an
emulator, a successful package, silence, or an earlier build.
