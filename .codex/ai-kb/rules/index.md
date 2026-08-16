# 模块路由表（Codex）

| 模块名 | 代码路径 | 别称 | 关键词 |
|---|---|---|---|
| 工作流总纲 | AGENTS.md | 宪法、总纲、Codex入口 | 五阶段、硬门禁、G1-G4 |
| 阶段技能 | .codex/skills/{open,design,build,verify,archive}/ | 编排器 | 四件套、计划书、两阶段审查、归档 |
| 支撑技能 | .codex/skills/{tdd,subagent-driven,code-review,...}/ | 执行器 | TDD、子代理、审查、调试、worktree |
| 工具映射 | .codex/README.md | 适配层 | spawn_agent、fork_context、update_plan |
| 知识库 | .codex/ai-kb/ | kb、记忆 | 踩坑、路由表、知识沉淀 |
| 数据层 | openspec/ | 变更目录 | proposal、specs、delta、tasks、archive |
| 安装器 | scripts/install-workflow.sh | 一键安装 | 安装、--force、.bak、装后自检 |
| 校验器 | scripts/validate-workflow.sh | 结构校验 | 不变量、假红、骨架目录 |
