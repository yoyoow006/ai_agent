模式: 严格
状态: 构建中

# 把电子签署业务抽离为 DDD 模块

## Why

`yuxiaor-pms` 中电子签署相关业务当前分散在 `yuxiaor-server` 的 `service/elcsignature`、`helper/esign`、`service/remote/elcsignature`、`service/orgsign`、`service/certification` 等包中。它们同时承担实名、刷脸、PDF 生成、供应商适配、回调、MQ、持久化和合同状态更新，与合同核心、公寓、租客等上下文相互引用，导致修改成本高、测试边界不清。

用户要求将公寓实名、签署主体实名、租客港澳台实名、刷脸认证、电子合同签署盖章抽离到单独模块，并保持 controller、API 与对外 Feign 契约不变。该变更属于大范围运行时重构，且涉及公开契约与跨上下文一致性，因此按严格模式处理。

## What Changes

- 新增 Maven 模块 `yuxiaor-pms/yuxiaor-esign`，作为仍在 `yuxiaor-server` 进程内加载的业务模块，不新增独立部署服务。
- 按 DDD 分层组织电子签署上下文：
  - domain：签署主体、身份认证、刷脸认证、合同签署/意愿签署领域模型与规则；
  - application：实名发起、刷脸发起与回调、签署方式决策、合同签署盖章、拒签、补偿等用例；
  - infrastructure：E签宝/君子签/平安/支付宝等供应商适配、MyBatis仓储、MQ、文件与配置适配；
  - adapter/facade：兼容既有 service FQCN 与 Spring Bean，供现有 controller 和业务调用方使用。
- 将 `yuxiaor-server` 对该上下文的直接依赖改为依赖 `yuxiaor-esign` 暴露的用例接口/兼容接口。
- 对合同、公寓、租客、服务次数等非本上下文数据使用出站端口，由 `yuxiaor-server` 提供适配器，避免 `yuxiaor-esign -> yuxiaor-server` 的 Maven 循环。
- 冻结现有 HTTP 路由、请求/响应类型、异常语义、Feign service name 与方法签名；`yuxiaor-api` 源码不做契约性修改。
- 不修改数据库 Schema、不迁移数据、不更换供应商、不拆独立进程。

## Impact

- 构建影响：根 `pom.xml` 增加 module，`yuxiaor-server` 增加 `yuxiaor-esign` 依赖，构建顺序和增量构建命令需要覆盖两个模块。
- 运行时影响：目标是行为等价迁移；Bean 名称、事务边界、异步线程池、MQ destination、回调验签和幂等行为必须保持兼容。
- 代码组织影响：大量电子签署类移动或改造为兼容门面；`yuxiaor-server` 中非电子签署调用方优先通过既有接口或新用例端口访问。
- 测试影响：现有约80个相关测试作为行为基线，新增/迁移模块级领域测试、仓储契约测试、HTTP/Feign契约快照测试与分层依赖测试。
- 回滚影响：按阶段保持旧实现可回退；完成旧实现删除前必须通过契约与行为基线。

## 范围

### 包含

- 公寓/企业实名认证与实名地址流程。
- 公寓签署主体、企业/个人主体实名、主体驳回/作废等状态流。
- 租客身份证、护照、港澳来往大陆通行证、台湾来往大陆通行证的电子签署账号映射。
- 刷脸认证发起、结果查询、回调、次数与状态处理。
- 电子合同/附加协议/意愿签署 PDF 准备、签署流程、盖章、回调、拒签与状态推进。
- E签宝、君子签、平安、支付宝刷脸等既有渠道的防腐适配。
- 电子签署模块的构建、测试、分层与兼容性验证。

### 不包含

- 拆分为独立部署服务或修改服务发现/网关拓扑。
- 修改数据库表结构、数据回填或历史数据修复。
- 修改 `yuxiaor-api` 对外接口定义、HTTP 路由、字段和 Feign 契约。
- 替换电子签署供应商或改变签署业务规则。
- 抽离全部合同上下文、租客上下文或公寓上下文。
- 修改前端、xxl-job、发布脚本或生产配置。

## 需要确认的方案假设

1. `yuxiaor-esign` 是 `yuxiaor-server` 进程内的 Maven JAR 模块，不是独立 Spring Boot 服务。
2. “controller/API/Feign保持不变”解释为外部契约和行为不变：路由、方法签名、参数、返回、Feign service name 不变；允许现有 controller 或本地 REST 实现内部改为委托模块用例，但不得改变注解映射。
3. 本次只做方案文档，不实施代码；四件套确认后再进入严格模式 Design/独立实现计划。

## 验收口径

- `yuxiaor-esign` 可独立完成编译和模块测试，`yuxiaor-server` 可与其联合构建。
- HTTP/Feign 契约快照与迁移前基线一致。
- DDD 分层依赖测试通过：domain 不依赖 Spring Web/MyBatis/Feign，模块不依赖 `yuxiaor-server`。
- 既有电子签署、实名、刷脸、意愿签署相关测试全绿。
- 无重复业务 Bean、无循环 Maven 依赖、无 Schema/数据变更。
