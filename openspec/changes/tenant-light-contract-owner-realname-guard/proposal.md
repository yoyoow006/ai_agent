模式: 标准
状态: 构建中

# 新增电子轻托租客合同业主实名校验与白名单豁免

## Why

当前 `POST /api/v1/contract/add-contract-fm` 新增租客合同时，若选择电子轻托管三方租客合同，系统不会在保存前校验对应业主实名状态。若业主未实名，合同与账单可能先被创建，直到后续电子盖章流程才发现业主 signer 不可用，造成无效数据和用户返工。

第一轮实现已在新增入口拦截业主未实名场景。用户随后确认新增白名单豁免：白名单公寓新增租客轻托管合同时不执行业主实名验证；同时 `/contracts/commonInfo` 的业主合同摘要需要返回公寓是否在轻托业主实名白名单中的标识。

## What Changes

- 在 `ContractNGServiceImpl.addFmContract` 的合同校验阶段新增验证：
  - 仅当新增租客合同为电子合同、轻托合同（`contractModel>0`）时执行；
  - 电子合同口径使用入参 `ContractFlatmateModel.contractType` 的既有枚举：`ELC_COMPANY=1`、`ELC_FLATMATE=2`；
  - 根据当前房源查询生效业主合同，读取业主 C 端用户；
  - 业主实名口径保持已确认定义：`UserFlatmate.AuthBinding=1 && UserAccount.Truth=1`；
  - 若公寓命中 `LIGHT_OWNER_REAL_NAME_WHITE_LIST`，直接跳过业主实名校验；
  - 非白名单公寓业主未实名时抛出业务异常：`请业主实名后，再签约轻托管三方租客合同`。
- 纸质轻托合同、轻托以外类型的合同不触发该校验。
- `/contracts/commonInfo` 的 `ownerContractInfo` 新增 `companyInLightOwnerWhiteList`：
  - 表示当前登录公寓是否命中同一白名单；
  - 不依赖是否存在业主合同，始终返回 true/false。
- 不修改盖章白名单放宽逻辑、数据库 Schema、请求参数和既有响应字段。

## Impact

- 运行时：`add-contract-fm` 新增电子轻托租客合同时，白名单公寓直接放行；非白名单公寓在业主未实名时快速失败。
- 一致性：新增校验、commonInfo 白名单标识、盖章阶段白名单均读取同一 `LIGHT_OWNER_REAL_NAME_WHITE_LIST` 配置。
- 性能：非白名单电子轻托合同新增少量业主合同与实名查询；commonInfo 新增一次白名单缓存读取。
- 测试：在既有测试上扩展白名单放行、非白名单拦截；commonInfo 测试覆盖白名单命中与未命中。
- 本地整合：业务仓库继续使用 `feature/tenant-light-owner-realname-flex` 任务分支追加一个职责提交；父仓库另建本变更 OpenSpec feature 分支。用户未提交的 `http-client.http`、`work_daily.md` 不触碰。

## 范围

### 包含

- `POST /api/v1/contract/add-contract-fm` 新增电子轻托租客合同的业主实名校验与白名单豁免。
- `/contracts/commonInfo` 业主合同摘要中的白名单标识。
- 目标单元测试。

### 不包含

- 修改续约、重置、线上合同消费等其他 `quickSave` 调用入口。
- 修改合同模板、轻托规则、分账、盖章流程。
- 修改前端提示或其他 API 契约。
- 数据库 Schema、迁移和运营配置。

## 验收口径

- 电子轻托 + 白名单公寓：不执行业主实名查询，直接继续既有保存流程。
- 电子轻托 + 非白名单公寓 + 业主未实名：在合同初始化/写入前抛出指定文案，不创建合同。
- 电子轻托 + 非白名单公寓 + 业主已实名：继续既有保存流程。
- 纸质轻托或电子包租：不执行业主实名拦截。
- `commonInfo.ownerContractInfo.companyInLightOwnerWhiteList` 正确返回当前公寓白名单命中状态。
- 目标测试与生产编译通过。
