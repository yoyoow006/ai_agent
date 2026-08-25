# 设计

## 决策

使用 `typing.Union[_CreatedFile, _CreatedDirectory, _UpdatedFile]` 表达 `JournalEntry`。该形式在 Python 3.8 与 3.10+ 都能立即求值，且只影响类型标注，不改变任何运行时分支。

源目录包含判断增加私有 helper：先调用 `Path.relative_to()`，捕获 `ValueError` 返回 `False`，否则返回 `True`。这保持 `target == resolved_source or ...` 的短路语义，并与 Python 3.9+ `Path.is_relative_to()` 的值语义一致。

测试文件只把括号形式的多个 context manager 改为等价逗号列表，不改变 mock、断言或测试边界，使完整回归可以在 Python 3.8 执行。

完整回归暴露的唯一剩余问题是指向安装后契约套件的总数断言。实际结果为 79 例全部通过、2 例按设计跳过；活动源文件与可复用资产字节一致，因此将硬编码 70 更新为 79，只修正测试事实，不放松任何通过/跳过条件。

## 替代方案

- 在 shell 启动器中检测 Python 版本并拒绝 3.8：会让已知可支持的本地环境继续不可用，而且用户仍需另装 Python。
- 强制要求 Python 3.10+：当前测试与执行环境就是 Python 3.8，且缺陷只来自一个类型别名，没有证据需要整体提升运行时要求。
- 给 shell 启动器增加复杂回退：不必要，Python 标准库已有跨版本类型表达。
- 只修安装器并放弃完整测试：无法满足 Python 3.8 支持的回归证据，也会留下测试套件自身不可运行的问题。
- 放宽或移除总数断言：会削弱对安装包测试集完整性的保护；仅更新为当前权威输出 79 更小且可复核。

## 风险与边界

- 生产代码仅修改类型别名、import 和源目录包含判断 helper；不改变事务、路径校验决策、manifest 或 CLI 契约。
- 测试文件做 context manager 语法兼容改写，并把陈旧计数 70 更新为 79；不改变被测行为或其余断言。
- `renameat2` 等 Linux 原子操作边界保持原状，本变更不扩大操作系统兼容性承诺。
- 当前源目录没有可用 Git 元数据，无法使用 Git 分支或 `git diff`；生产与测试文件均先保存 `/tmp` 副本，验证后分别复核 targeted diff。
