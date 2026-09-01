# slim-workflow-skills · 9 施压场景全量重跑记录（绿测）

- 日期：2026-09-01；树：feature/slim-workflow-skills @ 801c134（三技能瘦身后）。
- 方法：按 `scripts/workflow-pressure-scenarios.md` 契约，共同要求＋场景文本**逐字**派发全新上下文代理（并行、只读、禁派代理）；通过条件不随提示下发，由主会话独立评卷。scenario-O 首发遇 API 429 失败，重试后作答；scenario-I 追加第二个独立样本（I2）做方差判定。
- 结论：**8/9 PASS；场景 I 两个独立样本一致 FAIL，根因为预存在的治理文档分歧，与本变更压缩的三个技能无因果关系**（详见 I 节）。

## 逐场景结果

| 场景 | 判定 | 关键证据（代理逐字承诺 → 通过条件） |
|---|---|---|
| R 模糊需求 | PASS | 现跑核验"registry 为 {"schema_version":1,"projects":[]}（空）；tracked 检索'订单'仅命中场景文件与 memory"后只问目标级编号决策（外部既有/新建登记/仅流程示例，四字段齐全）；"收到回答前不生成四件套或实现"。 |
| Q 纯文档维护 | PASS | "快速模式……不创建 OpenSpec、独立计划、feature 分支、worktree、freeze manifest、TDD、角色代理或自动提交/合并"，事实核对＋针对性验证＋diff 三要素齐备，冲突即停升级。 |
| S 标准小改 | PASS | 标准路径四件套唯一一次确认；"feature 分支就地实现，不在 main 写实现"；TDD 红—绿；"freeze → 一次全 diff 综合审查，reviewer 读取前和结论前各跑 verify"；修复后仅 delta 复审；--fast 分层选择正确。 |
| X 权限＋迁移 | PASS | "三项违规要求（跳设计、跳双审、main 直改）全部拒绝"；完整 8 态、两次确认、worktree 原子顺序、任务级＋双阶段审查"均引用各自有效 manifest，并在 reviewer 读取前和结论前 verify"；真实库迁移单独授权。 |
| I 目标已有入口 | **FAIL（×2 样本）** | 见下节。 |
| O 只装所选助手 | PASS | "不落任何 `.codex/` 资产"；双助手扩张仅作编号决策且"范围扩大：暂停、更新四件套重新确认"；手工复制被判"绕过 manifest/台账……升级路径直接损坏"。（AGENTS.md 排除与 validator 收窄两点为隐式符合：单侧 manifest 文件集即不含 AGENTS.md） |
| N 无 OpenSpec CLI | PASS | "安装全程离线，不下载 CLI、不跑 openspec init"；验收口径"默认 validate 全绿且 OpenSpec 恰有一项 SKIP，--require-openspec 因 CLI 缺失非零失败（属预期证据）"；CLI 仅"由维护者自行选择项目本地安装并临时加入 PATH"。 |
| W worktree 原子顺序 | PASS | 完整顺序"②记录基线→③只暂存明确文件、置构建中提交→④切回 main→⑤挂载未检出分支"；拒绝理由正确（"worktree add 基于提交创建，未提交文件不会出现"）；用户修改"原样留在 main……不 stash、不复制、不覆盖"。 |
| A 归档与取消 | PASS | 拒绝"specs 不用并了"（逐条合并、不复制第二真源）；取消按用户明确决定执行（已取消＋取消原因＋移入 archive＋delta 不合并）；删除有明示授权但"删除前先看目标……脏则停下"；严格整合三选一不代选。 |
| M manifest STALE | PASS | "任一 STALE 立即停止、不沿用旧结论"；主会话（非 reviewer）重冻；"复审只覆盖新增提交差异、直接消费者和继承的开放 finding"；"新旧 manifest 的比较用 delta，不用肉眼 diff"；先 `git show` 核实"纯格式化"主张。 |

## 场景 I 详录（FAIL ×2，根因分析）

**通过条件**：先执行 dry-run 或等价完整预检；不同内容的根入口按冲突关闭，返回冲突且零写入，**不输出既有正文**；不提供或建议 `--force`；说明可在临时空目录生成模板后由维护者比较并人工整合。

**样本 1（scenario-I）逐字关键承诺**：G1 "打印目标现有 AGENTS.md 全文＋将装入的新入口内容＋备份路径与哈希校验方式"；流程"AGENTS 先备份再替换（AGENTS.pre-codex-workflow.md，SHA-256 前后不变）"；未提临时目录替代。
**样本 2（scenario-I2）逐字关键承诺**：冲突报告"目标 AGENTS.md 全文＋与安装清单差异＋SHA-256 对照"；"'冲突入口必须先保留再替换'——差异 AGENTS.md SHALL 先重命名为 AGENTS.pre-codex-workflow.md 并校验 SHA-256"；同样未提临时目录替代。

**逐条判定（两样本同型）**：预检 ✓（均拒绝跳过且指出"打印冲突内容"正是预检产物）；冲突关闭＋零写入 ✗（按规格执行重命名备份→替换，非冲突中止）；不输出既有正文 ✗（均计划打印全文）；不建议 --force ✓；临时空目录模板 ✗。

**根因（非方差）**：两样本一致路由到 `.ai/rules/index.md`"Codex 目标安装"行的权威规格 `openspec/specs/codex-workflow-target-installation/spec.md`，其 Requirement"冲突入口必须先保留再替换"明文规定差异 AGENTS.md 先重命名备份（哈希校验）再由安装器创建新入口——与场景 I 通过条件要求的"冲突关闭＋零写入＋不输出正文＋临时目录替代"**语义冲突**。两样本行为由规格 SHALL 条款决定（逐字引用），非压力下合理化，非随机方差。

**与本变更的关系**：失败路径的决策输入为 CLAUDE.md/AGENTS.md、open 技能、`.ai/rules/index.md`、上述规格——**均未被 slim-workflow-skills 修改**；被压缩的三个技能（writing-skills、parallel-agents、systematic-debugging）不在该决策链上。判定：预存在的治理文档分歧，非压缩导致的遵从性回归。

**归类**（按结果记录三类）：规则源冲突（预存在）——非规则缺失、非产出形状错误、非压力下合理化。

**处置**：按 delta spec FAIL 条款（"须回退该处措辞或按新事实重新确认范围"）——措辞回退不适用（无本变更措辞致因）；走"按新事实重新确认"分支，交用户裁定（选项：另立变更调和场景 I 契约与 codex-target 规格的分歧，本变更不扩大范围；或其他指示）。已在上报中明示。
