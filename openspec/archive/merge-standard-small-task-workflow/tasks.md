# 任务清单

- [x] 1. 治理语义与双运行时入口
  - [x] 1.1 修改：`openspec/specs/risk-tiered-ai-workflow/spec.md`，合并标准小任务判定、轻量 Verify/Archive、条件知识沉淀、两提交粒度与手工编译输出规则。
  - [x] 1.2 同步：`AGENTS.md`、`CLAUDE.md`、`.ai/rules/index.md`、`.ai/rules/review.md`、`.codex/skills/verify/SKILL.md`、`.codex/skills/archive/SKILL.md`、`.claude/skills/verify/SKILL.md`、`.claude/skills/archive/SKILL.md`。
  - [x] 1.3 验证：`python3 -B -m unittest -v scripts.tests.test_validate_workflow`
  - 预期结果：标准小任务、非小任务、严格模式和双运行时语义同步契约全部 PASS。

- [x] 2. OpenSpec 模板与归档辅助脚本
  - [x] 2.1 修改：`openspec/templates/proposal.md`、`openspec/templates/tasks.md`、`scripts/new-openspec-change.py`。
  - [x] 2.2 新增：`scripts/archive_openspec_change.py`、`scripts/archive-openspec-change.py`、`scripts/tests/test_archive_openspec_change.py`。
  - [x] 2.3 修改：`scripts/lib/validate-workflow-core.sh`，把归档脚本实现、wrapper 和测试纳入 required 输入与执行清单。
  - [x] 2.4 验证：`python3 -B -m unittest -v scripts.tests.test_archive_openspec_change scripts.tests.test_openspec_templates`
  - 预期结果：新增脚本、模板默认值与预检全部 PASS。

- [x] 3. 安装资产与契约回归
  - [x] 3.1 修改：`scripts/ai-workflow-assets/manifest.json` 及必要安装器测试，确保新增脚本随资产安装。
  - [x] 3.2 更新 `scripts/tests/test_validate_workflow.py` 的标准小任务、手工编译输出、归档辅助脚本和资产清单契约。
  - [x] 3.3 验证：`python3 -B -m unittest -v scripts.tests.test_validate_workflow scripts.tests.test_install_workflow scripts.tests.test_install_ai_workflow`
  - 预期结果：工作流、安装器和便携资产契约全部 PASS。

- [x] 4. 严格 Verify
  - [x] 4.1 运行：`bash scripts/validate-workflow.sh --require-openspec`
  - [x] 4.2 运行：`git diff --check`
  - [x] 4.3 记录：`openspec/changes/merge-standard-small-task-workflow/review-findings.md`，包含规格符合性、代码质量、最终 manifest ID、comparison base、finding 状态、未验证范围、残余风险和验证证据。
  - 预期结果：required 门禁零失败；若发现 Critical/Important，先修复并复验。

- [x] 5. Archive 与本地 main 合并
  - [x] 5.1 条件沉淀知识：仅当存在新坑、路由事实或模块入口变化时更新 `.ai/`；否则在归档记录写“知识沉淀：无”。
  - [x] 5.2 合并 delta、更新归档索引、置`已归档`并移动到 `openspec/archive/merge-standard-small-task-workflow/`。
  - [x] 5.3 运行：按 Verify 后 diff 分类执行 `bash scripts/validate-workflow.sh --archive-light` 或 `bash scripts/validate-workflow.sh --require-openspec`。
  - [x] 5.4 本地提交 feature 分支，经确认策略使用 `--no-ff` 合并回 `main`，不推送、不创建 PR、不删除分支。
  - [x] 5.5 在 main 合并结果运行：`bash scripts/validate-workflow.sh --require-openspec`、`git diff --check`、`git status --short`
  - 预期结果：归档记录完整；本地 main 合并后 required 门禁与状态检查全部 PASS。

## 本地整合策略

- 分支/worktree：严格模式，在已忽略的 `.worktrees/merge-standard-small-task-workflow` 创建隔离 worktree 和 `feature/merge-standard-small-task-workflow`；源仓库保持只读。
- 提交边界：OpenSpec 确认基线一个提交；治理/脚本/测试实现一个职责提交；Verify 结论与 Archive 结果一个终局提交；若重要 finding 修复或范围扩大，另加职责提交。
- 外部副作用授权：仅允许本地分支、本地提交、本地 `--no-ff` 合并回 main；禁止 push、PR、强推、删除未合并工作或修改源仓库。
- 手工测试编译输出：不适用（本仓库无 Maven 业务编译；新增 Python 脚本测试不写业务 target 目录）。
