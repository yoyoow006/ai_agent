# 范围清单

- [x] 1. 为 registry 依赖与 verification 声明、`project-context` 输出和 `verified_commit` freshness 编写失败测试，覆盖合法声明、未知/自/重复/循环依赖、非法命令、证据路径越界/缺失、非法 commit、只读性和输出稳定性。
- [x] 2. 实现 registry 可选 `dependencies` 与 `verification` 契约；`project-context` 输出直接依赖、build/test 入口、证据路径和 current/drifted/unavailable 基线状态，不执行命令。
- [x] 3. 新增通用项目卡模板 `.ai/kb/projects/_template.md`，覆盖职责/非职责、高频入口、跨仓关系、搜索锚点、验证入口、证据基线和定位特例，不携带业务事实。
- [x] 4. 新增 `.ai/kb/verification-evidence.md`，定义证据字段、等价复用条件、失效条件、脱敏要求和“不得替代 OpenSpec/新鲜验证”的边界。
- [x] 5. 更新项目登记 README、`.ai/kb/README.md`、`.ai/README.md`、`.ai/tools/README.md`、`.ai/rules/index.md` 和双侧 verification 技能，使项目上下文和证据复用路由可达。
- [x] 6. 更新 shared infrastructure delta/main spec、安装资产 manifest 和源/资产字节同步测试，确保新增模板与证据文档随包分发且源 registry 仍为空。
- [x] 7. 运行事实工具测试、workflow mutation/契约测试、便携安装器测试、一键安装器测试、`bash scripts/validate-workflow.sh --require-openspec`、OpenSpec strict 与 diff 检查。
- [ ] 8. 执行严格任务级审查和 Verify 双阶段独立审查，重点审查 registry 边界/只读性、证据复用不削弱完成门禁、安装资产同步与源仓库知识分层。

## 验收标准

- registry 可声明直接项目依赖和验证入口，非法依赖图、命令、证据路径和 commit 均被拒绝。
- `project-context` 能输出依赖与验证上下文，并对 `verified_commit` 给出确定性 freshness 状态；全程只读且不联网。
- 项目卡模板和验证证据文档随安装器分发，不包含 ai-pms 业务事实或敏感示例。
- verification 技能明确证据复用条件与失效条件，证据不能替代当前任务的新鲜验证或 OpenSpec 状态。
- `python3 -B -m unittest discover -v -s .ai/tools/tests -p 'test_project_facts.py'` 通过。
- `python3 -B -m unittest -v scripts.tests.test_validate_workflow`、`python3 -B -m unittest -v scripts.tests.test_install_ai_workflow`、`python3 -B -m unittest -v scripts.tests.test_install_workflow` 通过。
- `bash scripts/validate-workflow.sh --require-openspec` 与 `openspec validate --all --strict --no-interactive` 全绿。

## 本地整合策略

严格模式使用隔离 worktree 和 `feature/extend-project-context-and-evidence-reuse`。验证、任务级审查、Verify 双阶段和归档通过后，本地 `--no-ff` 合回 `main` 并复验；不 push，不创建 PR。已合并且 worktree 干净时，按确认策略清理 feature 分支和 worktree。
