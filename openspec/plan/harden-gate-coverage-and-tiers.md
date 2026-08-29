# 实现计划:harden-gate-coverage-and-tiers

目标、范围、规格与边界以 `openspec/changes/harden-gate-coverage-and-tiers/` 四件套为准。全局约束(逐字适用):串行单实例运行校验器;技能与入口改动必须双侧(`.claude`/`.codex`)+ 安装资产副本三方逐字节同步;mutation 断言既有短语不得删除;所有提交按可独立回滚职责单元;外部动作(推送)单独授权。

基线:main = 4861479。工作分支:`feature/harden-gate-coverage-and-tiers`,严格默认隔离 worktree(原子顺序见 T0)。

---

## T0 分支与 worktree 原子顺序

1. 记录当前分支(main);`git checkout -b feature/harden-gate-coverage-and-tiers`;暂存四件套 + 本计划 + proposal(`状态: 构建中`)提交,不得带入其他文件。
2. 切回 main;`git worktree add .worktrees/harden-gate-001 feature/harden-gate-coverage-and-tiers`(分支此时未被检出);在 worktree 内补齐被忽略的 `.codex/sdd`、`.claude/sdd` 占位目录。
3. 在 worktree 核对 `git branch --show-current`、`git status --short` 干净后进入 T1。
4. 验证:主工作区停在 main 且干净;worktree HEAD = 步骤 1 提交。

## T1 core 发布唯一命令清单(P1b 前半)

- 红测(先写,先跑):`scripts/tests/test_validate_workflow.py` 新增用例 `test_core_prints_external_commands`:调 `bash scripts/lib/validate-workflow-core.sh --print-external-commands`,断言退出 0、每行一个命令、无空行/重复、包含 `cat sort tr git grep find sed awk wc`。当前 core 无此参数 → 退出 2,红。
- 实现:`validate-workflow-core.sh` 参数循环(现 `--require-openspec` case 处,约 167-180 行)加 `--print-external-commands` 分支:调用新函数 `print_external_commands`(函数体 `printf '%s\n' awk bash cat cmp cp chmod dirname find git grep head mktemp rm rmdir sed sort stat tail touch tr wc`,与现行两份白名单的并集一致,排序输出)后 `exit 0`;该分支必须位于 `load_required_assistants` 之前,不需要 profile 即可调用。
- 验证:新用例绿;`bash scripts/lib/validate-workflow-core.sh --print-external-commands | wc -l` = 清单条数;默认无参行为与 `--require-openspec` 行为不变(跑 core 两次比对)。
- 提交:`feat(validator): core 发布唯一外部命令清单`。

## T2 两份测试消费唯一清单(P1b 后半)

- 修改 `scripts/tests/test_validate_workflow.py`:删除 `VALIDATOR_COMMANDS` 元组(22 行起),新增模块级 `_core_external_commands()`(subprocess 调 core `--print-external-commands`,返回 tuple,缓存);234 行 `for command in VALIDATOR_COMMANDS` 改为该函数结果。
- 修改 `scripts/tests/test_install_ai_workflow.py`:删除 `PORTABLE_VALIDATOR_COMMANDS`(65 行起),同样改为从**目标 fixture 内随包 core**调 `--print-external-commands`(331 行处);源仓自测路径(直接调本仓 core)与目标内路径都要覆盖。
- 红探针(验证单一来源生效):临时从 core 清单移除 `cat` → 两套件受限 PATH 用例必须失败(prerequisite 缺失);恢复 `cat` → 全绿。探针结果记入任务注记。
- 验证:`python3 -B -m unittest scripts.tests.test_validate_workflow` 全绿;`python3 -B -m unittest scripts.tests.test_install_ai_workflow` 全绿(后台串行,预计 >6 分钟)。
- 提交:`refactor(tests): 命令白名单单一来源化,删除双份硬编码`。

## T3 wrapper --fast 分层与 flock 并发锁(P2b/P2d)

- 红测 A(`test_fast_mode_skips_contract_suite`):调 `bash scripts/validate-workflow.sh --fast`,断言退出码与 `PASS=/FAIL=/SKIP=` 汇总存在,且输出**不含** `[PASS] 工作流顶层契约测试`,耗时 <30s;当前无 `--fast` → wrapper 原样传参给 core,core 退出 2,红。
- 红测 B(`test_concurrent_second_instance_fails`):后台起一个全量 `bash scripts/validate-workflow.sh`,立即再起第二个,断言第二个退出码 2 且输出含"另一实例";当前无锁 → 第二个正常跑,红。
- 实现:`scripts/validate-workflow.sh`:
  1. 参数解析:接受 `--fast`(置 `fast_mode=1`)并透传其余参数给 core;`--fast` 时不透传自身给 core(core 不认识会退出 2)。
  2. 顶部锁:`mkdir -p .ai-local`;若 `command -v flock` 存在,`exec 9>>.ai-local/.validate.lock && flock -n 9 || { printf '另一校验实例运行中,退出\n' >&2; exit 2; }`;不存在则 `printf 'flock 不可用,降级为无锁\n' >&2` 继续。
  3. `--fast` 时跳过顶层契约套件块(现 41-48 行),直接输出既有格式汇总(汇总计数=core 计数)。
- 验证:红测 A/B 绿;默认无参全量行为不变(跑一次全量确认含 `[PASS] 工作流顶层契约测试`);`--require-openspec` 组合仍有效。
- 提交:`feat(validator): wrapper 新增 --fast 分层与 flock 并发锁`。

## T4 pre-push 钩子与本地防护说明(P2a)

- 新建 `scripts/hooks/pre-push`(0755):`#!/usr/bin/env bash` + `set -u` + `exec bash "$(dirname "$0")/../lib/validate-workflow-core.sh"`。
- 红测(`test_pre_push_hook_blocks_on_red_gate`):临时目录造 `hooks/pre-push` + `lib/validate-workflow-core.sh`(stub,`exit 1`)与 `exit 0` 两个变体,断言钩子退出码透传;再对本仓真实钩子断言绿树退出 0。先写测试 → 红(stub 布局尚无钩子可执行路径)→ 实现 → 绿。
- `README.md` 增"本地防护"一节:`git config core.hooksPath scripts/hooks` 启用;钩子跑秒级 core,FAIL 阻断 push;不启用无影响。
- 验证:钩子测试绿;README diff 仅新增一节。
- 提交:`feat(guard): pre-push 秒级门禁钩子与启用说明`。

## T5 CI 增加安装器套件步骤(P1a)

- 红测:`test_validate_workflow.py` 既有 CI 结构断言处(grep `validate.yml` 的用例)增加断言:yml 含 `python3 -B -m unittest -v scripts.tests.test_install_ai_workflow` 步骤;先加断言跑 → 红 → 改 `.github/workflows/validate.yml`:在 "Validate workflow" 步骤后加 `- name: Install workflow installer tests\n  run: python3 -B -m unittest -v scripts.tests.test_install_ai_workflow`(步骤名自定,内容以断言为准)。
- 验证:结构断言绿;`openspec validate harden-gate-coverage-and-tiers --strict` 过。
- 提交:`ci: 安装器套件纳入必跑步骤`。

## T6 入口仲裁行(P3d)

- 修改 `CLAUDE.md`(技能路由段末)与 `AGENTS.md`(技能路由表后)各加一行:"宿主插件技能与仓库技能重叠时,以仓库技能为准;插件技能仅在仓库技能未覆盖时补充。"
- 同步资产:`scripts/ai-workflow-assets/claude/CLAUDE.md`、`scripts/ai-workflow-assets/codex/AGENTS.md` 同句插入(通用版措辞一致)。
- 红测先行:core 增结构断言(双侧入口含"以仓库技能为准")——先在 core 加 check 跑红,再改四处文件转绿;mutation 不需要(新增正向断言即可,另补一条 mutation:删除该行 → core 非零)。
- 验证:core 全绿;mirror/资产一致性相关用例绿。
- 提交:`feat(entry): 仓库技能优先于宿主插件技能的仲裁声明`。

## T7 技能分层与归档索引步骤(P2b 技能面 + 索引维护)

- `verify/SKILL.md`(双侧+资产):主会话终验清单中标准模式行改为"标准模式运行 `bash scripts/validate-workflow.sh --fast` 与变更相关目标/回归测试,逐项核对 `[PASS]`、`[FAIL]`、`[SKIP]` 和末尾汇总;变更触及工作流入口、技能、校验器或安装资产时改跑全量默认门禁";严格行原文不动。
- `archive/SKILL.md`(双侧+资产):归档后强制验证保持全量不变;"归档数据"清单加一步"追加 `openspec/archive/README.md` 索引行(名称—主旨—模式)"。
- 红测先行:core 增断言——verify 技能含 `--fast` 与"改跑全量默认门禁";archive 技能含 `openspec/archive/README.md`;既有 mutation 短语(`--require-openspec`、`不得 SKIP`)全部保留。先加断言跑红 → 改 6 处文件(2 技能 × {live,claude 资产,codex 资产}... 实为 live 双侧 + 资产双侧 = 每技能 4 份)转绿。
- 验证:core 全绿;全量契约套件(终验)确认 mutation/镜像/资产一致全过。
- 提交:`feat(skills): 标准终验分层 --fast 与归档索引维护步骤`。

## T8 资产逐字节同步核验

- 对 manifest 覆盖的全部变更文件(core、wrapper、verify/archive 双侧技能、CLAUDE/AGENTS)执行 `cmp` 逐字节比对 live vs `scripts/ai-workflow-assets/`;manifest 路径集合不变(无新增随包文件;钩子与 README 不随包)。
- 验证:全部 `cmp` 为空;`python3 -B -m unittest scripts.tests.test_install_ai_workflow` 全绿(其含资产逐字比较用例)。
- 提交(如需修正):`chore(assets): 同步门禁分层与仲裁行`。

## T9 任务级审查(每职责单元)

- T1–T8 每 1-2 个职责单元提交后:主会话 freeze 该单元精确范围,独立 reviewer 按 `.ai/rules/review.md` 审(读取前/结论前 verify manifest);Critical/Important 清零才进下一单元。SDD 草稿与报告只写 `.claude/sdd/`(已忽略)。

## T10 Verify 双阶段独立审查 + 终验

1. 规格符合性(新上下文):逐条核对 4 个 delta Requirement 的 Scenario 落地。
2. 代码质量(新上下文):正确性、锁与分层的边界、测试有效性、资产一致性。
3. 主会话终验(串行):`bash scripts/validate-workflow.sh --require-openspec` 全绿、`python3 -B -m unittest -v scripts.tests.test_install_ai_workflow` 全绿、`git diff --check`、`openspec validate --all --strict --no-interactive`。
4. finding 闭环后 `状态: 待归档`。

## T11 Archive 与整合

1. delta 合并:`shared-ai-workflow-infrastructure` MODIFIED+2 ADDED、`risk-tiered-ai-workflow` 2 ADDED。
2. 知识三写:memory(`.ai/memory/workflow.md` 本变更新坑)、kb(rules 路由如需)、archive 索引行。
3. `状态: 已归档`、目录移 archive、计划文件移为归档 `plan.md`、归档后全量 `--require-openspec` 复验、`chore(archive)` 提交。
4. 整合:回主工作区 main,`--no-ff` 合入 feature,合并结果复跑全量 required 门禁;按第二次确认的授权推送;worktree 清理在合并后执行。
