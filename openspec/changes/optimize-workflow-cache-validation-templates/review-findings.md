# Verify 审查记录

## full-review · 2026-09-30

- manifest: `fedffbe036988ad5130f2e8360f9728f81210eb8769ebdb3c627dba8211bdbd6`
- comparison base: `feature/optimize-workflow-cache-validation-templates@b135a4e`
- 规格阶段结论：初次发现的两个 Important 已修复并复验。

### Findings

id: delta-heading
severity: Important
repo/path: openspec/changes/optimize-workflow-cache-validation-templates/specs/workflow-optimization/spec.md:3
evidence: 初版使用 `## Requirements`，与仓库 delta 约定及模板预检要求不一致。
observable impact: OpenSpec 无法可靠识别新增需求。
status: resolved
minimal fix: 改为 `## ADDED Requirements`。
verification: `openspec validate --all --no-interactive` 退出 0；模板 8 项测试通过。

id: standard-promotion
severity: Important
repo/path: scripts/validate-workflow.sh:72
evidence: 初版 `--standard` 只打印层级，未依据显式变更文件升级 required。
observable impact: 工作流治理变更可能只运行 standard 门禁。
status: resolved
minimal fix: 对 `--archive-files` 提供的入口、技能、core、模板和安装资产路径执行确定性 required 升级并输出路径。
verification: `StandardLayerContractTest` 通过；`scripts/lib/validate-workflow-core.sh --require-openspec` 输出 `PASS=128 FAIL=0 SKIP=0`。

id: stale-cache-after-required-failure
severity: Important
repo/path: scripts/lib/validate-workflow-core.sh:410
evidence: 初版静态规则检查失败时仅在 fast 环境删除旧缓存，required/standard 失败可能留下旧 PASS。
observable impact: 后续 fast 执行可能沿用过期 PASS。
status: resolved
minimal fix: 任一实际失败都删除对应静态规则缓存。
verification: core 静态审查与 required core 退出 0；缓存命中/失效聚焦测试通过。

unverified（未验证范围）: 完整公共 wrapper 套件未取得完整 `Ran ...` 汇总；其长耗时用例已执行到既有 validator 测试但进程未在命令窗口内完成。
residual risk（残余风险）: 公共 wrapper 的完整契约套件仍需在 CI 或更长超时窗口现跑；OpenSpec CLI、required core、模板测试和 targeted cache/layer tests 已有新鲜 PASS 证据。
