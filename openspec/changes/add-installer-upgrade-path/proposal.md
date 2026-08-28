# 安装器升级路径：台账驱动的 --upgrade

模式: 严格
状态: 待验证

## Why

安装器首版无 upgrade/uninstall（`.ai/tools/README.md` 明示）。`_target_action`（install_ai_workflow.py:367-390）对"目标文件内容≠新资产"一律整体 `ConflictError`（exit 3）——源仓工作流每次演进后，已安装目标（如 yuxiaor）只能人工逐文件对比整合。P1/P2 两轮改造已让实体/资产树前进 3 个版本，该痛点已实际发生且随目标数量增长不可持续。

## What Changes

- **新增 `--upgrade` 模式**（与 `--target`/`--assistant` 组合，支持 `--dry-run`）：以"安装台账"判定每个 manifest 文件的可升级性，逐文件行动、逐文件报告，不再整体拒绝。
- **profile 升级为 schema v2 安装台账**：`.ai/assistant-profile.json` 在安装/升级时记录 `files: {path: sha256}`（manifest 文件的安装时内容哈希）；升级时"目标文件哈希＝台账哈希"即证明未被目标修改 → 可安全替换为新版。
- **三类文件行动**（按 2026-08-28 决策）：
  1. 未被目标修改（台账命中）→ 替换为新版；已等于新版 → `UNCHANGED`；
  2. 被目标修改（台账不匹配或 legacy 无台账且≠新版）→ `SKIPPED`＋逐文件报告，其余继续；
  3. 已从新版 manifest 移除且台账确认未修改 → 删除；被修改 → 保留＋报告。
- **legacy v1 profile**（无台账，如 yuxiaor）：仅"内容已等于新版"自动通过，其余全部 `SKIPPED` 报告；首次以 v2 安装/升级后即获得台账。入口文件（AGENTS.md/CLAUDE.md）既有语义不变——目标已有时仍不触碰，仅报告。
- 升级沿用既有事务（renameat2 原子发布＋回滚）、边界校验、退出码契约；报告输出每文件 `UPGRADED/UNCHANGED/CREATED/SKIPPED/REMOVED/KEPT` 与汇总。
- `.ai/tools/README.md` 与安装帮助同步更新；测试按严格模式 TDD 先红后绿补齐（台账判定、三类行动、legacy 降级、事务回滚、dry-run、删除清理）。

## 用户已确认决策（2026-08-28 提问轮）

1. 冲突策略：逐文件跳过＋报告，其余继续（非整体中止）。
2. 基线来源：profile 内置台账（schema v2，自包含可审计）。
3. 已移除文件：台账确认未被修改才删除，否则保留＋报告。

## Impact

- 修改：`scripts/lib/install_ai_workflow.py`（主要）、`scripts/install-ai-workflow.sh`（USAGE 如需）、`scripts/tests/test_install_ai_workflow.py`、`.ai/tools/README.md`。
- 不改：资产 manifest.json 结构、安装（非升级）语义、`.gitignore` 受管块逻辑、Python 3.8 兼容约束（新代码同样受限）。
- 外部副作用边界：`--upgrade` 只写入/删除台账证明属安装器所有的文件；目标自定义内容零触碰（SKIPPED/KEPT）。真实目标升级演练属外部动作，实施后单独授权执行。
- 风险：台账写入与文件发布的事务一致性（台账必须在同一事务内更新，否则半升级状态失真）；sha256 判定对"目标回改回旧版内容"视为未修改（可接受，内容等价）。
