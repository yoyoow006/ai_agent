# AI 编程助手 · 五阶段工作流

零第三方插件依赖的 AI 编程工作流模板仓库：把 **OpenSpec**（规范驱动变更）与 **Superpowers**（计划书、子代理驱动、TDD、代码审查）的方法论无损内联为原生资产，**Claude Code 与 Codex 双运行时可用**，openspec 变更数据层两套共享、不分叉。

## 核心特性

- **五阶段状态机**：Open → Design → Build → Verify → Archive，proposal 头部 `状态:` 字段是唯一断点真源，新会话可从任意断点续传
- **四道硬门禁**：四件套未确认不写计划（G1）、计划未确认不写代码（G2）、测试不全绿不交棒（G3）、两阶段审查未过不归档（G4）
- **13 个原生技能**：5 阶段编排器 + 8 个支撑技能（TDD、子代理驱动、代码审查、系统化调试、完成前验证、worktree、并行代理、技能写作），无需安装任何插件
- **ai-kb 知识库**：kb（架构）/ memory（踩坑）/ rules（路由）三层，坑即时记录、归档时三写沉淀
- **一键安装器**：把整套工作流装进任意目标项目，装后自检全绿才退出

## 五阶段工作流

```text
用户提需求 ──▶ Open ──▶ 用户确认 ──▶ Design ──▶ 用户确认 ──▶ Build ──▶ Verify ──▶ Archive
              四件套      (G1)       计划书       (G2)      TDD 实现   两阶段审查   归档+合并
                                                                      (G3→G4)
```

| 阶段 | 用户说什么 | 产出 | 完成标志 |
|---|---|---|---|
| **Open** | "开始做 X" | `openspec/changes/<名>/` 四件套：proposal / specs delta / design / tasks | 状态→`待确认规范` |
| **Design** | "确认规范，出计划" | `openspec/plan/<名>.md` 计划书 + `feature/<名>` 分支 | 状态→`构建中` |
| **Build** | "确认计划，开工" | 逐任务 TDD 实现（红→绿→提交），tasks 勾选 | 状态→`待验证` |
| **Verify** | "构建完成，审查" | 规格符合性 + 代码质量两阶段独立审查 + 终验证据 | 状态→`待归档` |
| **Archive** | "审查通过，归档" | delta 并入主 specs、知识三写、目录归档、分支收尾 | 状态→`已归档` |

变更状态八态：`草稿 → 待确认规范 → 设计中 → 待确认计划 → 构建中 → 待验证 → 待归档 → 已归档`

## 快速开始

### 方式一：直接使用本仓库

```bash
git clone <本仓库地址> && cd ai_agent
```

- **Claude Code**：自动读取 `CLAUDE.md` 总纲，按五阶段路由进入 `.claude/skills/`
- **Codex**：自动读取 `AGENTS.md` 总纲，按五阶段路由进入 `.codex/skills/`；子代理用原生 `multi_agent_v1__spawn_agent`（`fork_context: false`），工具映射见 `.codex/README.md`

### 方式二：安装到已有项目

```bash
bash scripts/install-workflow.sh /path/to/your-project        # 首次安装
bash scripts/install-workflow.sh /path/to/your-project --force # 覆盖升级（旧资产备份为 *.bak；memory 永不覆盖）
```

装完自检全绿后，填写目标项目 `openspec/project.md` 的项目上下文，重启 AI 会话即可使用。

## 目录结构

```text
├── CLAUDE.md              # Claude 工作流总纲（Claude Code 自动读取）
├── AGENTS.md              # Codex 工作流总纲（Codex 自动读取）
├── .claude/               # Claude 运行时
│   ├── skills/            #   13 个技能（5 阶段 + 8 支撑）
│   └── ai-kb/             #   知识库（kb / memory / rules）
├── .codex/                # Codex 运行时
│   ├── README.md          #   Claude→Codex 工具映射与派发契约
│   ├── skills/            #   13 个技能（与 .claude 镜像，含 Codex 适配注记）
│   ├── ai-kb/             #   知识库（kb / memory / rules）
│   └── sdd/               #   子代理驱动开发草稿区（台账/简报/报告/审查包，git 忽略）
├── openspec/              # 变更数据层（两套工作流共享，不分叉）
│   ├── changes/           #   活跃变更（proposal / specs delta / design / tasks）
│   ├── plan/              #   活跃计划书
│   ├── specs/             #   主规格（归档时 delta 合并于此）
│   └── archive/           #   已归档变更（含 plan.md，状态=已归档）
├── scripts/
│   ├── install-workflow.sh   # 一键安装器（装后自检）
│   └── validate-workflow.sh  # 结构不变量校验（双运行时 98 项）
└── docs/                  # 设计参考文档
```

## ai-kb 知识库规则

| 目录 | 用途 | 写入时机 |
|---|---|---|
| `ai-kb/kb/` | 模块功能介绍、架构设计 | Open 发现过时提示；Archive 必写 |
| `ai-kb/memory/` | 踩坑记录，按模块一文件，追加式 | 坑解决后即时写；Archive 归整 |
| `ai-kb/rules/` | 全局路由表：模块名 \| 代码路径 \| 别称 \| 关键词 | Archive 更新 |

memory 条目格式：

```markdown
## YYYY-MM-DD · 来源变更 <变更名>
**坑**：<现象>
**解**：<解法与注意事项>
```

## 校验

```bash
bash scripts/validate-workflow.sh   # 结构校验：双运行时技能/知识库/总纲/openspec 全量检查
openspec list                       # 列出活跃变更（装有 openspec CLI 时）
openspec validate <变更名> --strict --no-interactive
```

## 写作约定（避坑）

- openspec 的 Requirement 正文必须含英文关键字 **SHALL** 或 **MUST**（纯中文"应"会被 CLI 判错），推荐"系统 SHALL …"中英混排
- archive 新建主规格时先写完整骨架（`# <能力> 规范` + `## Purpose` + `## Requirements`）再并入 delta；`openspec validate --all` 会校验主规格
- Python 项目初始化即写 `.gitignore`（`__pycache__/`、`*.pyc`），避免生成物误入提交

## 典型会话

```text
你：开始做一个用户导出 CSV 的功能          # → Open：产出四件套，等你确认
你：确认规范，出计划                       # → Design：计划书 + feature 分支，等你确认
你：确认计划，开工                         # → Build：逐任务 TDD，tasks 全勾+测试全绿
你：构建完成，审查                         # → Verify：两阶段独立审查 + 终验证据
你：审查通过，归档                         # → Archive：并 specs、沉知识、归档、合并
```

## License

仅供内部使用（按需自行添加开源协议）。
