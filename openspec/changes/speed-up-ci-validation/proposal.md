# 加速 GitHub Actions validate

模式: 严格
状态: 待验证

## Why

GitHub Actions 近期运行显示 validate 的主要瓶颈不是 checkout、Node 或 OpenSpec 安装，而是安装器套件：

- 成功运行 `33704385709` 总耗时 1498 秒：`Validate workflow` 318 秒、`Install workflow installer tests` 1109 秒、Bash 安装器测试 58 秒。
- 最新运行 `34691053891` 总耗时 1582 秒并在安装器步骤失败：`Validate workflow` 已降至 196 秒，但 `Install workflow installer tests` 仍耗时 1375 秒。
- 源仓 `scripts/validate-workflow.sh` 已改用零依赖并行执行器；随包资产 `scripts/ai-workflow-assets/shared/scripts/validate-workflow.sh` 仍调用串行 unittest，且资产 manifest 不含 `scripts/tests/run_validate_workflow_parallel.py`。
- `scripts/tests/test_install_ai_workflow.py` 的安装目标集成用例对每个 assistant 额外执行串行契约套件、公共门禁与 required 门禁，导致同一真实契约套件重复多次。

因此需要把已完成的并行执行能力同步到安装资产，并移除安装器集成测试中不提供新覆盖的重复完整门禁；不得通过跳过测试、缓存 PASS 结果或降低断言来换取速度。

## What Changes

- 将零依赖并行契约执行器纳入 shared 安装资产与 `manifest.json`，并使随包 wrapper 与源仓 wrapper 保持同一并行调用语义。
- 让 wrapper 在契约套件成功时透明输出实际用例数，保留失败明细、设计性跳过明细和顶层 PASS/FAIL/SKIP 汇总语义。
- 重构安装目标集成测试：
  - 每个 assistant 保留一次真实完整公共门禁，仍实际执行全部随包契约用例、工具用例，并校验用例数与允许的 skip 原因。
  - required 缺少 OpenSpec CLI 的失败路径改用小型 sentinel 契约套件探针验证：证明 core 失败后 wrapper 仍实际调用契约套件且失败传播，不再重复执行 188 个真实用例。
  - 保留资产落位、幂等安装、Git 状态不变等既有断言。
- 保持 CI 必跑步骤与失败语义不变：源仓 required 门禁、`scripts.tests.test_install_ai_workflow`、`scripts.tests.test_install_workflow` 均必须实际运行，任一失败使任务失败。
- 补充回归守卫，防止随包 wrapper 回退为串行调用、执行器漏出 manifest，或安装器集成测试重新引入每个 assistant 多次完整契约套件的路径。

## Impact

- 修改：`scripts/validate-workflow.sh`、`scripts/tests/test_validate_workflow.py`、`scripts/tests/test_install_ai_workflow.py`、`scripts/ai-workflow-assets/shared/scripts/validate-workflow.sh`、`scripts/ai-workflow-assets/shared/scripts/tests/run_validate_workflow_parallel.py`（新增）、`scripts/ai-workflow-assets/shared/scripts/tests/test_validate_workflow.py`、`scripts/ai-workflow-assets/manifest.json`、`openspec/specs/shared-ai-workflow-infrastructure/spec.md`（归档时合并）。
- 可能修改：`.github/workflows/validate.yml` 仅在需要补充超时或防排队治理时；本变更不以拆分为多个 job 作为主要提速手段。
- 不改：OpenSpec CLI 版本、公共门禁状态口径、`--fast` 指纹缓存语义、安装器冲突/回滚行为、业务项目运行时代码、外部 API 或数据库。
- 风险：并行度受 CI CPU 与 I/O 影响，不能承诺固定墙钟时间； sentinel 探针必须证明 required 路径没有跳过契约套件。所有优化都以实际运行全部真实套件或等价 fail-closed 探针为边界，不得引入测试专用后门。

## 用户已确认决策

- 2026-09-12：用户确认按严格模式创建本变更方案，并接受先优化安装器测试瓶颈而非只缓存 checkout/npm 小步骤。
