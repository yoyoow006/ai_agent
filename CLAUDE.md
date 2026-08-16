# AI 编程助手 · 工作流总纲

本仓库自带零插件依赖的五阶段编程工作流。一切代码变更必须走：**Open → Design → Build → Verify → Archive**。

## 状态真源（新会话必读）

- 变更状态：`openspec/changes/<变更名>/proposal.md` 头部 `状态:` 字段
  取值：`草稿 → 待确认规范 → 设计中 → 待确认计划 → 构建中 → 待验证 → 待归档 → 已归档`
  活跃变更 = `openspec/changes/` 下各目录（可用 `openspec list` 列出）
- 进度：`openspec/changes/<变更名>/tasks.md` 勾选率
- 开始任何工作前：读上述两文件 + `.claude/ai-kb/rules/index.md`，从断点阶段继续，不重做已完成阶段。

## 五阶段路由

| 用户意图 | 技能 | 关键产出 | 完成标志 |
|---|---|---|---|
| 提出新需求 / "开始做 X" | open | changes/<名>/ 四件套 | 状态→待确认规范 |
| "确认规范，出计划" | design | plan/<名>.md + feature 分支 | 状态→构建中 |
| "确认计划，开工" | build | 逐任务代码+测试，tasks 勾选 | 状态→待验证 |
| "构建完成，审查" | verify | 两阶段审查报告+修复 | 状态→待归档 |
| "审查通过，归档" | archive | 主 specs 合并、archive/、合并分支 | 状态→已归档 |

支撑技能按需自动加载：tdd、subagent-driven、code-review、systematic-debugging、verification、git-worktrees、parallel-agents、writing-skills。

## 硬门禁（绝对纪律，违反即返工）

- **G1** 四件套未经用户明确确认，不得写计划
- **G2** 计划书未经用户明确确认，不得写实现代码
- **G3** tasks 未全勾/测试未全绿/无命令输出证据，不得声称构建完成
- **G4** 两阶段审查未通过，不得归档

## ai-kb 知识库规则

- Open：先读 rules/index.md 路由到模块，再读相关 kb/ 与 memory/
- Build：派发子代理时附受影响模块的 memory 摘要
- 任何坑解决后：立即追加 `.claude/ai-kb/memory/<模块>.md`（格式见 .claude/ai-kb/README.md）
- Archive：知识沉淀为归档六步之一（memory/kb/rules 三写）

## 通用纪律

- 任何不确定：停下问用户，不猜
- 声称完成前：运行验证命令并展示输出（无证据不声称完成）
- 审查意见：先验证正确性再实施；有理的改，无理的据实说明
- 提交粒度：每任务至少一次 git commit
