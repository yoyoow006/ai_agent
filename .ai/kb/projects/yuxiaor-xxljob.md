---
project: yuxiaor-xxljob
kind: Kotlin/Java Maven Spring Boot scheduled service
primary_domains:
  - 寓小二 xxl-job 定时任务
related_domains:
  - PMS API/Feign 调用
  - 任务执行器与调度中心
last_verified: 2026-10-08
sources:
  - 用户输入（2026-10-08）
  - yuxiaor-xxljob/pom.xml
  - yuxiaor-xxljob/src/main/java/com/yuxiaor/pms/yxrxxljob/YuxiaorXxlJobApp.java
  - yuxiaor-xxljob/src/main/java/com/yuxiaor/pms/yxrxxljob/XxlJobConfig.java

---

# yuxiaor-xxljob 项目卡

## 职责

- 负责：寓小二 xxl-job 定时任务入口、任务执行器配置和定时业务任务。
- 不负责：PMS 核心 HTTP 服务；核心业务接口由 `yuxiaor-pms` 提供。

## 高频入口

- `YuxiaorXxlJobApp` → `yuxiaor-xxljob/src/main/java/com/yuxiaor/pms/yxrxxljob/YuxiaorXxlJobApp.java` — xxl-job 定时任务服务启动入口。
- `XxlJobConfig` → `yuxiaor-xxljob/src/main/java/com/yuxiaor/pms/yxrxxljob/XxlJobConfig.java` — xxl-job admin、executor 和日志配置入口。
- `service/timer` → `yuxiaor-xxljob/src/main/kotlin/com/yuxiaor/pms/yxrxxljob/service/timer` — 定时任务实现目录。

## 跨仓库关系

- 上游依赖：`yuxiaor-pms` 提供 API/Feign 契约和业务服务调用目标。
- 下游消费者：xxl-job 调度中心触发本项目的任务执行器。
- 共享契约：`xxl.job.*` executor 配置和任务处理方法。

## 搜索锚点

- 业务词：`定时任务`、`xxl-job`、`调度任务`、`任务执行器`。
- 类型 / 注解 / 包名：`com.yuxiaor.pms.yxrxxljob`、`XxlJobSpringExecutor`、`YuxiaorXxlJobApp`。
- 特例：`yuxiaor-pms/yuxiaor-schedule` 是历史调度模块；新任务入口以本项目为准。

## 验证入口

- 构建：`cd yuxiaor-xxljob && mvn -s ../yuxiaor-pms/settings-work.xml validate -P dev,env-actuator -Denforcer.skip=true`
- 测试：`cd yuxiaor-xxljob && mvn -s ../yuxiaor-pms/settings-work.xml test -P dev,env-actuator -Denforcer.skip=true`
- 证据：尚未登记构建/测试验证证据；上述命令只是人工复核入口。

## 证据与维护

- 事实来源：用户输入、根 POM、启动类、xxl-job 配置类和定时任务源码目录。
- 最近复核：2026-10-08，项目 HEAD `a8dd841000d16a734ef8f19df06fade59a3d1f29`；复核启动入口、执行器配置和任务目录，未执行 Maven 构建或测试。
- 残余不确定：xxl-job admin 地址、生产调度配置和任务运行状态未核实。
