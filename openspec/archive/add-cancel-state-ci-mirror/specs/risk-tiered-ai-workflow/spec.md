# 取消路径与镜像覆盖 delta

## ADDED Requirements

### Requirement: 标准/严格变更可以经用户明确决定取消

系统 SHALL 允许处于`已归档`之前任一状态的活跃变更经用户明确决定进入`已取消`终态。助手可以建议取消，但 SHALL NOT 在没有用户明确决定时把任何变更置为`已取消`。取消时系统 SHALL 把 proposal 的`状态:`置为`已取消`、记录一句取消原因，并把变更目录整体移入 `openspec/archive/`；该变更的 delta 规格 SHALL NOT 合并进 `openspec/specs/` 主规格。已取消变更所在 feature 分支、worktree 与未提交修改的处置 SHALL 由用户在取消时明确指示；删除未合并工作仍 SHALL 遵守独立授权规则。

#### Scenario: 用户在实施前确认时拒绝方案并要求取消

- **WHEN** 变更处于`待确认规范`或`待确认计划`，用户明确表示不实施该方案并要求取消
- **THEN** 系统把 proposal 状态置为`已取消`并记录取消原因
- **AND** 变更目录移入 `openspec/archive/`，delta 不合并进主规格
- **AND** 系统不创建 feature 分支、worktree 或提交实现代码

#### Scenario: 构建中途取消

- **WHEN** 变更处于`构建中`或`待验证`，用户明确决定取消
- **THEN** 系统把 proposal 状态置为`已取消`、记录原因并移入 `openspec/archive/`
- **AND** feature 分支、worktree 与未提交修改的去留等待用户明确指示，不自动删除
- **AND** 后续不再对该变更执行 Verify、Archive 合并或知识沉淀

#### Scenario: 断点恢复不得复活已取消变更

- **WHEN** 后续会话在 `openspec/changes/` 恢复断点或用户新提同类需求
- **THEN** 已取消变更只作为 `openspec/archive/` 中的历史记录存在，不被恢复、不合并 delta
- **AND** 新需求按新变更目录重新分类进入

#### Scenario: 取消不破坏 OpenSpec 严格门禁

- **WHEN** 已取消变更（可能含未完成四件套）已移入 `openspec/archive/`
- **THEN** `openspec validate --all --strict` 与 `bash scripts/validate-workflow.sh --require-openspec` 仍按既有规则通过或失败，不因归档目录中的取消记录而新增失败项

#### Scenario: 助手不得自行取消

- **WHEN** 助手认为变更应当放弃但用户未明确决定
- **THEN** 助手只提出取消建议及理由，等待用户决定
- **AND** 不把`状态:`置为`已取消`，不移动变更目录

## MODIFIED Requirements

### Requirement: Codex 与 Claude 工作流必须保持一致

风险分流、模式边界、状态推进（含取消路径）、硬门禁和双套共存技能的语义 SHALL 同步体现在 `AGENTS.md`、`CLAUDE.md`、`.codex/skills/`、`.claude/skills/`、适配说明与校验脚本中。结构校验 SHALL 对全部双套共有的阶段与支撑技能执行镜像检查；镜像比对 SHALL 仅豁免声明的助手适配差异（技能目录路径前缀改写与显式标注的助手适配注记行），其余任何语义分叉 SHALL 使校验失败。结构校验 SHALL 能发现两套模式定义缺失、快速模式被错误要求四件套、或标准模式仍被强制独立计划/双审的回归。

#### Scenario: 工作流镜像发生漂移

- **WHEN** Codex 与 Claude 任一侧缺少快速/标准/严格模式或关键门禁定义
- **THEN** `scripts/validate-workflow.sh` 返回非零并指出缺失项

#### Scenario: 未受镜像检查的技能语义分叉

- **WHEN** 任一双套共存技能（含支撑技能）在两套运行时之间出现路径前缀与适配注记之外的语义差异
- **THEN** `scripts/validate-workflow.sh` 返回非零并指出该技能

#### Scenario: 旧规则重新强制统一重流程

- **WHEN** 总纲或阶段技能再次声明所有文档变更必须创建四件套、所有标准任务必须独立 Design 确认、或所有任务必须双阶段审查
- **THEN** 结构校验返回非零，阻止流程简化被后续修改悄悄回退
