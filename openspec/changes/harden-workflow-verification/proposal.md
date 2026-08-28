# 验证面加固：压力场景、mutation 与镜像豁免

模式: 标准
状态: 构建中

## Why

P1 完成后的三项验证面缺口（审计 P2-5/P2-6 + Verify 残余风险）：

1. **高风险流程路径无压力场景**：`workflow-pressure-scenarios.md` 现有 7 场景中仅 R/Q/S/X 覆盖工作流行为；worktree 原子顺序（design/build 的"先提交明确文件→切回基线→挂载未检出分支"）、archive 的 delta 合并与取消处置、manifest 中途 STALE 三个最易出错的路径完全无行为测试——而 `writing-skills` 技能自身要求技能用施压场景做红绿。
2. **mutation 仅 4 类**：`policy_ok` 正则表缺"快速模式自动提交""归档跳过校验""标准模式免确认实现"三类回退的守护（预检证实三条新正则对现有 12 份策略文件零假阳性）。
3. **镜像豁免前缀信任**：`> **Codex 执行环境` 开头的任意内容行都会被 mirror_equal 豁免（verify-quality 残余风险）；CI 动作按 tag 钉（CQ-2 可选加固未做）。

## What Changes

- **新增 3 个压力场景**（W/A/M，与既有 R/Q/S/X 同结构）：
  - W：严格实现前 worktree 原子顺序（催促直接挂已检出分支/在 main 实现）；
  - A：归档 delta 合并规则＋用户取消处置（复制目录代替合并、顺手自行取消并删分支）；
  - M：审查中途 manifest STALE（催促沿用旧结论）。
- **mutation 扩展**：`policy_ok` 新增 3 条禁令正则（预检零假阳性）；新增 9 个 mutation 检查（3 条注入句 × 入口＋对应技能双运行时）。
- **镜像豁免加固**：新增"适配注记登记数"检查——`^> \*\*Codex 执行环境` 前缀行全仓计数必须等于登记值 1；出现新的同前缀语义行即校验失败，强制显式登记。
- **CI SHA 钉**：checkout/setup-node 从 `@v4` tag 钉改为 commit SHA（`11d5960a…# v4.4.0`、`49933ea5…# v4.4.0`，同主版本、不引入大版本升级）。
- 压力契约 `contains_all` 检查同步纳入 W/A/M 关键词。

## Impact

- 修改 5 个文件：`scripts/workflow-pressure-scenarios.md`（+assets 副本）、`scripts/lib/validate-workflow-core.sh`（+assets 副本，字节一致）、`.github/workflows/validate.yml`。
- 不改：治理入口、技能正文、`.gitignore`、`manifest.json`、两个 Python 工具、安装器。
- 预期校验计数：main 现 172 → 新增 9 mutation＋1 登记数检查 → 182；变更活跃期间另 +2（本变更 proposal 两项）。
- 本地整合策略（明示）：全绿并归档后本地 `--no-ff` 合回 main 并复验；**推送与 CI 观察另行单独授权**。

## 用户已确认决策

- 2026-08-28 提问轮：本轮仅做"验证面加固"（含镜像豁免加固与 CI SHA 钉两个新候选）；安装器 upgrade 另行立项（严格模式）。
