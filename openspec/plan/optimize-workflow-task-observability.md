# 工作流可观测性与模板护栏实施计划

## 全局约束

- 只修改共享工作流工具、模板、测试、规范和 `.ai` 工具；不修改三个业务项目源码。
- 不联网、不安装依赖、不执行远程 API、推送或发布。
- 兼容现有 metrics JSON 与 manifest verify 的 fail-closed 语义。

## 任务 1：任务级 telemetry

Modify: `scripts/lib/workflow_events.py`, `scripts/lib/workflow_event_cli.py`, `scripts/validate-workflow.sh`。

Create/Modify tests: `scripts/tests/test_workflow_events.py`。

- 增加 task_id/phase/lifecycle 字段和旧记录兼容解析。
- 增加按 task_id 聚合的只读查询入口。
- 测试成功、失败、缺字段和跨阶段聚合；预期旧 JSON 仍可读取。

## 任务 2：proposal 与归档模板

Modify: `openspec/templates/proposal.md`, `openspec/templates/tasks.md`, `scripts/new-openspec-change.py` 及相关校验测试。

- 生成顶层 `模式:`、`状态:`。
- 生成标准归档索引 bullet 示例。
- 测试错误格式非零、正确格式通过，且不削弱现有严格状态约束。

## 任务 3：manifest 最终化

Modify: `.ai/tools/review_manifest.py`, `.ai/tools/README.md`, `scripts/tests/test_review_manifest.py`。

- 增加显式 finalize 子命令或等价接口，写入最终证据元数据。
- finalize 后执行 verify；任何范围变化必须返回 STALE。
- 测试 finalize、重复 finalize、stale 和路径越界。

## 任务 4：项目登记生成/校验

Create: `.ai/tools/project_registry.py`, `.ai/tools/tests/test_project_registry.py`。

- 实现 validate/render 两个只读或显式输出命令。
- 复用 registry 的路径、依赖、business_terms 和 application 校验。
- 生成内容包含 registry 项目对象、项目卡 frontmatter/章节骨架和 rules index 路由行。
- 测试不覆盖已有文件、拒绝越界路径、拒绝未知依赖和 JSON 可解析。

## 任务 5：综合验证

- 运行相关 Python 单测。
- 运行 `bash scripts/validate-workflow.sh --fast` 和 `bash scripts/validate-workflow.sh --archive-light`。
- 冻结 manifest，完成规格符合性审查和代码质量审查；记录未验证范围与残余风险。
