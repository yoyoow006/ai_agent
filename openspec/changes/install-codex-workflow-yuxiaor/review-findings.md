# Review findings

## T0-001

```text
id: T0-001
severity: Important
repo/path:line: openspec/plan/install-codex-workflow-yuxiaor.md:34-46
evidence: Task 0 originally required the workflow gate but did not state the exact observable summary; the independent reviewer could not confirm required evidence from the committed plan alone.
observable impact: A partial gate result could be mistaken for complete Task 0 evidence.
status: resolved
minimal fix: State the exact required summary and retain a fresh command transcript in the local SDD report.
verification: On clean commit e42816b, `bash scripts/validate-workflow.sh --require-openspec` exited 0 and ended with `PASS=169 FAIL=0 SKIP=0`; transcript is `.codex/sdd/install-codex-workflow-yuxiaor/task-0-validation.txt`.
```

## T0-002

```text
id: T0-002
severity: Important
repo/path:line: openspec/plan/install-codex-workflow-yuxiaor.md:57-110
evidence: The original Task 1 block did not enable `set -euo pipefail`, so a failed identity check could fall through to a misleading preflight PASS summary.
observable impact: Target identity mismatch could otherwise permit progression to rename/install.
status: resolved
minimal fix: Enable fail-fast immediately after Task 1 variables and before evidence directory creation or checks.
verification: Commit e42816b adds `set -euo pipefail`; `openspec validate install-codex-workflow-yuxiaor --strict --no-interactive` and `git diff --check` pass, and a fail-fast probe exited 1 with zero output bytes.
```

## TASK1-001

```text
id: TASK1-001
severity: Important
repo/path:line: openspec/changes/install-codex-workflow-yuxiaor/evidence/nested-repos-before.sha256:1-10; openspec/plan/install-codex-workflow-yuxiaor.md:104-118
evidence: The original snapshot printed each digest followed by the nested repository directory name, contrary to the privacy contract.
observable impact: Business repository/module names would enter committable evidence.
status: resolved
minimal fix: Include repository name, HEAD, and status only as inputs to a per-repository SHA-256 digest; output digest lines only and sort digests before writing.
verification: Regenerate the before snapshot with the privacy-safe format and confirm it has exactly 10 fixed-length digest lines with no repository names; Task 3 uses the identical format for byte comparison.
```

## Task 2 independent review

- Manifest: `62bf761359901f7cf8bb4a3b983efd8a3ceb081c4f37cc6d43f4b8669a8c3ae2`
- Verdict: `TASK2_REVIEW=PASS`
- Open Critical/Important findings: none.
- Independently confirmed: old entry preserved; key installed identities correct; `.gitignore` managed block correct; Codex-only; `CLAUDE.md` and `REVIEW.md` unchanged; installer output exact; no direct unauthorized-write evidence.

## TASK3-001

```text
id: TASK3-001
severity: Important
repo/path:line: openspec/changes/install-codex-workflow-yuxiaor/evidence/nested-repos-before.sha256:1-10; openspec/plan/install-codex-workflow-yuxiaor.md:174-245
evidence: After installation and before final validation, external concurrent state drift affected two nested business repositories, so the pre-install snapshot no longer represented the current state. Root workflow identities remained correct and installer output never touched nested repositories.
observable impact: Comparing final validation against the superseded pre-install snapshot would report an external business-repo drift as an installer failure.
status: resolved
minimal fix: Preserve the original pre-install snapshot unchanged; with user confirmation, take two identical read-only privacy-safe summary samples of the current 10-repository state and use that stable verified baseline across Task 3.
verification: Two consecutive GIT_OPTIONAL_LOCKS=0 samples must match exactly, the baseline must contain 10 digest-only lines, and the post-validation snapshot must compare byte-identical against this verified baseline. The accepted drift is two repositories (`BEFORE_ONLY=2`, `VERIFIED_ONLY=2`), without persisting repository names or status bodies.
```

## TASK3-002

```text
id: TASK3-002
severity: Important
repo/path:line: scripts/lib/validate-workflow-core.sh:202-210,504-509; scripts/ai-workflow-assets/shared/scripts/lib/validate-workflow-core.sh:202-210,504-509
evidence: The target root is not a Git repository, so direct `git check-ignore` probes returned 128. Required validation reported exactly `PASS=101 FAIL=2 SKIP=0` for Python-cache and SDD ignore checks even though all required `.gitignore` patterns were present.
observable impact: The installed Codex workflow could not meet its required validation gate in the authorized non-Git workspace without initializing Git or touching nested repositories.
status: resolved
minimal fix: Add a failing non-Git-root validator test, then make ignore checks use the real Git worktree when present or temporary external Git metadata with the target as work-tree otherwise; clean the temporary metadata on exit and never create `.git` in the target.
verification: The new test failed before implementation with the three expected ignore failures and passed after implementation. The fixed core and its contract-test asset must be synchronized to the target, target required validation must report no FAIL/SKIP, and the target must still have no root `.git`.
```

## TASK3-003

```text
id: TASK3-003
severity: Important
repo/path:line: scripts/tests/test_validate_workflow.py:643-663; scripts/ai-workflow-assets/shared/scripts/tests/test_validate_workflow.py:643-663
evidence: The new non-Git test unconditionally expected both Codex and Claude SDD labels. The source fixture has both assistants, but the authorized target is Codex-only; the second target run therefore failed only the inherited profile variant with `PASS=102 FAIL=1 SKIP=0`.
observable impact: A valid single-assistant non-Git installation could be rejected by the workflow's own contract suite.
status: resolved
minimal fix: Derive expected SDD labels from `_assistant_required_in_fixture`, asserting the selected assistant label is present and the unselected label is absent.
verification: The profile-aware test passed in both source and Codex-only target contexts; the final target required gate reports `PASS=103 FAIL=0 SKIP=0`.
```

## TASK3-004

```text
id: TASK3-004
severity: Important
repo/path:line: external target root outside Git manifest:1
evidence: The initial Task 3 review was interrupted before a fresh direct target recheck, so it could rely only on implementation evidence.
observable impact: Without direct read-only verification, final external target state would depend on the implementer rather than independent observation.
status: resolved
minimal fix: Complete only the assigned read-only checks: protected root hashes, repaired asset identity, `.git` and `.claude` absence, 10-repository count, and digest-only nested-repository comparison against the verified baseline.
verification: Independent reviewer checks produced ROOT_HASHES_PROFILE_AND_PROTECTED_FILES=PASS, REPAIRED_VALIDATOR_ASSETS_EXACT=PASS, TARGET_ROOT_GIT_ABSENT=PASS, TARGET_CLAUDE_ABSENT=PASS, NESTED_REPOSITORY_COUNT=10, and NESTED_REPOSITORIES_MATCH_VERIFIED_BASELINE=PASS; manifest remained VALID before and after.
```

## Task 3 independent review

- Manifest: `be03c53814c42974dcf8b98a02ef106056c1f71d694ac5387b93517bfc75cc8c`
- Verdict: `TASK3_DELTA_REVIEW=PASS`
- Open Critical/Important findings: none.
- Independently confirmed: final target identities and repaired assets; root `.git` and `.claude` absence; 10 nested repositories unchanged from the user-confirmed stable baseline.

## VERIFY-SPEC-A-001

```text
id: VERIFY-SPEC-A-001
severity: Important
repo/path:line: openspec/changes/install-codex-workflow-yuxiaor/proposal.md:32; openspec/changes/install-codex-workflow-yuxiaor/review-findings.md:49-60
evidence: Verify review found that the privacy-safe before/verified snapshots differ for two nested repositories, while the records initially described only one.
observable impact: The user-confirmed external drift scope would be understated.
status: resolved
minimal fix: Request and obtain explicit user confirmation for both drifted repositories; correct narrative records to two while preserving original digest evidence unchanged.
verification: Read-only stable sampling reports CURRENT_STABLE_TWO_SAMPLES=PASS, MATCHES_EXISTING_VERIFIED_BASELINE=PASS, BEFORE_ONLY=2, VERIFIED_ONLY=2.
```

## QUALITY-B-001

```text
id: QUALITY-B-001
severity: Minor
repo/path:line: openspec/changes/install-codex-workflow-yuxiaor/evidence/target-validation-second-failed.txt:186,194,202,210,213
evidence: Five blank lines in the committed failure transcript contain two trailing spaces.
observable impact: `git diff --check` fails on avoidable evidence whitespace.
status: resolved
minimal fix: Remove trailing whitespace only; preserve failure diagnostics and final counts.
verification: `git diff --check main..HEAD` exits 0.
```

## Unverified

- Strict Verify dual independent reviewers remain pending.

## Residual risk

- The external target is outside the Git review manifest; nested business repositories can drift concurrently. Final verification must compare against the user-confirmed stable baseline and report any further drift without attributing it to the installer without evidence.
- Portable tests that run under installed fixtures must derive assistant-specific expectations from the profile instead of assuming the source repository has both adapters.
