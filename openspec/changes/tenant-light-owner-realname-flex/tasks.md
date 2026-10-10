# Tasks

## 1. 白名单判断与轻托业主 signer 放宽

- [x] 1.1 在轻托/合同常量处定义白名单代码（默认 `LIGHT_OWNER_REAL_NAME_WHITE_LIST`，最终以实现时核对命名规范后为准）。
- [x] 1.2 先在 `EsignatureExtHelperContextTest` 增加失败用例：
  - 白名单命中且 `AuthBinding!=1`、`Truth=1` 时成功构建个人业主 signer；
  - 白名单命中但 `Truth!=1` 时仍失败；
  - 白名单未命中且 `AuthBinding!=1` 时失败；
  - 企业业主不读取个人白名单逻辑。
- [x] 1.3 修改 `EsignatureExtHelper` / `EsignatureHelper` 的最小保护方法，注入 `ICommonWhiteService`，实现公司白名单解析与个人业主放宽。
- [x] 1.4 运行：
  `cd yuxiaor-pms && mvn -pl yuxiaor-server -Dtest=EsignatureExtHelperContextTest -DfailIfNoTests=false -P dev,env-actuator -Denforcer.skip=true test`
  预期：新增与既有测试全部通过。

## 2. commonInfo 返回业主合同摘要

- [x] 2.1 新增响应嵌套模型（建议 `ContractCommonInfoRes.OwnerContractInfo` 或同包独立类）：
  `ownerId: Long`、`hasOwnerContract: Boolean`、`ownerContractLight: Boolean`、`ownerRealName: Boolean`。
- [x] 2.2 先为组装逻辑添加失败测试，覆盖：轻托业主合同、非轻托业主合同、无业主合同、实名完整、实名不完整、既有信息仍返回。
- [x] 2.3 在 `ContractController.getContractCommonInfo` 或其委托服务中组装：
  - 复用 `aptContractService.getFlContractIds(houseId, companyId)` 的既有生效合同口径；
  - 读取业主合同 `flId` -> `FirstLandLord.userId`；
  - `AuthBinding` 与 `Truth` 分别来自 `UserFlatmate`、C 端 `UserAccount`；
  - 轻托判断使用 `contractModel > 0`。
- [x] 2.4 运行新增测试及既有相关测试，随后执行：
  `cd yuxiaor-pms && mvn -pl yuxiaor-server -Dtest=EsignatureExtHelperContextTest,<新增测试类> -DfailIfNoTests=false -P dev,env-actuator -Denforcer.skip=true test`

## 3. 验证与收尾

- [x] 3.1 运行生产源码编译：
  `cd yuxiaor-pms && mvn -pl yuxiaor-server -P dev,env-actuator -Denforcer.skip=true compile`
- [x] 3.2 检查全量 diff，确认未修改 `http-client.http`、`work_daily.md`、Schema、迁移和外部 API 模块。
- [x] 3.3 执行 OpenSpec 校验：
  `openspec validate tenant-light-owner-realname-flex --strict --no-interactive`
- [x] 3.4 记录测试、编译、OpenSpec 校验结果并进入待验证。
