# Design——补安装器 legacy 归档自检回归用例

## 关键决策

### D1 断言"恰好单一 FAIL"而非仅"包含"

`fail_lines == ["[FAIL] 归档索引与目录 1:1"]` 逐行相等断言：证明信号精确（无其他连带红项、不误报安装损坏）。这是本用例的核心价值——若未来某改动让 legacy 目标混入第二个红项，用例会响亮失败并暴露语义漂移。

### D2 恢复步骤直接复跑目标 `--fast`，而非重跑安装器

bash 安装器对任何已存在的 manifest 路径都计冲突（`install-workflow.sh:128` `[ -e ]` 即冲突），重装需 `--force` 且会为每个文件产生 `.bak`——把恢复断言与安装器 --force 语义纠缠只会引入噪音。补救路径的真实使用者操作就是"改数据后复跑自检"，直接 `bash scripts/validate-workflow.sh --fast`（cwd=目标）最忠实。

### D3 预置目录放最小 proposal.md

空目录在真实 Git 中不可存续（克隆即丢），预置 `# 旧变更 / 模式: 标准 / 状态: 已归档` 三行 proposal.md 还原真实形态；归档目录内部内容不被 core 校验（proposal 状态检查只扫 `openspec/changes/`），不影响断言纯度。

### D4 放入 LegacyLayoutTests 类

与 `test_legacy_ai_kb_requires_force_then_backed_up` 同类（legacy 目标布局语义），文件头注释同步补一句覆盖说明。

## 替代方案

- **教安装器自动 back-fill 索引**：改变生产行为且替用户写归档元数据，超出"补回归用例"的请求；如未来要做属独立标准变更。
- **在便携安装器套件（test_install_ai_workflow）加同款用例**：该套件单轮约 20 分钟，且其目标模型不同（单侧+profile）；今日踩坑路径是 bash 安装器，先锁最痛路径，便携侧需要时再说。

## 风险与边界

- 安装器行为若未来改为"legacy 归档也整体备份/自愈"（类似 ai-kb 旧布局路径），本用例会失败——这正是契约锁定的目的，届时随行为变更同步改规格与用例。
- 目标内 `--fast` 在测试机需要 flock/mktemp 等基础工具（既有 fresh 用例的装后自检已依赖同等环境），无新增环境要求。
- 不验证范围：便携安装器升级路径的 legacy 归档行为（D4 替代方案所述，另行裁定）。
