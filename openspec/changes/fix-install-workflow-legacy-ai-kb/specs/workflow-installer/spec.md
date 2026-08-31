# workflow-installer 规范（delta）

## MODIFIED Requirements

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

### Requirement: 目标项目初始化适配

安装脚本 SHALL 为目标项目写入通用占位版 `openspec/project.md`（提示用户填写本项目上下文，措辞与当前风险分级工作流和 `.ai/` 知识层一致）；`.ai/memory/` 为空骨架（已有内容只补缺不覆盖）；其余资产（CLAUDE.md、AGENTS.md、技能、`.ai/rules/` 路由表、`.ai/kb/` 总览、校验套件）原样安装。

#### Scenario: 通用化内容

- **WHEN** 安装完成
- **THEN** 目标 project.md 含项目上下文占位提示而非本仓库特定描述，`.ai/memory/` 为空骨架

#### Scenario: 目标已有业务 memory

- **WHEN** 目标项目 `.ai/memory/` 下已有用户写入的踩坑记录文件
- **THEN** 安装不覆盖、不备份、不删除该文件，仅补缺缺失的骨架文件
