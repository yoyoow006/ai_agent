# 系统架构总览（共享工作流）

## 工作流组成

- `AGENTS.md` / `CLAUDE.md`：双助手入口、风险路由、状态路径和共享底线。
- `.codex/README.md`：Codex 工具映射与 SDD 约定。
- `.codex/skills/` / `.claude/skills/`：助手特有的阶段技能和支撑技能。
- `.ai/`：助手共享的 kb（稳定事实）、memory（踩坑）、rules（路由）、prompts 与 tools；事实查询只读，登记草稿和审查终局证据仅向显式输出路径写出。
- `.codex/sdd/` / `.claude/sdd/`：仅在确需子代理时使用的本地草稿区，Git 忽略。
- `openspec/`：标准/严格变更的数据层，与 Claude 共享。
- `scripts/validate-workflow.sh`：结构、镜像、禁止规则和 mutation 回归校验；`--fast` 仅跑秒级 core（标准 Verify 分层），默认全量，严格恒 `--require-openspec` 且该参数必须转发 core（CLI 缺失即 FAIL，不得降为 SKIP/成功）；`--fast` 对三组重检查（事实工具/review manifest/OpenSpec validate）使用输入指纹等价缓存——命中时透明标注`指纹/沿用`仍计 PASS，任一输入/core/命令变化、缺失、损坏或最近执行非 PASS 一律实际重跑，FAIL/SKIP 清缓存，全量与 required 模式完全不读写缓存，冲突模式组合 fail-closed。默认契约套件经 `scripts/tests/run_validate_workflow_parallel.py` 有界并行（`min(CPU,8)`；`WORKFLOW_TEST_JOBS=1` 回退原 unittest 命令），执行器随安装资产分发并在成功行透出真实用例数；flock 串行化并发，`scripts/hooks/pre-push` 提供自愿启用的本地推送防护。core 另守卫：废弃工具名零残留（技能树/`.codex/README.md`/资产树 `*.md`/`*.toml`）、parallel-agents 注记现行工具名、归档索引与目录 1:1；wrapper 在汇总行前透传契约套件内部设计性跳过明细（不改顶层计数）。安装器集成回归对每个 assistant 仅执行一份真实完整公共门禁，required 缺 CLI 用独立一用例 sentinel 目标证明契约调用与失败传播。
- `projects/test-login/`：离线 Python 标准库登录与随机验证演示，不承载共享业务项目事实。
- Archive 默认运行 `--archive-light`；若 Verify 后发生工作流可执行文件、助手入口、技能语义、契约测试或治理规格变化，则按 diff 分类自动升级 `--require-openspec`。

本总览合并了原 Claude 风险摘要与 Codex 模块/底线信息；助手特有工具行为仍留在各自适配目录。

## 风险模式与状态

| 模式 | 适用边界 | 状态/产物 |
|---|---|---|
| 快速 | 仅维护已有事实的非运行时文本 | 无 OpenSpec；直接修改和针对性验证 |
| 标准 | 不改变助手门禁且不满足快速条件的任务，包含高风险业务 | 三件套＋条件 design；`待确认计划 → 构建中 → 待验证 → 待归档 → 已归档` |
| 严格 | 仅 AI 助手流程门禁语义变更自动触发 | 四件套＋独立计划；完整 8 态 |

按实际影响而非文件路径判定。业务高风险最高标准，用户明确要求更严格流程时可自愿升级；标准小任务排除认证、资金账务、Schema/迁移、删除、并发、跨服务/公开 API 和大重构，仍保留失败/回滚设计、运行时 TDD、风险相称测试、一次独立综合审查与 manifest、实际外部/破坏性操作授权。门禁包括模式路由、确认/授权、状态限制、审查、验证阻断、证据有效性、归档及校验/安装传播契约；保持这些契约的内部优化走标准，满足快速条件的事实维护走快速。影响未知先按标准探索，确认门禁变化后更新真源并等待严格所需确认。

proposal 的`模式:`、`状态:`和 tasks 勾选是断点真源。标准只确认一次；严格先确认四件套，独立计划仅在权限、资金、Schema/迁移、数据删除、破坏性动作、外部副作用或引入未确认选择等硬风险时请求第二次确认。快速不自动提交；标准默认 feature、条件 worktree、一次综合审查；严格默认隔离 worktree、按高风险实现单元审查和 Verify 双阶段审查。

`已取消`是用户明确决定的异常终态：目录移入 `openspec/archive/`、不合并 delta、不恢复；分支/worktree 处置由用户明示。

Open 在进入任一模式前先建立需求共识：代码、测试、OpenSpec、共享知识层和用户明示输入能回答的事实先自行核对；只把会改变目标、范围、风险、术语、约束、验收、验证或授权的问题交给用户。模糊需求按当前已解锁问题分轮编号提问，每题提供证据、选项、具体或条件式推荐与影响；确认后的理解落入实际 OpenSpec 产物，不创建平行需求状态。

## 不可削弱底线

- 保护用户修改；外部/破坏性动作单独授权。
- 范围变化或风险升级重新确认。
- 运行时行为/缺陷修复使用 TDD；纯文本使用内容和结构验证。
- 审查意见先验证；完成前现跑验证。
- 提交按可独立回滚职责组织。
- 创建或重置 Git 基线前必须扫描待入库正文；提交后才发现凭据时，需在授权下同时净化当前树和不可达历史，本地清理不替代外部轮换。

## Git 仓库基线

- 仓库以 `main` 为初始分支，并保留至少一个本地 parentless root commit；后续远程配置和网络操作由独立授权变更管理。
- 根锚定 `.gitignore` 保护 `.ai-local`、双侧 SDD、worktree、Python 缓存和 Claude 本地配置，不把本机状态纳入版本控制。
- `openspec/` 保留项目说明、artifact 约定、空基线目录和共享工作流主规格；初始化时只补缺失基线，不覆盖既有活跃变更。

## 事实查询与审查证据

- 项目事实以 `.ai/kb/projects/registry.json`、项目卡、可选直接依赖、业务词和验证声明为入口；`project_facts.py` 提供 project/server/workspace/business-terms 只读查询，只访问登记边界，不联网、不 clone、不写业务仓、不执行登记命令。业务词只路由到项目卡与相对源码路径，不证明源码当前语义；`verified_commit` 只说明证据基线与当前 HEAD 的机械关系，不证明当前任务通过。
- 验证证据复用遵循 [`verification-evidence.md`](verification-evidence.md)：代码基线、相关输入、命令、环境类别和覆盖范围等价时才可复用；FAIL、NOT_RUN、UNKNOWN 或身份缺失不得计为通过，当前变更完成声明仍必须新鲜验证。
- 标准与严格审查使用 `review_manifest.py freeze/verify/delta` 冻结 comparison base、Git 层级、未忽略 untracked 与内容身份；结论前范围变化必须按 `STALE` 停止。`finalize` 可在有效身份下写出终局说明，不代替审查或关闭 finding；写入受审范围后仍须执行陈旧检测。
- `project_registry.py render` 生成显式目录内的项目登记草稿，支持无应用的库模块及显式构建类型，默认保护全部已有输出；核对事实后人工合入真实 registry。`validate` 复用现有登记 schema 校验。
- `scripts/validate-workflow.sh --require-openspec` 要求 OpenSpec CLI 与仓库必需测试真实执行；严格终验还应独立运行 `openspec validate --all --strict --no-interactive`。
- 便携工作流可安装在非 Git 根目录；忽略规则校验在无根 `.git` 时使用目标 worktree 加临时外部 Git metadata，不在目标初始化 Git。
- 在不支持 `renameat2(..., RENAME_NOREPLACE)` 的 fuseblk 目标上，便携安装器会在首个新父目录事务处失败并回滚；经用户确认后，先创建完整空父目录集合（必须包含中间父目录），重建/复核 dry-run，再执行原安装器，不得手工复制文件或盲目重试。
- 项目内 CLI 可放在已忽略的 `.ai-local/tools/openspec` 并临时加入 `PATH`；不得为验证执行 `openspec init` 或 `openspec update`。
