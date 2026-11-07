#!/usr/bin/env python3
"""Validate a finite completion ledger and current evidence without executing it."""

from __future__ import annotations

import argparse
import datetime as dt
from pathlib import Path
import re
import sys

from record_run import (EVIDENCE_CLASSES, MACHINE_CLASSES, ROLES, TERMINAL,
                        FormatError, absolute, collect_identity, common_fields,
                        file_identity, identity_errors, load_json, nonempty,
                        one_of, require, string_list, validate_manifest)


def validate_ledger(value: dict) -> None:
    require(string_list(value.get("profiles"), empty=False), "profiles must be a nonempty unique string list")
    require(string_list(value.get("targets"), empty=False), "targets must be a nonempty unique string list")
    require(string_list(value.get("unknowns")), "ledger unknowns must be a string list")
    require(isinstance(value.get("claims"), list), "claims must be a list")
    ids = []
    for claim in value["claims"]:
        require(isinstance(claim, dict), "each claim must be an object")
        require(nonempty(claim.get("id")) and nonempty(claim.get("path")), "claim needs stable id and scenario path")
        require(claim.get("profile") in value["profiles"], "claim profile must belong to profiles")
        require(claim.get("target") in value["targets"], "claim target must belong to targets")
        require(type(claim.get("required")) is bool, "claim required must be boolean")
        require(one_of(claim.get("implementation"), {"pending", "implemented", "blocked"}), "invalid implementation state")
        require(one_of(claim.get("verification"), {"untested", "passed", "failed", "interrupted", "skipped", "blocked"}),
                "invalid verification state")
        required = claim.get("required_evidence")
        require(string_list(required, empty=False) and set(required) <= EVIDENCE_CLASSES,
                "required_evidence must name one or more distinct evidence classes")
        require(string_list(claim.get("evidence")), "evidence must list distinct record paths")
        require(string_list(claim.get("unknowns")), "claim unknowns must be a string list")
        ids.append(claim["id"])
    require(len(ids) == len(set(ids)), "claim ids must be unique")


def validate_fingerprint(item: dict, *, role: bool = False) -> None:
    require(isinstance(item, dict) and nonempty(item.get("path")), "fingerprint needs path")
    require(isinstance(item.get("sha256"), str) and re.fullmatch(r"[0-9a-f]{64}", item["sha256"]) is not None,
            "fingerprint needs lowercase SHA-256")
    require(type(item.get("size")) is int and item["size"] >= 0, "fingerprint needs nonnegative integer size")
    if role:
        require(one_of(item.get("role"), ROLES), "manual input needs a valid role")


def current_fingerprint(item: dict, base: Path) -> bool:
    validate_fingerprint(item)
    actual = file_identity(absolute(item["path"], base), base)
    return actual.get("exists") is True and all(actual.get(key) == item.get(key) for key in ("path", "sha256", "size"))


def check_machine(record: dict, path: Path) -> list[str]:
    require(one_of(record.get("evidence_class"), MACHINE_CLASSES), "a machine record cannot claim device or human review")
    require(one_of(record.get("status"), TERMINAL | {"pending", "running"}), "invalid machine status")
    if record["status"] != "passed":
        return [f"record status is {record['status']}"]
    require(record.get("errors") == [], "passed record has errors or lacks error list")
    outcome = record.get("outcome")
    require(isinstance(outcome, dict) and type(outcome.get("exit_code")) is int
            and outcome["exit_code"] == 0 and outcome.get("termination_reason") is None
            and outcome.get("signal") is None and outcome.get("truncated") is False,
            "passed record has no successful uninterrupted outcome")
    require(type(outcome.get("bytes")) is int and outcome["bytes"] >= 0,
            "passed record needs output byte count")
    require(nonempty(record.get("started_at")) and nonempty(record.get("finished_at")),
            "passed record needs lifecycle timestamps")
    require(nonempty(record.get("manifest_path")), "machine record needs manifest_path")
    manifest_path = absolute(record["manifest_path"], path.parent)
    manifest = load_json(manifest_path)
    validate_manifest(manifest)
    for key in ("id", "claim_ids", "profile", "target", "evidence_class", "command"):
        require(record.get(key) == manifest[key], f"record does not match current manifest: {key}")
    before, after = record.get("identity_before"), record.get("identity_after")
    require(isinstance(before, dict) and isinstance(after, dict), "passed record needs both identity snapshots")
    if before != after:
        return ["identities changed during run"]
    current = collect_identity(manifest, manifest_path, path.parent)
    issues = identity_errors(current)
    if before != current:
        issues.append("current input, executable, tool, flags, manifest, or environment identity is stale")
    versions = record.get("tool_versions")
    require(isinstance(versions, list) and len(versions) == len(manifest["tools"]),
            "passed record needs every declared tool version")
    for version, tool in zip(versions, manifest["tools"]):
        require(isinstance(version, dict) and version.get("path") == tool["path"]
                and version.get("argv") == tool["version_argv"] and version.get("exit_code") == 0
                and version.get("termination_reason") is None and version.get("truncated") is False
                and isinstance(version.get("output"), str)
                and isinstance(version.get("sha256"), str)
                and re.fullmatch(r"[0-9a-f]{64}", version["sha256"]) is not None,
                "tool version probe is incomplete or failed")
    artifacts = record.get("artifacts")
    require(isinstance(artifacts, list) and len(artifacts) == len(manifest["artifacts"]),
            "record must identify every declared artifact")
    for item, requested in zip(artifacts, manifest["artifacts"]):
        require(isinstance(item, dict) and nonempty(item.get("path")), "artifact needs a path")
        expected = absolute(requested, manifest_path.parent)
        require(absolute(item["path"], path.parent) == expected, "artifact path does not match manifest")
        if not current_fingerprint(item, path.parent):
            issues.append(f"artifact missing or stale: {item['path']}")
    log = record.get("log")
    require(isinstance(log, dict) and nonempty(log.get("path")), "passed record needs durable log")
    require(absolute(log["path"], path.parent) == Path(f"{path}.log"), "log path must belong to its record")
    require(log.get("size") == outcome["bytes"] <= manifest["command"]["output_limit_bytes"],
            "log size does not match bounded command output")
    if not current_fingerprint(log, path.parent):
        issues.append("durable log missing or stale")
    return issues


def check_manual(record: dict, path: Path) -> list[str]:
    require(one_of(record.get("evidence_class"), {"target-device", "review"}), "manual evidence must be device or review")
    require(one_of(record.get("status"), TERMINAL), "manual record needs a terminal status")
    for key in ("operator", "procedure", "observed_at"):
        require(nonempty(record.get(key)), f"manual record needs {key}")
    require(string_list(record.get("observations"), empty=False), "manual record needs actual observations")
    device = record.get("device")
    require(isinstance(device, dict), "manual record needs device object")
    for key in ("kind", "model", "identifier", "configuration"):
        require(nonempty(device.get(key)), f"manual device needs {key}")
    expected_kind = "physical" if record["evidence_class"] == "target-device" else "review"
    require(device["kind"] == expected_kind, "emulator or machine evidence cannot stand in for a physical device")
    try:
        observed_at = dt.datetime.fromisoformat(record["observed_at"].replace("Z", "+00:00"))
    except ValueError as exc:
        raise FormatError("observed_at must be an ISO 8601 timestamp") from exc
    require(observed_at.tzinfo is not None, "observed_at needs a timezone")
    issues = []
    for key in ("inputs", "artifacts"):
        items = record.get(key)
        require(isinstance(items, list) and bool(items), f"manual record needs nonempty {key}")
        for item in items:
            validate_fingerprint(item, role=key == "inputs")
            if not current_fingerprint(item, path.parent):
                issues.append(f"manual {key} missing or stale: {item['path']}")
    if record["status"] != "passed":
        issues.append(f"record status is {record['status']}")
    return issues


def check_record(path: Path, claim: dict) -> tuple[str | None, list[str], bool]:
    try:
        record = load_json(path)
        common_fields(record)
        require(one_of(record.get("evidence_class"), EVIDENCE_CLASSES), "unknown evidence class")
        require(claim["id"] in record["claim_ids"], "record does not include this claim id")
        require(record["profile"] == claim["profile"] and record["target"] == claim["target"],
                "record profile or target does not match claim")
        kind = record.get("record_type")
        require(one_of(kind, {"machine", "manual"}), "record_type must be machine or manual")
        issues = check_machine(record, path) if kind == "machine" else check_manual(record, path)
        return record["evidence_class"], issues, kind == "manual"
    except (FormatError, OSError, KeyError, TypeError, ValueError) as exc:
        return None, [f"invalid or unavailable record {path.name}: {exc}"], False


def evaluate(ledger_path: Path) -> dict:
    ledger_path = absolute(ledger_path, Path.cwd())
    ledger = load_json(ledger_path)
    validate_ledger(ledger)
    results = []
    groups = {}
    evidence_counts = {}
    for claim in ledger["claims"]:
        issues = []
        present = set()
        manual = False
        for requested in claim["evidence"]:
            evidence_class, record_issues, is_manual = check_record(absolute(requested, ledger_path.parent), claim)
            issues.extend(record_issues)
            manual |= is_manual
            if evidence_class is not None and not record_issues:
                present.add(evidence_class)
        if claim["implementation"] != "implemented":
            issues.append(f"implementation is {claim['implementation']}")
        if claim["verification"] != "passed":
            issues.append(f"verification is {claim['verification']}")
        if claim["unknowns"]:
            issues.append(f"{len(claim['unknowns'])} unknown(s)")
        missing = set(claim["required_evidence"]) - present
        if missing:
            issues.append("missing current passed evidence: " + ", ".join(sorted(missing)))
        satisfied = not issues
        result = {"id": claim["id"], "profile": claim["profile"], "target": claim["target"],
                  "required": claim["required"], "satisfied": satisfied, "issues": issues,
                  "unknowns": claim["unknowns"], "manual_assertion": manual}
        results.append(result)
        if claim["required"]:
            group = groups.setdefault((claim["profile"], claim["target"]), {"required": 0, "satisfied": 0})
            group["required"] += 1
            group["satisfied"] += int(satisfied)
            for evidence_class in claim["required_evidence"]:
                counts = evidence_counts.setdefault(evidence_class, {"required": 0, "current_passed": 0})
                counts["required"] += 1
                counts["current_passed"] += int(evidence_class in present)
    required = sum(item["required"] for item in results)
    satisfied = sum(item["required"] and item["satisfied"] for item in results)
    return {"complete": required > 0 and required == satisfied and not ledger["unknowns"],
            "required": required, "satisfied": satisfied, "unknowns": ledger["unknowns"],
            "claims": results, "groups": groups, "evidence_classes": evidence_counts}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ledger", type=Path)
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args()
    try:
        result = evaluate(args.ledger)
    except (FormatError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    label = "COMPLETE" if result["complete"] else "INCOMPLETE"
    print(f"{label}: {result['satisfied']}/{result['required']} required claims have current declared evidence")
    for (profile, target), counts in sorted(result["groups"].items()):
        print(f"  {profile}/{target}: {counts['satisfied']}/{counts['required']}")
    for evidence_class, counts in sorted(result["evidence_classes"].items()):
        print(f"  {evidence_class}: {counts['current_passed']}/{counts['required']} required claims have current passed records")
    if result["unknowns"]:
        print(f"  Ledger unknowns: {len(result['unknowns'])}")
    incomplete = [item for item in result["claims"] if not item["satisfied"]]
    for item in incomplete[:20]:
        status = "required" if item["required"] else "optional"
        print(f"  {item['id']} ({status}): {'; '.join(item['issues'][:3])}")
    if len(incomplete) > 20:
        print(f"  {len(incomplete) - 20} further incomplete claims remain in the ledger")
    if any(item["manual_assertion"] for item in result["claims"]):
        print("  Manual records: shape and file identity checked; human truth and device acceptance require review")
    print("  Evidence classes stay separate. This check does not judge test quality or game fidelity.")
    return 1 if args.require_complete and not result["complete"] else 0


if __name__ == "__main__":
    sys.exit(main())
