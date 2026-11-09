# Verify 技能接线 WORKFLOW_STANDARD_BASE 基线

## ADDED Requirements

### Requirement: Verify 技能必须接线标准层裁剪基线

Verify 技能 SHALL 在标准层验证调用中显式提供 `WORKFLOW_STANDARD_BASE` 基线，基线取上一全量验证通过的提交（如上一变更归档提交，或已通过全量验证的本轮构建起点）；技能文本 SHALL 声明基线不确定时不提供变量以保持契约套件全量、层级升级为 required 时基线不适用。两棵助手技能树的 verify 技能 SHALL 保持镜像一致，打包资产副本 SHALL 与源逐字节同步。

#### Scenario: 技能接线提供基线

- **WHEN** Verify 技能文本描述标准层验证调用
- **THEN** 调用形式含 `WORKFLOW_STANDARD_BASE` 环境变量与基线取值说明
- **AND** `.claude` 与 `.codex` 两棵技能树对应语句镜像一致

#### Scenario: 基线不确定时回退全量

- **WHEN** 执行会话无法确定上一全量验证通过的提交
- **THEN** 技能指导不提供 `WORKFLOW_STANDARD_BASE` 变量
- **AND** wrapper 按现状执行契约套件全量

#### Scenario: 校验器锁定接线锚点

- **WHEN** core 的 Verify 标准分层技能内容锚点执行
- **THEN** 锚点要求 verify 技能文件包含 `WORKFLOW_STANDARD_BASE` token
- **AND** 契约测试镜像锁定该锚点 token
