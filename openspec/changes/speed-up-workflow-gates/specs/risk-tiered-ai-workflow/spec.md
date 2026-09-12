# Risk-tiered AI Workflow Gate Acceleration Delta

## MODIFIED Requirements

### Requirement: 验证门禁按阶段分层

公共校验入口 SHALL 提供 `--fast` 模式，仅运行内部 core 结构校验并跳过顶层契约套件，退出码与汇总口径与全量模式一致；未传参默认 SHALL 保持全量行为不变。`--fast` 模式 MAY 对指定的重检查使用输入指纹等价缓存：当检查命令、core 校验器内容与声明输入文件集合的指纹与上次实际执行的 PASS 记录一致时，MAY 沿用该结果，并 MUST 在该检查行内透明标注指纹、上次实际执行时间与“沿用”来源；任一输入、命令或实现变化，缓存缺失、损坏或格式非法，或上次结果非 PASS 时 SHALL 重新实际执行。`--require-openspec` 与默认全量模式 SHALL NOT 读取或写入该缓存。标准模式 Verify 终验 SHALL 运行 `--fast` 加变更相关目标与回归测试；标准模式 Archive 归档后验证 SHALL 运行全量默认门禁。严格模式 Verify 与 Archive SHALL 始终运行 `--require-openspec` 全量门禁，不得分层。变更若触及工作流入口、技能、校验器或安装资产，其标准模式 Verify 终验 SHALL 亦使用全量门禁。

#### Scenario: 标准模式内容变更的 Verify 终验

- **WHEN** 一个未触及工作流治理资产的标准变更到达 Verify 终验
- **THEN** 主会话现跑 `bash scripts/validate-workflow.sh --fast` 与目标/回归测试并读取退出结果
- **AND** 归档后验证仍现跑全量默认门禁，FAIL=0 才可声称归档完成

#### Scenario: fast 暖缓存命中

- **WHEN** `--fast` 模式下某重检查的命令、输入文件与 core 实现均与上次实际执行的 PASS 记录一致
- **THEN** 该检查输出 PASS 并透明标注指纹、上次实际执行时间与沿用来源
- **AND** 顶层汇总仍按 PASS 计数，不新增第四种检查状态

#### Scenario: 缓存输入变化

- **WHEN** 重检查任一输入文件、检查命令或 core 实现在上次 PASS 后发生变化
- **THEN** 该检查重新实际执行并按新结果更新或清除缓存

#### Scenario: 严格模式不得降级

- **WHEN** 严格模式变更进入 Verify 或 Archive
- **THEN** 门禁命令保持 `bash scripts/validate-workflow.sh --require-openspec`
- **AND** 不因任何分层或缓存能力改为 `--fast`，也不读取缓存结果

#### Scenario: 治理资产变更保持全量

- **WHEN** 标准模式变更修改了 CLAUDE/AGENTS、技能、校验器或安装资产
- **THEN** 其 Verify 终验运行全量门禁而非 `--fast`
