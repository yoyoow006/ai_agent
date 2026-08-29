# 实现计划:remove-stale-workflow-system-spec

目标、映射与边界以四件套为准(`openspec/changes/remove-stale-workflow-system-spec/`)。全局约束:校验器串行单实例;终验链期间零编辑;所有提交可独立回滚;推送单独授权(已随本计划确认)。基线 main = 5899f8c;分支 `feature/remove-stale-workflow-system-spec`;严格默认隔离 worktree `.worktrees/remove-wfspec-001`。

## T0 原子落点

1. main 上 `git checkout -b feature/remove-stale-workflow-system-spec`;暂存四件套+本计划+proposal(`状态: 构建中`)提交;不带其他文件。
2. 切回 main;`git worktree add .worktrees/remove-wfspec-001 feature/remove-stale-workflow-system-spec`;worktree 内补 `.claude/sdd`、`.codex/sdd` 占位;若 git 报 dubious ownership 则 `git config --global --add safe.directory <绝对路径>`(机器级,一次性)。
3. 验证:主工作区 main 干净;worktree 分支与 HEAD 正确。

## T1 删除前证据固化(在 worktree)

1. `openspec validate --all --strict --no-interactive` 输出存档(应 12 规格 passed)。
2. 引用扫描存档:`grep -rn "workflow-system" scripts/ .ai/ .github/ CLAUDE.md AGENTS.md README.md` 排除 `ai-kb` 与 `__pycache__` 后为空;`grep -rn "specs/workflow-system" . --include="*.md"` 排除 .git/archive/openspec/changes(本变更自身)后为空。
3. 验证:两份扫描输出为零(非零即停,回 Open 重新核实)。

## T2 删除与规格层复验

1. `git rm openspec/specs/workflow-system/spec.md`(目录随之消失,无 .gitkeep 需求——能力子目录不属 openspec/AGENTS.md 的四骨架目录)。
2. 现跑:`openspec validate remove-stale-workflow-system-spec --strict --no-interactive` 通过;`openspec validate --all --strict --no-interactive` 通过(11 规格)。
3. 现跑:`bash scripts/validate-workflow.sh --fast`(秒级,FAIL=0)。
4. 提交:`feat(specs): 移除迁移遗留的 workflow-system 五阶段旧规格`。
5. 验证:`git show --stat HEAD` 仅一个删除;worktree 干净。

## T3 任务级审查

1. freeze:`python3 .ai/tools/review_manifest.py freeze --change remove-stale-workflow-system-spec --workspace "$PWD" --repo-spec "$PWD::main" --output .ai-local/reviews/remove-stale-workflow-system-spec/task-manifest.json`;verify VALID。
2. 独立 reviewer(读取前/结论前各 verify):核对(a)REMOVED 10 条与被删文件逐条一致;(b)design 映射表每行的现行承接位置真实存在(grep 对应规格 Requirement 名);(c)T1 两份零引用扫描可复现;(d)无代码/技能/资产改动。
3. finding 闭环;Critical/Important 清零才进 T4。

## T4 Verify 双阶段 + 终验

1. 阶段 1(规格符合性,新上下文):delta REMOVED 完整性、openspec strict 通过、范围仅规格层。
2. 阶段 2(代码质量,新上下文):删除的干净性、无孤儿残留(specs/ 目录、manifest、文档提及)、提交组织。
3. 主会话终验(治理资产变更,不降层):`bash scripts/validate-workflow.sh --require-openspec` 全绿 + `git diff --check`。
4. finding 闭环后 `状态: 待归档` 并提交。

## T5 归档与整合

1. 归档落地:REMOVED 已由 T2 落地;`状态: 已归档`;变更目录移入 `openspec/archive/`;计划移为归档 `plan.md`;`openspec/archive/README.md` 追加索引行;知识沉淀(memory:如审查发现新坑则记,rules 路由无需变化——工作流校验器行不涉及规格清单)。
2. 归档后现跑 required 门禁全绿;`git add openspec/ .ai/ && git commit -m "chore(archive): remove-stale-workflow-system-spec"`。
3. 整合:回 main `--no-ff` 合入;合并结果复跑 required 门禁;按授权推送 origin/main。
4. 清理(用户已授权的本地收尾惯例):`git worktree remove` + `git branch -d` + unset safe.directory 对应项;报告终态。
