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
evidence: After installation and before final validation, an external concurrent process added and then removed untracked documents in one nested business repository, so the pre-install snapshot no longer represented the current state. Root workflow identities remained correct and installer output never touched nested repositories.
observable impact: Comparing final validation against the superseded pre-install snapshot would report an external business-repo drift as an installer failure.
status: resolved
minimal fix: Preserve the original pre-install snapshot unchanged; with user confirmation, take two identical read-only privacy-safe summary samples of the current 10-repository state and use that stable verified baseline across Task 3.
verification: Two consecutive GIT_OPTIONAL_LOCKS=0 samples must match exactly, the baseline must contain 10 digest-only lines, and the post-validation snapshot must compare byte-identical against this verified baseline.
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

## Unverified

- Task 3 target-validation still contains the first failed run; the fixed validator asset must be synchronized and the full target validation rerun.

## Residual risk

- The external target is outside the Git review manifest; nested business repositories can drift concurrently. Final verification must compare against the user-confirmed stable baseline and report any further drift without attributing it to the installer without evidence.
