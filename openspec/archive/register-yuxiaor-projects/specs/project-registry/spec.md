# 项目 registry 登记

## ADDED Requirements

### Requirement: 三个寓小二项目可被事实工具定位

系统 SHALL 在 registry 中登记 `yuxiaor-pms`、`yuxiaor-e-signature` 和 `yuxiaor-xxljob`，且每项包含实际存在的项目路径、项目卡、搜索根和应用入口。

#### Scenario: 查询项目上下文

- **WHEN** 对任一登记项目执行 `project-context`
- **THEN** 工具返回该项目的职责路由、应用入口和登记路径，且不访问 registry 外路径

### Requirement: 业务词路由到对应项目源码

登记 SHALL 为 PMS 核心业务、电子签署/实名认证和 xxl-job 定时任务声明业务词及实际源码路径。

#### Scenario: 按业务词搜索

- **WHEN** 使用“电子合同”“实名认证”或“定时任务”等业务词执行 `business-terms`
- **THEN** 工具返回对应项目卡和相对源码路径
