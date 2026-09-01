# Design——修复安装器套件无 -B 自污资产树

## 关键决策

### D1 根因修法：加载期字节码抑制，而非枚举过滤

在 `_shipped_contract_test_count` 的 `exec_module` 外围临时置 `sys.dont_write_bytecode = True`（finally 恢复原值）。对比备选"物理枚举过滤 `__pycache__/*.pyc`"：

- 自污源头唯一且明确（`exec_module` 触发 `SourceLoader.get_code` 写字节码），一处抑制覆盖资产树上全部现有与未来的枚举/一致性检查；
- 过滤法只护单个断言，污染文件仍落盘，任何新增的资产树遍历检查都要各自防御；
- `-B` 环境下 `sys.dont_write_bytecode` 本已为 True，守护为无害冗余，无行为差异。

### D2 回归测试用子进程模拟"无 -B"

套件自身通常以 `-B` 运行（CI/门禁约定），进程内 `sys.dont_write_bytecode` 已 True 无法复现陷阱。测试以子进程运行内联程序：显式 `sys.dont_write_bytecode = False`、环境剥离 `PYTHONDONTWRITEBYTECODE`、`sys.path` 插入仓库根后实例化 `InstalledWorkflowValidationTests` 调用 helper，输出资产树 `__pycache__` 探测结果；主测试断言 `NONE` 并在前后清理资产树残留（隔离既有污染）。子进程 import `scripts.tests` 包会在 `scripts/tests/` 落 `__pycache__`——该路径被根 `.gitignore` 忽略且门禁有"Python 缓存路径已忽略"检查，不在资产树、无影响。

### D3 分类

测试运行时代码修改，未命中严格条件；低风险、单文件、无资产副本、不分发——标准模式小任务，主会话直执，Verify 做一次全 diff 综合审查。

## 替代方案

- **物理枚举过滤**：见 D1，治标留污染，不采。
- **文档加注 `-B` 必需**：已在上一变更 tasks.md 完成（7a5ccc1），但陷阱机制仍在，纯文档不消除误导性失败，不充分。
- **改用 `importlib.util.cache_from_source` 预检清空**：过度工程。

## 风险与边界

- helper 在 `-B` 下行为不变（冗余守护）；异常路径经 finally 恢复全局标志，不泄漏到套件其余用例。
- 子进程测试新增约 1 个 Python 启动（秒级），安装器套件总时长影响可忽略。
- 不验证范围：不评估 `PYTHONDONTWRITEBYTECODE` 以外环境变量组合；不改 `workflow-installer`（bash 双运行时安装器）侧任何内容。
