# 任务

## 1. 建立 Git 与 OpenSpec 基线文件

- [x] 1.1 新增根 `.gitignore`，包含提案列出的本地路径与 Python 缓存规则。
- [x] 1.2 从 `scripts/ai-workflow-assets/shared/openspec/` 复制当前根目录缺失的基线文件，不覆盖既有活跃变更。
- [x] 1.3 创建 `.claude/sdd/.gitkeep`。

## 2. 初始化 Git 仓库

- [x] 2.1 恢复空 `.git` 目录的可写权限并运行 `git init`。
- [x] 2.2 用 `git symbolic-ref HEAD refs/heads/main` 固定初始分支。
- [x] 2.3 确认 Git 使用现有全局 `user.name=shitou` 与 `user.email=shitou@mgzf.com`，不修改全局配置。

## 3. 检查并创建初始提交

- [x] 3.1 运行 `git status --short --untracked-files=all`，确认 `.ai-local`、双侧 SDD 草稿、Python 缓存和 Claude 本地配置未进入待跟踪清单。
- [x] 3.2 运行 `git check-ignore -v` 验证提案中的本地路径。
- [x] 3.3 运行 `git add -A` 并复核 `git diff --cached --name-status`。
- [x] 3.4 创建初始提交，建议信息：`chore: initialize AI workflow repository`。

## 4. 验证

- [x] 4.1 `git rev-parse --is-inside-work-tree`，预期输出 `true`。
- [x] 4.2 `git branch --show-current`，预期输出 `main`。
- [x] 4.3 `git log -1 --oneline`，预期输出初始提交。
- [x] 4.4 `git status --short --branch`，预期初始提交后为空。
- [x] 4.5 `git fsck --full`，预期退出码 0。
- [x] 4.6 `bash scripts/install-ai-workflow.sh --help`，预期退出码 0 且 stderr 为空。
- [x] 4.7 `bash scripts/validate-workflow.sh`，预期除 OpenSpec CLI 缺失显式 SKIP 外无 FAIL。

## 5. 收尾

- [x] 5.1 更新 proposal 状态为`待验证`并记录验证证据。
- [x] 5.2 检查完整 Git 状态与提交清单，汇报未验证范围和残余风险。
