# Codex installation smoke observation

On 2026-11-07, Codex CLI 0.165.0 loaded the development skill archive from a fresh project-local `.agents/skills/` folder. The task used the synthetic normal-intake envelope. The client ran read-only, used no external tools beyond local reads, and returned within the 60-second harness limit.

The retained command events show the agent reading `SKILL.md`, the reference index, intake guidance, the browser adapter, the plan template and the three case inputs. It did not load every reference. A `git status` check returned 128 because the temporary envelope was not a Git repository. The later file reads and final response completed with client exit 0.

The [assessment](assessment.json) identified the missing practice completion path and persistence implementation. It explicitly said that no runtime, fixture or device verification occurred. [The result](result.json) records the exact archive hash and client-reported usage. Those totals include client context. They are not an estimate of skill-only tokens, monetary cost, or savings.

This is an installation and intake observation. It is **not** one of the 32 paired evaluation runs. Same-host read isolation from evaluator material was not enforced. The model identity was not established from the retained event metadata. No baseline comparison was performed.
