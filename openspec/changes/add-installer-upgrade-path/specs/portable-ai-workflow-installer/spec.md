# 升级路径 delta

## ADDED Requirements

### Requirement: 安装器必须支持台账驱动的升级

安装器 SHALL 提供 `--upgrade` 模式，与 `--target`、`--assistant` 组合并支持 `--dry-run` 预览。安装与升级 SHALL 在 `.ai/assistant-profile.json`（schema_version 2）中维护安装台账：记录每个 manifest 文件安装时的内容 SHA-256。升级时对每个文件 SHALL 按以下规则行动：目标内容哈希等于台账哈希（未被目标修改）时替换为新版内容；等于新版内容时记 `UNCHANGED`；台账不匹配或无台账且内容不等于新版时记 `SKIPPED` 并继续处理其余文件。已从新版 manifest 移除的文件 SHALL 仅在台账确认未被目标修改时删除，否则保留并报告。升级 SHALL 沿用安装的事务发布与回滚机制，台账更新 SHALL 与文件变更处于同一事务。目标已存在的助手入口文件 SHALL 不被升级触碰，仅报告。

#### Scenario: 未修改文件自动升级

- **WHEN** 目标中某 manifest 文件内容哈希等于台账记录且不等于新版内容
- **THEN** 升级将其替换为新版内容并输出 `UPGRADED`
- **AND** 同一事务内更新台账哈希

#### Scenario: 目标修改过的文件被跳过

- **WHEN** 目标中某 manifest 文件内容哈希不等于台账记录且不等于新版内容
- **THEN** 该文件保持原样并输出 `SKIPPED` 与差异提示
- **AND** 其余文件的升级继续执行

#### Scenario: legacy v1 profile 首次升级

- **WHEN** 目标 profile 为 schema_version 1（无台账）
- **THEN** 内容等于新版的文件记 `UNCHANGED`，其余全部 `SKIPPED` 报告
- **AND** 升级完成后 profile 升为 schema_version 2 并写入台账

#### Scenario: 已移除文件按台账清理

- **WHEN** 某文件存在于目标与台账但已不在新版 manifest
- **AND** 目标内容哈希等于台账哈希
- **THEN** 升级删除该文件并输出 `REMOVED`
- **AND** 哈希不匹配时保留并输出 `KEPT` 与报告

#### Scenario: 升级预览不写入

- **WHEN** 以 `--dry-run` 运行升级
- **THEN** 输出逐文件计划与汇总且零写入，退出码 0

#### Scenario: 升级中断回滚

- **WHEN** 升级事务在发布阶段失败或被中断
- **THEN** 目标文件与台账整体回滚到升级前状态，不出现半升级状态

#### Scenario: 助手入口不被升级触碰

- **WHEN** 目标已存在 `AGENTS.md` 或 `CLAUDE.md`
- **THEN** 升级不修改其内容，仅在报告中提示人工整合
