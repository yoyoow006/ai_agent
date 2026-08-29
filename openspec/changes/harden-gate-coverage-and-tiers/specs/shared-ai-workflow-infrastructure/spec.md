## MODIFIED Requirements

### Requirement: 工作流校验必须在 CI 自动运行

本仓库 SHALL 配置 CI，在每次推送到 main 和每个拉取请求上自动运行 `bash scripts/validate-workflow.sh --require-openspec`，并在运行前安装 OpenSpec CLI（`@fission-ai/openspec`）。CI SHALL 另以独立步骤现跑安装器套件 `python3 -B -m unittest -v scripts.tests.test_install_ai_workflow`，该步骤 SHALL NOT 被跳过且任一失败 SHALL 使 CI 任务失败。校验输出中任一 `FAIL` SHALL 使 CI 任务失败以阻断合并；仓库自带的必需测试 SHALL NOT 在 CI 中被跳过。CI 配置 SHALL 仅存在于本仓库，SHALL NOT 进入安装器 `manifest.json` 或随安装资产分发。

#### Scenario: 推送触发自动校验

- **WHEN** 有新提交推送到 main 分支或针对本仓库打开拉取请求
- **THEN** CI 自动检出代码、安装 OpenSpec CLI 并运行 `bash scripts/validate-workflow.sh --require-openspec`
- **AND** 随后独立步骤运行 `python3 -B -m unittest -v scripts.tests.test_install_ai_workflow`
- **AND** 任务退出码与校验汇总一致，任一 FAIL 或测试失败使任务失败

#### Scenario: 安装器套件回归被 CI 拦截

- **WHEN** 安装器或其测试资产发生使 `scripts.tests.test_install_ai_workflow` 任一用例失败的变更
- **THEN** CI 在合并前失败,不得依赖人工终验清单才发现

## ADDED Requirements

### Requirement: 校验器外部命令清单必须单一来源

校验器使用的外部命令清单 SHALL 由 `scripts/lib/validate-workflow-core.sh` 以 `--print-external-commands` 模式唯一发布;校验相关的测试沙箱(源仓契约测试与安装器套件)SHALL 在运行时从该模式解析白名单,SHALL NOT 维护第二份手写命令元组。core 新增依赖任一外部命令时 SHALL 同步其清单,否则受限 PATH 沙箱用例 SHALL 失败暴露不一致。

#### Scenario: core 新增外部命令

- **WHEN** 维护者向 core 新增一个清单外的外部命令调用
- **THEN** 受限 PATH 契约用例因缺少该命令而失败
- **AND** 更新 `--print-external-commands` 清单为唯一修复点,无需同步第二份白名单

#### Scenario: 安装目标内自包含

- **WHEN** 随资产安装的校验器与契约测试在目标项目运行
- **THEN** 白名单从目标内随包 core 的 `--print-external-commands` 解析
- **AND** 不依赖源仓任何未随包文件

### Requirement: 校验器必须防并发并提供本地推送防护

公共校验入口 SHALL 在可用 `flock` 的环境以排他锁串行化同一工作树的并发校验,第二实例 SHALL 立即失败退出而非与首实例互踩;`flock` 不可用时 SHALL 降级为无锁继续并输出提示。仓库 SHALL 提供 `scripts/hooks/pre-push` 钩子,在推送前现跑秒级 core 结构校验,任一 FAIL SHALL 阻断本次 push;钩子 SHALL 为源仓自愿启用(`git config core.hooksPath scripts/hooks`),SHALL NOT 进入安装资产。

#### Scenario: 两实例并发

- **WHEN** 一个校验实例运行期间另一实例在同工作树启动
- **THEN** 第二实例立即报错退出,两个实例不产生交叉的 mutation 假失败

- **WHEN** 运行环境没有 flock 工具
- **THEN** 校验降级为无锁执行并在输出中提示,功能不受影响

#### Scenario: 推送前本地拦截

- **WHEN** 已启用钩子的工作树在 main 门禁为红时执行 git push
- **THEN** pre-push 运行 core 校验失败并阻断 push
- **AND** 未启用钩子的环境不发生任何行为变化
