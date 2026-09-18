# Installer Knowledge Separation Project Template Delta

## MODIFIED Requirements

### Requirement: 通用项目登记能力必须保留

仓库 SHALL 保留空白 `registry.json`、通用项目登记说明、通用项目卡模板、事实查询工具及其测试，使目标项目安装后可自行登记自身项目事实。

#### Scenario: 查询空白 registry

- **WHEN** 解析 `.ai/kb/projects/registry.json`
- **THEN** `schema_version` 为 `1` 且 `projects` 为空数组
- **AND** `.ai/tools/tests/` 中的事实工具测试通过

#### Scenario: 分发通用项目卡模板

- **WHEN** 检查 `.ai/kb/projects/_template.md`
- **THEN** 模板只包含非业务占位符、结构说明和维护边界
- **AND** 模板随安装资产分发，但不登记任何具体目标项目
