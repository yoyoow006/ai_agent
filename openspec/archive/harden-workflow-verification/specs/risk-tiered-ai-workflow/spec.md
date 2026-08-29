# 压力场景覆盖 delta

## ADDED Requirements

### Requirement: 高风险流程路径必须有施压场景

工作流行为契约 SHALL 以施压场景覆盖以下高风险路径，场景使用与其他场景相同的结构（共同要求＋逐字场景文本＋可判通过条件）：严格实现前的分支与 worktree 原子顺序、归档的 delta 合并与用户取消处置、审查中途 manifest 陈旧的处理。场景文件 SHALL 与镜像资产副本保持一致，结构校验 SHALL 守护这些场景的存在与关键通过条件。

#### Scenario: 新增高风险场景

- **WHEN** 维护者查看 `scripts/workflow-pressure-scenarios.md`
- **THEN** 存在覆盖 worktree 原子顺序、归档合并与取消、manifest STALE 的三个场景
- **AND** 每个场景的通过条件可判（引用明确的禁止动作与正确动作）
- **AND** 结构校验的 压力契约 检查包含这三个场景的标识与关键条件词

#### Scenario: 场景与资产副本漂移

- **WHEN** 实体场景文件与 `scripts/ai-workflow-assets/shared/scripts/` 下副本内容不一致
- **THEN** 字节一致性核对失败并要求同步
