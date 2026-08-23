# 初始化 AI 工作流仓库 Git 基线

模式: 标准
状态: 待验证

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

- `git rev-parse --is-inside-work-tree` 输出 `true`；`git branch --show-current` 输出 `main`。
- 初始提交：`62a92d7 chore: initialize AI workflow repository`，收录 166 个未忽略文件。
- `git remote -v` 为空，未添加远端。
- `git fsck --full` 退出码 0；报告一个暂存阶段旧任务文件形成的悬空 blob，无对象损坏。
- `bash scripts/install-ai-workflow.sh --help` 退出码 0，stderr 为空。
- `openspec validate --all --no-interactive` 最终输出 4 passed、0 failed。
- `bash scripts/validate-workflow.sh` 最终输出 `PASS=168 FAIL=0 SKIP=0`。首次运行发现的既有 `fix-installer-python-38` delta 缺少字面 `SHALL`，已按 OpenSpec CLI 契约做最小 wording 修正后复验通过。
