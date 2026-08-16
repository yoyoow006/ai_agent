# Codex 工作流适配层

本目录是 Claude 五阶段工作流（OpenSpec + Superpowers 方法论内联版）在 Codex 中的无损迁移：13 个技能文档原样保留，仅路径与执行机制适配 Codex 原生能力，**不依赖任何第三方插件**。

## 目录结构

| 路径 | 用途 |
|---|---|
| `AGENTS.md`（仓库根） | Codex 工作流总纲，Codex 每次会话自动读取 |
| `.codex/skills/<名>/SKILL.md` | 13 个技能：5 阶段编排器 + 8 个支撑技能 |
| `.codex/ai-kb/` | 知识库：kb（架构）/ memory（踩坑）/ rules（路由） |
| `.codex/sdd/<变更名>/` | 子代理驱动开发草稿区（台账、任务简报、报告、审查包），git 忽略 |
| `openspec/` | 变更数据层（changes/plan/specs/archive），与 .claude 工作流共享，不分叉 |

## Claude → Codex 工具映射

技能文档沿用 Claude 术语，执行时按下表一一对应：

| 技能文档中的说法 | Codex 原生执行方式 |
|---|---|
| 派发子代理 / general-purpose 子代理 | `multi_agent_v1__spawn_agent`，**`fork_context: false`**（全新上下文，不继承会话历史） |
| 续用存活中的子代理（修复轮 1-3） | `multi_agent_v1__send_input`（同一 agent id 追加消息） |
| 等待/收取子代理结果 | `multi_agent_v1__wait_agent` |
| 释放子代理 | `multi_agent_v1__close_agent`（完成后及时关闭） |
| 同一回复并行派发 | 在同一条消息里发出多个 `spawn_agent` 调用 |
| TodoWrite / 待办清单 | `update_plan`（每任务一条） |
| Read / Edit / Write | `apply_patch`（编辑）、`exec_command`（读取） |
| Bash | `exec_command` |
| 子代理显式指定模型 | `spawn_agent` 的 `model` 字段（机械任务用 turbo，判断/终审用最强模型） |

## 派发契约（Codex 版）

1. 派发实现者前把任务全文提取到 `.codex/sdd/<变更名>/task-N-brief.md`，派发提示只放：任务定位一行、简报路径、前序接口、memory 摘要、TDD 硬规则、报告路径
2. `fork_context: false` 是硬规则——审查者与实现者都不许继承主会话历史，评估材料以文件形式构造
3. 实现者回传短契约（状态、提交哈希、一行测试摘要、疑虑），完整报告落盘 `.codex/sdd/<变更名>/task-N-report.md`
4. 审查包（`git log` / `git diff --stat` / `git diff -U10`）重定向到 `.codex/sdd/<变更名>/review-<base7>..<head7>.md`，审查子代理读文件评审
5. 台账 `.codex/sdd/<变更名>/progress.md` 首行写明计划文件路径——上下文压缩后靠台账与 `git log` 恢复断点

## 与 .claude 工作流的关系

- `openspec/`、`scripts/` 为共享层：无论从哪套工作流进入，状态机与归档产物一致
- `.claude/ai-kb` 与 `.codex/ai-kb` 各自独立维护（各自会话读各自知识库）；跨套沉淀时以归档方所在目录为准
- 双套并存时以 proposal `状态:` 字段为唯一断点真源，禁止两套同时推进同一变更
