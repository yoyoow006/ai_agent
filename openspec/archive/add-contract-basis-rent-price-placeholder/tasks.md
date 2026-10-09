# 任务清单

- [x] 1. 建立独立实现分支与失败测试
  - [x] 1.1 在嵌套仓库执行`git -C yuxiaor-pms checkout -b feature/contract-basis-rent-price-placeholder`，确认基线为当前`master`且工作区干净。
  - [x] 1.2 新增`yuxiaor-pms/yuxiaor-server/src/test/java/com/dream/yuxiaor/helper/template/ContractBasisRentPriceHelperTest.java`，先覆盖固定月租、按面积月租、两位小数、模式字段缺失、当前模式金额为空等格式化场景。
  - [x] 1.3 新增`yuxiaor-pms/yuxiaor-server/src/test/java/com/dream/yuxiaor/service/impl/ContractBasisRentPricePlaceholderTest.java`，先覆盖中文占位符映射/转换、模板模型渲染、按`houseId+roomId`读取定价、缺失定价为空，以及SQL迁移只追加一次。
  - [x] 1.4 运行`cd yuxiaor-pms && mvn -s settings-work.xml -pl yuxiaor-server test -P dev,env-actuator -Denforcer.skip=true -Dtest='ContractBasisRentPriceHelperTest,ContractBasisRentPricePlaceholderTest'`，确认新测试按预期失败。

- [x] 2. 实现基准租金格式化与模板模型集成
  - [x] 2.1 新增`yuxiaor-pms/yuxiaor-server/src/main/java/com/dream/yuxiaor/helper/template/ContractBasisRentPriceHelper.java`，实现`pricingMode=2 -> basisAreaPrice / 其他 -> basisPrice`、两位小数和人民币大写格式。
  - [x] 2.2 在`ContractTemplateHolder.templateKeyMap`追加`房源基准租金定价 -> basisRentPrice`。
  - [x] 2.3 在`AptContractServiceImpl.CTModel`追加`basisRentPrice`字段，并新增可测试填充方法：按合同`houseId+roomId`调用既有`IRentPriceService#getRentPriceByResourceId`后格式化写入模型。
  - [x] 2.4 在`genCTModel`押金数据组装附近调用新填充方法，保持既有租金、押金和租金单价逻辑不变。
  - [x] 2.5 在默认中文租客模板和默认业主模板的押金金额行后追加`房源基准租金定价：{房源基准租金定价}`行；不改英文模板和历史模板。

- [x] 3. 添加模板变量配置迁移
  - [x] 3.1 新增`yuxiaor-pms/yuxiaor-server/src/main/sql/v1/V1_0_478_contract_template_basis_rent_price.sql`。
  - [x] 3.2 SQL仅对`contractTemplateParams1/2/5/6`、`status=1`且尚未包含新占位符的行执行`CONCAT_WS`追加，并更新`updateTime`。

- [x] 4. 验证与质量检查
  - [x] 4.1 运行`cd yuxiaor-pms && mvn -s settings-work.xml -pl yuxiaor-server test -P dev,env-actuator -Denforcer.skip=true -Dtest='ContractBasisRentPriceHelperTest,ContractBasisRentPricePlaceholderTest,ContractRentUnitPriceHelperTest,ContractRightAddressPlaceholderTest'`，预期全部通过。
  - [x] 4.2 运行`cd yuxiaor-pms && mvn -s settings-work.xml -pl yuxiaor-server test-compile -P dev,env-actuator -Denforcer.skip=true`，预期`BUILD SUCCESS`。
  - [x] 4.3 运行`git -C yuxiaor-pms diff --check`并检查完整diff，确认无根仓库业务文件混入。
  - [x] 4.4 记录测试输出与残余风险，按标准模式进入综合Verify。

## 本地整合策略

- 实施仅修改嵌套仓库`yuxiaor-pms`，独立feature分支可整体回滚。
- 根仓库只保留OpenSpec状态文件；`http-client.http`和`work_daily.md`为用户已有修改，不得触碰。
- 默认不提交、不推送；用户明确要求提交时按“测试/实现/迁移”可回滚职责单元提交。

## 验证证据

- 2026-10-09 红阶段：新增2个测试类共12个测试；scoped `javac` 输出14个 `cannot find symbol`，均指向缺失的 `ContractBasisRentPriceHelper`、`CTModel.basisRentPrice` 与 `fillBasisRentPrice`。
- 2026-10-09 生产编译：`mvn -s settings-work.xml -Dmaven.repo.local=/tmp/repoYxr-contract-placeholder -o -pl yuxiaor-server compile -P dev,env-actuator -Denforcer.skip=true`，`BUILD SUCCESS`。
- 2026-10-09 目标与相关回归：JUnit 4 直跑4个测试类，`OK (22 tests)`。
- 2026-10-09 Verify修复：英文模板范围泄漏先以新增断言复现失败，再删除英文模板占位符；修复后4类合同测试再次 `OK (22 tests)`。
- 2026-10-09 Maven目标测试尝试：生产compile通过后，`testCompile` 被4个无关既有测试的当前 JUnit4/Mockito2 兼容基线阻断（已由活跃变更 `adapt-pms-tests-junit4-mockito2` 记录），不属于本变更范围。
- 2026-10-09 diff检查：`git diff --check` 通过；仅本分支6个目标文件变化。

## 最终审查证据

- 最终 manifest ID: `3a4baf43d00ff3f23a77a402f7289e2d2ab5a02271717881c522b410b2f9f35d`
- comparison base:
  - 根仓库: `37121a3fb86f7d7a78ba893a80ad2a5c5a631139`
  - `yuxiaor-pms`: `7f74dd1fc15a048d629eb9dc4421ce15902e1422`
- finding 状态: resolved=1（英文模板范围泄漏）; accepted-risk=2（用户文件既有 whitespace、全量 testCompile 被无关活跃基线阻断）
- 未验证范围: yuxiaor-server 全量 Surefire 测试；用户自有 `http-client.http` / `work_daily.md`；SQL 迁移未连库执行。
- 残余风险: 全量测试阻塞待 `adapt-pms-tests-junit4-mockito2` 完成；用户未提交文件保持原样；SQL 幂等性仅静态断言。
