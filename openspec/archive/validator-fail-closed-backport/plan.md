# 实现计划：validator-fail-closed-backport

零上下文可执行。所有路径相对仓库根。外部事实源：meta 库修复版位于 `/home/shitou/workspace/src/yuxiaor_prj_2025/scripts/`（只读参考，不修改）。

## 目标

把 meta 库 fail-closed 加固移植进本仓库并随资产模板发布：wrapper 2 处、core 2 函数、7 个回归测试（6 个移植 + 1 个计数整数化加强）、3 份资产模板镜像同步。

## 全局约束（逐字遵守）

- 汇总行 `PASS=%d FAIL=%d SKIP=%d` 保持输出末行；契约套件内部跳过不计入顶层 SKIP 字段。
- 检查名不得改：`归档索引与目录 1:1`、`废弃工具名零残留`。
- 空归档且无 README 的 vacuous 通过语义保持。
- 修复后 `scripts/lib/validate-workflow-core.sh --print-external-commands` 输出与修复前逐字一致（新代码只新增 bash 内建与已声明命令的使用：shopt/test/printf 为内建，grep/sed/sort/awk/cmp/mktemp 均已声明）。
- `manifest.json`、`workflow-pressure-scenarios.md`、`scripts/hooks/` 不改。
- 提交前 `scripts/validate-workflow.sh`（运行副本）与 `scripts/ai-workflow-assets/shared/scripts/` 三对文件逐字节一致。

## 任务

### T0 计划确认后的分支与 worktree（原子顺序，不得颠倒）

1. `git branch --show-current` 记录基线分支（预期 `main`）；`git status --short` 仅含本变更 5 个文件（`openspec/changes/validator-fail-closed-backport/` 四件套 + `openspec/plan/validator-fail-closed-backport.md`）。
2. 创建并切换 `feature/validator-fail-closed-backport`；proposal 状态置`构建中`；仅暂存上述 5 文件并提交 `docs(openspec): validator-fail-closed-backport 四件套与实现计划`。
3. 切回基线分支后 `git worktree add .worktrees/validator-fail-closed-backport feature/validator-fail-closed-backport`，进入该 worktree 执行后续任务；开工前核对 `git branch --show-current` 为 feature 分支且 `git status --short` 干净。

### T1 测试先行（红）——Modify `scripts/tests/test_validate_workflow.py`

全部加在 `ValidateWorkflowContractTest` 类内。

**(a) 提取公共 helper**：把 `test_public_entry_surfaces_contract_suite_internal_skips`（现约 :1160-1176）中「写 stub 契约套件 + 写 python3 透传 stub + 以 `PATH=stub_bin` 运行 `scripts/validate-workflow.sh`（timeout=120）」的机制提为：

```python
    def _run_public_entry_with_contract_skip(
        self, *arguments: str
    ) -> subprocess.CompletedProcess[str]:
        contract_test = self.fixture / "scripts/tests/test_validate_workflow.py"
        contract_test.write_text(
            "import unittest\n\n"
            "class InstalledContract(unittest.TestCase):\n"
            "    def test_ok(self):\n"
            "        self.assertTrue(True)\n\n"
            "    def test_skipped(self):\n"
            "        self.skipTest('source-repository only')\n",
            encoding="utf-8",
        )
        # 默认 stub 只处理 profile 解析；这里让契约套件真正跑起来，
        # 但 tools discover 仍走 stub（保持秒级）。
        self._write_executable(
            "python3",
            "#!/bin/sh\n"
            "if test \"$1\" = \"-B\" && test \"$2\" = \"-c\"; then\n"
            f"  exec {sys.executable} \"$@\"\n"
            "fi\n"
            "if test \"$1\" = \"-B\" && test \"$2\" = \"-m\" && test \"$4\" != \"discover\"; then\n"
            f"  exec {sys.executable} \"$@\"\n"
            "fi\n"
            "exit 0\n",
        )
        environment = {"LC_ALL": "C.UTF-8", "PATH": str(self.stub_bin)}
        return subprocess.run(
            ["/usr/bin/bash", "scripts/validate-workflow.sh", *arguments],
            cwd=self.fixture,
            env=environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
            timeout=120,
        )
```

原测试改调该 helper，断言全部保持不变（含 `PASS=\d+ FAIL=0 SKIP=1\s*\Z`）。

**(b) 新增 7 个测试**（第 1–3 个归档域测试放在 `test_empty_archive_without_index_still_passes` 之后；第 4–6 个公共入口测试放在原跳过透明化测试之后；第 7 个放在 `test_rejects_retired_codex_tool_names` 附近）。逐字采用以下代码（源自 meta 库已归档实现，仅第 5 个为本计划新增）：

```python
    def test_archive_index_does_not_require_gnu_find_printf(self) -> None:
        marker = self.stub_bin.parent / "gnu-find-argument-used"
        real_find = (self.stub_bin / "find").resolve()
        (self.stub_bin / "find").unlink()
        self._write_executable(
            "find",
            "#!/bin/sh\n"
            "for argument in \"$@\"; do\n"
            "  if test \"$argument\" = \"-printf\"; then\n"
            f"    : > \"{marker}\"\n"
            "    exit 64\n"
            "  fi\n"
            "done\n"
            f"exec \"{real_find}\" \"$@\"\n",
        )

        archive = self.fixture / "openspec/archive"
        backup = tempfile.TemporaryDirectory()
        self.addCleanup(backup.cleanup)
        shutil.move(str(archive), backup.name)
        archive.mkdir()
        readme = archive / "README.md"
        try:
            empty_result = self._run_validator()
            empty_used_gnu_find = marker.exists()
            marker.unlink(missing_ok=True)

            (archive / ".hidden-change").mkdir()
            readme.write_text(
                "# 归档变更索引\n\n- `.hidden-change` — 隐藏归档(严格)\n",
                encoding="utf-8",
            )
            populated_result = self._run_validator()
            populated_used_gnu_find = marker.exists()

            self.assertEqual(
                (0, False, 0, False),
                (
                    empty_result.returncode,
                    empty_used_gnu_find,
                    populated_result.returncode,
                    populated_used_gnu_find,
                ),
                msg=(
                    f"empty:\n{empty_result.stdout}\n"
                    f"populated:\n{populated_result.stdout}"
                ),
            )
        finally:
            shutil.rmtree(archive, ignore_errors=True)
            shutil.move(
                str(Path(backup.name) / "archive"), str(archive.parent)
            )

    def test_archive_index_rejects_all_directory_symlinks(self) -> None:
        archive = self.fixture / "openspec/archive"
        backup = tempfile.TemporaryDirectory()
        self.addCleanup(backup.cleanup)
        shutil.move(str(archive), backup.name)
        archive.mkdir()
        readme = archive / "README.md"
        outside = Path(self.temporary_directory.name) / "outside-archive"
        outside.mkdir()

        def write_index(*names: str) -> None:
            lines = "".join(f"- `{name}` — 受控归档(严格)\n" for name in names)
            readme.write_text(f"# 归档变更索引\n\n{lines}", encoding="utf-8")

        try:
            (archive / "real-change").mkdir()
            (archive / ".hidden-change").mkdir()
            base_names = ("real-change", ".hidden-change")
            write_index(*base_names)
            baseline = self._run_validator()

            internal_link = archive / "internal-link"
            internal_link.symlink_to("real-change", target_is_directory=True)
            write_index(*base_names, "internal-link")
            internal = self._run_validator()
            internal_link.unlink()

            external_link = archive / "external-link"
            external_link.symlink_to(outside, target_is_directory=True)
            write_index(*base_names, "external-link")
            external = self._run_validator()
            external_link.unlink()

            dangling_link = archive / "dangling-link"
            dangling_link.symlink_to("missing-change", target_is_directory=True)
            write_index(*base_names)
            dangling = self._run_validator()

            self.assertEqual(
                (0, True, True, True),
                (
                    baseline.returncode,
                    internal.returncode != 0,
                    external.returncode != 0,
                    dangling.returncode != 0,
                ),
                msg=(
                    f"baseline:\n{baseline.stdout}\n"
                    f"internal:\n{internal.stdout}\n"
                    f"external:\n{external.stdout}\n"
                    f"dangling:\n{dangling.stdout}"
                ),
            )
        finally:
            shutil.rmtree(archive, ignore_errors=True)
            shutil.move(
                str(Path(backup.name) / "archive"), str(archive.parent)
            )

    def test_archive_index_sort_errors_fail_closed(self) -> None:
        (self.stub_bin / "sort").unlink()
        self._write_executable("sort", "#!/bin/sh\nexit 64\n")

        result = self._run_validator()

        self.assertNotEqual(result.returncode, 0, msg=result.stdout)
        self.assertIn("[FAIL] 归档索引与目录 1:1", result.stdout)

    def test_public_entry_fails_closed_when_skip_count_grep_errors(self) -> None:
        real_grep = (self.stub_bin / "grep").resolve()
        (self.stub_bin / "grep").unlink()
        self._write_executable(
            "grep",
            "#!/bin/sh\n"
            "if test \"$1\" = \"-c\" && test \"$2\" = '\\.\\.\\. skipped'; then\n"
            "  exit 64\n"
            "fi\n"
            f"exec \"{real_grep}\" \"$@\"\n",
        )

        result = self._run_public_entry_with_contract_skip()

        self.assertNotEqual(result.returncode, 0, msg=result.stdout)
        self.assertIn("[FAIL] 契约套件内部跳过计数解析失败", result.stdout)

    def test_public_entry_fails_closed_when_skip_count_is_not_an_integer(self) -> None:
        real_grep = (self.stub_bin / "grep").resolve()
        (self.stub_bin / "grep").unlink()
        self._write_executable(
            "grep",
            "#!/bin/sh\n"
            "if test \"$1\" = \"-c\" && test \"$2\" = '\\.\\.\\. skipped'; then\n"
            "  printf 'x\\n'\n"
            "  exit 0\n"
            "fi\n"
            f"exec \"{real_grep}\" \"$@\"\n",
        )

        result = self._run_public_entry_with_contract_skip()

        self.assertNotEqual(result.returncode, 0, msg=result.stdout)
        self.assertIn("[FAIL] 契约套件内部跳过计数解析失败", result.stdout)

    def test_public_entry_fails_closed_when_skip_render_sed_errors(self) -> None:
        real_sed = (self.stub_bin / "sed").resolve()
        (self.stub_bin / "sed").unlink()
        self._write_executable(
            "sed",
            "#!/bin/sh\n"
            "for argument in \"$@\"; do\n"
            "  case \"$argument\" in\n"
            "    *'s/^/  - /'*) exit 64 ;;\n"
            "  esac\n"
            "done\n"
            f"exec \"{real_sed}\" \"$@\"\n",
        )

        result = self._run_public_entry_with_contract_skip()

        self.assertNotEqual(result.returncode, 0, msg=result.stdout)
        self.assertIn("[FAIL] 契约套件内部跳过明细渲染失败", result.stdout)

    def test_retired_tool_scan_errors_fail_closed(self) -> None:
        real_grep = (self.stub_bin / "grep").resolve()
        (self.stub_bin / "grep").unlink()
        self._write_executable(
            "grep",
            "#!/bin/sh\n"
            "for argument in \"$@\"; do\n"
            "  if test \"$argument\" = \"multi_agent_v1__spawn_agent\"; then\n"
            "    exit 64\n"
            "  fi\n"
            "done\n"
            f"exec \"{real_grep}\" \"$@\"\n",
        )

        result = self._run_validator()

        self.assertNotEqual(result.returncode, 0, msg=result.stdout)
        self.assertIn("[FAIL] 废弃工具名零残留", result.stdout)
```

**Test（预期红）**：`python3 -B -m unittest scripts.tests.test_validate_workflow -v 2>&1 | tail -40`

预期恰好 6 失败 1 通过（新测试中）：`...gnu_find_printf`（空归档 marker 命中为 True + 非空归档 rc!=0）、`...symlinks`（dangling 分支 rc==0）、`...skip_count_grep_errors`、`...skip_count_is_not_an_integer`、`...skip_render_sed_errors`、`...retired_tool_scan_errors`（四者 rc==0 无 FAIL 行）；`...sort_errors_fail_closed` 通过（当前实现对非空归档碰巧也失败，属不变量守护）。既有测试全绿；`test_public_entry_surfaces_contract_suite_internal_skips` 重构后仍绿。

### T2 core 修复（绿）——Modify `scripts/lib/validate-workflow-core.sh`

前置：`bash scripts/lib/validate-workflow-core.sh --print-external-commands > /tmp/extcmds.before`。

**(a) `retired_tool_names_absent`（约 :443）整函数替换为**：

```bash
retired_tool_names_absent() {
  local candidates=(.codex/skills .claude/skills .codex/README.md scripts/ai-workflow-assets)
  local targets=() path token grep_status
  for path in "${candidates[@]}"; do
    test -e "$path" && targets+=("$path")
  done
  test "${#targets[@]}" -gt 0 || return 0
  for token in 'multi_agent_v1__spawn_agent' 'send_input' 'close_agent' 'fork_context'; do
    grep -R -F -q --include='*.md' --include='*.toml' \
      -e "$token" -- "${targets[@]}"
    grep_status=$?
    case "$grep_status" in
      0) return 1 ;;
      1) ;;
      *) return 1 ;;
    esac
  done
  return 0
}
```

（函数前的 4 行注释与现行为相同，保留不动。）

**(b) `archive_index_ok`（约 :478）整函数连同前导注释替换为**：

```bash
# 归档索引与目录严格 1:1：缺失、悬空、重复都视为归档数据不完整。
# 空归档且无 README（安装目标空白基线）为 vacuous 通过。
archive_index_ok() {
  local readme=openspec/archive/README.md
  local dirs_unsorted dirs entries_unsorted entries path
  local archive_paths=() archive_names=()
  local dotglob_was_set=0 nullglob_was_set=0
  local enumeration_status=0 restore_status=0 awk_status
  dirs_unsorted="$(mktemp)" || return 1
  dirs="$(mktemp)" || { rm -f "$dirs_unsorted"; return 1; }
  entries_unsorted="$(mktemp)" || { rm -f "$dirs_unsorted" "$dirs"; return 1; }
  entries="$(mktemp)" || { rm -f "$dirs_unsorted" "$dirs" "$entries_unsorted"; return 1; }
  shopt -q dotglob && dotglob_was_set=1
  shopt -q nullglob && nullglob_was_set=1
  if ! shopt -s dotglob nullglob; then
    rm -f "$dirs_unsorted" "$dirs" "$entries_unsorted" "$entries"
    return 1
  fi
  archive_paths=(openspec/archive/*) || enumeration_status=$?
  if test "$dotglob_was_set" -eq 0; then
    shopt -u dotglob || restore_status=1
  fi
  if test "$nullglob_was_set" -eq 0; then
    shopt -u nullglob || restore_status=1
  fi
  if test "$enumeration_status" -ne 0 || test "$restore_status" -ne 0; then
    rm -f "$dirs_unsorted" "$dirs" "$entries_unsorted" "$entries"
    return 1
  fi
  for path in "${archive_paths[@]}"; do
    if test -L "$path"; then
      rm -f "$dirs_unsorted" "$dirs" "$entries_unsorted" "$entries"
      return 1
    fi
    test -d "$path" && archive_names+=("${path##*/}")
  done
  for path in "${archive_names[@]}"; do
    if ! printf '%s\n' "$path" >>"$dirs_unsorted"; then
      rm -f "$dirs_unsorted" "$dirs" "$entries_unsorted" "$entries"
      return 1
    fi
  done
  if ! sort "$dirs_unsorted" >"$dirs"; then
    rm -f "$dirs_unsorted" "$dirs" "$entries_unsorted" "$entries"
    return 1
  fi
  if test -s "$dirs" && ! test -f "$readme"; then
    rm -f "$dirs_unsorted" "$dirs" "$entries_unsorted" "$entries"
    return 1
  fi
  if test -f "$readme"; then
    if ! sed -n 's/^- `\([^`]*\)`.*/\1/p' "$readme" >"$entries_unsorted"; then
      rm -f "$dirs_unsorted" "$dirs" "$entries_unsorted" "$entries"
      return 1
    fi
    if ! sort "$entries_unsorted" >"$entries"; then
      rm -f "$dirs_unsorted" "$dirs" "$entries_unsorted" "$entries"
      return 1
    fi
    awk 'seen[$0]++ { found = 1 } END { exit !found }' "$entries"
    awk_status=$?
    case "$awk_status" in
      0)
        rm -f "$dirs_unsorted" "$dirs" "$entries_unsorted" "$entries"
        return 1
        ;;
      1) ;;
      *)
        rm -f "$dirs_unsorted" "$dirs" "$entries_unsorted" "$entries"
        return 1
        ;;
    esac
    if ! cmp -s "$dirs" "$entries"; then
      rm -f "$dirs_unsorted" "$dirs" "$entries_unsorted" "$entries"
      return 1
    fi
  fi
  rm -f "$dirs_unsorted" "$dirs" "$entries_unsorted" "$entries"
}
```

**Test（部分绿）**：
- `bash scripts/lib/validate-workflow-core.sh --print-external-commands | diff /tmp/extcmds.before -` → 无输出。
- `python3 -B -m unittest scripts.tests.test_validate_workflow -v 2>&1 | tail -15` → 新测试中 `gnu_find_printf`、`symlinks`、`sort_errors`、`retired_tool_scan` 4 个转绿；3 个公共入口测试仍红（wrapper 未修）；既有全绿。

### T3 wrapper 修复（绿）——Modify `scripts/validate-workflow.sh`

替换契约套件通过分支中 `contract_skips="$(grep -c ...)"` 至 `grep ... | sed ...` 的整块（现约 :88-93）为：

```bash
  contract_skip_status=0
  contract_skips="$(grep -c '\.\.\. skipped' "$contract_output")" || contract_skip_status=$?
  case "$contract_skip_status" in
    0|1)
      case "$contract_skips" in
        ""|*[!0-9]*)
          printf "[FAIL] 契约套件内部跳过计数解析失败（结果必须为非负整数）\n"
          fail_count=$((fail_count + 1))
          contract_skips=0
          ;;
      esac
      ;;
    *)
      printf "[FAIL] 契约套件内部跳过计数解析失败（grep exit %d）\n" "$contract_skip_status"
      fail_count=$((fail_count + 1))
      contract_skips=0
      ;;
  esac
  if test "$contract_skips" -gt 0; then
    printf "  契约套件内部设计性跳过 %d 项（源仓专属能力；不影响门禁计数）:\n" "$contract_skips"
    sed -n '/\.\.\. skipped/{s/^/  - /;p;}' "$contract_output"
    contract_skip_render_status=$?
    if test "$contract_skip_render_status" -ne 0; then
      printf "[FAIL] 契约套件内部跳过明细渲染失败（sed exit %d）\n" "$contract_skip_render_status"
      fail_count=$((fail_count + 1))
    fi
  fi
```

（`contract_skip_render_status=$?` 必须紧跟 sed 行，中间不得插入任何命令。）

**Test（全绿）**：
- `python3 -B -m unittest scripts.tests.test_validate_workflow -v 2>&1 | tail -5` → OK，0 失败。
- `bash scripts/validate-workflow.sh --fast 2>&1 | tail -1` → `PASS=197 FAIL=0 SKIP=0`。

### T4 资产模板同步——Modify `scripts/ai-workflow-assets/shared/scripts/`

```bash
cp scripts/validate-workflow.sh scripts/ai-workflow-assets/shared/scripts/validate-workflow.sh
cp scripts/lib/validate-workflow-core.sh scripts/ai-workflow-assets/shared/scripts/lib/validate-workflow-core.sh
cp scripts/tests/test_validate_workflow.py scripts/ai-workflow-assets/shared/scripts/tests/test_validate_workflow.py
diff -q scripts/validate-workflow.sh scripts/ai-workflow-assets/shared/scripts/validate-workflow.sh
diff -q scripts/lib/validate-workflow-core.sh scripts/ai-workflow-assets/shared/scripts/lib/validate-workflow-core.sh
diff -q scripts/tests/test_validate_workflow.py scripts/ai-workflow-assets/shared/scripts/tests/test_validate_workflow.py
```

三个 `diff -q` 均无输出。

**Test**：`python3 -B -m unittest scripts.tests.test_install_ai_workflow scripts.tests.test_install_workflow -v 2>&1 | tail -5` → OK（套件内部 `_run_target` 超时已为 900s，无预存失配；若有源仓专属 SKIP 属契约允许）。

### T5 全量门禁与提交

1. `bash scripts/validate-workflow.sh 2>&1 | tail -3` → 末行 `PASS=… FAIL=0 SKIP=…`，无新增 FAIL。
2. `git diff --check` → 无输出。
3. 单一职责单元提交：`fix(workflow): 校验器 fail-closed 加固回流自 meta 库（运行副本+资产模板）`——含 T1–T4 全部文件，不夹带其他改动。

## 提交单元

| 提交 | 内容 | 回滚 |
|---|---|---|
| C1（T0） | 四件套 + 本计划 + `构建中` 状态 | revert 恢复待确认计划态 |
| C2（T5） | T1–T4 测试、修复、模板同步 | 单 revert 即回现状，无中间不一致态 |
| C3（Verify/Archive 阶段） | 审查产物、主规格合并、memory、归档 | 后续阶段另行处理 |

## 风险与回滚

- 符号链接拒绝为行为收紧：当前 `openspec/archive/` 无符号链接（已核对），无存量影响。
- 测试 3（sort 错误）在修复前后均绿，定位为不变量守护而非红-绿测试；红灯判定以其余 6 个为准。
- C2 一次 revert 即回到当前全绿基线；模板与运行副本在同一次提交内保持逐字节一致，不存在分叉窗口。
