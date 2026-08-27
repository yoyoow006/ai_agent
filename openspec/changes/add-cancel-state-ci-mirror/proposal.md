# 取消路径、CI 门禁与镜像覆盖补全

模式: 严格
状态: 构建中

## Why

2026-08-27 只读审计发现三项治理缺口：

1. **状态机无中止路径**：标准 5 态/严格 8 态全部是前进态，无终态`已取消`。用户在`待确认规范`/`待确认计划`拒绝方案或中途放弃后，变更目录无任何文件定义处置规则，残留目录会被下次会话当作可恢复断点（open 技能要求从断点继续），形成僵尸状态。
2. **无 CI**：仓库远程为 GitHub（`github.com/yoyoow006/ai_agent`），但无 `.github/`；`validate-workflow.sh`（现 168 项）仅在 Verify/Archive 时由助手手动运行，推送/PR 阶段零自动回归防护。
3. **镜像守护有盲区**：`scripts/lib/validate-workflow-core.sh:504` 的镜像循环仅覆盖 9/13 技能，缺 `parallel-agents`、`systematic-debugging`、`verification`、`writing-skills`。现 diff 证实 4 技能当前无语义漂移（`verification` 双套字节相同；另 3 个仅差 `.claude/`↔`.codex/` 路径前缀与 parallel-agents 的 Codex 适配注记块），但未来分叉时校验器不会报警。

## What Changes

- **新增`已取消`终态**：任一`已归档`前状态可经用户明确决定进入`已取消`；助手可建议、不得自行取消。取消时 proposal 置`状态: 已取消`、记录取消原因、变更目录移入 `openspec/archive/`；delta 不合并主规格；分支/worktree/未提交修改的处置由用户在取消时明示，删除未合并工作仍需独立授权。探针已证实 `openspec validate --all --strict` 不扫描 `archive/`，残缺四件套移入后不破坏 `--require-openspec` 门禁。
- **新增 GitHub Actions CI**：push（main）与 pull_request 自动运行 `bash scripts/validate-workflow.sh --require-openspec`，预装 `@fission-ai/openspec@1.3.1`；任一 FAIL 使 CI 失败阻断合并。
- **镜像清单补至 13/13**：`verification` 直接镜像比对；`parallel-agents`、`systematic-debugging`、`writing-skills` 按「`.claude/skills/`→`.codex/skills/` 路径前缀改写 + 删除 `> **Codex 执行环境` 适配注记行 + 压缩空行」归一化后比对。
- **实体树与安装资产树同步**：治理入口、`openspec/AGENTS.md`、`.ai/kb/overview.md`、archive 技能（双运行时）、校验器 core、risk-tiered 主规格资产副本。

## 用户已确认决策

- 2026-08-27 提问轮：被取消变更移入 `openspec/archive/`（与完成归档靠 proposal 状态字段区分）。
- 2026-08-27 提问轮：CI 仅本仓库，不纳入 shared 安装资产，`manifest.json` 不变。

## Impact

- 修改：`CLAUDE.md`、`AGENTS.md`、`openspec/AGENTS.md`、`.ai/kb/overview.md`、`.claude/.codex` 两侧 `archive` 技能、`scripts/lib/validate-workflow-core.sh`（含 assets 副本）、上述文件的 `scripts/ai-workflow-assets/` 对应副本；新增 `.github/workflows/validate.yml`。
- 不改：安装器 `manifest.json`、`.gitignore`、`review_manifest.py`、`project_facts.py`、其余技能正文、`open` 技能（取消变更已移出 `changes/`，断点恢复天然不会命中）。
- 风险：状态枚举文字扩散到约 12 份文件，遗漏一处即镜像/文档校验失败（由校验器自身守护）；CI 首次推送前无法在本仓库内验证 Actions 实际执行，只能本地等价验证 + 推送后观察（推送属外部授权步骤）。
