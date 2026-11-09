模式: 标准
状态: 构建中

# Verify 技能接线 WORKFLOW_STANDARD_BASE 基线

## Why

workflow-tiers 变更已落地 standard 层契约套件按工作流资产分类裁剪：wrapper 仅当调用方显式提供 `WORKFLOW_STANDARD_BASE` 且基线后无工作流资产变更时裁剪（`scripts/validate-workflow.sh:186-223`，规格 `openspec/specs/workflow-tiers-incremental-cache-context/spec.md`）。但技能层（`.claude/skills/verify/SKILL.md`、`.codex/skills/verify/SKILL.md`）与共享知识层零处提及该变量——标准层 Verify 实际从不传基线，裁剪路径恒走"未提供 WORKFLOW_STANDARD_BASE"全量分支，特性处于死状态。

## What Changes

- 两棵技能树的 verify 技能第 57 行：标准层调用改为显式传基线 `WORKFLOW_STANDARD_BASE=<基线> bash scripts/validate-workflow.sh --standard`，并注明基线取值（上一全量验证通过的提交，如上一变更归档提交或本轮构建起点）与不传/不确定时保持现状全量、升级 required 时不适用。
- core 锚点（`validate-workflow-core.sh:911` Verify 标准分层 `contains_all`）增补 `WORKFLOW_STANDARD_BASE` token；`test_validate_workflow.py::test_core_requires_current_standard_verification_layers` 同步增补该 token 断言（锚点镜像锁定惯例）。
- `.ai/kb/overview.md` 验证入口条目补一句接线事实（基线取值与回退语义）。
- delta spec MODIFIED workflow-tiers 裁剪 Requirement：追加调用方（技能）接线义务与场景。

## Impact

- 构建/验证：技能文本双树镜像一致（既有"双套语义镜像"检查强制）；core 锚点与契约测试同步；kb 事实记录。变更命中技能与校验器，标准层验证将升级 required。
- 风险：低——wrapper 裁剪语义已有夹具测试锁定，本变更只接线调用方；基线不确定时不传变量即回退全量（现状语义），required 恒全量不变。

## Scope

### Included

- `.claude/skills/verify/SKILL.md`、`.codex/skills/verify/SKILL.md`（两树同步）。
- `scripts/lib/validate-workflow-core.sh`（锚点行 token 增补）、`scripts/tests/test_validate_workflow.py`（锚点镜像断言增补）；两者镜像资产 `scripts/ai-workflow-assets/shared/scripts/**` 同步。
- `.ai/kb/overview.md` 验证入口条目。
- delta spec：`workflow-tiers-incremental-cache-context` 能力裁剪 Requirement MODIFIED。

### Excluded

- 不修改 wrapper 裁剪/缓存/升级逻辑本身（已规格化并有测试）。
- 不修改 AGENTS.md/CLAUDE.md 宪法文本与状态机、门禁阻断语义。
- 不自动记录/推断基线（由执行技能的会话按"上一全量验证通过提交"取值）。

## Acceptance

- 两棵 verify 技能含一致的 `WORKFLOW_STANDARD_BASE` 接线语句；core 锚点与镜像测试同步通过。
- 基线回退语义明确：不确定/缺失→不传→全量（现状）；required 不受影响。
- required 层门禁、OpenSpec strict、双树镜像检查、`git diff --check` 通过。

## Unverified scope

无（接线为纯调用方说明，wrapper 行为已被既有夹具测试覆盖）。

## Residual risk

执行会话取错基线（选了含工作流资产变更的提交）时 wrapper 自动回退全量（diff 命中工作流资产即不裁剪），不会漏验；最坏代价是失去裁剪收益，无正确性风险。
