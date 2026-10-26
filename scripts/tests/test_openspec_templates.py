import tempfile
import unittest
from pathlib import Path
import subprocess
import sys
import importlib.util


ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "scripts" / "new-openspec-change.py"


class OpenSpecTemplateTests(unittest.TestCase):
    def test_proposal_rejects_list_prefixed_metadata(self):
        spec = importlib.util.spec_from_file_location('templates', TOOL)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'proposal.md'
            for field in ('模式', '状态'):
                path.write_text('模式: 标准\n状态: 待确认计划\n- ' + field + ': 标准\n')
                self.assertTrue(module.check_file(path, [], True), field)

    def run_tool(self, *args):
        return subprocess.run(
            [sys.executable, str(TOOL), *args], cwd=ROOT,
            text=True, capture_output=True,
        )

    def test_create_and_check_standard(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "change"
            created = self.run_tool("create", "sample-change", "--mode", "standard", "--target", str(target))
            self.assertEqual(0, created.returncode, created.stderr)
            self.assertFalse((target / "design.md").exists())
            proposal = target / "proposal.md"
            proposal.write_text(proposal.read_text().replace("{{WHY}}", "说明原因").replace("{{TITLE}}", "标题").replace("{{CHANGE}}", "变化").replace("{{IMPACT}}", "影响").replace("{{RISK}}", "风险").replace("{{INCLUDED}}", "范围").replace("{{EXCLUDED}}", "非范围").replace("{{ACCEPTANCE}}", "验收").replace("{{UNVERIFIED_SCOPE}}", "无").replace("{{RESIDUAL_RISK}}", "无"))
            for path in (target / "specs" / "sample-change").glob("spec.md"):
                path.write_text(path.read_text().replace("{{CAPABILITY}}", "能力").replace("{{REQUIREMENT}}", "要求").replace("{{REQUIREMENT_RULE}}", "满足要求").replace("{{SCENARIO}}", "场景").replace("{{WHEN}}", "条件").replace("{{THEN}}", "结果"))
            tasks = target / "tasks.md"
            tasks.write_text(tasks.read_text().replace("{{TASK}}", "任务").replace("{{PATH}}", "file.md").replace("{{COMMAND}}", "python3 check.py").replace("{{EXPECTED}}", "通过").replace("{{INTEGRATION}}", "feature 分支").replace("{{COMMIT_BOUNDARY}}", "职责单元").replace("{{SIDE_EFFECTS}}", "无"))
            checked = self.run_tool("check", str(target))
            self.assertEqual(0, checked.returncode, checked.stderr)

    def test_check_rejects_placeholder(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "change"
            self.run_tool("create", "sample-change", "--mode", "standard", "--target", str(target))
            checked = self.run_tool("check", str(target))
            self.assertNotEqual(0, checked.returncode)
            self.assertIn("占位符", checked.stderr)

    def test_create_rejects_nonempty_target(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "change"
            target.mkdir()
            (target / "existing").write_text("x")
            result = self.run_tool("create", "sample-change", "--mode", "standard", "--target", str(target))
            self.assertNotEqual(0, result.returncode)

    def test_create_requires_explicit_empty_target_and_is_transactional(self):
        result = self.run_tool("create", "sample-change", "--mode", "standard")
        self.assertNotEqual(0, result.returncode)
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "change"
            target.mkdir()
            (target / "old").write_text("x")
            result = self.run_tool("create", "sample-change", "--mode", "standard", "--target", str(target))
            self.assertNotEqual(0, result.returncode)
            self.assertEqual(["old"], [p.name for p in target.iterdir()])

    def test_create_rejects_symlink_target(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            real = root / "real"; real.mkdir()
            link = root / "link"; link.symlink_to(real, target_is_directory=True)
            result = self.run_tool("create", "sample-change", "--mode", "standard", "--target", str(link))
            self.assertNotEqual(0, result.returncode)
            self.assertFalse((real / "proposal.md").exists())

    def test_strict_requires_design_and_check_validates_content(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "change"
            created = self.run_tool("create", "sample-change", "--mode", "strict", "--target", str(target))
            self.assertEqual(0, created.returncode, created.stderr)
            self.assertTrue((target / "design.md").exists())
            checked = self.run_tool("check", str(target))
            self.assertNotEqual(0, checked.returncode)
            self.assertIn("占位符", checked.stderr)

    def test_check_templates_subcommand(self):
        result = self.run_tool("check-templates")
        self.assertEqual(0, result.returncode, result.stderr)


if __name__ == "__main__":
    unittest.main()
