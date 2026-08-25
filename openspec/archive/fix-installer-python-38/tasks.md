# 任务

## 1. 建立并保留失败基线

- [x] 已运行：`python3 -B -m unittest -v scripts.tests.test_install_ai_workflow.InstallAiWorkflowCliTests.test_help_succeeds`
- 预期：初始 Python 3.8.10 下失败，stderr 显示第 599 行 `unsupported operand type(s) for |`。
- [x] 已运行：`python3 -B -m unittest scripts.tests.test_install_ai_workflow`
- 结果：修复类型别名后为 57 例、13 failures、63 errors；主要根因是 `Path.is_relative_to` 需要 Python 3.9+。
- [x] 诊断：临时 monkeypatch `Path.is_relative_to` 后运行安装器 `--dry-run`，退出码 0 且目标未创建资产。

## 2. 实施已确认的第一处兼容修复

- [x] 备份：`cp scripts/lib/install_ai_workflow.py /tmp/install_ai_workflow.before-python38-fix.py`
- [x] 修改 `scripts/lib/install_ai_workflow.py`：
  - 从 `typing` 导入 `Union`。
  - 将 `JournalEntry` 改为 `Union[_CreatedFile, _CreatedDirectory, _UpdatedFile]`。
- [x] 复跑 `test_help_succeeds`，预期 1 个测试通过。

## 3. 实施范围扩大后的兼容修复

- [x] 备份：`cp scripts/tests/test_install_ai_workflow.py /tmp/test_install_ai_workflow.before-python38-fix.py`
- [x] 修改 `scripts/lib/install_ai_workflow.py`：
  - 增加 Python 3.8 可用的 `_is_relative_to(path, parent)` helper。
  - 将源目录包含判断改为使用该 helper。
- [x] 修改 `scripts/tests/test_install_ai_workflow.py`：
  - 将 11 处括号形式多 context manager 改为 Python 3.8 支持的逗号列表形式。
  - 不改变 mock、断言或测试语义。
- [x] 复核两个 targeted diff，确认只包含上述兼容性变更和 OpenSpec/收尾产物。

## 4. 修正陈旧完整回归计数

- [x] 已运行：`python3 -B -m unittest -v scripts.tests.test_install_ai_workflow`
- 结果：57 例中仅 2 失败；安装后契约套件实际 `Ran 79 tests` 且 `OK (skipped=2)`，失败均为期待陈旧值 70。
- [x] 已核对：活动 `scripts/tests/test_validate_workflow.py` 与可复用资产同名文件 SHA-256 一致。
- [x] 将 `scripts/tests/test_install_ai_workflow.py` 中的期待计数从 70 改为 79。

## 5. 验证

- [x] `python3 -B -m unittest -v scripts.tests.test_install_ai_workflow.InstallAiWorkflowCliTests.test_help_succeeds`，预期 1 个测试通过。
- [x] `bash scripts/install-ai-workflow.sh --help`，预期退出码 0、包含 `--target` 与 `--assistant`、stderr 为空。
- [x] 在 Python 3.8 下对临时空目录执行合法 `--dry-run`，预期退出码 0、输出计划、目标不出现安装资产。
- [x] `python3 -B -m unittest scripts.tests.test_install_ai_workflow`，预期 57 个安装器测试全部通过。
- [x] `python3 -B -m py_compile scripts/lib/install_ai_workflow.py scripts/tests/test_install_ai_workflow.py`，预期退出码 0。

## 6. 收尾

- [x] 记录 `.ai/memory/workflow.md` 踩坑条目，说明 `from __future__ import annotations` 不延迟类型别名赋值，并列出 Python 3.8 缺失的 `Path.is_relative_to` 与括号 context manager 语法。
- [x] 更新本变更状态为`待验证`，整理验证证据与残余风险。
