## MODIFIED Requirements

### Requirement: 工作流校验必须在 CI 自动运行

本仓库 SHALL 配置 CI，在每次推送到 main 和每个拉取请求上自动运行 `bash scripts/validate-workflow.sh --require-openspec`，并在运行前安装 OpenSpec CLI（`@fission-ai/openspec`）。CI SHALL 另以独立步骤现跑安装器套件 `python3 -B -m unittest -v scripts.tests.test_install_ai_workflow` 与 Bash 安装器套件 `python3 -B -m unittest -v scripts.tests.test_install_workflow`；两步 SHALL NOT 被跳过且任一失败 SHALL 使 CI 任务失败。安装器套件内部的耗时优化 SHALL NOT 免除真实用例执行、失败传播或源仓专属覆盖。校验输出中任一 `FAIL` SHALL 使 CI 任务失败以阻断合并；仓库自带的必需测试 SHALL NOT 在 CI 中被跳过。CI 配置 SHALL 仅存在于本仓库，SHALL NOT 进入安装器 `manifest.json` 或随安装资产分发。

#### Scenario: 推送触发自动校验

- **WHEN** 有新提交推送到 main 分支或针对本仓库打开拉取请求
- **THEN** CI 自动检出代码、安装 OpenSpec CLI 并运行 `bash scripts/validate-workflow.sh --require-openspec`
- **AND** 随后独立步骤分别运行 `python3 -B -m unittest -v scripts.tests.test_install_ai_workflow` 与 `python3 -B -m unittest -v scripts.tests.test_install_workflow`
- **AND** 任务退出码与校验汇总一致，任一 FAIL 或测试失败使任务失败

#### Scenario: OpenSpec CLI 预装后不得 SKIP

- **WHEN** CI 环境已安装 `@fission-ai/openspec`
- **THEN** `--require-openspec` 模式下的 OpenSpec 严格校验与仓库自带必需测试实际运行，不出现因工具缺失导致的 SKIP

#### Scenario: CI 配置不随安装器分发

- **WHEN** 安装器向目标项目安装工作流资产
- **THEN** 目标项目不获得 CI 配置文件，`manifest.json` 不含 `.github/` 路径
- **AND** 目标项目需要 CI 时另行评估，不由本变更引入

#### Scenario: 安装器套件回归被 CI 拦截

- **WHEN** 安装器、随包校验资产或其测试发生任一用例失败
- **THEN** CI 在合并前失败，不得依赖人工终验清单才发现

### Requirement: 契约套件必须支持有界并行执行

顶层契约套件 SHALL 通过仓库自带的零第三方依赖执行器并行运行相互独立的用例。源仓库与随包安装资产 SHALL 分发同一执行器，且随包 wrapper SHALL 与源仓 wrapper 保持等价的单一契约调用点；`WORKFLOW_TEST_JOBS=1` SHALL 完整回退为原串行 unittest 执行语义。默认并行度 SHALL 为 `min(CPU 核数, 8)`。执行器 SHALL 聚合每个用例的通过、失败、错误与跳过结果，任一用例失败或错误 SHALL 使套件退出码非零，失败明细 SHALL 完整保留且不得被并行输出吞没。执行器输出 SHALL 保持 wrapper 对 `... skipped` 行的统计与解析兼容，wrapper 成功路径 SHALL 透出实际运行的用例数。并行执行 SHALL NOT 引入共享可变状态或使多个用例写同一路径。

#### Scenario: 默认并行且失败传播

- **WHEN** 契约套件在默认并行度下运行且任一用例失败或错误
- **THEN** 套件以非零退出，失败用例名与错误明细完整可见
- **AND** 其余用例的结果仍被完整聚合

#### Scenario: 串行回退

- **WHEN** 设置 `WORKFLOW_TEST_JOBS=1`
- **THEN** 契约套件按原串行 unittest 命令执行
- **AND** 输出、退出码与跳过统计行为与回退前一致

#### Scenario: 安装目标使用随包并行执行器

- **WHEN** 安装器把工作流资产复制到目标项目并在目标内运行公共门禁
- **THEN** 目标使用随包 `run_validate_workflow_parallel.py` 执行契约套件
- **AND** manifest、物理资产与 wrapper 调用保持一致，不得静默退化为源仓专属路径或串行命令

#### Scenario: 成功输出保留审计计数

- **WHEN** 契约套件全部通过
- **THEN** wrapper 透出实际用例数与设计性跳过明细
- **AND** 顶层 PASS/FAIL/SKIP 汇总语义与末行口径不变

#### Scenario: 并行用例相互隔离

- **WHEN** 多个契约用例并行运行
- **THEN** 各用例使用独立临时目录与夹具，不发生交叉污染
- **AND** 不因并行引入非确定性失败

## ADDED Requirements

### Requirement: 安装器集成回归必须去除重复完整门禁

安装器集成测试 SHALL 保留每个 assistant 的真实资产落位、幂等安装、工具测试和完整公共门禁覆盖；同一 assistant 的单个集成路径 SHALL NOT 重复执行多份完整真实契约套件来验证可由一份执行结果证明的行为。required 模式缺少 OpenSpec CLI 的失败路径 SHALL 用独立 sentinel 探针验证 core 失败后 wrapper 仍实际调用契约套件并传播非零退出，SHALL NOT 通过跳过契约调用、测试专用后门或只检查最终退出码来缩短耗时。

#### Scenario: 每个助手保留一次真实完整门禁

- **WHEN** 安装器集成测试分别验证 codex 与 claude 单侧安装
- **THEN** 每个安装目标实际运行一次完整公共门禁并覆盖全部随包契约用例
- **AND** 用例数、允许的设计性跳过原因、工具测试与资产状态断言仍然生效

#### Scenario: required 缺 CLI 使用 sentinel 探针

- **WHEN** 安装目标缺少 OpenSpec CLI 且测试执行 `--require-openspec`
- **THEN** 探针显示 OpenSpec 缺失 FAIL、契约套件被实际调用且任务退出非零
- **AND** 探针不重复执行全部真实契约用例，也不修改真实安装目标断言所用的资产树

#### Scenario: 性能优化不得降低覆盖

- **WHEN** 随包 wrapper、并行执行器或安装器集成测试发生回退
- **THEN** CI 或仓库契约测试失败并指出漂移
- **AND** 不得以跳过安装器套件、缓存通过结果或删除源仓专属用例作为修复方式

