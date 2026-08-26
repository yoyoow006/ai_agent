# 优化 Open 需求理解与追问

模式: 严格
状态: 已归档

## Why

现有 `.codex/skills/open/SKILL.md` 与 `.claude/skills/open/SKILL.md` 只规定“范围不清且探索不能消除时询问用户”，但没有约束如何组织问题、哪些问题该问、用户回答如何落盘。模糊需求容易被助手拆成问题倾倒，也可能把代码可回答的事实推给用户；用户敲定的边界、术语和验收条件随后只留在对话中，四件套可能继续依赖助手猜测。

已学习外部 `grill-with-docs` 文档及其依赖的 `grilling`、`domain-modeling` 说明。可迁移的核心是：先区分事实与决策，按“当前已解锁的问题”分轮访谈，每个问题给出编号和推荐答案，用代码和既有文档回答事实，用具体场景 sharpen 模糊术语，并在共识形成时落盘。该技能的 `CONTEXT.md`/ADR 机制不适合直接引入本仓库，因为 OpenSpec 已是标准/严格变更的状态与需求真源，另建平行状态会制造漂移。

## What Changes

- 在双侧 `open` 技能中新增统一的需求理解契约：
  - 先从代码、规格、知识库和用户输入核对权威事实。
  - 只把会改变范围、风险、设计、验证或授权的决策性问题交给用户。
  - 模糊需求按轮次提出编号问题；每题说明证据、选项、推荐答案和影响，然后等待回答。
  - 依赖本轮回答的问题留到后续轮次，避免一次性问题倾倒。
  - 对过载术语引用权威来源并请求确定 canonical term。
  - 用户确认的目标、非目标、边界、约束、术语和验收标准写入四件套对应位置，而不是只留在对话中。
- 保留清晰请求的既有授权边界：事实足够且请求明确时不追加仪式化访谈。
- 不新增 `CONTEXT.md`、ADR 或其他平行需求状态。
- 同步修改 Codex/Claude 活动技能与可复用安装资产，保持字节一致。
- 为公共 validator 增加需求理解契约检查，并新增一个模糊需求压力场景。
- 归档时合并 `risk-tiered-ai-workflow` 主规格，保留 OpenSpec 作为唯一状态真源。

## Impact

- 受影响文件：
  - `.codex/skills/open/SKILL.md`
  - `.claude/skills/open/SKILL.md`
  - `scripts/ai-workflow-assets/codex/.codex/skills/open/SKILL.md`
  - `scripts/ai-workflow-assets/claude/.claude/skills/open/SKILL.md`
  - `scripts/lib/validate-workflow-core.sh`
  - `scripts/ai-workflow-assets/shared/scripts/lib/validate-workflow-core.sh`
  - `scripts/workflow-pressure-scenarios.md`
  - `scripts/ai-workflow-assets/shared/scripts/workflow-pressure-scenarios.md`
  - OpenSpec 变更与归档产物
- 用户影响：模糊需求会先被整理成少量可编号决策，助手不再把可查事实推给用户；确认后的理解会进入规格与任务，降低后续实现偏题风险。
- 兼容性：不改变快速/标准/严格分类、确认次数、状态路径、审查层数或 Git 底线；不把所有请求强制升级为访谈。
- 本地整合策略：本变更是工作流治理，按严格模式在确认四件套和独立计划后使用隔离 worktree 实施；不推送、不创建 PR、不执行破坏性 Git 操作。

## Verification Evidence

- Open 阶段事实核对：
  - `cmp` 确认当前 `.codex`、`.claude` 与安装资产中的 `open/SKILL.md` 四份字节一致。
  - `bash scripts/validate-workflow.sh` 的 core 部分确认现有 Open 快速豁免、标准单确认和双助手镜像检查均存在；当前完整命令还暴露本地忽略目录 `.codex/sdd/` 缺失导致的既有环境失败，实施前需在隔离工作区补齐本地占位后复验。
  - `openspec validate --all --strict --no-interactive` 当前为 7 passed、1 failed；失败项为既有 `git-remote-configuration` 主规格，与本变更目标文件无重叠，将在本变更验证中单独记录并避免混入修复。
- Build 验证与任务级审查：
  - `bash scripts/validate-workflow.sh` → `PASS=171 FAIL=0 SKIP=0`。
  - `bash scripts/validate-workflow.sh --require-openspec` → `PASS=171 FAIL=0 SKIP=0`，OpenSpec 检查未 SKIP。
  - `openspec validate improve-open-requirement-discovery --strict --no-interactive` → valid。
  - `python3 -B -m unittest scripts.tests.test_install_ai_workflow.PortableAssetContentTests.test_reusable_assets_are_byte_synchronized_with_active_sources` → 1 test OK。
  - `python3 -B -m unittest scripts.tests.test_validate_workflow` → 79 tests OK。
  - 四份 Open 技能、两份 validator、两份压力场景文件均字节一致；`git diff --check` 通过；无 `CONTEXT.md`/ADR 平行状态。
  - 任务级审查 manifest `97a636be…` 先发现绿色复测 Important 阻断；修正真实仓库前提并完成 3/3 结构化复测后，同 ID 差异复审将 `GREEN-RETEST-GATE-001` 置为 resolved，且判定无需第四轮技能文字修复。
- Verify 质量修复复验：
  - 独立质量审查发现结构门禁与范围 diff 两个 Important、两个 Minor；已按最小修复补齐清晰请求与 R 场景 token、允许“路径或用户输入”证据、修正 R 为真实仓库前提并清理 EOF 空行。
  - 两个 `/tmp` 临时副本 mutation 分别同步删除清晰请求直行句、仅删除 R 场景，公共 core 均按预期非 0 且输出对应 FAIL。
  - `python3 -B -m unittest scripts.tests.test_validate_workflow` → 79 tests OK；`python3 -B -m unittest ...test_reusable_assets_are_byte_synchronized_with_active_sources` → 1 test OK。
  - `bash scripts/validate-workflow.sh --require-openspec` → `PASS=171 FAIL=0 SKIP=0`；merge-base 到工作区的 `git diff --check` 通过；新增用户输入证据压力场景 PASS。
  - 主会话终验在 `ea6fc79` 亲自复跑：79 项 workflow 单测 OK、required wrapper `PASS=171 FAIL=0 SKIP=0`、资产同步单测 OK、merge-base 到 HEAD 的 `git diff --check` 通过，最新质量修复 manifest 有效。
