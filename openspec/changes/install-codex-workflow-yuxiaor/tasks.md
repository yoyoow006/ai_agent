# 任务范围

> 严格模式：本文件当前是范围清单；四件套确认后由 Design 产出独立实现计划，计划确认前不写入目标目录。

## 1. Open

- [x] 核对用户路径、真实路径、符号链接和目标存在性。
- [x] 核对安装器用法、清单内容、冲突策略、事务与验证契约。
- [x] 核对目标 `AGENTS.md`、`CLAUDE.md`、`.gitignore`、嵌套仓库与工作流目录现状。
- [x] 在临时目录完成只读 dry-run 预览。
- [x] 获得用户对四件套的第一次确认。

## 2. Design

- [x] 读取 `design` 技能并产出独立实现计划。
- [x] 明确保份、安装、失败回滚和验证的精确命令。
- [x] 获得用户对独立计划的第二次确认。

## 3. Build

- [x] 复核目标状态并处置确认后的 `.gitignore` 基线变化。
- [x] 保留旧 `AGENTS.md` 并安装 Codex 工作流到真实目标。
- [x] 记录安装器输出与目标文件状态。

## 4. Verify

- [ ] 运行目标 `scripts/validate-workflow.sh --require-openspec`。
- [ ] 运行目标 `openspec validate --all --strict --no-interactive`。
- [ ] 验证旧入口备份哈希不变，并检查安装边界。
- [ ] 按严格要求执行任务级审查和双阶段独立审查。

## 5. Archive

- [ ] 处理审查意见并归档 OpenSpec 变更。
- [ ] 汇报安装位置、验证证据、备份位置与未验证范围。
