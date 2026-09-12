# 范围清单

- [x] 1. 为 core 实现 `--fast` 专用的输入指纹缓存框架，并接入事实工具必需测试、review manifest 必需测试、OpenSpec validate 三项重检查（**已完成**：`FastValidationCacheTest` 6 用例全绿；commit `dc1133f`）。
- [x] 2. 增加缓存 fail-closed 契约测试：输入文件变化、检查命令变化、core 版本变化、缓存缺失/损坏/格式非法一律重新实际执行；`--require-openspec` 与默认全量模式完全不读写缓存（**已完成**：输入变化选择性失效、FAIL 不写缓存、损坏重跑、无 env 不读写、stub openspec 失败不缓存、wrapper 开关 8 用例全绿）。
- [x] 3. 新增零依赖并行契约执行器并接入 wrapper `run_contract_suite` 单一调用点；默认 `min(CPU, 8)`，`WORKFLOW_TEST_JOBS=1` 回退原串行命令（**已完成**：`run_validate_workflow_parallel.py` fork-per-test 有界并行、worker 崩溃折算 ERROR、wrapper 显式 `--module`；commit `64edcf4`）。
- [x] 4. 扩充并行安全与汇总兼容测试：任一用例失败/错误使套件非零、失败明细完整可见、`... skipped` 统计仍可被 `render_contract_suite_skips` 解析、串行回退行为与现状一致（**已完成**：`ParallelContractRunnerTest` 5 用例 + 归档门禁 8 用例回归全绿；跳过原因内联保持 grep 兼容）。
- [x] 5. 在验证环境实测并记录性能证据：`--fast` 暖缓存 ≤5 秒、本地默认全量门禁 ≤3 分钟；对照变更前 23 秒 / >8 分钟基线写入 tasks（**已完成**，见下；终验新鲜值为暖缓存 1.83s、契约套件 188/188 用例 146.15s、required 门禁 170.84s）。
- [ ] 6. 合并 delta 到 `risk-tiered-ai-workflow` 与 `shared-ai-workflow-infrastructure` 主规格，沉淀 `.ai/memory/workflow.md`（缓存边界、并行执行器、逃生阀）。
- [ ] 7. 严格 Verify 双阶段独立审查（规格符合性、代码质量）并按 `.ai/rules/review.md` 处置 finding；全绿后执行归档与本地 `--no-ff` 合回 `main` 复验。

## 性能实测（环境：Ubuntu 20.04 / fuseblk 慢速文件系统 / 8 并行 worker）

- `--fast` 冷/暖：**23.55s / 1.83s**（变更前基线 23s；暖缓存三处重检查全部带`指纹/沿用`透明标注，PASS=199 FAIL=0 SKIP=0）
- 契约套件：**188 用例并行 146.15s 全绿**（变更前同模块串行 >8 分钟仍未完成）
- 完整默认门禁：**173.65s，PASS=200 FAIL=0 SKIP=0**（目标 ≤3 分钟达标；输出 0 处指纹标注）
- 严格 `--require-openspec` 门禁终验：**170.84s，PASS=200 FAIL=0 SKIP=0**（输出 0 处指纹标注，缓存完全未读写）

## 最终审查证据（持久化在 OpenSpec 归档文件中）

- **最终 manifest ID**：`02714407ed6eb8dc235a3001680e669f007a899e4cd95b5a4ebdb33312d9712a`（full-3，HEAD `db99ff8`）
  - full-1 `69dbe33b729d191298020854028a55272af07f2348528a8de419d0d09b55f410`（阶段 1 起点，e35b47a）
  - full-2 `a5a8e2c145b0cb0d345c949fda7ef06844c33e8bddedd145fa8f64acd8a24395`（阶段 1 修复后，55e1747）
- **comparison base**：`b6bba03`（main：merge streamline-ai-workflow-overhead）
- **finding 状态**：
  - 阶段 1（规格符合性）：4 个 Important（SPEC-OPENSPEC-INPUT-OMITTED / SPEC-STRICT-CACHE-ENV-LEAK / SPEC-FAIL-STALE-CACHE / SPEC-MISSING-INPUT-CACHED），修复后 delta 复审全部 `resolved`
  - 阶段 1 delta 复审：0 新增 finding
  - 阶段 2（代码质量）：2 Important（CQ-CACHE-MODE-GUARD / CQ-PARALLEL-UNEXPECTED-SUCCESS）+ 1 Minor（CQ-CACHE-TEST-COVERAGE），修复后 delta 复审全部 `resolved`
  - **Critical/Important 计数：0 open / 0 accepted**
- **未验证范围**：
  - 未做 macOS Bash 3.2、非 Linux 无 fork、真实 CI 配额与真实 SIGTERM/SIGKILL 平台矩阵
  - OpenSpec CLI / Python 解释器版本漂移未纳入指纹（属声明边界外，由全量/严格门禁实际执行兜底）
  - reviewer 未重跑全量套件（采信主会话 188/188、146.15s 与各门禁新鲜证据）
- **残余风险**：
  - OpenSpec 指纹依赖维护者同步声明输入集合；CLI 未来引入未枚举输入时需扩展指纹
  - runner 无测试级超时（与原 unittest 行为一致）；子进程直写 OS 级 stdout 不按用例归档（当前套件均显式捕获）

## 验收标准

- `--fast` 在输入未变时输出透明的指纹沿用 PASS，且总计入 PASS；任一相关输入变化后必须重新实际执行。
- FAIL 结果永不产生缓存命中；缓存文件损坏不导致假绿或假红，一律实际执行。
- `--require-openspec` 与默认全量模式不读不写缓存，OpenSpec CLI 与必需测试实际执行。
- 契约套件默认并行执行，任一失败使门禁非零；`WORKFLOW_TEST_JOBS=1` 完整恢复串行语义。
- `bash scripts/validate-workflow.sh --require-openspec` 全绿；镜像、mutation、归档索引守卫不回退。
