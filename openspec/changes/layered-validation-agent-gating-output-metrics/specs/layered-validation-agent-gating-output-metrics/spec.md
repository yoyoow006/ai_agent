# 分层验证、代理门控与输出度量

## ADDED Requirements

### Requirement: 验证必须按可审计计划分层执行

系统 SHALL 为每次验证生成 fast、standard、required 或 archive-light 的显式执行计划，列明触发原因、检查集合、升级条件和停止规则；安全失败 SHALL 阻止依赖其结果的后续层级。

#### Scenario: standard 逐层升级

- **WHEN** 运行 standard 且变更文件命中工作流入口、技能、校验器、模板或安装资产
- **THEN** 输出升级原因并执行 required 计划
- **AND** 不把 fast 缓存结果当作终验结果

#### Scenario: 层级失败停止

- **WHEN** 前置 core 层返回 FAIL 或不可解析结果
- **THEN** 后续依赖层不执行
- **AND** 人类汇总与诊断事件均保留失败原因和未执行层级

### Requirement: 代理调用必须满足四项门控条件

系统 SHALL 仅在任务具有明确独立边界、角色契约匹配、可执行验收命令且无共享写入/顺序依赖时允许调用 explorer、reviewer 或 test worker；否则 SHALL 拒绝调用并记录结构化原因。快速任务与边界集中的标准小任务 SHALL NOT 自动调用代理。

#### Scenario: 缺少独立边界时拒绝

- **WHEN** 派发请求未声明独立文件/职责边界或与其他任务重叠
- **THEN** 调度器拒绝派发
- **AND** 输出 dispatch=denied、原因码和主会话处理路径

#### Scenario: 合法测试代理调用

- **WHEN** test worker 获得点名测试文件范围、明确命令且无共享写入冲突
- **THEN** 调度器允许派发并输出 dispatch/result 事件
- **AND** 结果包含退出码、失败数、未验证范围与残余风险

### Requirement: 输出协议必须稳定且双轨兼容

系统 SHALL 保持人类输出的 PASS/FAIL/SKIP 语义与汇总末行，并在启用 JSONL 诊断时为计划、检查、代理调用、错误和汇总分别输出可独立解析的事件；每个事件 SHALL 包含 schema_version、run_id、event、timestamp、layer 和 status，适用时包含 command、exit_code、reason_code 与 duration_ms。

#### Scenario: JSONL 失败事件可解析

- **WHEN** 检查命令失败、工具缺失或输出解析失败
- **THEN** 生成 status 为 FAIL 或 SKIP 的单行事件
- **AND** 事件包含稳定 reason_code，且人类汇总仍为末行

#### Scenario: 未启用诊断保持兼容

- **WHEN** 未设置 JSONL 输出选项
- **THEN** 不产生额外 tracked 输出文件
- **AND** 现有 PASS/FAIL/SKIP 行和退出码保持兼容

### Requirement: 轻量度量必须可丢弃且不改变门禁

系统 SHALL 为每次运行记录 schema、run_id、层级总耗时、检查结果计数、代理允许/拒绝计数、缓存沿用计数和输出解析错误计数；指标写入 .ai-local/metrics/ 失败或记录损坏 SHALL 不改变验证结果，且 required SHALL 不读取验证缓存。

#### Scenario: 指标写入失败

- **WHEN** 指标目录不可写或原子写入失败
- **THEN** 验证继续按真实检查结果返回
- **AND** 输出明确的 metrics_write_failed 诊断，不伪造指标成功

#### Scenario: 指标不作为状态真源

- **WHEN** 读取历史指标或删除指标文件
- **THEN** 当前运行不改变其层级、检查结果或 OpenSpec 状态
