# 实现计划：add-installer-upgrade-path

## 目标与上下文

- 四件套：`openspec/changes/add-installer-upgrade-path/`（proposal/design/tasks/delta）。本计划为严格模式独立实现计划。
- 交付：`--upgrade` 台账驱动升级；profile schema v2；四值判定＋REMOVED/KEPT；事务内台账原子更新。
- **这是运行时 Python 行为——全程 TDD**：每个职责单元先写失败测试、亲见其红、再最小实现、跑绿、重构。禁止先写实现。
- 关键既有锚点（`scripts/lib/install_ai_workflow.py`，行号为 2026-08-28 main 状态）：
  - `_target_action` :367（create/unchanged/ConflictError）
  - `_profile_bytes` :392、`_gitignore_block` :401、`_plan_gitignore` :412
  - `build_plan` :535（manifest 选择＋requested 列表＋捕获目标状态）
  - `execute_plan` :1272（dry-run 短路；**重建 plan 比对再验证**；journal 发布/回滚；action 仅认 create/update/unchanged）
  - `_parse_arguments` :1354、`_print_plan` :1379、`main` :1394（USAGE :17）
  - journal 原语：`_CreatedFile/_UpdatedFile` :581-610、`_publish_created_file/_publish_updated_file`、`_commit_journal/_rollback_journal`
- 测试约定（`scripts/tests/test_install_ai_workflow.py`，1918 行）：真实 `ASSET_ROOT` 作源、`tempfile` 目标、模块直载＋CLI 子进程双通道；按方面分类 TestCase（参照 `InstallDryRunTests` :795、`InstallConflictTests` :1024、`InstallRollbackTests` :1255 的 setUp 形态）。
- Python 3.8 约束：新代码不得使用 3.9+ 语法（类型标注用 `typing.Dict/Tuple/Optional` 导入式，禁 `list[str]` 于运行位置——沿用文件现有 `from __future__ import annotations` 头部做法即可，但运行时求值处仍需 3.8 安全）。

## 全局约束（逐字适用）

- 保护目标项目用户修改：判定为 SKIPPED/KEPT 的文件零触碰；结构性冲突（symlink/类型/受管块损坏）fail-closed。
- 事务语义不削弱：台账与文件同批原子发布，中断回滚后磁盘与台账回到升级前逐字节状态。
- 默认安装路径行为零改动（既有 1918 行测试全绿是硬门禁）。
- 提交按可独立回滚职责单元；测试与实现同单元提交。

## 任务 1：台账数据层（红→绿）

Create/Modify：`scripts/lib/install_ai_workflow.py`；`scripts/tests/test_install_ai_workflow.py` 新增 `UpgradeLedgerTests`。

1. 红：先写测试（预期 ImportError/AttributeError 红）：
   - `_profile_bytes_v2(assistant, files)` 产出确定性 JSON（sort_keys、缩进 2、尾换行），`files` 为 `Dict[str, str]`；
   - `_load_profile(target)`：v2 合法 → dict；v1（schema_version 1 或无 files）→ `{"schema_version": 1}`；v2 但 files 值非 64 位 hex/路径越界/非 dict → `InputError`；
   - `_sha256_hex(bytes)`。
2. 绿：实现上述三个纯函数（不触 plan/execute）。
3. 验证：`python3 -m unittest scripts.tests.test_install_ai_workflow.UpgradeLedgerTests -v` 全绿；`python3 -m py_compile scripts/lib/install_ai_workflow.py`。

提交：`feat(installer): add upgrade ledger data layer`

## 任务 2：升级计划构建（红→绿）

Modify：同上；新增 `UpgradePlanTests`（含决策矩阵）。

1. 红：测试 `build_upgrade_plan(source_root, target_input, assistant)`：
   - 目标文件 hash=台账旧值且≠新版 → action `upgrade`，item.content=新版字节；
   - =新版 → `unchanged`；目标缺失 → `create`；≠台账且≠新版 → `skip`（item 保留 content=目标当前字节用于谱系比对，但 execute 不写）；
   - 台账有＋新 manifest 无：hash=台账 → `remove`；否则 `kept`；
   - legacy v1：全部走 ≠新版→`skip` / =新版→`unchanged`；
   - profile 恒为 create/update/unchanged（新 profile 字节＝v2 台账：UPGRADED/CREATED/UNCHANGED 记新版 hash、SKIPPED/KEPT 沿用旧条目、REMOVED 删条目——**资产谱系哈希语义，design D1 修正版**）；
   - `.gitignore` 沿用 `_plan_gitignore` 结果；入口文件（AGENTS.md/CLAUDE.md）已存在 → `skip`＋标记，不产生写动作；
   - symlink/父目录非目录/非常规文件 → ConflictError（沿用 `_target_action` 结构检查路径）。
2. 绿：实现 `build_upgrade_plan`（复用 `build_plan` 骨架：manifest 载入、路径唯一性、`_capture_plan_target_state`；新增台账读取与四值判定函数 `_upgrade_action(target, path, new_bytes, ledger)`）。
3. 验证：决策矩阵测试全绿（≥12 用例覆盖上述每行）；`InstallManifestTests` 等既有套件不回归。

提交：`feat(installer): build ledger-driven upgrade plans`

## 任务 3：CLI 与报告（红→绿）

1. 红：`UpgradeCliTests`：
   - `--upgrade` 可选一次、重复报 UsageError；USAGE 文本含 `--upgrade`；`--help` 输出更新；
   - `ParsedArguments.upgrade` 字段存在且默认 False；
   - `main(["--upgrade", ...])` 分派 `build_upgrade_plan`；
   - 报告（`_print_plan` 升级变体）：逐行 `[UPGRADED|UNCHANGED|CREATED|SKIPPED|REMOVED|KEPT] <path>`，SKIPPED/KEPT 行附 `（目标已修改，保留）`/`（已移除但目标已修改，保留）`；末行 `RESULT assistant=… upgraded=n unchanged=n created=n skipped=n removed=n kept=n dry_run=…`；exit 0 含 SKIPPED。
2. 绿：实现参数、分派、报告。
3. 验证：CLI 测试全绿；`InstallAiWorkflowCliTests` 不回归。

提交：`feat(installer): upgrade CLI and per-file reporting`

## 任务 4：事务集成（红→绿，最高风险单元）

1. 红：`UpgradeTransactionTests`＋扩展 `InstallRollbackTests` 风格：
   - execute 接受 plan.rebuild 语义（升级计划再验证用 `build_upgrade_plan` 重建比对）；
   - action `upgrade` 复用 `_publish_updated_file`；`create` 复用既有；`skip/kept` 跳过不产生 journal；
   - **`remove` 新 journal 类型**：发布＝记录原字节＋unlink；回滚＝按原字节/模式重建；提交后文件消失；
   - 台账 profile item 与全部文件同批交换；人为故障点（沿用 `_fault_point` 机制）注入后回滚，断言目标逐字节＝升级前（含 profile 回到 v1/旧 v2）；
   - dry-run：零写入、零 journal、exit 0。
2. 绿：实现 remove journal 与 execute 分派。
3. 验证：新事务测试全绿；`InstallRollbackTests`/`InstallWriteTests`/`InstallSymlinkTests` 全绿；`python3 -m py_compile`。

提交：`feat(installer): atomic upgrade transaction with removal journal`

## 任务 5：文档（内容契约）

- `.ai/tools/README.md` 安装章节后新增「升级」小节：命令、判定规则表、SKIPPED/KEPT 处置指引、legacy 行为、退出码不变声明；USAGE :17-25 更新。
- 验证：`grep` 关键词（`--upgrade`、`SKIPPED`、`台账`）；`python3 -c` 无关；markdown 结构自检（标题层级、代码块闭合）。

提交：`docs(installer): document ledger-driven upgrade`

## 任务 6：Build 出口自证

```bash
python3 -m unittest -v scripts.tests.test_install_ai_workflow        # 全套（新旧）全绿
python3 -m unittest discover -v -s .ai/tools/tests -p 'test_*.py'
openspec validate add-installer-upgrade-path --strict --no-interactive
bash scripts/validate-workflow.sh --require-openspec                # 预期 183+2（本变更 proposal 两项）=185
git diff --check
```

勾选 tasks→`待验证`。严格模式继续：每任务级审查（本计划任务 1-5 各单元，实现后由主会话 freeze＋独立 reviewer 双 verify）→ Verify 双阶段（规格符合性→代码质量）→ 主会话终验 → Archive（delta 并入 `openspec/specs/portable-ai-workflow-installer/spec.md`＋cp 资产副本）→ `--no-ff` 合回 main 并复验；**推送与 yuxiaor 真实目标升级演练另行单独授权**。

## 分支与 worktree（计划确认后、实现前原子顺序）

1. main 记录基线；当前工作区创建/切到 `feature/add-installer-upgrade-path`，仅暂存四件套＋本计划，proposal 置`构建中`，提交。
2. 需要隔离时切回 main，用 git-worktrees 挂载未检出 feature 到 `.worktrees/add-installer-upgrade-path`；工作区干净且无并行时经确认可就地实现（本变更无 worktree 依赖冲突，建议就地＋严格审查兜底）。

## 回滚

每任务一提交，`git revert` 独立回滚；任务 4 失败不影响已合入的任务 1-3（纯增量函数）。
