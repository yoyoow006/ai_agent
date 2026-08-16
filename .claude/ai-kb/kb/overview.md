# 系统架构总览

（Open 阶段首次探索后填写；Archive 阶段保持同步）

## 组成
- CLAUDE.md — 工作流总纲
- .claude/skills/ — 13 技能（5 阶段 + 8 支撑）
- .claude/ai-kb/ — 本知识库
- openspec/ — 变更数据层（changes/plan/specs/archive）
- scripts/validate-workflow.sh — 结构校验（工作流的"测试套件"）
- scripts/install-workflow.sh — 一键安装器（把全套工作流装到目标项目；--force 备份覆盖）
