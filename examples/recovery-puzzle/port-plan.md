# Switchboard port plan

Reference: the original MIT C implementation and version 1 behavior contract. Public data: six original text boards and generated tones. Required target: TypeScript in a browser, with keyboard, adjacent pointer actions and touch buttons. The source-authored translation is preparation for a separate blinded Linux/Ghidra trial.

Feasibility: the small fixed state fits ordinary browser resources. File saves require an explicit browser storage/import/export adaptation. The reference has no network service, proprietary asset, random simulation, real-time physics or console requirement.

## Milestones

| Milestone | Gate | Current evidence |
|---|---|---|
| Rules and transitions | Both modes and all six boards finish through normal actions; no board7 | Cross-language fixture record |
| Saves and undo | Canonical formats match; cold load retains up to128 steps; invalid and failed writes preserve state | Cross-language fixture record and independent defect review |
| Browser shell | Keyboard/pointer routes, complete campaign, export/import, corruption and quota checks | Browser automation, not human listening or iPhone evidence |
| Device acceptance | Desktop Chrome/macOS plus actual iPhone/Safari checklist, including sound | Pending |
| Recovery | Withheld-source Linux x86-64 binary, buildable recovered C, independent comparisons | Pending Ghidra/Java/Linux and controlled access |

The [completion ledger](completion-ledger.json) is authoritative. The table is a navigation guide, not a second status ledger. Its finite scenario families do not exhaust all possible inputs.

## Required comparison

Compare full state after each controller action. Compare serialized saves byte for byte. Compare event identities for sound. Browser waveform and terminal bell are deliberate presentation adaptations. Timing acceptance concerns prompt action response and absence of stalls; no artificial frame-rate target is needed for this turn-based game.

Record exact browser build, compiler, flags, runtime, test driver, source and reference identities. Use one heavy job at a time. A changed input requires a new applicable record. Keep failed records and independent review limits.

The release gate remains open until missing device, audio and recovery evidence exists. Never describe the source-authored TypeScript implementation as recovered code.
