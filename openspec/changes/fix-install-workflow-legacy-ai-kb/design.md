# Design — 修复 install-workflow.sh 旧布局残留

## 根因证据链

| # | 事实 | 来源 |
|---|---|---|
| 1 | 复现：装到空目标，`cp` 在首个 ai-kb 文件 stat 失败，退出码 1，目标残留半成品 | 本地复现 2026-08-31 |
| 2 | 脚本第 139-140、165-166 行复制 `$SRC_ROOT/.claude{,.codex}/ai-kb/kb/overview.md`、`rules/index.md` 等已删除路径 | `scripts/install-workflow.sh` |
| 3 | 旧正文于 `943d914`（2026-08-29）移除，`.claude/ai-kb/` 仅剩重定向 README；校验器 `legacy_ai_kb_body_absent` 禁止回归 | git log；`scripts/lib/validate-workflow-core.sh:362-371` |
| 4 | 脚本最后实质修改 `d473afa` 早于迁移；`scripts/tests/` 无该脚本任何测试 | git log；tests 目录 |
| 5 | 连带缺陷：未装 `.ai/` 层；校验套件只装单文件（缺 `lib/validate-workflow-core.sh`、`tests/`，装后自检必失败）；project.md 占位文案写"五阶段/旧 ai-kb 路径"；.gitignore 规则缺 `.claude/sdd`、`.worktrees` | 脚本 176-229 行 |
| 6 | 资产树 `scripts/ai-workflow-assets/{shared,claude,codex}` 是 Python 安装器的经验证单一来源，shared 31 文件含完整 `.ai/` 通用骨架与校验套件 | manifest.json；冒烟：`--assistant claude` 退出码 0、53 文件落位 |
| 7 | `workflow-installer` 规格资产清单与 Purpose 停留在旧布局（"五阶段、ai-kb 空白骨架"） | `openspec/specs/workflow-installer/spec.md` |

## 关键决策

### D1：资产源改为 ai-workflow-assets 资产树整体复制（选定）

- 备选 A（选定）：`shared+claude+codex` 三棵树 `cp -r` 到目标，与 Python 安装器同源；悬空引用结构上不可能，布局迁移自动跟进。
- 备选 B（否决）：委托 `install-ai-workflow.sh` 调用两次。Python 安装器契约是"每次恰好装一侧"（`--assistant codex|claude`），双跑会产生两份 ledger/profile 且绕过本脚本 `--force/*.bak` 冲突契约。
- 备选 C（否决）：废弃本脚本只留 Python 安装器。规格与 README 均以它为"一条命令双运行时"入口，且用户实际在用；废弃属能力删除，超出本缺陷范围。

### D2：不解析 manifest.json，保持零依赖

规格"零依赖可移植"要求仅 bash + cp/mkdir。直接遍历资产目录树复制，mode 由 `cp -r` 保留；manifest.json 仍归 Python 安装器契约使用。`.gitkeep` 空目录随树落位。

### D3：冲突与保护语义逐文件保留

- 保留：冲突默认列出并中止；`--force` 逐文件 `<原名>.bak`（旧版技能整目录 `.bak/` 行为随整树复制一并取消）；`.ai/memory/` 与既有 memory 语义统一为"只补缺，永不覆盖、不备份"；无效目标/用法错误退出码 2。
- 既有目标升级：用户已用坏命令半装的项目重跑新脚本即自愈（缺什么补什么）。

### D4：回归测试即防回归门禁

新增 `scripts/tests/test_install_workflow.py`（unittest，风格随 `test_install_ai_workflow.py`）：空装、无效目标、无参、冲突中止、--force 备份、memory 保护。空装用例就是本次缺陷的回归捕获器——若资产树或脚本再漂移，用例失败。不改校验器结构（避免扩大范围）。

### D5：双运行时目标与随包契约的架构矛盾及终局（构建中证据驱动，用户两次重确认）

构建中实测三层证据：随包契约套件（随资产分发、字节同步保护）的目标模型是"单侧+profile"——

1. 无便携安装器脚本的目标必须携带 profile（2 例 selected-only 失败）；
2. 生成 profile 则非选中侧门禁突变不被拒（失败 2→10 例）；
3. 随附便携安装器三件则 `scripts/lib/install_ai_workflow.py` 被识别为"源仓标记"，目标被要求拥有 git 已提交的 pre-push 钩子与 CI 配置（pre-push 用例在非 git 目标直接 ERROR）。

穷举证明双运行时目标不存在让 105 例全绿的配置。用户终选（2026-08-31）：**保留双装 + 自检降层**——目标不生成 profile、不随附便携安装器；装后自检改 `./scripts/validate-workflow.sh --fast`（秒级 core 结构校验，双运行时布局全绿）；完整契约套件与便携安装器套件保持源仓 CI 职责（`validate.yml` 新增 bash 安装器契约测试步骤）。收益：安装从 ~5 分钟降到秒级；代价：双运行时目标内跑全量校验会有源仓专属用例不适用（usage 与自检输出注明）。

### D6：迁移前旧布局残留的自愈路径

迁移前安装过的目标残留 `ai-kb/{kb,rules,memory}` 平行正文，会使目标校验器 `legacy_ai_kb_body_absent` 必红。处理：无 `--force` 时以专属错误中止并指引（不动用户文件）；有 `--force` 时各侧 `ai-kb/` 整目录备份为 `ai-kb.bak/` 后重装重定向入口。备份式清除而非合并迁移——旧正文归属用户知识，合并语义风险高，保留 `.bak` 供人工迁移。

## 风险与边界

- **范围**：只动 bash 安装器与测试；不改 Python 安装器、校验器、技能、总纲。project.md 占位文案取资产树内版本（若资产树版本也含旧措辞，任务 3 一并修正资产树并靠既有字节一致性核对同步）。
- **资产树完整性**：若资产树与活动树存在未覆盖一致性校验的漂移，靠空装 e2e + 装后自检兜底；发现缺口记录 finding，不就地扩校验器范围。
- **验证分层**：触及安装资产 → Verify 终验与归档后验证均跑**全量** `bash scripts/validate-workflow.sh`（规格"验证门禁按阶段分层"要求），不用 `--fast`。
- **非目标**：不统一两个安装器为单进程；不新增 ledger 能力到 bash 脚本；不改 README（装好后现有 README 命令自然恢复正确）。

## 失败路径

- 冲突未 --force → 列清单退出非零，目标零写入。
- 资产源缺失 → `cp` 失败按现有错误通道退出 1（此时为真实缺陷信号，测试会捕获）。
- 装后自检红 → 退出 1 并提示反馈维护者（现状语义保留）。
