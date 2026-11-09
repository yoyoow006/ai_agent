# 任务清单

- [x] 1.1 先红：`test_validate_workflow.py::test_core_requires_current_standard_verification_layers` 增补 `WORKFLOW_STANDARD_BASE` token 断言，运行确认红（core 锚点尚无该 token）。
- [x] 1.2 双树同步改 `.claude/skills/verify/SKILL.md` 与 `.codex/skills/verify/SKILL.md` 第 57 行：标准层调用改为 `WORKFLOW_STANDARD_BASE=<基线> bash scripts/validate-workflow.sh --standard`，注明基线取值（上一全量验证通过的提交，如上一变更归档提交，或已通过全量验证的本轮构建起点）、不确定时不传保持全量、升级 required 时不适用。
- [x] 1.3 core 锚点 `validate-workflow-core.sh` 的 "Verify 标准分层" `contains_all` 行增补 `WORKFLOW_STANDARD_BASE` token；同步镜像 `scripts/ai-workflow-assets/shared/scripts/lib/validate-workflow-core.sh` 与 `scripts/ai-workflow-assets/shared/scripts/tests/test_validate_workflow.py`（cmp 校验 SAME）。
- [x] 1.4 `.ai/kb/overview.md` 验证入口条目补接线事实一句。
- [x] 1.5 目标回归：`python3 -B -m pytest scripts/tests/test_validate_workflow.py -q` 全绿；required 层验证（后台）：`bash scripts/validate-workflow.sh --require-openspec`、`openspec validate verify-skill-standard-base-wiring --strict --no-interactive`、`git diff --check`。

## 本地整合策略

- 分支/worktree：主会话 feature 分支 `fix/verify-skill-standard-base-wiring`（基于 main）；无未提交修改冲突，不建 worktree。
- 提交边界：技能接线 + 锚点/测试 + kb 一次职责单元提交；镜像同步随同提交；默认不推送、不合并，整合方式由用户在 Verify/Archive 后裁定。
- 外部副作用授权：无外部副作用。

## Verify 综合审查终局记录（2026-11-09，标准完整流程）

- 最终审查记录：独立 reviewer 一次综合审查（manifest `c5331dbb`，初审）+ finding 处置差异复审（重冻 manifest `613ae372a6f9621bef05a3c0cc503123a779824f15b2448a7c24c794d3052002`，两次 verify 均 VALID）；复审确认 R-VSW-01/02/03/04 全部 resolved、无新问题、无 Critical/Important 遗留。终局 manifest 以复审 ID 为 lineage 冻结，finalize 证据另存 `.ai-local/reviews/verify-skill-standard-base-wiring/`。
- comparison base：main=37dc852（分支基线，repo-spec `.::main`）；实现链 e39dec1→3b522cc→cbf35c8（finding 修复单元）。
- finding 状态：4 findings，resolved=4、open=0、not-an-issue=0、accepted-risk=0。R-VSW-01 tasks 勾选滞后（Minor）、R-VSW-02 proposal 误写 MODIFIED（Minor）、R-VSW-03 基线例句理论未验证窗口（Minor，限定语修复）、R-VSW-04 打包技能副本漏同步（Important，主会话复审前发现：3b522cc 漏同步使安装目标拿不到接线；cbf35c8 cp 同步 + 字节同步契约转绿 + delta 补同步义务 + proposal Scope 补条目）。另记：任务 1.1 先红过程未留存独立提交（测试与实现同在 3b522cc），红性由 diff 推断（断言先于锚点 token 存在）。
- 未验证范围：reviewer 未独立重跑 required 门禁与安装器全套件（采信主会话证据并独立复核子集）；安装器全套件在本分支 1 failed/89 passed + 172 subtests——唯一失败 `test_manifest_modes_are_exact_and_match_files` 为 main 上预存 sharedRepository 环境失败（0o664），修复在未合并分支 fix/manifest-mode-assertion-env-robust（2c4d6ea，`git branch --contains` 独立核实），与本变更无关，两分支整合后消失。
- 残余风险：会话无视技能文本取值基线的流程执行风险（文本层已尽指引义务，wrapper 侧 diff 命中工作流资产自动回退全量兜底）；cbf35c8（技能+打包资产）后的完整契约套件已现跑全绿（230 passed + 277 subtests，rc=0），归档门禁将在终局 HEAD 以 required 重跑覆盖。
- 验证证据汇总：required 门禁 PASS=282 FAIL=0（3b522cc）、openspec strict valid、diff-check 净、裁剪/回退双探针符合预期（提供基线→pruned；不提供→run(未提供 WORKFLOW_STANDARD_BASE)）、字节同步契约 1 passed + 54 subtests、锚点镜像测试绿、双树与打包副本四组 cmp SAME、完整契约套件 230 passed（cbf35c8，10:08）。
