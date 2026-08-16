# 变更提案：init-workflow-system

状态: 构建中
分支: feature/init-workflow-system
创建: 2026-08-16

## 为什么
当前依赖 openspec/superpowers 两个第三方 Claude 插件，不可控且难迁移。需要一套零插件、纯文本、随仓库走的工作流，能力无损。

## 做什么
- CLAUDE.md 工作流总纲（五阶段路由 + 硬门禁）
- .claude/skills/ 13 个原生技能（5 阶段 + 8 支撑）
- .claude/ai-kb/ 知识库骨架（kb / memory / rules）
- openspec/ 目录骨架与 CLI 兼容约定
- 以本变更自身完成首次五阶段 dogfood

## 影响
全新仓库，无存量代码。规格与设计见 specs/workflow-system/spec.md 与 design.md。
