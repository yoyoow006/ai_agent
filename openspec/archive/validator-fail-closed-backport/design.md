# 设计：校验器 fail-closed 加固回流

## Context

meta 库（`yuxiaor_prj_2025`）在 Codex 下完成 `commit-meta-workflow-hardening`（2026-08-31，严格模式已归档），产出 5 处 fail-closed 修复与 6 个回归测试。本源仓库的对应文件在其后又有独立演进（技能瘦身、场景 I 闭合），与 meta 库版本呈双向差异（core 差异 126 行）。本变更是单向回流：把 fail-closed 修复移植到本仓库现行代码，并把加固版随资产模板发布给未来安装目标。

## Decisions

### 1. 选择性移植，不整体拷贝

逐函数移植 3 处（wrapper 两段、core 两个函数）+ 1 份测试适配；不整体替换文件。理由：本地 core 含 meta 库没有的新增检查（近期场景闭合与瘦身改动），整体拷贝会回退本地能力。meta 库侧无需反向同步——它是修复发源地，且其版本较旧，下次升级随安装器覆盖。

### 2. 归档枚举采纳 Bash glob 实现，而非修补 find

以 `dotglob`/`nullglob` glob 枚举（函数内保存、设置并恢复 shopt 状态）替代 `find -printf`，配 `mktemp` 中转文件与 printf/sort/sed/awk/cmp 逐步退出码检查。理由：
- 可移植：Bash 3.2 兼容，消除 GNU 专有依赖（本地在 Linux 上不触发，但资产模板会装到 macOS 等环境）；
- fail-closed：任何一步工具错误即判失败并清理临时文件；
- 符号链接拒绝：直接子项任何 `-L` 即失败，堵住「链接绕过 1:1 索引」。

替代方案（否决）：保留 `find` 仅去 `-printf`——`find | sort` 管道仍无退出码检查，且 find 语义下符号链接只是被静默排除而非拒绝。

### 3. 符号链接语义收紧视为规格演进而非破坏

本地现行 `find -type d` 静默忽略符号链接；新语义判 FAIL。当前仓库 `openspec/archive/` 无符号链接（实测核对），无存量影响；收紧方向与「严格 1:1」条款一致，delta 规格已声明该 SHALL。

### 4. 运行副本与资产模板三对文件同步

`scripts/validate-workflow.sh`、`scripts/lib/validate-workflow-core.sh`、`scripts/tests/test_validate_workflow.py` 与 `scripts/ai-workflow-assets/shared/scripts/` 下镜像必须同批同步（当前逐字节一致，是既有不变量）。`manifest.json` 只记路径与 mode、无哈希（已核对），内容变更不需动账本；`workflow-pressure-scenarios.md` 与本修复无交集，不动。`scripts/hooks/pre-push` 透传 wrapper 结果，自动继承修复，不改。

### 5. 测试按本地基设适配移植

6 个测试（非 GNU find、目录符号链接、sort 错误、跳过计数 grep 错误、明细渲染 sed 错误、废弃名扫描错误）沿用 meta 库场景意图，fixture 与 stub 机制按本地套件现状适配（find stub 拒绝 `-printf`、grep/sed 错误注入等）。

## Alternatives

- 整体拷贝 meta 库三文件：会回退本地新增检查，否决。
- 仅修运行副本、不动资产模板：未加固版本继续随安装器扩散，与变更目的相悖，否决。
- 把 fail-closed 收敛为「套一层 set -e / pipefail」：shell 语义下管道与短路仍会吞非最后命令的失败，不可靠；meta 库实践已证明逐步显式检查是可控方案，否决。

## Risks and Boundaries

- 移植与本地新增检查的交互风险：以完整回归兜底（unittest 契约套件 + 全量 `validate-workflow.sh` + 涉及资产树的安装器套件）。
- 行为收紧（符号链接拒 FAIL）对未来仓库操作新增约束：规格已声明，无存量影响。
- wrapper/core 输出文案新增 FAIL 行：不改变顶层 PASS/FAIL/SKIP 字段语义与汇总行末位约定（delta 规格条款约束）。
- 不触碰业务项目、不产生外部副作用；`openspec/plan` 由 Design 阶段产出，Build 前须第二次确认。
