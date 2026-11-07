"""Archive boundary checks; a development bundle cannot silently be a release."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("build_release", ROOT / "tools/build_release.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

class ReleaseTests(unittest.TestCase):
    def test_development_archive_is_reproducible_and_self_contained(self):
        with tempfile.TemporaryDirectory() as tmp:
            a, b = Path(tmp) / "a.zip", Path(tmp) / "b.zip"
            self.assertEqual(MODULE.build(a, True), MODULE.build(b, True))
            with zipfile.ZipFile(a) as archive:
                names = archive.namelist()
                self.assertTrue(MODULE.PACKAGED_FILES <= {name.split('/', 1)[1] for name in names})
                self.assertTrue(all(name.startswith("port-any-game-anywhere/") and ".." not in Path(name).parts for name in names))
                self.assertFalse(any("private" in Path(name).parts or "__pycache__" in name for name in names))
                status = json.loads(archive.read("port-any-game-anywhere/BUILD-STATUS.json"))
                self.assertFalse(status["accepted_beta"])
                self.assertEqual(status["status"], "development")
                for row in archive.read("port-any-game-anywhere/SHA256SUMS.txt").decode().splitlines():
                    digest, name = row.split("  ", 1)
                    self.assertEqual(hashlib.sha256(archive.read("port-any-game-anywhere/" + name)).hexdigest(), digest)

    def test_release_refuses_development_version(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "release.zip"
            with self.assertRaisesRegex(ValueError, "development VERSION"):
                MODULE.build(target, False)
            self.assertFalse(target.exists())

    def test_archive_never_overwrites_an_existing_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "existing.zip"
            target.write_bytes(b"keep this")
            with self.assertRaises(FileExistsError):
                MODULE.build(target, True)
            self.assertEqual(target.read_bytes(), b"keep this")

    def test_ignored_environment_file_blocks_archive_admission(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = Path(tmp)
            (skill / '.env').write_text('PLACEHOLDER=value\n')
            with mock.patch.object(MODULE, 'SKILL', skill):
                with self.assertRaisesRegex(ValueError, 'unreviewed skill file'):
                    MODULE.payloads()

    def test_private_nested_file_blocks_archive_admission(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = Path(tmp)
            (skill / 'private').mkdir()
            (skill / 'private/notes.txt').write_text('synthetic private fixture')
            with mock.patch.object(MODULE, 'SKILL', skill):
                with self.assertRaisesRegex(ValueError, 'unreviewed skill file'):
                    MODULE.payloads()

if __name__ == "__main__":
    unittest.main()
