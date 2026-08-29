# 安装器知识分层规范

## Purpose

约束 AI 工作流安装工具源仓库与目标项目知识的边界，确保仓库只维护通用安装器、工作流和空白登记骨架，不携带目标项目的业务事实。

## Requirements

### Requirement: 安装工具仓库不得跟踪业务项目知识

仓库 SHALL 只保留工作流框架、安装器、测试和通用共享骨架；业务项目卡、业务契约、业务 memory、业务 registry 登记和业务 workspace 配置 SHALL NOT 出现在当前树或 reachable Git 历史。

#### Scenario: 检查 designated 业务路径

- **WHEN** 检查业务契约、除 README 外的项目卡、指定业务 memory、业务 review 清单和 workspace 配置路径
- **THEN** 这些路径不出现在当前 tracked 树
- **AND** 任一 reachable commit 的树中也不包含这些路径

### Requirement: 通用项目登记能力必须保留

仓库 SHALL 保留空白 `registry.json`、通用项目登记说明、事实查询工具及其测试，使目标项目安装后可自行登记自身项目事实。

#### Scenario: 查询空白 registry

- **WHEN** 解析 `.ai/kb/projects/registry.json`
- **THEN** `schema_version` 为 `1` 且 `projects` 为空数组
- **AND** `.ai/tools/tests/` 中的事实工具测试通过

### Requirement: 共享文档不得保留业务路由

`.ai/kb/overview.md`、`.ai/rules/index.md` 与 `.ai/tools/README.md` SHALL 只描述通用工作流、安装器和工具能力；项目查询示例 SHALL 使用非业务占位符。

#### Scenario: 扫描共享文档

- **WHEN** 检查共享文档的业务模块表、路由行和具体业务查询示例
- **THEN** 相关业务段落已移除或替换为通用占位符
- **AND** 通用工具命令与安全边界说明保留

### Requirement: 清理不得破坏安装器与工作流

业务知识移除 SHALL NOT 改变安装器运行时代码、资产清单、公共入口或测试语义；清理后 SHALL 通过 OpenSpec、事实工具、安装器资产契约和严格工作流门禁。

#### Scenario: 运行严格验证

- **WHEN** 清理和历史重建完成
- **THEN** `openspec validate --all --no-interactive` 通过
- **AND** `bash scripts/validate-workflow.sh --require-openspec` 末尾 `FAIL=0`
- **AND** Git 分支为 `main`、工作区 clean 且无 remote

### Requirement: 删除必须遵守不可逆授权边界

系统 SHALL NOT 在未获得两次明确确认前删除 tracked 业务内容或重建历史；执行后 SHALL NOT 声称存在迁移备份。

#### Scenario: 用户选择不另存

- **WHEN** 用户确认不迁移方案并完成严格模式两次确认
- **THEN** 指定业务内容只从本仓库删除
- **AND** 不创建迁移副本、外部备份或 remote
