# 设计——台账驱动的安装器升级

## 关键决策

### D1. 台账载体与格式（Build 期二次修正：独立文件）

- **`.ai/assistant-profile.json` 保持校验器契约格式 `{"assistant", "schema_version": 1}` 不变**——Build 期实测发现该文件的第二所有者（校验器契约测试 test_validate_workflow.py:306 断言键集与版本严格等于 v1），profile 升 v2 会击穿安装目标内的契约套件。
- 台账改存**安装器私有文件 `.ai/installer-ledger.json`**：`{"assistant": "codex|claude", "files": {"<manifest相对路径>": "<sha256hex>"}, "schema_version": 1}`（新文件自有版本从 1 起）；校验器不读取该文件；安装/升级事务内与文件同批生成。
- **台账记"资产谱系哈希"而非磁盘哈希**（Design 自审修正：若 SKIPPED 记磁盘当前内容，下一轮升级会把目标修改误判为"未被修改"而静默覆盖）：
  - `UPGRADED/CREATED/UNCHANGED` → 记**新版资产**内容哈希；
  - `SKIPPED` → **沿用旧台账条目**（人工回退到资产版本后自动恢复升级资格）；
  - `KEPT` → 同 SKIPPED，沿用旧条目；`REMOVED` → 删除该条目；
  - legacy（无台账文件）→ 不建立条目（稳定 SKIPPED，直至人工对齐）。
- 读取校验：文件缺失 → 空台账（legacy）；存在但结构/摘要非法或 assistant 与请求不符 → InputError（fail-closed）。

### D2. 升级计划构建（build_upgrade_plan）

复用 build_plan 骨架，`_target_action` 换为四值判定：`UPGRADED`（台账命中且≠新版）/`UNCHANGED`（=新版）/`CREATED`（目标缺失）/`SKIPPED`（不匹配）；再对"台账有、新 manifest 无"的路径生成 `REMOVED`/`KEPT`。入口文件与 symlink/类型异常沿用既有 ConflictError 硬失败（结构性冲突不容忍）。SKIPPED 文件**进入计划但不产生写动作**，仅报告——事务捕获范围因此只含真实变更，回滚边界与安装一致。

### D3. 报告与退出码

- 逐文件行：`UPGRADED <path>` / `UNCHANGED <path>` / `CREATED <path>` / `SKIPPED <path>（目标已修改，保留；请人工比对新版）` / `REMOVED <path>` / `KEPT <path>（已移除但目标已修改，保留）`；末尾汇总计数。
- 退出码沿用：0 成功（含存在 SKIPPED/KEPT——它们是报告不是失败）；1 事务失败；2 用法/输入；3 结构性冲突（symlink/类型/受管块损坏）。SKIPPED≠3，与"整体拒绝"语义区分。

### D4. 事务一致性

台账文件作为普通 PlanItem 参与 renameat2 原子发布：文件替换与台账重写同批交换、同批回滚。中途故障 → 全部还原（含台账），磁盘与台账永不脱钩。`.gitignore` 受管块在升级路径按既有 `_plan_gitignore` 幂等处理（完整块存在 → unchanged）。

### D5. 兼容与边界

- Python 3.8 约束不变：新代码仅用 3.8 语法（无 walrus 于类型位置、`Dict`/`Tuple` typing 导入）。
- 非 upgrade 的默认安装语义零改动（含 v1 目标重装仍按现状）；profile v2 由 upgrade 或新安装产生。
- `--upgrade` 与目标缺失/嵌套源仓等边界沿用 `_validated_target`/`build_plan` 现有校验。

## 替代方案

- 显式 `--baseline-manifest`：体验差、易传错，提问轮已否决。
- 无基线纯比对：无法区分"旧版未动"与"目标改过"，否决。
- 整体中止式升级：与现状无异，否决。
- 独立 uninstall 子命令：本次范围外（非目标），台账机制为其预留了可行性。

## 风险与边界

- "目标回改回旧内容"被判定为未修改→覆盖目标改动：内容等价即无信息损失，接受并记录残余风险。
- 台账哈希与 git 状态无关（按磁盘内容）：目标未提交修改同样受"未修改"判定保护——以内容为准，简单可审计。
- 首次对 yuxiaor 真实目标升级会产生大量 SKIPPED（v1 无台账）——预期行为，报告引导二次安装后恢复正常。

## 验证策略

- 严格 TDD：先写失败测试（台账判定矩阵、legacy 降级、REMOVED/KEPT、dry-run 零写入、中断回滚含台账、报告格式），后实现，后重构。
- 既有 1918 行安装测试全绿不回归；`python3.8 -m py_compile` 等价物（本机无 3.8 时用语法面检查＋CI 补）。
- 终验跑全量 `validate-workflow.sh --require-openspec`（其含安装器测试套件）。
