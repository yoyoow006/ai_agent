# 变更：对齐工作流语义并补齐业务上下文路由

模式: 严格
状态: 待归档

## Why

前序归档变更已经把标准三件套、严格硬风险二次确认、高风险实现单元审查和 Archive 轻量门禁落入部分入口、主规格与校验器，但收口检查发现这些语义没有覆盖全部消费者：Claude 入口、用户文档、共享 overview、部分阶段技能和便携安装资产仍保留旧口径；主规格中旧的“归档后全量/严格 Archive 永远 required”要求与新的 diff 分类升级要求并存；wrapper 的升级路径没有真正以 required 语义重跑 core，diff 失败还会被吞掉。

同时，通用项目 registry 只有项目、应用与源码搜索事实，缺少从业务词到项目卡和源码路径的声明式路由。目标项目安装后需要手工翻找上下文，而源仓库又不能携带目标项目业务事实。

## What Changes

- 修复 OpenSpec 变更身份：不再复用已归档的 `streamline-ai-workflow-overhead` 名称；本变更只修改仍冲突的验证分层 Requirement，并新增真正缺失的双运行时语义一致 Requirement。
- 将“标准三件套+条件 design、严格硬风险二次确认、高风险实现单元审查、archive-light 自动升级”同步到 Codex/Claude 入口、README、使用介绍、共享 overview、阶段技能、压力场景和便携安装资产。
- 修正主规格中旧 Archive 全量要求与新轻量升级要求之间的冲突，并同步安装资产规格副本。
- 加固 `--archive-light`：diff 分类在任何 Git/base/pathspec 错误上 fail-closed；命中语义变化时从本次 core 调用开始携带 `--require-openspec`，并继续运行顶层契约套件。
- 为声明式项目 registry 增加可选 `business_terms` 业务词路由，并提供只读 `business-terms` 查询：支持项目过滤、精确/包含匹配、同义词、分页和确定性输出；不输出匹配正文、不联网、不 clone、不写目标项目。
- 扩展 mutation/契约测试，覆盖双入口、用户文档、阶段技能、压力场景、源主规格与安装资产中的旧口径回归，以及 archive-light required 升级和 diff fail-closed。

## Impact

- 影响 meta库工作流治理：`AGENTS.md`、`CLAUDE.md`、README、使用介绍、`.codex/skills/`、`.claude/skills/`、`.ai/`、`scripts/`、OpenSpec 主规格与测试。
- 影响通用业务上下文层：`.ai/kb/projects/registry.json` 契约、`.ai/tools/project_facts.py`、事实工具测试、项目登记文档及对应安装资产。
- 不修改任何业务子仓库运行时代码、API、数据库 Schema 或部署配置。
- 工作流脚本行为会改变，属于严格模式；实现使用隔离 worktree，保护当前 meta库未提交修改。
- 本地整合建议：验证与独立审查通过后，在用户已确认的策略范围内本地 `--no-ff` 合回 `main` 并复验；不 push、不创建 PR、不删除未合并工作。

## Non-Goals

- 不新增第四种风险模式或新的状态真源。
- 不取消严格任务的规格确认、独立 Verify、OpenSpec required 校验或外部副作用授权。
- 不把 `.ai-local` 变成提交证据；归档后的持久证据仍位于 OpenSpec 归档文件。
- 不自动清理未知目录、活跃 review、未合并分支或包含未提交修改的 worktree。
- 不把 `/media/shitou/data2/ai-pms` 的具体业务事实、项目名、服务名、源码路径或文档搬入本仓库；源仓库 registry 继续保持空白，仅交付目标项目可自行登记的通用业务词路由能力。
