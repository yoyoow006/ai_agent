# Tasks: slim-workflow-skills

严格模式：本文件为范围清单；可执行实现计划由 Design 阶段的 `openspec/plan/slim-workflow-skills.md` 承担。

- [x] 1. 校验器守卫红测：3 用例（注入"未随本仓库迁移" / 删除 writing-skills `tr -d`/`wc -m` / 删除绑定句）按 `openspec/plan/slim-workflow-skills.md` 任务 5 红测契约注入必红，由 dcc116c 同步落地（`scripts/tests/test_validate_workflow.py` +81 用例）
- [x] 2. 实现 `validate-workflow-core.sh` 三守卫（迁移注记 absence、`tr -d`/`wc -m` 锚串、`workflow-pressure-scenarios.md`/`重跑` 绑定锚串；显式 return 0；零新外部命令）＋干净必绿配对；同步契约套件计数断言（提交 dcc116c，core +20 行；`--fast` 193→198 全绿；契约套件 129 用例 OK）
- [x] 3. writing-skills 内联瘦身（迁移注记并一行、示例单例化、去重；目标 ≤7500 去空白字符）＋字符口径验证命令与阈值登记＋场景重跑绑定句（提交 3877544＋修复 a82b177，任务级审查 PASS，T1-F1 已解决）
- [x] 4. parallel-agents 示例本土化（bash/python 安装器场景）＋叙事节压缩（目标 ≤1800）；保留适配注记行与 5 个现行工具名（提交 7300527＋修复 be03ca5，审查 PASS，T2-F1 已解决）
- [x] 5. systematic-debugging 示例本土化（安装器/校验器多层排查替代 macOS 签名链）；宿主语汇中性化；阈值合规（≤5000）（提交 ce23ce8＋修复 801c134，审查 PASS，T3-F1/F2 已解决）
- [x] 6. 四副本同步（`.codex`＋资产树两侧，路径前缀适配）；现验 mirror_equal、适配注记计数=1、废弃工具名零残留、资产/工作树逐字一致（已随任务 3/4/5 逐任务执行并经 --fast 与任务级审查背书）
- [x] 7. 9 个施压场景全量重跑；逐场景 PASS/FAIL 与逐字理由记录至 `scenario-rerun.md`（8/9 PASS；场景 I 双样本一致 FAIL，根因为预存在的规格分歧——场景契约 vs codex-target 规格"先保留再替换"，与本变更压缩无因果；按 delta spec FAIL 条款交用户裁定：用户裁定**维持现状，另立独立变更调和场景 I 契约与 codex-target 规格的分歧**，本变更不扩大范围、继续推进 Verify → Archive）
- [x] 8. 严格终验链：`--require-openspec` 全量门禁＋`openspec validate --all --strict`＋安装器套件（`-B`、串行、后台长跑）；umask-002 环境先做权限规范化；终验链期间零提交
  - 步骤 1：`bash scripts/validate-workflow.sh --require-openspec` → PASS=199 FAIL=0 SKIP=0（含契约套件 129 用例 OK + 顶层契约测试 OK，6m33s）
  - 步骤 2：`openspec validate --all --strict --no-interactive` → 11/11 PASS（含 change/slim-workflow-skills 与 10 specs）
  - 步骤 3：安装器套件 `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest scripts.tests.test_install_workflow scripts.tests.test_install_ai_workflow` → Ran 91 tests in 1398.746s OK（前置：`_run_target` timeout 240→900 秒的预存基础设施失配最小修复，提交 12836d5，基线全量门禁 ~350s + 当前 ~400s，2x 裕度）
  - 步骤 4：`git diff --check` exit=0；目标 diff（9 提交链 3877544/7300527/ce23ce8/801c134/dcc116c/c972e26/12836d5）文件改动全部为压缩/守卫/状态修正，无意外范围扩张
