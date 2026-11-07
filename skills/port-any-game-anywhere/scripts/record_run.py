#!/usr/bin/env python3
"""Record one explicit command. A command pass is not a fidelity judgment."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import io
import json
import math
import os
from pathlib import Path
import selectors
import shutil
import signal
import subprocess
import sys
import tempfile
import time

SCHEMA_VERSION = 1
MACHINE_CLASSES = {"source-inspection", "fixture-test", "automated-gameplay", "emulator"}
EVIDENCE_CLASSES = MACHINE_CLASSES | {"target-device", "review"}
TERMINAL = {"passed", "failed", "interrupted", "blocked", "skipped"}
ROLES = {"source", "reference", "asset", "fixture", "config"}


class FormatError(ValueError):
    """Invalid manifest, record, or ledger."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise FormatError(message)


def nonempty(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip()) and "\x00" not in value


def one_of(value: object, choices: set[str]) -> bool:
    return isinstance(value, str) and value in choices


def string_list(value: object, *, empty: bool = True) -> bool:
    return (isinstance(value, list) and (empty or bool(value))
            and all(nonempty(item) for item in value)
            and len(value) == len(set(value)))


def load_json(path: Path) -> dict:
    try:
        with path.open(encoding="utf-8") as stream:
            value = json.load(stream)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise FormatError(f"Cannot read {path.name}: {exc}") from exc
    require(isinstance(value, dict), "JSON root must be an object")
    require(type(value.get("schema_version")) is int and value["schema_version"] == 1,
            "schema_version must be 1")
    return value


def common_fields(value: dict) -> None:
    for key in ("id", "profile", "target"):
        require(nonempty(value.get(key)), f"{key} must be a nonempty string")
    require(string_list(value.get("claim_ids"), empty=False),
            "claim_ids must be a nonempty list of unique strings")


def validate_manifest(value: dict) -> None:
    common_fields(value)
    require(one_of(value.get("evidence_class"), MACHINE_CLASSES),
            "machine evidence_class must be an inspection, fixture, gameplay, or emulator class")
    command = value.get("command")
    require(isinstance(command, dict), "command must be an object")
    # Repeated arguments are valid, unlike repeated IDs and paths.
    require(isinstance(command.get("argv"), list) and bool(command["argv"])
            and all(nonempty(arg) for arg in command["argv"]), "command.argv must be a nonempty string list")
    require(nonempty(command.get("cwd")), "command.cwd must be a path")
    timeout = command.get("timeout_seconds")
    require(type(timeout) in (int, float) and math.isfinite(timeout) and 0 < timeout <= 86400,
            "timeout_seconds must be greater than zero and at most 86400")
    limit = command.get("output_limit_bytes")
    require(type(limit) is int and 0 < limit <= 16 * 1024 * 1024,
            "output_limit_bytes must be 1 through 16777216")
    require(isinstance(value.get("inputs"), list), "inputs must be a list")
    paths = []
    for item in value["inputs"]:
        require(isinstance(item, dict) and one_of(item.get("role"), ROLES) and nonempty(item.get("path")),
                "each input needs a role and path")
        paths.append(item["path"])
    require(len(paths) == len(set(paths)), "input paths must be unique")
    require(isinstance(value.get("tools"), list), "tools must be a list")
    paths = []
    for tool in value["tools"]:
        require(isinstance(tool, dict) and nonempty(tool.get("path")), "tool needs a path")
        argv = tool.get("version_argv")
        require(isinstance(argv, list) and bool(argv) and all(nonempty(arg) for arg in argv)
                and argv[0] == tool["path"], "tool version_argv must start with its path")
        require(isinstance(tool.get("flags"), list) and all(isinstance(arg, str) for arg in tool["flags"]),
                "tool flags must be a string list")
        paths.append(tool["path"])
    require(len(paths) == len(set(paths)), "tool paths must be unique")
    require(string_list(value.get("environment")), "environment must list unique variable names")
    require(all("=" not in name and "\x00" not in name for name in value["environment"]),
            "environment names cannot contain '=' or NUL")
    require(string_list(value.get("artifacts")), "artifacts must list unique paths")


def absolute(path: str | Path, base: Path) -> Path:
    return Path(os.path.abspath(base / path))


def relative(path: Path, base: Path) -> str:
    return os.path.relpath(path, base)


def file_identity(path: Path, record_dir: Path, role: str | None = None) -> dict:
    result = {"path": relative(path, record_dir), "exists": False}
    if role is not None:
        result["role"] = role
    try:
        before = path.stat()
        if not path.is_file():
            result["error"] = "not a regular file"
            return result
        digest = hashlib.sha256()
        size = 0
        with path.open("rb") as stream:
            while chunk := stream.read(1024 * 1024):
                digest.update(chunk)
                size += len(chunk)
        after = path.stat()
        if (before.st_ino, before.st_size, before.st_mtime_ns) != (after.st_ino, after.st_size, after.st_mtime_ns):
            result["error"] = "changed while hashing"
            return result
        result.update(exists=True, sha256=digest.hexdigest(), size=size)
    except OSError as exc:
        result["error"] = f"{type(exc).__name__}: file unavailable"
    return result


def executable_path(requested: str, cwd: Path) -> Path:
    if os.sep in requested or (os.altsep and os.altsep in requested):
        return absolute(requested, cwd)
    found = shutil.which(requested)
    return absolute(found, cwd) if found else absolute(requested, cwd)


def environment_identity(names: list[str]) -> dict:
    result = {}
    for name in names:
        value = os.environ.get(name)
        result[name] = {"present": value is not None,
                        "sha256": hashlib.sha256(value.encode()).hexdigest() if value is not None else None}
    return result


def collect_identity(manifest: dict, manifest_path: Path, record_dir: Path) -> dict:
    base = manifest_path.parent
    cwd = absolute(manifest["command"]["cwd"], base)
    files = [file_identity(manifest_path, record_dir, "manifest")]
    files.extend(file_identity(absolute(item["path"], base), record_dir, item["role"])
                 for item in manifest["inputs"])
    tools = []
    for tool in manifest["tools"]:
        tools.append({"file": file_identity(executable_path(tool["path"], base), record_dir),
                      "requested": tool["path"], "version_argv": tool["version_argv"], "flags": tool["flags"]})
    producer = file_identity(Path(__file__).resolve(), record_dir)
    producer.pop("path", None)  # Identical installed copies are the same tool.
    producer["id"] = "record_run.py"
    return {"files": files, "tools": tools, "recording_tool": producer,
            "invoked_executable": file_identity(executable_path(manifest["command"]["argv"][0], cwd), record_dir),
            "environment": environment_identity(manifest["environment"])}


def identity_errors(identity: dict) -> list[str]:
    files = identity["files"] + [tool["file"] for tool in identity["tools"]] + [identity["invoked_executable"], identity["recording_tool"]]
    return [f"Missing or unstable identity: {item.get('path', item.get('id'))}" for item in files if not item.get("exists")]


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def atomic_write(path: Path, value: dict) -> None:
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         prefix=f".{path.name}.", suffix=".tmp", delete=False) as stream:
            temp_path = Path(stream.name)
            json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_path, path)
    finally:
        if temp_path is not None and temp_path.exists():
            temp_path.unlink()


def stop_group(proc: subprocess.Popen, sig: int) -> None:
    try:
        os.killpg(proc.pid, sig)
    except ProcessLookupError:
        pass


def run_child(argv: list[str], cwd: Path, timeout: float, limit: int, sink,
              interrupted: dict, on_start=None) -> dict:
    proc = subprocess.Popen(argv, cwd=cwd, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, start_new_session=True, shell=False)
    start = time.monotonic()
    stop_at = None
    reason = None
    written = 0
    truncated = False
    try:
        if on_start is not None:
            on_start(proc.pid)
        with selectors.DefaultSelector() as selector:
            selector.register(proc.stdout, selectors.EVENT_READ)
            while selector.get_map() or proc.poll() is None:
                now = time.monotonic()
                if stop_at is None and (interrupted.get("signal") or now - start >= timeout):
                    reason = "signal" if interrupted.get("signal") else "timeout"
                    stop_at = now
                    stop_group(proc, signal.SIGTERM)
                if stop_at is not None and now - stop_at >= 0.5:
                    stop_group(proc, signal.SIGKILL)
                # Close background descendants left by a finished command too.
                if proc.poll() is not None:
                    stop_group(proc, signal.SIGKILL)
                for key, _ in selector.select(timeout=0.05):
                    chunk = os.read(key.fileobj.fileno(), 65536)
                    if not chunk:
                        selector.unregister(key.fileobj)
                        continue
                    keep = chunk[:max(0, limit - written)]
                    if keep:
                        sink.write(keep)
                        sink.flush()
                        written += len(keep)
                    if len(keep) < len(chunk):
                        truncated = True
        return {"exit_code": proc.wait(), "termination_reason": reason,
                "truncated": truncated, "bytes": written}
    finally:
        stop_group(proc, signal.SIGKILL)
        proc.wait()
        if proc.stdout is not None:
            proc.stdout.close()


def record_run(manifest_path: Path, output_path: Path) -> dict:
    require(os.name == "posix", "recording requires Linux or macOS process groups")
    manifest_path = absolute(manifest_path, Path.cwd())
    output_path = absolute(output_path, Path.cwd())
    manifest = load_json(manifest_path)
    validate_manifest(manifest)
    require(output_path.parent.is_dir(), "output parent must already exist")
    log_path = Path(f"{output_path}.log")
    require(not output_path.exists() and not log_path.exists(), "record or log already exists; choose a new run ID")
    record = {"schema_version": 1, "record_type": "machine", "status": "pending",
              "created_at": utc_now(), "started_at": None, "finished_at": None,
              "manifest_path": relative(manifest_path, output_path.parent),
              **{key: manifest[key] for key in ("id", "claim_ids", "profile", "target", "evidence_class")},
              "command": manifest["command"], "identity_before": None, "identity_after": None,
              "tool_versions": [], "artifacts": [], "log": None,
              "outcome": None, "errors": []}
    # Reserve ownership before atomic lifecycle replacements.
    with output_path.open("x", encoding="utf-8") as stream:
        json.dump(record, stream)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    interrupted = {"signal": None}
    previous_handlers = {}

    def handle_signal(number, _frame):
        interrupted["signal"] = number

    for number in (signal.SIGINT, signal.SIGTERM):
        previous_handlers[number] = signal.signal(number, handle_signal)
    try:
        with log_path.open("xb") as log:
            before = collect_identity(manifest, manifest_path, output_path.parent)
            record["identity_before"] = before
            record["errors"].extend(identity_errors(before))
            cwd = absolute(manifest["command"]["cwd"], manifest_path.parent)
            if not cwd.is_dir():
                record["errors"].append("Command working directory is unavailable")
            if not record["errors"]:
                for tool in manifest["tools"]:
                    argv = [str(executable_path(tool["path"], manifest_path.parent)), *tool["version_argv"][1:]]
                    capture = io.BytesIO()
                    result = run_child(argv, manifest_path.parent, 5, 4096, capture, interrupted)
                    output = capture.getvalue()
                    record["tool_versions"].append({"path": tool["path"], "argv": tool["version_argv"],
                                                    "output": output.decode("utf-8", errors="replace"),
                                                    "sha256": hashlib.sha256(output).hexdigest(), **result})
                    if result["exit_code"] != 0 or result["termination_reason"] or result["truncated"]:
                        record["errors"].append(f"Tool version probe failed: {tool['path']}")
            if interrupted["signal"]:
                record["status"] = "interrupted"
                record["outcome"] = {"exit_code": None, "termination_reason": "signal",
                                     "signal": interrupted["signal"], "truncated": False, "bytes": 0}
            elif record["errors"]:
                record["status"] = "blocked"
            else:
                def started(pid):
                    record.update(status="running", started_at=utc_now(), child_pid=pid)
                    atomic_write(output_path, record)

                argv = [str(executable_path(manifest["command"]["argv"][0], cwd)), *manifest["command"]["argv"][1:]]
                result = run_child(argv, cwd, manifest["command"]["timeout_seconds"],
                                   manifest["command"]["output_limit_bytes"], log, interrupted, started)
                result["signal"] = interrupted["signal"]
                record["outcome"] = result
                if result["termination_reason"] or interrupted["signal"]:
                    record["status"] = "interrupted"
                elif result["exit_code"] != 0:
                    record["status"] = "failed"
                    record["errors"].append(f"Command exited {result['exit_code']}")
                elif result["truncated"]:
                    record["status"] = "failed"
                    record["errors"].append("Output exceeded durable log limit")
                else:
                    record["status"] = "passed"
            log.flush()
            os.fsync(log.fileno())
        after = collect_identity(manifest, manifest_path, output_path.parent)
        record["identity_after"] = after
        record["errors"].extend(identity_errors(after))
        if before != after:
            record["errors"].append("Input, tool, manifest, or environment identity changed during run")
        record["artifacts"] = [file_identity(absolute(path, manifest_path.parent), output_path.parent)
                               for path in manifest["artifacts"]]
        if record["status"] == "passed" and any(not item["exists"] for item in record["artifacts"]):
            record["errors"].append("Required artifact missing or unstable")
        record["log"] = file_identity(log_path, output_path.parent)
        if record["status"] == "passed" and record["errors"]:
            record["status"] = "failed"
    except (OSError, ValueError) as exc:
        record["status"] = "interrupted" if interrupted["signal"] else "failed"
        record["errors"].append(f"Recorder error: {type(exc).__name__}: {exc}")
    finally:
        if record["identity_before"] is not None and record["identity_after"] is None:
            record["identity_after"] = collect_identity(manifest, manifest_path, output_path.parent)
        if record["log"] is None and log_path.exists():
            record["log"] = file_identity(log_path, output_path.parent)
        if interrupted["signal"]:
            record["status"] = "interrupted"
        record["finished_at"] = utc_now()
        for number, handler in previous_handlers.items():
            signal.signal(number, handler)
        atomic_write(output_path, record)
    return record


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        result = record_run(args.manifest, args.output)
    except (FormatError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(f"{result['status'].upper()}: {result['id']} (command outcome only); record={args.output}")
    for error in result["errors"][:5]:
        print(f"  {error}")
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    sys.exit(main())
