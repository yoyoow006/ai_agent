# Tasks（范围清单——严格模式实现计划由 Design 阶段独立产出）

- [x] 1. 取消路径治理文本
  - 实体：`openspec/AGENTS.md`（状态枚举＋处置规则＋归档区分）、`CLAUDE.md`、`AGENTS.md`（状态路径行加取消提示）、`.ai/kb/overview.md`（状态表）、`.claude` 与 `.codex` 两侧 `archive/SKILL.md`（取消路径小节）
  - 资产：上述全部对应副本
  - 验证：`bash scripts/validate-workflow.sh` 全 PASS
- [x] 2. 校验器扩展
  - `scripts/lib/validate-workflow-core.sh` 及 assets 副本：`标准:已取消|严格:已取消` 入合法组合；文档检查含`已取消`；镜像循环扩至 13 技能（新增 `mirror_normalized`：路径前缀改写＋适配注记豁免＋空行压缩）
  - 验证：validator 全 PASS；临时注入技能漂移确认非零后还原
- [x] 3. CI workflow
  - 新增 `.github/workflows/validate.yml`（push main + pull_request + workflow_dispatch；checkout fetch-depth 0；setup-node；npm i -g @fission-ai/openspec@1.3.1；跑 `--require-openspec`）
  - 验证：yaml 解析、`bash -n`、本地等价命令全绿；`manifest.json` 确认无 CI 路径
- [x] 4. 终验回归
  - `openspec validate add-cancel-state-ci-mirror --strict --no-interactive`、`bash scripts/validate-workflow.sh --require-openspec`、`python3 -m unittest -v scripts.tests.test_validate_workflow`、`python3 -m unittest discover -v -s .ai/tools/tests -p 'test_*.py'`
  - 逐项读取退出码与失败数
