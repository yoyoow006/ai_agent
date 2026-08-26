# 初始化 AI 工作流仓库 Git 基线

模式: 标准
状态: 待归档

## Why

当前目录只有空的 `.git` 目录，`git status` 失败，无法创建分支、冻结 review manifest、提交变更或完成标准/严格归档。仓库同时缺少根 `.gitignore` 与 OpenSpec 基线文件，导致本地工作流校验无法通过。

用户已明确要求把当前目录初始化成 Git 项目。初始化后需要建立可恢复的 `main` 基线提交，同时避免把本地草稿、审查 manifest、Python 缓存和助手本地配置纳入版本控制。

## What Changes

- 将空 `.git` 目录恢复为可用 Git 元数据，初始分支命名为 `main`。
- 新增根 `.gitignore`，忽略：
  - `/.ai-local/`
  - `/.codex/sdd/`
  - `/.claude/sdd/`
  - `/.worktrees/`
  - `__pycache__/`
  - `*.py[cod]`
  - `/.claude/settings.local.json`
- 从 `scripts/ai-workflow-assets/shared/openspec/` 补齐当前根目录缺失的 OpenSpec 基线：
  - `openspec/AGENTS.md`
  - `openspec/project.md`
  - `openspec/archive/.gitkeep`
  - `openspec/plan/.gitkeep`
  - `openspec/specs/.gitkeep`
  - 两个共享工作流主规格
- 创建 `.claude/sdd/.gitkeep`，使双侧助手本地草稿目录在当前工作区存在；该目录整体仍按本地状态忽略。
- 初始化后检查待跟踪清单，创建当前仓库的初始提交。

## Impact

- 受影响路径：`.git/`、`.gitignore`、`openspec/` 基线目录、`.claude/sdd/.gitkeep`，以及初始化后纳入 Git 的现有项目文件。
- 不添加 remote，不推送，不执行强推或历史改写。
- 不修改安装器运行时代码、资产清单或业务知识正文。
- 本地整合策略：正常标准模式应先创建 feature 分支；但本变更的目的正是创建 Git 仓库，实施前无法分支。因此按用户确认在当前工作区直接初始化 `main`，把当前状态与本变更四件套一起作为初始提交；后续新变更再恢复正常 feature 流程。

## Verification Evidence

- 实施时 `git rev-parse --is-inside-work-tree` 输出 `true`，`git branch --show-current` 输出 `main`；实施记录中的初始提交为 `62a92d7`。
- 后续已归档的 `sanitize-git-baseline-secrets` 为清除历史敏感内容重建 root，当前可复核根提交为 `71f84dcc5fc6bea7b32d97ef04528c0031772a16`；该根提交包含本变更四件套、根 `.gitignore` 和 OpenSpec 基线路径。
- 初始化时 `git remote -v` 为空，未添加远端或执行网络操作；后续已归档的 `add-origin-remote` 按独立授权配置 `origin`，本变更不禁止该后续状态。
- 当前 `git fsck --full` 退出码 0、无输出。
- 当前 `bash scripts/install-ai-workflow.sh --help` 退出码 0，stdout 为 usage，stderr 为空。
- 当前 `openspec validate initialize-git-repository --strict --no-interactive` 输出 valid。
- 当前 `bash scripts/validate-workflow.sh` 输出 `PASS=169 FAIL=0 SKIP=0`，OpenSpec 检查实际执行且未 SKIP。
- 标准 Verify manifest `ae18b9ce…` 发现 `IGR-001`：三份本变更 OpenSpec 修正尚未提交，导致干净基线场景临时失败；已用提交 `9ec162f` 精确处置。
- 差异复审 manifest `da154dd3…` 确认 delta 仅包含该三份文件、工作区 clean、`IGR-001` resolved；reviewer 与主会话均在提交后复跑 required workflow，结果均为 `PASS=169 FAIL=0 SKIP=0`。
