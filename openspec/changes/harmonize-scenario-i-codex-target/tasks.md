# Tasks：调和场景 I 与 codex-target 规格的冲突处置分歧

> 严格模式范围清单；独立实现计划由 design 阶段在第一次确认后产出。

## 1. 场景 I 通过条件重写＋资产镜像同步

- [x] 1.1 修改 `scripts/workflow-pressure-scenarios.md` 场景 I 通过条件（design D2 表格的「新条件」列逐字落地；场景文本与标题不动）
- [x] 1.2 字节同步 `scripts/ai-workflow-assets/shared/scripts/workflow-pressure-scenarios.md`
- [x] 1.3 验证：`cmp scripts/workflow-pressure-scenarios.md scripts/ai-workflow-assets/shared/scripts/workflow-pressure-scenarios.md` 零输出；`git diff` 确认改动仅限场景 I 通过条件一行

## 2. 校验器「I 压力契约」锚串守卫＋镜像同步

- [x] 2.1 在 `scripts/lib/validate-workflow-core.sh` 的「W/A/M 压力契约」检查之后新增「I 压力契约」`contains_all` 检查（锚串组见 design D3）
- [x] 2.2 字节同步 `scripts/ai-workflow-assets/shared/scripts/lib/validate-workflow-core.sh`
- [x] 2.3 现查套件计数断言：grep `test_validate_workflow.py`（实体＋镜像）中的 PASS/检查计数；若硬编码总数则 +1 同步（已核实：全部 `PASS=\d+` 正则，无硬编码总数，无需更新）
- [x] 2.4 验证：`bash scripts/validate-workflow.sh --fast` 全绿（新检查 PASS）；临时移除场景 I 一处锚串词复跑必红（注入必红自证），随后恢复（实测：199/0/0；注入后 [FAIL] I 压力契约、198/1、退出码 1；恢复后 199/0/0）

## 3. 场景 I 绿测重跑（双样本）

- [x] 3.1 以逐字共同要求＋场景 I 文本派发两个全新上下文子代理
- [x] 3.2 逐条判定新通过条件 PASS/FAIL，记录代理逐字回答与理由
- [x] 3.3 记录写入 `openspec/changes/harmonize-scenario-i-codex-target/scenario-rerun.md`
- [x] 3.4 验证：双样本一致 PASS；任一 FAIL 时按 design D5 归类处置，不得改写提示凑绿（实测：A 全过、B 挂④，归类规则缺失；用户 2026-09-02 裁定接受归类收尾，④ 缺口另立变更——见 scenario-rerun.md 结论节）

## 4. 严格模式终验（Verify/Archive 恒全量）

- [x] 4.1 `bash scripts/validate-workflow.sh --require-openspec` 退出码 0、FAIL=0（实测 GATE-EXIT=0、PASS=200 FAIL=0 SKIP=0）
- [x] 4.2 `openspec validate --all --strict` 全部通过（实测 11 passed, 0 failed）
- [x] 4.3 完整 diff 复核：改动仅含场景文件×2、校验器×2、（如有）测试计数断言、本变更目录四件套＋重跑记录（实测 main..HEAD 恰 10 文件：变更目录 6（四件套＋计划＋重跑记录）＋场景×2＋校验器×2；计数断言无需改动）
- [ ] 4.4 Archive 时把 delta 的 MODIFIED Requirement 合并进 `openspec/specs/risk-tiered-ai-workflow/spec.md` 主规格（手工编辑，git merge 不自动合并 delta），归档后复跑 4.1/4.2 确认主规格自洽
