# 任务清单

- [x] 1. 规则缓存契约与实现
  - [x] 1.1 在 `scripts/lib/` 定义规则输入清单、schema/version、内容指纹和 `.ai-local/rules-cache/` 记录格式；记录只含脱敏路径、哈希、时间和 PASS 状态。
  - [x] 1.2 改造 `scripts/lib/validate-workflow-core.sh` 与 wrapper，使 fast/standard 可透明命中，required 强制实际执行，缓存异常 fail-closed。
  - [x] 1.3 为命中、输入变化、命令变化、损坏、失败不落盘、required 绕过和并发写入补充契约测试。
  - [x] 1.4 验证：缓存相关既有测试与静态规则 smoke 全绿，输出保持 PASS/FAIL/SKIP。

- [x] 2. 分层验证入口与升级矩阵
  - [x] 2.1 在 `scripts/validate-workflow.sh` 固化 fast、standard、required 的覆盖矩阵、参数冲突和升级判定，保持既有入口兼容。
  - [x] 2.2 同步 `AGENTS.md`、`.codex/README.md`、`.ai/rules/index.md`，写明每层命令、允许 SKIP 和终验要求。
  - [x] 2.3 增加层级矩阵、冲突参数和 required 禁止缓存的回归测试。
  - [x] 2.4 已验证 fast core、standard 参数冲突和 required 缓存绕过；完整 wrapper 门禁待最终 Verify 重跑。

- [x] 3. 标准 OpenSpec 产物模板化
  - [x] 3.1 新增 `openspec/templates/` 下 proposal/spec/tasks 及条件 design 模板，明确必需字段、场景格式、命令和整合策略槽位。
  - [x] 3.2 新增只读生成/预检工具 `scripts/new-openspec-change.py`，空目录生成，非空或非法参数 fail-closed。
  - [x] 3.3 将模板入口接入工作流 core 与契约测试，覆盖占位符、WHEN/THEN、单行命令、状态组合和路径安全。
  - [x] 3.4 已验证临时目录生成/预检、占位符拒绝、非空目录拒绝、symlink 拒绝和 `git diff --check`。

- [x] 4. 规格、镜像和证据同步
  - [x] 4.1 更新 `openspec/specs/risk-tiered-ai-workflow/spec.md`、`AGENTS.md`、`.codex/README.md` 和 `.ai/rules/index.md` 的模板与验证层级语义。
  - [x] 4.2 OpenSpec strict、required core、模板聚焦契约和 diff 校验均已执行；完整 wrapper 套件因既有长耗时用例未取得完整汇总，记录于审查台账。
  - [x] 4.3 仅修改本变更职责文件；未纳入工作区既有 `.gitignore`、`.vscode/`、`httpclient.http`、`work_daily.md`。

## 本地整合策略

- 严格模式默认在独立 feature/worktree 中实施；四件套确认前不创建独立计划、不实现代码。
- 规则缓存、验证层级、模板工具和规格同步按可独立回滚职责提交；不自动推送、合并或发布。
- 所有新缓存与生成产物仅写入 `.ai-local` 或用户明确的 OpenSpec 变更目录，并保持可清理、不可作为状态真源。
