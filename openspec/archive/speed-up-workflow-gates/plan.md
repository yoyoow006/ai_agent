# 实现计划：speed-up-workflow-gates

## 目标与全局约束

- 目标 1：`--fast` 模式下，三组重检查（事实工具必需测试、Review manifest 必需测试、OpenSpec validate）在“命令 + core 实现 + 输入文件”指纹与上次实际执行 PASS 记录一致时透明沿用结果；任一变化、缓存异常或历史结果非 PASS 一律实际执行；FAIL 永不缓存；`--require-openspec`、默认全量与 `--archive-light` 完全不读写缓存。
- 目标 2：顶层契约套件默认通过仓库自带零依赖并行执行器运行，任一失败使退出码非零、失败明细完整、`... skipped` 行可被 wrapper 统计；`WORKFLOW_TEST_JOBS=1` 完整回退原 `python3 -B -m unittest -v scripts.tests.test_validate_workflow` 命令。
- 技术栈：bash（core/wrapper）、Python 3 标准库（runner、unittest）。禁止第三方依赖。
- 全局约束（逐字执行）：保护用户未提交修改；外部或破坏性动作（推送、PR、强推、删除未合并工作等）必须有明确授权；完成声明前必须现跑与风险相称的验证并读取退出结果；提交按可独立回滚的职责单元组织；不得改变 `--require-openspec` 实际执行语义与顶层 PASS/FAIL/SKIP 汇总口径。
- 性能验收（记录实测，不写为跨机器断言）：`--fast` 暖缓存 ≤5 秒（基线 23 秒）；本地默认全量门禁 ≤3 分钟（基线：契约模块单独 >8 分钟）。

## 任务 1：core 快速门禁指纹缓存（红→绿）

**Create/Modify/Test**

- Modify：`scripts/lib/validate-workflow-core.sh`
- Modify：`scripts/validate-workflow.sh`
- Test：`scripts/tests/test_validate_workflow.py`（新增 `FastValidationCacheTest(ValidateWorkflowContractTest)` 与 wrapper 缓存开关测试类）

**接口**

- 环境开关：`WORKFLOW_FAST_CACHE=1`。仅 wrapper 在 `fast_mode=1` 调用 core 时注入；core 默认关闭，任何其他模式不注入。
- 缓存目录：`.ai-local/validation-cache/`；文件 `<check-id>.cache`，内容恰好两行：第 1 行 64 位十六进制指纹，第 2 行 UTC ISO-8601 时间戳（`YYYY-MM-DDTHH:MM:SSZ`）。
- 检查 ID 与输入集合：
  - `project-facts-required-tests`：`scripts/lib/validate-workflow-core.sh`、`.ai/tools/project_facts.py`、`.ai/tools/tests/test_project_facts.py`、`.ai/tools/README.md`、`.ai/kb/projects/registry.json`、`.ai/kb/projects/README.md`
  - `review-manifest-required-tests`：`scripts/lib/validate-workflow-core.sh`、`.ai/tools/review_manifest.py`、`.ai/tools/tests/test_review_manifest.py`
  - `openspec-validate`：`scripts/lib/validate-workflow-core.sh`、`openspec/AGENTS.md`、`openspec/project.md`、`openspec/specs/` 下全部常规文件（排序后参与哈希）
- 指纹算法：`python3 -B -c` 内用 SHA-256 依次摄入“检查命令字符串 + 每个输入路径与文件内容”；任一文件读取失败摄入字面 `<missing>`（确定性，不中断执行）。
- 命中输出：`[PASS] <原检查名>（指纹 <前12位> 未变，沿用 <时间戳> 实际执行结果）`；仍计入 PASS。未命中输出与现状一致。
- `check_required_test` 增加 `return 0/1` 语义（现有调用方不受影响），供缓存只在 PASS 后写入。
- `print_external_commands` 白名单新增 `mkdir`（字典序置于 `mktemp` 之后）；不新增 `sha256sum`/`date`（指纹与时间戳均走已有 `python3 -B -c` 通道）。

**测试（先写，预期红）**

新增用例与断言：

1. `test_cache_hit_annotates_and_reuses`：`WORKFLOW_FAST_CACHE=1` 连跑两次 core；第一次两份必需测试缓存文件生成且输出无“沿用”；第二次两行输出均含 `指纹` 与 `沿用`，退出码 0。
2. `test_input_change_invalidates_only_affected_check`：首次缓存后向 `.ai/tools/project_facts.py` 追加注释再跑；事实工具行无“沿用”、Review manifest 行仍命中。
3. `test_failed_check_never_writes_cache`：用自定义 `python3` stub（`-B -c` 走真实 Python，其余退出 1）使必需测试 FAIL；断言 `[FAIL]`、core 退出非零且 `.ai-local/validation-cache/` 无对应缓存文件。
4. `test_corrupt_cache_reruns_execution`：写入垃圾内容到缓存文件再跑；输出无“沿用”仍 PASS，且缓存被合法新记录覆盖。
5. `test_cache_ignored_without_fast_env`：先带 env 生成缓存，再去掉 env 运行；输出无“沿用”，缓存文件保持原样（既不读也不写）。
6. `test_openspec_check_cached_when_cli_present`：stub `openspec` 退出 0；带 env 两次运行，第二次 OpenSpec 行含“沿用”；把 stub 改为退出 1 后删除缓存重跑，FAIL 且不写缓存。
7. wrapper 开关：复用归档测试的“stub core”布置，stub core 输出 `WORKFLOW_FAST_CACHE=<值>`；`--fast` 运行输出 `WORKFLOW_FAST_CACHE=1`，默认全量输出 `WORKFLOW_FAST_CACHE=0` 或无注入痕迹。

**命令与预期**

```bash
# 红：新用例失败（无沿用标注/无缓存文件/开关未接入）
python3 -B -m unittest -v \
  scripts.tests.test_validate_workflow.FastValidationCacheTest \
  scripts.tests.test_validate_workflow.WrapperFastCacheSwitchTest
# 绿：实现后同命令全部 PASS；随后
bash scripts/validate-workflow.sh --fast   # 两次，第二次重检查行含 沿用
```

## 任务 2：契约套件并行执行器与 wrapper 接入（红→绿）

**Create/Modify/Test**

- Create：`scripts/tests/run_validate_workflow_parallel.py`
- Modify：`scripts/validate-workflow.sh`（仅 `run_contract_suite` 函数体）
- Modify：`scripts/tests/test_validate_workflow.py`（新增 `ParallelContractRunnerTest`；`ArchiveLightGateTest._run_wrapper`/`_stage_wrapper_tree` 同步布置 runner 文件）

**接口**

- runner CLI：`python3 -B scripts/tests/run_validate_workflow_parallel.py [--module scripts.tests.test_validate_workflow] [--jobs N]`；默认 jobs=`WORKFLOW_TEST_JOBS` 或 `min(os.cpu_count(), 8)`；`--jobs 1` 在进程内按原顺序串行执行。
- runner 启动即把当前工作目录插入 `sys.path` 首位；按 loader 展开到叶子用例，逐用例分发（Linux 使用 fork 上下文；fork 不可用时进程内串行退化）。
- 每用例输出 `<test-id> ... ok|FAIL|ERROR|skipped`（skipped 附原因）；失败/错误明细块完整保留；末尾输出 `Ran N tests in <sec>s` 与 unittest 同款 `OK (skipped=k)` / `FAILED (failures=f, errors=e, skipped=s)` 汇总；退出码 0/1 与 unittest 语义一致。
- worker 异常/崩溃折算为该用例 ERROR 并保留 traceback；主进程按提交顺序确定性打印，禁止共享临时路径。
- wrapper：`WORKFLOW_TEST_JOBS=1` → 原命令原样执行；否则 → `python3 -B scripts/tests/run_validate_workflow_parallel.py`。保持 `run_contract_suite` 单一调用点。

**测试（先写，预期红）**

1. `test_mixed_results_propagate`：临时模块含 ok/FAIL/skipped 各 1；runner 退出非零，三类状态行齐全，汇总含 `FAILED (failures=1` 与 `skipped=1`，traceback 含失败用例名。
2. `test_skip_output_remains_parseable`：仅 ok+skipped；退出 0，输出含 `... skipped` 行（wrapper grep 兼容）与 `OK (skipped=1)`。
3. `test_worker_crash_becomes_error`：用例内 `os._exit(3)`；退出非零，该用例标 ERROR 且其余用例结果仍聚合。
4. `test_wrapper_uses_runner_by_default`：stub runner 写标记文件后退出 0；wrapper 默认运行后标记存在且输出 `[PASS] 工作流顶层契约测试`。
5. `test_wrapper_jobs_one_falls_back_to_unittest`：同 stub runner；`WORKFLOW_TEST_JOBS=1` 时标记不产生、sentinel 套件真实通过。
6. 既有回归：`ValidateWorkflowContractTest.test_profile_cannot_bypass_public_contract_suite` 与 `ArchiveLightGateTest` 全部保持原语义（布置树补 runner 文件）。

**命令与预期**

```bash
# 红：runner 不存在，新用例失败
python3 -B -m unittest -v \
  scripts.tests.test_validate_workflow.ParallelContractRunnerTest \
  scripts.tests.test_validate_workflow.ArchiveLightGateTest
# 绿：实现后同命令全 PASS
```

## 任务 3：综合回归与性能实测

**Modify/Test**

- Test：`scripts/tests/test_validate_workflow.py`（全部）、`.ai/tools/tests/*`（实际执行）
- Modify：`openspec/changes/speed-up-workflow-gates/tasks.md`（勾选 + 证据）

**命令与预期**

```bash
# 1) 契约套件（默认并行，目标 ≤3 分钟，记录真实耗时）
/usr/bin/time -f 'contract-suite %es' \
  python3 -B scripts/tests/run_validate_workflow_parallel.py
# 预期：88+ 个用例全部通过（含新增），退出码 0

# 2) fast 暖缓存（目标 ≤5 秒）
bash scripts/validate-workflow.sh --fast
bash scripts/validate-workflow.sh --fast
# 预期：第二次三处重检查含 沿用 标注，PASS=200 FAIL=0 SKIP=0

# 3) 严格门禁全绿（不读缓存）
bash scripts/validate-workflow.sh --require-openspec
# 预期：PASS/FAIL/SKIP 汇总 FAIL=0；OpenSpec 与必需测试实际执行
```

**性能证据格式（写入 tasks.md）**

```text
性能实测（环境：<主机/文件系统一句话>）：
- --fast 冷/暖：<冷秒数> / <暖秒数>（基线 23s）
- 契约套件串行/并行：<串行秒数> / <并行秒数>（基线 >8min）
```

## 任务 4：Build 内自查与状态推进

- 逐条对照 delta Scenario 自查；检查完整 diff（`git diff --stat`、`git diff --check`）。
- 按职责单元提交：
  1. `chore(openspec): speed-up-workflow-gates 四件套与实现计划`（Design 阶段）
  2. `feat(workflow): --fast 重检查输入指纹缓存`（任务 1）
  3. `feat(workflow): 契约套件零依赖并行执行器`（任务 2 + 测试基设）
  4. `test(workflow): 门禁提速实测证据与任务勾选`（任务 3）
- tasks 全勾、目标/回归全绿后，proposal 置`待验证`并提交；交 Verify 双阶段独立审查。

## 回滚与风险

- 任务 1/2 各自独立提交，可单独 revert；runner 是新增文件，回滚不影响现状语义。
- 缓存仅 `.ai-local`（Git 忽略），任何异常路径的兜底行为都是“重新实际执行”，不存在假绿通路。
- 并行暴露隐蔽共享状态时，`WORKFLOW_TEST_JOBS=1` 立即恢复原串行语义用于定位；修复方向是用例级隔离而非放宽断言。

## 计划自审（硬风险集合）

- 权限认证/资金账务：无。
- 数据库 Schema/迁移/数据回填：无。
- 数据删除/破坏性动作：无（仅新增本地缓存与临时测试产物）。
- 外部副作用：无推送/PR/远端操作；本地 worktree、feature 分支与最终 `--no-ff` 合回 main 已获用户 3A 明确授权。
- 新增未确认选择：缓存两行文本格式、`mkdir` 白名单条目、测试布置树补 runner 均为已确认 design（D2/D3/D5）与既有“外部命令清单单一来源”条款的必要展开，无范围外假设或依赖。

结论：未命中第二次确认硬风险集合，计划自审通过后连续进入 Build。
