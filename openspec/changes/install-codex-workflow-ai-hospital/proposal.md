# 安装 Codex AI 工作流到 ai_hospital

模式: 严格
状态: 构建中

## Why

用户要求把本仓库的 Codex AI 助手工作流安装到 `/home/yoyoo/wksoft/sources/gitdemo/ai_hospital`。该输入路径包含符号链接，真实目标为 `/home/yoyoo/windsk/ubuntu_dir/sources/gitdemo/ai_hospital`。目标目录存在但不是 Git 仓库，且当前没有 `AGENTS.md`、`.codex/`、`.ai/`、`openspec/`、`.claude/` 或 `CLAUDE.md`。

目标中已有用户文件 `docs/好实用合作协议I51.2.doc`，当前 SHA-256 为 `9a76ae560637818368ddbbaa298409747210a066c0c061224c257b798b25787f`。最新离线预览显示安装器将创建 55 个工作流文件，`updated=0`、`unchanged=0`，该用户文件不在计划内。安装涉及工作流治理和外部目录写入，按仓库风险路由属于严格模式。

## What Changes

- 在写入前重新解析真实路径并复核目标状态，确认没有入口冲突或计划外重叠。
- 使用既有 manifest 驱动安装器，只安装共享 `.ai/` 核心、OpenSpec 基线、校验脚本和 Codex 单侧 `.codex/` 适配。
- 不安装 `.claude/` 或 `CLAUDE.md`，不初始化 Git，不创建提交，不联网，不安装依赖，不修改嵌套业务仓库。
- 保留并校验目标中的 `docs/好实用合作协议I51.2.doc` 及其他非计划文件。
- 安装后在目标根目录运行完整工作流 required 门禁和 OpenSpec 严格校验，并复核安装幂等预览。
- 经用户确认规范后，先产出严格模式独立实施计划；第二次确认通过后才写入目标。

## Impact

- 写入目标：`/home/yoyoo/windsk/ubuntu_dir/sources/gitdemo/ai_hospital` 下的 `.ai/`、`.codex/`、`openspec/`、`scripts/`、`AGENTS.md`、`.gitignore`。
- 保护目标：`docs/好实用合作协议I51.2.doc` 不读取正文、不修改、不删除；写入前后校验 SHA-256。
- 不影响源仓库 `main` 的业务内容；本流程记录保存在隔离 worktree 的 OpenSpec 变更中。
- 目标不是 Git 仓库，因此不会产生目标侧分支、提交或远程操作。

## Verification Evidence

- 源仓库隔离 worktree 基线：`bash scripts/validate-workflow.sh --fast` 通过，`PASS=197 FAIL=0 SKIP=0`。
- 源仓库 OpenSpec 基线：`/home/yoyoo/.nvm/versions/node/v20.19.4/bin/openspec validate --all --strict --no-interactive` 通过，`10 passed, 0 failed`。
- 目标预览：`bash scripts/install-ai-workflow.sh --target /home/yoyoo/windsk/ubuntu_dir/sources/gitdemo/ai_hospital --assistant codex --dry-run` 通过，计划 `created=55 updated=0 unchanged=0`。
- 用户已于 2026-09-13 明确确认“确认”，规范确认完成；独立实施计划见 `openspec/plan/install-codex-workflow-ai-hospital.md`。

## Build Incident Reconfirmation

首次实际安装按已确认命令执行，但安装器退出码 1，仅输出 `ERROR: installation failed`。事后核查目标仍只剩 `docs/好实用合作协议I51.2.doc`，SHA-256 未变，dry-run 仍为 55 个 CREATE，说明事务已回滚且无部分安装。

系统化调试确认根因：目标与源同在 `fuseblk` 文件系统，安装器的 Linux `renameat2(..., RENAME_NOREPLACE)` 在该文件系统返回 `EINVAL`。在同一文件系统的自动清理临时目录中，先预创建清单推导出的 35 个空父目录、重建安装计划后再执行安装器，55 个文件创建成功。该适配会先写空目录再调用安装器，超出原“唯一写入命令”边界，必须获得用户重新确认。

用户已于 2026-09-13 回复“确认”，环境适配确认完成。

## Empty-Parent Reconfirmation

用户确认 35 个清单目录后，预创建脚本按清单顺序创建了 4 个空目录（`.ai`、`.ai/kb`、`.ai/kb/projects`、`.ai/memory`），随后在 `.ai/prompts/agents` 停止。原因是清单列出的是 manifest 文件直接父目录，遗漏了层级中必须存在的 `.ai/prompts` 与 `.codex/skills` 两个中间目录。当前目标只有这 4 个空工作流目录、既有 `docs` 及合作协议；文档 SHA-256 未变。继续安装需要把空父目录集合修正为 37 个，并先复核已创建 4 个目录均保持空目录。

用户已于 2026-09-13 回复“确认”，37 目录修正确认完成。
