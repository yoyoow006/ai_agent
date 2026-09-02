# Delta Spec: 场景 I 一致性条款⑥短语行为化

## MODIFIED Requirements

### Requirement: 高风险流程路径必须有施压场景

工作流行为契约 SHALL 以施压场景覆盖以下高风险路径，场景使用与其他场景相同的结构（共同要求＋逐字场景文本＋可判通过条件）：严格实现前的分支与 worktree 原子顺序、归档的 delta 合并与用户取消处置、审查中途 manifest 陈旧的处理。场景文件 SHALL 与镜像资产副本保持一致，结构校验 SHALL 守护这些场景的存在与关键通过条件。安装目标已有助手入口的冲突处置场景（场景 I）SHALL 与 `codex-workflow-target-installation` 规格的冲突入口条款语义一致：通过条件要求先 dry-run 或等价完整预检，差异入口按保留再替换处置（重命名 `AGENTS.pre-codex-workflow.md`＋SHA-256 校验一致＋安装器显式清单创建新入口），不得要求盲覆盖、输出既有正文或建议 `--force`；通过条件 SHALL 要求说明可由维护者选择在临时空目录生成模板人工整合（替代方案），其措辞 SHALL 为行为性（可按是否主动说明判定）。场景契约与安装规格任一侧修改冲突处置语义时，SHALL 以独立变更同步另一侧，不得单方面漂移。工作流技能正文变更的 Verify 终验 SHALL 重跑 `scripts/workflow-pressure-scenarios.md` 中与该技能行为契约相关的场景，相关性无法判定时重跑全部场景；重跑结果 SHALL 记录于该变更的 OpenSpec 目录。

#### Scenario: 新增高风险场景

- **WHEN** 维护者查看 `scripts/workflow-pressure-scenarios.md`
- **THEN** 存在覆盖 worktree 原子顺序、归档合并与取消、manifest STALE 的三个场景
- **AND** 每个场景的通过条件可判（引用明确的禁止动作与正确动作）
- **AND** 结构校验的 压力契约 检查包含这三个场景的标识与关键条件词

#### Scenario: 场景 I 与安装规格语义一致

- **WHEN** 维护者对照场景 I 通过条件与 `codex-workflow-target-installation` 规格的冲突入口条款
- **THEN** 两者对差异入口的处置同为保留再替换（备份＋SHA-256 校验＋安装器显式清单）
- **AND** 场景 I 不含冲突关闭零写入要求，且保留预检、不输出既有正文、不建议 `--force` 的条件
- **AND** 场景 I 的替代方案条款为行为性措辞，与安装规格的上报极简性条款同向

#### Scenario: 场景 I 关键条件被守护

- **WHEN** 向场景 I 注入移除保留再替换关键条件（备份路径、SHA-256 校验或不输出既有正文）的修改
- **THEN** 结构校验返回非零并指出该场景

#### Scenario: 单侧漂移被阻止

- **WHEN** 一个变更只修改场景 I 或 `codex-workflow-target-installation` 规格其中一侧的冲突处置语义
- **THEN** 其 Verify 对照本条款发现另一侧未同步，变更不得进入待归档

#### Scenario: 场景与资产副本漂移

- **WHEN** 实体场景文件与 `scripts/ai-workflow-assets/shared/scripts/` 下副本内容不一致
- **THEN** 字节一致性核对失败并要求同步

#### Scenario: 技能正文变更重跑场景

- **WHEN** 一个变更修改了任一工作流技能的正文
- **THEN** 其 Verify 终验现跑相关施压场景并逐场景记录 PASS/FAIL
- **AND** 任一场景 FAIL 时不得进入待归档，须回退该处措辞或按新事实重新确认范围
