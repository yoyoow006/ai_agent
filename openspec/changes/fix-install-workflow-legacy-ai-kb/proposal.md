# 修复 install-workflow.sh 残留旧 ai-kb 布局导致安装必然失败

模式: 标准
状态: 待验证

## Why

用户报告（2026-08-31）：`bash scripts/install-workflow.sh <目标>` 报
`cp: 对 '<源>/.claude/ai-kb/kb/overview.md' 调用 stat 失败: 没有那个文件或目录`。

已复现并定位根因（证据见 design.md）：

- 知识层已于 2026-08-29 迁移到 `.ai/` 共享层（`943d914` 移除 `.claude/ai-kb/`、`.codex/ai-kb/` 平行正文，仅留重定向 README），且校验器 `legacy_ai_kb_body_absent` 强制禁止旧正文回归。
- `scripts/install-workflow.sh`（最后实质修改 `d473afa`，早于迁移）仍按旧布局复制 6 个已不存在的源文件，安装中途中止（退出码 1，目标残留半成品：双总纲+技能已落、知识层与校验套件缺失）。
- 同一脚本还有 3 处连带滞后：完全没装 `.ai/` 共享层；校验脚本只装单文件 `validate-workflow.sh`（如今依赖 `scripts/lib/validate-workflow-core.sh` 与 `scripts/tests/`，装后自检必然失败）；`openspec/project.md` 占位文案仍写"五阶段、知识库见 .claude/ai-kb/"。
- 该脚本无任何测试覆盖（`scripts/tests/` 只覆盖 Python 安装器与校验器），布局迁移后无门禁拦截。
- `openspec/specs/workflow-installer/spec.md` 的资产清单与 Purpose 也停留在旧布局，需同步 delta。

## What Changes

- 重构 `scripts/install-workflow.sh` 的资产复制段：源从"手维护的仓库活动树路径"改为 `scripts/ai-workflow-assets/{shared,claude,codex}` 资产树整体复制（与 Python 安装器同一单一来源，不解析 manifest.json，保持零依赖），使布局迁移后悬空引用在结构上不可能。
- **双运行时目标模型定型**（2026-08-31 构建中两次证据驱动重确认，用户终选"保留双装+自检降层"）：不生成 `.ai/assistant-profile.json`、不随附便携安装器文件（`scripts/lib/install_ai_workflow.py` 是随包套件的源仓标记，随附即被要求成为完整源仓）；装后自检改跑 `--fast` 秒级 core 结构校验，完整契约套件归源仓 CI。曾实测否决两方案："生成规范侧 profile"（随包套件 2 例失败放大为 10 例）、"附带便携安装器三件"（撞源仓标记：要求 git 已提交钩子与 CI 配置）。
- 迁移前旧布局残留（`ai-kb/{kb,rules,memory}` 含正文）：无 `--force` 明确中止指引，有 `--force` 整目录备份 `ai-kb.bak/` 后重装重定向入口——否则目标校验器 `legacy_ai_kb_body_absent` 必红。
- 保留既有契约：冲突默认中止/`--force` 逐文件 `<原名>.bak` 备份、memory 永不覆盖（`.ai/memory/`）、无效目标退出码 2、装后自检全绿才算成功。
- 新增 `scripts/tests/test_install_workflow.py` 契约测试 7 例（空装/无效目标/无参/--help/冲突中止/--force+memory 保护/旧布局残留）并挂入源仓 CI（`validate.yml` 新增步骤），补齐零覆盖缺口。
- delta 修订 `workflow-installer` 规格：资产清单对齐当前布局（`.ai/` 通用共享层 + 兼容重定向入口 + 校验套件含 lib/tests）、装后自检分层为 `--fast`、新增旧布局残留场景；Purpose 措辞随归档合并更新。

## Impact

- 变更文件：`scripts/install-workflow.sh`、`scripts/tests/test_install_workflow.py`、本变更四件套；不改 Python 安装器与校验器行为。
- 触及安装资产 → Verify 终验与归档后验证使用**全量门禁**（非 `--fast`）。
- 用户影响：README"方式二"第一条命令恢复可用；已用旧命令半装的目标项目**重跑并加 `--force`** 即修复（冲突文件逐个备份后补齐；memory 不覆盖；迁移前旧布局残留同样走 `--force` 整目录备份自愈）。

## 本地整合策略

feature 分支 `fix-install-workflow-legacy-ai-kb` 就地实施（当前工作区干净）；Verify 通过 → Archive 归档 → 合并回 main。推送需另行明确授权。
