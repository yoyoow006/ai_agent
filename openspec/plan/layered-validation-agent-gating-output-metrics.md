# 实施计划：验证分层、代理门控、输出协议与轻量度量

## 目标与全局约束

在现有 `scripts/validate-workflow.sh` 与 core 上增加可审计分层计划、严格代理门控、兼容输出协议和可丢弃本地指标。保持现有 CLI、PASS/FAIL/SKIP 语义、末行汇总、required 禁止验证缓存；不修改业务运行时、API/Schema、数据库、外部发布或远程服务。

## 架构与接口决策

1. 新增 `scripts/lib/workflow_events.py`（标准库）：定义 schema_version=1、事件必需字段、JSONL writer、run_id 生成、原子指标写入和写入失败诊断。事件只含聚合字段，不含源码正文或凭据。
2. wrapper 在参数冲突检查后生成 `plan` 事件；每个层级/检查输出 `check` 事件；结束输出 `summary` 事件。JSONL 仅在 `WORKFLOW_OUTPUT=jsonl` 或 `--output-jsonl PATH` 启用，默认仍只输出现有人类文本。
3. 分层计划由 wrapper 的单一状态变量驱动：fast 只 core；standard 运行 core 后契约套件；命中治理路径提升 required；required 直接实际执行全套。core FAIL/不可解析时将依赖层标记未执行，不调用契约套件。
4. 新增 `scripts/lib/agent_dispatch.py`：接受 JSON 输入的角色、边界、验收命令、共享写入/顺序依赖和任务规模，输出 allow/deny 及稳定 reason_code；不启动宿主代理。门控规则：独立边界、角色匹配、可执行单行命令、无共享写入/顺序依赖，且 fast/标准小任务直接拒绝。
5. 指标写入 `.ai-local/metrics/<run_id>.json`，字段包含层级耗时、PASS/FAIL/SKIP、代理 allow/deny、缓存沿用和解析错误计数；写入失败只输出 `metrics_write_failed`，不改退出码。

## 任务与红—绿—重构顺序

### 1. 事件与指标工具

- Test：在 `scripts/tests/test_workflow_events.py` 先覆盖事件必填字段、JSONL 单行解析、原子写入和不可写降级，先见预期失败。
- Implement：创建 `scripts/lib/workflow_events.py`，只实现当前测试需要的 schema 校验、writer 和 metrics。
- Verify：`python3 -B -m unittest -v scripts.tests.test_workflow_events`，预期全绿。

### 2. 代理门控

- Test：在 `scripts/tests/test_agent_dispatch.py` 先覆盖四条件缺失、任务规模豁免、合法 test worker、重叠边界和非法命令。
- Implement：创建 `scripts/lib/agent_dispatch.py`；拒绝不启动任何代理并返回 reason_code。
- Verify：`python3 -B -m unittest -v scripts.tests.test_agent_dispatch`。

### 3. wrapper 分层与输出接入

- Test：扩展 `scripts/tests/test_validate_workflow.py` 覆盖 plan/check/summary JSONL、core 失败停止、`--output-jsonl` 参数与人类汇总末行兼容；先运行新增测试确认失败。
- Implement：修改 `scripts/validate-workflow.sh`，通过单一事件工具发出诊断，接入运行耗时、计数和 metrics；保持原契约 suite 调用点唯一。
- Verify：运行目标测试、`bash scripts/validate-workflow.sh --fast`、参数冲突和 `WORKFLOW_OUTPUT=jsonl ... --fast`。

### 4. 共享契约同步

- Modify：更新 `.ai/prompts/agents/*.md`、`.codex/agents/*.toml`、相关 `.codex/skills/`、`AGENTS.md`、`.ai/rules/index.md` 与主规格；记录四项门控、双轨输出和指标边界。
- Test：新增结构/镜像断言，确保未启用 JSONL 不写 tracked 文件、required 不读验证缓存。
- Verify：`python3 -B -m unittest -v scripts.tests.test_validate_workflow scripts.tests.test_workflow_events scripts.tests.test_agent_dispatch` 与 `git diff --check`。

### 5. 终验准备

- Run：`bash scripts/validate-workflow.sh --require-openspec`、OpenSpec strict 校验和必要压力场景。
- Record：更新 tasks 勾选、未验证范围和残余风险；状态交给 Verify。

## 失败与回滚

工具输出非法或 JSONL 写入失败时只增加诊断/解析计数，不改变真实检查结果；计划层失败停止后续依赖层。所有实现文件按职责单元可独立删除回滚，禁止自动提交、推送或发布。
