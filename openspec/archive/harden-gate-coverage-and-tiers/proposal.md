# 工作流门禁覆盖、分层与自防护加固

模式: 严格
状态: 已归档

## Why

2026-08-29 审计与两轮变更执行暴露五个门禁缺口,全部有实证:

1. **P1a 安装器套件无自动门禁**:`scripts/tests/test_install_ai_workflow.py` 82 个测试覆盖仓库最复杂运行时代码(69KB 事务安装器),但 `validate-workflow.sh`、CI、任何自动入口都不运行它(grep 全仓零引用);memory 已记录它曾"静默挂了两个版本"。
2. **P1b 命令白名单双份**:`VALIDATOR_COMMANDS`(test_validate_workflow.py:22)与 `PORTABLE_VALIDATOR_COMMANDS`(test_install_ai_workflow.py:65)手工同步,已发生过单侧遗漏(CQ-1,cat 遗漏致 6 子测试静默挂两版)。
3. **P2a 合并无本地防护**:45e8ed1 手工合并复活旧正文并推送,CI 只能事后红;pre-push 本地秒级 core 门禁可拦截同类事故。
4. **P2b 门禁耗时与"现跑"铁律摩擦**:契约套件约 5 分钟,完整门禁 6-8 分钟;标准 Verify 终验与 Archive 各跑一次全量,而 Verify 阶段后面仍有 Archive 全量兜底——分层后 Verify 用秒级 core+目标测试即可,全量留给 Archive。
5. **P2d 校验器并发互踩**:两实例并行时 mutation 测试互改文件产生大额假失败(本会话实测);无锁保护。
6. **P3d 插件技能无仲裁声明**:宿主 superpowers 插件与仓库技能同名重叠(tdd、systematic-debugging 等),CLAUDE.md/AGENTS.md 未声明优先级。

关联发现(本变更不处理,建议另行开变更):`openspec/specs/workflow-system/spec.md` 仍是五阶段旧文,与现行风险分级工作流矛盾,仅被自身和一条 memory 引用;安装资产早已只随包现行两份规格。

## What Changes

1. **P1a**:`.github/workflows/validate.yml` 增加独立步骤现跑 `python3 -B -m unittest -v scripts.tests.test_install_ai_workflow`,任一失败使 CI 红;不改本地 wrapper(避免拉长本地门禁)。
2. **P1b**:core 新增 `--print-external-commands` 模式,输出唯一权威命令清单;两份测试的 PATH 白名单改为运行时从 core 解析,删除两份硬编码元组;契约测试覆盖该模式;随资产分发(资产已含 core 与 test_validate_workflow.py,目标侧自包含成立)。
3. **P2a**:新增 `scripts/hooks/pre-push`(执行秒级 core 校验,FAIL 即阻断 push),README.md 增"本地防护"一节说明 `git config core.hooksPath scripts/hooks` 选择性启用;钩子为源仓自愿机制,不进安装资产。
4. **P2b**:wrapper 新增 `--fast`(仅跑 core,跳过契约套件,汇总口径不变);verify/archive 技能(双侧+资产)更新:标准模式 Verify 终验改跑 `--fast` + 目标/回归测试,Archive 归档后验证保持全量,严格模式两处保持 `--require-openspec` 全量不变;mutation 断言的既有短语全部保留。
5. **P2d**:wrapper 加 best-effort `flock` 锁(`.ai-local` 下锁文件,无 flock 工具时降级为无锁并继续),第二实例立即报错退出,不再互踩。
6. **P3d**:CLAUDE.md 与 AGENTS.md(及资产通用版)各加一行:仓库技能与宿主插件技能重叠时仓库技能优先,插件技能仅作补充。
7. **archive 技能**(双侧+资产)补一步:归档时更新 `openspec/archive/README.md` 索引行(上一变更已建立该索引)。

## Impact

- 运行时:wrapper/core CLI 新增两种模式(默认行为不变);CI 新增步骤;新增钩子脚本;不改安装器事务逻辑。
- 技能与入口:verify/archive 技能、CLAUDE/AGENTS 尾注变更,双侧镜像与资产副本同步更新,mutation/镜像/资产一致性校验必须全绿。
- 规格:`shared-ai-workflow-infrastructure` MODIFIED(CI 必跑安装器套件)+ 两个 ADDED(命令清单单一来源;校验并发防护与本地推送钩子);`risk-tiered-ai-workflow` 两个 ADDED(验证门禁按阶段分层;仓库技能优先)。
- 整合策略(建议):严格默认隔离 worktree;归档后本地 `--no-ff` 合回 main、合并结果复跑全量门禁、推送(本次一并授权)。
