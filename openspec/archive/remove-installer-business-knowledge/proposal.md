# 从安装工具仓库移除业务项目知识

模式: 严格
状态: 已归档

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

## Verification Evidence

- 任务级内容审查通过；R7 验证命令缺口已最小修复并完成 delta 复审，manifest `c316bf3e6e815d8ee8d198c5ef9fb7e2834af778d91c2de2bb6493603fdde986`。
- installer-only root：`71f84dcc5fc6bea7b32d97ef04528c0031772a16`；当前分支为 `main`，`git remote -v` 为空。
- 当前 designated 业务路径为 0，registry 为空；全部 reachable 历史扫描 `designated_history_paths=0`。
- 旧 `main` 与实施 feature 提交对象查询均失败，说明已从本地对象库修剪。
- `git fsck --full` 退出码 0，工作区 clean。
- `.ai/tools/tests` 53 例全部通过。
- 安装器资产 manifest/content 契约 6 例全部通过。
- `bash scripts/install-ai-workflow.sh --help` 退出码 0，stderr 为空。
- `openspec validate --all --no-interactive` 输出 6 passed、0 failed。
- `bash scripts/validate-workflow.sh --require-openspec` 输出 `PASS=169 FAIL=0 SKIP=0`。
