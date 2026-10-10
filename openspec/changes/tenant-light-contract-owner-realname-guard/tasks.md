# Tasks

## 1. TDD 新增前置校验

- [x] 1.1 核对 `ContractNGServiceImpl.addFmContract` 现有依赖，补齐业主合同、业主资料、C 端用户、账号服务所需最小依赖。
- [x] 1.2 新增 `ContractNGServiceImplAddFmLightOwnerRealNameTest`，先写失败用例：
  - 电子轻托 + 业主未实名，抛出 `请业主实名后，再签约轻托管三方租客合同`；
  - 电子轻托 + 业主已实名，通过该检查并进入后续既有校验；
  - 纸质轻托不触发；
  - 电子包租不触发；
  - 业主合同/业主用户缺失按未实名处理。
- [x] 1.3 运行目标测试并确认新增核心用例先失败，失败原因为缺少新校验。
- [x] 1.4 在 `addFmContract` 合同校验区实现 `checkElectronicLightOwnerRealName(Integer contractType, ContractInfoModel contract, ContractFlatmateDto dto)`：
  - `contractType` 为 `ELC_COMPANY` 或 `ELC_FLATMATE`，且 `contract.getContractModel()>0` 才继续；
  - 复用 `aptContractService.getFlContractIds(houseId, companyId)` 获取生效业主合同；
  - 读取 `AptContract.flId` -> `FirstLandLord.userId`;
  - `UserFlatmate.AuthBinding=1 && UserAccount.Truth=1` 才通过；
  - 否则抛 `businessExceptionFactory.fromMessage("请业主实名后，再签约轻托管三方租客合同")`。
- [x] 1.5 运行目标测试至全部通过。

## 2. 回归验证与收尾

- [x] 2.1 使用既有独立 JUnit4 classpath 方式运行：
  `ContractNGServiceImplAddFmLightOwnerRealNameTest`
  预期：新增测试全绿。
- [x] 2.2 运行生产编译：
  `cd yuxiaor-pms && mvn -o -pl yuxiaor-server -P dev,env-actuator -Denforcer.skip=true -Dmaven.repo.local=/tmp/repoYxr-compatible compile`
- [x] 2.3 检查业务 diff，确认未修改 `http-client.http`、`work_daily.md`、Schema、外部 API 与前端。
- [x] 2.4 执行 OpenSpec 校验：
  `openspec validate tenant-light-contract-owner-realname-guard --strict --no-interactive`
- [x] 2.5 记录验证证据，状态进入待验证。

## 3. 白名单豁免与 commonInfo 白名单标识

- [x] 3.1 将轻托业主实名白名单代码与公司命中判断抽取到共享 helper，避免复制逗号解析逻辑。
- [x] 3.2 先扩展失败测试：
  - `ContractNGServiceImplAddFmLightOwnerRealNameTest`：白名单公寓 + 业主未实名时不查询业主链路并放行；
  - `ContractControllerCommonInfoOwnerTest`：`companyInLightOwnerWhiteList` 命中为 true、未命中为 false，且无业主合同时仍返回该标识。
- [x] 3.3 修改 `ContractNGServiceImpl.checkElectronicLightOwnerRealName`：电子轻托且公寓命中白名单时直接 return。
- [x] 3.4 为 `ContractCommonInfoRes.OwnerContractInfo` 新增 `Boolean companyInLightOwnerWhiteList`，并在 `buildOwnerContractInfo` 中按登录公寓填充。
- [x] 3.5 运行目标测试至全绿。

## 4. 扩展验证与收尾

- [x] 4.1 使用独立 JUnit4 classpath 运行 `ContractNGServiceImplAddFmLightOwnerRealNameTest` 与 `ContractControllerCommonInfoOwnerTest`。
- [x] 4.2 运行 `mvn -o -pl yuxiaor-server -P dev,env-actuator -Denforcer.skip=true -Dmaven.repo.local=/tmp/repoYxr-compatible compile`。
- [x] 4.3 检查业务 diff，确认未修改用户本地文件、Schema、外部 API 与前端。
- [x] 4.4 执行 `openspec validate tenant-light-contract-owner-realname-guard --strict --no-interactive`。
- [x] 4.5 记录验证证据，重新进入待验证。
