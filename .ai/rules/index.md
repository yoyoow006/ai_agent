# 共享模块路由表

| 模块名 | 代码路径 | 别称 | 关键词 |
|---|---|---|---|
| 风险分级工作流 | `AGENTS.md`, `CLAUDE.md`, `openspec/specs/risk-tiered-ai-workflow/` | 宪法、总纲、流程路由 | 快速模式、标准模式、严格模式、单确认、状态路径、共享底线 |
| Codex 阶段与支撑技能 | `.codex/skills/` | Codex 编排器、执行器 | Open、Design、Build、Verify、Archive、TDD、审查、worktree |
| Claude 阶段与支撑技能 | `.claude/skills/` | Claude 编排器、执行器 | Open、Design、Build、Verify、Archive、TDD、审查、worktree |
| 助手适配 | `.codex/README.md`, `AGENTS.md`, `CLAUDE.md` | 工具映射、入口 | spawn_agent、update_plan、apply_patch、宿主能力 |
| 共享知识层 | `.ai/` | kb、memory、rules、prompts、tools | 路由、踩坑、项目卡、知识沉淀、事实查询 |
| 项目登记 | `.ai/kb/projects/registry.json`, `.ai/kb/projects/` | registry、项目卡 | project-context、server-registry、workspace-search |
| 安装器知识分层 | `.gitignore`, `.ai/kb/projects/README.md`, `openspec/specs/installer-knowledge-separation/` | 源仓库业务知识、目标项目登记 | 空白 registry、通用骨架、业务项目卡、防回流 |
| 测试登录项目 | `projects/test-login/` | 登录演示、随机验证 | PBKDF2、验证码、session token、一次性挑战 |
| OpenSpec 数据层 | `openspec/` | 变更目录 | 模式字段、proposal、delta、tasks、plan、archive |
| 工作流校验器 | `scripts/validate-workflow.sh` | 结构校验、回归守卫 | mutation、镜像、非法状态、旧重流程、假绿、required、OpenSpec strict、PASS/FAIL/SKIP |
| 仓库忽略规则 | `.gitignore` | Git 忽略、本地路径 | `.worktrees`、`.codex/sdd`、`.claude/sdd`、外部项目 |
| Git 基线安全 | `.git/`, `.gitignore`, `openspec/specs/git-baseline-secret-hygiene/` | secret scan、凭据清理、历史重建 | 字面凭据、reachable history、reflog、prune、外部轮换 |
| Git 远程配置 | `.git/config`, `openspec/specs/git-remote-configuration/` | origin、远程仓库 | remote URL、fetch、push、upstream、网络授权 |
