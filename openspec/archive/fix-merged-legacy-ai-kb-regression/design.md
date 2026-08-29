# Design

## 关键决策

1. **逐字迁移 10 条 memory 条目,不做改写**。旧条目已符合 `memory/README.md` 固定格式(日期·来源变更 + 坑/解);只改措辞会引入无证据的二次失真。条目按日期置于 `workflow.md` 顶部(2026-08-16 早于现存最早条目 2026-08-17)。两侧旧 memory 并非互为镜像:claude 侧 7 条(2 installer + 5 workflow-system),codex 侧 `workflow-system.md` 在相同 5 条外另有 3 条「工作流端到端验证(临时项目 add-greeting)」独有条目——初版只核对并迁移了 claude 侧,综合审查以逐文件 `grep -c '^## '` 计数揭穿(VQ-C01),已补迁。其中 init-workflow-system 第 5 条("verify 应把状态回写列为收尾步")的建议已在现行 verify 技能落地,作为历史记录原样保留——memory 是追加式历史,不回溯修订。

2. **旧 kb/overview.md 与 rules/index.md 不迁移、直接删除**。逐行比对确认其独有内容仅描述迁移前架构(五阶段流程、`.claude/ai-kb` 作为知识库、`install-workflow.sh --force` 覆盖语义),全部被共享层 `.ai/kb/overview.md`、`.ai/rules/index.md` 的现行版本取代且后者更新(共享层差 64/28 行均为演进)。保留任何一份都会形成可独立演化的第二真源,正是规格禁止的对象。

3. **终止形态对齐 origin 迁移后基线**。两侧 ai-kb 目录仅保留 `README.md` 兼容入口(与 9614f9e 的 `git ls-tree` 一致);`kb/`、`rules/`、`memory/` 目录整体消失,不留 `.gitkeep`——校验器对不存在目录直接跳过,README 存在性检查不受影响。

4. **不动安装资产**。`scripts/ai-workflow-assets/` 与 `manifest.json` 的 ai-kb 条目只有两个 README,未被合并污染;任何"顺手"资产调整都是范围扩大。

5. **不借本变更做 memory 分模块拆分**(审计 P3 项)。拆分是独立优化,混入会把"恢复合规"扩大为知识层重构,触发重新确认。

## 替代方案

- **回退合并(revert 45e8ed1)**:会连带撤销 origin 侧合入的 add-installer-upgrade-path 等有效成果,破坏面远大于删除 10 个文件,否决。
- **只删不迁**:丢失 7 条已验证未迁移的踩坑知识,违反"删除前核对迁移"边界,否决。
- **快速模式直接改**:涉及 tracked 文件删除与治理合规恢复,且需要审查留痕,按标准模式走四件套。

## 风险与边界

- **知识丢失风险**:已逐条 grep 验证 10 条 memory(含 codex 侧 3 条独有)在共享层零命中;kb/rules 独有内容确认为废弃描述(综合审查 VQ-M01 独立核验支持)。教训:双侧同名文件不必然同内容,核对迁移必须逐侧计数。残余风险:低——已由独立审查的差异复审覆盖。
- **校验器并发假失败**:契约套件含 mutation 测试,两实例并行互踩。全程串行单实例运行,长跑用后台任务等待,不加短 timeout。
- **时间成本**:契约套件单跑约 5 分钟,完整校验预计 6-8 分钟;Verify/Archive 各需现跑一次。
- **范围外(不做)**:pre-push 钩子/分支保护(审计 P2)、安装器测试纳入 CI(P1)、白名单单一来源化(P1)、memory 分模块(P3)。
