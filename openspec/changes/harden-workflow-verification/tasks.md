# Tasks

- [x] 1. 压力场景 W/A/M
  - `scripts/workflow-pressure-scenarios.md` 按 R/Q/S/X 同构新增三场景（场景文本＋可判通过条件，见 design D1）；`cp` 同步 assets 副本并 `cmp`。
  - 验证：`grep -c '^## [WAM]：'` = 3；`cmp` 通过。
- [x] 2. 校验器扩展
  - core（＋assets 副本字节一致）：`policy_ok` 追加 3 条正则（design D2）；新增 9 个 `mutation_rejected` 检查（3 句 × 入口/open/archive/build 落点）；新增"适配注记登记数"检查（合计=1）；压力契约 `contains_all` 纳入 `'W：严格实现前的 worktree 原子顺序' '已检出分支' 'A：归档合并与用户取消' '第二真源' '取消原因' 'M：审查中途 manifest STALE' '不沿用旧结论' '重新 freeze'`。
  - 红绿：三句逐一向 CLAUDE.md 注入→非零→还原；前缀注记注入 tdd 技能→登记数 FAIL→还原。
  - 验证：`bash scripts/validate-workflow.sh` 全 PASS，计数=184（172+10+本变更 2）。
- [x] 3. CI SHA 钉
  - `.github/workflows/validate.yml` 两个 `uses` 改为 design D4 的 SHA＋版本注释。
  - 验证：yaml 解析；`grep -c '#' ` 注释在位；本地 `bash scripts/validate-workflow.sh --require-openspec` 全绿。
- [ ] 4. 终验与归档
  - `openspec validate harden-workflow-verification --strict --no-interactive`；全量 required 门禁；`python3 -m unittest` 两套；`git diff --check`。
  - 勾选 tasks→`待验证`→标准模式唯一综合审查（freeze→一次全 diff 审查）→`待归档`→合并 delta 主规格＋cp 资产规格副本→移动归档→归档后 required 门禁→提交。
  - 整合：本地 `--no-ff` 合回 main 并复验；推送另行授权。
