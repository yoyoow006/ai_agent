# Tasks

- [x] 盘点现有 workflow events、metrics、OpenSpec 模板、归档索引解析和项目 registry 工具，冻结兼容边界。
- [x] 设计任务级 telemetry schema、CLI/查询入口和旧 metrics 兼容策略。
- [x] 修正 proposal 模板与生成器校验，补充错误格式回归测试。
- [x] 修正归档 README 模板/示例，补充缺失、悬空、重复索引测试。
- [x] 设计 manifest 最终化接口或记录策略，补充最终化后 stale 检测测试。
- [x] 实现项目登记生成/校验入口，覆盖 registry、项目卡、规则路由一致性测试。
- [x] 运行相关单元测试、`bash scripts/validate-workflow.sh --fast` 和 `bash scripts/validate-workflow.sh --archive-light`。
- [x] 完成 Verify 双阶段审查并记录未验证范围与残余风险。

## 本地整合策略

严格模式默认使用独立 feature 分支和 worktree；完成验证后保留分支，是否合并或推送另行授权。本任务不修改业务项目源码，不执行外部发布动作。

## 最终验证记录

- targeted tests：telemetry、manifest、项目登记和 OpenSpec 结构测试通过。
- workflow gates：`--fast` PASS=125、FAIL=0、SKIP=1；`--archive-light` PASS=125、FAIL=0、SKIP=1。
- accepted-risk：用户明确确认接受完整 `test_validate_workflow` 中 25 个与 `.claude`/`CLAUDE.md` 治理夹具相关的失败，以及 OpenSpec CLI 缺失导致的 SKIP，并授权继续归档合并。
