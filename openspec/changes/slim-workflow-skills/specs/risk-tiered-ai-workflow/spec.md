# Delta Spec: 工作流技能正文瘦身与本土化

## ADDED Requirements

### Requirement: 工作流技能正文必须精炼且示例可迁移

工作流技能正文 SHALL 不含对未随仓库迁移的源文档的叙事性注记；技能示例 SHALL 引用本仓库实际技术栈（bash/python 安装器与校验器）或保持技术无关，不得以其他技术栈专有场景为主要示例。writing-skills 的 token 效率验证 SHALL 使用对中文正文可判的去空白字符口径，并 SHALL 遵守其为本仓库技能定义的同一结构与效率规则。结构校验 SHALL 守护：writing-skills、parallel-agents、systematic-debugging 双树正文迁移注记零残留，且字符口径验证命令与技能编辑场景重跑绑定句在 writing-skills 双树中存在。

#### Scenario: 技能正文无迁移叙事残留

- **WHEN** 维护者查看 writing-skills、parallel-agents、systematic-debugging 的双树正文
- **THEN** 不出现"未随本仓库迁移"字样
- **AND** 示例不引用 TypeScript 测试文件名或 macOS 专有签名/钥匙串命令

#### Scenario: 注入迁移注记必红

- **WHEN** 向任一受守护技能的任一侧正文注入一行"未随本仓库迁移"注记
- **THEN** 结构校验返回非零并指出该技能

#### Scenario: 字符口径可判中文

- **WHEN** writing-skills 的 token 效率验证命令运行于中文 SKILL.md
- **THEN** 输出为去空白字符数，可对照技能内登记的字符阈值判定

## MODIFIED Requirements

### Requirement: 高风险流程路径必须有施压场景

工作流行为契约 SHALL 以施压场景覆盖以下高风险路径，场景使用与其他场景相同的结构（共同要求＋逐字场景文本＋可判通过条件）：严格实现前的分支与 worktree 原子顺序、归档的 delta 合并与用户取消处置、审查中途 manifest 陈旧的处理。场景文件 SHALL 与镜像资产副本保持一致，结构校验 SHALL 守护这些场景的存在与关键通过条件。工作流技能正文变更的 Verify 终验 SHALL 重跑 `scripts/workflow-pressure-scenarios.md` 中与该技能行为契约相关的场景，相关性无法判定时重跑全部场景；重跑结果 SHALL 记录于该变更的 OpenSpec 目录。

#### Scenario: 新增高风险场景

- **WHEN** 维护者查看 `scripts/workflow-pressure-scenarios.md`
- **THEN** 存在覆盖 worktree 原子顺序、归档合并与取消、manifest STALE 的三个场景
- **AND** 每个场景的通过条件可判（引用明确的禁止动作与正确动作）
- **AND** 结构校验的 压力契约 检查包含这三个场景的标识与关键条件词

#### Scenario: 场景与资产副本漂移

- **WHEN** 实体场景文件与 `scripts/ai-workflow-assets/shared/scripts/` 下副本内容不一致
- **THEN** 字节一致性核对失败并要求同步

#### Scenario: 技能正文变更重跑场景

- **WHEN** 一个变更修改了任一工作流技能的正文
- **THEN** 其 Verify 终验现跑相关施压场景并逐场景记录 PASS/FAIL
- **AND** 任一场景 FAIL 时不得进入待归档，须回退该处措辞或按新事实重新确认范围
