# 综合审查记录

## full-review · 2026-09-22

- manifest: `aef4493e3aebae3253b1cf6a3c45a1cecd33492cccfb54c2193178f555961a0b`
- repaired manifest: `99d05259a25bec5c267a96202b4b12a471d0ae9cdf9a90d2d22e3c409fd588cb`
- comparison base: `yuxiaor-pms@ecd92d1c1f`
- result: PASS with recorded baseline failures

### Findings

id: scope-expanded-to-unblock-baseline
severity: Important
repo/path: openspec/changes/adapt-pms-tests-junit4-mockito2/proposal.md
evidence: Initial confirmation covered three framework-incompatible tests, but full `testCompile` still failed in three stale electronic-signature tests and the contract reflection baseline could not run.
observable impact: Without those minimal test-only fixes, the requested baseline command still cannot enter Surefire.
status: resolved
minimal fix: Limit expansion to stale test call adaptation and contract reflection extraction; keep production and API source unchanged.
verification: Full `test-compile` exits 0; production/API diff is empty; proposal/tasks now record the expanded test-only scope.

id: skipped-list-imprecise
severity: Important
repo/path: yuxiaor-server/src/test/resources/esign-baseline/existing-test-baseline.md
evidence: Initial skipped section named one test and left the second identifier ambiguous.
observable impact: Migration comparisons could misidentify a changed skipped baseline.
status: resolved
minimal fix: Parse Surefire XML and list both skipped identifiers exactly.
verification: XML reports identify `CompanyWillingSignTaskMapperMySqlIT.companyWillingSignTaskMapperMySqlIT` and `UserFlatmateMarkServiceTest.userFlatmateMarkServiceTest`.

id: selected-adapted-tests-have-existing-failures
severity: Minor
repo/path: yuxiaor-server/src/test/java/com/dream/yuxiaor/service/contract/multihouse/service/MultiHouseSnapshotServiceTest.java:171
evidence: After framework adaptation, 2 of 8 tests fail on `BigDecimal` scale (`50` expected vs `50.00` actual). The other 14 adapted tests pass.
observable impact: These are pre-existing behavior/scale mismatches exposed once compilation succeeds; they are now part of the broader non-green baseline rather than hidden by compile failure.
status: open
minimal fix: A separate behavior-fix task should diagnose production scale semantics before changing either test or production.
verification: Selected command reports 22 run, 2 failures; failures are only the two BigDecimal-scale assertions.
residual note: `accepted-risk` is not a migration release acceptance; it records that no behavior was silently changed in this test-framework task.

unverified（未验证范围）: individual causes of the 12 baseline failures, 7 errors, and 2 skips; all production behavior behind failing tests; full repository test suite outside the requested pattern.
residual risk（残余风险）: local Maven depends on locally installed `yuxiaor-e-signature-api` and `acc-bill-api` snapshot artifacts; remote SNAPSHOT drift can reproduce dependency mismatch.
