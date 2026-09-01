# workflow-installer 规范

## Purpose

把本仓库验证过的风险分级工作流资产一键安装到任意目标项目的安装器能力：双运行时一键安装（资产树单一来源）、冲突防护、装后自检分层、零依赖可移植、目标项目初始化适配（含迁移前旧布局自愈）。

## Requirements

### Requirement: 一键安装
安装脚本 SHALL 以 `bash scripts/install-workflow.sh <目标路径>` 一条命令把全套工作流资产复制到目标项目。资产清单 SHALL 与当前仓库布局一致：CLAUDE.md、AGENTS.md、双运行时技能与角色适配、`.ai/` 通用共享层骨架（kb/rules/prompts/tools，其中 memory 只补缺永不覆盖）、`.claude/ai-kb/` 与 `.codex/ai-kb/` 兼容重定向入口、openspec 骨架（含通用占位版 project.md）以及校验脚本套件（`validate-workflow.sh` 及其 `lib/`、`tests/` 依赖）。资产源 SHALL 取自 `scripts/ai-workflow-assets/` 资产树（与便携安装器共用单一来源），脚本 SHALL NOT 手工枚举仓库活动树中可能随迁移消失的路径。
#### Scenario: 空目标项目安装
- **WHEN** 对一个不含任何工作流资产的目录执行安装
- **THEN** 全部资产落位且目录结构正确：`.ai/` 共享层、`.claude/` 与 `.codex/` 两侧技能、双总纲、openspec 骨架（含 .gitkeep 空目录占位）、`scripts/` 校验套件（含 lib 与 tests）、ai-kb 仅含重定向 README
- **AND** 脚本退出码为 0
#### Scenario: 目标路径无效
- **WHEN** 目标路径不存在或不是目录
- **THEN** 报错并以退出码 2 结束，不创建任何目录
#### Scenario: 无参数调用
- **WHEN** 不带参数或传 --help 调用脚本
- **THEN** 打印用法说明（含 --force 语义），退出码 2
#### Scenario: 布局迁移后安装不产生悬空引用
- **WHEN** 仓库布局再次迁移导致资产树中某路径消失或移动
- **THEN** 安装脚本因整体复制资产树而不引用任何不存在的源路径
- **AND** 空目标安装回归测试在源资产缺失或自检失败时返回失败

### Requirement: 冲突防护
安装脚本 SHALL 在复制前扫描目标路径的冲突文件；存在冲突时默认逐一列出并中止退出（非零退出码）；仅当传入 `--force` 时覆盖，且每个被覆盖文件先备份为 `<原名>.bak`。
#### Scenario: 已有 CLAUDE.md
- **WHEN** 目标项目已存在 CLAUDE.md 且未传 --force
- **THEN** 安装中止，输出冲突文件清单与 --force 用法提示
#### Scenario: 强制覆盖
- **WHEN** 传入 --force 且目标存在同名文件
- **THEN** 原文件备份为 <原名>.bak 后完成安装

### Requirement: 装后自检
安装脚本 SHALL 在复制完成后于目标路径运行 `./scripts/validate-workflow.sh --fast`（秒级 core 结构校验），全绿才算安装成功；有红项则报告并以非零退出码结束。完整契约套件与便携安装器套件 SHALL 保持为源仓 CI 职责（随包契约套件的目标模型为"单侧+profile"，双运行时目标内运行全量校验会有源仓专属用例不适用）。目标带有历史归档目录而缺少 `openspec/archive/README.md` 索引时，装后自检 SHALL 以精确的单一 `[FAIL] 归档索引与目录 1:1` 报告（不混入其他红项、不误报为安装损坏）；补齐索引行后复跑自检 SHALL 全绿。
#### Scenario: 安装完成即验证
- **WHEN** 资产复制完成
- **THEN** 目标项目 `./scripts/validate-workflow.sh --fast` 全绿（退出码 0），安装整体耗时为秒级
#### Scenario: 目标带历史归档缺索引
- **WHEN** 安装到 `openspec/archive/` 已有变更目录但从未建立 README 索引的目标
- **THEN** 装后自检报告恰好一个红项 `[FAIL] 归档索引与目录 1:1`，安装器以退出码 1 结束
- **AND** 在目标内补齐与目录 1:1 的索引行后复跑 `./scripts/validate-workflow.sh --fast` 全绿

### Requirement: 零依赖可移植
安装脚本 SHALL 仅依赖 bash 与 cp/mkdir 等基础工具，不依赖 openspec CLI、不使用新版 git/bash 特性，可在旧环境运行。
#### Scenario: 无 CLI 裸机安装
- **WHEN** 在未安装 openspec CLI 的机器上执行安装
- **THEN** 安装与装后自检完整成功

### Requirement: 目标项目初始化适配
安装脚本 SHALL 为目标项目写入通用占位版 `openspec/project.md`（提示用户填写本项目上下文，措辞与当前风险分级工作流和 `.ai/` 知识层一致）；`.ai/memory/` 为空骨架（已有内容只补缺不覆盖）；双运行时安装 SHALL NOT 生成 `.ai/assistant-profile.json`、SHALL NOT 随附便携安装器契约文件（`scripts/install-ai-workflow.sh`、`scripts/lib/install_ai_workflow.py` 是随包套件的源仓标记与源仓专属能力）；迁移前旧布局残留（`ai-kb/{kb,rules,memory}` 含正文的目录）SHALL 在无 `--force` 时明确中止并指引，有 `--force` 时整目录备份为 `ai-kb.bak/` 后重装重定向入口；其余资产（CLAUDE.md、AGENTS.md、技能、`.ai/rules/` 路由表、`.ai/kb/` 总览、校验套件）原样安装。
#### Scenario: 通用化内容
- **WHEN** 安装完成
- **THEN** 目标 project.md 含项目上下文占位提示而非本仓库特定描述，`.ai/memory/` 为空骨架，全新安装不产生 `.ai/assistant-profile.json` 也不含便携安装器文件
#### Scenario: 目标已有业务 memory
- **WHEN** 目标项目 `.ai/memory/` 下已有用户写入的踩坑记录文件
- **THEN** 安装不覆盖、不备份、不删除该文件，仅补缺缺失的骨架文件
#### Scenario: 迁移前旧布局残留
- **WHEN** 目标存在含正文的 `ai-kb/{kb,rules,memory}` 目录且未传 --force
- **THEN** 安装以非零退出码中止，输出旧布局指引，不改动用户文件
- **WHEN** 同一目标传入 --force
- **THEN** 各侧 ai-kb 整目录备份为 `ai-kb.bak/` 后重装重定向入口，装后自检通过
