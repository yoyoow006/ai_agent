# AI 编程助手 · Codex 工作流总纲

本仓库自带零第三方插件依赖的五阶段编程工作流（openspec 与 superpowers 的方法论已全部内联为本地技能）。在 Codex 中一切代码变更必须走：**Open → Design → Build → Verify → Archive**。

## 状态真源（新会话必读）

- 变更状态：`openspec/changes/<变更名>/proposal.md` 头部 `状态:` 字段
  取值：`草稿 → 待确认规范 → 设计中 → 待确认计划 → 构建中 → 待验证 → 待归档 → 已归档`
  活跃变更 = `openspec/changes/` 下各目录
- 进度：`openspec/changes/<变更名>/tasks.md` 勾选率
- 开始任何工作前：读上述两文件 + `.codex/ai-kb/rules/index.md`，从断点阶段继续，不重做已完成阶段
- openspec 数据层（changes/plan/specs/archive）为 `.claude` 与 `.codex` 两套工作流共享的唯一事实源，不复制、不分叉

## 技能加载规则

进入任一阶段前，先完整读取对应技能文档并严格遵循：

| 用户意图 | 技能文档 | 关键产出 | 完成标志 |
|---|---|---|---|
| 提出新需求 / "开始做 X" | `.codex/skills/open/SKILL.md` | changes/<名>/ 四件套 | 状态→待确认规范 |
| "确认规范，出计划" | `.codex/skills/design/SKILL.md` | plan/<名>.md + feature 分支 | 状态→构建中 |
| "确认计划，开工" | `.codex/skills/build/SKILL.md` | 逐任务代码+测试，tasks 勾选 | 状态→待验证 |
| "构建完成，审查" | `.codex/skills/verify/SKILL.md` | 两阶段审查报告+修复 | 状态→待归档 |
| "审查通过，归档" | `.codex/skills/archive/SKILL.md` | 主 specs 合并、archive/、合并分支 | 状态→已归档 |

支撑技能按需加载：tdd、subagent-driven、code-review、systematic-debugging、verification、git-worktrees、parallel-agents、writing-skills（均在 `.codex/skills/` 下）。

## Codex 原生工具映射

技能文档中的 Claude 概念在 Codex 中按 `.codex/README.md` 的映射表执行，核心三条：

- **子代理派发**：`multi_agent_v1__spawn_agent`（`fork_context: false` = 全新上下文）；续发追问用 `send_input`，收结果用 `wait_agent`，用完 `close_agent`
- **待办追踪**：`update_plan`（每任务一条，勾选即进度）
- **文件编辑 / 命令执行**：`apply_patch` / `exec_command`

## 硬门禁（绝对纪律，违反即返工）

- **G1** 四件套未经用户明确确认，不得写计划
- **G2** 计划书未经用户明确确认，不得写实现代码
- **G3** tasks 未全勾/测试未全绿/无命令输出证据，不得声称构建完成
- **G4** 两阶段审查未通过，不得归档

## ai-kb 知识库规则

- Open：先读 `.codex/ai-kb/rules/index.md` 路由到模块，再读相关 kb/ 与 memory/
- Build：派发子代理时附受影响模块的 memory 摘要
- 任何坑解决后：立即追加 `.codex/ai-kb/memory/<模块>.md`（格式见 `.codex/ai-kb/README.md`）
- Archive：知识沉淀为归档六步之一（memory/kb/rules 三写），把本次变更遇到的坑与注意事项沉入 memory

## 通用纪律

- 任何不确定：停下问用户，不猜
- 声称完成前：运行验证命令并展示输出（无证据不声称完成）
- 审查意见：先验证正确性再实施；有理的改，无理的据实说明
- 提交粒度：每任务至少一次 git commit
