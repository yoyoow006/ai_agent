模式: 标准
状态: 构建中

# 将4个无关 PMS 测试恢复为当前 JUnit 4 / Mockito 2.15 兼容基线

## Why

`yuxiaor-pms@fb6b634b7a` 的电子签署 DDD 抽离基线在恢复外部 API 后，已能完成生产源码 `compile`，但 `yuxiaor-server` 全量 `testCompile` 在 Surefire 之前失败。根因是既有测试源码使用了 JUnit 5 / Mockito 3+ API，而当前测试依赖实际解析为 `junit:junit:4.12` 与 `org.mockito:mockito-core:2.15.0`。该失败与电子签署生产代码无关，但阻止任何测试统计产出。

用户明确要求先处理这4个无关测试，并把它们改为当前 JUnit 4 / Mockito 2.15 写法；不新增依赖、不修改生产代码。

## What Changes

- 将 `MultiHouseSnapshotServiceTest` 从 JUnit 5 `@ExtendWith(MockitoExtension.class)` 迁移到 JUnit 4 `@RunWith(MockitoJUnitRunner.class)`：
  - `@BeforeEach` → `@Before`;
  - JUnit 5 assertions → JUnit 4 assertions;
  - 方法补充 `public` 修饰符；
  - 保持测试数据、stub、断言和验证不变。
- 将 `CustomerServiceImplDataMaskingTest` 和 `YuxiaorPaymentServiceImpl2PaymentInfoTest` 中 Mockito 3 的 `verifyNoInteractions(...)` 替换为 Mockito 2 兼容且语义等价的 `verifyZeroInteractions(...)`。
- `SmartDeviceVisibilityResolverTest` 已经是 JUnit 4 / Mockito 2 兼容代码，仅其注释包含 `verifyNoInteractions` 字符串；不修改该文件，改为验收扫描排除注释影响。
- 不修改 POM、生产源码、测试数据、断言期望或电子签署行为。

## Impact

- 构建：`yuxiaor-server` 的 `testCompile` 应通过既有 JUnit 4 / Mockito 2.15 classpath。
- 测试：4个被报告文件不再构成编译阻塞；其中3个真实修改文件的测试语义保持不变。
- 电子签署任务：解除任务 1.5 的当前测试编译阻塞，使原命令可以进入 Surefire 并记录真实测试结果。
- 风险：`verifyZeroInteractions` 在后续 Mockito 升级后可能 deprecate，但当前目标就是兼容 2.15；未来升级需另行处理。

## 范围

### 包含

- 目标仓库 `.worktrees/extract-esign-ddd-module` 中3个测试源文件的框架 API 适配。
- 重新运行契约基线测试和既有相关测试基线命令。

### 不包含

- 新增 JUnit 5 或 Mockito 依赖。
- 升级测试框架或 Maven 插件。
- 修改生产代码、POM、API 契约、数据库、配置或电子签署业务。
- 修复后续 Surefire 阶段暴露的其他既有测试失败。
