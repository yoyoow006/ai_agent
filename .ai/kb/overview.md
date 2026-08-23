# 系统架构总览（共享工作流）

## 工作流组成

- `AGENTS.md` / `CLAUDE.md`：双助手入口、风险路由、状态路径和共享底线。
- `.codex/README.md`：Codex 工具映射与 SDD 约定。
- `.codex/skills/` / `.claude/skills/`：助手特有的阶段技能和支撑技能。
- `.ai/`：助手共享的 kb（稳定事实）、memory（踩坑）、rules（路由）、prompts 与只读 tools。
- `.codex/sdd/` / `.claude/sdd/`：仅在确需子代理时使用的本地草稿区，Git 忽略。
- `openspec/`：标准/严格变更的数据层，与 Claude 共享。
- `scripts/validate-workflow.sh`：结构、镜像、禁止规则和 mutation 回归校验。
- `projects/test-login/`：离线 Python 标准库登录与随机验证演示，不承载共享业务项目事实。

本总览合并了原 Claude 风险摘要与 Codex 模块/底线信息；助手特有工具行为仍留在各自适配目录。

## 风险模式与状态

| 模式 | 适用边界 | 状态/产物 |
|---|---|---|
| 快速 | 仅维护已有事实的非运行时文本 | 无 OpenSpec；直接修改和针对性验证 |
| 标准 | 不命中严格条件的低到中风险运行时变更 | 四件套；`待确认计划 → 构建中 → 待验证 → 待归档 → 已归档` |
| 严格 | 权限、资金、迁移/删除、Schema、并发、公开契约、治理、破坏性操作、大重构 | 四件套＋独立计划；完整 8 态 |

proposal 的`模式:`、`状态:`和 tasks 勾选是断点真源。标准只确认一次；严格确认四件套和独立计划各一次。快速不自动提交；标准默认 feature、条件 worktree、一次综合审查；严格默认隔离 worktree、任务级审查和 Verify 双阶段审查。

## 不可削弱底线

- 保护用户修改；外部/破坏性动作单独授权。
- 范围变化或风险升级重新确认。
- 运行时行为/缺陷修复使用 TDD；纯文本使用内容和结构验证。
- 审查意见先验证；完成前现跑验证。
- 提交按可独立回滚职责组织。
- 创建或重置 Git 基线前必须扫描待入库正文；提交后才发现凭据时，需在授权下同时净化当前树和不可达历史，本地清理不替代外部轮换。

## 事实查询与审查证据

- 项目事实以 `.ai/kb/projects/registry.json` 和项目卡为声明式入口；`project_facts.py` 只查询登记且已检出的路径，不联网、不 clone、不写业务仓。
- 标准与严格审查使用 `review_manifest.py freeze/verify/delta` 冻结 comparison base、Git 层级、未忽略 untracked 与内容身份；结论前范围变化必须按 `STALE` 停止。
- `scripts/validate-workflow.sh --require-openspec` 要求 OpenSpec CLI 与仓库必需测试真实执行；严格终验还应独立运行 `openspec validate --all --strict --no-interactive`。
- 项目内 CLI 可放在已忽略的 `.ai-local/tools/openspec` 并临时加入 `PATH`；不得为验证执行 `openspec init` 或 `openspec update`。
