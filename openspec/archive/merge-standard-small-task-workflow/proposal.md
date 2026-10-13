模式: 严格
状态: 已归档

# 合并标准小任务轻量工作流

## Why

源项目 `yxr_prj_2026` 的 `feature/simplify-standard-task-workflow` 分支已在业务仓验证“标准小任务”轻量 Verify/Archive 路径：按条件免除 review manifest、条件沉淀知识、精简根仓库提交，并约束手工测试编译输出。当前仓库已具备分层验证、代理门控和输出协议能力，但标准小任务仍会触发完整审查仪式，未复用该分支的降本成果。

本变更将该分支的治理语义移植到本仓库，并与现有分层验证、双运行时镜像、安装资产和契约测试对齐；不直接复制业务仓项目事实。

## What Changes

- 定义“标准小任务”可观察条件：单一职责、目标生产代码不超过 3 个文件、无严格风险、不触及工作流治理/入口/校验器/安装资产、目标测试可直验、无并行或多仓审查需求。
- 标准小任务 Verify：主会话一次综合自查，不强制 review manifest，终局记录测试证据、diff 范围、finding 状态、未验证范围与残余风险。
- 标准小任务 Archive：仅条件沉淀知识，无新事实写“知识沉淀：无”；继续按 Verify 后 diff 分类选择 `--archive-light` 或 required 门禁。
- 标准小任务根仓库默认保留计划基线与终局归档两个职责提交。
- 增加手工 `javac`/`java` 临时测试通道约束：输出仅写 `/tmp` 或项目外目录，完成前仍需 Maven compile 或等效生产编译门禁。
- 移植 OpenSpec 归档辅助脚本并纳入 required 测试；同步模板、入口、共享规则、Codex/Claude 技能、安装资产清单和契约测试。
- 保留严格模式完整门禁，不降低任何高风险流程要求。

## Impact

- 构建/验证：新增归档辅助脚本单测；更新 workflow 契约测试、模板测试和 required 输入清单；本变更触及治理语义，Verify 与 Archive 均需 required 完整门禁。
- 风险：跨项目移植可能与本仓库现有分层验证、代理门控、归档索引和安装资产契约冲突；需逐文件语义合并并避免复制源项目业务知识。
- 流程分级：本变更为严格模式；移植后的“标准小任务”不适用于本变更自身。

## Scope

### Included

- `openspec/specs/risk-tiered-ai-workflow/` 主规格与模板。
- `AGENTS.md`、`CLAUDE.md`、`.ai/rules/`、`.codex/skills/verify|archive/`、`.claude/skills/verify|archive/`。
- `scripts/archive_openspec_change.py`、`scripts/archive-openspec-change.py`、`scripts/new-openspec-change.py`、`scripts/lib/validate-workflow-core.sh`。
- `scripts/tests/test_archive_openspec_change.py`、`scripts/tests/test_validate_workflow.py`、安装资产清单及必要安装器契约同步。
- 本地 feature/worktree 分支、OpenSpec 归档记录与 main 本地合并复验。

### Excluded

- 不修改 `yxr_prj_2026` 源仓库、其未提交的 `http-client.http` 与 `work_daily.md`。
- 不移植 `yuxiaor-pms`、业务项目卡、业务分支规则、业务测试阻塞修复或源仓归档记录。
- 不推送远端、不创建 PR、不强推、不删除未合并分支/worktree。
- 不降低严格模式门禁，不取消快速模式，不取消标准模式唯一实施确认或运行时 TDD。

## Acceptance

- 主规格和双运行时入口明确标准小任务判定、轻量 Verify/Archive、条件知识沉淀、两提交粒度和手工编译输出约束。
- 未命中小任务条件的标准变更仍必须 manifest 冻结与一次综合审查；严格模式仍执行任务级审查和 Verify 双阶段独立审查。
- 归档辅助脚本 dry-run 校验状态、任务勾选和终局证据；实际归档合并 delta、移动目录、更新索引并拒绝重复目标。
- 模板生成器为新增分类/手工编译字段提供安全默认值，预检拒绝残留占位符。
- required 门禁覆盖新增脚本、双运行时语义同步、安装资产清单和归档索引 1:1。
- 变更归档后本地合并到 `main`，并在合并结果上通过 required 验证；不执行远端副作用。

## Unverified scope

- 源分支在源项目业务代码环境中的 Maven 阻塞细节不在本仓库复验。
- 不验证外部目标项目重新安装后的全部业务行为；仅执行本仓库安装器契约测试。

## Residual risk

- 归档辅助脚本采用保守追加式 delta 合并，复杂 MODIFIED/REMOVED 语义仍需人工审查；测试将覆盖现有合并策略与拒绝路径。
- “标准小任务”判定依赖助手如实评估风险；治理契约测试只能防关键口径漂移，不能替代人工判断。
