# 从安装工具仓库移除业务项目知识

模式: 严格
状态: 待验证

## Why

本仓库定位是 AI 编程助手安装工具与工作流框架源码，但当前 tracked `.ai/` 中混入了原业务工作区的项目卡、契约、业务 memory、registry 登记和模块路由。根目录还包含 Java 业务审查清单与业务 VS Code workspace 配置。它们不属于安装器源码，也不随安装资产分发。

用户已选择方案 2：只从当前安装工具仓库移除，不迁移、不另存。由于需要删除 tracked 内容并重建本地 Git root 历史，属于不可逆破坏性清理，必须按严格模式执行。

## What Changes

- 删除业务契约与项目卡：
  - `.ai/kb/contracts/*`
  - `.ai/kb/projects/*.md`，但保留通用 `projects/README.md`
- 删除业务 memory：
  - `.ai/memory/api-server.md`
  - `.ai/memory/yuxiaor-server.md`
  - `.ai/memory/workflow.md` 中两条业务来源记录
- 将 `.ai/kb/projects/registry.json` 恢复为空白通用登记：

```json
{
  "schema_version": 1,
  "projects": []
}
```

- 清理 mixed 文件中的业务段落：
  - `.ai/kb/overview.md` 移除业务模块速查和项目映射；
  - `.ai/rules/index.md` 移除业务模块路由行；
  - `.ai/tools/README.md` 将项目查询示例改为通用占位符。
- 删除根目录业务工作区产物：
  - `REVIEW.md`
  - `pms-vs.code-workspace`
- 修改根目录 `.gitignore`，防止业务项目卡、契约、业务 memory 和本地 workspace 配置再次误入库；不修改安装器生成目标的 `.gitignore` 模板。
- 在两次确认后重建本地 sanitized root，删除旧引用、reflog 并修剪不可达对象。

## Impact

- 删除是永久性的：不迁移、不备份、不另存；历史重建后原业务知识文件不可从本仓库 Git 对象恢复。
- 保留安装器通用能力：空 registry、项目登记契约、`project_facts.py`、review manifest、共享规则与提示词。
- 不修改安装器运行时代码和资产清单。
- 不添加 remote、不推送、不创建 pack。
