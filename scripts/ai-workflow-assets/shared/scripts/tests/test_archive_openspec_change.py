import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts.archive_openspec_change import main, validate


class ArchiveOpenSpecChangeTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.changes = self.root / "openspec/changes"
        self.archive = self.root / "openspec/archive"
        self.specs = self.root / "openspec/specs"
        self.change = self.changes / "demo"
        (self.change / "specs/demo").mkdir(parents=True)
        (self.change / "proposal.md").write_text(
            "模式: 标准\n状态: 待归档\n\n# Demo\n", encoding="utf-8"
        )
        (self.change / "tasks.md").write_text(
            "# Tasks\n\n- [x] 1. done\n", encoding="utf-8"
        )
        (self.change / "review-findings.md").write_text(
            "finding 状态: 无\n未验证范围: 无\n残余风险: 无\n", encoding="utf-8"
        )
        (self.change / "specs/demo/spec.md").write_text(
            "## ADDED Requirements\n\n### Requirement: Demo\n系统 SHALL demo。\n",
            encoding="utf-8",
        )

    def test_validate_rejects_unchecked_tasks(self):
        (self.change / "tasks.md").write_text(
            "# Tasks\n\n- [ ] 1. pending\n", encoding="utf-8"
        )
        with mock.patch.multiple(
            "scripts.archive_openspec_change", CHANGES=self.changes, ARCHIVE=self.archive
        ):
            self.assertIsNone(validate(self.change))

    def test_validate_rejects_wrong_status(self):
        (self.change / "proposal.md").write_text(
            "模式: 标准\n状态: 待验证\n", encoding="utf-8"
        )
        self.assertIsNone(validate(self.change))

    def test_dry_run_does_not_move_change(self):
        with mock.patch.multiple(
            "scripts.archive_openspec_change", CHANGES=self.changes, ARCHIVE=self.archive
        ), mock.patch("sys.argv", ["archive-openspec-change.py", str(self.change), "--dry-run"]):
            self.assertEqual(main(), 0)
        self.assertTrue(self.change.is_dir())
        self.assertFalse(self.archive.exists())

    def test_archive_merges_spec_moves_directory_and_updates_index(self):
        readme = self.archive / "README.md"
        readme.parent.mkdir(parents=True)
        readme.write_text("# 归档变更索引\n", encoding="utf-8")
        with mock.patch.multiple(
            "scripts.archive_openspec_change",
            CHANGES=self.changes,
            ARCHIVE=self.archive,
            SPEC_ROOT=self.specs,
        ), mock.patch("sys.argv", ["archive-openspec-change.py", str(self.change)]):
            self.assertEqual(main(), 0)
        self.assertFalse(self.change.exists())
        destination = self.archive / "demo"
        self.assertTrue((destination / "proposal.md").is_file())
        self.assertIn("状态: 已归档", (destination / "proposal.md").read_text(encoding="utf-8"))
        self.assertTrue((self.specs / "demo/spec.md").is_file())
        self.assertIn("`demo`", readme.read_text(encoding="utf-8"))

    def test_archive_rejects_duplicate_destination(self):
        self.archive.mkdir(parents=True)
        (self.archive / "demo").mkdir()
        with mock.patch.multiple(
            "scripts.archive_openspec_change",
            CHANGES=self.changes,
            ARCHIVE=self.archive,
            SPEC_ROOT=self.specs,
        ), mock.patch("sys.argv", ["archive-openspec-change.py", str(self.change)]):
            self.assertEqual(main(), 1)
        self.assertTrue(self.change.is_dir())


if __name__ == "__main__":
    unittest.main()
