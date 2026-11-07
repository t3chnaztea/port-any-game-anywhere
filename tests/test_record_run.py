"""Behavioral checks for evidence recording, including unsafe green outcomes."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / "skills/port-any-game-anywhere/scripts"
sys.path.insert(0, str(SCRIPTS))
import record_run  # noqa: E402


class HelperFixture:
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="port evidence ")
        self.base = Path(self.temp.name)
        self.addCleanup(self.temp.cleanup)
        self.env_name = "PAGAA_TEST_SELECTED_ENV"
        old_value = os.environ.get(self.env_name)
        os.environ.pop(self.env_name, None)

        def restore_env():
            if old_value is None:
                os.environ.pop(self.env_name, None)
            else:
                os.environ[self.env_name] = old_value

        self.addCleanup(restore_env)
        for name in ("source.txt", "reference.txt", "asset.txt", "config.txt"):
            (self.base / name).write_text(name + " baseline\n", encoding="utf-8")
        self.script = self.base / "fixture.py"
        self.script.write_text("from pathlib import Path\nprint('assertion passed')\nPath('artifact.txt').write_text('actual state')\n")
        self.manifest_path = self.base / "run.json"
        self.output = self.base / "evidence.json"
        self.manifest = {
            "schema_version": 1, "id": "save-001", "claim_ids": ["save.reload"],
            "profile": "original", "target": "desktop", "evidence_class": "fixture-test",
            "command": {"argv": [sys.executable, "fixture.py"], "cwd": ".",
                        "timeout_seconds": 10, "output_limit_bytes": 1048576},
            "inputs": [{"role": role, "path": path} for role, path in [
                ("source", "source.txt"), ("reference", "reference.txt"), ("asset", "asset.txt"),
                ("config", "config.txt"), ("fixture", "fixture.py")]],
            "tools": [{"path": sys.executable, "version_argv": [sys.executable, "--version"], "flags": []}],
            "environment": [self.env_name], "artifacts": ["artifact.txt"],
        }
        self.write_manifest()

    def write_manifest(self):
        self.manifest_path.write_text(json.dumps(self.manifest), encoding="utf-8")

    def run_record(self):
        self.write_manifest()
        return record_run.record_run(self.manifest_path, self.output)

    def fingerprint(self, path, role=None):
        file = self.base / path
        result = {"path": path, "sha256": hashlib.sha256(file.read_bytes()).hexdigest(), "size": file.stat().st_size}
        if role is not None:
            result["role"] = role
        return result


@unittest.skipUnless(os.name == "posix", "recording requires POSIX process groups")
class RecordRunTests(HelperFixture, unittest.TestCase):
    def test_pass_has_current_before_after_artifact_and_log(self):
        result = self.run_record()
        self.assertEqual("passed", result["status"])
        self.assertEqual(result["identity_before"], result["identity_after"])
        self.assertEqual(0, result["outcome"]["exit_code"])
        self.assertEqual("assertion passed\n", Path(f"{self.output}.log").read_text())
        self.assertEqual(self.fingerprint("artifact.txt")["sha256"], result["artifacts"][0]["sha256"])
        self.assertEqual(False, result["identity_before"]["environment"][self.env_name]["present"])
        self.assertEqual(1, len(result["tool_versions"]))
        self.assertFalse(Path(result["identity_before"]["files"][0]["path"]).is_absolute())

    def test_nonzero_is_failed_even_with_artifact(self):
        self.script.write_text("from pathlib import Path\nPath('artifact.txt').write_text('bad')\nraise SystemExit(4)\n")
        result = self.run_record()
        self.assertEqual("failed", result["status"])
        self.assertEqual(4, result["outcome"]["exit_code"])

    def test_changed_reference_during_command_never_passes(self):
        self.script.write_text("from pathlib import Path\nPath('reference.txt').write_text('changed')\nPath('artifact.txt').write_text('result')\n")
        result = self.run_record()
        self.assertEqual("failed", result["status"])
        self.assertNotEqual(result["identity_before"], result["identity_after"])
        self.assertTrue(any("changed during run" in error for error in result["errors"]))

    def test_missing_input_blocks_execution(self):
        (self.base / "asset.txt").unlink()
        result = self.run_record()
        self.assertEqual("blocked", result["status"])
        self.assertIsNone(result["started_at"])
        self.assertFalse((self.base / "artifact.txt").exists())

    def test_missing_required_artifact_never_passes(self):
        self.script.write_text("print('booted')\n")
        result = self.run_record()
        self.assertEqual("failed", result["status"])
        self.assertFalse(result["artifacts"][0]["exists"])

    def test_failed_tool_probe_blocks_main_command(self):
        self.manifest["tools"][0]["version_argv"] = [sys.executable, "-c", "raise SystemExit(3)"]
        result = self.run_record()
        self.assertEqual("blocked", result["status"])
        self.assertEqual(3, result["tool_versions"][0]["exit_code"])
        self.assertFalse((self.base / "artifact.txt").exists())

    def test_log_is_bounded_and_truncation_is_not_green(self):
        self.script.write_text("from pathlib import Path\nprint('x' * 10000)\nPath('artifact.txt').write_text('result')\n")
        self.manifest["command"]["output_limit_bytes"] = 128
        self.write_manifest()
        completed = subprocess.run([sys.executable, str(SCRIPTS / "record_run.py"), str(self.manifest_path),
                                    "--output", str(self.output)], text=True, capture_output=True, timeout=10)
        self.assertEqual(1, completed.returncode)
        self.assertLess(len(completed.stdout), 1000)
        self.assertEqual(128, Path(f"{self.output}.log").stat().st_size)
        result = json.loads(self.output.read_text())
        self.assertEqual("failed", result["status"])
        self.assertTrue(result["outcome"]["truncated"])

    def test_timeout_preserves_interrupted_record(self):
        self.script.write_text("import time\nprint('started', flush=True)\ntime.sleep(30)\n")
        self.manifest["command"]["timeout_seconds"] = 0.15
        result = self.run_record()
        self.assertEqual("interrupted", result["status"])
        self.assertEqual("timeout", result["outcome"]["termination_reason"])
        self.assertIn("started", Path(f"{self.output}.log").read_text())
        self.assertIsNotNone(result["finished_at"])

    def test_timeout_stops_a_spawned_descendant(self):
        self.script.write_text(
            "import subprocess, sys, time\n"
            "subprocess.Popen([sys.executable, '-c', \"import time; from pathlib import Path; time.sleep(0.8); Path('leaked-child.txt').write_text('escaped')\"])\n"
            "time.sleep(30)\n")
        self.manifest["command"]["timeout_seconds"] = 0.15
        result = self.run_record()
        self.assertEqual("interrupted", result["status"])
        time.sleep(0.9)
        self.assertFalse((self.base / "leaked-child.txt").exists(), "owned descendant must not survive timeout")

    def test_failure_to_save_running_state_stops_child_and_preserves_failure(self):
        from unittest import mock

        self.script.write_text("import time\ntime.sleep(0.8)\nfrom pathlib import Path\nPath('artifact.txt').write_text('escaped')\n")
        original = record_run.atomic_write
        writes = []

        def fail_once(path, value):
            writes.append(value["status"])
            if len(writes) == 1:
                raise OSError("simulated unavailable storage")
            original(path, value)

        with mock.patch.object(record_run, "atomic_write", side_effect=fail_once):
            result = self.run_record()
        self.assertEqual("failed", result["status"])
        self.assertFalse((self.base / "artifact.txt").exists())
        self.assertTrue(result["log"]["exists"])
        self.assertEqual("failed", json.loads(self.output.read_text())["status"])

    def test_existing_record_or_log_is_never_replaced(self):
        self.output.write_text("owned by previous run")
        with self.assertRaises(record_run.FormatError):
            self.run_record()
        self.assertEqual("owned by previous run", self.output.read_text())
        self.output.unlink()
        Path(f"{self.output}.log").write_text("old log")
        with self.assertRaises(record_run.FormatError):
            self.run_record()
        self.assertEqual("old log", Path(f"{self.output}.log").read_text())

    def test_arguments_are_literal_without_a_shell(self):
        marker = "literal; $(touch SHOULD_NOT_EXIST)"
        self.manifest["command"]["argv"] = [sys.executable, "-c", "import sys; print(sys.argv[1])", marker]
        self.manifest["artifacts"] = []
        result = self.run_record()
        self.assertEqual("passed", result["status"])
        self.assertEqual(marker + "\n", Path(f"{self.output}.log").read_text())
        self.assertFalse((self.base / "SHOULD_NOT_EXIST").exists())

    def test_selected_environment_values_are_hashed(self):
        os.environ[self.env_name] = "private test value"
        result = self.run_record()
        stored = result["identity_before"]["environment"][self.env_name]
        self.assertTrue(stored["present"])
        self.assertEqual(hashlib.sha256(b"private test value").hexdigest(), stored["sha256"])
        self.assertNotIn("private test value", self.output.read_text())

    def test_bad_schema_rejected_before_execution(self):
        for key, value in (("schema_version", 2), ("evidence_class", "target-device"),
                           ("evidence_class", []), ("id", "invalid\x00id")):
            manifest = dict(self.manifest)
            manifest[key] = value
            self.manifest_path.write_text(json.dumps(manifest))
            with self.subTest(key=key), self.assertRaises(record_run.FormatError):
                record_run.record_run(self.manifest_path, self.output)
            self.assertFalse(self.output.exists())

    def test_sigint_and_sigterm_preserve_record_and_only_stop_owned_group(self):
        self.script.write_text("import time\nprint('started', flush=True)\ntime.sleep(30)\n")
        self.write_manifest()
        other = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"], start_new_session=True)

        def stop_other():
            if other.poll() is None:
                other.terminate()
            other.wait(timeout=5)

        self.addCleanup(stop_other)
        for number in (signal.SIGINT, signal.SIGTERM):
            output = self.base / f"signal-{number}.json"
            proc = subprocess.Popen([sys.executable, str(SCRIPTS / "record_run.py"), str(self.manifest_path),
                                     "--output", str(output)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            try:
                deadline = time.monotonic() + 5
                observed = None
                while time.monotonic() < deadline:
                    if output.exists():
                        observed = json.loads(output.read_text())
                        if observed["status"] == "running":
                            break
                    time.sleep(0.01)
                self.assertIsNotNone(observed)
                self.assertEqual("running", observed["status"])
                proc.send_signal(number)
                stdout, stderr = proc.communicate(timeout=5)
                self.assertEqual(1, proc.returncode, (stdout, stderr))
                result = json.loads(output.read_text())
                self.assertEqual("interrupted", result["status"])
                self.assertIsNotNone(result["finished_at"])
                self.assertTrue(result["log"]["exists"])
                self.assertIsNone(other.poll(), "recorder must not stop unrelated jobs")
            finally:
                if proc.poll() is None:
                    proc.kill()
                    proc.communicate()
        other.terminate()
        other.wait(timeout=5)


if __name__ == "__main__":
    unittest.main()
