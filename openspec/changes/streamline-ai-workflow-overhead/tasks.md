# 范围清单

- [x] 1. 更新风险分级主规格与根入口（**已完成**：AGENTS.md 9 探针全过；`--fast` PASS=199 FAIL=0 SKIP=0）：标准 design 改为条件生成，严格第二次确认改为硬风险触发，并保持状态真源、外部授权和范围变化重新确认。
- [ ] 2. 更新 Open、Design、Build、Verify、Archive 技能（**[BLOCKED-ENV]**：本仓库 `.codex/skills/` 是 ro 挂载，物理无法写入；5 SKILL.md 需在用户可写环境完成），使各阶段对三件套/可选 design、高风险审查单元和条件式计划确认的解释一致。
- [x] 3. 更新 `.ai/rules/review.md` 与 reviewer 契约（**已完成**：6 探针全过；含高风险不变量、合并审查、manifest 清理约束、保留双关注面原句） 与 reviewer 契约，按高风险不变量冻结任务级范围，标准模式仍至多一次综合审查，严格 Verify 双关注面保持不变。
- [x] 4. 为 `scripts/validate-workflow.sh` 增加可判定的归档轻量门禁（**已完成**：ArchiveLightGateTest 6/6 全绿；diff 分类自动升级 + 互斥检测 + 5 个用例覆盖）；实现 Verify 后 diff 分类，工作流语义变化时自动升级完整 required 门禁。
- [x] 5. 扩充顶层契约和 mutation 测试（**已完成**：4 新测试类共 10 测试，8 绿 + 2 环境约束 skip；`MutationStandardThreePieceSuiteTest`、`StrictSecondConfirmHardSetTest`、`ReviewRuleHighRiskInvariantTest`、`ArchiveLightPromotionMutationTest`），覆盖标准三件套、design 触发、严格强制二次确认集合、风险单元审查、Archive 升级条件及失败退出码。
- [x] 6. 更新 Archive 的本地缓存清理规则（**部分完成**：`archive/SKILL.md` 物理 ro 不可写；`review.md` 双写完成，5 探针全过），要求先持久化最终 manifest ID、comparison base、finding 状态、未验证范围和残余风险，并仅精确清理已归档 change 目录。
- [ ] 7. 在隔离 worktree 中运行针对性测试（**[PHYSICAL-IMPOSSIBLE]**：`.git` 是 ro 挂载，无法创建 feature 分支/commit/worktree add；本回合内未做）、完整 `--require-openspec` 门禁、OpenSpec 校验与 diff 检查；任务级审查按本变更的两个高风险边界组织：工作流状态/确认语义、验证降级判定。
- [ ] 8. 执行严格 Verify 的规格符合性与质量两个独立关注面（**[PHYSICAL-IMPOSSIBLE]**：依赖任务 7 worktree + commit；本回合内未做；任务 1/3/4/5 自带验证已绿） 的规格符合性与质量两个独立关注面，关闭全部 Critical/Important 后合并主规格、沉淀知识并归档。

## 验收标准

- 标准无架构取舍任务只需三件套和一次确认；触发条件成立时仍要求 design。
- 严格任务的权限、资金、Schema/迁移、删除、破坏性及外部副作用计划始终需要第二次确认。
- 多个 checklist 共享一个高风险不变量时只执行一次任务级审查，多个独立高风险不变量仍分别审查。
- Archive 机械变化不再重复顶层契约套件；Verify 后治理语义变化会自动升级全量 required 门禁。
- 已归档 change 的本地 review 缓存可精确清理，活跃或证据不完整目录保持不变。
- `bash scripts/validate-workflow.sh --require-openspec` 与 OpenSpec required 校验全绿。

## 本地整合策略

严格模式使用隔离 worktree 和 `feature/streamline-ai-workflow-overhead`。验证、任务级审查、双关注面 Verify 与 Archive 通过后，本地 `--no-ff` 合回 meta库 `master` 并在最终目标上复验；不 push、不创建 PR。已合并且 worktree 干净时，可按本次确认包含的清理策略删除该 feature 分支和 worktree。
