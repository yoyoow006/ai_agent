# 实现计划：工作流语义对齐与业务上下文路由

## 全局约束

- 基线：`main`；实现分支/worktree：`feature/align-workflow-semantics-and-business-context`。
- 不 push、不创建 PR、不删除未合并工作、不访问或写入 `/media/shitou/data2/ai-pms`。
- 源仓库 registry 保持空数组；业务词测试只用非业务 fixture。
- 运行时行为变更按红-绿-重构执行；文档同步用内容契约、链接、镜像和 mutation 测试验证。
- base 已存在的精简 Requirements 不重复 ADDED；本变更只 MODIFIED 冲突 Requirement 并新增缺失能力。

## 任务 1：修复 OpenSpec 身份与 delta

- Rename: `openspec/changes/streamline-ai-workflow-overhead/` → `openspec/changes/align-workflow-semantics-and-business-context/`
- Rename: `openspec/plan/streamline-ai-workflow-overhead.md` → `openspec/plan/align-workflow-semantics-and-business-context.md`
- Modify: active proposal/design/tasks、risk delta。
- 验证：活跃目录不与 archive 同名；`openspec validate align-workflow-semantics-and-business-context --strict --no-interactive` 通过；MODIFIED Requirement 在 base 存在，两个 ADDED Requirement 在 base 不存在。

## 任务 2：同步流程语义

- Modify: `AGENTS.md`, `CLAUDE.md`, `README.md`, `docs/ai-workflow-intro.md`, `openspec/project.md`, `.ai/kb/overview.md`, `.codex/README.md`, 双侧 Open/Design/Build 技能。
- Modify: `scripts/workflow-pressure-scenarios.md` 与对应 `scripts/ai-workflow-assets/` 入口、技能、主规格、项目说明、overview 和压力场景。
- 移除标准固定四件套、严格固定双确认、机械任务审查、归档后固定全量和主规格互斥 Archive 口径。
- Test: `python3 -B -m unittest -v scripts.tests.test_validate_workflow.WorkflowSemanticSyncTest`

## 任务 3：业务词路由红绿实现

- Modify: `.ai/tools/tests/test_project_facts.py`
- 先新增失败测试：包含/精确、同义词、项目过滤、分页、零匹配、非法 registry、路径/symlink 边界、只读性。
- Modify: `.ai/tools/project_facts.py`, `.ai/kb/README.md`, `.ai/kb/overview.md`, `.ai/kb/projects/README.md`, `.ai/rules/index.md`, `.ai/tools/README.md`, shared infrastructure delta 与安装资产副本。
- Test: `python3 -B -m unittest discover -v -s .ai/tools/tests -p 'test_project_facts.py'`

## 任务 4：加固 archive-light 升级

- Modify: `scripts/validate-workflow.sh`, `scripts/tests/test_validate_workflow.py`, 安装资产 wrapper/test 副本。
- 行为：diff 分类在 Git 缺失、非法 base/pathspec 或非零退出时立即失败；语义变化时本次 core 调用收到 `--require-openspec`，并运行顶层契约套件。
- Test: `python3 -B -m unittest -v scripts.tests.test_validate_workflow.ArchiveLightGateTest scripts.tests.test_validate_workflow.ArchiveLightPromotionMutationTest`

## 任务 5：完整验证与任务级审查

- Commands:
  - `python3 -B -m unittest discover -v -s .ai/tools/tests -p 'test_*.py'`
  - `python3 -B -m unittest -v scripts.tests.test_validate_workflow`
  - `python3 -B -m unittest -v scripts.tests.test_install_ai_workflow`
  - `python3 -B -m unittest -v scripts.tests.test_install_workflow`
  - `bash scripts/validate-workflow.sh --require-openspec`
  - `openspec validate --all --strict --no-interactive`
  - `git diff --check`
- 任务级审查单元：
  1. 工作流语义/验证降级边界。
  2. 业务词查询边界与只读性。

## 任务 6：严格 Verify 与 Archive

- 顺序执行规格符合性、代码质量两个独立关注面。
- 处置全部 Critical/Important 后合并 delta、沉淀知识、归档唯一变更名，并按已确认策略本地 `--no-ff` 合回 `main` 复验。
