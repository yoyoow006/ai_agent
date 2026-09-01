# 修复安装器套件无 -B 自污资产树

模式: 标准
状态: 已归档

## Why

harden-gate-honesty-and-coverage 审查 F-1（delta 复审裁定为"基线既有、范围外的后续小修建议"，已登记 `.ai/memory/installer.md`）：无 `-B` 手工运行 `python3 -m unittest scripts.tests.test_install_ai_workflow` 时，`_shipped_contract_test_count` 的 `exec_module` 会把 `__pycache__` 写进 `scripts/ai-workflow-assets/shared/scripts/tests/`，且 `InstalledWorkflowValidationTests`（I）默认排序先于 `PortableAssetManifestTests`（P）——同一轮内自污后物理枚举必败 `test_manifest_exactly_enumerates_sorted_physical_assets`，报错指向资产 manifest 而非真因，具误导性。CI 与门禁均带 `-B` 不受影响，纯属手工复跑陷阱。

## What Changes

- `scripts/tests/test_install_ai_workflow.py` 的 `_shipped_contract_test_count`：加载随包套件期间临时置 `sys.dont_write_bytecode = True`，结束后恢复原值——根因消除自污源头。
- 同文件新增回归测试：子进程显式 `sys.dont_write_bytecode = False`（并剥离 `PYTHONDONTWRITEBYTECODE` 环境）调用该 helper，断言资产树零 `__pycache__`。
- delta 规格：`shared-ai-workflow-infrastructure` ADDED 一条"契约测试基设不得污染安装器资产树"。

## Impact

- 仅 `scripts/tests/test_install_ai_workflow.py`（源仓专属，无资产副本、不分发到目标）；不改安装器本体与校验器。
- `-B` 环境行为不变（`dont_write_bytecode` 已为 True，守护冗余无害）；CI 绿灯不受影响。
- 风险极低：测试代码局部修改，红绿证据 + 安装器套件双模式（带/不带 `-B`）全绿回归。
