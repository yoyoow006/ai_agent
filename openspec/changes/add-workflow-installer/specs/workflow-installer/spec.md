# workflow-installer 规范 delta

## ADDED Requirements

### Requirement: 一键安装
安装脚本 SHALL 以 `bash scripts/install-workflow.sh <目标路径>` 一条命令把全套工作流资产（CLAUDE.md、13 技能、ai-kb 空白骨架、openspec 骨架、校验脚本）复制到目标项目。
#### Scenario: 空目标项目安装
- **WHEN** 对一个不含任何工作流资产的目录执行安装
- **THEN** 全部资产落位且目录结构正确（含 .gitkeep 空目录占位），脚本退出码为 0
#### Scenario: 目标路径无效
- **WHEN** 目标路径不存在或不是目录
- **THEN** 报错并以退出码 2 结束，不创建任何目录
#### Scenario: 无参数调用
- **WHEN** 不带参数或传 --help 调用脚本
- **THEN** 打印用法说明（含 --force 语义），退出码 2

### Requirement: 冲突防护
安装脚本 SHALL 在复制前扫描目标路径的冲突文件；存在冲突时默认逐一列出并中止退出（非零退出码）；仅当传入 `--force` 时覆盖，且每个被覆盖文件先备份为 `<原名>.bak`。
#### Scenario: 已有 CLAUDE.md
- **WHEN** 目标项目已存在 CLAUDE.md 且未传 --force
- **THEN** 安装中止，输出冲突文件清单与 --force 用法提示
#### Scenario: 强制覆盖
- **WHEN** 传入 --force 且目标存在同名文件
- **THEN** 原文件备份为 <原名>.bak 后完成安装

### Requirement: 装后自检
安装脚本 SHALL 在复制完成后于目标路径运行 `./scripts/validate-workflow.sh`，全绿才算安装成功；有红项则报告并以非零退出码结束。
#### Scenario: 安装完成即验证
- **WHEN** 资产复制完成
- **THEN** 目标项目校验脚本全绿（未装 openspec CLI 的环境下 CLI 两项自动跳过仍视为全绿）

### Requirement: 零依赖可移植
安装脚本 SHALL 仅依赖 bash 与 cp/mkdir 等基础工具，不依赖 openspec CLI、不使用新版 git/bash 特性，可在旧环境运行。
#### Scenario: 无 CLI 裸机安装
- **WHEN** 在未安装 openspec CLI 的机器上执行安装
- **THEN** 安装与装后自检完整成功

### Requirement: 目标项目初始化适配
安装脚本 SHALL 为目标项目写入通用占位版 `openspec/project.md`（提示用户填写本项目上下文），ai-kb 的 memory 为空骨架；其余资产（CLAUDE.md、技能、rules 路由表、kb 总览、AGENTS.md、校验脚本）原样安装。
#### Scenario: 通用化内容
- **WHEN** 安装完成
- **THEN** 目标 project.md 含项目上下文占位提示而非本仓库特定描述，memory 目录为空骨架
