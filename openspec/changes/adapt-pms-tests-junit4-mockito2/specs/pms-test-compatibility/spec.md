# PMS 测试框架兼容规范（Delta）

## ADDED Requirements

### Requirement: 既有测试必须使用当前解析的测试框架 API

系统 SHALL 保持 `yuxiaor-server` 测试源码可在当前解析的 `junit:junit:4.12` 与 `org.mockito:mockito-core:2.15.0` classpath 下编译；本次适配 SHALL NOT 新增或升级测试依赖。

#### Scenario: JUnit 5 风格 Mockito 测试改为当前 runner

- **WHEN** 编译 `MultiHouseSnapshotServiceTest`
- **THEN** 该测试使用 JUnit 4 `@RunWith(MockitoJUnitRunner.class)`、`@Before` 和 `org.junit.Assert` 断言
- **AND** 不导入 `org.junit.jupiter.*`
- **AND** 原测试数据、stub、断言期望和验证顺序保持不变

#### Scenario: Mockito 3 no-interaction API 改为当前兼容 API

- **WHEN** 编译 `CustomerServiceImplDataMaskingTest` 与 `YuxiaorPaymentServiceImpl2PaymentInfoTest`
- **THEN** no-interaction 验证使用 Mockito 2.15 提供的 `verifyZeroInteractions`
- **AND** 被验证的 mock 对象与原测试一致
- **AND** 测试不导入 `verifyNoInteractions`

### Requirement: 测试适配不得改变业务测试语义

系统 SHALL 仅替换测试框架 API，不得改变被测生产行为或测试断言语义。

#### Scenario: 仅框架 API 发生差异

- **WHEN** 对比适配前后3个测试文件
- **THEN** 变更只出现在 imports、runner/annotation、测试方法可见性和 `verifyNoInteractions` → `verifyZeroInteractions`
- **AND** `yuxiaor-server/src/main` 与 `yuxiaor-api/src/main` 无 diff

#### Scenario: 无关但被扫描命中的注释不触发修改

- **WHEN** 检查 `SmartDeviceVisibilityResolverTest`
- **THEN** 该文件已经是 JUnit 4 / Mockito 2 兼容源码
- **AND** 其注释中的 `verifyNoInteractions` 文本不作为编译失败依据，也不要求删除注释
