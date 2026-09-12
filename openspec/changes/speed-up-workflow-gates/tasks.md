# 范围清单

- [x] 1. 为 core 实现 `--fast` 专用的输入指纹缓存框架，并接入事实工具必需测试、review manifest 必需测试、OpenSpec validate 三项重检查（**已完成**：`FastValidationCacheTest` 6 用例全绿；commit `dc1133f`）。
- [x] 2. 增加缓存 fail-closed 契约测试：输入文件变化、检查命令变化、core 版本变化、缓存缺失/损坏/格式非法一律重新实际执行；`--require-openspec` 与默认全量模式完全不读写缓存（**已完成**：输入变化选择性失效、FAIL 不写缓存、损坏重跑、无 env 不读写、stub openspec 失败不缓存、wrapper 开关 8 用例全绿）。
- [x] 3. 新增零依赖并行契约执行器并接入 wrapper `run_contract_suite` 单一调用点；默认 `min(CPU, 8)`，`WORKFLOW_TEST_JOBS=1` 回退原串行命令（**已完成**：`run_validate_workflow_parallel.py` fork-per-test 有界并行、worker 崩溃折算 ERROR、wrapper 显式 `--module`；commit `64edcf4`）。
- [x] 4. 扩充并行安全与汇总兼容测试：任一用例失败/错误使套件非零、失败明细完整可见、`... skipped` 统计仍可被 `render_contract_suite_skips` 解析、串行回退行为与现状一致（**已完成**：`ParallelContractRunnerTest` 5 用例 + 归档门禁 8 用例回归全绿；跳过原因内联保持 grep 兼容）。
- [x] 5. 在验证环境实测并记录性能证据：`--fast` 暖缓存 ≤5 秒、本地默认全量门禁 ≤3 分钟；对照变更前 23 秒 / >8 分钟基线写入 tasks（**已完成**，见下）。
- [ ] 6. 合并 delta 到 `risk-tiered-ai-workflow` 与 `shared-ai-workflow-infrastructure` 主规格，沉淀 `.ai/memory/workflow.md`（缓存边界、并行执行器、逃生阀）。
- [ ] 7. 严格 Verify 双阶段独立审查（规格符合性、代码质量）并按 `.ai/rules/review.md` 处置 finding；全绿后执行归档与本地 `--no-ff` 合回 `main` 复验。

## 性能实测（环境：Ubuntu 20.04 / fuseblk 慢速文件系统 / 8 并行 worker）

- `--fast` 冷/暖：**23.55s / 1.73s**（变更前基线 23s；暖缓存三处重检查全部带`指纹/沿用`透明标注）
- 契约套件：**181 用例并行 144.36s 全绿**（变更前同模块串行 >8 分钟仍未完成）
- 完整默认门禁：**173.65s，PASS=200 FAIL=0 SKIP=0**（目标 ≤3 分钟达标）
- 严格 `--require-openspec` 门禁：**186.55s，PASS=200 FAIL=0 SKIP=0**（输出 0 处指纹标注，缓存完全未读写）

## 验收标准

- `--fast` 在输入未变时输出透明的指纹沿用 PASS，且总计入 PASS；任一相关输入变化后必须重新实际执行。
- FAIL 结果永不产生缓存命中；缓存文件损坏不导致假绿或假红，一律实际执行。
- `--require-openspec` 与默认全量模式不读不写缓存，OpenSpec CLI 与必需测试实际执行。
- 契约套件默认并行执行，任一失败使门禁非零；`WORKFLOW_TEST_JOBS=1` 完整恢复串行语义。
- `bash scripts/validate-workflow.sh --require-openspec` 全绿；镜像、mutation、归档索引守卫不回退。
