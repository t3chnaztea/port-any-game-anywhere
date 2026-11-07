"""No stale evidence, fixture, or emulator can close an unrelated gate."""

from __future__ import annotations

import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest import mock

from test_record_run import HelperFixture, SCRIPTS

sys.path.insert(0, str(SCRIPTS))
import check_port  # noqa: E402
import record_run  # noqa: E402


@unittest.skipUnless(os.name == "posix", "fixture recording requires POSIX")
class CheckPortTests(HelperFixture, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.record = self.run_record()
        self.assertEqual("passed", self.record["status"])
        self.ledger_path = self.base / "ledger.json"
        self.claim = {"id": "save.reload", "path": "Save, restart process, reload, continue",
                      "profile": "original", "target": "desktop", "required": True,
                      "implementation": "implemented", "verification": "passed",
                      "required_evidence": ["fixture-test"], "evidence": ["evidence.json"], "unknowns": []}
        self.ledger = {"schema_version": 1, "profiles": ["original", "enhanced"], "targets": ["desktop"],
                       "unknowns": [], "claims": [self.claim]}
        self.write_ledger()

    def write_ledger(self):
        self.ledger_path.write_text(json.dumps(self.ledger))

    def write_record(self, record=None):
        self.output.write_text(json.dumps(self.record if record is None else record))

    def evaluate(self):
        self.write_ledger()
        return check_port.evaluate(self.ledger_path)

    def assert_incomplete(self):
        result = self.evaluate()
        self.assertFalse(result["complete"])
        self.assertEqual(0, result["satisfied"])
        return result

    def test_current_run_closes_only_declared_fixture_gate(self):
        with mock.patch.object(subprocess, "Popen", side_effect=AssertionError("checker must not execute commands")):
            result = self.evaluate()
        self.assertTrue(result["complete"])
        self.assertEqual(1, result["required"])
        self.assertEqual({"required": 1, "current_passed": 1}, result["evidence_classes"]["fixture-test"])

    def test_changed_source_reference_asset_fixture_config_each_invalidates(self):
        for name in ("source.txt", "reference.txt", "asset.txt", "fixture.py", "config.txt"):
            path = self.base / name
            old = path.read_bytes()
            with self.subTest(name=name):
                path.write_bytes(old + b" changed")
                self.assert_incomplete()
                path.write_bytes(old)
                self.assertTrue(self.evaluate()["complete"])

    def test_missing_input_log_or_artifact_each_invalidates(self):
        for name in ("reference.txt", "evidence.json.log", "artifact.txt"):
            path = self.base / name
            old = path.read_bytes()
            with self.subTest(name=name):
                path.unlink()
                self.assert_incomplete()
                path.write_bytes(old)

    def test_modified_artifact_and_log_invalidate_pass(self):
        for name in ("evidence.json.log", "artifact.txt"):
            path = self.base / name
            old = path.read_bytes()
            with self.subTest(name=name):
                path.write_bytes(b"different output")
                self.assert_incomplete()
                path.write_bytes(old)

    def test_changed_command_tool_flags_and_environment_selection_invalidates(self):
        original = copy.deepcopy(self.manifest)
        mutations = [
            lambda m: m["command"]["argv"].append("changed"),
            lambda m: m["tools"][0]["flags"].append("-O2"),
            lambda m: m["tools"][0]["version_argv"].append("changed"),
            lambda m: m["environment"].append("ANOTHER_SELECTED_VARIABLE"),
        ]
        for mutation in mutations:
            self.manifest = copy.deepcopy(original)
            mutation(self.manifest)
            self.write_manifest()
            self.assert_incomplete()
        self.manifest = original
        self.write_manifest()

    def test_current_tool_executable_hash_change_invalidates(self):
        # A declared tool need not be the command interpreter.
        tool = self.base / "tool.py"
        tool.write_text("#!/usr/bin/env python3\nprint('version one')\n")
        tool.chmod(0o755)
        self.manifest["tools"] = [{"path": "tool.py", "version_argv": ["tool.py", "--version"], "flags": []}]
        self.output = self.base / "tool-evidence.json"
        self.run_record()
        self.claim["evidence"] = ["tool-evidence.json"]
        self.assertTrue(self.evaluate()["complete"])
        tool.write_text("#!/usr/bin/env python3\nprint('version two')\n")
        self.assert_incomplete()

    def test_env_absent_to_present_and_changed_value_invalidate(self):
        os.environ[self.env_name] = "new value"
        self.assert_incomplete()
        os.environ.pop(self.env_name)
        self.assertTrue(self.evaluate()["complete"])
        self.output = self.base / "env-evidence.json"
        os.environ[self.env_name] = "first"
        self.run_record()
        self.claim["evidence"] = ["env-evidence.json"]
        self.assertTrue(self.evaluate()["complete"])
        os.environ[self.env_name] = "second"
        self.assert_incomplete()
        os.environ.pop(self.env_name)
        self.assert_incomplete()

    def test_changed_before_after_record_cannot_be_promoted_to_pass(self):
        self.record["identity_after"]["files"][1]["sha256"] = "0" * 64
        self.write_record()
        self.assert_incomplete()

    def test_pending_running_failed_skipped_blocked_interrupted_never_count(self):
        for status in ("pending", "running", "failed", "skipped", "blocked", "interrupted"):
            with self.subTest(status=status):
                self.record["status"] = status
                self.write_record()
                self.assert_incomplete()

    def test_promoted_nonzero_timeout_or_truncated_outcome_is_rejected(self):
        original = copy.deepcopy(self.record)
        for key, value in (("exit_code", 7), ("termination_reason", "timeout"), ("signal", 2), ("truncated", True)):
            with self.subTest(key=key):
                self.record = copy.deepcopy(original)
                self.record["outcome"][key] = value
                self.write_record()
                self.assert_incomplete()

    def test_missing_tool_probe_cannot_count_as_pass(self):
        self.record["tool_versions"] = []
        self.write_record()
        self.assert_incomplete()

    def test_profile_target_claim_and_class_mismatches_never_count(self):
        original = copy.deepcopy(self.record)
        for key, value in (("profile", "enhanced"), ("target", "other-device"),
                           ("claim_ids", ["different.claim"]), ("evidence_class", "target-device")):
            with self.subTest(key=key):
                self.record = copy.deepcopy(original)
                self.record[key] = value
                self.write_record()
                self.assert_incomplete()

    def test_machine_emulator_cannot_satisfy_physical_device_gate(self):
        self.claim["required_evidence"] = ["fixture-test", "target-device"]
        result = self.assert_incomplete()
        self.assertEqual(0, result["evidence_classes"]["target-device"]["current_passed"])

    def test_malformed_ledger_and_record_are_not_completion(self):
        for mutation in (lambda l: l.update(schema_version=2),
                         lambda l: l["claims"][0].update(required=1),
                         lambda l: l["claims"][0].update(profile="undeclared"),
                         lambda l: l["claims"][0].update(verification=[]),
                         lambda l: l["claims"].append(copy.deepcopy(l["claims"][0]))):
            ledger = copy.deepcopy(self.ledger)
            mutation(ledger)
            self.ledger_path.write_text(json.dumps(ledger))
            with self.assertRaises(record_run.FormatError):
                check_port.evaluate(self.ledger_path)
        self.write_ledger()
        self.output.write_text('{"schema_version": 1, "record_type": "machine"}')
        self.assert_incomplete()

    def test_unknown_unimplemented_untested_and_no_required_claims_remain_visible(self):
        for key, value in (("implementation", "pending"), ("verification", "untested"), ("unknowns", ["audio unknown"])):
            old = self.claim[key]
            self.claim[key] = value
            result = self.assert_incomplete()
            self.assertTrue(result["claims"][0]["issues"])
            self.claim[key] = old
        self.ledger["unknowns"] = ["an ending may be missing"]
        self.assertFalse(self.evaluate()["complete"])
        self.ledger["unknowns"] = []
        self.claim["required"] = False
        result = self.evaluate()
        self.assertFalse(result["complete"])
        self.assertEqual(0, result["required"])

    def test_one_ledger_separates_enhancement_profile_denominators(self):
        extra = copy.deepcopy(self.claim)
        extra.update(id="save.reload.enhanced", profile="enhanced", evidence=[], verification="untested")
        self.ledger["claims"].append(extra)
        result = self.evaluate()
        self.assertEqual(2, result["required"])
        self.assertEqual(1, result["satisfied"])
        self.assertEqual(1, result["groups"][("original", "desktop")]["satisfied"])
        self.assertEqual(0, result["groups"][("enhanced", "desktop")]["satisfied"])

    def manual_record(self):
        return {"schema_version": 1, "record_type": "manual", "id": "device-001",
                "claim_ids": ["save.reload"], "profile": "original", "target": "desktop",
                "evidence_class": "target-device", "status": "passed", "operator": "Named tester",
                "device": {"kind": "physical", "model": "Example PC", "identifier": "test-device-1",
                           "configuration": "OS and controller configuration recorded by tester"},
                "observed_at": "2026-11-07T12:00:00+00:00", "procedure": "Save, restart process, reload",
                "observations": ["Observed the saved position after restart"],
                "inputs": [self.fingerprint("reference.txt", "reference")],
                "artifacts": [self.fingerprint("artifact.txt")]}

    def test_manual_shape_is_explicit_without_pretending_to_verify_truth(self):
        self.claim["required_evidence"] = ["fixture-test", "target-device"]
        self.claim["evidence"].append("manual.json")
        manual = self.manual_record()
        (self.base / "manual.json").write_text(json.dumps(manual))
        result = self.evaluate()
        self.assertTrue(result["complete"])
        self.assertTrue(result["claims"][0]["manual_assertion"])
        for mutation in (lambda m: m["device"].update(kind="emulator"),
                         lambda m: m.update(operator=""), lambda m: m.update(observed_at="not a date"),
                         lambda m: m.update(artifacts=[]), lambda m: m.update(status="skipped")):
            bad = copy.deepcopy(manual)
            mutation(bad)
            (self.base / "manual.json").write_text(json.dumps(bad))
            self.assert_incomplete()

    def test_require_complete_exit_codes_and_finite_summary(self):
        script = SCRIPTS / "check_port.py"
        self.claim["verification"] = "untested"
        self.write_ledger()
        normal = subprocess.run([sys.executable, str(script), str(self.ledger_path)], capture_output=True, text=True)
        strict = subprocess.run([sys.executable, str(script), str(self.ledger_path), "--require-complete"],
                                capture_output=True, text=True)
        self.assertEqual(0, normal.returncode)
        self.assertEqual(1, strict.returncode)
        self.assertIn("INCOMPLETE: 0/1", strict.stdout)
        self.assertIn("verification is untested", strict.stdout)
        self.ledger_path.write_text('{"schema_version": 88}')
        bad = subprocess.run([sys.executable, str(script), str(self.ledger_path)], capture_output=True, text=True)
        self.assertEqual(2, bad.returncode)


if __name__ == "__main__":
    unittest.main()
