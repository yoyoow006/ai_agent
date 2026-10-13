# 实施计划：合并标准小任务轻量工作流

## 目标与全局约束

- 将源项目分支 `feature/simplify-standard-task-workflow` 中“标准小任务”治理语义移植到本仓库，并与现有分层验证、代理门控、输出协议、缓存、安装资产和双运行时镜像契约合并。
- 以当前仓库文件为语义基准，不做跨仓 cherry-pick。
- 源仓库 `/media/shitou/data2/projects/yxr_prj_2026` 只读；不得修改其未提交文件。
- 严格模式实现位于 `.worktrees/merge-standard-small-task-workflow`、分支 `feature/merge-standard-small-task-workflow`。
- 不推送、不创建 PR、不强推、不删除未合并工作；本地合并回 `main` 后必须复验。
- 运行时脚本新增必须先写失败测试，再实现；文档/技能语义使用内容契约和 workflow 契约测试。

## 职责单元与步骤

### 1. OpenSpec 基线与治理语义

1. 在 feature 分支提交已确认四件套与本计划。
2. 修改 `openspec/specs/risk-tiered-ai-workflow/spec.md`：
   - 用 delta 中完整 Requirement 替换“标准模式必须消除重复审查”和“Archive 验证必须按 Verify 后变化选择层级”。
   - 追加“标准小任务根仓库提交必须精简”、“手工测试编译不得污染构建输出目录”。
3. 同步根入口：
   - `AGENTS.md`
   - `CLAUDE.md`
4. 同步共享规则：
   - `.ai/rules/index.md`
   - `.ai/rules/review.md`
5. 同步技能镜像：
   - `.codex/skills/verify/SKILL.md`
   - `.codex/skills/archive/SKILL.md`
   - `.claude/skills/verify/SKILL.md`
   - `.claude/skills/archive/SKILL.md`
6. 验证：
   - `python3 -B -m unittest -v scripts.tests.test_validate_workflow`
   - 预期：现有语义同步契约先因新语义缺失/旧契约不匹配而失败，随后同步后 PASS。

### 2. OpenSpec 模板与归档辅助脚本（TDD）

1. 先新增 `scripts/tests/test_archive_openspec_change.py`，测试：
   - 未勾选任务拒绝；
   - 状态非`待归档`拒绝；
   - dry-run 不移动文件；
   - 实际归档合并 spec、置`已归档`、移动目录、更新索引；
   - 重复归档目标拒绝。
2. 运行并确认红：
   - `python3 -B -m unittest -v scripts.tests.test_archive_openspec_change`
   - 预期：ImportError/ModuleNotFoundError，证明实现缺失。
3. 实现：
   - `scripts/archive_openspec_change.py`
   - `scripts/archive-openspec-change.py` wrapper
4. 更新：
   - `openspec/templates/proposal.md`：新增`流程分级`
   - `openspec/templates/tasks.md`：新增`手工测试编译输出`
   - `scripts/new-openspec-change.py`：为新增占位符提供安全默认值
5. 修改 `scripts/lib/validate-workflow-core.sh`，把实现、wrapper、测试纳入 required 输入和执行清单。
6. 验证：
   - `python3 -B -m unittest -v scripts.tests.test_archive_openspec_change scripts.tests.test_openspec_templates`
   - 预期：全部 PASS。

### 3. 安装资产与契约回归

1. 检查 `scripts/ai-workflow-assets/manifest.json` 的资产清单和校验规则。
2. 将新增归档脚本纳入必要资产清单；若安装器测试要求路径/哈希/复制清单，同步更新。
3. 更新 `scripts/tests/test_validate_workflow.py`：
   - 标准小任务主规格与入口口径；
   - 未命中条件和严格模式不降级；
   - 归档辅助脚本 required 挂载；
   - 归档索引 1:1；
   - 手工测试编译输出；
   - 安装资产包含新增脚本。
4. 验证：
   - `python3 -B -m unittest -v scripts.tests.test_validate_workflow scripts.tests.test_install_workflow scripts.tests.test_install_ai_workflow`
   - 预期：全部 PASS。

### 4. Build 内自查与提交

1. 核对完整 diff，确认没有源项目业务知识、源仓归档记录或无关文件。
2. 按职责单元提交：
   - 治理规格、入口、共享规则、技能；
   - 模板、归档脚本、校验器清单与测试；
   - 安装资产和契约回归。
3. 更新 tasks 勾选和 proposal 状态`待验证`，提交 OpenSpec 状态推进。

## 高风险实现单元审查

- 审查单元 A：归档辅助脚本状态迁移与半归档防护。
  - 不变量：任何拒绝路径不得修改主规格、索引或移动目录；实际归档必须原子顺序执行且重复目标拒绝。
- 审查单元 B：工作流治理语义不降低严格门禁。
  - 不变量：小任务豁免仅限 manifest；未命中条件仍 manifest；严格模式仍任务级审查和双阶段 Verify。
- 按上述单元记录任务级审查，并在 Verify 前冻结精确 diff。

## Verify 与 Archive

1. 运行：
   - `bash scripts/validate-workflow.sh --require-openspec`
   - `git diff --check`
2. 记录 `review-findings.md`：规格符合性、代码质量、最终 manifest ID、comparison base、finding 状态、未验证范围、残余风险和命令证据。
3. 条件沉淀知识；无新事实写“知识沉淀：无”。
4. 合并 delta 到主规格，移动变更目录，更新归档索引，置`已归档`。
5. 因 Verify 后发生治理/脚本/测试/资产变化，Archive 使用：
   - `bash scripts/validate-workflow.sh --require-openspec`
6. 本地提交 feature，`--no-ff` 合并回 `main`。
7. 在 main 合并结果运行：
   - `bash scripts/validate-workflow.sh --require-openspec`
   - `git diff --check`
   - `git status --short`

## 回滚策略

- Build 阶段失败：保留 worktree 与 feature 分支，按职责提交回滚或修复。
- Archive/合并失败：停止在 feature，不合并 main。
- main 合并后复验失败：立即停止并保留 merge commit，向用户报告，不推送。
