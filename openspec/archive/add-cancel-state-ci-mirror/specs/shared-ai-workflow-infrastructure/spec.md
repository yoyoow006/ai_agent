# CI 自动校验 delta

## ADDED Requirements

### Requirement: 工作流校验必须在 CI 自动运行

本仓库 SHALL 配置 CI，在每次推送到 main 和每个拉取请求上自动运行 `bash scripts/validate-workflow.sh --require-openspec`，并在运行前安装 OpenSpec CLI（`@fission-ai/openspec`）。校验输出中任一 `FAIL` SHALL 使 CI 任务失败以阻断合并；仓库自带的必需测试 SHALL NOT 在 CI 中被跳过。CI 配置 SHALL 仅存在于本仓库，SHALL NOT 进入安装器 `manifest.json` 或随安装资产分发。

#### Scenario: 推送触发自动校验

- **WHEN** 有新提交推送到 main 分支或针对本仓库打开拉取请求
- **THEN** CI 自动检出代码、安装 OpenSpec CLI 并运行 `bash scripts/validate-workflow.sh --require-openspec`
- **AND** 任务退出码与校验汇总一致，任一 FAIL 使任务失败

#### Scenario: OpenSpec CLI 预装后不得 SKIP

- **WHEN** CI 环境已安装 `@fission-ai/openspec`
- **THEN** `--require-openspec` 模式下的 OpenSpec 严格校验与仓库自带必需测试实际运行，不出现因工具缺失导致的 SKIP

#### Scenario: CI 配置不随安装器分发

- **WHEN** 安装器向目标项目安装工作流资产
- **THEN** 目标项目不获得 CI 配置文件，`manifest.json` 不含 `.github/` 路径
- **AND** 目标项目需要 CI 时另行评估，不由本变更引入
