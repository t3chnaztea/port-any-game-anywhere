# Development

Read `STATUS.md` for the current gates. Never promote planned or reported work to verified work.

Run `python3 tools/check_repository.py` for repository checks. Run `python3 -m unittest discover -s tests -v` for helper behavior checks.

Keep the skill self-contained. Its relative links must resolve inside the versioned skill directory.

Keep proprietary game data, credentials, and machine-specific source paths out of tracked files. Examples use original or explicitly licensed material.

One writer per worktree. Only the integrating agent edits shared release metadata and CI. Do not change a baseline to accept unexplained output.
