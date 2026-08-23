# 仓库忽略规则

## 职责

仓库根目录 `.gitignore` 管理仅供本地使用的工具链、依赖目录和外部项目入口，防止它们进入版本控制。

## 规则约定

- 指定路径使用 `/name` 形式。
- 前导 `/` 将匹配限定在仓库根目录，避免误忽略子目录中的同名路径。
- 不使用末尾 `/`，使规则同时匹配真实目录、普通文件和符号链接。
- 当前受管路径以主规格 `openspec/specs/repository-ignore-rules/spec.md` 为准。

## 验证

- 用 `git check-ignore -v --no-index <root-path>` 验证根路径被匹配。
- 用 `git check-ignore --no-index probe/<name>` 验证子目录同名路径不被匹配；预期退出码为 `1`。
