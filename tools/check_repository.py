#!/usr/bin/env python3
"""Check local links, skill portability, syntax, and public source boundaries."""
import ast
import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/port-any-game-anywhere"
FORBIDDEN_SUFFIXES = {".iso", ".cue", ".rom", ".bin", ".bios", ".mp3", ".mp4", ".wav"}

def source_files():
    result = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
                            cwd=ROOT, capture_output=True, check=True)
    return sorted({ROOT / name for name in result.stdout.decode().split("\0") if name})

def check(files):
    errors = []
    required = ["README.md", "LICENSE", "VERSION", "STATUS.md", "release-ledger.json",
                "CONTRIBUTING.md", "SECURITY.md", "THIRD-PARTY.md", "CHANGELOG.md",
                "docs/first-use.md", "docs/research.md", "docs/launch-history.md",
                "evaluations/README.md", "skills/port-any-game-anywhere/SKILL.md"]
    for name in required:
        if not (ROOT / name).is_file():
            errors.append(f"missing required file: {name}")
    for path in files:
        relative = path.relative_to(ROOT)
        if path.is_symlink():
            errors.append(f"source tree symlink requires review: {relative}")
            continue
        if not path.is_file():
            continue
        if path.suffix.lower() in FORBIDDEN_SUFFIXES or path.name.startswith(".env"):
            errors.append(f"forbidden public input: {relative}")
        if path.stat().st_size > 2_000_000:
            errors.append(f"large source file requires review: {relative}")
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            errors.append(f"unexpected binary in public sources: {relative}")
            continue
        if re.search(r"/(?:Users|Volumes)/[^\s\"']+", text):
            # This command intentionally accepts the documented Chrome app path,
            # never a private user or mounted-volume root.
            errors.append(f"machine-specific root in public file: {relative}")
        if re.search(r"-----BEGIN [A-Z ]*PRIVATE KEY-----", text):
            errors.append(f"private-key material: {relative}")
        if path.suffix == ".py":
            try:
                ast.parse(text, filename=str(relative))
            except SyntaxError as exc:
                errors.append(f"invalid Python {relative}: {exc}")
        if path.suffix == ".json":
            try:
                json.loads(text)
            except json.JSONDecodeError as exc:
                errors.append(f"invalid JSON {relative}: {exc}")
        if path.suffix == ".md":
            for target in re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", text):
                target = target.strip().split(' "', 1)[0].strip("<>")
                if not target or target.startswith("#") or urlsplit(target).scheme:
                    continue
                local = unquote(target.split("#", 1)[0])
                resolved = (path.parent / local).resolve()
                if not resolved.exists():
                    errors.append(f"broken link in {relative}: {target}")
                if path.is_relative_to(SKILL) and not resolved.is_relative_to(SKILL):
                    errors.append(f"skill link escapes package: {relative}: {target}")
    entry = SKILL / "SKILL.md"
    if entry.exists():
        text = entry.read_text()
        parts = text.split("---", 2)
        if len(parts) != 3 or parts[0].strip():
            errors.append("SKILL.md needs YAML frontmatter")
        else:
            keys = set(re.findall(r"^([a-z][a-z_-]*):", parts[1], re.MULTILINE))
            allowed = {"name", "description", "license", "compatibility", "metadata"}
            if keys - allowed or not {"name", "description"} <= keys:
                errors.append(f"nonportable or missing skill metadata keys: {sorted(keys)}")
            if not re.search(r"^name: port-any-game-anywhere$", parts[1], re.MULTILINE):
                errors.append("skill name must match its folder")
        if len(text.splitlines()) > 250:
            errors.append("main skill exceeds the 250-line project budget")
    return errors

def main():
    errors = check(source_files())
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print("PASS: repository syntax, local links, portable skill, and source boundaries")
    print("LIMIT: pattern checks do not replace license or secret review")
    return 0

if __name__ == "__main__":
    sys.exit(main())
