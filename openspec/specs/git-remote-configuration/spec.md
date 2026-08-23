# Git 远程仓库配置规范

## Purpose

约束本地仓库远程地址配置与验证边界，确保添加 remote 不隐含网络访问或推送授权。

## Requirements

### Requirement: 本地仓库必须配置用户指定的 origin

仓库 SHALL 将远程名 `origin` 的 fetch/push URL 配置为用户明确提供的 SSH 地址，且不得自动执行网络操作。

#### Scenario: 查询远程地址

- **WHEN** 运行 `git remote get-url origin`
- **THEN** 输出用户指定的 SSH 地址
- **AND** `git remote -v` 中 origin 的 fetch 与 push URL 相同

#### Scenario: 检查本地边界

- **WHEN** 添加远程地址后运行 `git status --short --branch --untracked-files=all`
- **THEN** 仓库仍位于 `main`，没有 tracked 或 staged 修改
- **AND** 未跟踪路径仅为当前变更的 OpenSpec 文件
- **AND** 没有执行 fetch、pull 或 push
