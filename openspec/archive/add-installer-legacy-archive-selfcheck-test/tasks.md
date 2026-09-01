# Tasks——补安装器 legacy 归档自检回归用例

> 前置：feature 分支 `feature/add-installer-legacy-archive-selfcheck-test`，主会话直执，TDD（对新用例而言"红"= 先证明其能捕获现状行为：注入伪造 FAIL 无法实现，故红验证采用行为锁定的等价形式——用例写好后先在真实安装器上跑通即为"锁定成立"；如需红绿，可临时破坏断言确认会失败）。

## 1. [x] 新增用例并验证锁定有效

> 证据：单用例 OK（31.5s，一装一检）；红性检查——期望标签临时改为不存在值 → FAILED，还原 → OK。

- 文件：`scripts/tests/test_install_workflow.py` → `LegacyLayoutTests.test_legacy_archive_without_index_fails_selfcheck_then_recovers`（按 design D1-D3）。
- 验证：
  - `python3 -B -m unittest -v scripts.tests.test_install_workflow` → 全绿（含新用例，证明当前行为与契约一致）；
  - 红性检查：临时把断言的期望 FAIL 标签改成不存在的标签（或删掉 back-fill 步骤）→ 用例必须失败 → 还原。证明用例不是恒真。

## 2. [x] 回归

> 证据：`python3 -B -m unittest -v scripts.tests.test_install_workflow` → Ran 8 tests OK；`--fast` 门禁 PASS=193 FAIL=0 SKIP=0。

- `python3 -B -m unittest -v scripts.tests.test_install_workflow` 全绿；
- `bash scripts/validate-workflow.sh --fast` → 全绿（工作树含新用例与变更目录）。

## 3. Verify

- freeze manifest → 一次全 diff 综合审查（reviewer 双 verify）→ findings 处置至零未决。

## 4. Archive

- 合并 delta 到 `openspec/specs/workflow-installer/spec.md`；proposal 置`已归档`、目录移入归档、追加索引行；
- memory：存量目标坑条目补"已加回归用例"标注；
- 归档后全量门禁全绿；提交；用户明示后合并。

## 本地整合策略

feature 分支主会话直执；构建提交随带工作区既有的 memory 新条目；main 不动直至用户明示合并。
