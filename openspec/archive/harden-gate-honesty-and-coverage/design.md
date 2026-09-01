# Design——门禁诚实性与覆盖加固

## 关键决策

### D1 透明化语义：明细透传，不进 SKIP 字段（用户已决策）

契约套件仍整体计 1 个门禁检查；内部跳过以"缩进明细 + 计数注解"呈现在**契约套件结果之后、最终汇总行之前**。理由：

- verify/archive 技能现行措辞"仓库自带必需测试不得 SKIP"不改——若计入顶层 SKIP，安装目标严格归档将永久 `SKIP=2` 而被自身措辞阻断，需连带改治理文本并升级严格模式（方案 B 已被否决）。
- 契约测试以 `PASS=\d+ FAIL=0 SKIP=\d+\s*\Z` 锚定汇总行为末行（`test_validate_workflow.py:487,495,696,1145`）；注解置于汇总之前可保持全部现有断言兼容。
- 注解行**不使用 `[...]` 括号标签**（避免被任何 `^\[` 计数解析器误读为第四种检查结果），采用缩进文本行：`  契约套件内部设计性跳过 N 项（不影响门禁计数）:` + 逐条 `  - <测试名> ... skipped '<原因>'`。
- 明细仅在套件 PASS 分支提取打印；FAIL 分支本就全量转储输出，含跳过信息，不重复。

### D2 检查 A 实现与范围

- `retired_tool_names_absent`：对存在的路径（`.codex/skills`、`.claude/skills`、`.codex/README.md`，`scripts/ai-workflow-assets` 存在时含资产树）`grep -R -F --include='*.md' --include='*.toml'` 固定废弃 token 清单：`multi_agent_v1__spawn_agent`、`send_input`、`close_agent`、`fork_context`。命中即 FAIL。限定文档后缀的原因：契约对象是指导正文而非可执行源码，且资产树内校验器自身副本含 token 清单字面量，不限定会自引用误报（实现中实测踩过）。
- `adapter_note_tools_ok`：`contains_all .codex/skills/parallel-agents/SKILL.md 'spawn_agent' 'followup_task' 'send_message' 'wait_agent' 'fork_turns'`，门控 `assistant_required codex`（Claude 侧镜像无注记，不检查）。
- 与登记数守卫互补：登记数管"有几条注记"，本检查管"注记和技能树里写的是什么"。

### D3 检查 B 实现与边界

- `archive_index_ok`：`find openspec/archive -mindepth 1 -maxdepth 1 -type d` 目录名排序为一边；`sed -n 's/^- \`([^\`]+)\`.*/\1/p'` 提取索引行排序为另一边；`cmp` 判 1:1；重复行用 `awk 'd[$0]++'` 检出即 FAIL。
- 边界：有目录无 README → FAIL（首次归档必须建索引）；有 README 无目录（悬空）→ FAIL；两者皆空 → PASS（安装目标空白基线，`openspec/archive/.gitkeep` 场景）。
- 外部命令仅用 `find/sed/sort/cmp/awk`，全部在既有白名单内，`--print-external-commands` 清单不变。

### D4 三树同步

`scripts/lib/validate-workflow-core.sh` 与 `scripts/validate-workflow.sh` 的修改同步 `scripts/ai-workflow-assets/shared/scripts/` 两份副本，`cmp` 字节一致是完成判据。`scripts/hooks/pre-push` 无资产副本（源仓专属），不动。

### D5 分类与先例

只增检查与输出注解，不改模式分层、技能措辞、汇总语义——与 `harden-workflow-verification`（标准）同类；区别于触及治理文本的 `harden-gate-coverage-and-tiers`（严格）。

## 替代方案

- **计入顶层 SKIP + 精确化技能措辞**：被用户否决（触发严格模式，且目标内严格流程将被永久阻断，收益仅是计数字段美观）。
- **把 CI/pre-push 测试拆到源仓专用测试文件**：消除目标内跳过本身，但重构契约套件布局、动 wrapper 必跑清单，范围远超本次目标，不采。
- **校验器直接解析注记行并与 `.codex/README.md` 映射表逐项比对**：过度工程——README 是人读映射表非机读契约，固定 token 清单 + 现行名 contains_all 已覆盖已知漂移向量，且失败信息更直白。

## 风险与边界

- **目标侧假阳性**：资产树缺席（条件包含已处理）、空归档（vacuous PASS 已处理）、`.claude/skills` 在 codex-only 目标缺席（grep 对不存在路径跳过）。
- **新检查自身出 bug 阻断归档**：三项检查逻辑均为纯文本集合比对，任务 6 的全量回归在源仓与 fixture 双路径验证；最坏回滚方式是 revert 单个检查函数。
- **注解解析兼容**：外部无程序化消费门禁输出的记录（pre-push 只透传退出码）；注解不进任何 `[PASS]` 行，风险可忽略。
- **不验证范围**：不验证 wrapper 注解对非 unittest 跳过格式的兼容（契约套件固定为 unittest）；不验证 `--fast` 下注解行为（该模式不跑套件，无注解，行为不变）。
