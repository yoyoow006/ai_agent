# 范围清单

- [x] 1. 更新风险分级主规格与根入口（**已完成**：AGENTS.md 9 探针全过；`--fast` PASS=199 FAIL=0 SKIP=0）：标准 design 改为条件生成，严格第二次确认改为硬风险触发，并保持状态真源、外部授权和范围变化重新确认。
- [x] 2. 更新 Open、Design、Build、Verify、Archive 技能（**已完成**：codex + claude 双套镜像同步，`mirror_equal` 5 项全绿；`--fast` PASS=199 FAIL=0 SKIP=0），使各阶段对三件套/可选 design、高风险审查单元和条件式计划确认的解释一致。
- [x] 3. 更新 `.ai/rules/review.md` 与 reviewer 契约（**已完成**：6 探针全过；含高风险不变量、合并审查、manifest 清理约束、保留双关注面原句） 与 reviewer 契约，按高风险不变量冻结任务级范围，标准模式仍至多一次综合审查，严格 Verify 双关注面保持不变。
- [x] 4. 为 `scripts/validate-workflow.sh` 增加可判定的归档轻量门禁（**已完成**：ArchiveLightGateTest 8/8 全绿；diff 分类自动升级 + 互斥检测 + git 缺失 fail-closed + run_contract_suite 收敛）；实现 Verify 后 diff 分类，工作流语义变化时自动升级完整 required 门禁。
- [x] 5. 扩充顶层契约和 mutation 测试（**已完成**：17 新测试，17 绿；`MutationStandardThreePieceSuiteTest` 3、`StrictSecondConfirmHardSetTest` 3、`ReviewRuleHighRiskInvariantTest` 2、`ArchiveLightPromotionMutationTest` 2、`ArchiveLightGateTest` 7 + 1 新回归），覆盖标准三件套、design 触发、严格强制二次确认集合、风险单元审查、Archive 升级条件及失败退出码。
- [x] 6. 更新 Archive 的本地缓存清理规则（**已完成**：archive SKILL.md + .ai/rules/review.md 双写，`mirror_equal` 通过），要求先持久化最终 manifest ID、comparison base、finding 状态、未验证范围和残余风险，并仅精确清理已归档 change 目录。
- [x] 7. 在隔离 worktree 中运行针对性测试（**已完成**：feature/streamline-ai-workflow-overhead 分支；fast + 任务级自检全绿）；完整 `--require-openspec` 门禁（PASS=200 FAIL=0 SKIP=0）、OpenSpec 校验与 diff 检查（11/11）；任务级审查按本变更的两个高风险边界组织：工作流状态/确认语义、验证降级判定。
- [x] 8. 执行严格 Verify 的规格符合性与质量两个独立关注面（**已完成**：阶段 1 PASS / 阶段 2 FAIL（5 finding，2 Important F-Q1/F-Q2）/ delta 复审 PASS）；F-Q1/F-Q2 已修复并新增 2 个回归测试，3 个 Low 保持 open accepted-risk。关闭全部 Critical/Important 后合并主规格、沉淀知识并归档。

## 最终审查证据（持久化在 OpenSpec 归档文件中）

- **最终 manifest ID**：`626feb7fdee4698f0e68a36299d3f4dd96a2fb85bb138bb8ca9ea27e2f519f68`（重冻于 commit `08dcbb7` 后）
  - 上一次 manifest：`621e7a3569a9b60b9b8bcaa127e2b2452a1d0444c5def94d8dbb95589dc9ed54`（阶段 1+2 起点）
- **comparison base**：`fa0f940`（merge: validator-fail-closed-backport — 校验器 fail-closed 加固回流自 meta 库）
- **finding 状态**：
  - 阶段 1（规格符合性）：7 个 finding，全部 `not-an-issue`
  - 阶段 2（代码质量）：5 个 finding（F-Q1 resolved / F-Q2 resolved / F-Q3 open accepted-risk 维护性 / F-Q4 open accepted-risk 文档 / F-Q5 open accepted-risk 边界）
  - delta 复审（F-Q1/F-Q2 修复）：4 个 finding，全部 `resolved` + 1 个 `not-an-issue`（pre-push 直接消费者）
  - **Critical/Important 计数**：0 open / 0 accepted
- **未验证范围**：
  - F-Q3/F-Q4/F-Q5（Low 维护性 / 文档漂移 / CLI 边界）未实现修复——按用户决定保持 open accepted-risk
  - 阶段 2 reviewer 标的"macOS /bin/bash 3.2 端到端实证"未在本变更内复跑（沿用 validator-fail-closed-backport 已建立的 bash 3.2 编译实证；本变更使用 `${archive_files[@]+"${archive_files[@]}"}` 仓库既有空数组守卫惯用法）
  - F-Q2 fail-closed 仅检查 `command -v git`，未校验 git 是否能正常读写 repo（worktree 损坏 / git 对象权限错误仍会静默退化到 git diff 段）——属 stage 2 Low 范畴保持 open
- **残余风险**：
  - 三个 Low accepted-risk（维护性 / 文档漂移 / CLI 边界）由 `.ai/rules/review.md` 台账记录；未来修改 ArchiveLightGateTest 时需双写 fixture（`_run_wrapper` 与 `_stage_wrapper_tree`）
  - `--archive-files` 后接 `--` 起头 path 会被静默截断——本仓库工作流文件命名约定不以 `--` 开头
  - 已确认范围内无 Critical；F-Q1/F-Q2 关闭后即可进入 Archive

## 验收标准

- 标准无架构取舍任务只需三件套和一次确认；触发条件成立时仍要求 design。
- 严格任务的权限、资金、Schema/迁移、删除、破坏性及外部副作用计划始终需要第二次确认。
- 多个 checklist 共享一个高风险不变量时只执行一次任务级审查，多个独立高风险不变量仍分别审查。
- Archive 机械变化不再重复顶层契约套件；Verify 后治理语义变化会自动升级全量 required 门禁。
- 已归档 change 的本地 review 缓存可精确清理，活跃或证据不完整目录保持不变。
- `bash scripts/validate-workflow.sh --require-openspec` 与 OpenSpec required 校验全绿。

## 本地整合策略

严格模式使用隔离 worktree 和 `feature/streamline-ai-workflow-overhead`。验证、任务级审查、双关注面 Verify 与 Archive 通过后，本地 `--no-ff` 合回 meta库 `master` 并在最终目标上复验；不 push、不创建 PR。已合并且 worktree 干净时，可按本次确认包含的清理策略删除该 feature 分支和 worktree。
