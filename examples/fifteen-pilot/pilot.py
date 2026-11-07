#!/usr/bin/env python3
"""Offline-first reproduction of the pinned upstream Fifteen browser build."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import signal
import subprocess
import sys
import tarfile
import tempfile
import threading
import time
import urllib.request


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LOCK = json.loads((HERE / "source-lock.json").read_text())
DEFAULT_WORK = ROOT / ".work" / "fifteen"
MAX_DOWNLOAD = 10_000_000
MAX_UNPACKED = 64 * 1024 * 1024
MAX_LOG = 1024 * 1024
WEB_TOOLS = ("emcc", "emcmake", "cmake", "make", "perl")


class PilotError(Exception):
    """A failed prerequisite or a rejected input, never a game pass."""


def digest(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def verify_archive(path: Path, expected: dict = LOCK) -> None:
    if not path.is_file():
        raise PilotError("archive missing; use the explicit fetch command")
    if path.stat().st_size != expected["size"] or digest(path) != expected["sha256"]:
        raise PilotError("archive identity mismatch; refusing extraction or build")


def require_tools(names: tuple[str, ...]) -> None:
    missing = [name for name in names if shutil.which(name) is None]
    if missing:
        raise PilotError("missing tools: " + ", ".join(missing))


def preflight(work: Path) -> dict:
    tools = {name: shutil.which(name) is not None for name in WEB_TOOLS}
    archive = work / LOCK["archive"]
    archive_state = "absent"
    if archive.exists():
        try:
            verify_archive(archive)
            archive_state = "verified"
        except PilotError:
            archive_state = "mismatch"
    ready = all(tools.values()) and archive_state == "verified"
    return {
        "status": "ready-to-build" if ready else "blocked",
        "network_used": False,
        "tools": tools,
        "archive": archive_state,
        "gameplay_verified": False,
        "device_verified": False,
    }


def fetch(work: Path, allow_network: bool) -> Path:
    path = work / LOCK["archive"]
    if path.exists():
        verify_archive(path)
        return path
    if not allow_network:
        raise PilotError("network is off; fetch requires --allow-network")
    work.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(LOCK["url"], headers={"User-Agent": "FifteenReproduction/0.1"})
    with urllib.request.urlopen(request, timeout=30) as response:
        if response.url != LOCK["url"]:
            raise PilotError("unexpected download redirect")
        data = response.read(MAX_DOWNLOAD + 1)
    if len(data) > MAX_DOWNLOAD:
        raise PilotError("download exceeds size limit")
    with tempfile.NamedTemporaryFile(dir=work, prefix="archive-", delete=False) as temp:
        temporary = Path(temp.name)
        temp.write(data)
    try:
        verify_archive(temporary)
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)
    return path


def checked_members(archive: tarfile.TarFile, expected_root: str) -> list[tarfile.TarInfo]:
    members = archive.getmembers()
    if len(members) > 3000 or sum(item.size for item in members) > MAX_UNPACKED:
        raise PilotError("archive exceeds extraction limits")
    seen = set()
    for item in members:
        name = PurePosixPath(item.name)
        if (name.is_absolute() or ".." in name.parts or "\\" in item.name
                or not name.parts or name.parts[0] != expected_root
                or str(name) in seen or not (item.isdir() or item.isfile())):
            raise PilotError("unsafe or duplicate archive member")
        seen.add(str(name))
    return members


def verify_tree(archive_path: Path, destination: Path, expected_root: str) -> None:
    with tarfile.open(archive_path, "r:gz") as archive:
        members = checked_members(archive, expected_root)
        expected_files = set()
        for item in members:
            relative = PurePosixPath(item.name).relative_to(expected_root)
            path = destination.joinpath(*relative.parts)
            if destination.is_symlink() or path.is_symlink() or any(
                    destination.joinpath(*relative.parts[:i]).is_symlink()
                    for i in range(len(relative.parts))):
                raise PilotError("source tree contains a symlink")
            if item.isdir():
                if not path.is_dir():
                    raise PilotError("source directory missing")
            else:
                expected_files.add(path)
                if not path.is_file() or path.stat().st_size != item.size:
                    raise PilotError("source tree identity mismatch")
                expected = hashlib.sha256(archive.extractfile(item).read()).hexdigest()
                if digest(path) != expected:
                    raise PilotError("source tree identity mismatch")
        actual_files = {path for path in destination.rglob("*") if path.is_file() or path.is_symlink()}
        if actual_files != expected_files:
            raise PilotError("source tree contains extra files")


def extract_archive(archive_path: Path, work: Path, expected_root: str = LOCK["archive_root"]) -> Path:
    destination = work / expected_root
    if destination.exists() or destination.is_symlink():
        verify_tree(archive_path, destination, expected_root)
        return destination
    work.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive_path, "r:gz") as archive:
        members = checked_members(archive, expected_root)
        with tempfile.TemporaryDirectory(dir=work, prefix="extract-") as temporary:
            base = Path(temporary)
            for item in members:
                path = base.joinpath(*PurePosixPath(item.name).parts)
                if item.isdir():
                    path.mkdir(parents=True, exist_ok=True)
                else:
                    path.parent.mkdir(parents=True, exist_ok=True)
                    with archive.extractfile(item) as source, path.open("xb") as target:
                        shutil.copyfileobj(source, target)
            (base / expected_root).replace(destination)
    verify_tree(archive_path, destination, expected_root)
    return destination


def run_logged(argv: list[str], cwd: Path, log: Path, timeout: float = 180) -> None:
    """Run one owned process group. Cap its log and printed output."""
    errors = []
    truncated = []
    log.parent.mkdir(parents=True, exist_ok=True)
    if log.exists():
        raise PilotError("log already exists; choose a new build directory")
    with log.open("xb") as output:
        process = subprocess.Popen(argv, cwd=cwd, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT, start_new_session=True)

        def drain():
            total = 0
            try:
                while data := process.stdout.read(8192):
                    remaining = max(0, MAX_LOG - total)
                    output.write(data[:remaining])
                    total += len(data)
                    if total > MAX_LOG:
                        truncated.append(True)
            except OSError as error:
                errors.append(str(error))

        reader = threading.Thread(target=drain, daemon=True)
        reader.start()
        started = time.monotonic()
        try:
            while process.poll() is None:
                if errors or time.monotonic() - started > timeout:
                    raise PilotError("command interrupted by time or storage limit")
                time.sleep(0.05)
        except BaseException:
            os.killpg(process.pid, signal.SIGTERM)
            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
            raise
        finally:
            reader.join(timeout=3)
            if reader.is_alive():
                try:
                    os.killpg(process.pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
                reader.join(timeout=3)
            process.stdout.close()
        if reader.is_alive() or errors or truncated or process.returncode:
            raise PilotError("command failed or log incomplete; inspect the local log")


def build_web(work: Path) -> Path:
    require_tools(WEB_TOOLS)
    archive = work / LOCK["archive"]
    verify_archive(archive)
    source = extract_archive(archive, work)
    build = work / "build-web"
    site = work / "site"
    if build.exists() or site.exists():
        raise PilotError("build output exists; use a new --work-dir with the pinned archive")
    build.mkdir()
    run_logged(["emcmake", "cmake", "-S", str(source), "-B", str(build),
                "-DCMAKE_BUILD_TYPE=Release"], work, build / "configure.log")
    run_logged(["cmake", "--build", str(build), "--target", "fifteen", "--parallel", "1"],
               work, build / "compile.log")
    site.mkdir()
    run_logged(["perl", str(source / "html/jspage.pl"), str(HERE / "footer.html"),
                str(source / "html/fifteen.html")], site, build / "page.log")
    for name in ("fifteen.js", "fifteen.wasm"):
        path = build / name
        if not path.is_file():
            raise PilotError("expected browser output missing: " + name)
        shutil.copy2(path, site / name)
    page = site / "fifteen.html"
    html = page.read_text()
    html = html.replace('href="../doc/fifteen.html#fifteen"',
                        'href="https://www.chiark.greenend.org.uk/~sgtatham/puzzles/doc/fifteen.html"')
    html = html.replace('href="../"', 'href="https://www.chiark.greenend.org.uk/~sgtatham/puzzles/"')
    page.write_text(html)
    shutil.copy2(source / "LICENCE", site / "LICENCE")
    verify_tree(archive, source, LOCK["archive_root"])
    return site


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work-dir", type=Path, default=DEFAULT_WORK)
    parser.add_argument("action", nargs="?", default="preflight",
                        choices=("preflight", "fetch", "extract", "build-web"))
    parser.add_argument("--allow-network", action="store_true")
    args = parser.parse_args(argv)
    work = args.work_dir.resolve()
    def interrupted(_signum, _frame):
        raise KeyboardInterrupt
    signal.signal(signal.SIGTERM, interrupted)
    try:
        if args.action == "preflight":
            result = preflight(work)
            print(json.dumps(result, indent=2))
            return 0 if result["status"] == "ready-to-build" else 2
        if args.action == "fetch":
            fetch(work, args.allow_network)
            print("VERIFIED: pinned source archive; no game test performed")
        elif args.action == "extract":
            path = work / LOCK["archive"]
            verify_archive(path)
            extract_archive(path, work)
            print("VERIFIED: source tree matches pinned archive; no game test performed")
        else:
            build_web(work)
            print("BUILT: browser files; gameplay and device acceptance remain untested")
        return 0
    except (PilotError, OSError, tarfile.TarError) as error:
        print("BLOCKED: " + str(error), file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("INTERRUPTED: build acceptance remains open", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
