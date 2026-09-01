# 补安装器 legacy 归档自检回归用例

模式: 标准
状态: 已归档

## Why

2026-09-01 存量目标实际踩坑（memory/workflow.md 已登记）：harden-gate-honesty-and-coverage 新增"归档索引与目录 1:1"后，升级/安装到**有历史归档目录但从未建 README 索引**的目标时，装后自检 `--fast` 报红退出码 1。这是预期数据契约信号（非安装损坏），但安装器测试只有 fresh 目标用例（fresh 归档为空、检查 vacuous PASS），该行为无契约锁定——信号精确性与补救路径都可能静默漂移。

## What Changes

- `scripts/tests/test_install_workflow.py` 的 `LegacyLayoutTests` 新增用例：目标预置 `openspec/archive/old-change/`（无 README 索引）→ 断言安装器退出码 1、输出中 `[FAIL]` 行**恰好等于** `[FAIL] 归档索引与目录 1:1`（精确单一信号）；随后在目标内 back-fill 一行索引、复跑 `./scripts/validate-workflow.sh --fast` → 断言退出码 0（一次性补救路径）。
- delta 规格：`workflow-installer` 的"装后自检"需求 MODIFIED，补一个 Scenario 锁定 legacy 归档目标上的信号与恢复语义。

## Impact

- 仅测试文件（源仓专属，无资产副本）+ 规格；不改安装器与校验器行为。
- 套件时长增加约一次安装 + 一次目标内 `--fast`（秒级），与既有 fresh 用例同量级。
- 同时把工作区已登记的 memory 条目（存量目标坑）随构建提交入库。
