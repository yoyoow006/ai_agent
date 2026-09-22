# 任务清单

- [ ] 1. 迁移 MultiHouseSnapshotServiceTest 到 JUnit 4
  - [ ] 1.1 修改 `.worktrees/extract-esign-ddd-module/yuxiaor-server/src/test/java/com/dream/yuxiaor/service/contract/multihouse/service/MultiHouseSnapshotServiceTest.java`。
  - [ ] 1.2 imports：删除 `org.junit.jupiter.api.*`、`org.junit.jupiter.api.extension.ExtendWith`、`org.mockito.junit.jupiter.MockitoExtension`；新增 JUnit 4 `Before/Test/RunWith` 与 `MockitoJUnitRunner`。
  - [ ] 1.3 类注解：`@ExtendWith(MockitoExtension.class)` → `@RunWith(MockitoJUnitRunner.class)`；`@BeforeEach` → `@Before`。
  - [ ] 1.4 assertions：`org.junit.jupiter.api.Assertions` → `org.junit.Assert`；所有测试方法改为 `public void`。
  - [ ] 1.5 保持 helper 构造、mock、stub、BigDecimal 期望和所有断言不变。
- [ ] 2. 替换两个 Mockito 3 no-interaction API
  - [ ] 2.1 修改 `CustomerServiceImplDataMaskingTest.java`：import 与唯一调用 `verifyNoInteractions(postService)` 改为 `verifyZeroInteractions(postService)`。
  - [ ] 2.2 修改 `YuxiaorPaymentServiceImpl2PaymentInfoTest.java`：import 与唯一调用 `verifyNoInteractions(flexibleRentService)` 改为 `verifyZeroInteractions(flexibleRentService)`。
  - [ ] 2.3 不修改 `SmartDeviceVisibilityResolverTest.java`；验收扫描需排除注释。
- [ ] 3. 编译与测试验证
  - [ ] 3.1 在目标 worktree 运行：`mvn -s settings-work.xml -pl yuxiaor-server test-compile -P dev,env-actuator -Denforcer.skip=true`，预期 `BUILD SUCCESS`。
  - [ ] 3.2 运行3个被修改测试：`mvn -s settings-work.xml -pl yuxiaor-server test -P dev,env-actuator -Denforcer.skip=true -Dtest='MultiHouseSnapshotServiceTest,CustomerServiceImplDataMaskingTest,YuxiaorPaymentServiceImpl2PaymentInfoTest'`，记录测试统计；若失败，不修改断言，先按失败证据定位是否为既有基线失败。
  - [ ] 3.3 运行电子签署契约测试：`mvn -s settings-work.xml -pl yuxiaor-server test -P dev,env-actuator -Denforcer.skip=true -Dtest=EsignHttpFeignContractBaselineTest`，预期 `BUILD SUCCESS`。
  - [ ] 3.4 运行原电子签署相关测试基线命令：`mvn -s settings-work.xml -pl yuxiaor-server test -P dev,env-actuator -Denforcer.skip=true -Dtest='*Esign*,*WillingSign*,*Face*,*Flatmate*,*Subsidiary*,*Certification*'`，把真实 Surefire 统计和失败/跳过清单更新到 `yuxiaor-server/src/test/resources/esign-baseline/existing-test-baseline.md`。
  - [ ] 3.5 校验非注释源码无 `org.junit.jupiter`、`MockitoExtension`、未注释 `verifyNoInteractions`；确认生产源码无 diff。
- [ ] 4. 状态与证据回写
  - [ ] 4.1 更新 `openspec/changes/extract-esign-ddd-module/tasks.md` 中 1.5 的当前状态：若 Surefire 统计已记录，则勾选1.5。
  - [ ] 4.2 更新 `openspec/changes/extract-esign-ddd-module/review-findings.md` 中 `unrelated-test-dependency-mismatch` 状态和验证证据。
  - [ ] 4.3 目标仓库按一个独立提交提交3个测试文件与基线文档；根仓库按一个提交提交 OpenSpec 状态。

## 本地整合策略

- 在既有 `.worktrees/extract-esign-ddd-module` 上实施，不创建新 worktree。
- 本变更与电子签署 DDD 分支共享任务分支，但目标仓库提交独立，只包含3个测试文件和 `existing-test-baseline.md`。
- 不提交本地 Maven 缓存或外部项目构建产物。
- 若 Surefire 暴露新的既有失败，只记录，不顺手修复。
