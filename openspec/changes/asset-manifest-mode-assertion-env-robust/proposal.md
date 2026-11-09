模式: 标准
状态: 待归档

# 资产清单模式断言环境无关化

## Why

`scripts/tests/test_install_ai_workflow.py` 的 manifest 模式断言（`test_manifest_modes_are_exact_and_match_files:236` 与 `test_parallel_runner_asset_is_manifested_and_byte_identical:244`）用工作树 stat 全量权限位比对 `0644/0755` 常量。本机 `git core.sharedRepository=true` + umask 0002 使 git 检出的工作树文件为 664/775（组写位为环境策略），断言在不含任何变更的干净 HEAD 上同样失败（2026-11-06 干净 worktree 探针已证明），长期产生假红并污染回归证据。安装器自身只消费 manifest 声明模式（`install_ai_workflow.py:267-288`），不读源工作树 stat——规范模式的真源是 git 索引（100644/100755），工作树 stat 是环境策略。

## What Changes

- `test_manifest_modes_are_exact_and_match_files` 改为双轨断言：manifest 声明模式必须等于 git 索引规范模式（`git ls-files -s`，未跟踪资产 fail-fast 报"未跟踪"）；工作树文件仅校验可执行位（user/group/other 任一 x 位组合与声明一致）不校验写位。
- `test_parallel_runner_asset_is_manifested_and_byte_identical` 的 `0o644` stat 断言同样改为 git 索引模式比对（该文件当前恰好 644 属偶然，与 :236 同为潜在环境失败）。
- 不改安装器运行时、manifest.json 内容与镜像资产。

## Impact

- 构建/验证：仅改测试断言逻辑；本测试文件不随安装资产镜像分发，无镜像同步。变更命中契约测试，标准层验证将升级 required。
- 风险：极低——断言从"环境敏感的强断言"收敛为"规范真源断言 + 可执行位一致性"，可执行位漂移（manifest 0755 ↔ 索引 100644）仍被捕获。

## Scope

### Included

- `scripts/tests/test_install_ai_workflow.py` 两处模式断言及其辅助函数。
- 本变更目录三件套。

### Excluded

- 不修改 `scripts/lib/install_ai_workflow.py`、`scripts/ai-workflow-assets/manifest.json`、镜像树与任何运行时代码。
- 不处理套件运行中 `__pycache__` 导致的枚举瞬态失败（另一独立现象，枚举断言单独运行与干净树均通过，暂不动）。

## Acceptance

- 本机（sharedRepository=true + umask 0002）`PortableAssetManifestTests` 全类通过；干净 worktree 探针同样通过。
- 反向锁定：人为把任一 manifest 资产的 git 索引模式从声明值改掉（如 100755→100644）时测试变红；未跟踪新资产时 fail-fast。
- required 层门禁、OpenSpec strict、diff-check 通过。

## Unverified scope

无（required 门禁、完整安装器套件与反向锁定覆盖全部断言路径；规范环境路径见 tasks 终局记录说明）。

## Residual risk

`core.fileMode=false` 场景下 git 索引不反映磁盘模式（本仓未启用，可执行位断言兜底）；套件运行中 `__pycache__` 枚举瞬态保持观察（本次全套件绿）。
