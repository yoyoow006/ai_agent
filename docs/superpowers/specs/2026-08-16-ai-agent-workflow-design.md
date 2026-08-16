# AI 编程助手工作流 — 设计文档

- 日期：2026-08-16
- 状态：已确认（用户于本次会话逐节批准）
- 目标仓库：`ai_agent/`（本仓库）

## 1. 背景与目标

构建一套不依赖任何第三方 Claude 插件（openspec 插件、superpowers 插件）的 AI 编程助手工作流，将两者的能力**无损迁移**为原生资产：

- 流程骨架取自 openspec：规范（specs）、设计（design）、任务清单（tasks）、归档（archive）
- 执行纪律取自 superpowers：头脑风暴、写计划、执行计划、子代理驱动开发、TDD、两阶段代码审查、完成前验证

参考 Comet 工作流的五阶段模型：**Open → Design → Build → Verify → Archive**。

### 已确认的决策

| 决策点 | 结论 |
|---|---|
| 部署形态 | 可复制模板仓库：全部资产为纯文本，整体复制到任何项目即用 |
| openspec CLI 兼容 | 保持兼容：工作流零依赖可独立跑通；装有 CLI（1.4.1）的机器额外获得 `list/validate` 机械校验 |
| 语言 | 全中文（技能指令与生成文档均为中文） |
| Git 策略 | 每个变更一个 `feature/<变更名>` 分支，Archive 阶段合回主干；需要并行隔离时用 worktree |
| 技能组织 | 方案 A：5 个阶段编排技能 + 支撑技能群（分层） |
| AI 知识库 | `.claude/ai-kb/`：kb（功能/架构文档）+ memory（踩坑/注意事项）+ rules（模块映射/别称/关键词） |

## 2. 总体架构

一句话：**CLAUDE.md 是宪法（路由 + 硬门禁），阶段技能是编排器，支撑技能是执行器，`openspec/` 是数据层（状态唯一真源），`.claude/ai-kb/` 是知识层。**

```
ai_agent/                              # 模板仓库本体
├── CLAUDE.md                          # 工作流总纲：五阶段路由 + 硬门禁 + ai-kb 使用规则
├── .claude/
│   ├── skills/                        # 原生技能，零插件依赖
│   │   ├── open/SKILL.md              # 阶段1：探索+提案
│   │   ├── design/SKILL.md            # 阶段2：计划书
│   │   ├── build/SKILL.md             # 阶段3：编排 TDD 子代理
│   │   ├── verify/SKILL.md            # 阶段4：双重验证+两阶段审查
│   │   ├── archive/SKILL.md           # 阶段5：归档+合并+提交
│   │   ├── tdd/SKILL.md               # 支撑：红-绿-重构
│   │   ├── subagent-driven/SKILL.md   # 支撑：子代理开发
│   │   ├── code-review/SKILL.md       # 支撑：请求/接收审查（合并版）
│   │   ├── systematic-debugging/SKILL.md  # 支撑：根因四阶段
│   │   ├── verification/SKILL.md      # 支撑：完成前验证
│   │   ├── git-worktrees/SKILL.md     # 支撑：worktree 隔离（可选）
│   │   ├── parallel-agents/SKILL.md   # 支撑：并行派发
│   │   └── writing-skills/SKILL.md    # 支撑：技能自进化
│   └── ai-kb/                         # AI 知识库（随仓库走）
│       ├── README.md                  # 三类文档格式约定
│       ├── kb/                        # 模块功能介绍+架构设计
│       │   ├── overview.md            #   系统级总览（骨架预置）
│       │   └── <模块名>.md
│       ├── memory/                    # 踩坑记录+注意事项（按模块追加式）
│       │   └── <模块名>.md
│       └── rules/
│           └── index.md               # 全局路由表：模块名|代码路径|别称|关键词
└── openspec/                          # 数据层
    ├── project.md                     # 项目上下文（openspec init 格式）
    ├── AGENTS.md                      # artifact 格式约定（CLI 兼容）
    ├── changes/                       # 活跃变更
    │   └── <变更名>/
    │       ├── proposal.md            #   为什么做/做什么 + 状态头
    │       ├── specs/<能力>/spec.md    #   Requirements delta
    │       ├── design.md              #   技术上下文、决策、权衡
    │       └── tasks.md               #   勾选清单（进度真源）
    ├── plan/                          # 计划书（CLI 忽略此目录）
    │   └── <变更名>.md
    ├── specs/                         # 主规范：能力当前真源
    │   └── <能力>/spec.md
    └── archive/                       # 已归档变更（含 plan 副本）
        └── <变更名>/
```

### 关键机制

- **状态在文件里**：`proposal.md` 头部 `状态:` 字段（草稿|待确认规范|待确认计划|构建中|待验证|待归档|已归档）+ `tasks.md` 勾选率。新会话读这两个文件即无损续接，无需额外状态管理。
- **技能触发双通道**：模型按 description 自动匹配阶段；用户可显式 `/open` `/design` `/build` `/verify` `/archive` 调用（原生技能即命令，无需 commands 双轨）。

## 3. AI 知识库（`.claude/ai-kb/`）

### 与五阶段的集成（4 个读写点）

| 阶段 | 操作 | 说明 |
|---|---|---|
| Open（读） | 先读 `rules/index.md` 将需求说法路由到模块（"登录/鉴权/SSO" → `src/auth/`），再读对应 `kb/`、`memory/` | 探索代码库前先探索知识库 |
| Build（读） | 派发子代理时附上受影响模块的 memory 摘要 | 实现者带着前车之鉴写代码 |
| Build 中（随时写） | `systematic-debugging` 硬规则：每个坑解决后立即追加到 `memory/<模块>.md` | 即时捕获，不等归档 |
| Archive（写，硬门禁项） | 知识沉淀：新坑归整进 memory；功能/架构变化同步 kb；新别称/关键词更新 rules | 归档清单第 6 项 |

### memory 条目格式（追加式）

```markdown
## 2026-08-16 · 来源变更 add-user-auth
**坑**：sqlite 并发写报 database is locked
**解**：改用 WAL 模式 + busy_timeout=5000；测试需用独立临时库
```

### 设计取舍

1. `rules/` 用单一 `index.md` 全局路由表而非按模块拆分——路由是"先查表才知道模块"的鸡生蛋问题，一张表模型一次读完即可路由；某模块规则膨胀后再拆独立文件。
2. `kb/overview.md` 为骨架预置空模板，Open 阶段发现缺失/过时会提示，Archive 阶段负责写。

## 4. 状态机与硬门禁

```
需求 → [Open] → 草稿 ──用户确认四件套──→ [Design] → 待构建 ──用户确认计划──→ [Build] → 构建完成
                                                                            │
      已归档 ←──合并+提交──── [Archive] ←──审查通过──── [Verify] ←──全勾+全绿──┘
```

### 硬门禁（不过门禁绝不推进）

| 门禁 | 通过条件 |
|---|---|
| Open → Design | 用户明确确认 proposal + specs + design + tasks 四件套 |
| Design → Build | 用户明确确认计划书 |
| Build → Verify | tasks.md 全勾 + 全部测试绿 + 每个勾选都有命令输出证据 |
| Verify → Archive | 两阶段审查通过 +（装有 CLI 则）`openspec validate` 绿 |

### 断点续传

任何会话中断后，新会话读 `proposal.md` 状态 + `tasks.md` 勾选率即恢复现场，从断点阶段继续。

## 5. 五阶段流程

### ① Open（探索 + 提案）

1. 读 ai-kb：rules 路由 → 相关模块 kb + memory
2. 探索代码库相关模块
3. 逐个澄清问题（一次一问，多选优先）
4. 产出四件套：`proposal.md`、`specs/<能力>/spec.md`（delta，Requirement 标注 ADDED/MODIFIED/REMOVED）、`design.md`、`tasks.md`
5. 自审：占位符/矛盾/歧义/范围
6. 请用户确认

### ② Design（计划书）

1. 对照 spec 查漏：边界场景、错误处理、被漏掉的需求；有缺口的先补回 spec
2. 写 `openspec/plan/<变更名>.md`：每个任务精确到**文件路径、改动说明、验证命令、验收标准、依赖关系**——子代理拿到单任务即可独立执行
3. 计划自审
4. 用户确认后创建 `feature/<变更名>` 分支（需隔离时用 worktree 技能）

### ③ Build（子代理 + TDD）

1. 逐任务派发子代理：派发提示 = 单任务计划 + 受影响模块 memory 摘要 + TDD 硬规则
2. TDD 硬规则：先写失败测试 → 最小实现通过 → 重构；禁止先写实现
3. 主会话逐个审查子代理产出（diff + 测试证据），通过才勾选 tasks.md
4. 测试红 → `systematic-debugging`（根因四阶段）；坑解决后立即记 memory
5. 独立任务用 `parallel-agents` 并行派发
6. 全勾 + 全绿 → 进入 Verify

### ④ Verify（双重验证）

两阶段审查均由**独立子代理**执行（防自查偏见）：

- **阶段一·规格符合性**：逐条对照 spec delta 的 Requirement，找"规格说了但代码没做 / 代码做了但规格没说"
- **阶段二·代码质量**：找缺陷（正确性、安全、性能、可维护性）

审查意见按 `receiving-code-review` 纪律处理：**先验证再实施**——有理的改，无理的据实反驳，不表演性顺从。修复后复审，直到两阶段都通过。最后按 `verification-before-completion` 运行完整验证命令留存证据（无证据不声称完成）。

### ⑤ Archive（归档 + 提交）— 六步

1. delta 合并进 `openspec/specs/<能力>/spec.md`（ADDED 添加 / MODIFIED 替换 / REMOVED 删除）
2. tasks 全勾终检 + proposal 状态改"已归档"
3. 知识沉淀（ai-kb 三写：memory / kb / rules）
4. 变更目录连同 plan 副本移入 `openspec/archive/<变更名>/`
5. 合并 feature 分支回主干并删除分支
6. git commit（文档 + 代码一次入库）

## 6. 无损迁移映射表（验收清单）

### superpowers 6.2.0（14 技能）

| 原技能 | 迁移去向 | 方式 |
|---|---|---|
| using-superpowers | CLAUDE.md 总纲 | 改写为五阶段路由 |
| brainstorming | open（澄清问答）+ design（查漏） | 拆两段全文移植 |
| writing-plans | design | 全文移植 |
| executing-plans | build（单人直执路径） | 移植 |
| subagent-driven-development | build（子代理路径） | 移植 |
| test-driven-development | tdd | 纪律逐条保留 |
| requesting-code-review | code-review + verify | 移植 |
| receiving-code-review | code-review + verify | 合并为两节 |
| systematic-debugging | systematic-debugging | 原文迁移 + 新增"记 memory"规则 |
| verification-before-completion | verification | 原文迁移 |
| using-git-worktrees | git-worktrees | 原文迁移 |
| dispatching-parallel-agents | parallel-agents | 原文迁移 |
| finishing-a-development-branch | archive | 移植 |
| writing-skills | writing-skills | 原文迁移（助手自进化） |

### openspec 插件侧

| 原能力 | 迁移去向 |
|---|---|
| explore + propose | open 技能（artifact 格式规范内嵌） |
| verify-change | verify 技能（Requirement 逐条对照） |
| archive-change | archive 技能（delta 合并算法 + 归档移动） |
| CLI 模板与校验规则 | openspec/AGENTS.md |

**"无损"验收标准**：逐技能对照——每个原技能的每条硬规则（HARD-GATE、纪律、检查清单）在新技能或 CLAUDE.md 中有对应条款。

## 7. 错误处理（回退路径）

| 故障 | 处理 |
|---|---|
| Open 发现需求过大 | 分解为多个变更，各自独立走五阶段 |
| Build 测试红 | systematic-debugging 根因四阶段，修复后重跑；坑即时记 memory |
| 子代理产出不合格 | 退回重做，退回单必须附明确不合格原因 |
| Verify 发现规格偏差 | 回 Build 补齐；spec 本身要改则回 Design 补计划 |
| 审查意见有争议 | 按 receiving-code-review 先验证；无法一致 → 用户仲裁 |
| Archive 合并冲突 | 停下报告，等人工决策 |
| 任何不确定 | 停下问用户，不猜 |

## 8. 验收方式（对助手本身）

1. **Dogfood**：用本工作流开发本工作流（本设计文档 → 计划书 → Build 产出全部技能文件）
2. 映射表逐条对照：每个原技能的硬规则在新文件中有对应条款
3. 冒烟演练：建示例变更走完五阶段，产物齐全、`openspec validate` 绿
4. 断点续传测试：中途换新会话，凭文件状态恢复现场
