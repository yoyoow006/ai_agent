# Implementation Plan——speed-up-ci-validation

## 目标与全局约束

目标是在不削弱任何门禁的前提下，把 GitHub Actions `workflow-validation` 的主要耗时从安装器集成测试中的重复完整契约套件，收敛为：每个 assistant 一次真实完整公共门禁 + 一个 fail-closed required sentinel 探针。

逐字全局约束：

- CI 必须实际运行 `bash scripts/validate-workflow.sh --require-openspec`、`python3 -B -m unittest -v scripts.tests.test_install_ai_workflow` 与 `python3 -B -m unittest -v scripts.tests.test_install_workflow`，任一失败使任务失败。
- 不得通过跳过测试、缓存 PASS 结果、删除源仓专属用例或添加测试专用后门来提速。
- 随包 `scripts/validate-workflow.sh`、`scripts/tests/test_validate_workflow.py`、`scripts/tests/run_validate_workflow_parallel.py` 必须与活动源文件字节一致，并进入 sorted manifest。
- `WORKFLOW_TEST_JOBS=1` 必须保留串行 unittest 回退；默认路径必须使用 bounded parallel runner。
- wrapper 顶层汇总末行仍必须是 `PASS=<n> FAIL=<n> SKIP=<n>`；契约套件整体仍只计 1 个顶层 PASS/FAIL 检查。
- 所有测试运行必须带 `-B` 或 `PYTHONDONTWRITEBYTECODE=1`，避免污染资产树。
- 长套件运行期间仓库零编辑；如需修复，先停止套件、修改并重启最终验证。

## 基线与事实

- GitHub run `33704385709`：总 1498s；Validate workflow 318s；安装器套件 1109s；Bash installer 58s。
- GitHub run `34691053891`：总 1582s；Validate workflow 196s；安装器套件 1375s 后失败。
- 活动源仓 wrapper 已默认调用 `scripts/tests/run_validate_workflow_parallel.py`；随包 wrapper 仍直接串行调用 unittest。
- 随包 manifest 缺 `scripts/tests/run_validate_workflow_parallel.py`，物理资产也不存在。
- `InstalledWorkflowValidationTests.test_installed_codex_and_claude_validate_without_source_or_openspec` 对每个 assistant 当前执行：直接串行契约套件、公共门禁、required 门禁；后两者都会再次执行完整随包契约套件。
- 现有基线还存在既有资产脱节（不是本变更新增语义）：`shared/.ai/rules/review.md`、`shared/scripts/lib/validate-workflow-core.sh`、双侧 `archive/build/design/open/verify` 技能资产未同步活动源。全局 `test_reusable_assets_are_byte_synchronized_with_active_sources` 因此已经红；必须先机械复制当前活动源到这些资产并单独提交，才能获得本变更的可验证绿基线。
- Unit B 首次绿灯进一步暴露两个随包前置问题：`codex/AGENTS.md` 资产仍为旧标准四件套/无条件双确认文案；随包契约测试的 `_recording_python_script` stub 未处理 `python3 -B scripts/tests/run_validate_workflow_parallel.py`，导致嵌套 wrapper 成功路径缺少 `Ran N tests`。先修这两点，再复跑 Unit B。
- Unit B sentinel 还暴露 wrapper 生产缺陷：`--require-openspec` 被解析进 `require_openspec_user` 后未转发 core，导致目标缺 OpenSpec CLI 时公共 wrapper 仍可能退出 0。必须以 targeted 红灯证明参数转发，再修复活动与随包 wrapper。
- Claude-only 目标还暴露 `MutationStandardThreePieceSuiteTest` 中 open/design 两个 Codex 专属用例未随 AGENTS guard 一起跳过；需按同一已允许理由适配单侧安装，并同步随包测试。

## Task 1——红灯守卫与 wrapper 成功计数

### Create / Modify

Before Task 1 implementation, commit one mechanical baseline-only synchronization of these existing drifted reusable assets to their current active sources:

- `scripts/ai-workflow-assets/shared/.ai/rules/review.md`
- `scripts/ai-workflow-assets/shared/scripts/lib/validate-workflow-core.sh`
- both assistants' packaged `archive/build/design/open/verify` skill files
- current `scripts/validate-workflow.sh` and `scripts/tests/test_validate_workflow.py` asset copies

This commit must not include new tests or the missing parallel runner.

- Modify `scripts/tests/test_validate_workflow.py`
  - In `ParallelContractRunnerTest`:
    - extend `_stage_wrapper_tree` so stub runner emits a valid `Ran 1 tests` summary;
    - add `test_wrapper_reports_contract_test_count_by_default`;
    - extend serial fallback test to assert count;
    - add `test_wrapper_fails_closed_when_contract_success_count_is_missing`.
  - Keep assertions for marker-based runner selection and existing failure propagation.

### Red test

```bash
python3 -B -m unittest -v \
  scripts.tests.test_validate_workflow.ParallelContractRunnerTest.test_wrapper_reports_contract_test_count_by_default \
  scripts.tests.test_validate_workflow.ParallelContractRunnerTest.test_wrapper_fails_closed_when_contract_success_count_is_missing
```

Expected red: current wrapper prints only `[PASS] 工作流顶层契约测试` and cannot distinguish a successful runner that omits `Ran N tests`.

### Minimal implementation

- Modify `scripts/validate-workflow.sh`:
  - after `run_contract_suite` succeeds, extract the last `Ran <positive-integer> test/tests` line from `$contract_output`;
  - accept both unittest singular `Ran 1 test` and runner plural `Ran 188 tests`;
  - valid count → print `[PASS] 工作流顶层契约测试（<count> tests）`;
  - missing/non-numeric count → print `[FAIL] 契约套件用例计数解析失败`, increment `fail_count`, do not increment contract PASS, and retain diagnostics;
  - run `render_contract_suite_skips` after either success or count-parse failure;
  - failed suite path remains fail-closed and continues to print complete captured output.

### Green test

```bash
python3 -B -m unittest -v \
  scripts.tests.test_validate_workflow.ParallelContractRunnerTest.test_wrapper_reports_contract_test_count_by_default \
  scripts.tests.test_validate_workflow.ParallelContractRunnerTest.test_wrapper_jobs_one_falls_back_to_unittest \
  scripts.tests.test_validate_workflow.ParallelContractRunnerTest.test_wrapper_fails_closed_when_contract_success_count_is_missing
```

Expected: all exit 0; success output contains count; malformed success output exits non-zero.

## Task 2——并行执行器随包分发

### Create / Modify

- Modify `scripts/tests/test_install_ai_workflow.py`
  - add `scripts/tests/run_validate_workflow_parallel.py` to `EXPECTED_ASSET_PATHS["shared"]`;
  - add byte-synchronization mapping `shared/scripts/tests/run_validate_workflow_parallel.py` → active runner;
  - add explicit assertion that manifest contains the runner as `0644`, physical file exists, and bytes match active source.
- Add `scripts/ai-workflow-assets/shared/scripts/tests/run_validate_workflow_parallel.py` as byte copy of active runner.
- Insert sorted manifest entry:

```json
{
   "mode" : "0644",
   "path" : "scripts/tests/run_validate_workflow_parallel.py"
}
```

- Copy updated `scripts/validate-workflow.sh` and `scripts/tests/test_validate_workflow.py` to their byte-synced shared asset paths.

### Red test before implementation

```bash
python3 -B -m unittest -v \
  scripts.tests.test_install_ai_workflow.PortableAssetManifestTests.test_manifest_exactly_enumerates_sorted_physical_assets \
  scripts.tests.test_install_ai_workflow.PortableAssetContentTests.test_reusable_assets_are_byte_synchronized_with_active_sources
```

Expected red after test expectations are added: runner path absent from manifest/physical tree and wrapper asset is stale.

### Green tests

```bash
python3 -B -m unittest -v \
  scripts.tests.test_install_ai_workflow.PortableAssetManifestTests \
  scripts.tests.test_install_ai_workflow.PortableAssetContentTests.test_reusable_assets_are_byte_synchronized_with_active_sources
```

Expected: manifest enumeration, mode, physical asset, and byte synchronization all pass.

### Task-level review unit A

Invariant: portable gate parity and bounded parallel semantics.

Review exact files:

- `scripts/validate-workflow.sh`
- `scripts/tests/test_validate_workflow.py`
- `scripts/tests/run_validate_workflow_parallel.py`
- `scripts/ai-workflow-assets/shared/scripts/validate-workflow.sh`
- `scripts/ai-workflow-assets/shared/scripts/tests/test_validate_workflow.py`
- `scripts/ai-workflow-assets/shared/scripts/tests/run_validate_workflow_parallel.py`
- `scripts/ai-workflow-assets/manifest.json`
- `scripts/tests/test_install_ai_workflow.py`

Main session freezes this scope; independent reviewer runs `review_manifest.py verify` before reading and before conclusion, then checks source/asset parity, serial fallback, count parsing fail-closed behavior, manifest/mode correctness, and no new external dependency.

## Task 3——安装器集成测试去重与 sentinel required 探针

### Modify

- `scripts/tests/test_install_ai_workflow.py`

### Add structural red test

Add `InstalledIntegrationPerformanceContractTests` using `ast.parse` over `InstalledWorkflowValidationTests.test_installed_codex_and_claude_validate_without_source_or_openspec`:

- direct `_run_target` argument containing `scripts.tests.test_validate_workflow` must occur 0 times;
- non-required `_run_target` invocation of `scripts/validate-workflow.sh` must occur exactly 1 time;
- `--require-openspec` invocation must occur exactly 1 time.

Red command:

```bash
python3 -B -m unittest -v \
  scripts.tests.test_install_ai_workflow.InstalledIntegrationPerformanceContractTests
```

Expected red: current method still has the direct serial contract call; structural counts violate the new contract.

### Refactor integration method

For each assistant:

1. Install once and snapshot Git identity/status exactly as now.
2. Run tools tests once.
3. Run exactly one real full public gate:

```python
self._run_target(
    target, environment,
    "bash", "scripts/validate-workflow.sh",
)
```

4. Assert:
   - return code 0;
   - `[PASS] 工作流顶层契约测试（<shipped_count> tests）`;
   - exactly one `[SKIP] OpenSpec CLI`;
   - final `PASS=<n> FAIL=0 SKIP=1`;
   - allowed skip reasons remain bounded by the existing allowlist;
   - required named profile/shared-gate tests still appear as `ok`.
5. Create `temporary_root / f"required-{assistant}"` as a copy of the installed target with `shutil.copytree(..., symlinks=True)`.
6. Overwrite only the copied target's `scripts/tests/test_validate_workflow.py` with a one-test sentinel module that prints `CONTRACT_SENTINEL_CALLED`.
7. Run copied target:

```python
self._run_target(
    required_target, environment,
    "bash", "scripts/validate-workflow.sh", "--require-openspec",
)
```

8. Assert non-zero exit, exact `[FAIL] OpenSpec CLI 缺失；required 模式不得跳过严格校验`, `CONTRACT_SENTINEL_CALLED`, `Ran 1 tests`, and final `FAIL=1`.
9. Continue existing status, Git identity, idempotence, and snapshot assertions on the untouched real target.

### Green tests

```bash
python3 -B -m unittest -v \
  scripts.tests.test_install_ai_workflow.InstalledIntegrationPerformanceContractTests \
  scripts.tests.test_install_ai_workflow.InstalledWorkflowValidationTests.test_installed_codex_and_claude_validate_without_source_or_openspec
```

Expected: structural contract passes; both assistant paths run one real full gate each and a one-test required sentinel.

### Task-level review unit B

Invariant: performance optimization does not diminish installed-target coverage or fail-closed required semantics.

Review exact files:

- `scripts/tests/test_install_ai_workflow.py`
- `scripts/tests/test_validate_workflow.py`
- `scripts/ai-workflow-assets/codex/AGENTS.md`
- `scripts/validate-workflow.sh`
- `scripts/ai-workflow-assets/shared/scripts/validate-workflow.sh`
- `scripts/ai-workflow-assets/shared/scripts/tests/run_validate_workflow_parallel.py`
- `scripts/ai-workflow-assets/shared/scripts/tests/test_validate_workflow.py`

Independent reviewer verifies:

- both assistants still execute the full real contract suite exactly once;
- tools, status, identity, and idempotence checks remain;
- sentinel proves contract execution rather than relying only on exit code;
- sentinel target is separate and does not contaminate real target assertions;
- no cache, skip, or test-only production branch was introduced.

## Task 4——全量验证与性能证据

Run only after Tasks 1–3 are green and repository is frozen:

```bash
openspec validate speed-up-ci-validation --strict --no-interactive
bash scripts/validate-workflow.sh --require-openspec
python3 -B -m unittest -v scripts.tests.test_install_ai_workflow
python3 -B -m unittest -v scripts.tests.test_install_workflow
```

Record in `tasks.md`:

- each exit code and relevant final summary;
- installer suite wall time measured with `/usr/bin/time -f 'ELAPSED=%e EXIT=%x'`;
- confirmation that no skipped source test was added and CI required commands remain unchanged.

Expected:

- OpenSpec strict valid;
- required workflow gate `FAIL=0`;
- 83+ installer tests pass (count may grow with new guards);
- Bash installer 8 tests pass;
- installer suite is materially below the GitHub 1109–1375s bottleneck; no fixed minute threshold is treated as pass/fail because CI CPU varies.

## Task 5——严格终验、知识沉淀与归档准备

1. Read `verification` and `verify` skills before claiming verification.
2. Run Verify dual independent reviews:
   - specification conformance: delta scenarios, CI non-skip semantics, asset distribution, sentinel behavior, performance evidence;
   - code quality: shell/Python robustness, test independence, failure diagnostics, asset drift risks, maintainability.
3. Resolve every Critical/Important finding with minimal in-scope fix and rerun targeted plus affected full verification.
4. Append a memory entry to `.ai/memory/workflow.md` only after root cause and fix are verified:
   - symptom: source runner optimization was not propagated to installed targets;
   - solution: byte-sync runner/wrapper/tests, manifest entry, one full gate per assistant plus required sentinel.
5. Update proposal status to `待归档`, merge delta into `openspec/specs/shared-ai-workflow-infrastructure/spec.md`, update archive index, and run Archive gate only after Verify evidence is complete.
6. Do not push or trigger remote GitHub Actions without a separate explicit user authorization.

## SDD execution

Use `.codex/sdd/speed-up-ci-validation/`:

- `progress.md`: BASE commit, plan path, task statuses, review manifest IDs, fix rounds.
- `task-1-brief.md` / `task-1-report.md`: Tasks 1–2 as one sequential implementation responsibility.
- `task-2-brief.md` / `task-2-report.md`: Task 3 as one sequential implementation responsibility.
- `task-3-brief.md` / `task-3-report.md`: full verification evidence only.
- `review-unit-a.md` / `review-unit-b.md`: reviewer findings with fixed finding fields, unverified scope, residual risk.

Workers must not modify outside their assigned file sets. Reviews use fresh independent context and valid manifests. No parallel implementation because tasks share `test_install_ai_workflow.py`, asset byte-sync constraints, and sequential green-state dependencies.

## Self-review

- Every delta scenario maps to Task 1/2/3 implementation or Task 4/5 verification.
- No external push, deletion, migration, remote API, dependency addition, authentication, funds, or schema action is included.
- CI commands and failure semantics remain stricter than or equal to current requirements.
- The only new distributed runtime file is the existing zero-dependency Python runner; no third-party dependency is introduced.
- Fixed wall-clock time is evidence, not a pass/fail gate, to avoid GitHub runner nondeterminism.
- This plan introduces no choice, assumption, dependency, or scope absent from the confirmed specification; therefore it may proceed from Design to Build without a second confirmation.
