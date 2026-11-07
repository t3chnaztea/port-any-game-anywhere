#!/usr/bin/env python3
"""Build an inspectable skill archive. Publication is a separate operation."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/port-any-game-anywhere"
PACKAGED_FILES = {
    "SKILL.md", "agents/openai.yaml",
    "adapters/console.md", "adapters/ghidra-linux-x86.md", "adapters/native-to-browser.md",
    "references/INDEX.md", "references/defect-loop.md", "references/efficient-agent-work.md",
    "references/intake-feasibility.md", "references/inventory-fidelity.md",
    "references/record-format.md", "references/source-recovery.md", "references/verification.md",
    "scripts/check_port.py", "scripts/record_run.py",
    "templates/bug.md", "templates/completion-ledger.json", "templates/coverage.md",
    "templates/handoff.md", "templates/manual-evidence.json", "templates/port-plan.md",
    "templates/release-audit.md", "templates/run-manifest.json", "templates/source-map.md",
}

def payloads():
    files = {}
    for path in SKILL.rglob("*"):
        if path.is_symlink():
            raise ValueError("skill archives cannot contain symlinks")
        if "__pycache__" in path.parts or path.suffix == ".pyc" or path.name == ".DS_Store":
            continue
        if path.is_file():
            relative = path.relative_to(SKILL).as_posix()
            if relative not in PACKAGED_FILES:
                raise ValueError(f"unreviewed skill file cannot enter archive: {relative}")
            files[str(Path("port-any-game-anywhere") / path.relative_to(SKILL))] = path.read_bytes()
    missing = PACKAGED_FILES - {name.split("/", 1)[1] for name in files}
    if missing:
        raise ValueError(f"required package files are missing: {', '.join(sorted(missing))}")
    files["port-any-game-anywhere/LICENSE"] = (ROOT / "LICENSE").read_bytes()
    return files

def build(destination, development):
    version = (ROOT / "VERSION").read_text().strip()
    if not re.fullmatch(r"\d+\.\d+\.\d+(?:-[a-z0-9.-]+)?", version):
        raise ValueError("invalid VERSION")
    if not development:
        if "-dev" in version:
            raise ValueError("development VERSION cannot be a release")
        subprocess.run([sys.executable, str(SKILL / "scripts/check_port.py"),
                        str(ROOT / "release-ledger.json"), "--require-complete"], check=True)
    files = payloads()
    files["port-any-game-anywhere/BUILD-STATUS.json"] = (json.dumps({
        "version": version, "status": "development" if development else "release",
        "accepted_beta": not development,
        "note": "Development archives do not close pilot, agent-evaluation, or device gates."
    }, indent=2, sort_keys=True) + "\n").encode()
    files["port-any-game-anywhere/SHA256SUMS.txt"] = "".join(
        f"{hashlib.sha256(data).hexdigest()}  {name.split('/', 1)[1]}\n"
        for name, data in sorted(files.items())).encode()
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination, "x", compression=zipfile.ZIP_STORED) as archive:
        for name, data in sorted(files.items()):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data)
    digest = hashlib.sha256(destination.read_bytes()).hexdigest()
    destination.with_suffix(destination.suffix + ".sha256").write_text(f"{digest}  {destination.name}\n")
    return digest

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    choice = parser.add_mutually_exclusive_group(required=True)
    choice.add_argument("--development", action="store_true")
    choice.add_argument("--release", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    version = (ROOT / "VERSION").read_text().strip()
    target = args.output or ROOT / "dist" / f"port-any-game-anywhere-{version}.zip"
    try:
        digest = build(target, args.development)
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        parser.exit(1, f"FAIL: archive not accepted: {exc}\n")
    print(f"PASS: {'development' if args.development else 'release'} archive {target.name} SHA-256 {digest}")

if __name__ == "__main__":
    main()
