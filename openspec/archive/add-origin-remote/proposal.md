# 添加 AI 工作流仓库远程地址

模式: 标准
状态: 已归档

## Why

用户要求为当前本地 `main` 仓库添加远程仓库：

```text
git@github-yoyoo.com:yoyoow006/ai_agent.git
```

当前仓库没有配置任何 remote。添加 remote 只写入本地 `.git/config`，不会联网、抓取、推送或修改分支。

## What Changes

- 将远程名称设为 `origin`。
- 将 `origin` URL 精确设置为用户提供的 SSH 地址。
- 不执行 `fetch`、`pull`、`push`、`clone` 或远端分支跟踪配置。
- 不修改 tracked 文件、分支或提交历史。

## Impact

- 受影响位置：本地 `.git/config`。
- 本地整合策略：这是未入库的本地 Git 配置，不创建 feature 分支、不产生提交；确认后直接配置并验证。
- 后续推送属于新的外部副作用，必须另行明确授权。

## Verification Evidence

- `git remote get-url origin` 输出 `git@github-yoyoo.com:yoyoow006/ai_agent.git`。
- `git remote -v` 显示同一个 URL 同时用于 fetch 与 push。
- 当前分支仍为 `main`。
- `git status --short --branch --untracked-files=all` 显示无 tracked/staged 修改；未跟踪路径仅为本变更四个 OpenSpec 文件。
