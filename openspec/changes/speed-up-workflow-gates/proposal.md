# 变更：加速工作流校验门禁

模式: 严格
状态: 构建中

## Why

实测瓶颈（本机 2026-09-12，`--fast` 全绿基线）：

- `--fast` 门禁 23 秒，其中 review manifest 必需测试 14.6 秒、OpenSpec validate 3.8 秒、事实工具必需测试 3.0 秒；其余约 190 项结构/镜像/mutation 检查合计仅约 2 秒。
- 顶层契约套件 `scripts/tests/test_validate_workflow.py` 共 88 个用例串行运行，单模块超过 8 分钟仍未完成；每个用例各自复制完整仓库夹具、初始化 Git 并运行 core。

现有 `--fast` 分层与 `--archive-light` 解决了“什么时候跑多少”，但没有解决“输入未变时重复实际执行”。标准 Verify 每次固定支付约 23 秒，本地全量门禁接近 10 分钟，验证成本与输入是否变化脱钩。

## What Changes

- `validate-workflow-core.sh` 在 `--fast` 模式为三组重检查（事实工具必需测试、review manifest 必需测试、OpenSpec validate）增加输入指纹等价缓存：指纹一致时透明沿用上次实际执行的 PASS 结果并标注来源；任一输入文件、检查命令或 core 实现变化即重新执行；FAIL 永不缓存；缓存缺失、格式或哈希异常一律按未命中处理。
- `--require-openspec` 与默认全量模式完全不读取、不写入该缓存；严格门禁“OpenSpec CLI 与全部必需测试实际执行”的语义不变。
- 新增零第三方依赖的契约套件并行执行器；wrapper 的 `run_contract_suite` 切换到该执行器。默认并行度为 `min(CPU, 8)`，`WORKFLOW_TEST_JOBS=1` 完整回退串行 unittest 语义；结果聚合并保持 unittest 退出码与输出兼容。
- 扩充契约测试：缓存命中沿用、输入变化重跑、FAIL 不缓存、缓存损坏 fail-closed 重跑、严格模式绕过缓存、并行失败传播、串行回退与输出汇总兼容。
- 性能目标（在验证环境实测记录）：`--fast` 暖缓存 ≤5 秒；本地默认全量门禁 ≤3 分钟。

## Impact

- 修改：`scripts/lib/validate-workflow-core.sh`、`scripts/validate-workflow.sh`、`scripts/tests/test_validate_workflow.py`、新增并行执行器；归档时合并 `risk-tiered-ai-workflow` 与 `shared-ai-workflow-infrastructure` 主规格并沉淀 `.ai/memory/workflow.md`。
- 不改变：`--require-openspec` 的实际执行语义、顶层 PASS/FAIL/SKIP 汇总口径、flock 并发锁、镜像一致性检查、mutation 覆盖与归档索引守卫。
- 本地整合策略：严格模式使用隔离 worktree 与 `feature/speed-up-workflow-gates` 分支；Verify/Archive 全绿后本地 `--no-ff` 合回 `main` 并在最终目标复验；不 push、不创建 PR、不删除未合并工作。

## Non-Goals

- 不缓存或跳过严格 `--require-openspec` 门禁的任何实际执行。
- 不引入 pytest、xdist 等第三方测试依赖。
- 不做 CI job 拆分、归档辅助脚本、决策默认值库（留作后续独立变更）。
- 不修改审查 manifest 双 verify 机制、archive-light 升级判定与技能正文。
