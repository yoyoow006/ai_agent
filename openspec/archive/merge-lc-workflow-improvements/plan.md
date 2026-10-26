# LC 工作流回流实现计划

## 目标、架构与全局约束

以当前 Python 标准库、Bash、Markdown 工作流为基础，选择性移植来源 76a1676319eaa7e6dbdd74f2a4b8b72d06f6fc58 的通用能力，不新增依赖。

全局约束（逐字沿用规范）：
- 不推送、不创建远程 PR、不删除来源或用户工作。
- 不处理已有 `layered-validation-agent-gating-output-metrics` 变更（待验证），不重做或归档其任务；仅兼容其已存在实现。
- 保留当前标准小任务豁免、验证分层说明和已有知识，排除来源倒退及无语义格式变化。详见 comparison.md。

## 单元 1：治理路由和传播

Modify：AGENTS.md、CLAUDE.md、.codex/README.md；双侧 open/design/build/verify/archive/code-review/git-worktrees/subagent-driven 技能；.ai/rules/review.md、index.md、.ai/kb/overview.md；openspec/specs/risk-tiered-ai-workflow/spec.md、shared-ai-workflow-infrastructure/spec.md；scripts/lib/validate-workflow-core.sh、scripts/workflow-pressure-scenarios.md、scripts/tests/test_validate_workflow.py。
Create：.ai/rules/archive.md、business-git-branching.md。
输入：已确认 comparison；输出：五类风险路由一致，小任务豁免保留，规则从技能可达。
先用新上下文基线压力探针记录业务高风险自动严格等旧行为；更新内容后重跑。校验器新增行为先补测试并确认红，再移植最小实现。
验证：`python3 -B -m unittest scripts.tests.test_validate_workflow`；安装镜像同步前允许仅镜像类检查报告差异，最终必须全绿。按门禁路由不变量独立任务审查。

## 单元 2：通用工具和证据

Modify：scripts/lib/workflow_events.py、workflow_event_cli.py、scripts/validate-workflow.sh、scripts/new-openspec-change.py、.ai/tools/review_manifest.py。
Create：.ai/tools/project_registry.py、.ai/tools/tests/test_project_registry.py。
Test：.ai/tools/tests/test_review_manifest.py、scripts/tests/test_workflow_events.py、test_workflow_wrapper.py、test_openspec_templates.py。
接口：EventWriter 可选 task_id，CLI 可选 task-id/phase；阶段汇总不重复计 summary。finalize 先 verify 再写 JSON，不关闭 finding。registry validate/render 仅草稿输出、显式 build、空 applications、防止任何输出静默覆盖。proposal 拒绝列表前缀模式/状态。
先编写并实际运行失败测试，确认失败来自功能缺失，然后最小实现并回归。
验证：`python3 -B -m unittest discover -s .ai/tools/tests`；`python3 -B -m unittest scripts.tests.test_workflow_events scripts.tests.test_workflow_wrapper scripts.tests.test_openspec_templates`。按证据有效性与输出保护不变量独立任务审查。

## 单元 3：分发、全量终验和整合

Modify：scripts/ai-workflow-assets/ 下对应双侧/共享镜像、manifest.json，必要安装测试；.ai/kb/projects/README.md、.ai/kb/verification-evidence.md、.ai/memory/workflow.md 和本变更记录。
同步已有资产映射，新工具显式加入清单，保留空 registry，不带业务资料。
验证：`bash scripts/validate-workflow.sh --require-openspec`；`openspec validate --all --strict --no-interactive`；`python3 -B -m unittest scripts.tests.test_install_ai_workflow scripts.tests.test_install_workflow`。安装套件串行执行，日志留 .ai-local。`git diff --check`。
freeze 有效 manifest，按安装传播不变量任务审查；再独立执行 Verify 规格符合性与代码质量两关注面，压力场景结果逐项落盘。修复后只审 delta 和消费者。
归档自身 delta，保留既有活跃变更；依据 Verify 后文件分类运行 archive-light 或 required。本地按职责提交后合回 main，不执行远程操作。

## 计划自审

所有接口和修复均在已确认范围；不涉及业务权限认证、资金、数据库、删除、外部副作用或新依赖。计划无待定选择。严格流程治理变更本身不触发第二次确认；用户原确认覆盖本地分支和整合。
