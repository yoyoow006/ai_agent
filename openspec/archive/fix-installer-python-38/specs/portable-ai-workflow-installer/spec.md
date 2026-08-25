## ADDED Requirements

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
