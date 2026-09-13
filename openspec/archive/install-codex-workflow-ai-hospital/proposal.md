# 安装 Codex AI 工作流到 ai_hospital

模式: 严格
状态: 已归档

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

## Build Verification Evidence

- 用户确认 37 目录修正后，预检确认原有 4 个工作流目录保持无文件，创建剩余 33 个空目录，总计 37 个目录、0 个工作流文件。
- 适配后 dry-run：`created=55 updated=0 unchanged=0 dry_run=1`。
- 实际安装：`created=55 updated=0 unchanged=0 dry_run=0`。
- 幂等 dry-run：`created=0 updated=0 unchanged=55 dry_run=1`。
- 目标 required 门禁：`PASS=120 FAIL=0 SKIP=0`；套件内部设计性跳过 4 项为源仓专属能力，不影响门禁计数。
- 目标 OpenSpec 严格校验：`2 passed, 0 failed`。
- 最终清单核对：55 个 manifest 文件、1 个既有用户文档、0 个 `.git`/`.claude`/`CLAUDE.md` 禁止项；用户文档 SHA-256 仍为 `9a76ae560637818368ddbbaa298409747210a066c0c061224c257b798b25787f`。
- 目标校验器产生 1 个允许的本地锁文件 `.ai-local/.validate.lock`；未发现其他计划外工作流文件。

## Task Review Evidence

- 任务级审查单元：`external-target-install-safety`。
- Manifest ID：`2b5f2be2f51fd57cdc35d19c3d30a702f15b2038dba346730d57442263518837`；comparison base 输入 `main`，解析为 `1fbad77089b52c424bc06c3b0759048d4618ef9e`。
- Reviewer 读取前与结论前均执行 manifest verify 并得到 `VALID`。
- 审查结论：PASS；未发现 Critical、Important 或 Minor finding。
- 已独立核对真实路径、无符号链接、37 个目录集合、55 个文件内容、ledger、Codex-only 边界、非 Git 目标、用户文档哈希和禁止项。
- 未验证范围与残余风险：目标非 Git 且可被并发修改；`fuseblk` 将文件模式映射为 `0777`，未审计 mount ACL 与其他本地用户写权限；任务级 reviewer 未重放三项目标验证，依赖构建时证据；未读取用户合作文档正文。

## Verify Evidence

- 规格符合性独立审查：Manifest `d7339f800f576168a0b5e74180d8a6156a1dddcfcc9c5e33c385b5b60229d541`，comparison base `main` 解析为 `1fbad77089b52c424bc06c3b0759048d4618ef9e`；读取前与结论前均 VALID，结论 PASS，无 finding。
- 代码与操作质量独立审查：同一 Manifest `d7339f800f576168a0b5e74180d8a6156a1dddcfcc9c5e33c385b5b60229d541`；发现 1 条 Minor 状态措辞不一致。
- Minor 修复复审：新 Manifest `ac6ffa67b5cc6582d93781dd795a6184372d41959ecb0fe05084a6d89c7224b4`；差异仅 `design.md` 与实施计划状态措辞，`verify-quality-001` 已 resolved。
- 终验目标幂等预览：`created=0 updated=0 unchanged=55 dry_run=1`。
- 终验目标 OpenSpec：`2 passed, 0 failed`。
- 终验目标 required 门禁：`PASS=120 FAIL=0 SKIP=0`。
- 终验目标不变量：55 个 manifest 文件、0 个禁止项、用户文档哈希匹配。
- 终验源仓 OpenSpec：`11 passed, 0 failed`。
- 终验源仓 required 门禁：`PASS=200 FAIL=0 SKIP=0`。第一次源仓 required 曾因未导出隔离 HOME 导致 Git dubious ownership 环境失败；失败测试用正确 HOME 单独复验通过，随后完整重跑通过。
- 最终源侧 diff 仅 5 个治理产物，`git diff --check` 通过，工作区 clean。
- 未验证范围与残余风险：目标非 Git 且可被并发修改；`fuseblk` 宽权限/ACL 未审计；未读取用户合作文档正文。

## Archive Evidence

- Delta 已合并到 `openspec/specs/codex-workflow-target-installation/spec.md`。
- 知识沉淀：`.ai/kb/overview.md` 与 `.ai/memory/installer.md` 记录 fuseblk 空父目录适配；未新增模块，`.ai/rules/index.md` 无需路由变更。
- 严格独立计划已移动为 `openspec/archive/install-codex-workflow-ai-hospital/plan.md`。
- 归档后 OpenSpec：`10 passed, 0 failed`。
- 归档后 `bash scripts/validate-workflow.sh --archive-light`：`PASS=197 FAIL=0 SKIP=0`。
- 归档后未合并分支、未推送、未清理 worktree；整合方式等待用户选择。
