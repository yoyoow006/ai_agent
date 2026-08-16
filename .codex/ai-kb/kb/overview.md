# 系统架构总览（Codex 工作流）

（Open 阶段首次探索后填写；Archive 阶段保持同步）

## 组成
- AGENTS.md — Codex 工作流总纲（Codex 每次会话自动读取的入口）
- .codex/README.md — Claude→Codex 工具映射与派发契约（适配层）
- .codex/skills/ — 13 技能（5 阶段编排器 + 8 支撑），零第三方插件依赖
- .codex/ai-kb/ — 本知识库（kb/memory/rules）
- .codex/sdd/ — 子代理驱动开发草稿区（台账/简报/报告/审查包，git 忽略）
- openspec/ — 变更数据层（changes/plan/specs/archive），与 .claude 工作流共享
- scripts/validate-workflow.sh — 结构校验（含 .codex 镜像检查）
- scripts/install-workflow.sh — 一键安装器

## 五阶段状态机
草稿 → 待确认规范 → 设计中 → 待确认计划 → 构建中 → 待验证 → 待归档 → 已归档
（真源：openspec/changes/<变更名>/proposal.md 头部 状态: 字段）
