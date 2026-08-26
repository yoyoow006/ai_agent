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

## Unverified

- Target directory state must be rechecked after the TASK1-001 privacy fix; no target write is authorized until the corrected Task 1 review passes.
- Task 2–3 execution outputs do not exist yet.

## Residual risk

- The external target is outside the Git review manifest; fixed hashes and the nested-repository count must be revalidated immediately before rename/install.
