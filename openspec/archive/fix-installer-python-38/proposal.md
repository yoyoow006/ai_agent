# 修复便携 AI 工作流安装器的 Python 3.8 兼容性

模式: 标准
状态: 已归档

## Why

在 Ubuntu 20.04 / Python 3.8.10 环境中，`scripts/install-ai-workflow.sh` 在参数解析前以退出码 1 失败。已复现的错误来自 `scripts/lib/install_ai_workflow.py:599`：

```text
TypeError: unsupported operand type(s) for |: 'type' and 'type'
```

`from __future__ import annotations` 只能延迟普通注解求值；`JournalEntry = _CreatedFile | _CreatedDirectory | _UpdatedFile` 是模块加载时立即执行的类型别名赋值，而类型按位合并需要 Python 3.10+。现有 CLI 契约测试 `test_help_succeeds` 在当前环境已经失败，证明这是安装命令的运行时缺陷。

第一次确认后已应用该最小修复；随后运行完整安装器测试，又暴露两个 Python 版本事实：

- `scripts/lib/install_ai_workflow.py:536` 调用 `Path.is_relative_to()`，该 API 需要 Python 3.9+，导致合法目标预览与安装继续以内部错误失败。
- `scripts/tests/test_install_ai_workflow.py` 有 11 处括号形式的多个 context manager 写法，该语法需要 Python 3.10+，导致完整回归在 Python 3.8 无法全绿。

诊断时临时 monkeypatch `Path.is_relative_to` 后，同一 Python 3.8 进程对空目标执行 `--dry-run` 成功且未创建资产，证明安装器下一个实际阻断点就是该 API。完整回归当前为 57 例：13 failures、63 errors，绝大多数 traceback 均指向 `Path.is_relative_to`。这属于实施中发现范围扩大，已暂停继续修改，等待对修订方案的一次确认。

修订范围实施后，完整 57 例安装器回归耗时 923.620 秒，仅剩 2 个失败且均为同一陈旧断言：安装后的契约套件实际输出 `Ran 79 tests ... OK (skipped=2)`，而 `scripts/tests/test_install_ai_workflow.py:398` 仍硬编码期待 `Ran 70 tests`。活动测试与可复用资产中的 `test_validate_workflow.py` SHA-256 完全一致，且资产同步测试通过，说明不是安装内容错配，而是计数断言未随测试集更新。这需要一行测试事实修正，属于验证范围扩大，已再次暂停，等待确认。

## What Changes

- 将 `JournalEntry` 的运行时类型别名改为 Python 3.8 可求值的 `typing.Union`。
- 为源目录包含判断增加 Python 3.8 可用的路径 helper，用 `Path.relative_to()` + `ValueError` 表达 `Path.is_relative_to()` 语义。
- 将安装器测试中 11 处括号多 context manager 语法改为 Python 3.8 支持的逗号列表形式，仅消除测试语法兼容性，不改变测试断言或注入行为。
- 将安装器回归中的陈旧契约计数从 70 更新为实际且全部通过的 79。
- 不改变安装参数、输出、退出码、清单、事务行为或资产内容。
- 复用现有失败的 `--help` 契约测试作为回归测试，不新增重复测试。

## Impact

- 受影响文件：`scripts/lib/install_ai_workflow.py`、`scripts/tests/test_install_ai_workflow.py`。
- 用户影响：Python 3.8 本地机器可以继续执行安装命令，而不是看到 Python traceback。
- 兼容性：Python 3.10+ 行为保持不变；Linux `renameat2` 事务边界仍按既有文档执行。
- 本地整合策略：当前目录的 `.git` 是空目录且不是可用 Git 仓库，无法创建 feature 分支；将在当前工作区直接实施，生产与测试文件均先备份到 `/tmp`，完成后用 targeted diff、文件清单和测试验证变更边界。
