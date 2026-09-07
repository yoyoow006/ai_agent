# AI 编程助手（精简版工作流）

一套精简的 AI 编程工作流配置，同时供 Claude Code 和 Codex 使用。核心思路：

- **单一事实源**：所有流程规则只维护 `.ai/workflow.md` 一份，`CLAUDE.md` / `AGENTS.md` 只是指向它的薄入口。
- **skill 单源分发**：skill 内容只维护 `.ai/skills/`，由 `scripts/sync.sh` 同步到 `.claude/skills/` 和 `.codex/skills/`。
- **按风险分级**：任务开始前先选模式（快速/标准/严格），流程随风险走，不搞一刀切重流程。

## 项目结构

```
├── CLAUDE.md              # Claude Code 入口（薄，指向 .ai/workflow.md）
├── AGENTS.md              # Codex 入口（薄，同上）
├── .ai/
│   ├── workflow.md        # 工作流规则 · 单一事实源（改规则只改这里）
│   ├── skills/            # skill 源文件（4 个，见下文）
│   └── memory/            # 踩坑与领域知识记录，按模块分文件
├── scripts/
│   └── sync.sh            # 把 .ai/skills/ 同步到 .claude/skills/ 和 .codex/skills/
├── .claude/skills/        # 生成物，勿手改
├── .codex/skills/         # 生成物，勿手改
└── changes/               # 变更文档（标准及以上变更时创建，完成后归档到 changes/archive/）
```

## 安装

### 前置要求

- bash（运行 `sync.sh`）
- 目标项目中使用 Claude Code 和/或 Codex

### 安装到你的项目

1. 把以下内容复制到目标项目根目录：

   ```bash
   CLAUDE.md AGENTS.md .ai/ scripts/
   ```

2. 运行同步脚本，生成分发副本：

   ```bash
   bash scripts/sync.sh
   ```

   输出类似 `synced: build code-review systematic-debugging verify` 即成功。

3. 把这些文件提交进目标仓库。AI 工具在项目内启动时会自动读取 `CLAUDE.md` / `AGENTS.md`，进而加载工作流。

说明：

- 只用其中一个工具也可以，`sync.sh` 生成的两份副本留着无害；想裁掉，改 `sync.sh` 里的 `for target in ...` 列表即可。
- `changes/` 目录按需创建，不需要预先建立。

### 验证安装

```bash
ls .claude/skills .codex/skills   # 各应看到 4 个 skill 目录
```

在项目里启动 Claude Code（或 Codex），让它复述当前工作流的风险分级规则，能正确引用 `.ai/workflow.md` 即生效。

## 使用

### 1. 开始任务：先分级

每个任务开始前，按风险选模式并向用户简短说明：

| 模式 | 适用 | 流程 |
|---|---|---|
| 快速 | 文档、注释、格式化等不影响运行时行为的修改 | 核对事实 → 直接改 → 针对性验证 |
| 标准 | 一般运行时代码变更 | 计划确认 → 实现 → 验证 → 完成 |
| 严格 | 认证/账务/删除迁移/Schema/并发/跨服务契约/破坏性操作 | 计划+设计确认 → worktree 隔离 → TDD → 双向验证 → 完成 |

不确定风险时按更高一级处理。

### 2. 标准及以上：写变更文档

在 `changes/<名称>.md` 建一个文档，字段：`模式` / `状态` / `目标`（3-5 句）/ `设计要点`（仅严格必填）/ `任务清单`（checkbox）。

状态流转：`待确认 → 进行中 → 待验证 → 完成`。**未获用户明确确认，不得从"待确认"进入实现。** 完成后移入 `changes/archive/`。

快速模式不建分支、不建变更文档。

### 3. Skills（4 个，按需加载）

| Skill | 触发条件 |
|---|---|
| `build` | 变更文档状态为"待确认"且已获用户实施确认，开始实现 |
| `verify` | 变更文档状态为"待验证"，做综合验证和收尾 |
| `code-review` | 审查 diff 或他人/其他会话产出的代码 |
| `systematic-debugging` | 测试失败、行为异常、需要定位根因；禁止未定位根因就改代码 |

典型一次标准变更的 skill 链路：确认变更文档 → `build`（TDD 实现）→ 测试失败时 `systematic-debugging` → `verify`（收尾归档）；需要时中途插 `code-review`。

### 4. Memory（踩坑记录）

遇到新坑立即写 `.ai/memory/<模块>.md`，格式：现象 → 根因 → 正确做法。开始相关任务前先读对应模块文件。定期合并重复、删除过时条目。

## 维护

- **改流程规则**：只改 `.ai/workflow.md`，不要改 `CLAUDE.md` / `AGENTS.md` 入口副本。
- **改/加 skill**：只改 `.ai/skills/`，改完跑 `bash scripts/sync.sh`；不要手改 `.claude/skills/` 和 `.codex/skills/`。
- 新增 skill 只要在 `.ai/skills/<名称>/` 放 `SKILL.md`（含 name/description frontmatter），再跑一次 `sync.sh`。
