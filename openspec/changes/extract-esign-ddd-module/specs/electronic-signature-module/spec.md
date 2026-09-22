# 电子签署模块规范（Delta）

## ADDED Requirements

### Requirement: 电子签署上下文必须成为独立 Maven 模块

系统 SHALL 新增 `yuxiaor-esign` Maven 模块承载电子签署限界上下文，并保持 `yuxiaor-server -> yuxiaor-esign` 的单向依赖；`yuxiaor-esign` SHALL NOT 依赖 `yuxiaor-server`。

#### Scenario: 构建新增电子签署模块

- **WHEN** 根项目执行聚合构建
- **THEN** `yuxiaor-esign` 与 `yuxiaor-server` 均被纳入 Reactor
- **AND** `yuxiaor-server` 编译 classpath 包含 `yuxiaor-esign`
- **AND** Maven 依赖图不存在两个模块之间的循环

#### Scenario: 模块被现有启动类加载

- **WHEN** `com.dream.yuxiaor.YuxiaorServiceApp` 启动
- **THEN** `com.dream.yuxiaor` 前缀下的电子签署 Bean 被组件扫描加载
- **AND** 不需要新增独立服务地址、端口或网关路由

### Requirement: 对外 HTTP、API 与 Feign 契约必须保持不变

系统 SHALL 保持既有 controller 路由、HTTP 方法、路径参数、请求/响应类型、Feign 接口、Feign service name 和方法签名不变；`yuxiaor-api` 中的对外契约定义 SHALL NOT 发生契约性修改。

#### Scenario: 迁移后比对契约快照

- **WHEN** 运行 HTTP/Feign 契约快照测试
- **THEN** `/api/v1/certification`、`/api/elcsign/**`、`/api/v1/contract-willing-sign/**`、`/local/company/auth/**`、`/local/faceAuth/**`、`/local/renterFaceSign/**`、`/local/contractSignMethod/**`、`/local/company-subsidiary/**`、`/local/flatmate-realname-auth/**` 的映射与迁移前一致
- **AND** Feign client 的目标服务仍为 `yuxiaor-server`
- **AND** 契约快照测试不因实现类移动而失败

#### Scenario: controller 只能委托用例

- **WHEN** 电子签署 controller 或本地 REST 实现需要调用抽离后的业务
- **THEN** 它仅保留参数校验、认证上下文读取、契约适配和用例调用
- **AND** 它不得改变既有 `@RequestMapping`、HTTP 方法、参数注解和返回类型

### Requirement: DDD 分层必须隔离业务规则与技术实现

`yuxiaor-esign` SHALL 按 domain、application、infrastructure、adapter/facade 分层；domain 层 SHALL NOT 依赖 Spring Web、MyBatis、Feign、Redis、MQ或供应商 SDK；application 层 SHALL 只通过出站端口访问外部上下文。

#### Scenario: 检查分层依赖

- **WHEN** 运行模块分层依赖测试
- **THEN** domain 包没有 Spring、MyBatis、Feign、Redis、MQ或供应商技术导入
- **AND** application 包只导入自身分层、领域模型和出站端口
- **AND** 供应商、数据库、Redis、MQ和文件系统实现位于 infrastructure

#### Scenario: 跨上下文数据访问

- **WHEN** 用例需要合同、公寓、租客、服务次数或用户资料
- **THEN** application 通过出站端口读取或更新
- **AND** `yuxiaor-server` 提供端口实现
- **AND** `yuxiaor-esign` 不直接导入 `yuxiaor-server` 的 service、mapper 或 entity

### Requirement: 实名与签署主体用例必须统一编排

系统 SHALL 在电子签署上下文中统一编排公寓实名、签署主体实名、企业/个人签署账号、租客港澳台证件映射与实名回调；证件类型映射和状态推进 SHALL 保持迁移前行为。

#### Scenario: 租客使用港澳台证件创建电子签署账号

- **WHEN** 租客证件类型为港澳来往大陆通行证或台湾来往大陆通行证
- **THEN** 领域规则按既有逻辑识别香港、澳门或台湾证件类型
- **AND** 供应商请求中的证件类型与迁移前一致

#### Scenario: 公寓实名或签署主体实名回调

- **WHEN** 供应商实名/企业授权回调到达
- **THEN** 系统按既有验签规则校验请求
- **AND** 回调处理保持幂等和异步执行语义
- **AND** 主体状态、电子签署账号和后续事件的推进顺序与迁移前一致

### Requirement: 刷脸认证用例必须保留幂等和限额行为

系统 SHALL 将刷脸认证发起、结果查询、回调、状态存储和服务次数处理放入电子签署上下文，并保留 flowId 幂等、成功后扣减、失败不扣减和异常兼容行为。

#### Scenario: 刷脸认证成功回调

- **WHEN** 同一 flowId 的成功回调重复到达
- **THEN** 系统不重复推进业务状态
- **AND** 不重复扣减公寓刷脸服务次数

#### Scenario: 刷脸认证失败或未完成

- **WHEN** 刷脸结果为失败、取消或未完成
- **THEN** 系统仅记录失败状态和原因
- **AND** 不触发成功签署状态推进

### Requirement: 合同签署盖章用例必须保留状态机与内容一致性

系统 SHALL 在电子签署上下文中编排 PDF 准备、签署方式决策、意愿签署、电子签章、回调、拒签和状态查询；合同内容版本、flowId 归属、状态机和事务/异步边界 SHALL 与迁移前等价。

#### Scenario: 发起租客意愿签署

- **WHEN** 同一合同、文件类型和内容版本重复发起意愿签署
- **THEN** 系统复用或按既有规则恢复流程
- **AND** flowId 不跨越内容版本
- **AND** 返回给调用方的状态语义不变

#### Scenario: 电子合同签署盖章回调

- **WHEN** 供应商合同签署完成回调到达
- **THEN** 系统验签后按既有策略选择合同类型对应处理器
- **AND** 签署文件、合同状态和后续事件的更新保持原有顺序
- **AND** 重复回调不会产生重复副作用

### Requirement: 兼容迁移必须可验证且可回滚

系统 SHALL 在迁移期间提供兼容门面或端口，避免重复 Bean 和双写；在旧实现删除前 SHALL 保留可回滚的阶段边界，并通过契约与行为测试验证每一阶段。

#### Scenario: 兼容门面接入

- **WHEN** `yuxiaor-server` 既有调用方仍使用电子签署旧接口或旧 FQCN
- **THEN** 兼容门面委托新的 application 用例
- **AND** Spring 容器中同一业务契约只有一个主实现
- **AND** 调用方无需感知模块迁移

#### Scenario: 阶段回滚

- **WHEN** 某迁移阶段验证失败
- **THEN** 该阶段提交可独立回滚
- **AND** 已冻结的 HTTP/Feign 契约和数据 Schema 不需要随回滚变更
