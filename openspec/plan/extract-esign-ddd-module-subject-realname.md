# 电子签署 DDD 模块 · 签署主体与实名上下文实施计划

## 目标

在不改变 HTTP/Feign 契约、数据库和 MQ 语义的前提下，先建立 `SignSubject` 领域模型、账号 ID/证件类型映射、用例端口和跨上下文出站端口，并迁移一条低风险运行时链路（公寓电子签署账号修复事件）作为首个兼容门面示范。随后按同一模式分批迁移其余实名/主体路径。

## 权威事实

- 账号 ID 前缀：公寓 `4`，租客企业 `3`，租客刷脸 `6`，业主个人 `7`，租客个人 `8`。
- 除旧租客企业 `3` 为 18 位外，`4/6/7/8` 均按 1 位前缀 + 18 位原始 ID 组成 19 位。
- 证件映射：`2->护照`，`3->回乡证`且回乡证号以 `M/m` 开头时映射澳门，否则香港，`4->台胞证`，其余默认身份证。
- 首个迁移链路：`CompanyEsignAcctService.repaireCompanyEsignerAcct` 消费 `ElsignerBinding.INPUT`，检查公寓电子签署账号，不存在则按公寓资料创建账号。
- `yuxiaor-esign` 已有架构门禁：模块不得导入 server service/mapper/entity，domain/application 不得导入 Spring、MyBatis、Feign、Redis、MQ 或供应商 SDK。

## 任务 1：领域模型与测试（TDD）

Create:

- `yuxiaor-esign/src/main/java/com/dream/yuxiaor/esign/subject/domain/model/*.java`
  - `CertificateType`
  - `ElectronicSignAccountType`
  - `ElectronicSignAccountId`
  - `SubjectAuthStatus`
  - `SubjectType`
  - `SignSubject`
- `yuxiaor-esign/src/test/java/com/dream/yuxiaor/esign/subject/domain/SubjectDomainTest.java`

Requirements:

1. `CertificateType.fromLegacyCode(Integer, String)` preserves ID card, passport, Hong Kong/Macao/Taiwan mapping.
2. `ElectronicSignAccountType` preserves all five prefixes and legacy digit width.
3. `ElectronicSignAccountId.encode/decode/matches` preserves generation and reverse parsing; malformed IDs return the specified legacy fallback without throwing.
4. `SubjectAuthStatus.fromVendorStatus` maps only vendor success/error; other statuses remain unchanged/pending.
5. Domain imports only JDK classes.

Test-first: write tests before model classes; expected initial compile failure, then green implementation.

## 任务 2：应用端口与首个用例

Create:

- `subject/application/port/in/RepairCompanyEsignAccountUseCase.java`
- `subject/application/port/out/CompanyContextPort.java`
- `subject/application/port/out/ElectronicSignVendorGateway.java`
- `subject/application/port/out/SubjectAccountAssembler.java`
- `subject/application/usecase/RepairCompanyEsignAccountUseCaseImpl.java`
- domain command/result records under `domain/command` or `domain/query` as needed.

Use case behavior:

1. Input is domain `CompanySnapshot`.
2. Query vendor account by company ID and company user type.
3. If account ID is present, return no-op result.
4. Otherwise assemble a domain account request and call vendor create-account port.
5. No Spring/vendor/server imports in application layer.

Tests:

- Mock outbound ports in JUnit 4.
- Cover existing account, missing account, absent company, and vendor failure/no account result.

## 任务 3：infrastructure 适配器

Create module infrastructure only where it does not touch server internals:

- `subject/infrastructure/account/ElectronicSignAccountIdMapper.java`
- `subject/infrastructure/certificate/CertificateTypeMapper.java`

These adapters map between legacy scalar/DTO forms and domain values. They may use the external signature API but must not import `yuxiaor-server`.

## 任务 4：server 兼容适配器与首链路切换

Create in `yuxiaor-server`:

- `com.dream.yuxiaor.service.elcsignature.esign.EsignSubjectServerAdapter`

Implement module outbound ports by delegating to existing `EsignChannelUtil`, `ICompanyService`, and existing convert logic. This is the anti-corruption layer and is allowed to depend on server internals.

Modify:

- `CompanyEsignAcctService`

Behavior contract:

- Keep `@StreamListener(value = ElsignerBinding.INPUT, condition = ...)` unchanged.
- Keep invalid event short-circuit and exception swallowing/logging semantics.
- Move account-exists/create decision into `RepairCompanyEsignAccountUseCase`.
- Preserve logs at equivalent boundaries; do not alter MQ destination or transaction behavior.

Tests:

- New module use case tests.
- Existing `ElectronicSignAccountNormalFlowTest` must remain green.

## 任务 5：后续迁移边界（不在首个提交内）

After the first chain is stable, repeat the same pattern for:

- `CompanyStatusCheckEventProcess`
- `CompanySubsidiaryStatusEventProcess`
- real-name callback processors
- `FlatmateSignService` public subject/real-name methods
- `CertificationAPI` quota/local verification decisions
- reject/void/delete subject flows

Each batch must:

1. add characterization tests before moving logic;
2. preserve legacy FQCN and route annotations;
3. switch only one cohesive flow;
4. run its server tests plus module architecture tests.

## 验证命令

```bash
cd yuxiaor-pms
mvn -s settings-work.xml -pl yuxiaor-esign test -P dev,env-actuator -Denforcer.skip=true
mvn -s settings-work.xml -pl yuxiaor-server test -P dev,env-actuator -Denforcer.skip=true -Dtest=ElectronicSignAccountNormalFlowTest
mvn -s settings-work.xml -pl yuxiaor-esign,yuxiaor-server -am validate -P dev,env-actuator -Denforcer.skip=true
```

Also verify empty diffs in `yuxiaor-api/src` and non-target production sources where not part of the selected chain.

## 自审结论

- No schema, data migration, deletion, external publishing, new dependency, or public contract change.
- The first implementation slice is reversible and does not duplicate a primary business Bean.
- Further batches remain under the already confirmed strict change; any new dependency or transactional semantic change will pause for reconfirmation.
