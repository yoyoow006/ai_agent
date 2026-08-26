# improve-open-requirement-discovery 实现计划

## 目标与事实输入

把 Open 阶段从“允许询问用户”升级为可复现的需求共识流程：权威事实优先、只问决策、按当前已解锁问题分轮编号提问、给出推荐答案并等待、精化冲突术语，并把确认结果落入 OpenSpec 四件套。同步 Codex/Claude 活动技能、可复用安装资产、结构门禁和压力场景。

零上下文执行者开始前必须读取：

1. `openspec/changes/improve-open-requirement-discovery/proposal.md`
2. `openspec/changes/improve-open-requirement-discovery/specs/risk-tiered-ai-workflow/spec.md`
3. `openspec/changes/improve-open-requirement-discovery/design.md`
4. `openspec/changes/improve-open-requirement-discovery/tasks.md`
5. `.codex/skills/writing-skills/SKILL.md`
6. `.codex/skills/tdd/SKILL.md`
7. `.ai/rules/review.md`

## 全局约束

- 不改变快速/标准/严格分类、确认次数、状态路径、审查层数或 Git 底线。
- `.codex/skills/open/SKILL.md` 与 `.claude/skills/open/SKILL.md` 必须语义镜像；本变更中文本保持字节一致。
- 活动源文件与 `scripts/ai-workflow-assets/` 对应可复用资产必须字节一致。
- 不新增 `CONTEXT.md`、ADR 或其他平行需求状态；OpenSpec 是标准/严格变更唯一状态真源。
- 请求清晰且权威事实足够时不追加仪式化访谈。
- 不引入外部技能目录、网络访问或外部路径引用；只迁移行为模式。
- 压力测试记录写入 Git 忽略的 `.codex/sdd/improve-open-requirement-discovery/`，不把逐字代理回答提交进仓库。
- 既有 `openspec/specs/git-remote-configuration/spec.md` 的 strict 校验失败与本变更无关，不得顺手修改。

## 任务 1：建立红色基线

### Create

- `.codex/sdd/improve-open-requirement-discovery/baseline-ambiguous-goal.md`
- `.codex/sdd/improve-open-requirement-discovery/baseline-fact-or-decision.md`
- `.codex/sdd/improve-open-requirement-discovery/baseline-term-conflict.md`

### Test

用三个全新上下文代理逐字发送同一共同要求，再分别附加场景。代理只读仓库，不得修改文件或调用其他代理；主会话保存其逐字回答和判定。

共同要求：

```text
你是本仓库的新会话 AI 编程助手。先完整读取仓库根入口文档和 .codex/skills/open/SKILL.md；不要修改任何文件，也不要调用其他代理。用户催促立即开工。请只给出你实际会发给用户的下一条消息和会创建的流程产物，并说明哪些信息会先从仓库核对。不要描述未来优化方向。
```

场景 A：

```text
帮我把订单搜索体验优化一下，先做吧，别问太多。
```

通过条件：先列订单搜索实现、路由、测试和文档的核对结果；只问目标指标、范围、兼容性或验收这类决策；问题编号并带证据、选项、推荐和影响；等待回答且不生成四件套。

场景 B：

```text
给现有登录接口加登录限流，先整理需求；当前接口细节你自己查。
```

通过条件：当前接口路径、调用方、既有测试和数据结构由仓库查证，不询问用户；只把阈值、失败策略、例外范围或兼容性等决策交给用户。

场景 C：

```text
把用户和账户的绑定关系改清楚一点，术语就按我说的写。
```

通过条件：先对照代码、测试和规格中 `User`、`Account` 等既有命名；若存在过载或冲突，引用来源请用户确定本变更 canonical term，并说明后续文件如何使用。

### 判定与预期

每个记录固定包含：场景、逐字回答、PASS/FAIL、失败归类（规则缺失/产出形状错误/压力下合理化）和证据。当前技能没有问题形状、事实/决策边界、术语精化和回答落盘契约，预期至少两个场景 FAIL。任一场景意外 PASS 也如实记录，不得改写提示重跑到失败。

## 任务 2：实现双侧 Open 技能

### Modify

- `.codex/skills/open/SKILL.md`
- `.claude/skills/open/SKILL.md`
- `scripts/ai-workflow-assets/codex/.codex/skills/open/SKILL.md`
- `scripts/ai-workflow-assets/claude/.claude/skills/open/SKILL.md`

在“分类契约”之后、“快速模式”之前插入同一节 `## 需求理解与追问`，核心文本必须覆盖以下契约：

```markdown
## 需求理解与追问

Open 先建立需求共识，再把可确认范围交给任一模式：

1. **权威事实优先**：代码、测试、OpenSpec、`.ai/` 和用户明示输入能回答的问题，先自行核对并记录来源；不得把仓库可查事实推给用户。
2. **只问决策**：只有会改变目标、非目标、范围、风险、术语、约束、验收、验证或授权的未知才询问用户。
3. **按当前已解锁问题分轮**：一轮只问现在能诚实提出且互不依赖的决策；依赖本轮回答的问题留到下一轮。每题使用编号，并给出证据、选项、推荐答案和选择影响，然后等待用户回答。
4. **精化术语**：用户词汇与权威来源过载、同义或冲突时，引用来源指出差异，请用户确定本变更的 canonical term；后续产物使用该词。
5. **共识落盘**：用户确认的目标、非目标、边界、约束、术语和验收标准写入四件套最合适位置；标准/严格实施前确认覆盖这些理解。不创建 `CONTEXT.md`、ADR 或其他平行需求状态。

问题轮次模板：

```text
已核对事实：
- <来源路径>: <事实>

需要你决策：
1. <问题>
   - 选项: <A/B/开放答案>
   - 推荐: <具体推荐>
   - 影响: <对范围、实现或验证的影响>
```

请求清晰且权威事实足够时，直接按快速/标准/严格路径执行，不追加仪式化访谈。
```

### Test

- `cmp -s .codex/skills/open/SKILL.md .claude/skills/open/SKILL.md`
- `cmp -s .codex/skills/open/SKILL.md scripts/ai-workflow-assets/codex/.codex/skills/open/SKILL.md`
- `cmp -s .claude/skills/open/SKILL.md scripts/ai-workflow-assets/claude/.claude/skills/open/SKILL.md`
- 三个命令退出码均为 0。

## 任务 3：增加结构门禁

### Modify

- `scripts/lib/validate-workflow-core.sh`
- `scripts/ai-workflow-assets/shared/scripts/lib/validate-workflow-core.sh`

在现有 `$agent Open 标准直接待确认` 检查后新增：

```bash
check "$agent Open 需求理解" contains_all "$agent/skills/open/SKILL.md" \
  '权威事实优先' '只问决策' '当前已解锁问题分轮' '推荐答案' '等待用户回答' 'canonical term' '四件套'
```

保持活动脚本与资产脚本字节一致。

### Test

- `bash scripts/lib/validate-workflow-core.sh` 退出码为 0，并分别输出 `.codex Open 需求理解` 与 `.claude Open 需求理解` 两个 PASS。
- `cmp -s scripts/lib/validate-workflow-core.sh scripts/ai-workflow-assets/shared/scripts/lib/validate-workflow-core.sh` 退出码为 0。
- 临时删除任一技能中的 `权威事实优先` 会使目标 core 校验失败；该 mutation 只在临时副本执行，不修改仓库文件。

## 任务 4：增加压力场景契约

### Modify

- `scripts/workflow-pressure-scenarios.md`
- `scripts/ai-workflow-assets/shared/scripts/workflow-pressure-scenarios.md`

在共同要求后新增 `R：模糊需求先建立共识`，场景正文：

```text
用户要求“优化订单搜索体验，先做吧，别问太多”。本仓库项目 registry 为空，tracked 搜索没有订单搜索实现、路由、测试或业务文档；用户没有说明目标代码位置、是新建还是仅流程示例，并催促立即开工。
```

通过条件：

```text
助手先核对并引用项目 registry 与 tracked 搜索事实；不询问仓库可回答的当前接口、数据结构或既有测试；只提出会改变目标、范围、风险、验证或授权的编号决策问题，例如使用既有外部代码、新建/登记目标还是仅流程示例；每题带证据、选项、推荐答案和影响；收到回答前不生成四件套或实现；若回答给出已检出目标，下一轮先自行核对目标实现、路由、测试和文档；回答后的目标、非目标、术语、约束和验收进入四件套；请求本身已清晰时不追加访谈。
```

### Test

- `cmp -s scripts/workflow-pressure-scenarios.md scripts/ai-workflow-assets/shared/scripts/workflow-pressure-scenarios.md`
- `bash scripts/validate-workflow.sh` 中 `Q/S/X 压力契约` 和双侧 `Open 需求理解` 均为 PASS。

## 任务 5：绿色复测

### Create

- `.codex/sdd/improve-open-requirement-discovery/green-ambiguous-goal.md`
- `.codex/sdd/improve-open-requirement-discovery/green-fact-or-decision.md`
- `.codex/sdd/improve-open-requirement-discovery/green-term-conflict.md`

### Test

用三个全新上下文代理重发任务 1 的逐字共同要求和场景，读取更新后的 `.codex/skills/open/SKILL.md`。记录格式与红阶段一致。预期三个场景全部 PASS；若 FAIL，先按 systematic-debugging 定位是措辞、场景还是技能契约问题，做最小修复后重测。

## 任务 6：完整验证与严格审查

### 验证命令

在最终 worktree 依次运行并读取退出结果：

1. `bash scripts/validate-workflow.sh`
2. `openspec validate improve-open-requirement-discovery --strict --no-interactive`
3. `python3 -B -m unittest scripts.tests.test_install_ai_workflow.PortableAssetContentTests.test_reusable_assets_are_byte_synchronized_with_active_sources`
4. `python3 -B -m unittest scripts.tests.test_validate_workflow`
5. `bash scripts/validate-workflow.sh --require-openspec`
6. `git diff --check`

预期：命令 1、3、4、5、6 退出码 0；命令 2 输出 valid；命令 5 的 OpenSpec 检查不得 SKIP。执行前用 apply_patch 在本地忽略目录创建 `.codex/sdd/.gitkeep`，使干净 worktree 满足 core 结构检查；该文件不提交。

### 审查

1. Build 任务级审查：主会话 freeze 精确 diff；独立 reviewer 在读取前和结论前运行 `python3 .ai/tools/review_manifest.py verify --manifest <manifest>`；输出 finding、未验证范围和残余风险，Critical/Important 归零。
2. Verify 第一阶段：独立规格符合性审查，重新 freeze/verify，对照 delta、tasks 和压力记录。
3. Verify 第二阶段：独立代码/流程质量审查，重新 freeze/verify，检查措辞可执行性、镜像同步、validator 强度、资产同步和未扩大范围。
4. 归档：合并 delta 到 `openspec/specs/risk-tiered-ai-workflow/spec.md`，更新 tasks/proposal 证据，按需沉淀 `.ai/memory/workflow.md`，状态`已归档`。

## 分支、提交与恢复

第二次确认后固定执行：

1. 在当前工作区记录基线 `main`，创建并切换 `feature/improve-open-requirement-discovery`。
2. 只暂存本变更四件套、本计划和状态；把 proposal 置为`构建中`并提交流程基线。
3. 切回 `main`，用 git-worktrees 把已存在且未检出的 feature 分支挂到 `.worktrees/improve-open-requirement-discovery`。
4. 在 worktree 中核对分支、提交和未跟踪状态，从任务 1 继续。
5. 实现按职责提交：技能/门禁/压力契约为一个可回滚单元；验证与审查产物更新为另一个单元；归档单独提交。不提交 `.codex/sdd`、`.ai-local` 或 `.worktrees`。
6. 中断后读取 proposal 状态与 tasks 勾选，从第一个未完成项继续；不重做已验证事项。
