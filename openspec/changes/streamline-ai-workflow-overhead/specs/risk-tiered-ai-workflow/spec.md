# Risk-tiered AI Workflow Simplification Delta

## MODIFIED Requirements

### Requirement: 标准模式只保留一个实施前确认点

标准模式 SHALL 由 Open 一次性产出 `proposal.md`、`specs/<能力>/spec.md` 和包含可执行步骤的 `tasks.md`。仅当变更存在跨模块取舍、新依赖、状态模型、重要替代方案或无法在 proposal/tasks 中清晰表达的架构决策时，才 SHALL 增加 `design.md`；不得为无独立设计决策的变更制造空壳 design。标准模式不得生成独立 `openspec/plan/<变更名>.md`。用户确认这些产物时 SHALL 同时确认范围、设计（如有）、任务与建议的本地分支整合策略，确认后系统可连续执行 Build、综合 Verify 和 Archive，除非范围变化、验证失败、出现争议或需要外部副作用授权。

#### Scenario: 标准任务没有独立架构决策

- **WHEN** 低到中风险变更只需在既有结构内修改一个职责边界
- **AND** 不引入新依赖、状态模型或跨模块取舍
- **THEN** Open 创建 proposal、delta spec 和可执行 tasks
- **AND** 不创建 design.md 或独立 plan
- **AND** 用户只进行一次实施前确认

#### Scenario: 标准任务存在重要设计取舍

- **WHEN** 标准变更存在两个以上有实质影响的实现方案或跨模块边界调整
- **THEN** Open 增加 design.md 记录决策、替代方案和风险
- **AND** 唯一一次实施前确认覆盖全部实际产物

#### Scenario: 标准模式确认后连续执行

- **WHEN** 用户确认标准模式产物及建议的本地整合策略
- **THEN** 系统无需在 Build 完成和本地 Archive 合并前重复请求确认
- **AND** 推送、创建 PR、强推、删除未合并工作或其他外部/破坏性动作仍须遵守独立授权规则

#### Scenario: 标准模式状态推进

- **WHEN** Open 已完成标准模式实际需要的产物并准备请求唯一一次实施前确认
- **THEN** 状态直接置为 `待确认计划`
- **AND** 确认后依次推进 `构建中 → 待验证 → 待归档 → 已归档`
- **AND** 不经过严格模式专用的 `待确认规范` 与 `设计中`

#### Scenario: 普通低到中风险代码变更

- **WHEN** 变更影响运行时代码但不满足严格模式条件
- **THEN** Open 将范围、行为契约和逐步实施/验证命令写入必要产物
- **AND** 只有存在独立架构决策时才增加 design.md
- **AND** 用户只需进行一次实施前确认

#### Scenario: 标准模式范围发生变化

- **WHEN** 构建或审查发现必须新增已确认范围之外的行为、依赖或数据变更
- **THEN** 系统暂停实施、更新当前变更产物并请求用户重新确认

## ADDED Requirements

### Requirement: 严格模式的第二次确认必须由计划风险触发

严格模式 SHALL 在 Open 四件套获得规范确认后进入独立 Design。若独立计划包含权限或资金行为、数据库 Schema/迁移、数据删除、破坏性动作、外部副作用，或引入规范确认中没有覆盖的选择、假设、依赖及范围，系统 SHALL 将状态置为`待确认计划`并等待第二次实施前确认。若计划只把已确认设计展开为可执行步骤且不包含上述风险，系统 MAY 在完成计划自审后直接进入 Build；用户明确要求查看计划时仍 SHALL 等待确认。

#### Scenario: Schema 变更生成实施计划

- **WHEN** 严格计划包含数据库字段、索引、迁移或数据回填
- **THEN** 系统必须请求第二次计划确认
- **AND** 未确认前不得实现

#### Scenario: 工作流文本与测试按已确认方案展开

- **WHEN** 严格变更不涉及业务运行时、数据迁移或外部副作用
- **AND** 独立计划没有引入规范之外的新选择或范围
- **THEN** 系统完成计划自审后可以连续进入 Build
- **AND** 计划和状态推进仍须记录在 OpenSpec 真源中

#### Scenario: 用户要求查看所有严格计划

- **WHEN** 用户明确要求实施前查看独立计划
- **THEN** 系统将状态置为`待确认计划`并等待用户确认

### Requirement: 严格任务级审查必须绑定高风险实现单元

严格模式 SHALL 对权限、资金、Schema/迁移、数据删除、并发一致性、跨服务契约和不可逆副作用等高风险实现单元执行任务级审查；多个 checklist 若共同构成同一风险边界 SHALL 合并为一次审查。纯机械适配、文档同步和同一风险单元内的测试补充 SHALL NOT 各自触发完整任务级审查。Verify 仍 SHALL 保留规格符合性与代码质量两个独立关注面。

#### Scenario: 多个步骤共同实现一个并发边界

- **WHEN** 三个 checklist 分别增加条件写、竞争测试和日志，但共同保证同一个并发不变量
- **THEN** 系统按该并发不变量形成一个任务级审查单元
- **AND** 不机械执行三次完整审查

#### Scenario: 严格变更包含多个独立高风险边界

- **WHEN** 同一变更同时修改权限判定和数据库迁移
- **THEN** 两个风险边界分别获得任务级审查
- **AND** Verify 阶段继续执行两个独立关注面

### Requirement: Archive 验证必须按 Verify 后变化选择层级

Archive SHALL 对归档后的主规格、目录结构、OpenSpec、diff 与 Git 状态运行新鲜校验。若最新有效 Verify 完整门禁通过后仅发生 proposal 状态更新、delta 到主规格的语义保持合并、目录移动、索引和知识沉淀，Archive SHALL 使用归档专用轻量门禁，不重复顶层契约套件。若工作流可执行文件、助手入口、技能语义、契约测试或其他运行时/治理语义在 Verify 后发生变化，Archive SHALL 重新运行完整 required 门禁。

#### Scenario: 归档只产生机械状态变化

- **WHEN** Verify 后仅移动已审查文件、合并已审查 delta、更新状态与索引
- **THEN** Archive 运行 core、OpenSpec required、diff 和 Git 状态检查
- **AND** 不重复运行耗时的顶层契约套件

#### Scenario: 归档阶段修正工作流规则

- **WHEN** Archive 为通过校验而修改阶段技能、校验脚本或治理语义
- **THEN** 轻量门禁升级为完整 required 门禁
- **AND** 完整门禁失败时不得归档

### Requirement: 已归档审查缓存必须可安全清理

`.ai-local` SHALL 只保存本地运行时锁和活跃审查缓存，不作为变更状态或永久证据真源。Archive 在持久归档记录包含最终 manifest ID、逐仓 comparison base、finding 处置、未验证范围和残余风险后 MAY 删除该变更的本地 review 目录；活跃变更、STALE 待处理审查或尚未持久化最终证据的目录 SHALL NOT 被自动清理。

#### Scenario: 变更完成归档

- **WHEN** 最终审查身份与结论已经写入归档 tasks 或 review 记录
- **AND** 变更状态已置为已归档
- **THEN** 对应 `.ai-local/reviews/<change>/` 可作为缓存清理
- **AND** 删除缓存不影响 OpenSpec 状态、规格或审查可追溯性

#### Scenario: 变更仍在复审

- **WHEN** manifest 为 STALE、仍有开放 finding 或 proposal 尚未归档
- **THEN** 系统保留该 review 目录
- **AND** 不把缓存清理当作关闭 finding 的手段

