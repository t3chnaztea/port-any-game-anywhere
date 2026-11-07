#!/usr/bin/env python3
"""Build the original C and source-authored browser example. No installation."""
from pathlib import Path
import argparse
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples/recovery-puzzle"

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--native-only", action="store_true")
    args = parser.parse_args()
    output = ROOT / ".work/switchboard"
    output.mkdir(parents=True, exist_ok=True)
    compiler = shutil.which("clang")
    if not compiler:
        parser.exit(2, "BLOCKED: clang is required; no tools were installed\n")
    subprocess.run([compiler, "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
                    str(EXAMPLE / "reference/switchboard.c"), "-o", str(output / "switchboard")], check=True)
    if not args.native_only:
        tsc = EXAMPLE / "node_modules/typescript/bin/tsc"
        if not tsc.is_file():
            parser.exit(2, "BLOCKED: run npm ci --ignore-scripts in examples/recovery-puzzle\n")
        subprocess.run(["node", str(tsc)], cwd=EXAMPLE, check=True)
        site = output / "site"
        site.mkdir(exist_ok=True)
        for path in (EXAMPLE / ".work/web").glob("*.js"):
            shutil.copyfile(path, site / path.name)
        for name in ["index.html", "style.css"]:
            shutil.copyfile(EXAMPLE / "web" / name, site / name)
    print("PASS: source-authored Switchboard build (not recovery or device acceptance)")

if __name__ == "__main__":
    main()
