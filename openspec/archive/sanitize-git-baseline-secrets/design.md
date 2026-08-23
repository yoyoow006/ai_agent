# 设计

## 初步方向

本文件是严格模式 Open 四件套的一部分，不是独立实施计划。用户确认规范后，需按 Design 阶段产出可执行计划并再次确认。

初步方向是先净化当前正文并修正 tasks 格式，再以当前工作树建立新的 sanitized root commit。由于当前仓库没有 remote，且两个旧提交均为本轮刚生成的本地基线提交，可以在用户明确授权后移除旧引用、清理 reflog 并修剪不可达对象。这样比逐 commit filter 更简单，也避免把敏感对象保留在任何 reachable 历史中。

## 关键边界

- 不把 reviewer 发现的字面凭据写入新的 OpenSpec、提交信息或日志。
- 不添加 remote、不推送、不创建 pack。
- 不访问外部系统，不声称凭据轮换完成。
- 历史重建前必须完成用户确认与严格 Design 独立计划确认。

## 待 Design 细化

- 精确的脱敏替换文本。
- 使用 orphan branch 或 `commit-tree` 重建 root 的具体安全步骤。
- 旧引用、reflog、临时 review 对象与 prune 的顺序。
- 清理后对 current tree、全部 reachable history、`git fsck`、OpenSpec 和工作流的完整验证矩阵。
