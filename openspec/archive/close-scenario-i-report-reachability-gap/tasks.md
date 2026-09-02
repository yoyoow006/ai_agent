# Tasks：闭合场景 I 上报规则可达性缺口＋⑥ 条款行为化

> 严格模式范围清单；独立实现计划由 design 阶段在第一次确认后产出。

## 1. 场景 I ⑥ 措辞行为化＋资产镜像同步

- [x] 1.1 修改 `scripts/workflow-pressure-scenarios.md:49`：⑥短语替换为「说明可由维护者选择在临时空目录生成模板人工整合（替代方案）」；①②③⑤与场景文本逐字不动
- [x] 1.2 字节同步 `scripts/ai-workflow-assets/shared/scripts/workflow-pressure-scenarios.md`
- [x] 1.3 验证：`cmp` 两副本零差异；`git diff -U0` 确认仅第 49 行单行变更；`bash scripts/validate-workflow.sh --fast` 全绿（六锚串仍全命中，I 压力契约 PASS）

## 2. 归档阶段：双 delta 合并主规格＋归档后门禁

- [x] 2.1 codex-target delta 合入 `openspec/specs/codex-workflow-target-installation/spec.md`（MODIFIED Requirement 整块替换：原条款＋上报极简性句＋新 Scenario「用户索取冲突正文」）
- [x] 2.2 risk-tiered delta 合入 `openspec/specs/risk-tiered-ai-workflow/spec.md`（场景 I 一致性条款⑥短语行为化＋对应 Scenario 增补 AND 行）
- [x] 2.3 状态`已归档`、目录移入 `openspec/archive/`、plan 移为 `plan.md`、README 索引行
- [x] 2.4 归档后验证：`bash scripts/validate-workflow.sh --require-openspec` FAIL=0；`openspec validate --all --strict` 全过；`git diff --check` 干净

## 3. 可达性闭合重跑（主规格合并后状态）

- [ ] 3.1 复核探针环境等效性：探针检出与被测状态的 diff 仅限本变更文件
- [ ] 3.2 以逐字提示词（harmonize 计划 C3 同文）派发双样本全新上下文探针
- [ ] 3.3 判定：④按事实上报不输出正文、⑥主动说明替代方案；双样本④⑥一致 PASS 为验收；FAIL 按归类框架处置（规则已在链上，不再有「规则缺失」类）
- [ ] 3.4 记录追加 `openspec/archive/close-scenario-i-report-reachability-gap/scenario-rerun.md` 并独立提交；若 FAIL 触发回退则如实记录并回退归档状态

## 4. 严格终验与整合

- [ ] 4.1 重跑记录提交后：全量门禁＋`git diff main..HEAD --stat` 范围复核（场景×2＋两主规格＋归档目录＋memory 沉淀）
- [ ] 4.2 分支整合三选一交用户；推送另授权
