"""Safety and bookkeeping tests. These do not exercise Fifteen gameplay."""

from contextlib import redirect_stdout, redirect_stderr
import hashlib
import io
from pathlib import Path
import sys
import tarfile
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pilot


class PilotTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.work = Path(self.temporary.name).resolve()
        self.addCleanup(self.temporary.cleanup)

    def archive(self, members):
        path = self.work / "source.tar.gz"
        with tarfile.open(path, "w:gz") as archive:
            for name, data, link in members:
                item = tarfile.TarInfo(name)
                if link:
                    item.type = tarfile.SYMTYPE
                    item.linkname = link
                    archive.addfile(item)
                else:
                    item.size = len(data)
                    archive.addfile(item, io.BytesIO(data))
        return path

    def test_archive_hash_mismatch_blocks(self):
        path = self.work / "archive"
        path.write_bytes(b"wrong")
        with self.assertRaisesRegex(pilot.PilotError, "identity mismatch"):
            pilot.verify_archive(path)

    def test_exact_archive_identity_is_accepted(self):
        path = self.work / "archive"
        path.write_bytes(b"controlled fixture")
        pilot.verify_archive(path, {"size": path.stat().st_size,
                                    "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})

    def test_fetch_is_offline_without_explicit_permission(self):
        with mock.patch.object(pilot.urllib.request, "urlopen") as request:
            with self.assertRaisesRegex(pilot.PilotError, "network is off"):
                pilot.fetch(self.work, False)
            request.assert_not_called()

    def test_bad_download_never_becomes_pinned_archive(self):
        response = mock.MagicMock()
        response.__enter__.return_value = response
        response.url = pilot.LOCK["url"]
        response.read.return_value = b"not the pinned archive"
        with mock.patch.object(pilot.urllib.request, "urlopen", return_value=response):
            with self.assertRaisesRegex(pilot.PilotError, "identity mismatch"):
                pilot.fetch(self.work, True)
        self.assertFalse((self.work / pilot.LOCK["archive"]).exists())
        self.assertEqual(list(self.work.iterdir()), [])

    def test_traversal_is_rejected_before_writing(self):
        path = self.archive([("demo/good", b"good", None), ("demo/../../escape", b"bad", None)])
        with self.assertRaisesRegex(pilot.PilotError, "unsafe"):
            pilot.extract_archive(path, self.work, "demo")
        self.assertFalse((self.work / "demo").exists())
        self.assertFalse((self.work.parent / "escape").exists())

    def test_symlink_is_rejected(self):
        path = self.archive([("demo/link", b"", "../../escape")])
        with self.assertRaisesRegex(pilot.PilotError, "unsafe"):
            pilot.extract_archive(path, self.work, "demo")

    def test_duplicate_members_are_rejected(self):
        path = self.archive([("demo/file", b"a", None), ("demo/file", b"b", None)])
        with self.assertRaisesRegex(pilot.PilotError, "duplicate"):
            pilot.extract_archive(path, self.work, "demo")

    def test_modified_extraction_cannot_be_reused(self):
        path = self.archive([("demo/file", b"original", None)])
        destination = pilot.extract_archive(path, self.work, "demo")
        (destination / "file").write_text("changed")
        with self.assertRaisesRegex(pilot.PilotError, "identity mismatch"):
            pilot.extract_archive(path, self.work, "demo")

    def test_extra_source_file_blocks_reuse(self):
        path = self.archive([("demo/file", b"original", None)])
        destination = pilot.extract_archive(path, self.work, "demo")
        (destination / "extra").write_text("unexpected")
        with self.assertRaisesRegex(pilot.PilotError, "extra files"):
            pilot.extract_archive(path, self.work, "demo")

    def test_missing_tools_block_without_build(self):
        with mock.patch.object(pilot.shutil, "which", return_value=None):
            with mock.patch.object(pilot, "run_logged") as runner:
                with self.assertRaisesRegex(pilot.PilotError, "missing tools"):
                    pilot.build_web(self.work)
                runner.assert_not_called()

    def test_default_preflight_uses_no_network_or_subprocess(self):
        with mock.patch.object(pilot.shutil, "which", return_value=None):
            with mock.patch.object(pilot.urllib.request, "urlopen") as request:
                with mock.patch.object(pilot.subprocess, "Popen") as process:
                    with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                        self.assertEqual(pilot.main(["--work-dir", str(self.work)]), 2)
                    request.assert_not_called()
                    process.assert_not_called()
        self.assertEqual(list(self.work.iterdir()), [])

    def test_failing_command_is_not_success(self):
        with self.assertRaisesRegex(pilot.PilotError, "command failed"):
            pilot.run_logged([sys.executable, "-c", "raise SystemExit(7)"],
                             self.work, self.work / "failed.log", timeout=3)

    def test_successful_command_preserves_complete_log(self):
        pilot.run_logged([sys.executable, "-c", "print('controlled result')"],
                         self.work, self.work / "success.log", timeout=3)
        self.assertEqual((self.work / "success.log").read_text(), "controlled result\n")

    def test_timeout_stops_owned_command(self):
        with self.assertRaisesRegex(pilot.PilotError, "interrupted"):
            pilot.run_logged([sys.executable, "-c", "import time;time.sleep(10)"],
                             self.work, self.work / "timeout.log", timeout=0.1)

    def test_output_cap_prevents_success(self):
        with self.assertRaisesRegex(pilot.PilotError, "log incomplete"):
            pilot.run_logged([sys.executable, "-c", "print('x' * 1100000)"],
                             self.work, self.work / "output.log", timeout=3)
        self.assertEqual((self.work / "output.log").stat().st_size, pilot.MAX_LOG)


if __name__ == "__main__":
    unittest.main()
