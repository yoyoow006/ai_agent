# 审查台账(标准模式唯一一次全 diff 综合审查 + VQ-C01 差异复审)

- 首轮 manifest:`730107c61d41694a25dd717c82c3aabf7865c4ef0b1a48edfbb9520f74b5f2ab`(base=main/45e8ed1,HEAD=3a73c79,reviewer 两次 verify VALID)
- 差异复审 manifest:`1bddc094a929aaf019b1820263fdeced8d1269c4272ab6df358c5c3bdadfa4d7`(base=main,HEAD=cdcf5a2,reviewer 两次 verify VALID)
- 审查者:独立上下文 reviewer(.claude/agents/reviewer.md 共享契约);意见均经主会话亲自核实后处置。

## VQ-C01 Critical → resolved

```text
id: VQ-C01
severity: Critical
repo/path:line: .codex/ai-kb/memory/workflow-system.md(已删,原文见 45e8ed1);落点 .ai/memory/workflow.md:29-40;初版错误事实源 proposal/design/tasks
evidence: codex 侧该文件实有 8 条(尾部 3 条「工作流端到端验证(临时项目 add-greeting)」独有),逐文件 grep -c '^## ' 计数 2/5/2/8;3 条在共享层与主规格零命中;初版仅迁 claude 侧 7 条即删。
observable impact: 3 条活知识将永久缺失,违反本变更 delta 新增 Scenario 第 2 条 THEN(先迁共享层缺失条目再删除)。
status: resolved(修复提交 cdcf5a2:awk 逐字补迁至 10 条/56 条,md5 双侧一致;proposal/design/tasks 及审计 memory 事实源同步更正;core 复跑 PASS=184 FAIL=0)
minimal fix: 已完成——在已确认范围内补迁 + 更正事实源,未扩大行为/依赖/迁移/外部副作用。
verification: 主会话逐侧计数/零命中 grep 核实;reviewer 差异复审 (a)-(e) 现跑证据(逐字 diff 为空、落点正确、计数相符、事实源一致、core 184/0、diff --check 干净),结论 resolved。
```

## VQ-M01 Minor → not-an-issue

```text
id: VQ-M01
severity: Minor
repo/path:line: design.md:7(design 主张"旧 kb/rules 无可保留独有事实")
evidence: 四文件与共享层逐行比对,五阶段/install-workflow.sh --force 均已被取代;唯一残留"13 技能"可平凡再推导且共享层按角色描述属有意选择。
observable impact: 无。
status: not-an-issue(独立核验支持 design 主张)
minimal fix: 无
verification: reviewer 逐行比对,无需动作。
```

## 未验证范围

- 完整门禁 `bash scripts/validate-workflow.sh` 在首轮审查与差异复审中均未由 reviewer 复跑(须串行单实例、约 5-8 分钟);由主会话终验(4.1)现跑并读取结果。

## 残余风险

- origin/main(45e8ed1)CI 持续为红,直至整合推送(6.1,已获用户授权)完成;期间基于 main 的克隆会拿到平行正文。
- 补迁的 3 条条目描述 2026-08-16 旧安装器(`install-workflow.sh`)行为,按追加式历史原样保留,与现行 `install-ai-workflow.sh` 术语存在轻度混淆可能(低;来源行标注历史变更名)。
- 第二工作目录 `/home/yoyoo/wksoft/sources/gitdemo/ai_agent` 不在本审查 manifest 逐仓范围。
