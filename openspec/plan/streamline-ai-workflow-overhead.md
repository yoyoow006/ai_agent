# 实现计划：流程口径同步与业务上下文路由

## 全局约束

- 保护用户修改；只在 `feature/streamline-ai-workflow-overhead` 的隔离 worktree 中实现。
- 不 push、不创建 PR、不删除未合并工作、不访问或写入 `/media/shitou/data2/ai-pms`。
- 源仓库 registry 保持空数组；业务词测试只用非业务 fixture。
- 运行时行为变更按红-绿-重构执行；文档同步用内容契约、链接、镜像和 mutation 测试验证。
- 当前 main 已包含部分精简实现；先核对并复用，不重写已满足部分。

## 任务 1：收口既有精简语义

- Modify: `AGENTS.md`, `CLAUDE.md`, `.codex/skills/design/SKILL.md`, `.claude/skills/design/SKILL.md`
- 确保标准实际产物、严格硬风险二次确认和 archive-light 语义一致。
- Test: `python3 -m unittest -v scripts.tests.test_validate_workflow`
- 预期：既有三件套、硬风险确认和 archive-light mutation 用例全部通过。

## 任务 2：同步文档与安装资产

- Modify: `README.md`, `docs/ai-workflow-intro.md`, `.ai/kb/overview.md`, `.codex/README.md`, 双侧 Open/Design/Build 技能。
- Modify: `scripts/ai-workflow-assets/claude/**`, `scripts/ai-workflow-assets/codex/**`, `scripts/ai-workflow-assets/shared/**` 中对应入口、技能、主规格、项目说明和压力场景。
- 移除“标准固定四件套”“严格固定双确认”“归档后固定全量”的旧口径。
- Test: 源文档与安装资产的关键语义 grep 无旧口径；工作流契约测试通过。

## 任务 3：业务词路由红测

- Modify: `.ai/tools/tests/test_project_facts.py`
- 新增 `business-terms` 用例：包含/精确、同义词、项目过滤、分页、零匹配、非法 registry、路径边界、只读性。
- Test: `python3 -m unittest -v .ai.tools.tests.test_project_facts`
- 预期先失败：命令不存在或参数不支持，失败原因正是行为缺失。

## 任务 4：实现业务词路由

- Modify: `.ai/tools/project_facts.py`, `.ai/kb/projects/README.md`, `.ai/tools/README.md`, `.ai/rules/index.md`
- Modify: `openspec/specs/shared-ai-workflow-infrastructure/spec.md`
- Modify: `scripts/ai-workflow-assets/shared/.ai/**` 与安装资产规格副本。
- 实现 optional `business_terms` 解析与 `business-terms` CLI。
- Test: `python3 -m unittest -v .ai.tools.tests.test_project_facts`
- 预期：新增和既有事实工具测试全部通过。

## 任务 5：扩展漂移回归

- Modify: `scripts/tests/test_validate_workflow.py`, `scripts/lib/validate-workflow-core.sh`, `scripts/ai-workflow-assets/shared/scripts/**`
- 覆盖 Claude 入口、README/intro/overview、双侧 Design 技能和安装资产旧口径注入。
- Test: `python3 -m unittest -v scripts.tests.test_validate_workflow`
- 预期：新增 mutation 均能红绿拦截。

## 任务 6：综合验证与审查

- Commands:
  - `python3 -m unittest -v .ai.tools.tests.test_project_facts`
  - `python3 -m unittest -v scripts.tests.test_validate_workflow`
  - `python3 -B -m unittest -v scripts.tests.test_install_ai_workflow`
  - `python3 -B -m unittest -v scripts.tests.test_install_workflow`
  - `bash scripts/validate-workflow.sh --require-openspec`
  - `git diff --check`
- 任务级审查单元：
  1. 工作流语义双运行时/安装资产一致性。
  2. 业务词查询边界与只读性。
- Verify 双阶段：规格符合性、代码质量。
