# 变更提案：add-workflow-installer

状态: 已归档
创建: 2026-08-16

## 为什么
工作流 v1 目前只能靠手动复制文件迁移到其他项目，易漏易错（空目录、执行位、文件清单都靠人记）。需要一个一键安装脚本，把本仓库验证过的整套工作流资产可靠地落到任意目标项目。

## 做什么
- 新增 `scripts/install-workflow.sh`：`bash scripts/install-workflow.sh <目标项目路径>` 一键安装全套工作流资产
- 安装范围（用户已确认）：CLAUDE.md + 13 技能（`.claude/skills/`）+ ai-kb 空白骨架 + openspec 骨架（通用版 project.md、AGENTS.md、四目录）+ `scripts/validate-workflow.sh`
- 冲突策略（用户已确认）：默认扫描冲突即中止并列出；`--force` 时先备份为 `<名>.bak` 再覆盖
- 装后自检：在目标项目运行校验脚本并要求全绿
- 目标项目的 `openspec/project.md` 安装通用占位版（提示用户填写本项目上下文），不照搬本仓库特定描述

## 影响
- 新增文件，不修改任何现有资产；本仓库自身流程不受影响
- 依赖：纯 bash + cp/mkdir，零外部依赖（沿用全局约束）
