# 任务清单

- [ ] 1. 规则缓存契约与实现
  - [ ] 1.1 在 `scripts/lib/` 定义规则输入清单、schema/version、内容指纹和 `.ai-local/rules-cache/` 记录格式；记录只含脱敏路径、哈希、时间和 PASS 状态。
  - [ ] 1.2 改造 `scripts/lib/validate-workflow-core.sh` 与 wrapper，使 fast/standard 可透明命中，required 强制实际执行，缓存异常 fail-closed。
  - [ ] 1.3 为命中、输入变化、命令变化、损坏、失败不落盘、required 绕过和并发写入补充契约测试。
  - [ ] 1.4 验证：`python3 -B -m unittest -v scripts.tests.test_validate_workflow`；预期缓存相关用例全绿且输出保持 PASS/FAIL/SKIP。

- [ ] 2. 分层验证入口与升级矩阵
  - [ ] 2.1 在 `scripts/validate-workflow.sh` 固化 fast、standard、required 的覆盖矩阵、参数冲突和升级判定，保持既有入口兼容。
  - [ ] 2.2 同步 `AGENTS.md`、`.codex/README.md`、阶段技能、`.ai/rules/index.md` 与工作流压力场景，写明每层命令、允许 SKIP 和终验要求。
  - [ ] 2.3 增加层级矩阵、冲突参数、自动升级和 required 禁止缓存的回归测试。
  - [ ] 2.4 验证：`bash scripts/validate-workflow.sh --fast`、默认 `bash scripts/validate-workflow.sh`、`bash scripts/validate-workflow.sh --require-openspec`；分别记录退出码、汇总和 SKIP。

- [ ] 3. 标准 OpenSpec 产物模板化
  - [ ] 3.1 新增 `openspec/templates/` 下 proposal/spec/tasks 及条件 design 模板，明确必需字段、场景格式、命令和整合策略槽位。
  - [ ] 3.2 新增只读生成/预检工具（建议 `scripts/new-openspec-change.py`），空目录生成，非空或非法参数 fail-closed，不触碰目录外文件。
  - [ ] 3.3 将模板结构接入工作流 core 与契约测试，覆盖占位符、WHEN/THEN、单行命令、状态组合和路径安全。
  - [ ] 3.4 验证：在临时目录生成后预检通过；注入缺字段/占位符/多行命令后预检非零；`git diff --check` 通过。

- [ ] 4. 规格、镜像和证据同步
  - [ ] 4.1 更新 `openspec/specs/risk-tiered-ai-workflow/spec.md` 与 `openspec/specs/shared-ai-workflow-infrastructure/spec.md` 的 delta 语义及镜像资产。
  - [ ] 4.2 运行 OpenSpec 严格校验、压力场景和模板/验证契约，记录输出、manifest、未验证范围和残余风险。
  - [ ] 4.3 仅提交本变更职责单元；不纳入工作区既有 `.gitignore`、`.vscode/`、`httpclient.http`、`work_daily.md` 修改。

## 本地整合策略

- 严格模式默认在独立 feature/worktree 中实施；四件套确认前不创建独立计划、不实现代码。
- 规则缓存、验证层级、模板工具和规格同步按可独立回滚职责提交；不自动推送、合并或发布。
- 所有新缓存与生成产物仅写入 `.ai-local` 或用户明确的 OpenSpec 变更目录，并保持可清理、不可作为状态真源。
