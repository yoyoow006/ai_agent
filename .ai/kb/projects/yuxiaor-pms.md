---
project: yuxiaor-pms
kind: Java Maven multi-module service
primary_domains:
  - 寓小二 PMS
  - 房源与租约业务
related_domains:
  - 对外 API / Feign 契约
  - 风控规则
  - Redis 缓存与分布式锁
last_verified: 2026-09-19
sources:
  - 用户输入（2026-09-19）
  - yuxiaor-pms/README.md
  - yuxiaor-pms/pom.xml
  - yuxiaor-pms/build.sh
  - yuxiaor-pms/build-and-test.sh
  - yuxiaor-pms/yuxiaor-server/src/main/java/com/dream/yuxiaor/YuxiaorServiceApp.java
  - yuxiaor-pms/yuxiaor-server/src/main/java/com/dream/yuxiaor/config/RedissionConfig.java
  - yuxiaor-pms/yuxiaor-schedule/src/main/kotlin/com/yuxiaor/pms/yxrschedule/service/timer/CheckOutServiceTask.kt
---

# yuxiaor-pms 项目卡

## 职责

- 负责：寓小二 PMS 业务核心服务、对外开放 API 与 Feign 契约、风控规则框架执行。
- 不负责：已由 xxl-job 承接的定时任务调度；`yuxiaor-schedule` 仅保留历史模块，不应作为新定时任务的首选入口。

## 技术与运行基线

- 构建运行时：JDK 1.8 + Maven + Spring Boot 2.0.4 + Spring Cloud Finchley.SR1（来源：用户输入，2026-09-19）。
- Maven 主要参数：`-P dev,env-actuator -Denforcer.skip=true`（来源：用户输入；仓库脚本另包含线程数、settings 与 skip-test 参数）。
- Redis 拓扑：测试环境为主从复制，生产环境为 Cluster 集群（来源：用户输入，2026-09-19）。
- Redisson 配置代码区分 Cluster 与非 Cluster 连接，并在当前实现中不支持哨兵模式；环境拓扑不得仅从本地配置文件推断。

## 高频入口

- `yuxiaor-server` → `yuxiaor-pms/yuxiaor-server/src/main/java/com/dream/yuxiaor/YuxiaorServiceApp.java` / `com.dream.yuxiaor.YuxiaorServiceApp` — 业务核心应用启动入口。
- `yuxiaor-api` → `yuxiaor-pms/yuxiaor-api/src/main/java` / `com.yuxiaor.pms.yuxiaorapi.api` — 外部应用 API 与 Feign 契约。
- `yuxiaor-risk-control` → `yuxiaor-pms/yuxiaor-risk-control/src/main/java/com/dream/yuxiaor/risk/EngineService.java` — 风控规则框架入口。
- `yuxiaor-schedule` → `yuxiaor-pms/yuxiaor-schedule/src/main` / `com.yuxiaor.pms.yxrschedule` — 已废弃定时任务历史模块；新调度应走 xxl-job 契约。
- Redis 分布式锁 → `yuxiaor-pms/yuxiaor-server/src/main/java/com/dream/yuxiaor/config/RedissionConfig.java` — Redis Cluster/非 Cluster 连接转换与 Redisson 客户端配置。

## 跨仓库关系

- 上游依赖：
  - Maven 父级与公共依赖来自外部 `com.yuxiaor.pms` artifacts（如 `pms-server-parent`、`pms-apilib`、`pms-testlib`）；当前 registry 未登记这些外部仓库。
- 下游消费者：
  - `yuxiaor-api` 暴露的 API / Feign 契约供外部应用消费；具体消费者未在本次登记中核实。
- 共享契约：
  - 定时任务触发契约已迁移到 xxl-job；`yuxiaor-xxljob` 当前未登记进 registry，本卡仅记录职责边界，不声明 registry 级依赖。

## 搜索锚点

- 业务词：
  - `寓小二 PMS`、`PMS`、`房源`、`租约`。
- 类型 / 注解 / 包名：
  - `com.dream.yuxiaor.YuxiaorServiceApp`
  - `com.yuxiaor.pms.yuxiaorapi.api`
  - `com.dream.yuxiaor.risk`
  - `com.yuxiaor.pms.yxrschedule`
- 特例：
  - `yuxiaor-schedule` 仍包含可启动的 Spring 应用类，但业务调度职责已迁移到 xxl-job；查询现状时优先看 server 中的 xxl-job 触发入口和调度文档。

## 验证入口

- 构建：`cd yuxiaor-pms && mvn -T1C clean validate compile -P dev,env-actuator,nexus-dailybuild -Denforcer.skip=true -am`
- 测试：`cd yuxiaor-pms && mvn -T2C test -P dev,env-actuator,nexus-dailybuild -Denforcer.skip=true`
- 证据：尚未登记 Maven 构建/测试验证证据；上述命令只是人工复核入口。
- 基线：本卡未声明 `verified_commit`，因此 project-context 不提供构建证据漂移状态。

## 证据与维护

- 事实来源：
  - 技术栈、Maven 主要参数、测试/生产 Redis 拓扑：用户输入，2026-09-19。
  - 模块结构：`yuxiaor-pms/pom.xml`。
  - 主类：`YuxiaorServiceApp.java`。
  - xxl-job 迁移：`yuxiaor-schedule` 中多个任务标注 deprecated 并写明迁移到 xxl-job。
  - Redis Cluster 处理：`RedissionConfig.java`。
- 最近复核：
  - 2026-09-19，目标项目事实复核 commit `20bc28727a83ab2c6df2f8afb06555ac3eb61e66`；本次仅做静态事实登记，未执行 Maven 构建或测试。
- 残余不确定：
  - 未验证本地 Maven 构建、测试、测试/生产 Redis 实际连通性与部署拓扑。
  - 外部 Maven 父级仓库、API 消费者和 xxl-job 控制台配置未核实。
