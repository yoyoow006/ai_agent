# 范围清单

- [x] 1. 使用唯一 OpenSpec 变更身份，保留 base 已存在的精简 Requirements，只以 MODIFIED 替换冲突的验证分层规则，并新增双运行时语义一致与业务词路由 Requirements。
- [x] 2. 同步流程口径文档与安装资产：更新 `CLAUDE.md`、README、使用介绍、共享 overview、双侧阶段技能、压力场景、源主规格和 `scripts/ai-workflow-assets/`，消除标准固定四件套、严格固定双确认、机械任务审查和归档后固定全量旧口径。
- [x] 3. 为 `business-terms` 先写失败测试，再实现 registry `business_terms` 契约与只读查询；覆盖包含/精确匹配、同义词、项目过滤、分页、零匹配、非法声明、路径/symlink 边界和只读性。
- [x] 4. 加固 archive-light 自动升级：Git diff 分类错误 fail-closed；语义变化时 core 从调用开始收到 `--require-openspec` 并运行顶层契约套件；同步安装资产。
- [x] 5. 扩展语义同步与 archive-light 回归，覆盖源主规格、双入口、关键文档、阶段技能、压力场景和安装资产。
- [ ] 6. 在隔离 worktree 中运行事实工具、工作流契约、便携安装器、一键安装器、`--require-openspec`、OpenSpec strict 与 diff 检查。
- [ ] 7. 任务级审查按两个高风险单元执行：工作流语义/验证降级边界、业务词查询边界与只读性；处置全部 Critical/Important。
- [ ] 8. 执行严格 Verify 的规格符合性与代码质量两个独立关注面，关闭全部 Critical/Important 后合并主规格、沉淀知识并归档。

## 验收标准

- 活跃变更名不与归档目录冲突；delta 的 MODIFIED Requirement 在 base 主规格中有唯一替换目标，ADDED Requirement 在 base 主规格中不存在。
- Codex/Claude 入口、用户文档、阶段技能、压力场景、源主规格与安装资产均表达同一套三档流程、条件 design、硬风险二次确认、高风险实现单元审查和 archive-light 语义。
- 注入旧流程口径到任一双入口、关键文档、阶段技能、压力场景、源主规格或安装资产时，mutation/契约测试失败。
- Archive diff 分类错误非零退出；语义变化时 core 收到 `--require-openspec`，OpenSpec CLI 缺失时 promoted 路径非零。
- `business-terms` 能按声明式 term/synonym 路由到项目卡与相对源码路径，支持过滤、精确/包含匹配和分页；不联网、不写入、不输出匹配正文。
- `bash scripts/validate-workflow.sh --require-openspec` 与 OpenSpec required 校验全绿。

## 本地整合策略

严格模式使用隔离 worktree 和 `feature/align-workflow-semantics-and-business-context`。验证、任务级审查、双关注面 Verify 与 Archive 通过后，本地 `--no-ff` 合回 `main` 并在最终目标上复验；不 push，不创建 PR。已合并且 worktree 干净时，可按本次确认包含的清理策略删除该 feature 分支和 worktree。
