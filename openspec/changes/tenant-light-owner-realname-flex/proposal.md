模式: 标准
状态: 待归档

# 租客轻托合同业主实名判断与基本信息扩展

## Why

租客轻托管合同盖章时，个人业主 signer 复用 `EsignatureHelper.loadPersonSignersC(FlatmateDTO)`，当前同时要求 `UserFlatmate.AuthBinding=1` 与 `UserAccount.Truth=1`。部分白名单公寓的业主已有人工确认的实名资料，但尚未完成 C 端账号绑定，导致盖章流程被“业主未实名认证”阻断。

添加合同页的 `/api/v1/contracts/commonInfo` 目前只返回房源基础信息与价格信息，前端无法在新建租客轻托合同前判断当前房源对应业主合同、轻托状态与业主实名状态。

## What Changes

- 新增轻托业主实名白名单代码常量，使用既有 `t_common_white.companyIds` 白名单配置和 `ICommonWhiteService.getCompanyIdsByCode` 30 分钟缓存。
- `EsignatureExtHelper.getSignersA` 中仅放宽个人业主：
  - 公寓在白名单时，忽略 `UserFlatmate.AuthBinding`，但仍要求 `UserAccount.Truth=1` 及既有姓名、证件号有效条件；
  - 公寓不在白名单时保持现有双条件判断；
  - 企业业主实名判断不变。
- `GET /api/v1/contracts/commonInfo` 返回新增 `ownerContractInfo`：
  - `ownerId`：当前房源生效业主合同的 `FirstLandLord.id`；
  - `hasOwnerContract`：是否存在生效业主合同；
  - `ownerContractLight`：该业主合同是否轻托管；
  - `ownerRealName`：业主 C 端 `AuthBinding=1` 且 `UserAccount.Truth=1`。
- 为白名单判断、盖章 signer 构建和 commonInfo 业主信息组装增加单元测试；不改数据库 Schema、路由、请求参数和既有响应字段。

## Impact

- 运行时：白名单公寓个人业主可以继续盖章，但账号真实身份仍必须满足 `Truth=1`，避免完全绕过实名资料校验；企业业主不受影响。
- API：`ContractCommonInfoRes` 新增可空嵌套对象，不破坏既有消费者；没有业主合同时返回 `hasOwnerContract=false`，其余字段为 null。
- 数据/配置：需要运营在通用白名单中维护指定代码和公司 ID 列表；白名单生效受既有 30 分钟缓存影响。
- 测试：补充白名单命中/未命中、AuthBinding 与 Truth 组合、存在/不存在业主合同、轻托/非轻托业主合同场景。
- 本地整合：当前工作区已有未提交 `http-client.http`、`work_daily.md`，本变更不触碰它们；默认在当前分支直接实现，不额外创建 worktree。

## 范围

### 包含

- 租客轻托管盖章流程的个人业主实名绑定条件放宽。
- `/api/v1/contracts/commonInfo` 返回业主合同摘要。
- 相关单元测试。

### 不包含

- 修改企业业主实名规则。
- 修改合同创建、轻托关联重建、支付分账规则。
- 修改数据库 Schema、迁移数据或运营后台白名单管理界面。
- 修改前端页面与外部 API 模块。
