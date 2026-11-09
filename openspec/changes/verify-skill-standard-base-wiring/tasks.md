# 任务清单

- [x] 1.1 先红：`test_validate_workflow.py::test_core_requires_current_standard_verification_layers` 增补 `WORKFLOW_STANDARD_BASE` token 断言，运行确认红（core 锚点尚无该 token）。
- [x] 1.2 双树同步改 `.claude/skills/verify/SKILL.md` 与 `.codex/skills/verify/SKILL.md` 第 57 行：标准层调用改为 `WORKFLOW_STANDARD_BASE=<基线> bash scripts/validate-workflow.sh --standard`，注明基线取值（上一全量验证通过的提交，如上一变更归档提交，或已通过全量验证的本轮构建起点）、不确定时不传保持全量、升级 required 时不适用。
- [x] 1.3 core 锚点 `validate-workflow-core.sh` 的 "Verify 标准分层" `contains_all` 行增补 `WORKFLOW_STANDARD_BASE` token；同步镜像 `scripts/ai-workflow-assets/shared/scripts/lib/validate-workflow-core.sh` 与 `scripts/ai-workflow-assets/shared/scripts/tests/test_validate_workflow.py`（cmp 校验 SAME）。
- [x] 1.4 `.ai/kb/overview.md` 验证入口条目补接线事实一句。
- [ ] 1.5 目标回归：`python3 -B -m pytest scripts/tests/test_validate_workflow.py -q` 全绿；required 层验证（后台）：`bash scripts/validate-workflow.sh --require-openspec`、`openspec validate verify-skill-standard-base-wiring --strict --no-interactive`、`git diff --check`。

## 本地整合策略

- 分支/worktree：主会话 feature 分支 `fix/verify-skill-standard-base-wiring`（基于 main）；无未提交修改冲突，不建 worktree。
- 提交边界：技能接线 + 锚点/测试 + kb 一次职责单元提交；镜像同步随同提交；默认不推送、不合并，整合方式由用户在 Verify/Archive 后裁定。
- 外部副作用授权：无外部副作用。
