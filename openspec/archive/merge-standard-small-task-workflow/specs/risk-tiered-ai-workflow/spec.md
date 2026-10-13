# risk-tiered-ai-workflow

## MODIFIED Requirements

### Requirement: 标准模式必须消除重复审查

系统 SHALL 按任务规模与风险组织标准模式审查。命中“标准小任务”条件的变更 SHALL 由主会话执行一次综合自查并记录测试证据、diff 范围、finding 状态、未验证范围和残余风险，且 SHALL NOT 强制创建 review manifest。未命中小任务条件或多仓、跨契约、并行实现的变更 SHALL 保留一次独立综合审查与 manifest 冻结。严格模式仍 SHALL 使用任务级审查和 Verify 双阶段独立审查。

“标准小任务” SHALL 同时满足：单一职责；目标生产代码影响不超过3个文件；不涉及权限、资金、Schema/迁移、数据删除、并发一致性、跨服务或公开运行时契约；不触及工作流治理、助手入口、校验器或安装资产；目标测试能直接验证行为；不存在并行实现或多仓审查需求。

#### Scenario: 单文件或单一职责的小型代码任务

- **WHEN** 标准任务只修改一个服务方法并补充目标单元测试
- **AND** 不命中严格条件且无跨仓或契约风险
- **THEN** 主会话执行一次综合自查并记录简化终局证据
- **AND** 不创建 `.ai-local/reviews/<change>/manifest.json`

#### Scenario: 标准任务规模或风险提升

- **WHEN** 任务影响多个模块、公开契约、多仓或存在并行实现
- **THEN** 系统使用现有 review manifest 与一次综合审查
- **AND** 小任务简化记录不能替代该审查

#### Scenario: 标准模式完成构建

- **WHEN** 小任务实现与目标测试通过
- **THEN** Verify 现跑目标测试、相关回归和 `--fast`
- **AND** 简化记录包含测试命令、退出结果、finding 状态、未验证范围和残余风险

#### Scenario: 严格模式审查

- **WHEN** 任务被分类为严格模式
- **THEN** 继续使用任务级审查、规格符合性审查和质量审查，不因标准小任务简化而降低门禁

### Requirement: Archive 验证必须按 Verify 后变化选择层级

Archive SHALL 对归档后的主规格、目录结构、OpenSpec、diff 与 Git 状态运行新鲜校验。若最新有效 Verify 完整门禁通过后仅发生 proposal 状态更新、delta 到主规格的语义保持合并、目录移动、索引和条件知识沉淀，Archive SHALL 使用归档专用轻量门禁，不重复顶层契约套件。若工作流可执行文件、助手入口、技能语义、契约测试或其他运行时/治理语义在 Verify 后发生变化，Archive SHALL 重新运行完整 required 门禁。

Archive 知识沉淀 SHALL 条件触发：memory 仅用于新坑、环境绕行或非显然根因；kb 仅用于模块职责、入口、架构、契约或验证方式变化；rules 仅用于新术语、别名、路由或治理约束。无可复用事实时归档记录 SHALL 写明“知识沉淀：无”。

#### Scenario: 归档只产生机械状态变化

- **WHEN** Verify 后仅移动已审查文件、合并已审查 delta、更新状态与索引
- **THEN** Archive 运行 core、OpenSpec required、diff 和 Git 状态检查
- **AND** 不重复运行耗时的顶层契约套件

#### Scenario: 无新增知识事实

- **WHEN** 业务实现、模块入口和验证方式没有产生新事实
- **THEN** Archive 不机械写 memory/kb/rules
- **AND** 归档记录写明“知识沉淀：无”

#### Scenario: Archive 阶段修正工作流规则

- **WHEN** Archive 为通过校验而修改阶段技能、校验脚本或治理语义
- **THEN** 轻量门禁升级为完整 required 门禁
- **AND** 完整门禁失败时不得归档

## ADDED Requirements

### Requirement: 标准小任务根仓库提交必须精简

标准小任务 SHALL 在根仓库默认保留两个职责提交：已确认的 OpenSpec 计划基线，以及包含 Verify 结论与 Archive 结果的终局提交。中间状态推进 SHALL 记录在 OpenSpec 文件中，不要求逐状态提交。重要 finding 修复、范围扩展或治理资产变更 MAY 追加独立职责提交。

#### Scenario: 标准小任务正常完成

- **WHEN** 小任务从确认计划推进到已归档且未出现范围变化
- **THEN** 根仓库保留计划基线提交和终局归档提交
- **AND** 不为构建中、待验证、待归档分别制造状态提交

#### Scenario: Verify 修复重要问题

- **WHEN** 综合自查发现并修复 Critical/Important 问题
- **THEN** 允许为修复追加独立职责提交
- **AND** 终局提交仍包含 finding 处置与最终证据

### Requirement: 手工测试编译不得污染构建输出目录

当 Maven 目标测试不可用而使用手工 `javac`/`java` 作为临时测试通道时，编译输出 SHALL 写入 `/tmp` 或项目外目录，SHALL NOT 写入业务仓 `target/classes`、`target/test-classes` 或其他构建系统管理的输出目录。完成前 SHALL 运行一次 Maven compile 或同等生产编译门禁验证受影响生产源码。

#### Scenario: 使用独立 JUnit classpath

- **WHEN** 目标 Maven 测试被无关测试编译问题阻塞
- **THEN** 临时测试类编译到 `/tmp`
- **AND** 不更新 `target/classes` 的增量编译状态

#### Scenario: 完成声明前

- **WHEN** 临时通道测试全部通过
- **THEN** 系统运行 Maven compile 或同等生产编译命令并读取退出结果
- **AND** 未通过生产编译不得声称完成

### Requirement: OpenSpec 归档辅助脚本必须防误归档

系统 SHALL 提供归档辅助脚本：dry-run SHALL 校验 proposal 模式/状态、任务全勾选和终局证据；实际归档 SHALL 拒绝重复目标、保守合并 delta、置`已归档`、移动变更目录并更新归档索引；脚本 SHALL 提示后续 Archive 门禁与 Git 检查。归档辅助脚本 SHALL 纳入工作流 required 测试。

#### Scenario: 变更仍有未完成任务

- **WHEN** tasks 存在未勾选项且调用辅助脚本
- **THEN** 脚本非零退出且不移动变更目录

#### Scenario: 变更达到待归档且证据完整

- **WHEN** proposal 为`待归档`、任务全勾选、终局记录包含 finding 状态/未验证范围/残余风险
- **THEN** dry-run 输出 PASS 且不产生文件系统移动

#### Scenario: 执行实际归档

- **WHEN** 归档目标不存在且 delta 可合并
- **THEN** 脚本更新主规格、置状态`已归档`、移动目录并追加索引
- **AND** 提示运行 Archive 门禁与 Git 状态检查
