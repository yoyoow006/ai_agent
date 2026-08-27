# 实现计划：add-cancel-state-ci-mirror

## 目标与上下文

- 四件套：`openspec/changes/add-cancel-state-ci-mirror/`（proposal/design/tasks 与两个 delta spec）。本计划是其严格模式独立实现计划。
- 三个交付：① `已取消`终态治理文本；② 校验器镜像清单 9→13 与状态合法组合扩展；③ GitHub Actions CI。全部为纯文档/流程文本/CI 配置/shell 校验器扩展，无运行时业务代码。
- 关键实证（已在 Design 阶段现跑验证，执行者可直接信赖）：
  - `openspec validate --all --strict` 不扫描 `openspec/archive/`；
  - `mirror_equal`（core 372-386 行）现有双侧归一化下 `verification`、`systematic-debugging`、`writing-skills` 已相等；`parallel-agents` 仅差 `> **Codex 执行环境` 注记行＋其后空行，删除该行并压缩空行后相等；
  - `scripts/lib/validate-workflow-core.sh` 与 assets 副本当前字节一致（`cmp` 通过）；
  - `scripts/tests/test_validate_workflow.py` 断言用 `PASS=\d+` 正则，不锁定检查条数，新增检查不破坏契约测试。

## 全局约束（逐字适用）

- 保护用户数据与未提交修改；外部或破坏性动作（推送、PR、强推、删除未合并工作）必须明确授权。
- 风险条件、状态、确认点、审查门禁必须在 `.claude` 与 `.codex` 保持语义一致；允许差异仅限工具映射和助手适配。
- `validate-workflow-core.sh` 实体副本与 assets 副本必须字节一致；其余 assets 文件按各自既有措辞（"本仓库/当前项目"）做语义等价同步。
- 验证纪律：纯文档/流程文本用内容契约、结构校验与 diff 校验；校验器 shell 扩展用"注入漂移必须失败"作为红—绿等价物（先证现状检测不到＝红，扩展后必须非零＝绿）。完成声明前现跑命令并读取退出码。
- 提交按可独立回滚的职责单元组织；不按 checklist 机械拆分。

## 任务 1：取消路径治理文本（13 个文件，一个职责单元）

### 1.1 实体 `openspec/AGENTS.md`

- 行 7 替换：
  - 旧：`  - \`状态:\`：草稿|待确认规范|设计中|待确认计划|构建中|待验证|待归档|已归档`
  - 新：`  - \`状态:\`：草稿|待确认规范|设计中|待确认计划|构建中|待验证|待归档|已归档|已取消`
- 行 8 替换并在其后新增一条 bullet：
  - 旧：`- 状态路径：标准从\`待确认计划\`开始；严格使用完整 8 态；快速模式不创建变更目录。`
  - 新：`- 状态路径：标准从\`待确认计划\`开始；严格使用完整 8 态前进路径；快速模式不创建变更目录。`
  - 新增：`- 取消：任一未归档状态可经用户明确决定转\`已取消\`；proposal 追加\`取消原因: <一句话>\`，目录移入 \`openspec/archive/\`，delta 不合并、不恢复；分支/worktree/未提交修改由用户明示处置。助手可建议、不得自行取消。`

### 1.2 实体 `CLAUDE.md`

- 「状态真源与技能」首条 bullet 之后新增：
  `- 任一未归档状态可经用户明确决定转\`已取消\`终态：proposal 记\`取消原因:\`并移入 \`openspec/archive/\`，不合并 delta、不恢复；助手可建议、不得自行取消。`
- 标准模式/严格模式节的状态前进链**不改**（`已取消`是异常终态，不入前进链）。

### 1.3 实体 `AGENTS.md`

- 「状态真源」节 `- 活跃变更：…` 条目之后新增与 1.2 相同语义的一条（Codex 措辞一致）。

### 1.4 实体 `.ai/kb/overview.md`

- 「风险模式与状态」节 `proposal 的\`模式:\`…双阶段审查。` 段落之后新增一句段：
  `\`已取消\`是用户明确决定的异常终态：目录移入 \`openspec/archive/\`、不合并 delta、不恢复；分支/worktree 处置由用户明示。`

### 1.5 实体 `.claude/skills/archive/SKILL.md` 与 `.codex/skills/archive/SKILL.md`（两侧插入相同内容）

- 插入点：开头前言段（以 `…任一 \`STALE\` 立即停止，不沿用旧结论。` 结尾）之后、`## 1. 合并 delta 到主规格` 之前，新增：

```markdown
## 取消路径（用户明确决定）

任一`已归档`前状态的变更可经用户明确决定取消；助手只能建议，不得自行置为`已取消`。

1. proposal 置`状态: 已取消`，追加一行`取消原因: <一句话>`。
2. 把 `openspec/changes/<变更名>/` 整体移入 `openspec/archive/`；delta 不合并进主规格，不执行本章其余流程（主规格合并、知识沉淀、归档后验证、分支整合）。
3. feature 分支、worktree 与未提交修改的去留由用户明确指示；删除未合并工作仍需独立授权。
4. 已取消变更只作历史记录：不恢复、不合并 delta；同类新需求按新变更目录重新进入。
```

### 1.6 实体 `.ai/rules/index.md`

- 行 5 关键词列末尾追加 `、取消路径`（路由词，不改正文其他内容）。

### 1.7 资产副本（与 1.1–1.5 语义等价同步）

- `scripts/ai-workflow-assets/claude/CLAUDE.md`、`codex/AGENTS.md`：按各自"当前项目"措辞加入与 1.2/1.3 相同位置的句子。
- `scripts/ai-workflow-assets/shared/openspec/AGENTS.md`：同步 1.1 的三处修改（该文件与实体版结构相同）。
- `scripts/ai-workflow-assets/shared/.ai/kb/overview.md`：同步 1.4。
- `scripts/ai-workflow-assets/claude/.claude/skills/archive/SKILL.md`、`codex/.codex/skills/archive/SKILL.md`：同步 1.5。
- 资产 `rules/index.md` 为通用骨架（无状态路径关键词行），**不改**。

### 1.8 任务 1 验证

```bash
bash scripts/validate-workflow.sh          # 预期 PASS=168 FAIL=0 SKIP=0（本任务只加文本，不动校验器）
git diff --stat                            # 预期恰好 13 个文件
```

提交：`feat(workflow): add user-decided cancel terminal state`

## 任务 2：校验器扩展（2 个文件，红—绿等价）

### 2.1 红：证明现状有盲区（注入后还原，不提交）

```bash
printf '\n漂移注入行\n' >> .claude/skills/verification/SKILL.md
bash scripts/validate-workflow.sh; echo "EXIT=$?"   # 预期 EXIT=0（漂移未被检出＝红）
git checkout -- .claude/skills/verification/SKILL.md # 还原
```

### 2.2 修改 `scripts/lib/validate-workflow-core.sh`（四处）

1. `mirror_equal`（372-386 行）：两侧 sed 各追加一条 `-e '/^> \*\*Codex 执行环境/d'`，输出改经 `cat -s` 压缩空行后落盘：
   - `sed -e … -e '/^> \*\*Codex 执行环境/d' ".codex/skills/$skill/SKILL.md" | cat -s >"$left"`（claude 侧同理）。
2. 镜像循环（约 504 行）：
   - 旧：`for skill in open design build verify archive tdd code-review subagent-driven git-worktrees; do`
   - 新：`for skill in open design build verify archive tdd code-review subagent-driven git-worktrees verification parallel-agents systematic-debugging writing-skills; do`
3. `proposal_ok` case（256-257 行）两行末尾各追加 `|标准:已取消`、`|严格:已取消`（在 `) return 0 ;;` 之前）。
4. 文档检查（453 行）：
   - 旧：`check "$doc 严格 8 态" contains_all "$doc" '草稿' '待确认规范' '设计中' '构建中' '待验证' '待归档' '已归档'`
   - 新：`check "$doc 严格 9 态" contains_all "$doc" '草稿' '待确认规范' '设计中' '构建中' '待验证' '待归档' '已归档' '已取消'`

### 2.3 同步资产副本（必须字节一致）

```bash
cp scripts/lib/validate-workflow-core.sh scripts/ai-workflow-assets/shared/scripts/lib/validate-workflow-core.sh
cmp scripts/lib/validate-workflow-core.sh scripts/ai-workflow-assets/shared/scripts/lib/validate-workflow-core.sh && echo SYNCED
```

### 2.4 绿：注入漂移必须被检出（三种注入逐一验证后还原）

```bash
printf '\n漂移注入行\n' >> .claude/skills/verification/SKILL.md
bash scripts/validate-workflow.sh; echo "EXIT=$?"   # 预期非零，输出含 FAIL: 双套语义镜像: verification
git checkout -- .claude/skills/verification/SKILL.md
# 同法对 .codex/skills/writing-skills/SKILL.md、.claude/skills/parallel-agents/SKILL.md 各注入一次，均须非零后还原
```

### 2.5 回归

```bash
bash scripts/validate-workflow.sh                    # 预期 PASS=172 FAIL=0 SKIP=0（168+4 镜像）
python3 -m unittest -v scripts.tests.test_validate_workflow   # 预期 OK，契约断言不破坏
```

说明：`标准:已取消|严格:已取消` 合法性的正向探针不可行（临时变更目录会触发 openspec --strict 失败），以 case 行评审核对＋既有非法组合 mutation 仍通过为证据；此为已接受的未验证范围，写入审查台账。

提交：`feat(validator): mirror all shared skills and accept cancelled state`

## 任务 3：CI workflow（1 个新文件）

### 3.1 创建 `.github/workflows/validate.yml`（内容如下，逐字）

```yaml
name: workflow-validation
on:
  push:
    branches: [main]
  pull_request:
  workflow_dispatch:

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: actions/setup-node@v4
        with:
          node-version: 22
      - name: Install OpenSpec CLI
        run: npm install -g @fission-ai/openspec@1.3.1
      - name: Validate workflow
        run: bash scripts/validate-workflow.sh --require-openspec
```

### 3.2 验证

```bash
python3 -c "import yaml,sys; yaml.safe_load(open('.github/workflows/validate.yml')); print('YAML OK')" \
  || npx --yes yaml-lint .github/workflows/validate.yml      # 预期输出 OK
bash scripts/validate-workflow.sh --require-openspec          # 预期全 PASS（CI 将运行的同一命令）
grep -c '\.github' scripts/ai-workflow-assets/manifest.json   # 预期 0（CI 不入安装资产）
```

CI 在 GitHub 上的实际首跑只能在推送后观察；推送属外部授权动作，届时单独请求，未观察前不声称 CI 生效。

提交：`ci: auto-run workflow validation on push and PR`

## 任务 4：Build 出口自证

```bash
openspec validate add-cancel-state-ci-mirror --strict --no-interactive   # 预期 valid
bash scripts/validate-workflow.sh --require-openspec                     # 预期全 PASS
python3 -m unittest discover -v -s .ai/tools/tests -p 'test_*.py'        # 预期全 OK
git diff --check && git status --short                                   # 预期无空白错误；仅预期内改动
```

全部通过后勾选 tasks、proposal 置`待验证`，交 Verify 双阶段独立审查（规格符合性 → 代码质量），不在 Build 内重复终审。

## Archive 阶段附加同步（收尾时执行，非 Build 任务）

- delta 合并进 `openspec/specs/risk-tiered-ai-workflow/spec.md`（ADDED 取消 Requirement 追加；MODIFIED 一致性 Requirement 整条替换）与 `openspec/specs/shared-ai-workflow-infrastructure/spec.md`（ADDED CI Requirement 追加）。
- `cp` 上述两个主规格到 `scripts/ai-workflow-assets/shared/openspec/specs/<能力>/spec.md`（资产副本与实体主规格字节一致）。
- 按 archive 技能完成 memory/kb 沉淀与归档后验证。

## 分支与 worktree（计划确认后、实现前的原子顺序）

1. 记录当前基线分支（main）；在当前工作区创建并切到 `feature/add-cancel-state-ci-mirror`。
2. 仅暂存本变更四件套＋本计划文件，proposal 置`状态: 构建中`，提交 `chore(openspec): add-cancel-state-ci-mirror four-piece set and plan`；不带任何其他未跟踪/修改文件。
3. 需要 worktree 隔离时：切回 main，用 git-worktrees 把已存在且未检出的 feature 分支挂到 `.worktrees/add-cancel-state-ci-mirror`（不得对已检出分支执行 `git worktree add`）。工作区干净且无并行实现时，经用户同意可留在 feature 分支就地实现。
4. 在最终实现工作区核对 `git branch --show-current`、`git status --short` 后，从任务 1 开始执行。

## 回滚

- 每任务一个提交：`git revert <commit>` 即可独立回滚文本、校验器或 CI。
- 校验器回滚后 assets 副本需同步回滚（同一提交内成对变更，revert 自动成对）。
