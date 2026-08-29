# 项目登记与项目卡

`registry.json` 是事实工具允许访问的项目白名单，项目卡保存人类可读的稳定语义。登记不代表项目当前已检出或事实刚刚复验。

## registry 契约

- `schema_version` 当前为 `1`。
- 每个项目包含 `name`、相对 `path`、`build`、相对 `.ai/` 的 `card`、`search_roots` 和 `applications`。
- 每个 application 包含 `server`、`module`、`main_class`、`source_path`。
- 路径不得是绝对路径，不得含 `..`；事实工具还会用真实路径检查 symlink 逃逸。
- 未登记路径、被忽略内容和敏感文件不属于查询范围。

## 项目卡维护

- 保留技术、安全、契约和验证事实，注明来源；不要加入助手身份包装。
- 不把运行时“已检出/缺失”观察写入项目卡。
- 新增项目必须有权威来源，并同时更新 registry、项目卡和 `.ai/rules/index.md`。
