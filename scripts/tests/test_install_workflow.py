"""install-workflow.sh（bash 一键安装器）契约测试。

覆盖规格 openspec/specs/workflow-installer：一键安装（当前 .ai/ 布局）、
目标路径无效、用法错误、冲突防护、--force 备份、memory 永不覆盖。
空目标端到端用例同时是"布局迁移后安装器悬空引用"的回归捕获器。
"""
from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
INSTALLER = REPOSITORY_ROOT / "scripts" / "install-workflow.sh"

# 空目标安装后必须存在的代表性资产（跨三层：.ai 共享层、双运行时、校验套件）
REQUIRED_INSTALLED_PATHS = (
    ".ai/rules/index.md",
    ".ai/rules/review.md",
    ".ai/kb/overview.md",
    ".ai/memory/README.md",
    ".ai/tools/review_manifest.py",
    ".ai/prompts/agents/reviewer.md",
    "CLAUDE.md",
    "AGENTS.md",
    ".claude/skills/open/SKILL.md",
    ".codex/skills/open/SKILL.md",
    ".claude/agents/reviewer.md",
    ".codex/README.md",
    ".claude/ai-kb/README.md",
    ".codex/ai-kb/README.md",
    "openspec/project.md",
    "openspec/specs/risk-tiered-ai-workflow/spec.md",
    "scripts/validate-workflow.sh",
    "scripts/lib/validate-workflow-core.sh",
    "scripts/tests/test_validate_workflow.py",
)


def run_installer(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(INSTALLER), *arguments],
        cwd=REPOSITORY_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        timeout=300,
    )


class FreshInstallTests(unittest.TestCase):
    def test_fresh_install_succeeds(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "demo"
            target.mkdir()
            result = run_installer(str(target))
            combined = result.stdout + result.stderr
            self.assertEqual(result.returncode, 0, msg=combined)
            for rel in REQUIRED_INSTALLED_PATHS:
                self.assertTrue((target / rel).is_file(), msg=f"缺少资产: {rel}")
            # ai-kb 仅兼容重定向入口，不得出现旧布局平行正文目录
            self.assertFalse((target / ".claude/ai-kb/kb").exists(), msg=".claude/ai-kb/kb 不应被安装")
            self.assertFalse((target / ".codex/ai-kb/rules").exists(), msg=".codex/ai-kb/rules 不应被安装")
            # project.md 是通用占位版而非本仓库业务描述
            project_md = (target / "openspec/project.md").read_text(encoding="utf-8")
            self.assertIn("项目上下文", project_md)
            # .gitignore 标记块幂等落位（含 Python 缓存与草稿区规则）
            gitignore = (target / ".gitignore").read_text(encoding="utf-8")
            for rule in ("/.ai-local/", "/.worktrees/", "__pycache__/", "*.py[cod]"):
                self.assertIn(rule, gitignore, msg=f".gitignore 缺规则: {rule}")
            # 双运行时目标模型：不生成 profile、不随附便携安装器（源仓标记），
            # 装后自检为 --fast 秒级 core 校验
            self.assertFalse(
                (target / ".ai/assistant-profile.json").exists(),
                msg="双运行时安装不应生成 assistant-profile",
            )
            self.assertFalse(
                (target / "scripts/install-ai-workflow.sh").exists(),
                msg="双运行时安装不应随附便携安装器（源仓专属标记）",
            )
            self.assertIn("--fast", result.stdout, msg="装后自检应使用 --fast 分层")

    def test_invalid_target_exit2(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            missing = str(Path(tmp) / "definitely-missing")
            result = run_installer(missing)
            self.assertEqual(result.returncode, 2, msg=result.stdout + result.stderr)
            self.assertFalse(Path(missing).exists())


class UsageTests(unittest.TestCase):
    def test_no_args_exit2(self) -> None:
        result = run_installer()
        self.assertEqual(result.returncode, 2, msg=result.stdout + result.stderr)

    def test_help_exit2(self) -> None:
        result = run_installer("--help")
        self.assertEqual(result.returncode, 2, msg=result.stdout + result.stderr)
        self.assertIn("--force", result.stdout)


class ConflictTests(unittest.TestCase):
    def test_conflict_aborts_without_force(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "demo"
            target.mkdir()
            (target / "CLAUDE.md").write_text("既有总纲，不许覆盖\n", encoding="utf-8")
            result = run_installer(str(target))
            combined = result.stdout + result.stderr
            self.assertEqual(result.returncode, 1, msg=combined)
            self.assertIn("--force", combined)
            self.assertIn("CLAUDE.md", combined)
            # 目标既有文件原样保留
            self.assertEqual(
                (target / "CLAUDE.md").read_text(encoding="utf-8"),
                "既有总纲，不许覆盖\n",
            )


class LegacyLayoutTests(unittest.TestCase):
    def test_legacy_ai_kb_requires_force_then_backed_up(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "demo"
            target.mkdir()
            legacy = target / ".claude/ai-kb/kb"
            legacy.mkdir(parents=True)
            (legacy / "overview.md").write_text("迁移前旧正文\n", encoding="utf-8")
            # 无 --force：明确中止并指引用户
            result = run_installer(str(target))
            combined = result.stdout + result.stderr
            self.assertEqual(result.returncode, 1, msg=combined)
            self.assertIn("旧布局", combined)
            self.assertTrue((legacy / "overview.md").exists(), msg="无 --force 不得动用户文件")
            # --force：整目录备份后清除，重装重定向入口，自检全绿
            result = run_installer(str(target), "--force")
            combined = result.stdout + result.stderr
            self.assertEqual(result.returncode, 0, msg=combined)
            self.assertTrue(
                (target / ".claude/ai-kb.bak/kb/overview.md").is_file(),
                msg="旧正文应整体备份到 ai-kb.bak/",
            )
            self.assertTrue((target / ".claude/ai-kb/README.md").is_file(), msg="重定向入口应重装")
            self.assertFalse((target / ".claude/ai-kb/kb").exists(), msg="旧正文目录应已清除")


class ForceAndMemoryTests(unittest.TestCase):
    def test_force_backs_up_and_memory_survives(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "demo"
            target.mkdir()
            (target / ".ai/memory").mkdir(parents=True)
            (target / "CLAUDE.md").write_text("旧版总纲\n", encoding="utf-8")
            (target / ".ai/memory/workflow.md").write_text(
                "## 2026-01-01 · 用户自己的坑\n**坑**：业务踩坑\n**解**：业务解法\n",
                encoding="utf-8",
            )
            result = run_installer(str(target), "--force")
            combined = result.stdout + result.stderr
            self.assertEqual(result.returncode, 0, msg=combined)
            # 覆盖前备份为 <原名>.bak，内容是旧版
            self.assertTrue((target / "CLAUDE.md.bak").is_file(), msg="缺 CLAUDE.md.bak")
            self.assertEqual((target / "CLAUDE.md.bak").read_text(encoding="utf-8"), "旧版总纲\n")
            # memory 永不覆盖、不备份
            memory = target / ".ai/memory/workflow.md"
            self.assertIn("用户自己的坑", memory.read_text(encoding="utf-8"))
            self.assertFalse(memory.with_suffix(".md.bak").exists(), msg="memory 不得产生 .bak")


if __name__ == "__main__":
    unittest.main()
