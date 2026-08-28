# 设计——取消路径、CI 门禁与镜像覆盖

## 关键决策

### D1. 取消语义（依用户 2026-08-27 决策）

- `已取消`是**双模式共用的异常终态**，不插入前进路径：标准态列变为 6、严格态列变为 9，但前进状态机不变，只在门禁文本中增加"任一`已归档`前状态可经用户决定转`已取消`"。
- 触发权限对齐 `accepted-risk` 哲学：只有用户明确决定才能取消；助手只能建议。
- 处置规则：proposal 置`状态: 已取消`＋`取消原因:`一行 → 目录移入 `openspec/archive/` → delta 永不合并 → 分支/worktree/未提交修改由用户明示（删除仍走独立授权）。探针证据：`openspec validate --all --strict` 不扫描 `archive/`（垃圾归档 EXIT=0，对照组垃圾活跃变更 EXIT=1），残缺四件套不会破坏门禁。
- 不改 `open` 技能：恢复逻辑只读 `openspec/changes/`，取消变更移出后天然不命中；不新增`openspec/cancelled/`目录。
- 正文真源放 `openspec/AGENTS.md`（artifact 格式权威）；`archive` 技能增加执行步骤小节；入口总纲与 `kb/overview.md` 只加最小提示，不复制完整规则。

### D2. CI（依用户 2026-08-27 决策：仅本仓库）

- 文件 `.github/workflows/validate.yml`：触发 `push`（main）+ `pull_request` + `workflow_dispatch`（便于手动复跑）。
- 步骤：`actions/checkout@v4`（`fetch-depth: 0`，保证 review manifest 测试用到的 merge-base 语义在浅克隆下无隐患）、`actions/setup-node@v4` + `npm install -g @fission-ai/openspec@1.3.1`、`bash scripts/validate-workflow.sh --require-openspec`。
- 单命令入口即覆盖结构、mutation、事实工具、manifest 测试、OpenSpec 严格校验与契约测试（`.ai/tools/README.md:84` 契约），不额外重复 unittest 命令。
- 版本钉住 `1.3.1`（与本机一致，结果可复现）；升级走后续变更。
- 不入 `manifest.json`：安装器对非 GitHub 托管目标是死文件；目标项目需要时另行评估。
- `.gitignore` 无 `.github` 规则，已核实无冲突。

### D3. 镜像归一化

- `verification` 双套字节相同 → 直接加入现有 `mirror_equal` 循环。
- `parallel-agents`、`systematic-debugging`、`writing-skills` 的合法差异经全量 diff 证实恰为两类：
  1. 路径前缀：`.claude/skills/` ↔ `.codex/skills/`（10 处）；
  2. Codex 适配注记：parallel-agents 第 8 行 `> **Codex 执行环境：** …` 引用行及其后空行。
- 实现 `mirror_normalized`：claude 侧 `sed 's@\.claude/skills/@.codex/skills/@g'`；两侧删除 `^> \*\*Codex 执行环境` 行并压缩连续空行（`cat -s`）后 `diff`。豁免规则在校验器内显式写成注释表，未来新增适配注记必须同步登记，否则校验失败——这是有意的：新差异应当显式化。
- 镜像循环从 9 技能扩至 13，`contains_all` 文档检查（core 453 行）同步加`已取消`。

### D4. 实体树与资产树同步范围

需同步的资产副本（`scripts/ai-workflow-assets/`）：`claude/CLAUDE.md`、`codex/AGENTS.md`、`shared/openspec/AGENTS.md`、`shared/.ai/kb/overview.md`、`shared/.claude` 与 `codex` 两侧 `archive` 技能、`shared/scripts/lib/validate-workflow-core.sh`、`shared/openspec/specs/risk-tiered-ai-workflow/spec.md` 与 `shared-ai-workflow-infrastructure/spec.md`（主规格资产副本随 Archive 合并同时更新，避免资产超前或滞后于真源）。校验器两副本必须字节一致；其余文件按各自措辞差异（"本仓库/当前项目"）做语义等价同步。

## 替代方案

- 取消留在 `changes/` 标记：会持续导致 `--strict` 失败，阻断严格门禁，否决。
- 新增 `openspec/cancelled/`：语义最清晰但结构扩散，P1 否决，保留为未来选项。
- 重构 13 技能共享正文到 `.ai/` 单源：消除镜像需求但属大重构（审计 P3），本变更不做，归一化比对已封住漂移风险。
- CI 用 pre-push hook / husky 等本地钩子：不覆盖 PR 与他机推送，否决。

## 风险与边界

- 状态枚举文字散布约 12 份文件——遗漏即校验失败，属安全失败（fail closed）；构建时以校验器为唯一收敛标准。
- CI 首跑结果只能在推送后观察（推送属外部授权，单独执行）；本地用 yaml 解析 + `bash -n` + 等价命令全绿作为前置证据。
- `mirror_normalized` 的空行压缩可能掩盖真正的空行差异——可接受：空行差异无语义，换取规则简单。
- mutation 测试未新增取消路径注入项（P2 范围），本变更靠文档检查 + 状态合法组合校验守护。

## 验证策略

- 每个 `已取消`文本落点后现跑 `bash scripts/validate-workflow.sh`，全 `[PASS]`。
- 镜像规则生效性：临时向任一技能注入语义差异，确认校验非零并指出该技能，随后还原（不提交注入）。
- CI 文件：`python3` yaml 安全解析 + 动作步骤与本地等价命令核对。
- 终验：`openspec validate add-cancel-state-ci-mirror --strict --no-interactive` + `bash scripts/validate-workflow.sh --require-openspec` + 两个 unittest 命令。
