# Risk-tiered AI Workflow Semantic Sync Delta

## MODIFIED Requirements

### Requirement: 验证门禁按阶段分层

公共校验入口 SHALL 提供 `--fast` 模式，仅运行内部 core 结构校验并跳过顶层契约套件，退出码与汇总口径与全量模式一致；未传参默认 SHALL 保持全量行为不变。`--fast` 模式 MAY 对指定的重检查使用输入指纹等价缓存：当检查命令、core 校验器内容与声明输入文件集合的指纹与上次实际执行的 PASS 记录一致时，MAY 沿用该结果，并 MUST 在该检查行内透明标注指纹、上次实际执行时间与“沿用”来源；任一输入、命令或实现变化，缓存缺失、损坏或格式非法，或上次结果非 PASS 时 SHALL 重新实际执行。`--require-openspec` 与默认全量模式 SHALL NOT 读取或写入该缓存。标准模式 Verify 终验 SHALL 运行 `--fast` 加变更相关目标与回归测试；严格模式 Verify SHALL 运行 `--require-openspec`。Archive SHALL 按“Archive 验证必须按 Verify 后变化选择层级”执行轻量或升级后的 required 门禁，而不是按模式无条件重复完整门禁。变更若触及工作流入口、技能、校验器或安装资产，其标准模式 Verify 终验 SHALL 亦使用全量门禁。

#### Scenario: 标准模式内容变更的 Verify 终验

- **WHEN** 一个未触及工作流治理资产的标准变更到达 Verify 终验
- **THEN** 主会话现跑 `bash scripts/validate-workflow.sh --fast` 与目标/回归测试并读取退出结果
- **AND** Archive 按 Verify 后 diff 分类运行轻量或升级后的 required 门禁，FAIL=0 才可声称归档完成

#### Scenario: 严格模式 Verify 不得降级

- **WHEN** 严格模式变更进入 Verify
- **THEN** 门禁命令保持 `bash scripts/validate-workflow.sh --require-openspec`
- **AND** 不因任何分层或缓存能力改为 `--fast`，也不读取缓存结果
- **AND** 其 Archive 若发生 Verify 后治理语义变化，同样升级为 required 门禁

#### Scenario: 治理资产变更保持全量

- **WHEN** 标准模式变更修改了 CLAUDE/AGENTS、技能、校验器或安装资产
- **THEN** 其 Verify 终验运行全量门禁而非 `--fast`

## ADDED Requirements

### Requirement: 流程语义必须在双运行时文档和安装资产中保持一致

Codex 与 Claude 根入口、用户文档、共享知识总览、阶段技能和便携安装资产 SHALL 表达同一套风险分级语义：标准模式三件套加条件 design、严格模式第二次确认由硬风险触发、任务级审查按高风险实现单元组织，以及 Archive 按 Verify 后变化选择轻量或完整门禁。自动化回归 SHALL 覆盖双入口、关键文档和安装资产中的旧口径回归。

#### Scenario: Claude 入口保留旧标准口径

- **WHEN** Claude 根入口或其安装资产重新要求标准模式固定创建 design
- **THEN** 工作流契约测试失败
- **AND** 安装产物不得被判为与 Codex 语义一致

#### Scenario: 用户文档保留旧归档口径

- **WHEN** README、使用介绍或共享 overview 要求归档后一律重复完整契约套件
- **THEN** mutation/契约测试失败
- **AND** 文档必须同步 archive-light 与自动升级语义

#### Scenario: 安装资产保留旧严格确认口径

- **WHEN** 便携安装资产要求所有严格计划无条件二次确认
- **THEN** 工作流回归失败
- **AND** 安装器不得把旧语义发布到目标项目
