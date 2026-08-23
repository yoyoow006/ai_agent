# 设计

## 决策

使用 `git remote add origin git@github-yoyoo.com:yoyoow006/ai_agent.git` 精确保留用户提供的 SSH host 别名和路径。该操作只修改本地 `.git/config`，没有 tracked 文件变化，因此不需要 feature 分支或提交。

## 验证

- `git remote get-url origin` 精确匹配用户提供的地址。
- `git remote -v` 显示同一个 fetch/push URL。
- `git branch --show-current` 仍为 `main`。
- `git status --short --branch --untracked-files=all` 显示没有 tracked/staged 修改，且未跟踪路径仅为本变更四个 OpenSpec 文件。

## 边界

- 不验证 SSH 认证，因为那需要联网访问远端。
- 不设置 upstream 分支。
- 不推送、不抓取、不创建 PR。
