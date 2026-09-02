# 变更：校验器 fail-closed 加固回流

模式: 严格
状态: 构建中

## Why

安装目标 `yuxiaor_prj_2025`（meta 库，codex profile）于 2026-08-31 深夜在 Codex 下以严格模式完成 `commit-meta-workflow-hardening`，修复了工作流校验器的 5 个 fail-open 坑（底层工具报错被当作「无匹配/空集合/无跳过」继续，门禁假绿）并沉淀 6 个 fail-closed 回归测试。该批修复**未回流本源仓库**：

- `scripts/validate-workflow.sh:88,91` 跳过计数 grep 与明细渲染 `grep|sed` 管道仍不查退出码；
- `scripts/lib/validate-workflow-core.sh` 的 `archive_index_ok`（约 :478）仍用 GNU 专有 `find -printf` 且 `2>/dev/null` 静默、管道各步无退出码检查；
- `retired_tool_names_absent`（约 :443）仍是 `grep … && return 1` 布尔短路，grep rc>1 被当「无匹配」；
- 6 个对应回归测试（`test_archive_index_does_not_require_gnu_find_printf` 等）全部缺失。

且运行副本与资产模板 `scripts/ai-workflow-assets/shared/scripts/` 逐字节一致，未加固版本会随安装器扩散到每个新目标库，让 meta 库踩过的假绿坑在下一个目标重演。

## What Changes

- wrapper `scripts/validate-workflow.sh`：契约套件跳过计数改为显式读取 grep 退出码（0/1 之外判 FAIL）并校验结果为非负整数；跳过明细渲染改用独立检查退出码的 `sed -n`，渲染失败计 FAIL。
- core `scripts/lib/validate-workflow-core.sh`：`retired_tool_names_absent` 改为 grep_status 三态 case（0 命中判失败、1 无匹配继续、其余判失败）；`archive_index_ok` 重写为 Bash glob 枚举（`dotglob`/`nullglob` 并保存恢复 shopt 状态）、拒绝 `openspec/archive/` 直接子项中任何符号链接、`mktemp` 中转并逐步检查 printf/sort/sed/awk/cmp 退出码，不再依赖 GNU `find -printf`。
- 测试 `scripts/tests/test_validate_workflow.py`：移植适配 meta 库的 6 个 fail-closed 回归测试（非 GNU find、目录符号链接、sort 错误、跳过计数 grep 错误、明细渲染 sed 错误、废弃名扫描错误）。
- 资产模板同步：`scripts/ai-workflow-assets/shared/scripts/` 下 core、wrapper、tests 三份镜像同步修改（manifest.json 仅记路径与权限、无哈希，无需变更）。
- memory 沉淀：回流结论与移植差异记入 `.ai/memory/workflow.md`。

## Impact

- 影响文件：`scripts/validate-workflow.sh`、`scripts/lib/validate-workflow-core.sh`、`scripts/tests/test_validate_workflow.py` 及三者在 `scripts/ai-workflow-assets/shared/scripts/` 的镜像；`openspec/specs/shared-ai-workflow-infrastructure/` 主规格（Archive 时合并 delta）。
- 行为收紧：归档目录出现符号链接从「静默忽略」变为判 FAIL（当前仓库 `openspec/archive/` 无符号链接，实测基线不受影响）；其余修复只把原假绿路径变为真实 FAIL，不改变任何健康路径的判定。
- 基线证据：2026-09-02 实测 `bash scripts/validate-workflow.sh --fast` 为 PASS=197 FAIL=0 SKIP=0，工作区干净；本变更以全绿保持为验收底线。
- 风险：本地校验器相对 meta 库修复基线已有新增能力（近期技能瘦身与场景闭合改动），须选择性移植而非整体拷贝，移植后以完整套件回归。

## 非目标

- 不调整 legacy 安装器 `install-workflow.sh` 的 `--force` `.bak` 备份机制（设计行为，另线评估）。
- 不调和场景 I root 入口冲突的规格分歧（已登记独立治理线）。
- 不对已安装目标做升级推送：meta 库本身即修复发源地；未来目标经安装器自动获得加固版本。
