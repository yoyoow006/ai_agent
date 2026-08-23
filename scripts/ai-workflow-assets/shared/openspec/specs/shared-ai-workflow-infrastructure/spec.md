# 共享 AI 工作流基础设施规范

## Purpose

定义跨助手共享知识、确定性项目事实查询、审查范围冻结、有限代理角色和验证诚实性，使标准与严格流程可复核，同时保持快速模式轻量且不改变业务运行时。

## Requirements

### Requirement: 跨助手知识必须只有一个共享真源

系统 SHALL 使用根 `.ai/` 作为 Claude、Codex 等助手共享知识的唯一正文来源，并按 `kb`、`rules`、`memory`、`prompts`、`tools` 分离稳定事实、硬约束、跨会话经验、轻量角色契约和确定性工具。`.codex` 与 `.claude` SHALL 只保存助手特有适配或技能；旧 ai-kb 路径在迁移期只能提供指向共享真源的兼容说明，不得继续保存可独立演化的平行正文。

#### Scenario: 同一知识被两个助手读取

- **WHEN** Claude 与 Codex 需要读取同一项目事实、路由规则或踩坑记录
- **THEN** 两者解析到 `.ai/` 中同一份正文
- **AND** 校验器能够拒绝旧路径再次出现平行知识文件

#### Scenario: 助手存在工具特有行为

- **WHEN** 某项指令只适用于 Codex 或 Claude 的工具调用方式
- **THEN** 该适配保留在对应助手目录
- **AND** 不把工具特有配置提升为共享业务事实或共享治理正文

### Requirement: OpenSpec 必须继续作为变更状态唯一真源

共享知识迁移 SHALL NOT 创建第二套 tracked 变更状态。标准和严格模式的模式、状态、范围与进度仍 SHALL 由 `openspec/changes/<变更名>/proposal.md` 和 `tasks.md` 表示；快速模式仍不创建 OpenSpec 状态。

#### Scenario: 助手恢复严格变更

- **WHEN** 任一助手接手已有严格模式变更
- **THEN** 它先读取 OpenSpec proposal 状态和 tasks 进度，再按 `.ai` 路由补充知识
- **AND** 不从本地临时 manifest、prompt 或助手私有目录推断权威状态

### Requirement: 项目事实查询必须声明式、有界且只读

系统 SHALL 提供声明式项目 registry 和项目卡，并至少提供 `project-context`、`server-registry`、`workspace-search` 三类只读查询。查询 SHALL 只进入 registry 登记且本地已检出的路径，遵循 ignore，支持显式项目过滤和输出上限，不得自动 clone、联网、修改源码、生成知识正文或输出凭据与被忽略文件内容。

#### Scenario: 已知项目名获取上下文

- **WHEN** 助手以登记项目名调用 `project-context`
- **THEN** 工具返回项目路径、构建类型、项目卡、入口和可用状态的有界摘要
- **AND** 项目未检出时明确报告缺失，不尝试联网补齐

#### Scenario: 已知 server 名定位实现

- **WHEN** 助手以 server 名调用 `server-registry`
- **THEN** 工具在登记项目内返回唯一项目、模块和应用入口，或者明确返回零匹配/歧义
- **AND** 不要求无界扫描整个工作区

#### Scenario: 搜索跨项目消费者

- **WHEN** 助手以符号、API 或消息名调用 `workspace-search`
- **THEN** 工具只搜索显式选择或 registry 登记的已检出项目并遵守结果上限
- **AND** 截断时返回可继续分页或缩小范围的提示

#### Scenario: 查询试图越过登记边界

- **WHEN** 参数指向未登记路径、被忽略内容或要求写入知识正文
- **THEN** 工具拒绝请求并返回非零

### Requirement: 标准和严格 Review 必须冻结并校验精确范围

标准与严格模式的完整审查 SHALL 在 reviewer 读取前生成本地 freeze manifest。manifest SHALL 对每个受影响 Git 仓记录仓路径、comparison base 输入及解析 SHA、HEAD、committed/staged/unstaged 范围、未忽略 untracked 路径和内容哈希。reviewer SHALL 在读取范围前和形成结论前执行只读 verify；任一记录发生变化时 SHALL 返回 `STALE` 并停止沿用该结论。

#### Scenario: 审查范围在结论前未变化

- **WHEN** freeze 后各仓 base、HEAD、tracked 差异、untracked 路径和哈希均未变化
- **THEN** verify 返回有效
- **AND** 审查结论引用 manifest 标识和逐仓范围

#### Scenario: 审查期间文件发生变化

- **WHEN** freeze 后任一纳入范围的文件、HEAD、base 或未跟踪文件集合发生变化
- **THEN** verify 返回 `STALE` 和变化摘要
- **AND** reviewer 不得把旧结论作为当前文件树的通过证据

#### Scenario: 快速模式维护现有事实

- **WHEN** 任务符合快速模式
- **THEN** 系统继续使用权威事实核对、针对性验证和完整 diff 检查
- **AND** 不强制创建 freeze manifest 或独立 reviewer

### Requirement: 审改必须使用有界 finding 台账和差异复审

完整审查 SHALL 一次列出有证据的阻断项、非阻断建议、未验证范围和残余风险。修复后 SHALL 只审上一有效 manifest 到当前 manifest 的差异、直接消费者以及继承的开放阻断项；不得无新证据重读未变化范围或追加原本可在完整审查发现的建议。风险接受 SHALL 只有用户在看到影响和残余风险后明确设置。

#### Scenario: 完整审查发现阻断项

- **WHEN** reviewer 发现影响正确性、安全、契约或可验证性的 Critical/Important 问题
- **THEN** 台账记录位置、证据、可观察影响、状态、最小修复方向和复验方式
- **AND** 问题在解决、被证明不成立或用户明确接受风险前阻断归档

#### Scenario: 已确认范围内修复 finding

- **WHEN** finding 的最小修复不扩大已确认需求范围
- **THEN** 按当前模式的既有授权规则实施并生成新的 delta manifest
- **AND** 复审限于该差异、直接消费者和继承问题

#### Scenario: 修复需要扩大范围

- **WHEN** finding 只能通过新增未确认行为、依赖、迁移或外部副作用解决
- **THEN** 系统暂停并更新事实源，请求用户重新确认

### Requirement: 代理角色必须有限、只在命中边界时启用

系统 SHALL 为 explorer、reviewer、test worker 提供最小共享角色契约和助手适配。角色 SHALL 分别限制为只读探索、独立只读审查、测试设计与验证；是否委派仍由现有风险、独立性和可验收边界决定。快速任务和标准小任务 SHALL NOT 因存在角色配置而默认使用子代理。

#### Scenario: 严格模式需要独立审查

- **WHEN** 严格模式进入任务级或 Verify 独立审查
- **THEN** reviewer 使用全新上下文、有效 manifest、规格和验证证据
- **AND** 不继承实现者的结论或修改工作树

#### Scenario: 标准小任务边界集中

- **WHEN** 标准任务规模小且没有可独立验收的并行边界
- **THEN** 主会话直接执行
- **AND** 不为使用角色配置而机械委派

### Requirement: 工作流验证必须显式区分通过、失败和未运行

工作流校验 SHALL 对每项检查输出 PASS、FAIL 或 SKIP；依赖不可用时不得静默省略。默认本地校验可以显式 SKIP 可选工具，但严格 Verify/Archive 使用的门禁 SHALL 能要求 OpenSpec CLI 和全部必需测试实际执行。共享知识结构、旧路径双真源、项目 registry、工具单测、查询边界、manifest stale 检测、助手适配与风险分级 mutation SHALL 进入自动化回归。

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

### Requirement: 迁移必须可回退且不得改变业务运行时

共享层迁移 SHALL 分阶段完成，每阶段在删除旧正文前验证新入口、引用、助手适配和回归测试。迁移 SHALL 保护用户未提交修改，不得修改业务项目运行时代码、API、Schema、部署配置或自动执行远端操作。

#### Scenario: 旧 ai-kb 引用尚未迁移完成

- **WHEN** 校验发现仍有入口引用旧正文路径
- **THEN** 迁移停止在兼容阶段，不删除对应旧内容
- **AND** 报告引用位置和剩余风险

#### Scenario: 业务项目目录存在未提交修改

- **WHEN** 工具或迁移发现登记业务仓存在用户修改
- **THEN** 只读查询可以继续按边界运行
- **AND** 任何会触及该仓的写入、清理或分支操作必须停止并另行处理
