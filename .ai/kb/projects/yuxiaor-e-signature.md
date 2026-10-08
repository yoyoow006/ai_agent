---
project: yuxiaor-e-signature
kind: Java Maven multi-module service
primary_domains:
  - 电子合同签署与盖章
  - 用户实名认证
related_domains:
  - E签宝供应商适配
  - 君子签供应商（已作废）
  - yuxiaor-pms 合同与用户业务
last_verified: 2026-10-08
sources:
  - 用户输入（2026-10-08）
  - yuxiaor-e-signature/README.md
  - yuxiaor-e-signature/pom.xml
  - yuxiaor-e-signature/yuxiaor-e-sign-server/src/main/java/com/yuxiaor/pms/esign/YuxiaorEsignApplication.java

---

# yuxiaor-e-signature 项目卡

## 职责

- 负责：电子合同签署、签署盖章流程、签署详情，以及个人和企业用户实名认证接口。
- 不负责：寓小二 PMS 的房源、租约等核心业务数据管理；这些由 `yuxiaor-pms` 提供。

## 高频入口

- `YuxiaorEsignApplication` → `yuxiaor-e-signature/yuxiaor-e-sign-server/src/main/java/com/yuxiaor/pms/esign/YuxiaorEsignApplication.java` — 电子签名服务启动入口。
- `yuxiaor-e-signature-api` → `yuxiaor-e-signature/yuxiaor-e-signature-api/src/main/java/com/yuxiaor/pms/esign` — 实名、账号和合同签署 DTO/API 契约。

## 跨仓库关系

- 上游依赖：`yuxiaor-pms` 提供 PMS 业务集成和共享 API 依赖。
- 下游消费者：`yuxiaor-pms` 的电子签署、实名和合同流程调用本项目接口。
- 共享契约：`yuxiaor-e-signature-api` 中的 `/sign/*` 签署与实名接口。

## 搜索锚点

- 业务词：`电子合同`、`电子签名`、`合同签署`、`盖章`、`实名认证`、`人脸认证`。
- 类型 / 注解 / 包名：`com.yuxiaor.pms.esign`、`YuxiaorEsignApplication`。
- 特例：`yuxiaor-e-sign-junzi`（君子签）供应商已作废；现存供应商实现分布在 `yuxiaor-e-sign-bo` 和 server 模块，查询具体行为时需按接口契约回溯实现。

## 验证入口

- 构建：`cd yuxiaor-e-signature && mvn -s ../yuxiaor-pms/settings-work.xml validate -P dev,env-actuator -Denforcer.skip=true`
- 测试：`cd yuxiaor-e-signature && mvn -s ../yuxiaor-pms/settings-work.xml test -P dev,env-actuator -Denforcer.skip=true`
- 证据：尚未登记构建/测试验证证据；上述命令只是人工复核入口。

## 证据与维护

- 事实来源：用户输入（君子签供应商已作废，2026-10-08）、项目 README、根 POM、电子签名服务启动类和 API 源码目录。
- 最近复核：2026-10-08，项目 HEAD `6c679be923afb66c13506e4801aca289306249d8`；复核职责、模块、启动类和 API 目录，未执行 Maven 构建或测试。
- 残余不确定：外部供应商服务、部署拓扑和运行时注册中心状态未核实。
