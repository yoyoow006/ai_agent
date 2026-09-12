# 设计：加速工作流校验门禁

## D1 缓存只进入 fast 分层

`shared-ai-workflow-infrastructure` 主规格明确要求“严格 Verify/Archive 使用的门禁 SHALL 能要求 OpenSpec CLI 和全部必需测试实际执行”。因此缓存只允许出现在 `--fast`；`--require-openspec` 与默认全量模式既不读也不写缓存。这条边界使标准 Verify 提速，同时保持严格终验与 Archive 全量证据不动。

## D2 指纹输入集合

指纹 = 检查命令 + core 校验器版本（`validate-workflow-core.sh` 内容）+ 输入文件内容的确定性哈希。初始输入集合：

- 事实工具必需测试：`.ai/tools/project_facts.py`、`.ai/tools/tests/test_project_facts.py`、`.ai/tools/README.md`、`.ai/kb/projects/registry.json`、`.ai/kb/projects/README.md`；
- review manifest 必需测试：`.ai/tools/review_manifest.py`、`.ai/tools/tests/test_review_manifest.py`；
- OpenSpec validate：`openspec/AGENTS.md`、`openspec/project.md`、`openspec/specs/` 全部文件。

实现计划阶段以测试实际 import/读取的文件为准固化精确清单；集合中任一路径缺失即按未命中处理。

## D3 缓存存储与失效

- 位置：`.ai-local/cache/validation/<check-id>.txt`（`.ai-local` 已被 Git 忽略，不进入提交证据）。
- 格式：两行文本——指纹、上次实际执行的 UTC ISO-8601 时间；格式、哈希、解析任一异常按未命中处理并实际执行。
- 只缓存 PASS；FAIL/SKIP 永不写入。写入与读取只发生在 `--fast`。
- wrapper 已有 flock 串行化同一工作树的并发校验，缓存无跨进程写竞争；其他工作树各有独立 `.ai-local`。

## D4 输出口径

命中时输出形如 `[PASS] <检查名>（指纹 <前12位> 未变，沿用 <时间> 实际执行结果）`；仍计入顶层 PASS，不新增第四种状态，不改变汇总行语义。未命中时与现状完全一致。

## D5 契约套件并行执行器

- 新增 `scripts/tests/run_validate_workflow_parallel.py`：标准库 `concurrent.futures`，按测试用例分发到 worker 进程，聚合通过/失败/错误/跳过与失败明细，退出码与 unittest 语义一致。
- 默认 `WORKFLOW_TEST_JOBS=min(CPU, 8)`；`WORKFLOW_TEST_JOBS=1` 走原 `python3 -B -m unittest -v` 串行路径，作为回归逃生阀。
- wrapper 的 `run_contract_suite` 保持单一调用点（mutation 守卫继续可检出），仅替换为执行器调用；`... skipped` 输出兼容 `render_contract_suite_skips` 解析。
- 用例已各自使用独立 `TemporaryDirectory` 夹具，无共享可变状态；执行器不得引入共享临时路径。
- 替代方案：pytest-xdist（违反零第三方依赖，拒绝）；bash 按类分片（类内仍串行且退出码聚合复杂，拒绝）；全量改写为 pytest（范围失控，拒绝）。

## D6 性能验收与风险

- 在验证环境实测并记录：`--fast` 暖缓存 ≤5 秒（当前 23 秒）；本地默认全量门禁 ≤3 分钟（当前 >8 分钟仅契约模块）。绝对秒数作为证据记录，不写成跨机器规格断言。
- 风险：并行暴露隐藏共享状态——用 `WORKFLOW_TEST_JOBS=1` 定位，必要时以用例级隔离修复；缓存被误当作归档证据——归档仍要求严格/全量门禁实际执行；慢文件系统（本机 fuseblk）放大夹具复制开销——并行收益可能高于估算，但验收以实测为准。
