from __future__ import annotations

import dataclasses
import hashlib
import importlib.util
import json
import os
import re
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
import unicodedata
from unittest import mock


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
INSTALLER = REPOSITORY_ROOT / "scripts" / "install-ai-workflow.sh"
INSTALLER_MODULE = REPOSITORY_ROOT / "scripts" / "lib" / "install_ai_workflow.py"
ASSET_ROOT = REPOSITORY_ROOT / "scripts" / "ai-workflow-assets"

# 命令白名单唯一来源是 core 的 --print-external-commands;解析 helper 复用契约套件定义。
from scripts.tests.test_validate_workflow import _core_external_commands  # noqa: E402

SKILL_NAMES = (
    "archive", "build", "code-review", "design", "git-worktrees", "open",
    "parallel-agents", "subagent-driven", "systematic-debugging", "tdd",
    "verification", "verify", "writing-skills",
)

EXPECTED_ASSET_PATHS = {
    "shared": (
        ".ai/README.md", ".ai/kb/README.md", ".ai/kb/overview.md",
        ".ai/kb/projects/README.md", ".ai/kb/projects/registry.json",
        ".ai/kb/repository-ignore-rules.md", ".ai/memory/README.md",
        ".ai/prompts/agents/explorer.md", ".ai/prompts/agents/reviewer.md",
        ".ai/prompts/agents/test-worker.md", ".ai/rules/index.md",
        ".ai/rules/review.md", ".ai/tools/README.md",
        ".ai/tools/project_facts.py", ".ai/tools/review_manifest.py",
        ".ai/tools/tests/__init__.py", ".ai/tools/tests/test_project_facts.py",
        ".ai/tools/tests/test_review_manifest.py", "openspec/AGENTS.md",
        "openspec/archive/.gitkeep", "openspec/changes/.gitkeep",
        "openspec/plan/.gitkeep", "openspec/project.md", "openspec/specs/.gitkeep",
        "openspec/specs/risk-tiered-ai-workflow/spec.md",
        "openspec/specs/shared-ai-workflow-infrastructure/spec.md",
        "scripts/lib/validate-workflow-core.sh", "scripts/tests/__init__.py",
        "scripts/tests/test_validate_workflow.py", "scripts/validate-workflow.sh",
        "scripts/workflow-pressure-scenarios.md",
    ),
    "codex": (
        ".codex/README.md", ".codex/agents/explorer.toml",
        ".codex/agents/reviewer.toml", ".codex/agents/test_worker.toml",
        ".codex/ai-kb/README.md", ".codex/sdd/.gitkeep", "AGENTS.md",
        *(f".codex/skills/{name}/SKILL.md" for name in SKILL_NAMES),
    ),
    "claude": (
        ".claude/agents/explorer.md", ".claude/agents/reviewer.md",
        ".claude/agents/test-worker.md", ".claude/ai-kb/README.md",
        ".claude/sdd/.gitkeep", "CLAUDE.md",
        *(f".claude/skills/{name}/SKILL.md" for name in SKILL_NAMES),
    ),
}


def load_installer_module():
    if not INSTALLER_MODULE.is_file():
        raise AssertionError(f"installer module is missing: {INSTALLER_MODULE}")
    spec = importlib.util.spec_from_file_location("install_ai_workflow", INSTALLER_MODULE)
    if spec is None or spec.loader is None:
        raise AssertionError("installer module cannot be loaded")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def run_installer(*arguments: str, env: dict[str, str] | None = None):
    return subprocess.run(
        ["bash", str(INSTALLER), *arguments],
        cwd=REPOSITORY_ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def run_source_installer(source_root: Path, *arguments: str):
    module_path = source_root / "scripts" / "lib" / "install_ai_workflow.py"
    module_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(INSTALLER_MODULE, module_path)
    return subprocess.run(
        [sys.executable, "-B", str(module_path), *arguments],
        cwd=REPOSITORY_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def create_source(root: Path) -> Path:
    source_root = root / "source"
    asset_root = source_root / "scripts" / "ai-workflow-assets"
    entries = {
        "shared": [(".ai/README.md", b"shared\n", "0644")],
        "codex": [("AGENTS.md", b"codex\n", "0644")],
        "claude": [("CLAUDE.md", b"claude\n", "0644")],
    }
    manifest: dict[str, object] = {"schema_version": 1}
    for group, group_entries in entries.items():
        manifest[group] = [
            {"path": path, "mode": mode} for path, _content, mode in group_entries
        ]
        for path, content, _mode in group_entries:
            destination = asset_root / group / Path(*path.split("/"))
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(content)
    (asset_root / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    return source_root


def snapshot_tree(root: Path):
    snapshot: dict[str, tuple[object, ...]] = {}
    paths = [root, *sorted(root.rglob("*"), key=lambda path: os.fsencode(str(path)))]
    for path in paths:
        relative = "." if path == root else path.relative_to(root).as_posix()
        metadata = path.lstat()
        common = (stat.S_IFMT(metadata.st_mode), metadata.st_mode & 0o7777,
                  metadata.st_mtime_ns, metadata.st_ino)
        if stat.S_ISREG(metadata.st_mode):
            snapshot[relative] = (*common, path.read_bytes())
        elif stat.S_ISLNK(metadata.st_mode):
            snapshot[relative] = (*common, os.readlink(path))
        else:
            snapshot[relative] = common
    return snapshot


def logical_snapshot_tree(root: Path):
    snapshot: dict[str, tuple[object, ...]] = {}
    paths = [root, *sorted(root.rglob("*"), key=lambda path: os.fsencode(str(path)))]
    for path in paths:
        relative = "." if path == root else path.relative_to(root).as_posix()
        metadata = path.lstat()
        common = (stat.S_IFMT(metadata.st_mode), stat.S_IMODE(metadata.st_mode))
        if stat.S_ISREG(metadata.st_mode):
            snapshot[relative] = (*common, path.read_bytes())
        elif stat.S_ISLNK(metadata.st_mode):
            snapshot[relative] = (*common, os.readlink(path))
        else:
            snapshot[relative] = common
    return snapshot


def identity_snapshot_tree(root: Path):
    snapshot: dict[str, tuple[object, ...]] = {}
    paths = [root, *sorted(root.rglob("*"), key=lambda path: os.fsencode(str(path)))]
    for path in paths:
        relative = "." if path == root else path.relative_to(root).as_posix()
        metadata = path.lstat()
        common = (
            stat.S_IFMT(metadata.st_mode), stat.S_IMODE(metadata.st_mode),
            metadata.st_mtime_ns, metadata.st_ino,
        )
        if stat.S_ISREG(metadata.st_mode):
            snapshot[relative] = (*common, hashlib.sha256(path.read_bytes()).hexdigest())
        elif stat.S_ISLNK(metadata.st_mode):
            snapshot[relative] = (*common, os.readlink(path))
        else:
            snapshot[relative] = common
    return snapshot


def execute_plan(testcase, module, plan, dry_run=False):
    testcase.assertTrue(
        hasattr(module, "execute_plan"),
        "transactional execute_plan behavior is not implemented",
    )
    return module.execute_plan(plan, dry_run=dry_run)


def managed_block(assistant: str) -> bytes:
    return (
        "# >>> portable-ai-workflow installer >>>\n"
        "/.ai-local/\n"
        f"/.{assistant}/sdd/\n"
        "__pycache__/\n"
        "*.py[cod]\n"
        "# <<< portable-ai-workflow installer <<<\n"
    ).encode("utf-8")


class PortableAssetManifestTests(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads((ASSET_ROOT / "manifest.json").read_text(encoding="utf-8"))

    def test_manifest_exactly_enumerates_sorted_physical_assets(self):
        self.assertEqual(set(self.manifest), {"schema_version", "shared", "codex", "claude"})
        self.assertEqual(self.manifest["schema_version"], 1)
        for group, expected in EXPECTED_ASSET_PATHS.items():
            paths = tuple(entry["path"] for entry in self.manifest[group])
            self.assertEqual(paths, tuple(sorted(expected, key=os.fsencode)), group)
            physical = tuple(sorted((path.relative_to(ASSET_ROOT / group).as_posix() for path in (ASSET_ROOT / group).rglob("*") if path.is_file()), key=os.fsencode))
            self.assertEqual(physical, paths, group)

    def test_manifest_modes_are_exact_and_match_files(self):
        executable = {"scripts/validate-workflow.sh", "scripts/lib/validate-workflow-core.sh"}
        for group in EXPECTED_ASSET_PATHS:
            for entry in self.manifest[group]:
                expected = "0755" if group == "shared" and entry["path"] in executable else "0644"
                self.assertEqual(entry, {"path": entry["path"], "mode": expected})
                self.assertEqual(stat.S_IMODE((ASSET_ROOT / group / entry["path"]).stat().st_mode), int(expected, 8))


class PortableAssetContentTests(unittest.TestCase):
    def asset_bytes(self, relative):
        path = ASSET_ROOT / relative
        self.assertTrue(path.is_file(), f"missing asset: {relative}")
        return path.read_bytes()

    def asset_text(self, relative):
        return self.asset_bytes(relative).decode("utf-8")

    def test_reusable_assets_are_byte_synchronized_with_active_sources(self):
        mappings = {
            "shared/.ai/prompts/agents/explorer.md": ".ai/prompts/agents/explorer.md",
            "shared/.ai/prompts/agents/reviewer.md": ".ai/prompts/agents/reviewer.md",
            "shared/.ai/prompts/agents/test-worker.md": ".ai/prompts/agents/test-worker.md",
            "shared/.ai/rules/review.md": ".ai/rules/review.md",
            "shared/.ai/tools/project_facts.py": ".ai/tools/project_facts.py",
            "shared/.ai/tools/review_manifest.py": ".ai/tools/review_manifest.py",
            "shared/.ai/tools/tests/__init__.py": ".ai/tools/tests/__init__.py",
            "shared/.ai/tools/tests/test_project_facts.py": ".ai/tools/tests/test_project_facts.py",
            "shared/.ai/tools/tests/test_review_manifest.py": ".ai/tools/tests/test_review_manifest.py",
            "shared/scripts/validate-workflow.sh": "scripts/validate-workflow.sh",
            "shared/scripts/lib/validate-workflow-core.sh": "scripts/lib/validate-workflow-core.sh",
            "shared/scripts/tests/__init__.py": "scripts/tests/__init__.py",
            "shared/scripts/tests/test_validate_workflow.py": "scripts/tests/test_validate_workflow.py",
            "shared/scripts/workflow-pressure-scenarios.md": "scripts/workflow-pressure-scenarios.md",
        }
        for assistant, suffix, source_prefix in (("codex", ".toml", ".codex"), ("claude", ".md", ".claude")):
            names = ("explorer", "reviewer", "test_worker") if assistant == "codex" else ("explorer", "reviewer", "test-worker")
            for name in names:
                mappings[f"{assistant}/.{assistant}/agents/{name}{suffix}"] = f"{source_prefix}/agents/{name}{suffix}"
            for name in SKILL_NAMES:
                mappings[f"{assistant}/.{assistant}/skills/{name}/SKILL.md"] = f"{source_prefix}/skills/{name}/SKILL.md"
        for packaged, active in mappings.items():
            with self.subTest(packaged=packaged):
                self.assertEqual(self.asset_bytes(packaged), (REPOSITORY_ROOT / active).read_bytes())

    def test_templates_exclude_source_business_and_local_state(self):
        deny = (b"--workspace /projects", b"`/projects", b"willing-sign", b"yuxiaor", b"pms-hpc", b"e-signature", b"com.dream", b"com.yuxiaor", b"install-portable-ai-workflow")
        for path in ASSET_ROOT.rglob("*"):
            if path.is_file() and path.name != "manifest.json":
                lowered = path.read_bytes().lower()
                for token in deny:
                    self.assertNotIn(token, lowered, f"{token!r} leaked in {path}")

    def test_empty_baselines_and_registry_have_no_project_state(self):
        registry = json.loads(self.asset_text("shared/.ai/kb/projects/registry.json"))
        self.assertEqual(registry, {"schema_version": 1, "projects": []})
        for group, relative in (("shared", "openspec/archive/.gitkeep"), ("shared", "openspec/changes/.gitkeep"), ("shared", "openspec/plan/.gitkeep"), ("shared", "openspec/specs/.gitkeep"), ("codex", ".codex/sdd/.gitkeep"), ("claude", ".claude/sdd/.gitkeep")):
            self.assertEqual(self.asset_bytes(f"{group}/{relative}"), b"")
        paths = {path.relative_to(ASSET_ROOT).as_posix() for path in ASSET_ROOT.rglob("*") if path.is_file()}
        self.assertFalse(any(any(fragment in path for fragment in ("kb/contracts/", ".ai-local/", "openspec/changes/archive/")) for path in paths))
        self.assertEqual([path for path in paths if "/.ai/memory/" in path], ["shared/.ai/memory/README.md"])

    def test_json_frontmatter_and_legacy_references_are_valid(self):
        for path in ASSET_ROOT.rglob("*.json"):
            json.loads(path.read_text(encoding="utf-8"))
        for assistant in ("codex", "claude"):
            for name in SKILL_NAMES:
                content = self.asset_text(f"{assistant}/.{assistant}/skills/{name}/SKILL.md")
                self.assertTrue(content.startswith("---\nname:"), name)
                self.assertGreaterEqual(content.count("---\n"), 2, name)
        for root_name in ("codex/AGENTS.md", "claude/CLAUDE.md"):
            content = self.asset_text(root_name)
            for phrase in ("快速", "标准", "严格", "openspec/changes", ".ai/rules/index.md"):
                self.assertIn(phrase, content, root_name)
        for path in ASSET_ROOT.rglob("*.md"):
            text = path.read_text(encoding="utf-8")
            self.assertNotIn(".codex/ai-kb/rules", text, str(path))
            self.assertNotIn(".claude/ai-kb/rules", text, str(path))
            packaged = path.relative_to(ASSET_ROOT)
            group = packaged.parts[0]
            relative = Path(*packaged.parts[1:])
            available = set(EXPECTED_ASSET_PATHS["shared"]) | set(EXPECTED_ASSET_PATHS[group])
            for target in re.findall(r"\[[^]]+\]\(([^)#]+)(?:#[^)]*)?\)", text):
                if "://" not in target:
                    destination = Path(os.path.normpath((relative.parent / target).as_posix())).as_posix()
                    self.assertIn(destination, available, f"broken link {target} in {path}")


class AssistantSelectionTests(unittest.TestCase):
    def test_each_install_contains_only_shared_selected_and_generated_files(self):
        for assistant, other in (("codex", "claude"), ("claude", "codex")):
            with self.subTest(assistant=assistant), tempfile.TemporaryDirectory() as temporary:
                target = Path(temporary) / "target"
                target.mkdir()
                result = run_installer("--target", str(target), "--assistant", assistant)
                self.assertEqual(result.returncode, 0, result.stderr)
                actual = {path.relative_to(target).as_posix() for path in target.rglob("*") if path.is_file()}
                expected = set(EXPECTED_ASSET_PATHS["shared"]) | set(EXPECTED_ASSET_PATHS[assistant]) | {".ai/assistant-profile.json", ".ai/installer-ledger.json", ".gitignore"}
                self.assertEqual(actual, expected)
                self.assertFalse((target / f".{other}").exists())
                self.assertFalse((target / ("CLAUDE.md" if other == "claude" else "AGENTS.md")).exists())
                profile = json.loads((target / ".ai/assistant-profile.json").read_text(encoding="utf-8"))
                self.assertEqual(profile, {"schema_version": 1, "assistant": assistant})
                ledger = json.loads((target / ".ai/installer-ledger.json").read_text(encoding="utf-8"))
                self.assertEqual(
                    set(ledger["files"]),
                    set(EXPECTED_ASSET_PATHS["shared"]) | set(EXPECTED_ASSET_PATHS[assistant]),
                )


class InstalledWorkflowValidationTests(unittest.TestCase):
    def _shipped_contract_test_count(self) -> int:
        """随包契约套件的用例数:从资产副本动态加载统计,避免硬编码漂移。"""
        shipped = ASSET_ROOT / "shared" / "scripts" / "tests" / "test_validate_workflow.py"
        spec = importlib.util.spec_from_file_location("shipped_contract_tests", shipped)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        # 随包文件使用 @dataclass,其字段解析要求模块已注册进 sys.modules。
        sys.modules[spec.name] = module
        # 无 -B 运行时 exec_module 会把 __pycache__ 写进资产树,令同轮稍后
        # 的物理枚举自污必败;加载期间抑制字节码写入(-B 下为无害冗余)。
        previous_dont_write_bytecode = sys.dont_write_bytecode
        sys.dont_write_bytecode = True
        try:
            spec.loader.exec_module(module)
        finally:
            sys.dont_write_bytecode = previous_dont_write_bytecode
        suite = unittest.defaultTestLoader.loadTestsFromModule(module)

        def collect(test) -> int:
            if isinstance(test, unittest.TestSuite):
                return sum(collect(item) for item in test)
            return 1

        return collect(suite)

    def test_shipped_contract_count_leaves_no_asset_pycache_without_dash_b(self) -> None:
        """无 -B 运行时统计随包套件不得把 __pycache__ 写进资产树。

        陷阱：exec_module 的字节码缓存落在资产副本旁，同轮稍后的
        test_manifest_exactly_enumerates_sorted_physical_assets 即自污必败，
        且报错误导性指向 manifest 而非真因。
        """
        program = (
            "import sys\n"
            "sys.dont_write_bytecode = False\n"
            "sys.path.insert(0, '.')\n"
            "from scripts.tests.test_install_ai_workflow import"
            " InstalledWorkflowValidationTests\n"
            "case = InstalledWorkflowValidationTests(\n"
            "    'test_installed_codex_and_claude_validate_without_source_or_openspec')\n"
            "case._shipped_contract_test_count()\n"
            "from pathlib import Path\n"
            "found = [str(p) for p in"
            " Path('scripts/ai-workflow-assets').rglob('__pycache__')]\n"
            "print('PYCACHE:' + (';'.join(found) if found else 'NONE'))\n"
        )
        environment = {
            key: value for key, value in os.environ.items()
            if key != "PYTHONDONTWRITEBYTECODE"
        }

        def clean_asset_pycache() -> None:
            for entry in ASSET_ROOT.rglob("__pycache__"):
                shutil.rmtree(entry, ignore_errors=True)

        clean_asset_pycache()
        try:
            result = subprocess.run(
                [sys.executable, "-c", program],
                cwd=REPOSITORY_ROOT,
                env=environment,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
                timeout=120,
            )
            self.assertEqual(result.returncode, 0, msg=result.stderr or result.stdout)
            self.assertIn("PYCACHE:NONE", result.stdout, msg=result.stdout)
        finally:
            clean_asset_pycache()

    def _restricted_environment(self, root: Path) -> dict[str, str]:
        binary_directory = root / "bin"
        binary_directory.mkdir()
        target_core = next(
            path
            for path in (root / "target", root)
            if (path / "scripts" / "lib" / "validate-workflow-core.sh").is_file()
        ) / "scripts" / "lib" / "validate-workflow-core.sh"
        for command in (*_core_external_commands(target_core), "python3"):
            executable = sys.executable if command == "python3" else shutil.which(command)
            self.assertIsNotNone(executable, msg=f"missing test prerequisite: {command}")
            (binary_directory / command).symlink_to(executable)
        return {"LC_ALL": "C.UTF-8", "PATH": str(binary_directory)}

    def _run_target(self, target: Path, environment: dict[str, str], *command: str):
        return subprocess.run(
            list(command), cwd=target, env=environment, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False, timeout=240,
        )

    def _git_identity(self, target: Path):
        def git(*arguments: str):
            return subprocess.run(
                ["git", *arguments], cwd=target, text=True,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True,
            ).stdout.strip()

        return {
            "head": git("rev-parse", "HEAD"),
            "branch": git("symbolic-ref", "HEAD"),
            "HEAD": (target / ".git" / "HEAD").read_bytes(),
            "config": (target / ".git" / "config").read_bytes(),
            "index": (target / ".git" / "index").read_bytes(),
        }

    def test_installed_codex_and_claude_validate_without_source_or_openspec(self):
        for assistant in ("codex", "claude"):
            with self.subTest(assistant=assistant), tempfile.TemporaryDirectory() as temporary:
                temporary_root = Path(temporary)
                target = temporary_root / "target"
                target.mkdir()
                subprocess.run(
                    ["git", "init", "-q"], cwd=target, check=True,
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                )
                (target / "seed.txt").write_text("baseline\n", encoding="utf-8")
                subprocess.run(
                    ["git", "add", "seed.txt"], cwd=target, check=True,
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                )
                subprocess.run(
                    ["git", "-c", "user.name=Portable Workflow Test", "-c",
                     "user.email=portable-workflow@example.invalid", "commit", "-qm",
                     "baseline"],
                    cwd=target, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                )
                git_before = self._git_identity(target)
                installed = run_installer("--target", str(target), "--assistant", assistant)
                self.assertEqual(installed.returncode, 0, installed.stderr or installed.stdout)
                self.assertEqual(self._git_identity(target), git_before)
                environment = self._restricted_environment(temporary_root)

                contract = self._run_target(
                    target, environment, "python3", "-B", "-m", "unittest", "-v",
                    "scripts.tests.test_validate_workflow",
                )
                tools = self._run_target(
                    target, environment, "python3", "-B", "-m", "unittest", "discover", "-v",
                    "-s", ".ai/tools/tests", "-p", "test_*.py",
                )
                public = self._run_target(
                    target, environment, "bash", "scripts/validate-workflow.sh",
                )
                required = self._run_target(
                    target, environment, "bash", "scripts/validate-workflow.sh",
                    "--require-openspec",
                )

                with self.subTest(assistant=assistant, command="contract"):
                    self.assertEqual(contract.returncode, 0, contract.stdout)
                    self.assertIn(f"Ran {self._shipped_contract_test_count()} tests", contract.stdout)
                    # 只允许已知理由的 skip;出现新理由即失败,防止必需用例静默消失。
                    allowed_skip_reasons = {
                        "single-assistant installation lacks the compatibility fixture",
                        "codex assistant is not present in this fixture",
                        "source installer unavailable; current selected side remains covered",
                        "pre-push hook is not shipped with this installation",
                        "CI pipeline configuration is source-repository only",
                        "flock is required to exercise the concurrency lock",
                        "flock is required to exercise the lock infrastructure path",
                    }
                    observed_skips = set(
                        re.findall(r"\.\.\. skipped '([^']*)'", contract.stdout)
                    )
                    self.assertLessEqual(
                        observed_skips, allowed_skip_reasons, contract.stdout
                    )
                    self.assertRegex(
                        contract.stdout,
                        r"test_installer_selected_only_metadata_allows_core_validation .* \.\.\. ok",
                    )
                    self.assertRegex(
                        contract.stdout,
                        r"test_shared_gates_remain_required_for_each_profile .* \.\.\. ok",
                    )
                with self.subTest(assistant=assistant, command="tools"):
                    self.assertEqual(tools.returncode, 0, tools.stdout)
                    self.assertIn("Ran 53 tests", tools.stdout)
                with self.subTest(assistant=assistant, command="public"):
                    self.assertEqual(public.returncode, 0, public.stdout)
                    self.assertEqual(
                        len(re.findall(r"^\[SKIP\] OpenSpec CLI ", public.stdout, re.MULTILINE)),
                        1,
                        public.stdout,
                    )
                    summaries = re.findall(
                        r"^PASS=\d+ FAIL=0 SKIP=1$", public.stdout, re.MULTILINE
                    )
                    self.assertEqual(len(summaries), 1, public.stdout)
                with self.subTest(assistant=assistant, command="required"):
                    self.assertNotEqual(required.returncode, 0, required.stdout)
                    fail_lines = re.findall(r"^\[FAIL\] .*$", required.stdout, re.MULTILINE)
                    self.assertEqual(
                        fail_lines,
                        ["[FAIL] OpenSpec CLI 缺失；required 模式不得跳过严格校验"],
                        required.stdout,
                    )
                    required_summaries = [
                        line for line in required.stdout.splitlines()
                        if re.fullmatch(r"PASS=\d+ FAIL=1 SKIP=0", line)
                    ]
                    self.assertEqual(len(required_summaries), 1, required.stdout)

                expected_status = set(EXPECTED_ASSET_PATHS["shared"])
                expected_status.update(EXPECTED_ASSET_PATHS[assistant])
                expected_status.update({".ai/assistant-profile.json", ".ai/installer-ledger.json", ".gitignore"})
                expected_status.discard(f".{assistant}/sdd/.gitkeep")
                status = subprocess.run(
                    ["git", "status", "--short", "--untracked-files=all"],
                    cwd=target, text=True, stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE, check=True,
                )
                status_lines = status.stdout.splitlines()
                self.assertTrue(
                    all(line.startswith("?? ") for line in status_lines), status.stdout
                )
                actual_status = {line[3:] for line in status_lines}
                self.assertEqual(actual_status, expected_status)
                self.assertEqual(self._git_identity(target), git_before)

                installed_snapshot = identity_snapshot_tree(target)
                rerun = run_installer("--target", str(target), "--assistant", assistant)
                self.assertEqual(rerun.returncode, 0, rerun.stderr or rerun.stdout)
                self.assertNotIn("[CREATE]", rerun.stdout)
                self.assertNotIn("[UPDATE]", rerun.stdout)
                self.assertEqual(identity_snapshot_tree(target), installed_snapshot)
                preview = run_installer(
                    "--target", str(target), "--assistant", assistant, "--dry-run"
                )
                self.assertEqual(preview.returncode, 0, preview.stderr or preview.stdout)
                self.assertIn("dry_run=1", preview.stdout)
                self.assertEqual(identity_snapshot_tree(target), installed_snapshot)

    def test_existing_selected_root_entry_conflict_is_zero_write_and_redacted(self):
        for assistant, root_entry in (("codex", "AGENTS.md"), ("claude", "CLAUDE.md")):
            with self.subTest(assistant=assistant), tempfile.TemporaryDirectory() as temporary:
                target = Path(temporary) / "target"
                target.mkdir()
                secret = b"private existing workflow instructions\n"
                (target / root_entry).write_bytes(secret)
                before = identity_snapshot_tree(target)

                result = run_installer("--target", str(target), "--assistant", assistant)

                self.assertEqual(result.returncode, 3, result)
                self.assertEqual(result.stdout, "")
                self.assertEqual(result.stderr, "CONFLICT: target file has different content\n")
                self.assertNotIn(secret.decode("utf-8").strip(), result.stderr)
                self.assertEqual(identity_snapshot_tree(target), before)


class InstallAiWorkflowCliTests(unittest.TestCase):
    def test_help_succeeds(self):
        result = run_installer("--help")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--target", result.stdout)
        self.assertIn("--assistant", result.stdout)
        self.assertEqual(result.stderr, "")

    def test_usage_matrix_is_rejected_without_writing_target(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "target"
            target.mkdir()
            marker = target / "marker.bin"
            marker.write_bytes(b"keep-me")
            before = snapshot_tree(target)
            cases = (
                (),
                ("--target", str(target)),
                ("--assistant", "codex"),
                ("--target", str(target), "--assistant", "CODEX", "--dry-run"),
                ("--target", str(target), "--assistant", "both", "--dry-run"),
                ("--target", str(target), "--target", str(target),
                 "--assistant", "codex", "--dry-run"),
                ("--target", str(target), "--assistant", "codex",
                 "--assistant", "claude", "--dry-run"),
                ("--target", str(target), "--assistant", "codex",
                 "--dry-run", "--dry-run"),
                ("--target", str(target), "--assistant", "codex",
                 "--unknown", "--dry-run"),
                ("--target", str(target), "--assistant", "codex",
                 "extra", "--dry-run"),
            )
            for arguments in cases:
                with self.subTest(arguments=arguments):
                    result = run_installer(*arguments)
                    self.assertEqual(result.returncode, 2, result)
                    self.assertEqual(result.stdout, "")
                    self.assertTrue(result.stderr.startswith("USAGE:"), result.stderr)
                    self.assertEqual(snapshot_tree(target), before)

    def test_non_dry_run_installs_and_reports_only_after_success(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "target"
            target.mkdir()

            result = run_installer("--target", str(target), "--assistant", "codex")

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stderr, "")
            self.assertIn("[CREATE] AGENTS.md\n", result.stdout)
            self.assertTrue(result.stdout.endswith("dry_run=0\n"), result.stdout)
            self.assertEqual(
                (target / "AGENTS.md").read_bytes(),
                (REPOSITORY_ROOT / "scripts" / "ai-workflow-assets" / "codex" / "AGENTS.md").read_bytes(),
            )

    def test_invalid_target_uses_input_exit_code_without_traceback_or_writes(self):
        with tempfile.TemporaryDirectory() as temporary:
            temporary_root = Path(temporary)
            missing = temporary_root / "missing"
            before = snapshot_tree(temporary_root)

            result = run_installer(
                "--target", str(missing), "--assistant", "codex", "--dry-run"
            )

            self.assertEqual(result.returncode, 3)
            self.assertEqual(result.stdout, "")
            self.assertTrue(result.stderr.startswith("UNSAFE:"), result.stderr)
            self.assertNotIn("Traceback", result.stderr)
            self.assertEqual(snapshot_tree(temporary_root), before)

    def test_invalid_targets_fail_closed(self):
        module = load_installer_module()
        with tempfile.TemporaryDirectory() as temporary:
            temporary_root = Path(temporary)
            source_root = create_source(temporary_root)
            missing = temporary_root / "missing"
            regular_file = temporary_root / "file"
            regular_file.write_text("not a directory", encoding="utf-8")
            child = source_root / "child"
            child.mkdir()
            real_target = temporary_root / "real-target"
            real_target.mkdir()
            target_symlink = temporary_root / "target-link"
            target_symlink.symlink_to(real_target, target_is_directory=True)
            for target in (missing, regular_file, source_root, child, target_symlink):
                with self.subTest(target=target):
                    source_before = snapshot_tree(source_root)
                    with self.assertRaises(ValueError):
                        module.build_plan(source_root, target, "codex")
                    self.assertEqual(snapshot_tree(source_root), source_before)


class InstallManifestTests(unittest.TestCase):
    def setUp(self):
        self.module = load_installer_module()
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.source_root = create_source(Path(self.temporary.name))
        self.asset_root = self.source_root / "scripts" / "ai-workflow-assets"

    def read_manifest_data(self):
        return json.loads((self.asset_root / "manifest.json").read_text(encoding="utf-8"))

    def write_manifest_data(self, data):
        (self.asset_root / "manifest.json").write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

    def test_valid_manifest_returns_frozen_dataclasses(self):
        manifest = self.module.load_manifest(self.asset_root)

        self.assertTrue(dataclasses.is_dataclass(manifest))
        self.assertEqual([entry.path for entry in manifest.shared], [".ai/README.md"])
        self.assertEqual([entry.path for entry in manifest.codex], ["AGENTS.md"])
        self.assertEqual([entry.path for entry in manifest.claude], ["CLAUDE.md"])
        with self.assertRaises(dataclasses.FrozenInstanceError):
            manifest.schema_version = 2

    def test_manifest_requires_exact_deep_schema(self):
        valid = self.read_manifest_data()
        cases = []
        cases.append([])
        cases.append({**valid, "extra": []})
        cases.append({key: value for key, value in valid.items() if key != "claude"})
        cases.append({**valid, "schema_version": True})
        cases.append({**valid, "schema_version": 2})
        cases.append({**valid, "shared": {}})
        cases.append({**valid, "shared": [".ai/README.md"]})
        cases.append({**valid, "shared": [{"path": ".ai/README.md", "mode": "0644",
                                             "extra": False}]})
        cases.append({**valid, "shared": [{"path": 7, "mode": "0644"}]})
        cases.append({**valid, "shared": [{"path": ".ai/README.md", "mode": 0o644}]})
        for data in cases:
            with self.subTest(data=data):
                self.write_manifest_data(data)
                with self.assertRaises(ValueError):
                    self.module.load_manifest(self.asset_root)

    def test_manifest_rejects_duplicate_json_keys(self):
        (self.asset_root / "manifest.json").write_text(
            '{"schema_version":1,"schema_version":1,"shared":[],"codex":[],"claude":[]}\n',
            encoding="utf-8",
        )

        with self.assertRaises(ValueError):
            self.module.load_manifest(self.asset_root)

    def test_manifest_requires_sorted_unique_paths(self):
        data = self.read_manifest_data()
        second_path = ".ai/Z.md"
        second_source = self.asset_root / "shared" / ".ai" / "Z.md"
        second_source.write_text("z\n", encoding="utf-8")
        data["shared"] = [
            {"path": second_path, "mode": "0644"},
            {"path": ".ai/README.md", "mode": "0644"},
        ]
        self.write_manifest_data(data)
        with self.assertRaises(ValueError):
            self.module.load_manifest(self.asset_root)

        data["shared"] = [
            {"path": ".ai/README.md", "mode": "0644"},
            {"path": ".ai/README.md", "mode": "0644"},
        ]
        self.write_manifest_data(data)
        with self.assertRaises(ValueError):
            self.module.load_manifest(self.asset_root)

    def test_manifest_rejects_dangerous_paths(self):
        dangerous_paths = (
            "", "/absolute", ".", "..", "./file", "dir/../file", "dir//file",
            "dir/", "dir\\file", "nul\0file", unicodedata.normalize("NFD", "caf\u00e9"),
        )
        for dangerous_path in dangerous_paths:
            with self.subTest(path=dangerous_path):
                data = self.read_manifest_data()
                data["shared"] = [{"path": dangerous_path, "mode": "0644"}]
                self.write_manifest_data(data)
                with self.assertRaises(ValueError):
                    self.module.load_manifest(self.asset_root)

    def test_manifest_rejects_invalid_modes(self):
        for invalid_mode in ("644", "0600", "0777", "0754", "0644 "):
            with self.subTest(mode=invalid_mode):
                data = self.read_manifest_data()
                data["shared"] = [{"path": ".ai/README.md", "mode": invalid_mode}]
                self.write_manifest_data(data)
                with self.assertRaises(ValueError):
                    self.module.load_manifest(self.asset_root)

    def test_manifest_rejects_missing_directory_and_symlink_sources(self):
        source = self.asset_root / "shared" / ".ai" / "README.md"
        source.unlink()
        with self.assertRaises(ValueError):
            self.module.load_manifest(self.asset_root)

        source.mkdir()
        with self.assertRaises(ValueError):
            self.module.load_manifest(self.asset_root)

        source.rmdir()
        external = Path(self.temporary.name) / "external"
        external.write_text("outside\n", encoding="utf-8")
        source.symlink_to(external)
        with self.assertRaises(ValueError):
            self.module.load_manifest(self.asset_root)

    def test_manifest_rejects_symlinked_asset_group(self):
        real_group = Path(self.temporary.name) / "real-shared"
        (self.asset_root / "shared").rename(real_group)
        (self.asset_root / "shared").symlink_to(real_group, target_is_directory=True)

        with self.assertRaises(ValueError):
            self.module.load_manifest(self.asset_root)

    def test_build_plan_rejects_symlinked_asset_root(self):
        target = Path(self.temporary.name) / "target"
        target.mkdir()
        external_asset_root = Path(self.temporary.name) / "external-assets"
        self.asset_root.rename(external_asset_root)
        self.asset_root.symlink_to(external_asset_root, target_is_directory=True)

        with self.assertRaises(ValueError):
            self.module.build_plan(self.source_root, target, "codex")

    def test_manifest_rejects_parent_replacement_during_source_open(self):
        original_parent = self.asset_root / "shared" / ".ai"
        moved_parent = Path(self.temporary.name) / "moved-ai"
        external_parent = Path(self.temporary.name) / "external-ai"
        external_parent.mkdir()
        (external_parent / "README.md").write_bytes(b"external\n")
        real_lstat = self.module.os.lstat
        real_open = self.module.os.open
        replaced = False

        def replace_parent_before_leaf_access(path):
            nonlocal replaced
            if not replaced and Path(os.fspath(path)).name == "README.md":
                original_parent.rename(moved_parent)
                original_parent.symlink_to(external_parent, target_is_directory=True)
                replaced = True

        def racing_lstat(path, *args, **kwargs):
            replace_parent_before_leaf_access(path)
            return real_lstat(path, *args, **kwargs)

        def racing_open(path, flags, *args, **kwargs):
            replace_parent_before_leaf_access(path)
            return real_open(path, flags, *args, **kwargs)

        with mock.patch.object(self.module.os, "lstat", side_effect=racing_lstat), \
            mock.patch.object(self.module.os, "open", side_effect=racing_open):
            with self.assertRaises(ValueError):
                self.module.load_manifest(self.asset_root)
        self.assertTrue(replaced)

    def test_manifest_rejects_same_inode_content_mutation_during_read(self):
        source = self.asset_root / "shared" / ".ai" / "README.md"
        size = 3 * 1024 * 1024
        source.write_bytes(b"A" * size)
        source_inode = source.stat().st_ino
        real_read = self.module.os.read
        mutated = False

        def racing_read(descriptor, count):
            nonlocal mutated
            chunk = real_read(descriptor, count)
            if not mutated and self.module.os.fstat(descriptor).st_ino == source_inode:
                mutated = True
                source.write_bytes(b"B" * size)
            return chunk

        with mock.patch.object(self.module.os, "read", side_effect=racing_read):
            with self.assertRaises(ValueError):
                self.module.load_manifest(self.asset_root)
        self.assertTrue(mutated)

    def test_selected_groups_must_have_globally_unique_targets(self):
        data = self.read_manifest_data()
        duplicate_source = self.asset_root / "codex" / ".ai" / "README.md"
        duplicate_source.parent.mkdir(parents=True)
        duplicate_source.write_text("duplicate\n", encoding="utf-8")
        data["codex"] = [{"path": ".ai/README.md", "mode": "0644"}]
        self.write_manifest_data(data)
        target = Path(self.temporary.name) / "target"
        target.mkdir()

        with self.assertRaises(ValueError):
            self.module.build_plan(self.source_root, target, "codex")

    def test_build_plan_returns_frozen_sorted_items_with_bytes_and_modes(self):
        target = Path(self.temporary.name) / "target"
        target.mkdir()

        plan = self.module.build_plan(self.source_root, target, "claude")

        self.assertTrue(dataclasses.is_dataclass(plan))
        self.assertEqual(
            [item.path for item in plan.items],
            [".ai/README.md", ".ai/assistant-profile.json", ".ai/installer-ledger.json", ".gitignore", "CLAUDE.md"],
        )
        self.assertTrue(all(type(item.source_bytes) is bytes for item in plan.items))
        self.assertTrue(all(item.mode in {0o644, 0o755} for item in plan.items))
        self.assertTrue(all(item.action == "create" for item in plan.items))
        with self.assertRaises(dataclasses.FrozenInstanceError):
            plan.assistant = "codex"


class InstallDryRunTests(unittest.TestCase):
    def test_manifest_control_characters_fail_closed_before_cli_output(self):
        unsafe_paths = (
            "line\n[CREATE] forged",
            "line\rRESULT forged",
            "ansi\x1b[31m",
        )
        for unsafe_path in unsafe_paths:
            with self.subTest(path=unsafe_path), tempfile.TemporaryDirectory() as temporary:
                temporary_root = Path(temporary)
                source_root = create_source(temporary_root)
                asset_root = source_root / "scripts" / "ai-workflow-assets"
                data = json.loads(
                    (asset_root / "manifest.json").read_text(encoding="utf-8")
                )
                data["shared"] = [{"path": unsafe_path, "mode": "0644"}]
                (asset_root / "manifest.json").write_text(
                    json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )
                source = asset_root / "shared" / unsafe_path
                source.write_bytes(b"unsafe-name\n")
                target = temporary_root / "target"
                target.mkdir()
                before = snapshot_tree(target)

                result = run_source_installer(
                    source_root,
                    "--target", str(target), "--assistant", "codex", "--dry-run",
                )

                self.assertEqual(result.returncode, 3)
                self.assertEqual(result.stdout, "")
                self.assertEqual(
                    result.stderr,
                    "UNSAFE: manifest path contains control characters\n",
                )
                self.assertEqual(snapshot_tree(target), before)

    def test_target_control_characters_fail_closed_before_cli_output(self):
        unsafe_names = (
            "target\n[CREATE] forged",
            "target\rRESULT forged",
            "target\x1b[31m",
        )
        for unsafe_name in unsafe_names:
            with self.subTest(name=unsafe_name), tempfile.TemporaryDirectory() as temporary:
                target = Path(temporary) / unsafe_name
                target.mkdir()
                before = snapshot_tree(target)

                result = run_installer(
                    "--target", str(target), "--assistant", "claude", "--dry-run"
                )

                self.assertEqual(result.returncode, 3)
                self.assertEqual(result.stdout, "")
                self.assertEqual(
                    result.stderr,
                    "UNSAFE: target path contains control characters\n",
                )
                self.assertEqual(snapshot_tree(target), before)

    def test_dry_run_output_is_sorted_stable_and_read_only(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "target"
            target.mkdir()
            marker = target / "unchanged.bin"
            marker.write_bytes(b"unchanged\0bytes")
            os.chmod(marker, 0o640)
            before = snapshot_tree(target)
            arguments = ("--target", str(target), "--assistant", "codex", "--dry-run")

            first = run_installer(*arguments)
            middle = snapshot_tree(target)
            second = run_installer(*arguments)

            expected_created = len(EXPECTED_ASSET_PATHS["shared"]) + len(EXPECTED_ASSET_PATHS["codex"]) + 3
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertEqual(first.stdout, second.stdout)
            self.assertEqual(first.stderr, "")
            self.assertEqual(second.stderr, "")
            lines = first.stdout.splitlines()
            action_lines = lines[:-1]
            self.assertEqual(action_lines, sorted(action_lines, key=os.fsencode))
            self.assertIn("[CREATE] .ai/README.md", action_lines)
            self.assertIn("[CREATE] AGENTS.md", action_lines)
            self.assertNotIn("CLAUDE.md", first.stdout)
            self.assertEqual(
                lines[-1],
                f"RESULT assistant=codex target={target.resolve()} "
                f"created={expected_created} updated=0 unchanged=0 dry_run=1",
            )
            self.assertEqual(before, middle)
            self.assertEqual(before, snapshot_tree(target))

    def test_dry_run_plans_gitignore_update_without_modifying_original_bytes(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "target"
            target.mkdir()
            gitignore = target / ".gitignore"
            gitignore.write_bytes(b"existing-rule\n")
            before = snapshot_tree(target)

            result = run_installer(
                "--target", str(target), "--assistant", "codex", "--dry-run"
            )

            expected_created = len(EXPECTED_ASSET_PATHS["shared"]) + len(EXPECTED_ASSET_PATHS["codex"]) + 2
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("[UPDATE] .gitignore\n", result.stdout)
            self.assertTrue(
                result.stdout.endswith(
                    f"RESULT assistant=codex target={target.resolve()} "
                    f"created={expected_created} updated=1 unchanged=0 dry_run=1\n"
                ),
                result.stdout,
            )
            self.assertEqual(snapshot_tree(target), before)

    def test_restricted_path_dry_run_needs_only_bash_and_python(self):
        with tempfile.TemporaryDirectory() as temporary:
            temporary_root = Path(temporary)
            target = temporary_root / "target"
            target.mkdir()
            binary_directory = temporary_root / "bin"
            binary_directory.mkdir()
            bash = shutil.which("bash")
            python3 = shutil.which("python3")
            self.assertIsNotNone(bash)
            self.assertIsNotNone(python3)
            (binary_directory / "bash").symlink_to(bash)
            (binary_directory / "python3").symlink_to(python3)
            environment = os.environ.copy()
            environment["PATH"] = str(binary_directory)
            before = snapshot_tree(target)

            result = run_installer(
                "--target", str(target), "--assistant", "claude", "--dry-run",
                env=environment,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("assistant=claude", result.stdout)
            self.assertEqual(snapshot_tree(target), before)


class InstallWriteTests(unittest.TestCase):
    def setUp(self):
        self.module = load_installer_module()
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.source_root = create_source(self.root)

    def test_codex_and_claude_create_minimal_assets_modes_and_canonical_profile(self):
        asset_root = self.source_root / "scripts" / "ai-workflow-assets"
        manifest_path = asset_root / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["shared"][0]["mode"] = "0755"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expected_profile = {
            assistant: (json.dumps(
                {"assistant": assistant, "schema_version": 1},
                indent=2,
                sort_keys=True,
            ) + "\n").encode("utf-8")
            for assistant in ("codex", "claude")
        }
        expected_ledger = {
            assistant: (json.dumps(
                {
                    "assistant": assistant,
                    "files": {
                        ".ai/README.md": hashlib.sha256(b"shared\n").hexdigest(),
                        ("AGENTS.md" if assistant == "codex" else "CLAUDE.md"):
                            hashlib.sha256(
                                b"codex\n" if assistant == "codex" else b"claude\n",
                            ).hexdigest(),
                    },
                    "schema_version": 1,
                },
                indent=2,
                sort_keys=True,
            ) + "\n").encode("utf-8")
            for assistant in ("codex", "claude")
        }

        for assistant in ("codex", "claude"):
            with self.subTest(assistant=assistant):
                target = self.root / f"target-{assistant}"
                target.mkdir()
                plan = self.module.build_plan(self.source_root, target, assistant)

                result = execute_plan(self, self.module, plan)

                self.assertTrue(dataclasses.is_dataclass(result))
                self.assertEqual(result.plan, plan)
                self.assertFalse(result.dry_run)
                self.assertEqual((target / ".ai" / "README.md").read_bytes(), b"shared\n")
                self.assertEqual(
                    stat.S_IMODE((target / ".ai" / "README.md").stat().st_mode),
                    0o755,
                )
                self.assertEqual(
                    (target / ".ai" / "assistant-profile.json").read_bytes(),
                    expected_profile[assistant],
                )
                self.assertEqual(
                    (target / ".ai" / "installer-ledger.json").read_bytes(),
                    expected_ledger[assistant],
                )
                selected = "AGENTS.md" if assistant == "codex" else "CLAUDE.md"
                unselected = "CLAUDE.md" if assistant == "codex" else "AGENTS.md"
                self.assertTrue((target / selected).is_file())
                self.assertFalse((target / unselected).exists())
                self.assertEqual((target / ".gitignore").read_bytes(), managed_block(assistant))
                self.assertEqual(stat.S_IMODE((target / ".gitignore").stat().st_mode), 0o644)

    def test_second_install_is_inode_mtime_mode_and_bytes_stable(self):
        target = self.root / "target"
        target.mkdir()
        first_plan = self.module.build_plan(self.source_root, target, "codex")
        execute_plan(self, self.module, first_plan)
        installed = snapshot_tree(target)

        second_plan = self.module.build_plan(self.source_root, target, "codex")
        self.assertTrue(all(item.action == "unchanged" for item in second_plan.items))
        result = execute_plan(self, self.module, second_plan)

        self.assertTrue(all(item.action == "unchanged" for item in result.plan.items))
        self.assertEqual(snapshot_tree(target), installed)

    def test_execute_plan_dry_run_and_runtime_use_no_subprocess(self):
        for dry_run in (True, False):
            with self.subTest(dry_run=dry_run):
                target = self.root / f"target-{dry_run}"
                target.mkdir()
                plan = self.module.build_plan(self.source_root, target, "claude")
                before = snapshot_tree(target)
                with mock.patch("subprocess.run", side_effect=AssertionError("subprocess.run")), \
                    mock.patch("subprocess.Popen", side_effect=AssertionError("subprocess.Popen")), \
                    mock.patch.dict(os.environ, {"PATH": ""}):
                    execute_plan(self, self.module, plan, dry_run=dry_run)
                if dry_run:
                    self.assertEqual(snapshot_tree(target), before)
                else:
                    self.assertTrue((target / "CLAUDE.md").is_file())


class InstallConflictTests(unittest.TestCase):
    def setUp(self):
        self.module = load_installer_module()
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.source_root = create_source(self.root)

    def test_different_content_and_non_regular_leaf_types_fail_before_writes(self):
        cases = ("different", "directory", "fifo", "symlink", "dangling")
        for case in cases:
            with self.subTest(case=case):
                target = self.root / f"target-{case}"
                target.mkdir()
                leaf = target / "AGENTS.md"
                if case == "different":
                    leaf.write_bytes(b"different\n")
                elif case == "directory":
                    leaf.mkdir()
                elif case == "fifo":
                    os.mkfifo(leaf)
                elif case == "symlink":
                    outside = self.root / f"outside-{case}"
                    outside.write_bytes(b"outside\n")
                    leaf.symlink_to(outside)
                else:
                    leaf.symlink_to(self.root / "missing")
                before = snapshot_tree(target)

                with self.assertRaises(ValueError):
                    self.module.build_plan(self.source_root, target, "codex")

                self.assertEqual(snapshot_tree(target), before)

    def test_profile_conflict_fails_before_any_asset_is_created(self):
        target = self.root / "profile-conflict"
        (target / ".ai").mkdir(parents=True)
        (target / ".ai" / "assistant-profile.json").write_bytes(b"{}\n")
        before = snapshot_tree(target)

        with self.assertRaises(ValueError):
            self.module.build_plan(self.source_root, target, "codex")

        self.assertEqual(snapshot_tree(target), before)
        self.assertFalse((target / "AGENTS.md").exists())

    def test_execute_rejects_root_parent_source_and_gitignore_changes_since_plan(self):
        mutators = {}

        def replace_root(target, _source):
            moved = target.with_name(target.name + "-moved")
            target.rename(moved)
            target.mkdir()

        def replace_parent(target, _source):
            parent = target / ".ai"
            moved = target / ".ai-old"
            parent.rename(moved)
            parent.mkdir()

        def replace_source(_target, source):
            (source / "scripts" / "ai-workflow-assets" / "shared" / ".ai" / "README.md").write_bytes(b"changed\n")

        def replace_gitignore(target, _source):
            (target / ".gitignore").write_bytes(b"changed-after-plan\n")

        mutators["root inode"] = replace_root
        mutators["parent inode"] = replace_parent
        mutators["source bytes"] = replace_source
        mutators["gitignore bytes"] = replace_gitignore
        for label, mutate in mutators.items():
            with self.subTest(label=label):
                case_root = self.root / label.replace(" ", "-")
                case_root.mkdir()
                source = create_source(case_root)
                target = case_root / "target"
                (target / ".ai").mkdir(parents=True)
                (target / ".gitignore").write_bytes(b"original\n")
                plan = self.module.build_plan(source, target, "codex")
                mutate(target, source)
                current = snapshot_tree(target)

                with self.assertRaises(ValueError):
                    execute_plan(self, self.module, plan)

                self.assertEqual(snapshot_tree(target), current)
                self.assertFalse((target / "AGENTS.md").exists())


class InstallSymlinkTests(unittest.TestCase):
    def setUp(self):
        self.module = load_installer_module()
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.source_root = create_source(self.root)

    def test_root_intermediate_and_existing_leaf_symlinks_are_rejected(self):
        real_target = self.root / "real-target"
        real_target.mkdir()
        root_link = self.root / "root-link"
        root_link.symlink_to(real_target, target_is_directory=True)
        with self.assertRaises(ValueError):
            self.module.build_plan(self.source_root, root_link, "codex")

        for destination in (self.root / "outside", real_target):
            destination.mkdir(exist_ok=True)
            target = self.root / f"middle-{destination.name}"
            target.mkdir()
            (target / ".ai").symlink_to(destination, target_is_directory=True)
            with self.subTest(destination=destination):
                with self.assertRaises(ValueError):
                    self.module.build_plan(self.source_root, target, "codex")

        target = self.root / "leaf-target"
        target.mkdir()
        for name, destination in (("inside", target / "marker"), ("outside", self.root / "outside-file")):
            destination.write_bytes(b"marker\n")
            leaf = target / "AGENTS.md"
            leaf.symlink_to(destination)
            with self.subTest(name=name):
                with self.assertRaises(ValueError):
                    self.module.build_plan(self.source_root, target, "codex")
            leaf.unlink()

    def test_post_preflight_parent_symlink_and_rename_replacement_fail_closed(self):
        for replacement in ("symlink", "directory"):
            with self.subTest(replacement=replacement):
                case_root = self.root / replacement
                case_root.mkdir()
                source = create_source(case_root)
                target = case_root / "target"
                parent = target / ".ai"
                parent.mkdir(parents=True)
                external = case_root / "external"
                external.mkdir()
                marker = external / "marker"
                marker.write_bytes(b"do-not-touch\n")
                plan = self.module.build_plan(source, target, "codex")
                called = False

                def mutate(_plan):
                    nonlocal called
                    called = True
                    parent.rename(target / ".ai-old")
                    if replacement == "symlink":
                        parent.symlink_to(external, target_is_directory=True)
                    else:
                        parent.mkdir()

                with mock.patch.object(
                    self.module, "_after_revalidation", create=True, side_effect=mutate,
                ):
                    with self.assertRaises(ValueError):
                        execute_plan(self, self.module, plan)
                self.assertTrue(called)
                self.assertEqual(marker.read_bytes(), b"do-not-touch\n")
                self.assertEqual(list(external.iterdir()), [marker])
                self.assertFalse((target / "AGENTS.md").exists())

    def test_gitignore_replacement_at_publish_is_not_overwritten(self):
        target = self.root / "publish-race"
        (target / ".ai").mkdir(parents=True)
        gitignore = target / ".gitignore"
        gitignore.write_bytes(b"original\n")
        external = self.root / "external-gitignore"
        external.write_bytes(b"external-marker\n")
        plan = self.module.build_plan(self.source_root, target, "codex")
        publishes = 0

        def replace_before_update(operation):
            nonlocal publishes
            if operation != "publish":
                return
            publishes += 1
            if publishes == 4:
                gitignore.rename(target / ".gitignore-original")
                gitignore.symlink_to(external)

        with mock.patch.object(self.module, "_fault_point", side_effect=replace_before_update):
            with self.assertRaises(ValueError):
                execute_plan(self, self.module, plan)

        self.assertEqual(publishes, 4)
        self.assertTrue(gitignore.is_symlink())
        self.assertEqual(os.readlink(gitignore), str(external))
        self.assertEqual(external.read_bytes(), b"external-marker\n")
        self.assertFalse((target / "AGENTS.md").exists())

    def test_parent_rename_after_profile_link_is_detected_and_rolled_back(self):
        for destination_kind in ("target-inside", "target-outside"):
            with self.subTest(destination_kind=destination_kind):
                case_root = self.root / destination_kind
                case_root.mkdir()
                source = create_source(case_root)
                target = case_root / "target"
                parent = target / ".ai"
                parent.mkdir(parents=True)
                moved = (
                    target / ".ai-moved"
                    if destination_kind == "target-inside"
                    else case_root / "outside-moved-ai"
                )
                plan = self.module.build_plan(source, target, "codex")
                real_link = self.module.os.link
                mutated = False
                target_after_mutation = None

                def racing_link(source_name, target_name, *args, **kwargs):
                    nonlocal mutated, target_after_mutation
                    result = real_link(source_name, target_name, *args, **kwargs)
                    if target_name == "assistant-profile.json":
                        parent.rename(moved)
                        parent.mkdir()
                        mutated = True
                        target_after_mutation = {
                            path: value
                            for path, value in logical_snapshot_tree(target).items()
                            if not path.startswith(".ai-moved/")
                        }
                    return result

                with mock.patch.object(self.module.os, "link", side_effect=racing_link):
                    with self.assertRaises((ValueError, RuntimeError)):
                        execute_plan(self, self.module, plan)

                self.assertTrue(mutated)
                self.assertEqual(logical_snapshot_tree(target), target_after_mutation)
                self.assertEqual(list(moved.iterdir()), [])


class InstallRollbackTests(unittest.TestCase):
    def setUp(self):
        self.module = load_installer_module()
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.source_root = create_source(self.root)

    def _target_and_plan(self, name):
        target = self.root / name
        (target / ".ai").mkdir(parents=True)
        gitignore = target / ".gitignore"
        gitignore.write_bytes(b"existing-rule")
        os.chmod(gitignore, 0o600)
        return target, self.module.build_plan(self.source_root, target, "codex")

    def test_open_write_fsync_fchmod_and_publish_failures_roll_back_journal(self):
        matrix = (
            ("open", 2),
            ("write", 2),
            ("fsync", 3),
            ("fchmod", 2),
            ("publish", 3),
        )
        for operation, fail_at in matrix:
            with self.subTest(operation=operation, fail_at=fail_at):
                target, plan = self._target_and_plan(f"target-{operation}")
                calls = 0

                def inject(actual):
                    nonlocal calls
                    if actual == operation:
                        calls += 1
                        if calls == fail_at:
                            raise OSError(f"injected {operation}")

                with mock.patch.object(
                    self.module, "_fault_point", create=True, side_effect=inject,
                ):
                    with self.assertRaises(RuntimeError):
                        execute_plan(self, self.module, plan)
                self.assertGreaterEqual(calls, fail_at)
                self.assertEqual((target / ".gitignore").read_bytes(), b"existing-rule")
                self.assertEqual(stat.S_IMODE((target / ".gitignore").stat().st_mode), 0o600)
                self.assertEqual(list((target / ".ai").iterdir()), [])
                self.assertFalse((target / "AGENTS.md").exists())

    def test_rollback_failure_reports_primary_and_rollback_errors_without_content(self):
        target, plan = self._target_and_plan("rollback-failure")
        publishes = 0

        def fail_second_publish(operation):
            nonlocal publishes
            if operation == "publish":
                publishes += 1
                if publishes == 2:
                    raise OSError("primary secret content")

        with mock.patch.object(
                self.module, "_fault_point", create=True, side_effect=fail_second_publish,
            ), \
            mock.patch.object(
                self.module,
                "_rollback_journal",
                create=True,
                side_effect=OSError("rollback secret content"),
            ):
            with self.assertRaises(RuntimeError) as raised:
                execute_plan(self, self.module, plan)
        message = str(raised.exception)
        self.assertIn("installation failed", message)
        self.assertIn("rollback failed", message)
        self.assertNotIn("secret content", message)

    def test_keyboard_interrupt_after_created_file_parent_fsync_rolls_back(self):
        target, plan = self._target_and_plan("created-file-keyboard-interrupt")
        before = logical_snapshot_tree(target)
        real_link = self.module.os.link
        real_fsync = self.module.os.fsync
        published = False
        injected = False

        def tracking_link(source_name, target_name, *args, **kwargs):
            nonlocal published
            result = real_link(source_name, target_name, *args, **kwargs)
            if target_name == "README.md":
                published = True
            return result

        def interrupt_parent_fsync(descriptor):
            nonlocal injected
            if published and not injected:
                injected = True
                raise KeyboardInterrupt("cancel after create publication")
            return real_fsync(descriptor)

        with mock.patch.object(self.module.os, "link", side_effect=tracking_link), \
            mock.patch.object(self.module.os, "fsync", side_effect=interrupt_parent_fsync):
            with self.assertRaises(KeyboardInterrupt):
                execute_plan(self, self.module, plan)

        self.assertTrue(injected)
        self.assertEqual(logical_snapshot_tree(target), before)
        self.assertFalse(any(
            "portable-ai-workflow" in path.name for path in target.rglob("*")
        ))

    def test_keyboard_interrupt_after_create_link_syscall_removes_bound_leaf(self):
        target, plan = self._target_and_plan("create-link-keyboard-interrupt")
        before = logical_snapshot_tree(target)
        real_link = self.module.os.link
        injected = False

        def link_then_interrupt(source_name, target_name, *args, **kwargs):
            nonlocal injected
            result = real_link(source_name, target_name, *args, **kwargs)
            if not injected and target_name == "README.md":
                injected = True
                raise KeyboardInterrupt("cancel after create link syscall")
            return result

        with mock.patch.object(self.module.os, "link", side_effect=link_then_interrupt):
            with self.assertRaises(KeyboardInterrupt):
                execute_plan(self, self.module, plan)

        self.assertTrue(injected)
        self.assertEqual(logical_snapshot_tree(target), before)
        self.assertFalse(any(
            "portable-ai-workflow" in path.name for path in target.rglob("*")
        ))

    def test_keyboard_interrupt_after_exchange_syscall_restores_by_binding(self):
        target, plan = self._target_and_plan("exchange-keyboard-interrupt")
        before = logical_snapshot_tree(target)
        real_exchange = self.module._rename_exchange
        injected = False

        def exchange_then_interrupt(directory_fd, left, right):
            nonlocal injected
            result = real_exchange(directory_fd, left, right)
            if not injected and right == ".gitignore":
                injected = True
                raise KeyboardInterrupt("cancel after exchange syscall")
            return result

        with mock.patch.object(
            self.module, "_rename_exchange", side_effect=exchange_then_interrupt,
        ):
            with self.assertRaises(KeyboardInterrupt):
                execute_plan(self, self.module, plan)

        self.assertTrue(injected)
        self.assertEqual(logical_snapshot_tree(target), before)
        self.assertFalse(any(
            "portable-ai-workflow" in path.name for path in target.rglob("*")
        ))

    def test_restored_exchange_cleanup_failure_is_reported_as_rollback_failure(self):
        target, plan = self._target_and_plan("exchange-cleanup-failure")
        original = (target / ".gitignore").read_bytes()
        real_exchange = self.module._rename_exchange
        real_unlink_bound = self.module._unlink_regular_if_bound
        interrupted = False
        cleanup_failed = False

        def exchange_then_interrupt(directory_fd, left, right):
            nonlocal interrupted
            result = real_exchange(directory_fd, left, right)
            if not interrupted and right == ".gitignore":
                interrupted = True
                raise KeyboardInterrupt("cancel after exchange syscall")
            return result

        def fail_restored_temp_cleanup(parent_fd, name, expected):
            nonlocal cleanup_failed
            if interrupted and not cleanup_failed and "gitignore" in name:
                cleanup_failed = True
                raise OSError("cleanup secret content")
            return real_unlink_bound(parent_fd, name, expected)

        caught = None
        with mock.patch.object(
                self.module, "_rename_exchange", side_effect=exchange_then_interrupt,
            ), \
            mock.patch.object(
                self.module,
                "_unlink_regular_if_bound",
                side_effect=fail_restored_temp_cleanup,
            ):
            try:
                execute_plan(self, self.module, plan)
            except BaseException as error:
                caught = error

        self.assertTrue(interrupted)
        self.assertTrue(cleanup_failed)
        self.assertIsInstance(caught, RuntimeError)
        self.assertIn("rollback failed", str(caught))
        self.assertNotIn("secret content", str(caught))
        self.assertEqual((target / ".gitignore").read_bytes(), original)

    def test_new_directory_is_journaled_before_nofollow_open_can_fail(self):
        target = self.root / "directory-open-failure"
        target.mkdir()
        plan = self.module.build_plan(self.source_root, target, "codex")
        real_open = self.module.os.open
        writing = False
        failed = False

        def begin_writing(_plan):
            nonlocal writing
            writing = True

        def fail_new_ai_open(path, flags, *args, **kwargs):
            nonlocal failed
            if (
                writing
                and not failed
                and "portable-ai-workflow" in os.fspath(path)
                and flags & os.O_DIRECTORY
            ):
                failed = True
                raise OSError("injected directory open")
            return real_open(path, flags, *args, **kwargs)

        with mock.patch.object(self.module, "_after_revalidation", side_effect=begin_writing), \
            mock.patch.object(self.module.os, "open", side_effect=fail_new_ai_open):
            with self.assertRaises((RuntimeError, ValueError)):
                execute_plan(self, self.module, plan)
        self.assertTrue(failed)
        self.assertEqual(list(target.iterdir()), [])

    def test_failed_atomic_exchange_reversal_reports_rollback_failure(self):
        target, plan = self._target_and_plan("exchange-reversal-failure")
        gitignore = target / ".gitignore"
        external = self.root / "exchange-external"
        external.write_bytes(b"external\n")
        publishes = 0
        exchanges = 0
        real_exchange = self.module._rename_exchange

        def replace_before_update(operation):
            nonlocal publishes
            if operation == "publish":
                publishes += 1
                if publishes == 4:
                    gitignore.rename(target / ".gitignore-original")
                    gitignore.symlink_to(external)

        def fail_reversal(directory_fd, left, right):
            nonlocal exchanges
            exchanges += 1
            if exchanges > 1:
                raise OSError("rollback secret content")
            return real_exchange(directory_fd, left, right)

        with mock.patch.object(self.module, "_fault_point", side_effect=replace_before_update), \
            mock.patch.object(self.module, "_rename_exchange", side_effect=fail_reversal):
            with self.assertRaises(RuntimeError) as raised:
                execute_plan(self, self.module, plan)
        self.assertIn("installation failed", str(raised.exception))
        self.assertIn("rollback failed", str(raised.exception))
        self.assertNotIn("secret content", str(raised.exception))
        self.assertEqual(external.read_bytes(), b"external\n")

    def test_create_journal_fault_windows_leave_no_published_artifacts(self):
        for fault in ("post-link-stat", "temp-unlink", "parent-fd-dup"):
            with self.subTest(fault=fault):
                target = self.root / fault
                (target / ".ai").mkdir(parents=True)
                plan = self.module.build_plan(self.source_root, target, "codex")
                before = logical_snapshot_tree(target)
                real_prepare = self.module._prepare_temporary_file
                real_link = self.module.os.link
                real_stat = self.module.os.stat
                real_unlink = self.module.os.unlink
                real_dup = self.module.os.dup
                prepared = False
                linked = False
                failed = False

                def preparing(parent_fd, name, content, mode):
                    nonlocal prepared
                    result = real_prepare(parent_fd, name, content, mode)
                    if name == "README.md":
                        prepared = True
                    return result

                def linking(source_name, target_name, *args, **kwargs):
                    nonlocal linked
                    result = real_link(source_name, target_name, *args, **kwargs)
                    if target_name == "README.md":
                        linked = True
                    return result

                def failing_stat(path, *args, **kwargs):
                    nonlocal failed
                    if fault == "post-link-stat" and linked and not failed and path == "README.md":
                        failed = True
                        raise OSError("injected post-link stat")
                    return real_stat(path, *args, **kwargs)

                def failing_unlink(path, *args, **kwargs):
                    nonlocal failed
                    if (
                        fault == "temp-unlink"
                        and linked
                        and not failed
                        and "portable-ai-workflow" in os.fspath(path)
                    ):
                        failed = True
                        raise OSError("injected temp unlink")
                    return real_unlink(path, *args, **kwargs)

                def failing_dup(descriptor):
                    nonlocal failed
                    if (
                        fault == "parent-fd-dup"
                        and prepared
                        and (target / ".ai" / "README.md").exists()
                        and not failed
                    ):
                        failed = True
                        raise OSError("injected parent dup")
                    return real_dup(descriptor)

                error = None
                with mock.patch.object(self.module, "_prepare_temporary_file", side_effect=preparing), \
                    mock.patch.object(self.module.os, "link", side_effect=linking), \
                    mock.patch.object(self.module.os, "stat", side_effect=failing_stat), \
                    mock.patch.object(self.module.os, "unlink", side_effect=failing_unlink), \
                    mock.patch.object(self.module.os, "dup", side_effect=failing_dup):
                    try:
                        execute_plan(self, self.module, plan)
                    except (ValueError, RuntimeError) as caught:
                        error = caught
                if failed:
                    self.assertIsNotNone(error)
                    self.assertEqual(logical_snapshot_tree(target), before)
                else:
                    self.assertIsNone(error)
                    self.assertTrue((target / "AGENTS.md").is_file())

        for fault in ("post-mkdir-stat", "post-mkdir-dup"):
            with self.subTest(fault=fault):
                target = self.root / fault
                target.mkdir()
                plan = self.module.build_plan(self.source_root, target, "codex")
                before = logical_snapshot_tree(target)
                real_mkdir = self.module.os.mkdir
                real_stat = self.module.os.stat
                real_dup = self.module.os.dup
                created_name = None
                failed = False

                def tracking_mkdir(path, *args, **kwargs):
                    nonlocal created_name
                    result = real_mkdir(path, *args, **kwargs)
                    value = os.fspath(path)
                    if "portable-ai-workflow" in value:
                        created_name = value
                    return result

                def failing_stat(path, *args, **kwargs):
                    nonlocal failed
                    if (
                        fault == "post-mkdir-stat"
                        and created_name is not None
                        and not failed
                        and os.fspath(path) == created_name
                    ):
                        failed = True
                        raise OSError("injected post-mkdir stat")
                    return real_stat(path, *args, **kwargs)

                def failing_dup(descriptor):
                    nonlocal failed
                    if (
                        fault == "post-mkdir-dup"
                        and created_name is not None
                        and not failed
                    ):
                        failed = True
                        raise OSError("injected post-mkdir dup")
                    return real_dup(descriptor)

                error = None
                with mock.patch.object(self.module.os, "mkdir", side_effect=tracking_mkdir), \
                    mock.patch.object(self.module.os, "stat", side_effect=failing_stat), \
                    mock.patch.object(self.module.os, "dup", side_effect=failing_dup):
                    try:
                        execute_plan(self, self.module, plan)
                    except (ValueError, RuntimeError) as caught:
                        error = caught
                if failed:
                    self.assertIsNotNone(error)
                    self.assertEqual(logical_snapshot_tree(target), before)
                else:
                    self.assertIsNone(error)
                    self.assertTrue((target / "AGENTS.md").is_file())

    def test_commit_backup_failure_matrix_never_fails_after_destroying_backup(self):
        for fault in ("backup-stat", "backup-unlink", "post-unlink-fsync"):
            with self.subTest(fault=fault):
                target, plan = self._target_and_plan(f"commit-{fault}")
                gitignore = target / ".gitignore"
                original = gitignore.read_bytes()
                original_mode = stat.S_IMODE(gitignore.stat().st_mode)
                real_stat = self.module.os.stat
                real_unlink = self.module.os.unlink
                real_fsync = self.module.os.fsync
                backup_stats = 0
                backup_destroyed = False
                injected = False

                def is_backup(path):
                    value = os.fspath(path)
                    return "gitignore" in value and "portable-ai-workflow" in value

                def failing_stat(path, *args, **kwargs):
                    nonlocal backup_stats, injected
                    if is_backup(path):
                        backup_stats += 1
                        if fault == "backup-stat" and backup_stats == 2:
                            injected = True
                            raise OSError("injected backup stat")
                    return real_stat(path, *args, **kwargs)

                def failing_unlink(path, *args, **kwargs):
                    nonlocal backup_destroyed, injected
                    if is_backup(path):
                        if fault == "backup-unlink":
                            injected = True
                            raise OSError("injected backup unlink")
                        result = real_unlink(path, *args, **kwargs)
                        backup_destroyed = True
                        return result
                    return real_unlink(path, *args, **kwargs)

                def failing_fsync(descriptor):
                    nonlocal injected
                    if fault == "post-unlink-fsync" and backup_destroyed and not injected:
                        injected = True
                        raise OSError("injected post-unlink fsync")
                    return real_fsync(descriptor)

                error = None
                with mock.patch.object(self.module.os, "stat", side_effect=failing_stat), \
                    mock.patch.object(self.module.os, "unlink", side_effect=failing_unlink), \
                    mock.patch.object(self.module.os, "fsync", side_effect=failing_fsync):
                    try:
                        execute_plan(self, self.module, plan)
                    except RuntimeError as caught:
                        error = caught

                if fault == "post-unlink-fsync":
                    self.assertIsNone(error)
                    self.assertTrue(injected is False)
                    self.assertIn(managed_block("codex"), gitignore.read_bytes())
                else:
                    self.assertIsNotNone(error)
                    self.assertTrue(injected)
                    self.assertEqual(gitignore.read_bytes(), original)
                    self.assertEqual(stat.S_IMODE(gitignore.stat().st_mode), original_mode)

    def test_commit_revalidates_target_before_destroying_original_backup(self):
        target, plan = self._target_and_plan("commit-target-replacement")
        gitignore = target / ".gitignore"
        original = gitignore.read_bytes()
        replacement_content = b"replacement secret content\n"
        replacement = self.root / "replacement-gitignore"
        replacement.write_bytes(replacement_content)
        real_verify = self.module._verify_journal_bindings
        injected = False

        def replace_after_final_binding_check(actual_plan, root_fd, journal):
            nonlocal injected
            result = real_verify(actual_plan, root_fd, journal)
            if not injected and any(
                isinstance(entry, self.module._UpdatedFile) for entry in journal
            ):
                os.replace(replacement, gitignore)
                injected = True
            return result

        with mock.patch.object(
            self.module,
            "_verify_journal_bindings",
            side_effect=replace_after_final_binding_check,
        ):
            with self.assertRaises(RuntimeError) as raised:
                execute_plan(self, self.module, plan)

        self.assertTrue(injected)
        self.assertNotIn("secret content", str(raised.exception))
        self.assertEqual(gitignore.read_bytes(), replacement_content)
        backups = [
            path for path in target.iterdir()
            if "gitignore" in path.name and "portable-ai-workflow" in path.name
        ]
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_bytes(), original)
        self.assertEqual(list((target / ".ai").iterdir()), [])
        self.assertFalse((target / "AGENTS.md").exists())

    def test_commit_checks_after_backup_unlink_and_recovers_on_interrupt(self):
        for fault in ("target-replacement", "keyboard-interrupt"):
            with self.subTest(fault=fault):
                target, plan = self._target_and_plan(f"commit-after-unlink-{fault}")
                gitignore = target / ".gitignore"
                original = gitignore.read_bytes()
                original_mode = stat.S_IMODE(gitignore.stat().st_mode)
                before = logical_snapshot_tree(target)
                replacement_content = b"post-unlink replacement secret\n"
                replacement = self.root / f"replacement-{fault}"
                replacement.write_bytes(replacement_content)
                real_verify = self.module._verify_journal_bindings
                real_unlink = self.module.os.unlink
                binding_checks = 0
                injected = False

                def count_binding_checks(actual_plan, root_fd, journal):
                    nonlocal binding_checks
                    if any(
                        isinstance(entry, self.module._UpdatedFile)
                        for entry in journal
                    ):
                        binding_checks += 1
                    return real_verify(actual_plan, root_fd, journal)

                def mutate_after_backup_unlink(path, *args, **kwargs):
                    nonlocal injected
                    value = os.fspath(path)
                    if (
                        not injected
                        and binding_checks == 2
                        and "gitignore" in value
                        and "portable-ai-workflow" in value
                    ):
                        result = real_unlink(path, *args, **kwargs)
                        injected = True
                        if fault == "target-replacement":
                            os.replace(replacement, gitignore)
                            return result
                        raise KeyboardInterrupt("cancel after backup unlink")
                    return real_unlink(path, *args, **kwargs)

                caught = None
                with mock.patch.object(
                        self.module,
                        "_verify_journal_bindings",
                        side_effect=count_binding_checks,
                    ), \
                    mock.patch.object(
                        self.module.os, "unlink", side_effect=mutate_after_backup_unlink,
                    ):
                    try:
                        execute_plan(self, self.module, plan)
                    except BaseException as error:
                        caught = error

                self.assertTrue(injected)
                if fault == "target-replacement":
                    self.assertEqual(binding_checks, 3)
                    self.assertIsInstance(caught, RuntimeError)
                    self.assertIn("rollback failed", str(caught))
                    self.assertNotIn("secret", str(caught))
                    self.assertEqual(gitignore.read_bytes(), replacement_content)
                    backups = [
                        path for path in target.iterdir()
                        if "gitignore" in path.name
                        and "portable-ai-workflow" in path.name
                    ]
                    self.assertEqual(len(backups), 1)
                    self.assertEqual(backups[0].read_bytes(), original)
                    self.assertEqual(
                        stat.S_IMODE(backups[0].stat().st_mode), original_mode,
                    )
                    self.assertEqual(list((target / ".ai").iterdir()), [])
                    self.assertFalse((target / "AGENTS.md").exists())
                else:
                    self.assertIsInstance(caught, KeyboardInterrupt)
                    self.assertEqual(logical_snapshot_tree(target), before)
                    self.assertFalse(any(
                        "portable-ai-workflow" in path.name
                        for path in target.rglob("*")
                    ))


class InstallGitignoreTests(unittest.TestCase):
    def setUp(self):
        self.module = load_installer_module()
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.source_root = create_source(self.root)

    def test_missing_empty_and_existing_gitignore_bytes_and_modes(self):
        cases = (
            ("missing", None, managed_block("codex"), 0o644),
            ("empty", b"", managed_block("codex"), 0o600),
            ("no-newline", b"rule", b"rule\n\n" + managed_block("codex"), 0o600),
            ("newline", b"rule\n", b"rule\n\n" + managed_block("codex"), 0o600),
        )
        for name, original, expected, expected_mode in cases:
            with self.subTest(name=name):
                target = self.root / name
                target.mkdir()
                if original is not None:
                    gitignore = target / ".gitignore"
                    gitignore.write_bytes(original)
                    os.chmod(gitignore, 0o600)
                plan = self.module.build_plan(self.source_root, target, "codex")

                execute_plan(self, self.module, plan)

                gitignore = target / ".gitignore"
                self.assertEqual(gitignore.read_bytes(), expected)
                self.assertEqual(stat.S_IMODE(gitignore.stat().st_mode), expected_mode)

    def test_identical_complete_block_is_unchanged(self):
        target = self.root / "same"
        target.mkdir()
        gitignore = target / ".gitignore"
        gitignore.write_bytes(b"rule\n\n" + managed_block("claude"))
        os.chmod(gitignore, 0o640)
        before = snapshot_tree(target)
        plan = self.module.build_plan(self.source_root, target, "claude")
        item = next(item for item in plan.items if item.path == ".gitignore")
        self.assertEqual(item.action, "unchanged")

        execute_plan(self, self.module, plan)

        self.assertEqual(snapshot_tree(target)[".gitignore"], before[".gitignore"])

    def test_conflicting_duplicate_half_embedded_and_other_assistant_blocks_fail(self):
        block = managed_block("codex")
        start = b"# >>> portable-ai-workflow installer >>>"
        end = b"# <<< portable-ai-workflow installer <<<"
        conflicts = (
            managed_block("claude"),
            block + b"\n" + block,
            start + b"\npartial\n",
            b"partial\n" + end + b"\n",
            b"prefix " + block,
            block.replace(b"/.codex/sdd/", b"/.codex/other/"),
        )
        for index, content in enumerate(conflicts):
            with self.subTest(index=index):
                target = self.root / f"conflict-{index}"
                target.mkdir()
                gitignore = target / ".gitignore"
                gitignore.write_bytes(content)
                before = snapshot_tree(target)

                with self.assertRaises(ValueError):
                    self.module.build_plan(self.source_root, target, "codex")

                self.assertEqual(snapshot_tree(target), before)
                self.assertFalse((target / "AGENTS.md").exists())


class UpgradeLedgerTests(unittest.TestCase):
    def setUp(self):
        self.module = load_installer_module()
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.target = Path(self.temporary.name)

    def test_sha256_hex_matches_known_digest(self):
        self.assertEqual(
            self.module._sha256_hex(b"abc"),
            "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad",
        )
        self.assertEqual(self.module._sha256_hex(b""), hashlib.sha256(b"").hexdigest())

    def test_ledger_bytes_are_deterministic_and_round_trip(self):
        files = {".ai/README.md": "a" * 64, "AGENTS.md": "b" * 64}
        first = self.module._ledger_bytes("codex", files)
        second = self.module._ledger_bytes("codex", dict(reversed(list(files.items()))))
        self.assertEqual(first, second)
        self.assertTrue(first.endswith(b"\n"))
        decoded = json.loads(first.decode("utf-8"))
        self.assertEqual(decoded, {"assistant": "codex", "files": files, "schema_version": 1})

    def test_load_ledger_missing_file_is_legacy(self):
        self.assertEqual(self.module._load_ledger(self.target), {})

    def test_load_ledger_returns_files(self):
        (self.target / ".ai").mkdir()
        (self.target / ".ai" / "installer-ledger.json").write_text(json.dumps({
            "assistant": "claude", "files": {"CLAUDE.md": "c" * 64},
            "schema_version": 1,
        }), encoding="utf-8")
        self.assertEqual(
            self.module._load_ledger(self.target), {"CLAUDE.md": "c" * 64},
        )

    def test_load_ledger_malformed_fails_closed(self):
        cases = [
            {"assistant": "codex", "schema_version": 1},
            {"assistant": "codex", "schema_version": 1, "files": []},
            {"assistant": "codex", "schema_version": 1, "files": {"x": "zz"}},
            {"assistant": "codex", "schema_version": 1, "files": {"../escape": "a" * 64}},
            {"assistant": "codex", "schema_version": 2, "files": {}},
            {"schema_version": 1, "files": {}},
        ]
        (self.target / ".ai").mkdir()
        ledger = self.target / ".ai" / "installer-ledger.json"
        for payload in cases:
            ledger.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(self.module.InputError, msg=repr(payload)):
                self.module._load_ledger(self.target)

    def test_load_ledger_assistant_mismatch_fails_closed(self):
        (self.target / ".ai").mkdir()
        (self.target / ".ai" / "installer-ledger.json").write_text(json.dumps({
            "assistant": "claude", "files": {"CLAUDE.md": "c" * 64},
            "schema_version": 1,
        }), encoding="utf-8")
        with self.assertRaises(self.module.InputError):
            self.module._load_ledger(self.target, expected_assistant="codex")

    def test_profile_assistant_read_and_mismatch(self):
        self.assertIsNone(self.module._read_profile_assistant(self.target))
        (self.target / ".ai").mkdir()
        (self.target / ".ai" / "assistant-profile.json").write_text(json.dumps({
            "assistant": "codex", "schema_version": 1,
        }), encoding="utf-8")
        self.assertEqual(self.module._read_profile_assistant(self.target), "codex")
        (self.target / ".ai" / "assistant-profile.json").write_text(json.dumps({
            "assistant": "codex", "schema_version": 2,
        }), encoding="utf-8")
        with self.assertRaises(self.module.InputError):
            self.module._read_profile_assistant(self.target)


class UpgradePlanTests(unittest.TestCase):
    def setUp(self):
        self.module = load_installer_module()
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.target = Path(self.temporary.name) / "target"
        self.target.mkdir()

    def _asset(self, relative):
        return (ASSET_ROOT / "shared" / relative).read_bytes()

    def _write(self, relative, data):
        path = self.target / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    def _ledger_profile(self, files):
        return json.dumps({"assistant": "codex", "files": files, "schema_version": 1})

    def _plan(self):
        return self.module.build_upgrade_plan(REPOSITORY_ROOT, self.target, "codex")

    def _item(self, plan, path):
        matching = [entry for entry in plan.items if entry.path == path]
        self.assertEqual(len(matching), 1, f"expected exactly one item for {path}")
        return matching[0]

    def _prepare_matrix_target(self):
        old_readme = b"old readme content\n"
        modified_rules = b"locally tuned rules\n"
        removed_intact = b"legacy file intact\n"
        removed_touched = b"legacy file edited\n"
        self._write(".ai/README.md", old_readme)
        self._write(".ai/rules/index.md", self._asset(".ai/rules/index.md"))
        self._write(".ai/kb/overview.md", modified_rules)
        self._write("zz-removed-intact.txt", removed_intact)
        self._write("zz-removed-touched.txt", removed_touched)
        self._write(
            ".ai/installer-ledger.json",
            self._ledger_profile({
                ".ai/README.md": hashlib.sha256(old_readme).hexdigest(),
                ".ai/kb/overview.md": hashlib.sha256(b"old overview\n").hexdigest(),
                "zz-removed-intact.txt": hashlib.sha256(removed_intact).hexdigest(),
                "zz-removed-touched.txt": hashlib.sha256(b"old removed\n").hexdigest(),
            }).encode("utf-8"),
        )

    def test_decision_matrix_actions(self):
        self._prepare_matrix_target()
        plan = self._plan()
        self.assertEqual(self._item(plan, ".ai/README.md").action, "upgrade")
        self.assertEqual(
            self._item(plan, ".ai/README.md").source_bytes, self._asset(".ai/README.md"),
        )
        self.assertEqual(self._item(plan, ".ai/rules/index.md").action, "unchanged")
        self.assertEqual(self._item(plan, ".ai/kb/overview.md").action, "skip")
        self.assertEqual(self._item(plan, "openspec/AGENTS.md").action, "create")
        self.assertEqual(self._item(plan, "zz-removed-intact.txt").action, "remove")
        self.assertEqual(self._item(plan, "zz-removed-touched.txt").action, "kept")

    def test_profile_item_uses_lineage_ledger(self):
        self._prepare_matrix_target()
        plan = self._plan()
        profile = self._item(plan, ".ai/installer-ledger.json")
        self.assertIn(profile.action, {"create", "update", "unchanged"})
        decoded = json.loads(profile.source_bytes.decode("utf-8"))
        self.assertEqual(decoded["schema_version"], 1)
        files = decoded["files"]
        self.assertEqual(
            files[".ai/README.md"],
            hashlib.sha256(self._asset(".ai/README.md")).hexdigest(),
        )
        self.assertEqual(
            files[".ai/kb/overview.md"], hashlib.sha256(b"old overview\n").hexdigest(),
        )
        self.assertNotIn("zz-removed-intact.txt", files)
        self.assertEqual(
            files["zz-removed-touched.txt"],
            hashlib.sha256(b"old removed\n").hexdigest(),
        )

    def test_legacy_profile_downgrades_to_conservative(self):
        old_readme = b"old readme content\n"
        self._write(".ai/README.md", old_readme)
        self._write(
            ".ai/assistant-profile.json",
            json.dumps({"assistant": "codex", "schema_version": 1}).encode("utf-8"),
        )
        plan = self._plan()
        self.assertEqual(self._item(plan, ".ai/README.md").action, "skip")
        ledger = json.loads(self._item(plan, ".ai/installer-ledger.json").source_bytes)
        self.assertNotIn(".ai/README.md", ledger["files"])

    def test_existing_entry_file_is_skipped(self):
        self._write("AGENTS.md", b"team private entry\n")
        self._write(
            ".ai/installer-ledger.json",
            self._ledger_profile({
                "AGENTS.md": hashlib.sha256(b"installed entry\n").hexdigest(),
            }).encode("utf-8"),
        )
        plan = self._plan()
        item = self._item(plan, "AGENTS.md")
        self.assertEqual(item.action, "skip")
        self.assertEqual(item.source_bytes, b"team private entry\n")

    def test_structural_conflicts_still_fail_closed(self):
        (self.target / "openspec").symlink_to(self.temporary.name)
        with self.assertRaises(self.module.ConflictError):
            self._plan()


class UpgradeCliTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.source = create_source(self.root)
        self.target = self.root / "target"
        self.target.mkdir()

    def _install(self):
        return run_source_installer(
            self.source, "--target", str(self.target), "--assistant", "codex",
        )

    def _upgrade(self, *extra):
        return run_source_installer(
            self.source, "--target", str(self.target), "--assistant", "codex",
            "--upgrade", *extra,
        )

    def _set_asset(self, content: bytes):
        (self.source / "scripts" / "ai-workflow-assets" / "shared" /
         ".ai" / "README.md").write_bytes(content)

    def test_parse_arguments_accepts_single_upgrade_flag(self):
        module = load_installer_module()
        parsed = module._parse_arguments(
            ["--upgrade", "--target", str(self.target), "--assistant", "codex"],
        )
        self.assertTrue(parsed.upgrade)
        parsed_without = module._parse_arguments(
            ["--target", str(self.target), "--assistant", "codex"],
        )
        self.assertFalse(parsed_without.upgrade)
        with self.assertRaises(module.UsageError):
            module._parse_arguments([
                "--upgrade", "--upgrade", "--target", str(self.target),
                "--assistant", "codex",
            ])

    def test_usage_documents_upgrade(self):
        module = load_installer_module()
        self.assertIn("--upgrade", module.USAGE)

    def test_upgrade_replaces_untouched_and_reports(self):
        installed = self._install()
        self.assertEqual(installed.returncode, 0, installed.stderr or installed.stdout)
        self._set_asset(b"shared v2\n")
        upgraded = self._upgrade()
        self.assertEqual(upgraded.returncode, 0, upgraded.stderr or upgraded.stdout)
        self.assertIn("[UPGRADED] .ai/README.md", upgraded.stdout)
        self.assertRegex(
            upgraded.stdout, r"RESULT assistant=codex target=.+ upgraded=1 ",
        )
        self.assertEqual(
            (self.target / ".ai" / "README.md").read_bytes(), b"shared v2\n",
        )
        ledger = json.loads(
            (self.target / ".ai" / "installer-ledger.json").read_text("utf-8"),
        )
        self.assertEqual(ledger["schema_version"], 1)

    def test_upgrade_skips_locally_modified_file_with_exit_zero(self):
        self._install()
        (self.target / ".ai" / "README.md").write_bytes(b"local tweak\n")
        self._set_asset(b"shared v2\n")
        upgraded = self._upgrade()
        self.assertEqual(upgraded.returncode, 0, upgraded.stderr or upgraded.stdout)
        self.assertIn("[SKIPPED] .ai/README.md", upgraded.stdout)
        self.assertEqual(
            (self.target / ".ai" / "README.md").read_bytes(), b"local tweak\n",
        )

    def test_upgrade_removes_intact_and_keeps_modified_orphans(self):
        self._install()
        ledger_path = self.target / ".ai" / "installer-ledger.json"
        ledger = json.loads(ledger_path.read_text("utf-8"))
        ledger["files"]["zz-orphan.txt"] = hashlib.sha256(b"orphan\n").hexdigest()
        ledger["files"]["zz-edited.txt"] = hashlib.sha256(b"edited-old\n").hexdigest()
        ledger_path.write_text(json.dumps(ledger), encoding="utf-8")
        (self.target / "zz-orphan.txt").write_bytes(b"orphan\n")
        (self.target / "zz-edited.txt").write_bytes(b"edited-new\n")
        self._set_asset(b"shared v2\n")
        upgraded = self._upgrade()
        self.assertEqual(upgraded.returncode, 0, upgraded.stderr or upgraded.stdout)
        self.assertIn("[REMOVED] zz-orphan.txt", upgraded.stdout)
        self.assertIn("[KEPT] zz-edited.txt", upgraded.stdout)
        self.assertFalse((self.target / "zz-orphan.txt").exists())
        self.assertEqual(
            (self.target / "zz-edited.txt").read_bytes(), b"edited-new\n",
        )

    def test_upgrade_replaces_unmodified_entry_file(self):
        self._install()
        (self.source / "scripts" / "ai-workflow-assets" / "codex" /
         "AGENTS.md").write_bytes(b"codex v2\n")
        upgraded = self._upgrade()
        self.assertEqual(upgraded.returncode, 0, upgraded.stderr or upgraded.stdout)
        self.assertIn("[UPGRADED] AGENTS.md", upgraded.stdout)
        self.assertEqual(
            (self.target / "AGENTS.md").read_bytes(), b"codex v2\n",
        )

    def test_upgrade_mixes_skip_and_upgrade_with_notes(self):
        self._install()
        (self.target / ".ai" / "README.md").write_bytes(b"local tweak\n")
        self._set_asset(b"shared v2\n")
        (self.source / "scripts" / "ai-workflow-assets" / "codex" /
         "AGENTS.md").write_bytes(b"codex v2\n")
        upgraded = self._upgrade()
        self.assertEqual(upgraded.returncode, 0, upgraded.stderr or upgraded.stdout)
        self.assertIn(
            "[SKIPPED] .ai/README.md（目标已修改，保留；请人工比对新版）",
            upgraded.stdout,
        )
        self.assertIn("[UPGRADED] AGENTS.md", upgraded.stdout)
        self.assertRegex(upgraded.stdout, r"RESULT .*upgraded=1 .*skipped=1 ")

    def test_upgrade_rejects_assistant_mismatch_at_plan_level(self):
        self._install()
        module = load_installer_module()
        with self.assertRaises(module.InputError) as raised:
            module.build_upgrade_plan(self.source, self.target, "claude")
        self.assertIn("different assistant", str(raised.exception))

    def test_upgrade_dry_run_writes_nothing(self):
        self._install()
        self._set_asset(b"shared v2\n")
        before = logical_snapshot_tree(self.target)
        preview = self._upgrade("--dry-run")
        self.assertEqual(preview.returncode, 0, preview.stderr or preview.stdout)
        self.assertIn("[UPGRADED] .ai/README.md", preview.stdout)
        self.assertIn("dry_run=1", preview.stdout)
        self.assertEqual(logical_snapshot_tree(self.target), before)


class UpgradeTransactionTests(unittest.TestCase):
    def setUp(self):
        self.module = load_installer_module()
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.source_root = create_source(self.root)

    def _prepared_target(self, name, version=2):
        target = self.root / name
        target.mkdir()
        installed = run_source_installer(
            self.source_root, "--target", str(target), "--assistant", "codex",
        )
        self.assertEqual(installed.returncode, 0, installed.stderr or installed.stdout)
        (self.source_root / "scripts" / "ai-workflow-assets" / "shared" /
         ".ai" / "README.md").write_bytes(f"shared v{version}\n".encode("utf-8"))
        ledger_path = target / ".ai" / "installer-ledger.json"
        ledger = json.loads(ledger_path.read_text("utf-8"))
        ledger["files"]["zz-orphan.txt"] = hashlib.sha256(b"orphan\n").hexdigest()
        ledger_path.write_text(json.dumps(ledger), encoding="utf-8")
        (target / "zz-orphan.txt").write_bytes(b"orphan\n")
        return target

    def test_publish_failure_rolls_back_files_and_ledger(self):
        matrix = (
            ("publish", 1), ("publish", 2), ("publish", 3),
            ("fsync", 2), ("fsync", 5),
        )
        for index, (operation, fail_at) in enumerate(matrix):
            with self.subTest(operation=operation, fail_at=fail_at):
                target = self._prepared_target(
                    f"target-{operation}-{fail_at}", version=2 + index,
                )
                plan = self.module.build_upgrade_plan(
                    self.source_root, target, "codex",
                )
                before = logical_snapshot_tree(target)
                calls = 0

                def inject(actual):
                    nonlocal calls
                    if actual != operation:
                        return
                    calls += 1
                    if calls == fail_at:
                        raise OSError("injected fault")

                with mock.patch.object(
                    self.module, "_fault_point", side_effect=inject,
                ):
                    with self.assertRaises((OSError, RuntimeError)):
                        self.module.execute_plan(plan)

                self.assertEqual(logical_snapshot_tree(target), before)

    def test_remove_publish_window_failure_restores_original_path(self):
        target = self._prepared_target("target-window", version=11)
        orphan = target / "zz-orphan.txt"
        original = orphan.read_bytes()
        plan = self.module.build_upgrade_plan(self.source_root, target, "codex")
        publishes = 0

        def chmod_at_remove_publish(operation):
            nonlocal publishes
            if operation != "publish":
                return
            publishes += 1
            if publishes == 3:
                os.chmod(orphan, 0o600)

        with mock.patch.object(
            self.module, "_fault_point", side_effect=chmod_at_remove_publish,
        ):
            with self.assertRaises((ValueError, RuntimeError)):
                self.module.execute_plan(plan)

        self.assertTrue(orphan.is_file(), "orphan must be restored to its path")
        self.assertEqual(orphan.read_bytes(), original)
        leftovers = [p.name for p in target.rglob("*.tmp")]
        self.assertEqual(leftovers, [])

    def test_commit_partial_destruction_rolls_back_via_recovery(self):
        target = self._prepared_target("target-commit-partial", version=12)
        plan = self.module.build_upgrade_plan(self.source_root, target, "codex")
        before = logical_snapshot_tree(target)
        real_verify = self.module._verify_journal_bindings
        single_calls = 0

        def fail_after_first_destruction(plan_arg, root_fd, entries):
            nonlocal single_calls
            if len(entries) != 1:
                return real_verify(plan_arg, root_fd, entries)
            single_calls += 1
            if single_calls == 2:
                raise ConflictError("injected post-unlink failure")
            return real_verify(plan_arg, root_fd, entries)

        with mock.patch.object(
            self.module, "_verify_journal_bindings",
            side_effect=fail_after_first_destruction,
        ):
            with self.assertRaises((ValueError, RuntimeError)):
                self.module.execute_plan(plan)

        self.assertEqual(logical_snapshot_tree(target), before)
        leftovers = [p.name for p in target.rglob("*.tmp")]
        self.assertEqual(leftovers, [])

    def test_upgrade_commits_leave_no_backup_artifacts(self):
        target = self._prepared_target("target-commit", version=9)
        result = run_source_installer(
            self.source_root, "--target", str(target), "--assistant", "codex",
            "--upgrade",
        )
        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
        leftovers = [
            path.name for path in target.rglob("*.tmp")
            if "portable-ai-workflow" in path.name
        ]
        self.assertEqual(leftovers, [])
        self.assertEqual(
            (target / ".ai" / "README.md").read_bytes(), b"shared v9\n",
        )
        self.assertFalse((target / "zz-orphan.txt").exists())
        ledger = json.loads(
            (target / ".ai" / "installer-ledger.json").read_text("utf-8"),
        )
        self.assertEqual(
            ledger["files"][".ai/README.md"],
            hashlib.sha256(b"shared v9\n").hexdigest(),
        )


if __name__ == "__main__":
    unittest.main()
