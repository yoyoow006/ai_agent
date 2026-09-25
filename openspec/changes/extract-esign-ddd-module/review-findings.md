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

id: subject-fourth-slice-personal-realname
severity: Important
repo/path: yuxiaor-server/src/main/java/com/dream/yuxiaor/service/orgsign/FlatmateSignService.java:145
evidence: C-end personal real-name eligibility, cache reuse, vendor-result validity, revocation ordering, Redis routing key/TTL and clear-state semantics were frozen by tests before migration. The facade now delegates start/revoke to pure use cases; the server adapter preserves exact legacy vendor request assembly, 15-minute process cache, DO_AUTH event, C-account type 1, missing-account no-op deletion, local clear only after successful vendor deletion, and flow-cache removal. The initial pure-policy test was compile-red, then green; a remote yuxiaor-api SNAPSHOT drift caused unrelated production compile failures and was recorded as an environmental risk, not treated as a code regression.
observable impact: `/local/flatmate-realname-auth/**` facade behavior and error messages remain observable while personal real-name decisions move into yuxiaor-esign.
status: resolved
minimal fix: Keep FlatmateSignService as a compatibility facade; keep identity/vendor/cache side effects only in EsignPersonalRealNameServerAdapter and policy/order in the pure use cases.
verification: Module tests 41/41; FlatmateSignServicePersonalRealNameTest 6/6; combined callback/personal/normal-flow tests 20/20; joint validate succeeds; yuxiaor-api has no diff; manifest ca2a5ecd0087ab3aadb9f721f7f8d0189c9b793470e4900f08aa4e21669f61e4 remains VALID.

id: subject-twelfth-slice-certificate-mapping
severity: Important
repo/path: yuxiaor-server/src/main/java/com/dream/yuxiaor/helper/EsignChannelUtil.java:182
evidence: Legacy certificate switch behavior was frozen by EsignCertificateMappingFacadeTest and module mapper tests before delegation. Legacy codes 1/unknown default to mainland ID, 2 maps passport, 3 maps Hong Kong unless the certificate begins M/m which maps Macao, and 4 maps Taiwan. EsignChannelUtil now delegates through LegacyCertificateTypeMapper and CertificateTypeMapper instead of duplicating the switch.
observable impact: Vendor certificate names remain unchanged while certificate mapping becomes module-owned infrastructure.
status: resolved
minimal fix: Keep vendor enum conversion in CertificateTypeMapper and legacy scalar conversion in LegacyCertificateTypeMapper; do not reintroduce certificate switch logic in server helpers.
verification: Module tests 94/94; EsignCertificateMappingFacadeTest 1/1; combined certificate/channel/identity/assembly/lifecycle/certification/realname/callback/normal-flow tests 69/69; joint validate succeeds; yuxiaor-api has no diff; manifest 39202b6477dc19e36044400e708ce546efbe00ff99f75569fc535f84042243c4 remains VALID.

id: subject-task-completion-audit
severity: Important
repo/path: openspec/changes/extract-esign-ddd-module/tasks.md:22
evidence: Task 3 checklist was audited against the implemented ports and tests. Apartment/account maintenance, real-name callbacks, C-end enterprise/personal real-name, certification authorization, subject lifecycle, account identity, channel, assembly and certificate mapping have module-owned decisions with server adapters. Shared reads/writes for apartment subject rows, identity rows, service quota, process caches and status rows pass through server adapters. Contract-specific reads intentionally remain for task 5's contract-signing context and are not unowned subject-lifecycle writes.
observable impact: Task 3 can be marked complete without claiming contract-signing migration scheduled for task 5.
status: resolved
minimal fix: Keep task 3 and task 5 boundaries separate; do not remove remaining contract-context helpers until task 5 establishes its ports and tests.
verification: Module tests 94/94; task-related server regression selection 69/69; joint validate succeeds; yuxiaor-api has no diff; openspec strict validation passes.

id: subject-eleventh-slice-active-channel
severity: Important
repo/path: yuxiaor-server/src/main/java/com/dream/yuxiaor/helper/EsignChannelUtil.java:108
evidence: Active channel behavior was first frozen by EsignActiveChannelFacadeTest. Exact Redis flag value 2 selects Junzi channel index 2; null, blank, or other values default to E-Sign Bo index 3. The decision now lives in ElectronicSignChannelPolicy and ResolveElectronicSignChannelUseCase; Redis flag access is isolated in EsignActiveChannelServerAdapter and the legacy helper only adapts the resolved channel.
observable impact: Account source channel indexes and Junzi detection remain byte-compatible while channel selection moves into yuxiaor-esign.
status: resolved
minimal fix: Keep EsignChannelUtil as the compatibility helper; keep flag storage in EsignActiveChannelServerAdapter and channel selection in the pure module policy.
verification: Module tests 89/89; EsignActiveChannelFacadeTest 3/3; combined channel/assembly/identity/lifecycle/certification/realname/callback/normal-flow tests 68/68; joint validate succeeds; yuxiaor-api has no diff; manifest bfa822f5c379c291b1b749b6ffbc0d785c689f7249d46c75d120b4815d0cb792 remains VALID.

id: subject-tenth-slice-company-context-read-boundary
severity: Important
repo/path: yuxiaor-server/src/main/java/com/dream/yuxiaor/service/elcsignature/esign/EsignCompanySubjectContextService.java:1
evidence: The subject adapter previously combined a service abstraction with direct CompanySubsidiaryMapper access for subject-by-certificate reads. A dedicated server context service now provides subjectByIdNum and signInfo reads, and EsignSubjectServerAdapter consumes that boundary instead of importing the shared mapper. Existing normal-flow tests were updated only at the injection boundary and retained all behavioral assertions.
observable impact: No response or persistence behavior changes; shared apartment/subject read ownership is explicit and module adapters no longer bypass the server context boundary.
status: resolved
minimal fix: Keep shared company/subject reads in EsignCompanySubjectContextService; keep EsignSubjectServerAdapter as module port implementation without direct mapper access.
verification: Module tests 85/85; combined assembly/identity/lifecycle/certification/realname/callback/normal-flow tests 65/65; joint validate succeeds; yuxiaor-api has no diff; manifest 49b0aef9bdbd9e04b92a8e520e1cdd13ba82ceca2b3aba9979c0a93a378d2376 remains VALID.

id: subject-ninth-slice-company-account-assembly
severity: Important
repo/path: yuxiaor-server/src/main/java/com/dream/yuxiaor/service/elcsignature/esign/EsignSubjectServerAdapter.java:78
evidence: Apartment account field selection and fallback were frozen by module/server tests before delegation. Company type 3 now selects legal fields and falls back to link-man fields; personal type selects legal identity/link-man mobile according to legacy behavior. AssembleCompanyAccountUseCase owns request assembly, and server vendor DTO conversion consumes CompanyAccountAssemblyPolicy.SelectedFields rather than independently duplicating fallback rules.
observable impact: Vendor account requests keep the same names, certificates, mobiles, licences and fallback order while assembly decisions move into yuxiaor-esign.
status: resolved
minimal fix: Keep EsignSubjectServerAdapter as the vendor DTO adapter; keep fallback/classification rules in CompanyAccountAssemblyPolicy and request construction in the module use case.
verification: Module tests 85/85; EsignCompanyAccountAssemblyTest 2/2; combined assembly/identity/lifecycle/certification/realname/callback/normal-flow tests 65/65; joint validate succeeds; yuxiaor-api has no diff; manifest ff4051c5f7a752548e7e79e8c03f486b7394d4d9302b81998fa53c8aac15c874 remains VALID.

id: subject-eighth-slice-account-identity-port
severity: Important
repo/path: yuxiaor-server/src/main/java/com/dream/yuxiaor/helper/EsignChannelUtil.java:259
evidence: Account identity scalar behavior was frozen by EsignChannelIdentityFacadeTest before delegation. Apartment, renter-face, renter-personal and owner-personal encode/decode/type checks now delegate to SubjectAccountIdentityPort backed by ElectronicSignAccountId, preserving legacy widths 4/6/8/7, malformed zero fallback and wrong-type false result. Legacy renter organization remains 18-digit and stays in the compatibility helper until the contract-signing context migrates.
observable impact: External account IDs and callback routing remain unchanged while the module owns all non-legacy organization identity mappings.
status: resolved
minimal fix: Keep EsignChannelUtil as compatibility helper; use SubjectAccountIdentityPort for all subject identity conversions and keep the legacy 3-prefix local until its wider callers migrate.
verification: Module tests 80/80; EsignChannelIdentityFacadeTest 4/4; combined identity/lifecycle/certification/realname/callback/normal-flow tests 63/63; joint validate succeeds; yuxiaor-api has no diff; manifest 7a56c5c3d7ef6715c25a0e015e2331c220db17f244691e1d387227980b793516 remains VALID.

id: subject-seventh-slice-lifecycle
severity: Important
repo/path: yuxiaor-server/src/main/java/com/dream/yuxiaor/service/elcsignature/esign/EsignSubjectLifecycleServerAdapter.java:1
evidence: Reject, unAuth and void lifecycle ordering was guarded by characterization/module tests before delegation. The pure policy checks requested-company ownership, sign-info existence, approved-plus-closed state for void, and pending willing tasks. The server adapter preserves reject auth reset to 0, unbind, default recalculation, after-commit vendor deletion, unAuth cancel status 4 plus subject deletion, and void-only local status 4 without vendor deletion. Existing void tests were extended only to inject the new use case while retaining their assertions.
observable impact: Legacy FQCNs, transactional facades, error messages, local state writes and after-commit vendor ordering remain externally compatible.
status: resolved
minimal fix: Keep CompanySubsidiaryOutService and CompanySubsidiaryServiceAdapter as transactional facades; keep persistence/events in EsignSubjectLifecycleServerAdapter and guard ordering in the pure lifecycle use case.
verification: Module tests 75/75; CompanySubsidiaryLifecycleFacadeTest 5/5; existing void tests 11/11; combined lifecycle/certification/realname/callback/normal-flow tests 59/59; joint validate succeeds; yuxiaor-api has no diff; manifest 69044ab102045c1ee33827f5d1f37b36f4cc0bba7ce64becd6d5877f42d26eec remains VALID.

id: subject-sixth-slice-certification-authorization
severity: Important
repo/path: yuxiaor-server/src/main/java/com/dream/yuxiaor/service/certification/CertificationAPI.java:73
evidence: Real-name service gate, quota exhaustion, billing exemption for company 64043 and company electronic contract type 1, invalid-user no-billing, and third-party one-count billing behavior were first frozen by CertificationAuthorizationApiTest. The decisions now live in a pure policy/use case; the adapter preserves the exact legacy consume DTO. The method retains @Transactional(REQUIRES_NEW), quota access is skipped for exempt paths, local/invalid results do not consume quota, and only a positive third-party result consumes one count.
observable impact: Real-name authorization responses, error codes and service-count consumption remain externally compatible while gate/quota/billing decisions move into yuxiaor-esign.
status: resolved
minimal fix: Keep CertificationAPI as the transactional compatibility facade; keep quota persistence only in EsignCertificationAuthorizationServerAdapter and gate/billing ordering in the pure use case.
verification: Module tests 65/65; CertificationAuthorizationApiTest 6/6; combined certification/enterprise/personal/callback/normal-flow tests 35/35; joint validate succeeds; yuxiaor-api has no diff; manifest 60933b709562ae142a71728bbde21b534045bba4601507254dd436aff13aa73f remains VALID.

id: subject-fifth-slice-enterprise-realname
severity: Important
repo/path: yuxiaor-server/src/main/java/com/dream/yuxiaor/service/orgsign/FlatmateSignService.java:160
evidence: C-end enterprise URL and revocation behavior was frozen before migration with 9 characterization tests covering missing/approved/incomplete profiles, 20-day URL caching plus DO_AUTH transition, live cache reuse, vendor-approved local transition, and vendor-delete failure ordering. The pure policy/use case now makes those decisions; the server adapter preserves exact legacy profile filtering, vendor account checks, URL creation, cache key/TTL, status-row re-read before update, successful-update cache removal, null vendor-result behavior, and deleted-profile write after successful vendor deletion.
observable impact: `/local/flatmate-realname-auth/**` enterprise URL and revocation behavior remains externally compatible while enterprise real-name decisions move into yuxiaor-esign.
status: resolved
minimal fix: Keep FlatmateSignService as the compatibility facade; keep profile/vendor/cache/persistence side effects in EsignEnterpriseRealNameServerAdapter and state/reuse/revoke ordering in the pure use case.
verification: Module tests 57/57; FlatmateSignServiceEnterpriseRealNameTest 9/9; combined enterprise/personal/callback/normal-flow tests 29/29; joint validate succeeds; yuxiaor-api has no diff; manifest b23579e053b104cd68b527ffc6bea65f4992f073b137f944094fe3f7ed18c7ce remains VALID.

id: subject-third-slice-callback-migration
severity: Important
repo/path: yuxiaor-server/src/main/java/com/dream/yuxiaor/service/elcsignature/realname/SubjectRealNameCallbackServerAdapter.java:63
evidence: Four legacy callback processors were first frozen by SubjectRealNameCallbackProcessorTest (initial compile-red followed by legacy green), then converted to compatibility facades. The pure callback use case only propagates non-null routing IDs and success/failure outcomes; the server sink preserves apartment events, subject DB update/default recalculation/todo push, C-end enterprise/person status events and user synchronization, including the personal missing-user short-circuit. A manifest STALE caused by a minimal null-routing fix was discarded and re-frozen before review conclusion.
observable impact: Legacy FQCNs, Bean names, callback routing and terminal vendor-status propagation remain observable while callback decisions move into yuxiaor-esign.
status: resolved
minimal fix: Keep processors as compatibility adapters; keep all server persistence/events in SubjectRealNameCallbackServerAdapter and routing/status policy in HandleSubjectRealNameCallbackUseCaseImpl.
verification: Module tests 27/27; SubjectRealNameCallbackProcessorTest 10/10; combined server callback/normal-flow tests 14/14; joint validate succeeds; yuxiaor-api has no diff; manifest dbf11e25121f15cc000e5523dce6e55ab57deb6632c9f0c4bd208895bda765d8 remains VALID.

unverified（未验证范围）: the individual causes of the 12 failures, 7 errors, and 2 skips are recorded as baseline facts but not diagnosed; transaction boundaries, MQ delivery, executor behavior, callback ack timing, and callback idempotency behind passing tests remain uncharacterized.
residual risk（残余风险）: Maven `SNAPSHOT` dependencies are configured with `updatePolicy=always`; later remote artifact changes can alter dependency resolution even without source changes. `yuxiaor-api-20260924.060501-4779` again removed unrelated checkout APIs and blocked the default local repository; verification used an isolated copy pinned to compatible `yuxiaor-api-20260923.074928-4775`, without changing source dependencies or yuxiaor-api/src.
