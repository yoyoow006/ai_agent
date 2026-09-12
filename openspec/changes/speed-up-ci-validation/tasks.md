# Tasks（范围清单——严格模式实现计划由 Design 阶段独立产出）

- [ ] 1. 建立红灯与结构守卫
  - 修改：`scripts/tests/test_validate_workflow.py`、`scripts/tests/test_install_ai_workflow.py`
  - 先加入能失败的守卫：资产 manifest 必含并行执行器、随包 wrapper 必须调用执行器、wrapper 成功路径必须透出用例数、安装器集成测试不得对同一 assistant 重复执行完整真实契约套件。
  - 验证：运行 targeted unittest，确认新守卫在当前实现上按预期失败。
- [ ] 2. 同步并行执行器到随包资产
  - 新增：`scripts/ai-workflow-assets/shared/scripts/tests/run_validate_workflow_parallel.py`
  - 修改：`scripts/ai-workflow-assets/manifest.json`、`scripts/ai-workflow-assets/shared/scripts/validate-workflow.sh`、`scripts/ai-workflow-assets/shared/scripts/tests/test_validate_workflow.py`
  - 保持 `WORKFLOW_TEST_JOBS=1` 回退、失败明细、skip 统计和单一调用点。
  - 验证：资产 manifest 测试与 targeted 契约测试通过。
- [ ] 3. 重构安装器集成测试
  - 修改：`scripts/tests/test_install_ai_workflow.py`
  - 每个 assistant 保留一次真实完整公共门禁；删除重复的直接串行契约冒烟与 required 真实套件重复执行。
  - 用复制目标＋sentinel 契约用例验证 required 缺 CLI 时 core 失败、契约调用发生且退出非零。
  - 保留资产清单、幂等安装、Git identity、工具测试和允许 skip 原因断言。
  - 验证：先运行安装器 targeted 用例，确认结构与输出断言通过。
- [ ] 4. 全量本地回归与耗时证据
  - 运行：`openspec validate speed-up-ci-validation --strict --no-interactive`
  - 运行：`bash scripts/validate-workflow.sh --require-openspec`
  - 运行：`python3 -B -m unittest -v scripts.tests.test_install_ai_workflow`
  - 运行：`python3 -B -m unittest -v scripts.tests.test_install_workflow`
  - 记录优化后安装器套件墙钟时间，并确认没有测试被跳过以换取速度。
- [ ] 5. 严格终验与归档准备
  - 执行任务级审查与 Verify 双阶段独立审查。
  - 检查完整 diff、OpenSpec delta、资产 manifest、CI 失败语义和知识沉淀。
  - 通过后将状态推进到`待归档`；推送或触发远端 Actions 仍需用户单独授权。

