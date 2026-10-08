# 工作流任务可观测性与模板护栏

## ADDED Requirements

### Requirement: 任务耗时必须可按任务和阶段追踪

工作流 SHALL 支持以稳定任务名标识一次变更，并为每个阶段记录开始时间、结束时间、耗时、结果和失败原因；现有汇总指标 SHALL 保持兼容。

#### Scenario: 查询完整任务耗时

- **WHEN** 一个任务完成 Open、Build、Verify 和 Archive 阶段
- **THEN** 工具能按任务名返回各阶段耗时与总耗时
- **AND** 失败阶段包含非空原因码

### Requirement: OpenSpec 模板必须生成可解析状态

OpenSpec proposal 模板 SHALL 生成顶层 `模式:` 和 `状态:` 字段，生成器 SHALL 拒绝带列表前缀或缺失字段的状态文档。

#### Scenario: 新建标准或严格变更

- **WHEN** 使用生成器创建变更
- **THEN** workflow validator 能直接解析 proposal 的模式和状态

### Requirement: 归档索引模板必须与目录一一对应

归档模板 SHALL 生成校验器识别的反引号变更名索引行；归档门禁 SHALL 在缺失、悬空或重复索引时失败。

#### Scenario: 归档新变更

- **WHEN** 变更目录移动到 `openspec/archive/`
- **THEN** 索引自动包含且只包含该变更名

### Requirement: manifest 最终化必须减少重复冻结且保留 stale 防护

审查工具 SHALL 支持在归档前固定最终 manifest 身份；任何最终化后的范围变化仍 SHALL 被 verify 判定为 `STALE`。

#### Scenario: 归档前写入最终证据

- **WHEN** tasks 或 review 记录写入最终 manifest 身份
- **THEN** 工具能完成一次最终 verify，且不要求因记录自身更新而无界重复冻结

### Requirement: 项目登记必须有可复用生成与校验入口

项目登记工具 SHALL 能生成或校验 registry、项目卡和规则路由的必填字段、路径边界和名称一致性。

#### Scenario: 登记一个新项目

- **WHEN** 输入项目名、路径、应用入口、职责和业务词
- **THEN** 工具生成三处登记内容或报告精确缺失项
- **AND** 不修改目标项目源码
