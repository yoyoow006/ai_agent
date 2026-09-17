# 项目登记与项目卡

`registry.json` 是事实工具允许访问的项目白名单，项目卡保存人类可读的稳定语义。登记不代表项目当前已检出或事实刚刚复验。

## registry 契约

- `schema_version` 当前为 `1`。
- 每个项目包含 `name`、相对 `path`、`build`、相对 `.ai/` 的 `card`、`search_roots` 和 `applications`。
- 每个 application 包含 `server`、`module`、`main_class`、`source_path`。
- 每个项目可声明 `business_terms`；每条包含非空单行 `term`、非空 `source_paths`，并可声明 `synonyms`。它只用于把业务词路由到项目卡和相对源码路径，不证明路径内容当前仍与业务语义一致。
- 路径不得是绝对路径，不得含 `..`；事实工具还会用真实路径检查 symlink 逃逸。
- 未登记路径、被忽略内容和敏感文件不属于查询范围。

## 项目卡维护

- 保留技术、安全、契约和验证事实，注明来源；不要加入助手身份包装。
- 不把运行时“已检出/缺失”观察写入项目卡。
- 新增项目必须有权威来源，并同时更新 registry、项目卡和 `.ai/rules/index.md`。
- 业务词、同义词和源码路径必须从目标项目权威代码、契约或业务文档复核后登记；后续用 `business-terms` 查询只做路由，命中后仍要读取当前源码或项目卡核实。
