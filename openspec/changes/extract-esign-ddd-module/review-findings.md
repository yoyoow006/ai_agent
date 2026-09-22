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

unverified（未验证范围）: the individual causes of the 12 failures, 7 errors, and 2 skips are recorded as baseline facts but not diagnosed; transaction boundaries, callback idempotency, MQ delivery, and executor behavior behind passing tests remain uncharacterized.
residual risk（残余风险）: Maven `SNAPSHOT` dependencies are configured with `updatePolicy=always`; later remote artifact changes can alter dependency resolution even without source changes.
