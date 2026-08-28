# 回归防护扩展 delta

## MODIFIED Requirements

### Requirement: 工作流验证必须显式区分通过、失败和未运行

工作流校验 SHALL 对每项检查输出 PASS、FAIL 或 SKIP；依赖不可用时不得静默省略。默认本地校验可以显式 SKIP 可选工具，但严格 Verify/Archive 使用的门禁 SHALL 能要求 OpenSpec CLI 和全部必需测试实际执行。共享知识结构、旧路径双真源、项目 registry、工具单测、查询边界、manifest stale 检测、助手适配与风险分级 mutation SHALL 进入自动化回归。行为回退注入 SHALL 额外覆盖：快速模式被要求自动提交或合并、标准模式被允许跳过唯一实施前确认直接实现、归档被允许跳过校验直接移动目录。镜像归一化豁免 SHALL 受登记数守卫：以受豁免前缀开头的适配注记行全仓数量 SHALL 等于显式登记值，超出即校验失败。CI 的动作引用 SHALL 以 commit SHA 固定并注明对应版本。

#### Scenario: OpenSpec CLI 不可用的普通诊断

- **WHEN** 运行默认工作流校验且环境没有 OpenSpec CLI
- **THEN** 输出明确的 `SKIP`、原因和未覆盖范围
- **AND** 不宣称 OpenSpec 严格校验通过

#### Scenario: 严格终验缺少 OpenSpec CLI

- **WHEN** 严格 Verify 或 Archive 以 required 模式运行校验且 OpenSpec CLI 不可用
- **THEN** 校验返回非零并阻止完成声明

#### Scenario: 事实工具发生回归

- **WHEN** registry 解析、查询边界、分页、敏感内容过滤或 manifest stale 检测测试失败
- **THEN** 主校验返回非零并指出失败测试

#### Scenario: 新类行为回退被注入

- **WHEN** 向入口或阶段技能注入"快速模式必须自动提交合并""标准模式无需用户确认即可实现"或"归档前无需校验直接移动目录"类规则
- **THEN** 结构校验返回非零并指出该注入

#### Scenario: 未登记的适配注记出现

- **WHEN** 双套技能树中出现超出登记数量的受豁免前缀适配注记行
- **THEN** 结构校验返回非零，要求显式登记后再放行

#### Scenario: CI 动作引用漂移回 tag

- **WHEN** CI 工作流中的动作引用回退为不带 commit SHA 的浮动 tag
- **THEN** 维护者可通过登记的 SHA 注释直接识别；该加固随本规格落地后不得移除
