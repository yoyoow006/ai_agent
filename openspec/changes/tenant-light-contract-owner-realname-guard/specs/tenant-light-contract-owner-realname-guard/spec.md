## ADDED Requirements

### Requirement: 新增电子轻托租客合同必须校验业主实名并支持公寓白名单豁免

系统 SHALL 在新增租客电子轻托管三方合同前校验对应业主实名状态；非白名单公寓业主未实名时 MUST 阻止合同创建，白名单公寓 SHALL 跳过业主实名校验。

#### Scenario: 电子轻托业主未实名

- WHEN 调用 `POST /api/v1/contract/add-contract-fm` 新增租客合同
- AND 请求 `contractType` 为电子合同类型 `ELC_COMPANY=1` 或 `ELC_FLATMATE=2`
- AND `contractModel>0`
- AND 公寓不在 `LIGHT_OWNER_REAL_NAME_WHITE_LIST`
- AND 对应业主 `AuthBinding!=1` 或 `Truth!=1`
- THEN 抛出业务异常 `请业主实名后，再签约轻托管三方租客合同`
- AND 不写入租客合同或租客信息

#### Scenario: 白名单公寓跳过业主实名校验

- WHEN 新增租客电子轻托管三方合同
- AND 公寓在 `LIGHT_OWNER_REAL_NAME_WHITE_LIST`
- THEN 不查询业主合同、业主资料、C 端用户或实名账号
- AND 继续既有合同保存流程

#### Scenario: 电子轻托业主已实名

- WHEN 新增租客电子轻托管三方合同
- AND 对应业主 `AuthBinding=1` 且 `Truth=1`
- THEN 业主实名校验通过
- AND 继续既有合同保存流程

#### Scenario: 纸质轻托合同不校验

- WHEN 新增租客轻托管三方合同
- AND 合同不是电子合同类型
- THEN 不执行业主实名前置拦截

#### Scenario: 电子包租合同不校验

- WHEN 新增租客电子合同
- AND `contractModel=0` 或未选择轻托模式
- THEN 不执行业主实名前置拦截

#### Scenario: 业主或业主合同缺失

- WHEN 新增租客电子轻托管三方合同
- AND 当前房源不存在生效业主合同，或业主合同缺少可识别的 C 端业主用户
- THEN 抛出同一业务异常 `请业主实名后，再签约轻托管三方租客合同`

### Requirement: 添加合同业主合同摘要必须返回轻托实名白名单标识

`GET /api/v1/contracts/commonInfo` SHALL 在 `ownerContractInfo` 中返回当前公寓是否命中轻托业主实名白名单，且该标识 MUST 与新增合同豁免使用同一配置代码。

#### Scenario: 公寓在白名单

- WHEN 调用 `/api/v1/contracts/commonInfo`
- AND 当前登录公寓在 `LIGHT_OWNER_REAL_NAME_WHITE_LIST`
- THEN `ownerContractInfo.companyInLightOwnerWhiteList=true`
- AND 该标识不依赖是否存在生效业主合同

#### Scenario: 公寓不在白名单

- WHEN 调用 `/api/v1/contracts/commonInfo`
- AND 当前登录公寓不在 `LIGHT_OWNER_REAL_NAME_WHITE_LIST`
- THEN `ownerContractInfo.companyInLightOwnerWhiteList=false`
