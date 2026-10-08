# 登记寓小二项目

模式: 标准
状态: 已归档

## Why

事实查询工具当前 registry 为空，但工作区已经检出 `yuxiaor-pms`、`yuxiaor-e-signature` 和 `yuxiaor-xxljob`。缺少登记会使项目上下文、业务词路由和受限工作区搜索无法定位这些项目。

## What Changes

- 在 `.ai/kb/projects/registry.json` 登记三个项目的路径、构建入口、搜索根、应用启动类、项目依赖和业务词。
- 为三个项目新增 `.ai/kb/projects/<name>.md` 项目卡，记录职责、高频入口、跨仓库关系和验证入口。
- 在 `.ai/rules/index.md` 的项目登记路由中补充三个项目名与业务关键词。

## Impact

- 只扩大 `.ai` 事实查询白名单和知识路由，不修改三个项目源码、构建配置或运行时行为。
- 登记内容以当前工作区代码、README、Maven POM 和启动类为事实来源；不声明未经核实的部署状态或构建通过证据。
