## ADDED Requirements

### Requirement: 验证门禁按阶段分层

公共校验入口 SHALL 提供 `--fast` 模式,仅运行内部 core 结构校验并跳过顶层契约套件,退出码与汇总口径与全量模式一致;未传参默认 SHALL 保持全量行为不变。标准模式 Verify 终验 SHALL 运行 `--fast` 加变更相关目标与回归测试;标准模式 Archive 归档后验证 SHALL 运行全量默认门禁。严格模式 Verify 与 Archive SHALL 始终运行 `--require-openspec` 全量门禁,不得分层。变更若触及工作流入口、技能、校验器或安装资产,其标准模式 Verify 终验 SHALL 亦使用全量门禁。

#### Scenario: 标准模式内容变更的 Verify 终验

- **WHEN** 一个未触及工作流治理资产的标准变更到达 Verify 终验
- **THEN** 主会话现跑 `bash scripts/validate-workflow.sh --fast` 与目标/回归测试并读取退出结果
- **AND** 归档后验证仍现跑全量默认门禁,FAIL=0 才可声称归档完成

#### Scenario: 严格模式不得降级

- **WHEN** 严格模式变更进入 Verify 或 Archive
- **THEN** 门禁命令保持 `bash scripts/validate-workflow.sh --require-openspec`
- **AND** 不因任何分层能力改为 --fast

#### Scenario: 治理资产变更保持全量

- **WHEN** 标准模式变更修改了 CLAUDE/AGENTS、技能、校验器或安装资产
- **THEN** 其 Verify 终验运行全量门禁而非 --fast

### Requirement: 仓库技能优先于宿主插件技能

当宿主环境提供的插件技能与仓库技能职责重叠(如同名或同触发条件的 TDD、调试、审查类技能)时,助手 SHALL 以仓库技能(`.claude/skills/`、`.codex/skills/` 及其共享正文)为准;插件技能 SHALL 仅在仓库技能未覆盖的空缺时补充使用。该仲裁 SHALL 同步声明于 `CLAUDE.md` 与 `AGENTS.md`,并随安装资产的通用入口分发。

#### Scenario: 宿主插件提供同名 TDD 技能

- **WHEN** 宿主同时加载了仓库 tdd 技能与插件 TDD 技能
- **THEN** 助手按仓库 tdd 技能的红—绿—重构与适用边界执行
- **AND** 不因插件技能的存在产生第二套触发或仪式

#### Scenario: 仓库技能未覆盖的空缺

- **WHEN** 某任务无对应仓库技能而插件技能可用
- **THEN** 可以使用插件技能,并在汇报中注明所用技能来源
