# Tasks——门禁诚实性与覆盖加固

> 前置：feature 分支 `feature/harden-gate-honesty-and-coverage`，主会话直执。测试先红后绿（TDD，运行时行为）。

## 1. [x] 红：注记工具名契约测试

- 文件：`scripts/tests/test_validate_workflow.py`（沿用既有 fixture 复制 `WORKFLOW_FIXTURE_DIRECTORIES` 建仓的模式）。
- 用例：
  - fixture 中 `.codex/skills/parallel-agents/SKILL.md` 注记注入 `multi_agent_v1__spawn_agent` → 运行 core 必须出现对应 `[FAIL]`；
  - fixture 中资产树副本注入 `send_input` → `[FAIL]`；
  - 注记缺 `wait_agent`（替换为任意非现行名）→ `[FAIL]`。
- 验证：`python3 -B -m unittest -v scripts.tests.test_validate_workflow` 新用例红（FAIL 项缺失导致断言失败），其余不回归。

## 2. [x] 红：归档索引完整性测试

- 用例：fixture `openspec/archive/<名>/` 目录 + README 缺该行 → FAIL；README 有悬空行 → FAIL；重复行 → FAIL；空归档 + 无 README → PASS 不变。
- 验证：同上，新用例红。

## 3. [x] 红：套件内部跳过透明化测试

- 用例：fixture 契约套件含 `skipTest("...")` → wrapper 全量输出含"内部设计性跳过"注解与该原因；汇总行仍为末行（`PASS=\d+ FAIL=0 SKIP=\d+\s*\Z` 兼容）；顶层 SKIP 计数不含内部跳过。
- 验证：同上，新用例红。

## 4. [x] 绿：core 实现

> 实现注记：废弃名扫描限定 `*.md`/`*.toml`（契约对象是指导正文，且避免校验器资产副本 token 清单自引用）；`retired_tool_names_absent` 必须显式 `return 0`（无命中时末条 grep 退出码 1 会令检查恒 FAIL，实测踩坑）。

- 文件：`scripts/lib/validate-workflow-core.sh` + 资产副本 `scripts/ai-workflow-assets/shared/scripts/lib/validate-workflow-core.sh`。
- 实现 `retired_tool_names_absent`（D2 范围与 token 清单）、`adapter_note_tools_ok`、`archive_index_ok`（D3），挂 `check`；位置：注记两项紧邻"适配注记登记数"，索引检查置于 openspec 结构检查区。
- 完成判据：任务 1、2 用例转绿；`cmp` 两份 core 字节一致。

## 5. [x] 绿：wrapper 实现

- 文件：`scripts/validate-workflow.sh` + 资产副本 `scripts/ai-workflow-assets/shared/scripts/validate-workflow.sh`。
- 套件 PASS 分支后：`grep '\.\.\. skipped'` 提取行与计数，N>0 时按 D1 格式在汇总前打印注解与明细；N=0 无输出。
- 完成判据：任务 3 用例转绿；`cmp` 两份 wrapper 字节一致。

## 6. [x] 全量回归（源仓 + 安装器套件）

> 最终证据：契约套件 120 tests OK；安装器套件 `Ran 82 tests ... OK`（含白名单登记后）；全量门禁 `PASS=194 FAIL=0 SKIP=0`（exit 0）；`--fast` `PASS=193 FAIL=0 SKIP=0`。

> 过程记录：首轮安装器套件 2 失败——byte-sync（遗漏 `shared/scripts/tests/test_validate_workflow.py` 资产副本同步，已补）与 mode 断言（0775/0664 vs 0755/0644）。基线对照（main 干净 worktree 同跑）证实 mode 失败为 umask-002 检出环境的预存问题（基线同样仅败该项，CI 检出 umask 022 不受影响），与本变更无关；主检出资产树已 chmod 规范模式（git 不可见、无 diff）。
>
> 第二轮 6 失败、单一根因：`test_rejects_archive_index_drift` 假设归档 README 存在，而安装目标按设计没有该文件（空白基线），目标环境套件 ERROR 并连带 contract/public/required 三变体失败。已重写为自包含受控归档（备份/恢复整个 archive 目录，合成目录+索引四种状态），并同步资产副本。
>
> 第三轮 1 失败（claude+contract）：安装器测试的跳过理由白名单拦截了新理由 `codex assistant is not present in this fixture`（note 测试在 claude-only 目标的设计性跳过）。诊断运行证实差异集恰为该理由；已按白名单机制显式登记（`test_install_ai_workflow.py:426`）。该文件为源仓专属，无资产副本需要同步。

- `python3 -B -m unittest -v scripts.tests.test_validate_workflow` → 全绿；
- `python3 -B -m unittest -v scripts.tests.test_install_ai_workflow` → 全绿（资产一致性受其保护；`-B` 必需——无 `-B` 时 `exec_module` 会把 `__pycache__` 写进资产树令物理枚举必败，审查 F-1 指出的基线既有陷阱）；
- `bash scripts/validate-workflow.sh` → 全 PASS、`SKIP=0`、无内部跳过注解（源仓契约套件零跳过）；
- `bash scripts/validate-workflow.sh --fast` → 行为不变（无注解、无新检查异常）。
- 预期结果：全部退出码 0。

## 7. Verify：综合审查

- 主会话 freeze manifest（`review_manifest.py freeze`，repo-spec 指向本仓 main 基线）；
- 按共享规则做一次全 diff 综合审查（reviewer 读取前/结论前双 `verify`）；
- 处置 findings：Critical/Important 清零或经用户裁决。

## 8. Archive

- 合并 delta 到 `openspec/specs/shared-ai-workflow-infrastructure/spec.md`；
- proposal 置`已归档`、目录移入 `openspec/archive/`，**追加本变更索引行**（新检查 B 生效后索引必须 1:1）；
- memory/kb 沉淀（新坑：注记内容契约、目标侧设计性跳过的透明化语义）；
- 用户明示后合并 feature 分支。

## 本地整合策略

feature 分支主会话直执；main 不动直至归档完成、用户明示合并；无 worktree（无并行实现、工作区已干净）。
