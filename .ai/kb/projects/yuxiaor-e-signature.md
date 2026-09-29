---
project: yuxiaor-e-signature
kind: Java Maven multi-module electronic-signature service
primary_domains:
  - 电子签署
  - 实名认证
  - 合同签署与回调
related_domains:
  - E签宝渠道适配
  - 君子签历史渠道
  - 对外 API / Feign 契约
last_verified: 2026-09-29
verified_commit: 6c679be
sources:
  - 用户输入（2026-09-29）
  - yuxiaor-e-signature/pom.xml
  - yuxiaor-e-signature/README.md
  - yuxiaor-e-signature/build.sh
  - yuxiaor-e-signature/build-and-test.sh
  - yuxiaor-e-signature/yuxiaor-e-sign-server/src/main/resources/application.yml
  - yuxiaor-e-signature/yuxiaor-e-sign-server/src/main/java/com/yuxiaor/pms/esign/YuxiaorEsignApplication.java
  - yuxiaor-e-signature/yuxiaor-e-signature-api/src/main/java/com/yuxiaor/pms/esign/api/EsignatureService.java
  - yuxiaor-e-signature/yuxiaor-e-signature-api/src/main/java/com/yuxiaor/pms/esign/api/EsignatureFeignService.java
  - yuxiaor-e-signature/yuxiaor-e-sign-server/src/main/java/com/yuxiaor/pms/esign/service/gw/EsignatureProcessRoute.java
---

# yuxiaor-e-signature 项目卡

## 职责

- 负责：电子签署独立服务的业务编排、渠道路由、实名/刷脸/合同签署流程、签署数据持久化、供应商回调入口和对外 API/Feign 契约。
- 不负责：PMS 合同业务决策、公寓/租客上下文状态推进、供应商计费策略；这些仍由调用方或 PMS 侧决定。

## 技术与运行基线

- 构建运行时：Java + Maven 多模块 Spring 服务，使用根 `pom.xml` 与 `settings-work.xml`（来源：项目 POM 与构建脚本）。
- 服务名：`spring.application.name=yuxiaor-e-sign-server`，默认端口 8500（来源：`yuxiaor-e-sign-server/src/main/resources/application.yml`）。
- 对外 Feign service name：`yuxiaor-e-sign-server`（来源：`EsignatureFeignService`）。
- 当前本地基线：`master@6c679be`。本登记仅复核结构、模块和入口，不声明完整构建/测试验证。

## 模块职责

- `yuxiaor-e-sign-server`：服务启动与业务编排模块；入口 `com.yuxiaor.pms.esign.YuxiaorEsignApplication`，包含 controller、domain service、渠道路由和回调入口。
- `yuxiaor-e-sign-bo`：E签宝渠道适配模块，包含 E签宝 SDK、DTO 转换、异步事件处理和实名/刷脸/签署流程适配。
- `yuxiaor-e-sign-junzi`：君子签渠道模块。用户确认该渠道已废弃；仅为历史数据、兼容问题和回滚排查保留搜索入口，不作为新渠道开发方向。
- `yuxiaor-e-sign-base`：电子签基础包，包含签署账号、认证流、合同流、实体与 MyBatis mapper、Redis/OSS/七牛等基础设施适配。
- `yuxiaor-e-signature-api`：对外 API 与 Feign 契约模块，包含 `EsignatureService`、`EsignatureFeignService`、DTO、枚举和 Feign 启用配置。

## 高频入口

- `YuxiaorEsignApplication` → `yuxiaor-e-sign-server/src/main/java/com/yuxiaor/pms/esign/YuxiaorEsignApplication.java` — 服务启动入口。
- `EsignatureService` → `yuxiaor-e-signature-api/src/main/java/com/yuxiaor/pms/esign/api/EsignatureService.java` — 服务端业务接口。
- `EsignatureFeignService` → `yuxiaor-e-signature-api/src/main/java/com/yuxiaor/pms/esign/api/EsignatureFeignService.java` — 外部应用调用的 Feign 契约。
- `EsignatureController` → `yuxiaor-e-sign-server/src/main/java/com/yuxiaor/pms/esign/controller/EsignatureController.java` — HTTP `/sign/**` 入口。
- `EsignatureCallbackController` → `yuxiaor-e-sign-server/src/main/java/com/yuxiaor/pms/esign/controller/EsignatureCallbackController.java` — 供应商回调入口。
- `EsignatureProcessRoute` → `yuxiaor-e-sign-server/src/main/java/com/yuxiaor/pms/esign/service/gw/EsignatureProcessRoute.java` — 按来源与规则路由电子签渠道。
- `IEsignatureProcess` → `yuxiaor-e-sign-base/src/main/java/com/yuxiaor/pms/esign/base/domain/IEsignatureProcess.java` — E签宝/君子签共同流程接口。

## 跨仓库关系

- 上游依赖：
  - 依赖外部 PMS 公共库、`yuxiaor-api`、基础设施 SDK 和供应商 SDK；除本地登记的 `yuxiaor-pms` 外，其余外部仓库未登记。
- 下游消费者：
  - `yuxiaor-pms` 及其他业务系统可通过 `yuxiaor-e-signature-api` 中的 Feign 契约访问本服务；具体消费者本次未核实。
- 共享契约：
  - `EsignatureService` / `EsignatureFeignService` 定义实名、刷脸、账号、合同签署、回调等跨系统契约。
  - `yuxiaor-pms` 正在抽离进程内电子签署 DDD 模块，与本项目是并存但不同部署边界的实现；不要把 PMS 内兼容门面误认为本服务源码。

## 搜索锚点

- 业务词：电子签署、实名认证、刷脸认证、合同签署、电子签署回调、渠道路由、电子签署账号、E签宝、君子签。
- 类型 / 包名：`com.yuxiaor.pms.esign`、`EsignatureService`、`EsignatureFeignService`、`IEsignatureProcess`。
- 特例：`yuxiaor-e-sign-junzi` 已废弃但仍保留源码；“君子签”命中仅表示历史渠道实现，不代表建议继续使用。

## 验证入口

- 构建：`cd yuxiaor-e-signature && ./build.sh`
- 测试：`cd yuxiaor-e-signature && mvn -s settings-work.xml -T2C test -P dev,env-actuator`
- 证据：尚无完整构建/测试证据基线；registry 未声明 `verified_commit`。
- 基线：frontmatter 的本地复核 commit 仅说明项目结构事实来源，不代表完整验证通过。

## 证据与维护

- 事实来源：用户输入、根 POM、模块 POM、启动类、application.yml、API 接口、README 和构建脚本。
- 最近复核：2026-09-29，`6c679be`；复核范围为项目结构、模块、入口、服务名与契约位置。
- 残余不确定：服务部署拓扑、生产流量、安全配置、外部依赖解析、完整构建/测试结果和消费者清单未验证。
