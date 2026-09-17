# 范围清单

- [ ] 1. 更新风险分级主规格与根入口：标准 design 改为条件生成，严格第二次确认改为硬风险触发，并保持状态真源、外部授权和范围变化重新确认。
- [ ] 2. 更新 Open、Design、Build、Verify、Archive 技能，使各阶段对三件套/可选 design、高风险审查单元和条件式计划确认的解释一致。
- [ ] 3. 更新 `.ai/rules/review.md` 与 reviewer 契约，按高风险不变量冻结任务级范围，标准模式仍至多一次综合审查，严格 Verify 双关注面保持不变。
- [ ] 4. 为 `scripts/validate-workflow.sh` 增加可判定的归档轻量门禁；实现 Verify 后 diff 分类，工作流语义变化时自动升级完整 required 门禁。
- [ ] 5. 扩充顶层契约和 mutation 测试，覆盖标准三件套、design 触发、严格强制二次确认集合、风险单元审查、Archive 升级条件及失败退出码。
- [ ] 6. 更新 Archive 的本地缓存清理规则，要求先持久化最终 manifest ID、comparison base、finding 状态、未验证范围和残余风险，并仅精确清理已归档 change 目录。
- [ ] 7. 在隔离 worktree 中运行针对性测试、完整 `--require-openspec` 门禁、OpenSpec 校验与 diff 检查；任务级审查按本变更的两个高风险边界组织：工作流状态/确认语义、验证降级判定。
- [ ] 8. 执行严格 Verify 的规格符合性与质量两个独立关注面，关闭全部 Critical/Important 后合并主规格、沉淀知识并归档。
- [ ] 9. 同步流程口径文档与安装资产：更新 `CLAUDE.md`、README、使用介绍、共享 overview、阶段技能措辞、`scripts/ai-workflow-assets/` 内入口/技能/主规格/压力场景，消除标准固定四件套、严格固定双确认和归档后固定全量的旧口径。
- [ ] 10. 为 `business-terms` 先写失败测试：覆盖 registry 校验、包含/精确匹配、同义词、项目过滤、分页截断、零匹配、输入错误、路径边界和只读性。
- [ ] 11. 实现 `project_facts.py business-terms` 与 registry `business_terms` 契约，保持源仓库 registry 空白并同步安装资产副本。
- [ ] 12. 更新项目登记、事实工具、共享路由和 shared infrastructure 规格文档，说明目标项目如何登记业务词以及查询不证明源码事实的边界。

## 验收标准

- 标准无架构取舍任务只需三件套和一次确认；触发条件成立时仍要求 design。
- 严格任务的权限、资金、Schema/迁移、删除、破坏性及外部副作用计划始终需要第二次确认。
- 多个 checklist 共享一个高风险不变量时只执行一次任务级审查，多个独立高风险不变量仍分别审查。
- Archive 机械变化不再重复顶层契约套件；Verify 后治理语义变化会自动升级全量 required 门禁。
- 已归档 change 的本地 review 缓存可精确清理，活跃或证据不完整目录保持不变。
- Codex/Claude 入口、用户文档、阶段技能与安装资产均表达同一套三档流程、条件 design、硬风险二次确认和 archive-light 语义。
- 注入旧流程口径到任一双入口、关键文档或安装资产时，mutation/契约测试失败。
- `business-terms` 能按声明式 term/synonym 路由到项目卡与相对源码路径，支持过滤、精确/包含匹配和分页；不联网、不写入、不输出匹配正文。
- `bash scripts/validate-workflow.sh --require-openspec` 与 OpenSpec required 校验全绿。

## 本地整合策略

严格模式使用隔离 worktree 和 `feature/streamline-ai-workflow-overhead`。验证、任务级审查、双关注面 Verify 与 Archive 通过后，本地 `--no-ff` 合回 `main` 并在最终目标上复验；不 push，不创建 PR。已合并且 worktree 干净时，可按本次确认包含的清理策略删除该 feature 分支和 worktree。
