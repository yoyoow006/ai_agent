模式: 标准
状态: 构建中

# 新增电子轻托租客合同前校验业主实名

## Why

当前 `POST /api/v1/contract/add-contract-fm` 新增租客合同时，若选择电子轻托管三方租客合同，系统不会在保存前校验对应业主实名状态。若业主未实名，合同与账单可能先被创建，直到后续电子盖章流程才发现业主 signer 不可用，造成无效数据和用户返工。

上一变更已在 `/contracts/commonInfo` 返回业主实名状态，并在盖章阶段对白名单公寓个人业主放宽 `AuthBinding`。本变更需要在新增入口持久化前拦截明确失败场景，错误信息为：`请业主实名后，再签约轻托管三方租客合同`。

## What Changes

- 在 `ContractNGServiceImpl.addFmContract` 的合同校验阶段新增验证：
  - 仅当新增租客合同为电子合同、轻托合同（`contractModel>0`）时执行；
  - 电子合同口径使用入参 `ContractFlatmateModel.contractType` 的既有枚举：`ELC_COMPANY=1`、`ELC_FLATMATE=2`；
  - 根据当前房源查询生效业主合同，读取业主 C 端用户；
  - 业主实名口径保持已确认定义：`UserFlatmate.AuthBinding=1 && UserAccount.Truth=1`；
  - 业主未实名时抛出业务异常：`请业主实名后，再签约轻托管三方租客合同`。
- 纸质轻托合同、轻托以外类型的合同不触发该校验。
- 不修改 `/contracts/commonInfo`、盖章白名单放宽逻辑、数据库 Schema、请求参数和响应结构。

## Impact

- 运行时：`add-contract-fm` 新增电子轻托租客合同会在初始化合同/租客与写入合同前快速失败；对应业主已实名时行为不变。
- 一致性：入口校验使用与 commonInfo 相同的实名口径；后续盖章阶段白名单逻辑仍保留，二者作用点不同。
- 性能：仅电子轻托租客合同新增少量业主合同与实名查询。
- 测试：新增单元测试覆盖电子轻托未实名拦截、已实名放行、纸质轻托不校验、电子包租不校验、业主缺失报同一错误。
- 本地整合：业务仓库继续使用 `feature/tenant-light-owner-realname-flex` 任务分支追加一个职责提交；父仓库另建本变更 OpenSpec feature 分支。用户未提交的 `http-client.http`、`work_daily.md` 不触碰。

## 范围

### 包含

- `POST /api/v1/contract/add-contract-fm` 新增电子轻托租客合同的业主实名校验。
- 目标单元测试。

### 不包含

- 修改续约、重置、线上合同消费等其他 `quickSave` 调用入口。
- 修改合同模板、轻托规则、分账、盖章流程。
- 修改前端提示或其他 API 契约。
- 数据库 Schema、迁移和运营配置。

## 验收口径

- 电子轻托 + 业主未实名：在合同初始化/写入前抛出指定文案，不创建合同。
- 电子轻托 + 业主已实名：继续既有保存流程。
- 纸质轻托或电子包租：不执行业主实名拦截。
- 目标测试与生产编译通过。
