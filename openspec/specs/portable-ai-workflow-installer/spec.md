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
