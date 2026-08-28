# 便携 AI 工作流安装器规范

## Purpose

约束 `scripts/install-ai-workflow.sh` 与 `scripts/lib/install_ai_workflow.py` 跨环境加载、入口契约、目标预览与事务行为，确保安装器在项目声明的本地 Python 上从参数解析、计划到回滚全链路可运行，且不因运行时类型语法、路径 API 或上下文管理器语法受限于特定 Python 版本。

## Requirements

### Requirement: 安装器应在 Python 3.8 上加载

安装器的公开命令 SHALL 在进入参数解析、预览或安装前，于项目声明的本地 Python 3.8 环境中完成模块加载，并且不得因为仅用于类型标注的语法失败。

#### Scenario: Python 3.8 请求帮助

- **WHEN** 用户在 Python 3.8.10 环境运行 `bash scripts/install-ai-workflow.sh --help`
- **THEN** 命令以退出码 0 输出既有 Usage
- **AND** stderr 不包含 Python traceback

#### Scenario: Python 3.8 预览安装

- **WHEN** 用户在 Python 3.8.10 环境对已存在目标目录运行合法 `--dry-run` 参数
- **THEN** 命令进入既有计划逻辑并以退出码 0 输出预览
- **AND** 目标目录内容不被写入

### Requirement: 安装器必须支持台账驱动的升级

安装器 SHALL 提供 `--upgrade` 模式，与 `--target`、`--assistant` 组合并支持 `--dry-run` 预览。安装与升级 SHALL 在安装器私有的 `.ai/installer-ledger.json` 中维护安装台账：记录每个 manifest 文件安装时的内容 SHA-256；`.ai/assistant-profile.json` 保持校验器契约格式不变。升级时对每个文件 SHALL 按以下规则行动：目标内容哈希等于台账哈希（未被目标修改）时替换为新版内容；等于新版内容时记 `UNCHANGED`；台账不匹配或无台账且内容不等于新版时记 `SKIPPED` 并继续处理其余文件；目标缺失的 manifest 文件 SHALL 记 `CREATED` 并写入新版内容与台账条目。已从新版 manifest 移除的文件 SHALL 仅在台账确认未被目标修改时删除，否则保留并报告。升级 SHALL 沿用安装的事务发布与回滚机制，台账更新 SHALL 与文件变更处于同一事务。目标已存在的助手入口文件 SHALL 与其他 manifest 文件适用同一台账规则：未被目标修改（台账命中）时可升级，已被目标修改时 `SKIPPED` 并报告（2026-08-28 用户裁定）。

#### Scenario: 未修改文件自动升级

- **WHEN** 目标中某 manifest 文件内容哈希等于台账记录且不等于新版内容
- **THEN** 升级将其替换为新版内容并输出 `UPGRADED`
- **AND** 同一事务内更新台账哈希

#### Scenario: 目标修改过的文件被跳过

- **WHEN** 目标中某 manifest 文件内容哈希不等于台账记录且不等于新版内容
- **THEN** 该文件保持原样并输出 `SKIPPED` 与差异提示
- **AND** 其余文件的升级继续执行

#### Scenario: 无台账旧安装首次升级

- **WHEN** 目标没有台账文件（旧版安装）
- **THEN** 内容等于新版的文件记 `UNCHANGED`，其余全部 `SKIPPED` 报告
- **AND** 升级完成后写入台账文件，后续升级按台账判定

#### Scenario: 已移除文件按台账清理

- **WHEN** 某文件存在于目标与台账但已不在新版 manifest
- **AND** 目标内容哈希等于台账哈希
- **THEN** 升级删除该文件并输出 `REMOVED`
- **AND** 哈希不匹配时保留并输出 `KEPT` 与报告

#### Scenario: 升级预览不写入

- **WHEN** 以 `--dry-run` 运行升级
- **THEN** 输出逐文件计划与汇总且零写入，退出码 0

#### Scenario: 升级中断回滚

- **WHEN** 升级事务在发布阶段失败或被中断
- **THEN** 目标文件与台账整体回滚到升级前状态，不出现半升级状态

#### Scenario: 入口文件按台账判定

- **WHEN** 目标已存在 `AGENTS.md` 或 `CLAUDE.md`
- **AND** 其内容哈希等于台账记录且不等于新版内容
- **THEN** 升级将其替换为新版并输出 `UPGRADED`
- **AND** 内容被目标修改过时保持原样并输出 `SKIPPED`，提示人工比对
