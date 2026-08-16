# init-workflow-system 实现计划

> **执行者须知：** 必须使用子代理驱动开发（推荐）或逐任务直执方式实现本计划，一次一个任务。步骤用 `- [ ]` 复选框追踪。

**目标：** 在本仓库建成零插件依赖的五阶段 AI 编程助手工作流（CLAUDE.md + 13 技能 + ai-kb 知识库 + openspec 目录），并以本变更自身完成首次全流程 dogfood。

**架构：** CLAUDE.md 是宪法（路由+硬门禁），5 个阶段技能是编排器，8 个支撑技能是执行器，`openspec/` 是状态真源（CLI 兼容），`.claude/ai-kb/` 是知识层。全部资产为纯文本，`scripts/validate-workflow.sh` 是结构不变量的"测试套件"。

**技术栈：** Markdown（SKILL.md 带 YAML frontmatter）、Bash（校验脚本）、Git（feature 分支流）、openspec CLI 1.4.1（可选校验）。

## 全局约束

- 全中文：技能指令与生成文档均中文
- 零运行时依赖：不引入任何包管理器依赖；纯 markdown + bash
- 源技能路径（本机，仅构建期读取）：`/home/yoyoo/.claude/plugins/cache/claude-plugins-official/superpowers/6.2.0/skills/<技能名>/SKILL.md`
- frontmatter 统一格式：`name: <目录名>` + `description: <一句中文触发条件>`
- 提交规范：`feat:`/`docs:`/`chore:` 前缀 + 中文描述，每个任务至少一次提交
- 不修改 `.gitignore` 之外的本机全局配置
- 工作分支：`feature/init-workflow-system`（Task 1 创建，Task 8 合并回 main）

## 文件结构总览

| 文件 | 职责 | 产生任务 |
|---|---|---|
| `CLAUDE.md` | 总纲：五阶段路由 + 硬门禁 + 8 态 + ai-kb 规则 | 2 |
| `.claude/skills/{open,design,build,verify,archive}/SKILL.md` | 阶段编排技能 | 5,6 |
| `.claude/skills/{tdd,subagent-driven,code-review,systematic-debugging,verification,git-worktrees,parallel-agents,writing-skills}/SKILL.md` | 支撑技能 | 3,4 |
| `.claude/ai-kb/{README.md,kb/overview.md,rules/index.md}` | 知识库骨架与格式约定 | 1 |
| `openspec/{project.md,AGENTS.md}` | CLI 兼容基础文件 | 1 |
| `openspec/changes/init-workflow-system/*` | 本变更四件套 | 1 |
| `scripts/validate-workflow.sh` | 结构不变量测试套件 | 1 |

---

### Task 1: 骨架、变更四件套与校验脚本

**Files:**
- Create: `openspec/project.md`、`openspec/AGENTS.md`
- Create: `openspec/changes/init-workflow-system/{proposal.md,design.md,tasks.md}`、`openspec/changes/init-workflow-system/specs/workflow-system/spec.md`
- Create: `.claude/ai-kb/README.md`、`.claude/ai-kb/kb/overview.md`、`.claude/ai-kb/rules/index.md`、`.claude/ai-kb/memory/.gitkeep`
- Create: `scripts/validate-workflow.sh`
- Create 分支: `feature/init-workflow-system`

**Interfaces:**
- Consumes: 已批准的设计文档 `docs/superpowers/specs/2026-08-16-ai-agent-workflow-design.md`、已保存的本计划
- Produces: 目录骨架（后续所有任务的写入目标）、8 态状态字段约定、frontmatter 约定、校验脚本（后续每任务的"测试"命令）

- [ ] **Step 1: 创建 feature 分支与目录骨架**

```bash
git checkout -b feature/init-workflow-system
mkdir -p openspec/changes/init-workflow-system/specs/workflow-system \
         openspec/plan openspec/specs openspec/archive \
         .claude/skills .claude/ai-kb/{kb,memory,rules} scripts
touch .claude/ai-kb/memory/.gitkeep
```

- [ ] **Step 2: 取样 openspec 官方格式（保证 CLI 兼容）**

```bash
openspec init /tmp/os-sample --tools none --force
find /tmp/os-sample -name '*.md' | head -20 && cat /tmp/os-sample/openspec/project.md 2>/dev/null | head -30
```

Expected: 样例目录生成。对照样例确认 `project.md`、changes 目录结构后再写我们的版本；若样例结构有出入，以样例为准调整 Step 3-4 的文件位置，`openspec list` 能识别为准。

- [ ] **Step 3: 写 openspec 基础文件**

`openspec/project.md`（内容要点，全文照写）：

```markdown
# 项目上下文

本仓库是 AI 编程助手工作流的模板仓库：CLAUDE.md（总纲）+ .claude/skills/（13 个原生技能）+ .claude/ai-kb/（知识库）+ openspec/（变更数据层）。

目的：脱离第三方插件依赖，将 openspec 与 superpowers 的能力无损迁移为原生资产。
```

`openspec/AGENTS.md`（内容要点，全文照写）：

```markdown
# artifact 格式约定（CLI 兼容）

- 变更目录：`openspec/changes/<kebab-case变更名>/`
- 四件套：`proposal.md`、`specs/<能力>/spec.md`（delta，Requirement 标注 ADDED/MODIFIED/REMOVED，每条至少一个 Scenario）、`design.md`、`tasks.md`（`- [ ] 1.1` 编号勾选）
- proposal.md 头部：`状态:` 字段，取值：草稿|待确认规范|设计中|待确认计划|构建中|待验证|待归档|已归档
- 归档：目录整体移入 `openspec/archive/`，delta 合并进 `openspec/specs/<能力>/spec.md`
- 校验：`openspec validate <变更名> --strict --no-interactive`
```

- [ ] **Step 4: 写本变更四件套（Open/Design 阶段回填——两阶段均已获用户确认）**

`openspec/changes/init-workflow-system/proposal.md`（全文照写）：

```markdown
# 变更提案：init-workflow-system

状态: 构建中
分支: feature/init-workflow-system
创建: 2026-08-16

## 为什么
当前依赖 openspec/superpowers 两个第三方 Claude 插件，不可控且难迁移。需要一套零插件、纯文本、随仓库走的工作流，能力无损。

## 做什么
- CLAUDE.md 工作流总纲（五阶段路由 + 硬门禁）
- .claude/skills/ 13 个原生技能（5 阶段 + 8 支撑）
- .claude/ai-kb/ 知识库骨架（kb / memory / rules）
- openspec/ 目录骨架与 CLI 兼容约定
- 以本变更自身完成首次五阶段 dogfood

## 影响
全新仓库，无存量代码。规格与设计见 specs/workflow-system/spec.md 与 design.md。
```

`openspec/changes/init-workflow-system/specs/workflow-system/spec.md`（全文照写，Requirement 逐条对应设计文档第 2-7 节）：

```markdown
# workflow-system 规范 delta

## ADDED Requirements

### Requirement: 五阶段工作流
系统 SHALL 以 Open → Design → Build → Verify → Archive 五阶段组织代码变更，每阶段有独立技能与产出物。
#### Scenario: 新需求进入
- **WHEN** 用户提出开发需求
- **THEN** 助手进入 Open 阶段产出四件套（proposal/specs delta/design/tasks），等待用户确认

### Requirement: 硬门禁
系统 SHALL 在四个推进点强制门禁：Open→Design 需用户确认四件套；Design→Build 需用户确认计划书；Build→Verify 需 tasks 全勾+测试全绿+有证据；Verify→Archive 需两阶段审查通过。
#### Scenario: 未确认不得推进
- **WHEN** 四件套未获用户确认
- **THEN** 不得开始计划编写

### Requirement: 状态真源与断点续传
系统 SHALL 将变更状态存于 proposal.md 的 状态 字段（8 态）与 tasks.md 勾选率，新会话凭文件恢复现场。
#### Scenario: 会话中断恢复
- **WHEN** 新会话开始且存在活跃变更
- **THEN** 读取状态字段与勾选率，从断点阶段继续

### Requirement: 原生技能库
系统 SHALL 提供 13 个技能：open/design/build/verify/archive 五阶段技能 + tdd/subagent-driven/code-review/systematic-debugging/verification/git-worktrees/parallel-agents/writing-skills 支撑技能。
#### Scenario: 显式调用
- **WHEN** 用户输入 /build
- **THEN** 加载 build 技能并从 tasks.md 断点继续

### Requirement: ai-kb 知识库
系统 SHALL 维护 .claude/ai-kb/ 三层知识：kb（功能/架构）、memory（踩坑/注意事项，追加式）、rules（全局路由表）。Open 阶段先读后探索；Build 派发附 memory 摘要；坑解决后即时记 memory；Archive 阶段三写沉淀。
#### Scenario: 归档沉淀
- **WHEN** 变更通过验证进入归档
- **THEN** memory/kb/rules 依据本变更新知识完成更新

### Requirement: TDD 硬规则
Build 阶段 SHALL 遵循红-绿-重构：先写失败测试并运行确认失败，再最小实现，再重构；禁止先写实现。
#### Scenario: 实现前必须有失败测试
- **WHEN** 子代理开始实现某任务
- **THEN** 其首个产出是对应的失败测试与失败运行证据

### Requirement: 两阶段审查
Verify 阶段 SHALL 由独立子代理执行规格符合性审查与代码质量审查；审查意见先验证后实施，争议由用户仲裁。
#### Scenario: 规格偏差
- **WHEN** 阶段一发现代码与 delta 不符
- **THEN** 退回 Build 补齐后复审

### Requirement: 归档六步
Archive 阶段 SHALL 依次：合并 delta 进主 specs → tasks 全勾终检+状态改已归档 → 知识沉淀 → 变更目录与计划书移入 archive → 合并 feature 分支并删除 → git commit。
#### Scenario: 计划书归位
- **WHEN** 归档完成
- **THEN** openspec/plan/ 不再含该变更计划，archive/ 内含其副本

### Requirement: openspec CLI 兼容
目录格式 SHALL 兼容 openspec CLI：装有 CLI 的机器可通过 list/validate 校验；未安装时工作流完整可用。
#### Scenario: 无 CLI 环境
- **WHEN** 机器未装 openspec CLI
- **THEN** 五阶段流程仍可完整走通

### Requirement: 零插件依赖
全部能力 SHALL 由本仓库内纯文本文件承载，不引用任何插件市场技能名。
#### Scenario: 裸机复制
- **WHEN** 仓库被复制到无任何插件的新机器
- **THEN** 工作流全部功能可用
```

`openspec/changes/init-workflow-system/design.md`（全文照写）：

```markdown
# 设计：init-workflow-system

详细设计见已批准文档：docs/superpowers/specs/2026-08-16-ai-agent-workflow-design.md（本文件为索引）。

## 关键决策
1. 可复制模板仓库形态（资产纯文本随仓库走）
2. 保持 openspec CLI 兼容（零依赖但白赚校验）
3. 全中文
4. feature 分支流（worktree 可选）
5. 技能分层：5 编排 + 8 支撑
6. ai-kb 四读写点（Open 读 / Build 读 / 随时写 / Archive 写）
7. 迁移映射表 = 无损验收清单（设计文档第 6 节）
```

`openspec/changes/init-workflow-system/tasks.md`（全文照写，与计划 Task 一一对应）：

```markdown
# 任务清单：init-workflow-system

## 1. 骨架与四件套
- [ ] 1.1 feature 分支 + 目录骨架
- [ ] 1.2 openspec 基础文件（project.md / AGENTS.md）
- [ ] 1.3 本变更四件套回填
- [ ] 1.4 ai-kb 骨架文件
- [ ] 1.5 校验脚本（骨架项绿、技能项红）
## 2. CLAUDE.md 总纲
- [ ] 2.1 编写并自验
## 3. 支撑技能·纪律组
- [ ] 3.1 tdd
- [ ] 3.2 systematic-debugging（+记 memory 规则）
- [ ] 3.3 verification
- [ ] 3.4 git-worktrees
- [ ] 3.5 parallel-agents
## 4. 支撑技能·协作组
- [ ] 4.1 subagent-driven
- [ ] 4.2 code-review（请求+接收合并版）
- [ ] 4.3 writing-skills
## 5. 阶段技能·上半
- [ ] 5.1 open（brainstorming 澄清段 + openspec propose 格式）
- [ ] 5.2 design（brainstorming 查漏段 + writing-plans 移植）
## 6. 阶段技能·下半
- [ ] 6.1 build（subagent-driven + executing-plans + TDD 编排）
- [ ] 6.2 verify（两阶段审查 + verification）
- [ ] 6.3 archive（归档六步 + 知识沉淀）
## 7. 集成验收
- [ ] 7.1 校验脚本全绿
- [ ] 7.2 映射表逐条对照
- [ ] 7.3 openspec CLI 校验
## 8. dogfood 归档
- [ ] 8.1 知识沉淀（memory/kb/rules）
- [ ] 8.2 归档六步走完（含分支合并）
```

- [ ] **Step 5: 写 ai-kb 骨架文件**

`.claude/ai-kb/README.md`（全文照写）：

```markdown
# AI 知识库（ai-kb）

| 目录 | 用途 | 写入时机 |
|---|---|---|
| kb/ | 模块功能介绍、架构设计（overview.md 为系统总览） | Open 发现过时提示；Archive 必写 |
| memory/ | 踩坑记录、注意事项，按模块一文件，追加式 | 坑解决后即时写；Archive 归整 |
| rules/ | index.md 全局路由表：模块名 \| 代码路径 \| 别称 \| 关键词 | Archive 更新 |

## memory 条目格式
## YYYY-MM-DD · 来源变更 <变更名>
**坑**：<现象>
**解**：<解法与注意事项>
```

`.claude/ai-kb/kb/overview.md`（全文照写）：

```markdown
# 系统架构总览

（Open 阶段首次探索后填写；Archive 阶段保持同步）

## 组成
- CLAUDE.md — 工作流总纲
- .claude/skills/ — 13 技能（5 阶段 + 8 支撑）
- .claude/ai-kb/ — 本知识库
- openspec/ — 变更数据层（changes/plan/specs/archive）
- scripts/validate-workflow.sh — 结构校验
```

`.claude/ai-kb/rules/index.md`（全文照写）：

```markdown
# 模块路由表

| 模块名 | 代码路径 | 别称 | 关键词 |
|---|---|---|---|
| 工作流总纲 | CLAUDE.md | 宪法、总纲 | 五阶段、硬门禁 |
| 阶段技能 | .claude/skills/{open,design,build,verify,archive}/ | 编排器 | 四件套、计划书、归档 |
| 支撑技能 | .claude/skills/{tdd,subagent-driven,code-review,...}/ | 执行器 | TDD、审查、调试 |
| 知识库 | .claude/ai-kb/ | kb、记忆 | 踩坑、路由表 |
| 数据层 | openspec/ | 变更目录 | proposal、delta、archive |
```

- [ ] **Step 6: 写校验脚本（本计划的"测试套件"）**

`scripts/validate-workflow.sh`（全文照写）：

```bash
#!/usr/bin/env bash
# 结构不变量校验——工作流的"测试套件"。骨架项立即绿，技能项随任务推进转绿。
set -u
cd "$(dirname "$0")/.."
fail=0
check() { if eval "$2" >/dev/null 2>&1; then echo "✓ $1"; else echo "✗ $1"; fail=1; fi; }

for d in openspec/changes openspec/plan openspec/specs openspec/archive \
         .claude/skills .claude/ai-kb/kb .claude/ai-kb/memory .claude/ai-kb/rules; do
  check "目录存在: $d" "[ -d '$d' ]"
done

for s in open design build verify archive tdd subagent-driven code-review \
         systematic-debugging verification git-worktrees parallel-agents writing-skills; do
  f=".claude/skills/$s/SKILL.md"
  check "技能存在: $s" "[ -f '$f' ]"
  check "frontmatter: $s" "head -1 '$f' | grep -q '^---' && awk 'NR>1&&/^---/{exit} NR>1' '$f' | grep -q '^name:' && awk 'NR>1&&/^---/{exit} NR>1' '$f' | grep -q '^description:'"
done

check "CLAUDE.md 硬门禁" "grep -q '硬门禁' CLAUDE.md"
check "CLAUDE.md 8态" "grep -q '待确认规范' CLAUDE.md && grep -q '已归档' CLAUDE.md"
check "CLAUDE.md ai-kb" "grep -q 'ai-kb' CLAUDE.md"
check "rules/index.md" "[ -f .claude/ai-kb/rules/index.md ]"
check "kb/overview.md" "[ -f .claude/ai-kb/kb/overview.md ]"
check "tdd 红绿重构" "grep -q '红' .claude/skills/tdd/SKILL.md && grep -q '绿' .claude/skills/tdd/SKILL.md && grep -q '重构' .claude/skills/tdd/SKILL.md"
check "debugging 记 memory" "grep -q 'ai-kb/memory' .claude/skills/systematic-debugging/SKILL.md"
check "verify 两阶段审查" "grep -q '规格符合性' .claude/skills/verify/SKILL.md && grep -q '代码质量' .claude/skills/verify/SKILL.md"
check "archive 知识沉淀" "grep -q '知识沉淀' .claude/skills/archive/SKILL.md"
check "archive delta 合并" "grep -q 'ADDED' .claude/skills/archive/SKILL.md"
check "open 四件套" "grep -q 'proposal' .claude/skills/open/SKILL.md && grep -q 'tasks' .claude/skills/open/SKILL.md"

if command -v openspec >/dev/null 2>&1; then
  check "openspec list" "openspec list --json 2>/dev/null | grep -q init-workflow-system"
  check "openspec validate" "openspec validate init-workflow-system --type change --strict --no-interactive"
fi
exit $fail
```

- [ ] **Step 7: 运行脚本验证"部分红"（红）**

```bash
chmod +x scripts/validate-workflow.sh && ./scripts/validate-workflow.sh; echo "exit=$?"
```

Expected: 目录类与 ai-kb 类检查 ✓；13 个技能类检查 ✗（尚未创建）；`exit=1`。若骨架项也 ✗，修正后重跑。

- [ ] **Step 8: 提交**

```bash
git add -A && git commit -m "feat: openspec/ai-kb 骨架、变更四件套与结构校验脚本"
```

---

### Task 2: CLAUDE.md 总纲

**Files:**
- Create: `CLAUDE.md`

**Interfaces:**
- Consumes: Task 1 的 8 态字段、技能目录名（必须与 Task 3-6 创建的目录完全一致）
- Produces: 五阶段路由表——所有阶段技能的入口引用；硬门禁条款编号 G1-G4

- [ ] **Step 1: 编写 CLAUDE.md（全文照写）**

```markdown
# AI 编程助手 · 工作流总纲

本仓库自带零插件依赖的五阶段编程工作流。一切代码变更必须走：**Open → Design → Build → Verify → Archive**。

## 状态真源（新会话必读）

- 变更状态：`openspec/changes/<变更名>/proposal.md` 头部 `状态:` 字段
  取值：`草稿 → 待确认规范 → 设计中 → 待确认计划 → 构建中 → 待验证 → 待归档 → 已归档`
- 进度：`openspec/changes/<变更名>/tasks.md` 勾选率
- 开始任何工作前：读上述两文件 + `.claude/ai-kb/rules/index.md`，从断点阶段继续，不重做已完成阶段。

## 五阶段路由

| 用户意图 | 技能 | 关键产出 | 完成标志 |
|---|---|---|---|
| 提出新需求 / "开始做 X" | open | changes/<名>/ 四件套 | 状态→待确认规范 |
| "确认规范，出计划" | design | plan/<名>.md + feature 分支 | 状态→构建中 |
| "确认计划，开工" | build | 逐任务代码+测试，tasks 勾选 | 状态→待验证 |
| "构建完成，审查" | verify | 两阶段审查报告+修复 | 状态→待归档 |
| "审查通过，归档" | archive | 主 specs 合并、archive/、合并分支 | 状态→已归档 |

支撑技能按需自动加载：tdd、subagent-driven、code-review、systematic-debugging、verification、git-worktrees、parallel-agents、writing-skills。

## 硬门禁（绝对纪律，违反即返工）

- **G1** 四件套未经用户明确确认，不得写计划
- **G2** 计划书未经用户明确确认，不得写实现代码
- **G3** tasks 未全勾/测试未全绿/无命令输出证据，不得声称构建完成
- **G4** 两阶段审查未通过，不得归档

## ai-kb 知识库规则

- Open：先读 rules/index.md 路由到模块，再读相关 kb/ 与 memory/
- Build：派发子代理时附受影响模块的 memory 摘要
- 任何坑解决后：立即追加 `.claude/ai-kb/memory/<模块>.md`（格式见 .claude/ai-kb/README.md）
- Archive：知识沉淀为归档六步之一（memory/kb/rules 三写）

## 通用纪律

- 任何不确定：停下问用户，不猜
- 声称完成前：运行验证命令并展示输出（无证据不声称完成）
- 审查意见：先验证正确性再实施；有理的改，无理的据实说明
- 提交粒度：每任务至少一次 git commit
```

- [ ] **Step 2: 验证（绿）**

```bash
./scripts/validate-workflow.sh | grep -E 'CLAUDE.md'
```

Expected: 三项 CLAUDE.md 检查 ✓。

- [ ] **Step 3: 提交**

```bash
git add CLAUDE.md && git commit -m "feat: CLAUDE.md 工作流总纲（路由+硬门禁+8态+ai-kb 规则）"
```

---

### Task 3: 支撑技能·纪律组（5 个，原文迁移）

**Files:**
- Create: `.claude/skills/tdd/SKILL.md`
- Create: `.claude/skills/systematic-debugging/SKILL.md`
- Create: `.claude/skills/verification/SKILL.md`
- Create: `.claude/skills/git-worktrees/SKILL.md`
- Create: `.claude/skills/parallel-agents/SKILL.md`

**Interfaces:**
- Consumes: 源技能（superpowers 6.2.0，路径见全局约束）；ai-kb memory 格式（Task 1）
- Produces: 被 build/verify 阶段技能引用的技能名：`tdd`、`systematic-debugging`、`verification`、`git-worktrees`、`parallel-agents`

**迁移规则（本组五文件通用，逐文件执行）：**
1. Read 源文件全文
2. 逐节中文化：源文件每个 `##` 节必须在新文件有对应节；每条 EXTREMELY-IMPORTANT / HARD-GATE / 红线 / 检查清单项必须有对应中文条款（可合并措辞，不可删减语义）
3. frontmatter：`name:` = 目录名；`description:` = "用于…时"一句中文
4. 引用改写：`superpowers:xxx` → 本仓库技能名（无前缀）；`Skill 工具`调用名同步改
5. 自验：数源文件 `##` 节数 = 目标节数；对源中每条加粗/大写强调逐条核对

- [ ] **Step 1: 迁移 tdd**

源：`.../skills/test-driven-development/SKILL.md`。必须保留的硬规则（中文对应条款必须出现）：先写失败测试并运行确认失败才准实现；最小实现（不多写）；红→绿→重构循环；禁止"先实现后补测试"；测试行为而非实现细节；每轮循环一次只处理一个失败。

- [ ] **Step 2: 迁移 systematic-debugging（+项目增补）**

源：`.../skills/systematic-debugging/SKILL.md`。必须保留：四阶段根因法（重现→根因隔离→最小修复→验证）；禁止在未定位根因前改代码；假设-验证循环。**项目增补条款**（原文本写明）：每个坑定位解决后，立即按 `.claude/ai-kb/README.md` 格式追加 `.claude/ai-kb/memory/<模块>.md`，标注来源变更。

- [ ] **Step 3: 迁移 verification（原 verification-before-completion）**

源：`.../skills/verification-before-completion/SKILL.md`。必须保留：声称完成/修复/通过前必须运行验证命令并确认输出；"证据先于断言"；禁止把"应该能跑"当验证。

- [ ] **Step 4: 迁移 git-worktrees**

源：`.../skills/using-git-worktrees/SKILL.md`。必须保留：何时需要隔离（并行任务/保护主工作区）；native worktree 优先、`git worktree add` 兜底的创建与清理流程；退出时的保留/删除决策。

- [ ] **Step 5: 迁移 parallel-agents（原 dispatching-parallel-agents）**

源：`.../skills/dispatching-parallel-agents/SKILL.md`。必须保留：仅无共享状态、无顺序依赖的任务可并行；每个子代理提示自包含；结果汇合检查。

- [ ] **Step 6: 运行校验（渐绿）**

```bash
./scripts/validate-workflow.sh | grep -E 'tdd|systematic-debugging|verification|git-worktrees|parallel-agents'
```

Expected: 上述 5 技能的存在+frontmatter 检查 ✓，tdd 红绿重构 ✓，debugging 记 memory ✓。

- [ ] **Step 7: 提交**

```bash
git add .claude/skills/ && git commit -m "feat: 支撑技能·纪律组（tdd/debugging/verification/worktrees/parallel）"
```

---

### Task 4: 支撑技能·协作组（3 个）

**Files:**
- Create: `.claude/skills/subagent-driven/SKILL.md`
- Create: `.claude/skills/code-review/SKILL.md`
- Create: `.claude/skills/writing-skills/SKILL.md`

**Interfaces:**
- Consumes: 迁移规则同 Task 3（逐字适用）
- Produces: `subagent-driven`（build 技能的执行引擎）、`code-review`（verify 技能引用，含请求与接收两节）、`writing-skills`（修改技能文件时的纪律）

- [ ] **Step 1: 迁移 subagent-driven（原 subagent-driven-development）**

源：`.../skills/subagent-driven-development/SKILL.md`。必须保留：每任务一个全新子代理（不携带前文上下文）；派发提示自包含（单任务计划+精确文件+验收标准）；主会话逐任务审查产出，通过才勾选；不合格退回重做且说明原因；两阶段审查（规格符合性+代码质量）在全部任务完成后由独立子代理执行。

- [ ] **Step 2: 迁移 code-review（合并 requesting-code-review + receiving-code-review）**

源：两个文件。必须保留：请求侧——何时请求审查（任务完成/大特性/合并前）、给审查者的上下文清单、子代理审查的提示要素（对照规格逐条+找缺陷，输出 findings 列表）。接收侧——收到意见先逐条验证技术正确性，不表演性顺从；有理的改、无理的据实反驳；争议升级用户仲裁。两源文件合并为 `# 请求代码审查` 与 `# 接收代码审查` 两节。

- [ ] **Step 3: 迁移 writing-skills**

源：`.../skills/writing-skills/SKILL.md`。必须保留：SKILL.md 结构规范（frontmatter 的 name/description 写法、正文 <500 行）；写完必须实际测试技能触发；一键可读格式要求。

- [ ] **Step 4: 运行校验（渐绿）**

```bash
./scripts/validate-workflow.sh | grep -E 'subagent-driven|code-review|writing-skills'
```

Expected: 3 技能存在+frontmatter ✓。

- [ ] **Step 5: 提交**

```bash
git add .claude/skills/ && git commit -m "feat: 支撑技能·协作组（subagent-driven/code-review/writing-skills）"
```

---

### Task 5: 阶段技能·上半（open / design）

**Files:**
- Create: `.claude/skills/open/SKILL.md`
- Create: `.claude/skills/design/SKILL.md`

**Interfaces:**
- Consumes: Task 2 的 G1 门禁与 8 态；Task 1 的四件套格式（openspec/AGENTS.md）；迁移规则同 Task 3
- Produces: `open`（四件套产出流程）、`design`（计划书格式：文件路径/改动/验证命令/验收标准/依赖）

- [ ] **Step 1: 编写 open 技能**

合并三源：`.../skills/brainstorming/SKILL.md`（取"澄清问答"段）+ openspec explore/propose 的 artifact 格式（以 Task 1 的 AGENTS.md 约定为准）。流程七步必须完整：
1. 读 ai-kb（rules/index.md 路由 → 相关 kb + memory）
2. 探索代码库相关模块
3. 逐个澄清问题——**一次一问、多选优先**，禁一次多问（brainstorming 硬规则）
4. 需求过大则分解为多个变更（各自独立走五阶段）
5. 产出四件套（proposal/specs delta/design/tasks，格式见 openspec/AGENTS.md），状态置`草稿`→完成后`待确认规范`
6. 自审：占位符/矛盾/歧义/范围四查，内联修复
7. 请用户确认（G1 门禁话术：明确列出四件套路径）

- [ ] **Step 2: 编写 design 技能**

合并三源：`.../skills/brainstorming/SKILL.md`（取"查漏"视角：边界场景/错误处理/被漏需求）+ `.../skills/writing-plans/SKILL.md`（计划书结构全文移植：目标/架构/全局约束/任务分节/ bite-size 步骤/无占位符规则/自审三查/执行交接）。流程六步：
1. 前置检查：proposal 状态=待确认规范（否则拒绝，提示先走 open 确认）
2. 对照 spec delta 查漏，有缺口先补回 spec
3. 写 `openspec/plan/<变更名>.md`：每任务含**精确文件路径、改动说明、验证命令、验收标准、依赖关系**；步骤 bite-size；禁止 TBD/TODO/"稍后补充"
4. 计划自审：spec 覆盖/占位符扫描/接口一致性（类型与名称前后一致）
5. 请用户确认计划（G2 门禁）
6. 确认后：创建 `feature/<变更名>` 分支（需隔离时用 git-worktrees 技能），状态→`构建中`

- [ ] **Step 3: 运行校验（渐绿）**

```bash
./scripts/validate-workflow.sh | grep -E 'skills/open|skills/design|open 四件套'
```

Expected: open/design 存在+frontmatter ✓，open 四件套 ✓。

- [ ] **Step 4: 提交**

```bash
git add .claude/skills/ && git commit -m "feat: 阶段技能 open/design（brainstorming 拆分 + writing-plans 移植）"
```

---

### Task 6: 阶段技能·下半（build / verify / archive）

**Files:**
- Create: `.claude/skills/build/SKILL.md`
- Create: `.claude/skills/verify/SKILL.md`
- Create: `.claude/skills/archive/SKILL.md`

**Interfaces:**
- Consumes: Task 2 的 G3/G4 门禁；Task 3-4 全部支撑技能名；Task 1 的归档目录与状态字段
- Produces: `build`（默认子代理路径+直执降级路径）、`verify`（两阶段审查流程）、`archive`（归档六步算法）

- [ ] **Step 1: 编写 build 技能**

源：`.../skills/subagent-driven-development/SKILL.md` + `.../skills/executing-plans/SKILL.md`。流程：
1. 前置检查：状态=`构建中`（否则拒绝并指向正确阶段）；恢复断点（读 tasks.md 勾选）
2. 路径选择：默认逐任务派发子代理（subagent-driven 技能）；任务极小（单文件微改）或用户要求时主会话直执（executing-plans 纪律：逐任务-验证-勾选-提交）
3. 派发提示模板（必须写明三要素）：单任务计划全文 + 受影响模块 memory 摘要 + TDD 硬规则（引用 tdd 技能）
4. 每任务收尾：审查子代理 diff 与测试证据→勾选 tasks.md→git commit
5. 故障路径：测试红→systematic-debugging（坑即时记 memory）；子代理不合格→退回重做附原因
6. 独立任务用 parallel-agents 并行
7. 全勾+全绿+证据留存→状态→`待验证`

- [ ] **Step 2: 编写 verify 技能**

源：`.../skills/requesting-code-review/SKILL.md` + `.../skills/verification-before-completion/SKILL.md`。流程：
1. 前置检查：状态=`待验证`且 tasks 全勾
2. 派发**独立子代理**做阶段一·规格符合性审查：逐条对照 delta Requirement，输出"规格-代码偏差"清单
3. 派发独立子代理做阶段二·代码质量审查：正确性/安全/性能/可维护性缺陷清单
4. 意见处理（receiving 纪律，引用 code-review 技能）：逐条先验证；有理修复→回 Build 路径重走 TDD；无理据实反驳记录；争议升级用户
5. 复审循环直至两阶段零未决问题
6. 终验：运行完整验证命令（测试套件+`./scripts/validate-workflow.sh`+有 CLI 则 `openspec validate <变更名> --strict --no-interactive`），输出全部留存
7. 状态→`待归档`

- [ ] **Step 3: 编写 archive 技能**

源：openspec archive-change 语义 + `.../skills/finishing-a-development-branch/SKILL.md`。六步（顺序固定）：
1. 前置检查：状态=`待归档`
2. **delta 合并**：逐条把 `changes/<名>/specs/*/spec.md` 的 ADDED（追加）/MODIFIED（替换对应 Requirement）/REMOVED（删除）应用到 `openspec/specs/<能力>/spec.md`
3. **知识沉淀**：memory 归整本变更新坑；kb 同步功能/架构变化；rules 更新别称/关键词
4. **归档移动**：变更目录移入 `openspec/archive/<名>/`；计划书从 `openspec/plan/` **移入**归档目录（plan/ 只留活跃）；tasks 全勾终检+proposal 状态→`已归档`
5. **分支收尾**（finishing-a-development-branch 纪律）：feature 分支合回 main（--no-ff），删除分支与 worktree（如有）
6. **提交**：归档与代码一次 commit（`chore(archive): <变更名>`）

- [ ] **Step 4: 运行校验（渐绿）**

```bash
./scripts/validate-workflow.sh | grep -E 'build|verify|archive'
```

Expected: 3 技能 ✓；verify 两阶段审查 ✓；archive 知识沉淀与 delta 合并 ✓。

- [ ] **Step 5: 提交**

```bash
git add .claude/skills/ && git commit -m "feat: 阶段技能 build/verify/archive（执行编排+两阶段审查+归档六步）"
```

---

### Task 7: 集成验收

**Files:**
- Modify: 发现问题时的任何工作流文件

**Interfaces:**
- Consumes: 全部前序任务产物 + 设计文档第 6 节映射表
- Produces: 全绿校验报告 + 映射对照结论（归档材料）

- [ ] **Step 1: 校验脚本全绿**

```bash
./scripts/validate-workflow.sh; echo "exit=$?"
```

Expected: 全部 ✓，`exit=0`。有 ✗ 则修复对应文件后重跑（此步骤本身就是 verification 技能的实践）。

- [ ] **Step 2: 映射表逐条对照（无损验收）**

对照设计文档第 6 节两表逐行核对：14 个 superpowers 技能 + 4 类 openspec 能力，每行在新文件中有对应落点。方法：对每个源技能 Read 源文件，列出其全部硬规则/检查清单项，grep 目标技能确认逐条存在。发现语义丢失→补齐对应条款→重跑 Step 1。

- [ ] **Step 3: openspec CLI 兼容复核**

```bash
openspec list && openspec validate init-workflow-system --type change --strict --no-interactive
```

Expected: 变更可列出、校验通过（delta 格式合规）。报错则按提示修正 artifact 格式。

- [ ] **Step 4: 提交（如有修复）**

```bash
git add -A && git commit -m "fix: 集成验收修复（映射对照补齐）"
```

（无修复则跳过）

---

### Task 8: dogfood 归档（本变更收尾）

**Files:**
- Create: `.claude/ai-kb/memory/workflow-system.md`
- Modify: `.claude/ai-kb/kb/overview.md`、`.claude/ai-kb/rules/index.md`（如需）
- Move: `openspec/changes/init-workflow-system/` → `openspec/archive/init-workflow-system/`；`openspec/plan/init-workflow-system.md` → 归档目录

**Interfaces:**
- Consumes: archive 技能（Task 6）——本任务就是它的首次执行
- Produces: 干净的 main 分支（工作流 v1 落成）+ 首批真实 memory 记录

- [ ] **Step 1: 知识沉淀——写 memory（真实坑）**

`.claude/ai-kb/memory/workflow-system.md` 首条（全文照写，均为本次真实踩坑）：

```markdown
# workflow-system 踩坑与注意事项

## 2026-08-16 · 来源变更 init-workflow-system
**坑**：仓库目录属主为 root 时 git 报 "dubious ownership" 拒绝操作
**解**：git config --global --add safe.directory <仓库路径>；注意这是机器级配置，换机器要重配

## 2026-08-16 · 来源变更 init-workflow-system
**坑**：本机 git 版本旧，git init -b main 不被支持（exit 129）
**解**：git init 后用 git checkout -b main 兼容；写脚本时避免依赖新 git 特性
```

- [ ] **Step 2: delta 合并进主 specs**

把 `changes/init-workflow-system/specs/workflow-system/spec.md` 的 10 条 ADDED Requirement 追加到 `openspec/specs/workflow-system/spec.md`（去掉 "## ADDED Requirements" 包装层，作为主规范正文）。

- [ ] **Step 3: 归档移动**

```bash
mkdir -p openspec/archive && git mv openspec/changes/init-workflow-system openspec/archive/ \
  && git mv openspec/plan/init-workflow-system.md openspec/archive/init-workflow-system/plan.md
```

检查 `openspec/changes/` 为空、`openspec/plan/` 为空；tasks.md 全勾终检；proposal.md 状态→`已归档`。

- [ ] **Step 4: 分支合并**

```bash
git add -A && git commit -m "chore(archive): init-workflow-system 归档与知识沉淀" \
  && git checkout main && git merge --no-ff feature/init-workflow-system -m "merge: 工作流系统 v1（init-workflow-system）" \
  && git branch -d feature/init-workflow-system
```

- [ ] **Step 5: 终验（verification 纪律）**

```bash
./scripts/validate-workflow.sh && openspec list --specs && git log --oneline | head -5
```

Expected: 脚本 exit=0；specs 列表含 workflow-system；合并历史清晰。

---

## 计划自审结论

- **Spec 覆盖**：设计文档第 2 节（架构）→ Task 1-2；第 3 节（ai-kb）→ Task 1/3/8；第 4 节（状态机门禁）→ Task 2/5/6；第 5 节（五阶段）→ Task 5/6；第 6 节（映射表）→ Task 3-6 逐技能+Task 7 对照；第 7 节（错误处理）→ 各技能故障路径条款；第 8 节（验收）→ Task 7/8。无缺口。
- **占位符扫描**：技能迁移任务的"内容"以 源路径+迁移规则+必须保留条款+验收 grep 完整指定，无 TBD/TODO。
- **一致性**：技能目录名在 Task 1 脚本、Task 2 路由表、Task 3-6 文件清单三处一致（13 个）；8 态字段在 Task 1 AGENTS.md、Task 2 CLAUDE.md 两处一致。

## 后续跟进（计划外，自然发生）

- **真实冒烟演练**：下一次用户提需求即首次实战（各门禁天然需要用户参与）
- **断点续传实测**：任意会话中断后重进验证恢复
