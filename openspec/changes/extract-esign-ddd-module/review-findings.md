# 任务级审查记录

## baseline-task · 2026-09-22

- manifest: `370b10e368ef5c4b6e27040ae516c17cfa388c0ed42e82cd5d47342a2d62fe32`
- comparison base: `yuxiaor-pms@fb6b634b7a7383903a7c2672502fd4b631236717`
- scope: `yuxiaor-server/src/test/java/com/dream/yuxiaor/service/elcsignature/EsignHttpFeignContractBaselineTest.java`, `yuxiaor-server/src/test/resources/esign-baseline/runtime-compatibility.md`, `yuxiaor-server/src/test/resources/esign-baseline/existing-test-baseline.md`
- result: PASS with documented external dependency blocker

### Findings

id: baseline-route-sort
severity: Important
repo/path: yuxiaor-server/src/test/java/com/dream/yuxiaor/service/elcsignature/EsignHttpFeignContractBaselineTest.java:52
evidence: API-only JUnit first showed `PersonFaceAuthService` mappings in the previous non-lexicographic expectation.
observable impact: A valid baseline could fail depending on method-name ordering, producing a false migration regression.
status: resolved
minimal fix: Sort mapped methods by method name and freeze the observed lexicographic route list.
verification: API-only contract assertions passed `OK (3 tests)` after the fix.

id: baseline-implementation-coverage
severity: Important
repo/path: yuxiaor-server/src/test/java/com/dream/yuxiaor/service/elcsignature/EsignHttpFeignContractBaselineTest.java:37
evidence: Initial inventory omitted API-mapped implementation classes `PersonFaceAuthServiceImpl`, `CompanySubsidiaryOutService`, `YxrCompanyAuthServiceImpl`, and `FlatmateSignService`.
observable impact: Their inherited routes would not be frozen before moving implementations.
status: resolved
minimal fix: Add the four implementation classes to reflection captures and route assertions.
verification: Test source compiles with project test classpath; API-only route/parameter/return/Feign assertions passed.

id: external-api-missing-dto
severity: Important
repo/path: yuxiaor-server/src/main/java/com/dream/yuxiaor/service/elcsignature/WillingSignRejectService.java:6
evidence: The original required Maven command exited 1 during production `compile`; `WillingSignRejectResultDTO` was absent from the then-resolved API artifact. The newly cloned `yuxiaor-e-signature@6c679be` contains it, and the API JAR was installed locally with SHA-256 `148d2d7ddcbeb9b92ad8a5c1811cdda28bc7d1b77f26d0d9c25cee26d195ce31`.
observable impact: The original production compilation blocker is removed and production compile now succeeds.
status: resolved
minimal fix: Build `yuxiaor-e-signature-api` from the matching clone and install it locally; additionally restore the matching `acc-bill-api` local snapshot.
verification: Retry reaches `testCompile`, proving all previously missing production symbols are resolved.

id: unrelated-test-dependency-mismatch
severity: Important
repo/path: yuxiaor-server/src/test/java/com/dream/yuxiaor/service/contract/multihouse/service/MultiHouseSnapshotServiceTest.java:12
evidence: The independently authorized test adaptation changed the incompatible framework APIs to JUnit 4 / Mockito 2.15 and repaired the remaining stale electronic-signature test constructor/mapper signatures. Full `test-compile` exits 0.
observable impact: The required electronic-signature baseline command now reaches Surefire and records a real result set.
status: resolved
minimal fix: Keep test dependencies unchanged; adapt test source API usage and stale call sites only.
verification: Final baseline aggregate is 476 run, 12 failures, 7 errors, 2 skipped; `EsignHttpFeignContractBaselineTest` is green with 3/3.

id: module-skeleton-architecture-gate
severity: Important
repo/path: yuxiaor-esign/src/test/java/com/dream/yuxiaor/esign/EsignModuleArchitectureTest.java:1
evidence: The new module skeleton is gated by six tests covering Maven direction, bounded-context packages, server-internal import denial, domain technology denial, and application-to-adapter/infrastructure denial. A temporary forbidden application-to-infrastructure import produced the expected failure, and removal restored 6/6 green.
observable impact: The new module cannot silently reintroduce a server dependency, server internals into yuxiaor-esign, or forbidden technology imports in domain/application layers.
status: resolved
minimal fix: Keep the architecture test in the module and extend denylists only when delta spec explicitly changes an architectural rule.
verification: Module test exits 0 with 6 run, 0 failures, 0 errors, 0 skipped; joint Reactor validate exits 0 with yuxiaor-esign before yuxiaor-server.

id: subject-first-slice-architecture
severity: Important
repo/path: yuxiaor-esign/src/main/java/com/dream/yuxiaor/esign/subject/domain/model/ElectronicSignAccountId.java:1
evidence: First subject-context slice adds pure-JDK domain models, application ports, a repair-account use case, infrastructure mappers, and a server anti-corruption adapter. A temporary application-to-infrastructure import made the architecture test fail; after removal, 16 module tests passed.
observable impact: Account prefixes, Hong Kong/Macao distinction, subject status mapping, and the first MQ account-repair flow are now guarded without importing server internals from the module.
status: resolved
minimal fix: Keep domain/application pure, implement outbound ports in yuxiaor-server, and wire pure use cases through server configuration.
verification: Module tests: 16 run / 0 fail; ElectronicSignAccountNormalFlowTest: 4 run / 0 fail; joint validate succeeds.

id: subject-second-slice-event-migration
severity: Important
repo/path: yuxiaor-server/src/main/java/com/dream/yuxiaor/service/elcsignature/realname/CompanyStatusCheckEventProcess.java:17
evidence: Two subject real-name event listeners now delegate to a pure application use case. The server adapter preserves subject/company authentication guards, certificate matching, vendor-account existence checks, and exact legacy AccountDTO assembly. A temporary application-to-infrastructure import failed the architecture gate before removal.
observable impact: Apartment real-name and subject-passed account maintenance events remain externally compatible while subject business decisions move into yuxiaor-esign.
status: resolved
minimal fix: Keep listeners as compatibility adapters; keep repository/vendor assembly in EsignSubjectServerAdapter and decision orchestration in MaintainCompanyAccountUseCaseImpl.
verification: Module tests 20/20 green; ElectronicSignAccountNormalFlowTest 4/4 green; joint validate succeeds; yuxiaor-api has no diff.

id: subject-third-slice-callback-migration
severity: Important
repo/path: yuxiaor-server/src/main/java/com/dream/yuxiaor/service/elcsignature/realname/SubjectRealNameCallbackServerAdapter.java:63
evidence: Four legacy callback processors were first frozen by SubjectRealNameCallbackProcessorTest (initial compile-red followed by legacy green), then converted to compatibility facades. The pure callback use case only propagates non-null routing IDs and success/failure outcomes; the server sink preserves apartment events, subject DB update/default recalculation/todo push, C-end enterprise/person status events and user synchronization, including the personal missing-user short-circuit. A manifest STALE caused by a minimal null-routing fix was discarded and re-frozen before review conclusion.
observable impact: Legacy FQCNs, Bean names, callback routing and terminal vendor-status propagation remain observable while callback decisions move into yuxiaor-esign.
status: resolved
minimal fix: Keep processors as compatibility adapters; keep all server persistence/events in SubjectRealNameCallbackServerAdapter and routing/status policy in HandleSubjectRealNameCallbackUseCaseImpl.
verification: Module tests 27/27; SubjectRealNameCallbackProcessorTest 10/10; combined server callback/normal-flow tests 14/14; joint validate succeeds; yuxiaor-api has no diff; manifest dbf11e25121f15cc000e5523dce6e55ab57deb6632c9f0c4bd208895bda765d8 remains VALID.

unverified（未验证范围）: the individual causes of the 12 failures, 7 errors, and 2 skips are recorded as baseline facts but not diagnosed; transaction boundaries, MQ delivery, executor behavior, callback ack timing, and callback idempotency behind passing tests remain uncharacterized.
residual risk（残余风险）: Maven `SNAPSHOT` dependencies are configured with `updatePolicy=always`; later remote artifact changes can alter dependency resolution even without source changes.
