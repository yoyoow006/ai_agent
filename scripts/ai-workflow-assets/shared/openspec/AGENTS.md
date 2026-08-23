# artifact 格式约定（CLI 兼容）

- 变更目录：`openspec/changes/<kebab-case变更名>/`
- 四件套：`proposal.md`、`specs/<能力>/spec.md`（delta，Requirement 标注 ADDED/MODIFIED/REMOVED，每条至少一个 Scenario）、`design.md`、`tasks.md`（`- [ ] 1.1` 编号勾选）
- proposal.md 头部：标准/严格变更必须同时包含：
  - `模式:`：标准|严格
  - `状态:`：草稿|待确认规范|设计中|待确认计划|构建中|待验证|待归档|已归档
- 状态路径：标准从`待确认计划`开始；严格使用完整 8 态；快速模式不创建变更目录。
- 独立计划：仅严格模式使用 `openspec/plan/<变更名>.md`。
- 归档：目录整体移入 `openspec/archive/`，delta 合并进 `openspec/specs/<能力>/spec.md`；严格模式同时归档独立计划。
- 校验：`openspec validate <变更名> --strict --no-interactive`
