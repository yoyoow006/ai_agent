# Delta Spec: shared-ai-workflow-infrastructure

## ADDED Requirements

### Requirement: 契约测试基设不得污染安装器资产树

为统计或校验而加载随包契约套件（如 `exec_module` 动态加载资产副本）的测试基设 SHALL NOT 在 `scripts/ai-workflow-assets/` 写入任何文件（含 `__pycache__`/`*.pyc`）。资产 manifest 的物理枚举一致性 SHALL 在套件以任意通行方式（带或不带 `-B`）运行时均成立。

#### Scenario: 无 -B 手工复跑安装器套件

- **WHEN** 维护者不带 `-B` 运行 `python3 -m unittest scripts.tests.test_install_ai_workflow`
- **THEN** 套件不为统计目的在资产树产生 `__pycache__`
- **AND** `test_manifest_exactly_enumerates_sorted_physical_assets` 不因测试自身的中间产物失败
