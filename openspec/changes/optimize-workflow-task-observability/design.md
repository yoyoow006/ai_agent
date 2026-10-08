# 工作流可观测性与模板护栏设计

## 当前事实

- `scripts/validate-workflow.sh` 已记录门禁级 `duration_ms`，但指标只有 run_id、layer 和计数，没有任务名或阶段生命周期。
- `scripts/new-openspec-change.py` 已校验 proposal 内容，但模板格式与 `validate-workflow-core.sh` 的顶层解析要求存在偏差风险。
- `archive_index_ok` 只识别 `- \`变更名\`...` 索引行。
- `review_manifest.py` 能 freeze/verify，但没有“最终化”记录协议。
- `.ai/tools/project_facts.py` 能校验 registry，却没有生成项目卡和规则路由的入口。

## 目标与约束

- 保持现有 metrics JSON 可读取；新增字段必须可选或通过 schema_version 兼容。
- 保持 manifest fail-closed：任何文件、HEAD、base 或 untracked 范围变化仍返回 `STALE`。
- 模板生成结果必须同时满足 OpenSpec 生成器和工作流校验器。
- 项目登记生成器只写入明确目标文件，不扫描、clone、修改业务源码或联网。
- 不引入第三方依赖；优先使用现有 Python 标准库和 Bash 工具。

## 方案与替代方案

### 1. 任务 telemetry

在现有 `workflow_events.py`/metrics 写入层增加 `task_id`、`phase`、`started_at`、`finished_at`、`duration_ms`、`result` 和 `reason_code`；保留现有 summary JSON 字段。新增只读汇总命令按 task_id 聚合 JSONL，缺字段的旧记录按 UNKNOWN 处理。

替代方案是只依赖 Git 提交时间；该方案无法覆盖未提交阶段、失败阶段和同一任务多次验证，因此不采用。

### 2. 模板护栏

把顶层 `模式:`、`状态:` 和归档索引行写入模板单一来源，并在 `new-openspec-change.py check-templates` 与回归测试中验证解析结果。归档 README 使用已有解析器认可的 bullet 格式。

### 3. manifest 最终化

新增 finalization metadata 文件或 manifest 字段，记录最终 manifest ID、comparison base、finding 状态、未验证范围和残余风险；finalize 操作只写入审查目录并立即 verify。禁止通过忽略变化或自动刷新绕过 stale。

### 4. 项目登记生成/校验

新增 `.ai/tools/project_registry.py`：`validate` 复用现有 registry 边界校验，`render` 根据显式输入生成 registry 项目对象、项目卡骨架和规则索引行；默认输出到 stdout 或指定新文件，覆盖写入需要显式参数。先生成草稿，再由维护者补充权威来源和职责事实。

## 验证矩阵

| 能力 | 单元/契约测试 | 门禁 |
|---|---|---|
| task telemetry | `scripts/tests/test_workflow_events.py`、新增聚合测试 | `bash scripts/validate-workflow.sh --fast` |
| proposal/归档模板 | `scripts/tests/test_validate_workflow.py` 模板与索引用例 | `bash scripts/validate-workflow.sh --archive-light` |
| manifest finalization | `scripts/tests/test_review_manifest.py` final/stale 用例 | freeze → finalize → verify |
| registry render/validate | `.ai/tools/tests/test_project_facts.py` 或新增 registry 测试 | JSON、diff、事实工具回归 |

## 风险边界

- 不迁移或重写既有 `.ai-local/metrics` 历史文件。
- 不把未验证的项目卡草稿自动标记为 verified。
- 不让生成器覆盖用户已有项目卡或规则正文，除非显式指定覆盖并通过路径边界检查。
