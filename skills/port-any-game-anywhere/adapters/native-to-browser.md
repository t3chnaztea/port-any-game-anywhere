# Native to browser

**Status: untested adapter.** Use this reference when a native game moves to a web
browser. It does not claim that any native engine or language can be translated.

## Inspect the boundary

Identify rendering/audio dependencies, threads, filesystem calls, networking,
native extensions, and input assumptions. Decide whether the port retains the
engine, uses a compatible runtime, or rewrites parts. Record that choice and its
evidence before implementation. Pin browser, build tools, and runtime versions.

## Preserve the game contract

- Separate simulation updates from rendering callbacks. Background tabs and display
  refresh rates can change callback timing. Define pause and resume behavior.
- Define keyboard, pointer, touch, and gamepad mapping. Check focus loss, key repeat,
  disconnects, resizing, scaling, and browser-reserved shortcuts.
- Check audio startup after user interaction, interruption, latency, and cue sync.
- Map saves to persistent storage. Test reload, version migration, corrupt data,
  quota failure, denied storage, and interrupted writes where relevant.
- Measure load time, memory, frame times, and long sessions on the declared devices.
  Test offline behavior only when the product promises it.

Use the same reference routes and expected state across native and browser builds.
Record platform differences rather than deleting a failing comparison.
Controller recordings and screenshots supplement state checks; they do not replace
save, audio, or timing tests.

## Declare support

Name exact tested OS/browser/device combinations and controls. A headless browser
run does not prove audio, real input latency, or presentation on a physical device.
Test declared devices directly. Keep other combinations explicitly untested.
