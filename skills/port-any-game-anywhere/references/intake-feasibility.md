# Intake and feasibility

The intake produces a port plan and acceptance criteria. It does not promise a port.
Inspect existing documentation before asking the developer for missing facts.

## Establish the reference

Identify the exact edition, region, patch, executable, source revision, and asset
set. State what the developer can lawfully inspect, execute, modify, and distribute.
Do not infer permission from a public download or the age of a game.
List missing assets, unavailable services, proprietary tools, and inaccessible code.
Keep legal uncertainty explicit. This method does not supply legal clearance.

For source-based work, first build an unmodified reference if feasible. Confirm
that it represents the selected game version. For binary-only work, establish a
repeatable way to observe the reference before estimating source recovery.

## Test the target constraint

Record the actual hardware and operating environment. Measure a small workload
when a performance or memory assumption decides feasibility. Check:

- CPU architecture, instruction support, arithmetic, and byte order.
- Memory budgets, storage, load times, and available runtime services.
- Graphics features, resolution, aspect ratio, refresh rate, and synchronization.
- Audio format, latency, mixing, streaming, and device behavior.
- Controllers, keyboard, mouse, touch, accessibility, and device disconnects.
- Save locations, permissions, failure recovery, and any external services.

Identify what the developer can test on the target now. A cross-compiled build
does not establish that it runs. An emulator can reduce uncertainty but cannot
satisfy a physical-device gate.

## Make a bounded recommendation

Select one of three conclusions: feasible within stated limits; a measured
experiment is needed; blocked by a named constraint. Record the evidence.
If a different target or reduced scope is needed, ask before changing the goal.

The first milestone must cross a meaningful boundary. Examples include loading a
save and continuing play, completing a turn and entering the next scenario, or
finishing a level and returning through the correct menu. Select the boundary
most likely to reveal an architectural risk. A screenshot alone cannot close it.

Use the port-plan template. Name who accepts deliberate differences and who can
supply target-device evidence. If no operator is available, leave that gate open.
