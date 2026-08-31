# 门禁诚实性与覆盖加固：注记工具名契约、套件跳过透明化、归档索引完整性

模式: 标准
状态: 已归档

## Why

审查意见核实（2026-08-31）确认三个门禁盲区，均为"当前内容正确但无门禁拦截"的漂移风险：

1. **适配注记工具名可漂移**（F-1 残余）：`.codex/skills/parallel-agents/SKILL.md:8` 的适配注记曾引用已废弃工具名（`multi_agent_v1__spawn_agent`/`send_input`/`close_agent`）且随安装器资产分发，文本已修正（提交 008d6eb），但校验器只做两件事：`mirror_equal` 在比较镜像前整行删除注记、`adapter_note_registry_ok` 只比对注记行数与登记值——注记内容与 `.codex/README.md` 权威映射的一致性无任何检查，同类漂移可原样复发。
2. **契约套件内部跳过不可见**（F-3）：公共 wrapper 把整个契约套件计为 1 个 `[PASS]`，成功分支吞掉 `-v` 输出；安装目标中 CI/pre-push 两个测试必然设计性跳过（manifest 不分发 `.github`/`pre-push`/安装器源码），既不进 SKIP 计数也不可见。
3. **归档索引靠纪律维持**（F-4）：校验器只检查技能正文出现 `openspec/archive/README.md` 字符串（`validate-workflow-core.sh:533`），不检查文件存在、条目与目录 1:1 或重复；漏加索引行无拦截。当前源仓 18/18 完整，纯靠流程纪律。

## What Changes

- **core 新增检查 A（注记工具名契约）**：已废弃工具名（`multi_agent_v1__spawn_agent`、`send_input`、`close_agent`、`fork_context`）在 `.codex/skills`、`.claude/skills`、`.codex/README.md` 及资产树（存在时）零残留；Codex 侧 `parallel-agents` 技能必须含现行派发工具名（`spawn_agent`、`followup_task`、`send_message`、`wait_agent`、`fork_turns`）。
- **core 新增检查 B（归档索引完整性）**：`openspec/archive/` 每个变更目录在 `README.md` 恰好一行索引，无缺失、悬空、重复；无归档目录时允许 README 缺席（安装目标空白基线 vacuous PASS）。
- **wrapper 透明化（套件内部跳过明细）**：契约套件存在内部跳过时，在最终汇总行之前逐条列出跳过的测试与原因并给出计数注解；顶层 `PASS/FAIL/SKIP` 字段语义不变（用户已决策：明细透传、不进 SKIP 字段，技能措辞不动）。
- **测试**：三项各加红绿契约测试；回归覆盖源仓与 fixture 双路径。
- **规格**：`shared-ai-workflow-infrastructure` 的"工作流验证必须显式区分通过、失败和未运行"需求合并上述三个场景。
- **三树同步**：`validate-workflow-core.sh` 与 `validate-workflow.sh` 修改后同步 `scripts/ai-workflow-assets/shared/scripts/` 副本，保持字节一致。

## Impact

- **运行时行为**：`scripts/lib/validate-workflow-core.sh`（+2 检查）、`scripts/validate-workflow.sh`（成功分支新增注解输出）；两者均在安装 manifest 内，随升级分发到目标。新检查对现状全绿（F-1 已修、索引 18/18、源仓零内部跳过），属"固化当前不变量"而非改变放行结果。
- **不改变**：verify/archive 技能措辞、`--fast` 行为、汇总行末行约定（契约测试 `\Z` 锚定兼容）、外部命令白名单（仅用 awk/find/sed/sort/cmp/wc 等既有项）。
- **风险**：低——纯增量检查与输出注解；目标侧最坏情况为新检查假阳性阻断，已通过条件化（资产树缺席、空归档）排除。
