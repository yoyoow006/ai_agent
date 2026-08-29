# 移除迁移遗留的 workflow-system 五阶段旧规格

模式: 严格
状态: 构建中

## Why

`openspec/specs/workflow-system/spec.md` 是共享层迁移前的旧宪法,与现行治理体系直接矛盾,且已完全孤儿化:

1. **三处实质矛盾**:①宣称所有变更走五阶段——已被风险分级三模式取代(risk-tiered-ai-workflow);②要求维护 `.claude/ai-kb/` 三层知识——该路径现为兼容指针、平行正文被校验器明令禁止(shared-ai-workflow-infrastructure);③要求 Verify 恒两阶段审查——标准模式已明确单次综合审查(risk-tiered「标准模式必须消除重复审查」)。
2. **零活引用**:全仓 grep 代码/测试/CI/文档(除归档与 memory 的历史来源名)无任何引用;安装资产只随包 risk-tiered 与 shared-ai-workflow-infrastructure 两份规格。
3. **误导风险**:12 份主规格中 1 份描述已废弃世界,新会话按路由读到它会得到与现行规则相反的指令——这正是 P0 事故类"第二真源"问题的文字版。

## What Changes

1. 以 REMOVED delta 移除该能力全部 10 条 Requirement(五阶段工作流、硬门禁、状态真源与断点续传、原生技能库、ai-kb 知识库、TDD 硬规则、两阶段审查、归档六步、openspec CLI 兼容、零插件依赖),归档时删除 `openspec/specs/workflow-system/spec.md` 与目录。
2. 逐条映射存档于 design:每条旧 Requirement 的现行承接位置(或不承接理由)。
3. 复验:`openspec validate --all --strict --no-interactive` 通过(12→11 份规格);`bash scripts/validate-workflow.sh --require-openspec` 全绿;资产 manifest 不变(本就不随包)。

## Impact

- 规格:主规格 12→11 份;无任何行为、技能、校验器、入口文档或安装资产变化。
- 历史可追溯:旧正文保留在 git 历史与归档 delta 中;memory 条目的"来源变更 init-workflow-system"是变更名引用,不受影响。
- 整合策略(建议):严格默认隔离 worktree;归档后本地 `--no-ff` 合回 main、合并结果复跑 required 门禁、推送(本次一并授权)。
