# 共享 memory 按模块拆分,落实既有目录约定

模式: 标准
状态: 待归档

## Why

`.ai/memory/workflow.md` 现有 56 条/约 200 行,所有模块踩坑堆在一个文件;`memory/README.md` 与 `.ai/README.md` 早已约定"按模块保存",但从未落实。逐条核对:安装器域(便携安装器契约模块)条目 32 条,占 57%——检索时必须在无关条目里过滤,且每次追加都要读写全文件。

## What Changes

1. 新建 `.ai/memory/installer.md`,承接安装器域 32 条:来源变更为 `add-workflow-installer`(2)、`工作流端到端验证(临时项目 add-greeting)`(3,源于安装器端到端验证)、`install-portable-ai-workflow`(16)、`fix-installer-python-38`(1)、`remove-installer-business-knowledge`(1)、`install-codex-workflow-yuxiaor`(5)、`add-installer-upgrade-path`(4)。
2. `.ai/memory/workflow.md` 保留其余 24 条(工作流治理、校验器、Git 基线/远程/安全、test-login、openspec 流程等)。
3. **条目正文逐字不动**,只做整条移动;各文件内保持原有时间顺序;两文件均无总标题(与现格式一致)。
4. 机械校验:两文件 `^## ` 计数之和 = 56(32+24);移动前后全部条目标题+坑/解行拼接 diff 为空;`bash scripts/lib/validate-workflow-core.sh` FAIL=0(审查 VQ-SM02 更正:原路径漏 lib/ 前缀)。
5. 规格化:`shared-ai-workflow-infrastructure` 新增 ADDED Requirement「共享 memory 按模块文件维护」,把 README 既有约定升为主规格要求(归档三写与断点恢复按模块落盘/读取)。

## Impact

- 知识层:检索与追加成本下降;后续安装器坑写 `installer.md`、流程坑写 `workflow.md`。
- 无运行时、无治理语义变化(README 约定的执行,非新规则;规格化只是把既有约定固化为可校验要求)。
- 安装资产不受影响(assets 的 memory 只随包 README)。
- 本地整合策略(建议):feature 分支,归档后本地 `--no-ff` 合回 main 并推送(沿用上一变更同款授权口径,本次确认一并授权)。
