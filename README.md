# AI 编程助手 · 风险分级工作流

零第三方插件依赖的 AI 编程工作流模板仓库：把 **OpenSpec**（规范驱动变更）与 **Superpowers**（计划书、子代理驱动、TDD、代码审查）的方法论无损内联为原生资产，**Claude Code 与 Codex 双运行时可用**，变更数据层（`openspec/`）与知识层（`.ai/`）两套共享、不分叉。

任何变更先按风险分类，再选择与风险相称的流程：改文档不走过场，动认证必走全部门禁。

## 核心特性

- **三级风险分流**：快速 / 标准 / 严格三档，流程成本与风险相称；未知风险至少升级到标准，严格任务不得降级
- **单一状态真源**：`openspec/changes/<变更名>/proposal.md` 的`状态:`字段是唯一断点真源，新会话可从任意断点续传，不依赖对话历史
- **按风险分层的确认与门禁**：标准模式仅一次实施前确认；严格模式保留 G1–G4 四道硬门禁（四件套未确认不写计划、计划未确认不写代码、测试不全绿不交棒、两阶段审查未过不归档）
- **13 个原生技能**：5 个阶段编排器 + 8 个支撑技能（TDD、代码审查、系统化调试、完成前验证、worktree、并行代理、子代理驱动、技能写作），无需安装任何插件
- **共享审查契约**：manifest 冻结 + STALE 双检杜绝"审旧代码报新结论"，finding 台账固定字段，最小修复沿用授权
- **`.ai/` 共享知识层**：kb（架构）/ memory（踩坑）/ rules（路由与审查契约）/ prompts（角色契约）/ tools（事实工具），双运行时共用，坑即时记录、归档时三写沉淀
- **双运行时镜像校验**：Claude 与 Codex 技能字节级镜像比对，流程语义分叉即校验失败；旧版"一刀切重流程"的回归同样会被拦截
- **一键安装器**：把整套工作流装进任意目标项目，装后自检全绿才退出；升级走台账驱动事务路径，失败自动回滚

## 工作流总览

```text
                ┌─ 快速：探索事实 → 直接修改 → 针对性验证 → 汇报
用户提需求 ──▶ 分类 ─┼─ 标准：Open 四件套 → 一次确认 → Build → 综合 Verify → Archive
                └─ 严格：Open → 确认 → Design → 确认 → Build(TDD) → Verify(双阶段) → Archive
```

| 模式 | 条件 | 路径 | 确认 |
|---|---|---|---|
| **快速** | 只维护已有事实的 Markdown、纯文本、注释或机械格式，不影响运行时、API/Schema、配置语义、安全合规、工作流治理或发布 | 探索事实 → 直接修改 → 针对性验证 → 汇报 | 0 |
| **标准** | 低到中风险运行时代码变更 | Open 一次产出可执行四件套 → 一次确认 → Build → 综合 Verify → Archive | 1 |
| **严格** | 权限认证、资金账务、删除/迁移、数据库 Schema、并发一致性、跨服务或公开运行时契约、工作流治理、破坏性操作、大范围重构 | Open → Design → Build → Verify → Archive 完整门禁 | 2 |

- 标准状态：`待确认计划 → 构建中 → 待验证 → 待归档 → 已归档`（不创建独立 `openspec/plan`）
- 严格状态：`草稿 → 待确认规范 → 设计中 → 待确认计划 → 构建中 → 待验证 → 待归档 → 已归档`
- 任一未归档变更可经用户明确决定进入`已取消`终态（助手只能建议）；已取消的 delta 不合并、不复活

完整介绍与使用指南见 **[docs/ai-workflow-intro.md](docs/ai-workflow-intro.md)**。

## 快速开始

### 方式一：直接使用本仓库

```bash
git clone <本仓库地址> && cd ai_agent
```

- **Claude Code**：自动读取 `CLAUDE.md` 总纲，按风险路由进入 `.claude/skills/`
- **Codex**：自动读取 `AGENTS.md` 总纲，按风险路由进入 `.codex/skills/`；工具映射见 `.codex/README.md`

### 方式二：安装到已有项目

```bash
bash scripts/install-workflow.sh /path/to/your-project         # 首次安装
bash scripts/install-workflow.sh /path/to/your-project --force # 覆盖升级（旧资产备份为 *.bak；memory 永不覆盖）
bash scripts/install-ai-workflow.sh --help                      # 便携安装器（--upgrade 台账驱动升级）
```

装完自检全绿后，填写目标项目 `openspec/project.md` 的项目上下文，重启 AI 会话即可使用。

## 目录结构

```text
├── CLAUDE.md / AGENTS.md   # 双运行时工作流总纲（各自助手自动读取）
├── .claude/                # Claude 运行时
│   ├── skills/             #   13 个技能（5 阶段 + 8 支撑）
│   └── agents/             #   explorer / reviewer / test-worker 角色适配
├── .codex/                 # Codex 运行时
│   ├── skills/             #   13 个技能（与 .claude 镜像，含 Codex 适配注记）
│   ├── agents/             #   角色适配
│   └── README.md           #   Claude→Codex 工具映射与派发契约
├── .ai/                    # 共享知识层（唯一正文来源，双运行时共用）
│   ├── kb/                 #   架构事实、项目卡与 registry
│   ├── memory/             #   踩坑记录（按模块一文件，追加式）
│   ├── rules/              #   路由表 index.md 与审查契约 review.md
│   ├── prompts/agents/     #   共享角色契约（explorer/reviewer/test-worker）
│   └── tools/              #   只读事实工具（project_facts、review_manifest）
├── openspec/               # 变更数据层（双运行时共享，不分叉）
│   ├── changes/            #   活跃变更（proposal / specs delta / design / tasks）
│   ├── plan/               #   严格模式独立计划书
│   ├── specs/              #   主规格（归档时 delta 合并于此）
│   └── archive/            #   已归档与已取消变更
├── scripts/
│   ├── install-workflow.sh    # 一键安装器（装后自检）
│   ├── install-ai-workflow.sh # 便携安装器（台账驱动 --upgrade）
│   ├── validate-workflow.sh   # 结构校验（镜像/门禁/分层）
│   └── hooks/                 # pre-push 秒级防护（自愿启用）
└── docs/                   # 参考文档（ai-workflow-intro.md 介绍与使用指南）
```

`.claude/ai-kb/`、`.codex/ai-kb/` 仅为兼容重定向入口，知识正文一律在 `.ai/`。

## 知识库规则

| 目录 | 用途 | 写入时机 |
|---|---|---|
| `.ai/kb/` | 模块功能介绍、架构设计、项目卡 | 权威事实变化并经核对后；Archive 必写 |
| `.ai/memory/` | 踩坑记录，按模块一文件，追加式 | 坑解决后即时写；Archive 归整 |
| `.ai/rules/` | 硬约束与路由表（`index.md`） | 路由或治理规则变化时 |

memory 条目格式（详见 `.ai/memory/README.md`）：

```markdown
## YYYY-MM-DD · 来源变更 <变更名>
**坑**：<可观察现象与根因>
**解**：<经过验证的解法与注意事项>
```

## 校验

```bash
bash scripts/validate-workflow.sh                    # 全量结构校验（默认）
bash scripts/validate-workflow.sh --fast             # 秒级 core 校验（标准模式 Verify 终验分层用）
bash scripts/validate-workflow.sh --require-openspec # 严格模式 / 治理资产变更全量门禁
openspec list                                        # 列出活跃变更（装有 openspec CLI 时）
openspec validate <变更名> --strict --no-interactive
```

分层规则：标准模式内容变更的 Verify 终验用 `--fast` 加目标/回归测试，归档后跑全量；严格模式及触及工作流入口、技能、校验器、安装资产的变更始终全量。

## 本地防护（自愿启用）

```bash
git config core.hooksPath scripts/hooks
```

启用后每次 `git push` 前自动运行秒级 core 结构校验，任一 FAIL 阻断推送——避免"本地合并破坏门禁后靠 CI 事后发现"（本仓库 2026-08-29 曾发生合并复活旧正文直推 main 的事故）。`validate-workflow.sh` 公共入口以 flock 串行化并发实例（钩子直接调用 core，不经过该锁）；`flock` 不可用时自动降级为无锁并提示。取消启用：`git config --unset core.hooksPath`。

## 写作约定（避坑）

- openspec 的 Requirement 正文必须含英文关键字 **SHALL** 或 **MUST**（纯中文"应"会被 CLI 判错），推荐"系统 SHALL …"中英混排
- archive 新建主规格时先写完整骨架（`# <能力> 规范` + `## Purpose` + `## Requirements`）再并入 delta；`openspec validate --all` 会校验主规格
- Python 项目初始化即写 `.gitignore`（`__pycache__/`、`*.pyc`），避免生成物误入提交

## 典型会话

```text
你：帮我补一段接口说明文档                    # → 快速：核对事实直接改，现跑校验后汇报
你：开始做一个用户导出 CSV 的功能             # → Open：分类+四件套，等你确认
你：确认计划，开工                            # → Build：逐任务实现，tasks 全勾+测试全绿
你：构建完成，审查                            # → Verify：综合审查（严格模式为双阶段）+ 终验证据
你：审查通过，归档                            # → Archive：并 specs、知识三写、归档、合并
你：继续 <变更名> / 取消这个变更              # → 断点续传 / 已取消终态（等你指示分支去留）
```

## License

仅供内部使用（按需自行添加开源协议）。
