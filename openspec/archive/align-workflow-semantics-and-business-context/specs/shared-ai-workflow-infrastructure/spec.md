# Shared AI Workflow Infrastructure Business Context Delta

## ADDED Requirements

### Requirement: 业务词上下文路由必须保持声明式且有界

项目 registry SHALL 支持每个项目声明可选 `business_terms` 列表；每条业务词 SHALL 包含非空单行 `term`、非空 `source_paths` 列表，并 MAY 包含同义词列表。事实工具 SHALL 提供 `business-terms` 只读查询，支持重复项目过滤、默认包含匹配、显式精确匹配、分页和确定性输出。查询 SHALL NOT 联网、clone、写入项目或 registry、读取并输出匹配正文，或访问 registry 白名单和项目边界之外的路径。

#### Scenario: 按业务词路由项目

- **WHEN** 目标项目 registry 中某项目声明 term 为“合同”且存在同义词“租约”
- **AND** 助手以“租约”执行包含匹配
- **THEN** 查询返回该业务词、项目、项目卡和声明的相对源码路径
- **AND** 不输出源码正文或凭据内容

#### Scenario: 精确过滤与分页

- **WHEN** 查询使用 `--exact`、重复 `--project`、`--limit` 和 `--offset`
- **THEN** 仅所选项目的精确 term/synonym 匹配按确定性顺序返回
- **AND** 超出上限时在 stderr 输出下一页提示

#### Scenario: 非法声明被拒绝

- **WHEN** registry 中业务词、同义词或源码路径为空、多行、绝对路径或包含 `..`
- **THEN** 查询以输入错误退出
- **AND** 不回退到未声明白名单的路径扫描

#### Scenario: 查询保持只读

- **WHEN** 连续执行 `business-terms` 查询
- **THEN** workspace 文件内容与 mtime 均不改变
