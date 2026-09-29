# Delta Specification for project-registration

## ADDED Requirements

### Requirement: 登记电子签署项目

系统 SHALL 在项目 registry 中登记 `yuxiaor-e-signature`，并使其项目事实查询、工作区搜索和业务词路由能进入该项目的权威源码路径，同时保持查询有界且只读。

#### Scenario: 查询电子签署项目上下文

- **WHEN** 执行 `project-context --project yuxiaor-e-signature`
- **THEN** 输出项目路径、Maven 构建、项目卡、`yuxiaor-e-sign-server` 应用入口与验证入口
- **AND** 输出可用状态，不修改项目或执行构建命令

#### Scenario: 按服务名定位启动模块

- **WHEN** 执行 `server-registry --server yuxiaor-e-sign-server`
- **THEN** 唯一返回项目 `yuxiaor-e-signature`、模块 `yuxiaor-e-sign-server`
- **AND** main class 为 `com.yuxiaor.pms.esign.YuxiaorEsignApplication`

#### Scenario: 搜索电子签署权威源码

- **WHEN** 在已检出的 `yuxiaor-e-signature` 项目内搜索 `EsignatureService`
- **THEN** 结果仅来自 registry 声明的搜索根
- **AND** 不扫描未登记路径、被忽略内容或输出凭据

#### Scenario: 按业务词路由渠道知识

- **WHEN** 查询业务词“君子签”
- **THEN** 返回 `yuxiaor-e-signature`、项目卡和君子签相关源码路径
- **AND** 项目卡明确该渠道已废弃，仅保留历史/兼容排查价值

### Requirement: 电子签署项目卡记录模块边界

系统 SHALL 提供电子签署项目卡，记录项目根、启动模块、E签宝渠道、君子签废弃渠道、基础包和对外 API/Feign 模块的职责与权威入口。

#### Scenario: 阅读项目卡定位模块

- **WHEN** 维护者打开电子签署项目卡
- **THEN** 能区分 `yuxiaor-e-sign-server`、`yuxiaor-e-sign-bo`、`yuxiaor-e-sign-junzi`、`yuxiaor-e-sign-base`、`yuxiaor-e-signature-api`
- **AND** 能定位启动类、对外接口与 Feign 契约、渠道路由和持久化基础组件
- **AND** 卡片显式记录未验证的部署、安全和运行环境边界

### Requirement: 路由索引暴露电子签署项目

共享规则索引 SHALL 包含电子签署项目条目，使其可由项目名、业务词和技术符号路由到对应项目卡与源码路径。

#### Scenario: 查找电子签署路由

- **WHEN** 用户询问电子签署、E签宝或君子签相关问题
- **THEN** `.ai/rules/index.md` 的“电子签署服务”条目可路由到 registry、项目卡和项目路径
- **AND** 不把 PMS 项目内的电子签署兼容代码误认为独立服务源码根
