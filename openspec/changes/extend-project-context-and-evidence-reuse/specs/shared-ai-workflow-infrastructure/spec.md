# Shared AI Workflow Infrastructure Project Context Delta

## MODIFIED Requirements

### Requirement: 项目事实查询必须声明式、有界且只读

系统 SHALL 提供声明式项目 registry 和项目卡，并至少提供 `project-context`、`server-registry`、`workspace-search` 三类只读查询。查询 SHALL 只进入 registry 登记且本地已检出的路径，遵循 ignore，支持显式项目过滤和输出上限，不得自动 clone、联网、修改源码、生成知识正文或输出凭据与被忽略文件内容。

项目 registry SHALL 支持每个项目声明可选 `dependencies` 项目名列表和可选 `verification` 对象。`dependencies` SHALL 只引用同 registry 中存在的其他项目，并 SHALL NOT 包含自依赖、重复项或形成循环。`verification` MAY 声明非空单行 `build_command` 与 `test_command`、相对 `.ai/` 且实际存在的 `evidence` 文档，以及 40 或 64 位十六进制 `verified_commit`。`project-context` SHALL 输出直接依赖和验证入口，并在本地项目为 Git 工作树时把 `verified_commit` 与当前 HEAD 比较为 current 或 drifted，未检出或非 Git 时输出 unavailable；比较 SHALL 保持只读且 SHALL NOT 执行 registry 中声明的 build/test 命令。

#### Scenario: 已知项目名获取上下文

- **WHEN** 助手以登记项目名调用 `project-context`
- **THEN** 工具返回项目路径、构建类型、项目卡、入口、直接依赖、验证入口、证据位置和可用状态的有界摘要
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

#### Scenario: 输出多仓直接依赖

- **WHEN** registry 中 alpha 声明依赖 beta，且 beta 也是登记项目
- **THEN** `project-context --project alpha` 输出 beta 为 alpha 的声明依赖
- **AND** 工具不递归声称传递依赖真实存在

#### Scenario: 依赖图非法

- **WHEN** dependencies 引用未登记项目、自身、重复项目名或形成循环
- **THEN** registry 解析以输入错误拒绝
- **AND** 不执行任何查询输出

#### Scenario: 验证入口只被展示

- **WHEN** registry 声明 build_command 和 test_command
- **THEN** `project-context` 输出这些命令作为目标项目验证入口
- **AND** 工具不执行命令、不写入项目、不产生外部副作用

#### Scenario: 已验证 commit 与当前 HEAD 一致

- **WHEN** 目标项目是 Git 工作树且 registry 的 verified_commit 等于当前 HEAD
- **THEN** `project-context` 输出 current
- **AND** 该状态只表示验证基线 commit 一致，不表示 dirty worktree 或当前任务已经通过

#### Scenario: 已验证 commit 漂移或不可用

- **WHEN** verified_commit 不等于当前 HEAD、项目未检出或项目不是 Git 工作树
- **THEN** `project-context` 分别输出 drifted 或 unavailable
- **AND** 不得沿用该证据声称当前代码通过

#### Scenario: Git 元数据或间接引用越界

-- **WHEN** 项目 `.git` 符号链接、gitdir 文件、commondir、alternate object store 或 Git 元数据内部 symlink 解析到声明 workspace 外
- **THEN** `project-context` 与 `workspace-search` 在输出结果前以输入错误拒绝
- **AND** 不得读取外部 Git 元数据或输出外部 HEAD

#### Scenario: Git 配置不得引入命令执行

- **WHEN** 项目 Git config 或其 include 声明 fsmonitor、hooks、外部 attributes/excludes 或 pager 等可执行/可扩展配置
- **THEN** 事实工具以安全命令行配置覆盖这些执行路径
- **AND** 查询过程中不得执行 registry/Git config 声明的脚本或产生外部副作用

#### Scenario: 验证声明非法

- **WHEN** verification 命令为空或多行、evidence 是绝对路径、包含 `..`、指向 `.ai` 边界外或文件不存在，或 verified_commit 不是 40/64 位十六进制
- **THEN** registry 解析以输入错误拒绝

## ADDED Requirements

### Requirement: 项目验证证据复用必须可判定且不得削弱新鲜验证

系统 SHALL 提供通用验证证据文档契约，使目标项目能记录验证范围、命令、代码基线、环境类别、执行结果、日志或报告位置、覆盖边界和残余限制。证据 MAY 在代码 commit、相关输入、命令和运行环境等价时复用，用于避免无意义重复执行；但证据 SHALL NOT 成为 OpenSpec 之外的第二任务状态，SHALL NOT 把 NOT_RUN、UNKNOWN、失败或旧环境结果当作通过，也 SHALL NOT 替代当前变更完成前与风险相称的新鲜目标/回归验证。

#### Scenario: 等价输入复用

- **WHEN** 证据记录的 commit、相关输入、命令、环境类别和覆盖范围均与当前请求等价
- **AND** 用户请求仅为确认同一事实而非声明新的代码变更完成
- **THEN** 助手可引用该证据避免重复执行
- **AND** 必须披露证据位置、基线和未覆盖范围

#### Scenario: 代码或输入变化

- **WHEN** 当前项目 HEAD 不等于证据基线、相关输入变化、命令不同或环境类别不匹配
- **THEN** 该证据不可用于声称当前代码通过
- **AND** 助手必须执行与风险相称的新验证

#### Scenario: 证据状态未知

- **WHEN** 证据缺少退出结果、基线、命令、范围或环境身份
- **THEN** 该证据按 UNKNOWN 处理
- **AND** 不得在完成声明中计为通过

#### Scenario: 证据包含敏感内容

- **WHEN** 目标项目记录验证证据
- **THEN** 证据文档只保留脱敏命令、路径、摘要和必要标识
- **AND** 不保存凭据、生产数据、完整敏感日志或私有连接串
