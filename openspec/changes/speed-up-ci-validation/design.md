# 设计——加速 GitHub Actions validate

## 关键决策

### D1. 提速不削弱门禁

- CI 仍必须实际执行源仓 `bash scripts/validate-workflow.sh --require-openspec`、完整安装器套件和 Bash 安装器契约套件。
- 不用 PR check 结论、GitHub cache 或本地 `.ai-local` 缓存替代 CI 中的真实测试。
- 不把 CI 拆成多个重复检出的 job：瓶颈是单步骤内重复完整契约套件，拆 job 只会增加准备开销并保留长路径。
- 验收关注可观察的执行结构：每个 assistant 的安装目标真实完整公共门禁恰好一次；required 缺 CLI 路径用 sentinel 探针证明契约套件仍被调用。

### D2. 随包资产与源仓执行语义对齐

- `scripts/tests/run_validate_workflow_parallel.py` 进入 shared 安装资产与 `manifest.json`。
- 随包 `scripts/validate-workflow.sh` 与源仓 wrapper 使用同一个 `run_contract_suite` 单一调用点：默认调用零依赖并行执行器，`WORKFLOW_TEST_JOBS=1` 时回退串行 unittest。
- 随包契约测试同步守护资产 manifest、wrapper 调用和外部命令白名单，避免源仓快而安装目标慢的分叉再次出现。

### D3. wrapper 成功输出补足可审计计数

- 并行执行器已输出 `Ran N tests`；wrapper 在成功路径解析并透出该计数，例如 `[PASS] 工作流顶层契约测试（N tests）`。
- 失败路径继续输出完整套件日志；设计性跳过仍在最终汇总前列明，顶层 `PASS=/d FAIL=/d SKIP=/d` 仍为末行。
- 安装器集成测试用该计数和允许的 skip 原因证明“真实完整套件已执行”，因此可以删除单独的串行 `python -m unittest` 冒烟调用。

### D4. 安装目标集成测试去重

现有一个用例对每个 assistant 执行三类昂贵路径：直接串行契约套件、公共门禁、required 门禁。后两者均通过 wrapper 再次执行完整契约套件。

新结构：

1. 每个 assistant 安装后运行一次真实 `bash scripts/validate-workflow.sh`，通过并行执行器覆盖全部随包契约用例；同时运行既有工具测试。
2. 对 required 缺少 OpenSpec CLI 的行为，复制已安装目标为独立探针目标，仅将契约测试模块替换为一个 sentinel 用例，再执行 `--require-openspec`。探针必须显示 core 的 OpenSpec 缺失 FAIL、sentinel 套件被实际调用且整体非零，从而保留 fail-closed 语义而不重复 188 个真实用例。
3. 保留安装后资产状态、幂等安装、Git identity 不变等断言；如断言依赖真实套件输出，则改从公共门禁透明输出解析。

### D5. 性能证据与回归边界

- 本地验证分别记录优化前后安装器套件墙钟时间，并保留失败/成功输出；GitHub 实际耗时以推送后的 Actions 运行为准，推送仍需独立授权。
- 预计主要收益来自两处：随包 wrapper 从串行切到并行；每个 assistant 从多份完整真实契约套件降为一份。
- 不把固定分钟数作为唯一硬门禁，避免 GitHub CPU 波动造成假红；结构守卫必须能检出执行器漏分发、wrapper 串行回退和重复完整门禁调用。

## 替代方案

- 只缓存 checkout/npm：三者合计不到 10 秒，对 25 分钟级瓶颈无效，否决。
- 将 CI 拆成多个 job 并行：重复 checkout/setup，且长安装器测试仍在关键路径，收益有限，否决。
- 直接跳过安装目标 required 探针：无法证明 core 失败后契约套件仍被调用，削弱 fail-closed 覆盖，否决。
- 给 wrapper 增加测试专用跳过参数：会制造公共门禁后门，否决。
- 用 GitHub cache 缓存测试结果：输入指纹难以覆盖测试代码语义与运行环境，且违背 CI 必须现跑套件的治理要求，否决。

## 风险与边界

- 并行测试可能受 CPU 争抢影响；保留 `WORKFLOW_TEST_JOBS=1` 回退，并用 GitHub 实际运行确认稳定性。
- sentinel 探针若实现不当可能只验证退出码而不证明套件被调用；设计要求 sentinel 输出唯一标记并由断言捕获。
- 资产 manifest 与物理文件必须严格一致；新增执行器漏入 manifest 或漏复制均会导致安装器契约测试失败。
- 本变更不处理业务运行时、OpenSpec CLI 升级或外部发布动作。

