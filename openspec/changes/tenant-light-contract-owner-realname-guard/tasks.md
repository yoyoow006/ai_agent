# Tasks

## 1. TDD 新增前置校验

- [ ] 1.1 核对 `ContractNGServiceImpl.addFmContract` 现有依赖，补齐业主合同、业主资料、C 端用户、账号服务所需最小依赖。
- [ ] 1.2 新增 `ContractNGServiceImplAddFmLightOwnerRealNameTest`，先写失败用例：
  - 电子轻托 + 业主未实名，抛出 `请业主实名后，再签约轻托管三方租客合同`；
  - 电子轻托 + 业主已实名，通过该检查并进入后续既有校验；
  - 纸质轻托不触发；
  - 电子包租不触发；
  - 业主合同/业主用户缺失按未实名处理。
- [ ] 1.3 运行目标测试并确认新增核心用例先失败，失败原因为缺少新校验。
- [ ] 1.4 在 `addFmContract` 合同校验区实现 `checkElectronicLightOwnerRealName(Integer contractType, ContractInfoModel contract, ContractFlatmateDto dto)`：
  - `contractType` 为 `ELC_COMPANY` 或 `ELC_FLATMATE`，且 `contract.getContractModel()>0` 才继续；
  - 复用 `aptContractService.getFlContractIds(houseId, companyId)` 获取生效业主合同；
  - 读取 `AptContract.flId` -> `FirstLandLord.userId`;
  - `UserFlatmate.AuthBinding=1 && UserAccount.Truth=1` 才通过；
  - 否则抛 `businessExceptionFactory.fromMessage("请业主实名后，再签约轻托管三方租客合同")`。
- [ ] 1.5 运行目标测试至全部通过。

## 2. 回归验证与收尾

- [ ] 2.1 使用既有独立 JUnit4 classpath 方式运行：
  `ContractNGServiceImplAddFmLightOwnerRealNameTest`
  预期：新增测试全绿。
- [ ] 2.2 运行生产编译：
  `cd yuxiaor-pms && mvn -o -pl yuxiaor-server -P dev,env-actuator -Denforcer.skip=true -Dmaven.repo.local=/tmp/repoYxr-compatible compile`
- [ ] 2.3 检查业务 diff，确认未修改 `http-client.http`、`work_daily.md`、Schema、外部 API 与前端。
- [ ] 2.4 执行 OpenSpec 校验：
  `openspec validate tenant-light-contract-owner-realname-guard --strict --no-interactive`
- [ ] 2.5 记录验证证据，状态进入待验证。
