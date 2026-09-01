# Design: slim-workflow-skills

## 上下文

- 变更对象：三个技能的 SKILL.md 正文（writing-skills、parallel-agents、systematic-debugging），各自存在 4 份副本（`.claude`/`.codex` 工作树＋`scripts/ai-workflow-assets/{claude,codex}` 资产树）；校验器 `scripts/lib/validate-workflow-core.sh`；主规格 `openspec/specs/risk-tiered-ai-workflow/spec.md`。
- 校验既有锚定（已逐条核对，瘦身不得破坏）：13 技能 `mirror_equal` 镜像（路径前缀归一化＋`cat -s`）；`ADAPTER_NOTE_REGISTERED_COUNT=1`（`> **Codex 执行环境` 前缀行全仓恰 1 条，在 parallel-agents）；`adapter_note_tools_ok`（.codex 侧 parallel-agents 含 `spawn_agent`/`followup_task`/`send_message`/`wait_agent`/`fork_turns`）；废弃工具名零残留；三技能**无**其他内容锚串（565-585 行锚串只覆盖 open/design/build/verify/archive/tdd/code-review/subagent-driven/git-worktrees）。

## 关键决策

### D1 纯内联压缩，不新增辅助文件

- 备选 A（拆分重型参考到 `testing-patterns.md` 等辅助文件）被否：安装器 manifest 逐文件登记（`manifest.json` 每 path 一条），新增文件扩大变更面到安装器契约＋随包用例＋资产计数断言；`mirror_equal` 仅比对 SKILL.md，辅助文件不受结构守护；writing-skills 低频加载，token 收益边际。
- 备选 B（纯内联压缩，选定）：零文件增删，manifest 不动，安装器行为不变。"100+ 行重型参考拆分"保留为 writing-skills 内的既有规则，约束未来技能。

### D2 校验器三守卫的形态

1. **迁移注记零残留（absence）**：对 6 个显式路径（3 技能 × 2 树的 SKILL.md）`grep -F '未随本仓库迁移'`，命中即 FAIL。目标为显式文件清单而非目录递归扫描——归档后主规格与 memory 合法含该字样，不得误伤。函数显式 `return 0` 收尾（记忆坑：shell 检查函数返回值）。
2. **字符口径锚串（contains）**：writing-skills 双树含 `tr -d` 与 `wc -m`。锚串不以 `--` 开头（记忆坑：contains_all 前导连字符）。
3. **场景重跑绑定句锚串（contains）**：writing-skills 双树含 `workflow-pressure-scenarios.md` 与 `重跑`。
- 全部用既有 `grep`/`test` 外部命令，**零新增外部命令**，不触碰唯一命令清单与两份沙箱白名单（其已单一来源化于 core:38）。
- 每个守卫配对"注入必红＋干净必绿"契约用例；同步契约套件的硬编码计数断言（记忆坑：实际总数与硬编码计数脱节）。

### D3 校验器不做硬字符数阈值断言

- 字符上限登记在 writing-skills 正文内（编辑指导＋可判命令），校验器只锚定口径存在。理由：硬数值断言脆弱，合理的内容增长会假红；数值合规由"技能编辑 → 场景重跑"行为闭环背书。
- 阈值（去空白字符，随本次瘦身后基线设定）：
  - 常规技能（流程/纪律/支撑）：≤ 5000
  - 方法论参考型（writing-skills）：≤ 7500
  - 本次瘦身后全仓 13 技能须全部合规。

### D4 场景重跑范围：本变更重跑全部 9 个场景

- 文本压缩影响的是全树代理遵从，无法先验限定"相关场景"子集；9 个场景即行为契约全集，全量重跑最稳妥。绑定条款写入规格（相关性无法判定时重跑全部），本变更按全集执行。
- 结果记录：`openspec/changes/slim-workflow-skills/scenario-rerun.md`，按既有"结果记录"格式（逐字回答摘要＋逐条 PASS/FAIL＋逐字理由归类）。
- 任一场景 FAIL：停止、回退该处措辞、复跑——不带着 FAIL 进入待归档。

### D5 压缩红线（不得丢失的语义）

- parallel-agents 保留：Codex 适配注记行（含 5 个现行工具名）、dot 决策流程图、代理提示结构四要素、"何时不该用"边界。
- systematic-debugging 保留：铁律与四阶段结构、"3 次修复失败质疑架构"、红旗清单、合理化表、坑位即时入库（`.ai/memory` 格式）。
- writing-skills 保留：TDD 映射、SDO（含 description 反工作流捷径的实测理由）、形式匹配失败类型表、合理化免疫工具、微测措辞 5 条、测试类型分型、部署清单。压缩目标：迁移注记并为一行、单例化示例、去重"停下/铁律"重复段。
- 全部改动为措辞与示例层，不新增/删除任何行为规则。

### D6 验证链（严格）

1. 契约套件（新守卫注入/干净配对）先行红后绿。
2. 四副本同步后现验：`mirror_equal`（跑 core 即覆盖）、适配注记计数=1、废弃工具名零残留、资产树与工作树逐字一致。
3. 9 场景全量重跑（D4）。
4. `bash scripts/validate-workflow.sh --require-openspec` 全量门禁；`openspec validate --all --strict --no-interactive`（CLI 缺失时装到已忽略 `.ai-local` 并临时扩展 PATH，不跑 init/update）。
5. 安装器套件 `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest scripts.tests.test_install_workflow scripts.tests.test_install_ai_workflow`，串行、后台长跑，不带超时武断截断；umask-002 检出环境在 merge/checkout 后、跑套件前重跑权限规范化（dirs/files 644、两个可执行 755）。
6. 终验链启动后仓库零编辑（记忆坑：套件运行期间提交产生时序伪影）。

## 风险与边界

| 风险 | 处置 |
|---|---|
| 压缩措辞意外丢失校验锚定语义 | 三技能仅 parallel-agents 有工具名锚定（D5 红线保留）；镜像与注记计数由 core 现验兜底 |
| 压缩改变代理遵从（场景重跑 FAIL） | D4：停止回退该处措辞，不带 FAIL 归档 |
| absence 检查误伤合法含该字样的文档 | 检查只命中 6 个显式 SKILL.md 路径（D2） |
| 契约套件计数断言脱节 | D2 同步计数；套件单跑约 5 分钟，长跑用后台任务 |
| 资产树内容与工作树失同步 | 四副本由同一份内容＋路径前缀改写生成，同步后逐字 diff 复核 |

## 备选方案摘要

- 拆辅助文件（否，D1）；校验器做字符数硬断言（否，D3）；新增第 10 个施压场景覆盖"技能编辑"（否——本变更不改技能行为语义，9 场景重跑已背书，扩场景属范围膨胀）；连带处理低价值审查项（否，proposal 非目标）。
