# 任务

## 1. 配置远程仓库

- [x] 1.1 执行 `git remote add origin git@github-yoyoo.com:yoyoow006/ai_agent.git`。

## 2. 验证

- [x] 2.1 运行 `git remote get-url origin`，预期精确输出用户提供的地址。
- [x] 2.2 运行 `git remote -v`，预期 origin 的 fetch/push URL 相同。
- [x] 2.3 运行 `git status --short --branch --untracked-files=all`，预期仍为 `main`、无 tracked/staged 修改，且仅有本变更四个 OpenSpec 文件未跟踪。

## 3. 收尾

- [x] 3.1 汇报未执行的网络操作和后续推送所需的独立授权。
