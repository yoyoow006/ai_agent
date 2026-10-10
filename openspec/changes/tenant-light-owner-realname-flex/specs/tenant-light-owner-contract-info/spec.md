## ADDED Requirements

### Requirement: 租客轻托个人业主实名绑定白名单放宽

轻托管租客合同 SHALL 按公寓白名单放宽个人业主实名绑定校验，同时 MUST 保留账号真实身份校验。

#### Scenario: 白名单个人业主跳过绑定校验

- WHEN 租客轻托管合同进入 `EsignatureExtHelper.getSignersA`
- AND 业主为个人
- AND 合同公寓在指定轻托业主实名白名单中
- AND 业主 `UserAccount.Truth=1`、姓名与证件号有效
- THEN 不要求 `UserFlatmate.AuthBinding=1`
- AND 继续按既有逻辑获取或创建个人签署账号并返回成功 signer

#### Scenario: 非白名单个人业主保持双条件校验

- WHEN 租客轻托管合同进入 `EsignatureExtHelper.getSignersA`
- AND 业主为个人
- AND 合同公寓不在指定白名单中
- AND `AuthBinding` 不为 1 或 `Truth` 不为 1
- THEN 返回既有“业主未实名认证”错误
- AND 不进入签署发送流程

#### Scenario: 企业业主规则保持不变

- WHEN 租客轻托管合同进入 `EsignatureExtHelper.getSignersA`
- AND 业主为企业
- THEN 继续使用既有企业签署主体实名判断，不应用个人白名单放宽逻辑

### Requirement: 添加合同基本信息返回业主合同摘要

`GET /api/v1/contracts/commonInfo` SHALL 返回当前房源的业主合同摘要，且 MUST NOT 改变既有基本信息与价格信息。

#### Scenario: 存在生效轻托业主合同

- WHEN 调用 `/api/v1/contracts/commonInfo`
- AND 房源存在生效业主合同
- THEN 返回 `ownerContractInfo.ownerId` 为该业主合同业主 ID
- AND `hasOwnerContract=true`
- AND 当业主合同 `contractModel>0` 时 `ownerContractLight=true`
- AND 业主 `AuthBinding=1` 且 `Truth=1` 时 `ownerRealName=true`

#### Scenario: 生效业主合同不是轻托

- WHEN 调用 `/api/v1/contracts/commonInfo`
- AND 生效业主合同 `contractModel=0`
- THEN `hasOwnerContract=true`
- AND `ownerContractLight=false`

#### Scenario: 不存在生效业主合同

- WHEN 调用 `/api/v1/contracts/commonInfo`
- AND 房源不存在生效业主合同
- THEN `hasOwnerContract=false`
- AND `ownerId`、`ownerRealName`、`ownerContractLight` 为 null

#### Scenario: 业主实名不完整

- WHEN 生效业主合同存在
- AND 业主 `AuthBinding!=1` 或 `UserAccount.Truth!=1`
- THEN `ownerRealName=false`

#### Scenario: 既有基本信息保持不变

- WHEN 调用 `/api/v1/contracts/commonInfo`
- THEN 响应仍包含既有 `houseBasicInfo` 与 `rentPriceHouse`
- AND 请求参数、路由和既有字段语义不变
