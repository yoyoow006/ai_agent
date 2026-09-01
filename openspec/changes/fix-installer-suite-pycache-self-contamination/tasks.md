# Tasks——修复安装器套件无 -B 自污资产树

> 前置：feature 分支 `feature/fix-installer-suite-pycache-self-contamination`，主会话直执，TDD。

## 1. [x] 红：自污复现测试

- 文件：`scripts/tests/test_install_ai_workflow.py` 新增 `test_shipped_contract_count_leaves_no_asset_pycache_without_dash_b`（子进程按 D2 模拟无 `-B` 调用 helper，断言资产树零 `__pycache__`，前后清理残留）。
- 验证：`python3 -B -m unittest -v scripts.tests.test_install_ai_workflow.PortableAssetManifestTests`（或该用例所属类）确认新用例红。

## 2. [x] 绿：加载期字节码抑制

- `_shipped_contract_test_count` 的 `exec_module` 外围临时 `sys.dont_write_bytecode = True`，finally 恢复。
- 完成判据：新用例转绿；资产树无残留。

## 3. [x] 回归

> 证据：带 -B `Ran 83 tests OK`（exit 0）；**不带 -B（陷阱原场景）`Ran 83 tests OK`（exit 0）**，跑后资产树 `__pycache__` 计数 0；`--fast` 门禁 PASS=193 FAIL=0 SKIP=0。首轮并行双跑的两处失败均非代码问题：mode 断言为 merge 重置权限的 umask-002 环境复发（chmod 后消），超时为并行争抢（串行后消），已记 memory。

- `python3 -B -m unittest -v scripts.tests.test_install_ai_workflow` → 全绿（82+1）；
- `python3 -m unittest scripts.tests.test_install_ai_workflow`（**不带 -B**，陷阱原场景）→ 全绿，资产树无 `__pycache__` 残留（本轮终验即本变更的目标行为）；
- `bash scripts/validate-workflow.sh --fast` → 全绿。

## 4. Verify

- freeze manifest → 一次全 diff 综合审查（reviewer 双 verify）→ 处置 findings 至零未决。

## 5. Archive

- 合并 delta 到主规格；proposal 置`已归档`、目录移入 `openspec/archive/`、追加索引行；
- 更新 `.ai/memory/installer.md` 相应条目标注已修；
- 归档后全量门禁 `bash scripts/validate-workflow.sh` 全绿；提交；用户明示后合并。

## 本地整合策略

feature 分支主会话直执；main 不动直至归档完成、用户明示合并。
