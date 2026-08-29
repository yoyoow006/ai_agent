# 修复合并复活的旧 ai-kb 平行正文导致的主线门禁红

模式: 标准
状态: 待验证

## Why

合并提交 `45e8ed1`(本地线并入 origin/main)把共享层迁移前的 `.claude/ai-kb/`、`.codex/ai-kb/` 下 `kb/`、`rules/`、`memory/` 平行正文带回 main,并已推送(origin/main == HEAD)。后果(2026-08-29 现跑证据):

- `scripts/lib/validate-workflow-core.sh` 的 `旧 ai-kb 不含平行正文` 检查 FAIL;
- 顶层契约套件因 fixture 忠实复制现行文件,级联 40/82 失败(全部同根因);
- CI(每次推送 main 必跑 `validate-workflow.sh --require-openspec`)当前为红。

这违反 `openspec/specs/shared-ai-workflow-infrastructure/spec.md` 既有要求"跨助手知识必须只有一个共享真源:旧 ai-kb 路径……不得继续保存可独立演化的平行正文"。旧正文与共享层已分叉(kb/overview.md 差 64 行、rules/index.md 差 28 行),继续保留会形成第二真源。

## What Changes

1. **迁移**:旧 `.claude|.codex/ai-kb/memory/{installer.md,workflow-system.md}` 中 10 条 2026-08-16 踩坑条目(2 条 add-workflow-installer、5 条 init-workflow-system、3 条 codex 侧独有的「工作流端到端验证(临时项目 add-greeting)」)逐字迁入 `.ai/memory/workflow.md`。已验证共享层对这 10 条零命中,不迁移直接删除会丢失真实知识。(初版误按 claude 侧 7 条执行,综合审查 VQ-C01 发现 codex 侧 `workflow-system.md` 多 3 条独有条目,已在该 finding 核实后补迁并更正本事实源。)
2. **删除**:移除两侧共 10 个 tracked 平行正文文件(`kb/overview.md`、`rules/index.md`、`memory/{.gitkeep,installer.md,workflow-system.md}` ×2);保留各自 `README.md` 兼容入口。旧 kb/rules 与共享层逐行比对,其独有内容均为迁移前旧架构描述(五阶段、`.claude/ai-kb` 为知识库、`install-workflow.sh --force`),已被共享层取代,无可保留事实。
3. **复验**:串行单实例运行 `bash scripts/validate-workflow.sh` 至全绿(core FAIL 消除、契约 82/82、汇总 FAIL=0),`git diff --check` 干净。

另:本变更目录创建前,审计已按 CLAUDE.md"新坑立即写 memory"常设授权向 `.ai/memory/workflow.md` 追加 1 条 2026-08-29 踩坑记录(校验器串行运行、合并复活根因),随本变更一并提交。

## Impact

- **运行时与安装资产**:零变化。`scripts/ai-workflow-assets/` 与 `manifest.json` 只含 ai-kb README,未受合并污染(已核对)。
- **知识层**:共享 memory 净增 10 条历史踩坑(7 条 claude/codex 共有 + 3 条 codex 独有)+ 1 条审计踩坑;恢复与 origin 迁移后基线(9614f9e)一致的目录形态与门禁绿。
- **不改**任何治理规则、技能、校验器代码、入口文档;不触碰运行时代码。
- 本地整合策略(建议):feature 分支 `fix-merged-legacy-ai-kb-regression`,归档后本地 `--no-ff` 合回 main 并复跑校验;推送 origin/main 单独请求授权(main 当前 CI 为红,修复推送后转绿)。
