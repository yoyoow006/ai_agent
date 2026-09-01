# 工作流技能正文瘦身与本土化

模式: 严格
状态: 构建中

## Why

2026-09-01 以 writing-skills 自身质量标准对全部 13 个技能做只读审查，发现四类问题（证据均实测）：

1. **writing-skills 违反自身规则**：自带验证命令 `wc -w` 实测 1225 词（空白分词还系统性低估中文），远超其自定义"其他技能 <500 词"上限；9780 去空白字符为全仓最大（tdd 的 8.7 倍）；正文 5 处"源技能……未随本仓库迁移"注记命中其自身"❌ 叙事式示例"反模式。
2. **示例不可迁移**：parallel-agents（2518 字符）全部示例为 TypeScript 测试文件并含整节"来自真实会话的示例"叙事；systematic-debugging（3640 字符）阶段 1 的 4 层示例是 macOS `codesign`/钥匙链——本仓库实际技术栈是 bash/python 安装器与校验器。
3. **验证口径失效**：`wc -w` 以空白分词，中文正文整行记 1 词，writing-skills"验证"一节在中文技能上不可判且恒乐观。
4. **技能编辑与行为测试脱钩**：writing-skills 铁律要求"对既有技能的编辑"同样走红—绿，但 `scripts/workflow-pressure-scenarios.md` 的 9 个场景与"改了哪个技能 → 重跑哪些场景 → 结果记在哪"之间无显式绑定条款。

## What Changes

- `writing-skills`：纯内联瘦身——5 处迁移注记合并为概述处一行来源说明；压缩重叠示例与节；验证命令由 `wc -w` 词数改为去空白字符口径（`tr -d '[:space:]' < SKILL.md | wc -m`）并登记中文阈值；编辑流程节新增"技能正文变更后 Verify 重跑相关施压场景并记录于变更目录"绑定句。
- `parallel-agents`：TS 测试文件示例与"来自真实会话的示例"叙事节改写为本仓库 bash/python 场景最小示例；保留 Codex 适配注记行现行工具名（`spawn_agent` 等，校验器 `adapter_note_tools_ok` 锚定）。
- `systematic-debugging`：macOS 签名/钥匙链示例本土化为安装器/校验器多层排查示例；"Ultra-think"等宿主特定语汇中性化。
- 四副本逐字同步：`.claude/`、`.codex/` 工作树＋`scripts/ai-workflow-assets/` 两侧资产副本（仅登记过的路径前缀适配差异）；manifest 无文件增删。
- 校验器 `validate-workflow-core.sh` 新增守卫：三技能双树"未随本仓库迁移"零残留（absence 检查，目标为显式 SKILL.md 路径而非目录扫描）；writing-skills 双树含字符口径验证命令与场景重跑绑定句锚串；配对"注入必红＋干净必绿"契约用例并同步套件计数断言。
- delta 规格：`risk-tiered-ai-workflow` ADDED"工作流技能正文必须精炼且示例可迁移"Requirement；MODIFIED"高风险流程路径必须有施压场景"补技能正文变更重跑条款。

**范围调整说明（相对立项选项原文）**：立项选项含"结构拆分"。经探索：安装器 manifest 按文件逐条登记（新增辅助文件扩大变更面到安装器契约与随包用例）；镜像检查仅守护 SKILL.md（辅助文件不受守护）；writing-skills 属低频加载技能，拆分的 token 收益边际。故本变更改为**纯内联压缩**，"100+ 行重型参考拆分独立文件"继续作为 writing-skills 内既有规则约束未来技能。此调整随本次四件套确认一并裁定。

**非目标**（审查已识别、明确不做）：verification description 措辞调整；manifest 双检规则四处复述的压缩；任何技能改名（校验器硬编码 13 技能名＋四副本＋已装目标，成本远大于收益）。

## Impact

- 触及工作流治理资产＋校验器＋安装资产：Verify/Archive 恒跑 `bash scripts/validate-workflow.sh --require-openspec` 全量门禁与 `openspec validate --all --strict`；安装器套件（约 20 分钟）以 `-B` 串行纳入终验；推送后 CI 自动跑门禁。
- 行为语义不变（措辞压缩＋示例替换）；代理遵从性由 9 个施压场景全量重跑背书，任一场景 FAIL 即停止并回退该处措辞。
- 已核对记忆坑并规避：外部命令清单单一来源（新守卫用纯 bash，预期零新外部命令）、适配注记全仓计数恰为 1、umask-002 检出环境先做权限规范化、终验链期间零提交、契约套件硬编码计数同步。
