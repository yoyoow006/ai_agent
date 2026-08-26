# 安装 Codex AI 工作流到 yuxiaor_prj_2025

模式: 严格
状态: 构建中

## Why

用户要求把本仓库的 Codex AI 助手流程安装到 `/home/shitou/workspace/src/yuxiaor_prj_2025`。该输入路径中的 `/home/shitou/workspace/src` 是指向 `/media/shitou/石头/wksource` 的符号链接；便携安装器契约拒绝含符号链接的目标路径，因此必须使用无符号链接的真实目标 `/media/shitou/石头/wksource/yuxiaor_prj_2025`。

目标目录已有旧版 `AGENTS.md`，且与安装清单中的 Codex 通用入口内容不同；`.ai/`、`.codex/`、`openspec/` 与工作流校验脚本均不存在。安装属于工作流治理变更，并写入当前仓库沙盒之外的目标目录，故按严格模式执行。

## What Changes

- 使用既有 `scripts/install-ai-workflow.sh --assistant codex` 安装共享 `.ai` 核心、空白 OpenSpec 基线、工作流校验入口和 Codex 单侧适配。
- 安装前把目标旧版 `AGENTS.md` 原子重命名为 `AGENTS.pre-codex-workflow.md`，保留原字节和元数据，避免安装器覆盖用户内容。
- 目标 `.gitignore` 由安装器按受管块策略追加/更新；不修改目标嵌套业务仓库。
- 不安装 Claude 适配，不替换目标现有 `CLAUDE.md`，不执行 Git 初始化、提交、推送、依赖安装或联网操作。
- 本仓库仅在隔离 worktree 中记录本次严格流程产物；目标目录不是 Git 工作树，回滚依赖安装器事务和旧入口备份。

## Impact

- 目标真实根目录：`/media/shitou/石头/wksource/yuxiaor_prj_2025`。
- 目标将新增共享 `.ai/`、Codex `.codex/`、空白 `openspec/` 与 `scripts/` 工作流资产；预览结果为 52 个创建、1 个 `.gitignore` 更新。
- 旧 `AGENTS.md` 将保留为 `AGENTS.pre-codex-workflow.md`，安装后的 `AGENTS.md` 来自显式安装清单。
- 目标现有 `CLAUDE.md`、`REVIEW.md`、`docs/`、`.idea/` 和全部嵌套业务仓库保持不写入。

## Acceptance Evidence

- 目标旧入口 SHA-256：`74d7b6cd7d755cb07b04f205e5b6beef9ca7c7412379c2bbd9db166f1bac47cc`。
- 初始目标 `.gitignore` SHA-256 为 `bec10e5dc357805b65436e39e33433be69f6366bd88d336ffb1c94b69b6b581f`；Task 1 fail-fast 发现确认后变更为 `8c87e32e6d72973f1f46ab5b69d6f7e97fb99aa25e7847612942f6a39437e7ca`，用户已确认接受该 490 字节现状作为受保护基线。
- 在临时目录按目标 `.gitignore` 状态执行安装器 dry-run 成功：`created=52 updated=1 unchanged=0 dry_run=1`。
