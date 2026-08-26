# Codex 工作流目标安装规范

## Purpose

约束把共享 AI 工作流安装到外部 Codex 目标目录时的真实路径解析、入口冲突保护、非 Git 根验证和嵌套业务仓库边界，确保安装可审计、可重复且不吞掉用户既有内容。

## Requirements

### Requirement: Codex 工作流必须安装到无符号链接的真实目标

系统 SHALL 将用户给出的目标路径解析为真实路径，并在安装前确认目标路径及任一组件不是符号链接；目标必须是已存在目录。系统 SHALL 使用既有离线安装器安装共享核心与 Codex 单侧适配，不得安装 Claude 适配。

#### Scenario: 用户路径包含符号链接

- **WHEN** 用户提供 `/home/shitou/workspace/src/yuxiaor_prj_2025`
- **AND** `/home/shitou/workspace/src` 是指向 `/media/shitou/石头/wksource` 的符号链接
- **THEN** 系统使用真实目标 `/media/shitou/石头/wksource/yuxiaor_prj_2025`
- **AND** 不把含符号链接的路径传给安装器执行写入

#### Scenario: 仅安装 Codex 适配

- **WHEN** 安装器以 `--assistant codex` 执行
- **THEN** 目标获得共享 `.ai` 核心、空白 OpenSpec 基线、校验入口和 `.codex` 适配
- **AND** 目标不获得 `.claude` 适配，现有 `CLAUDE.md` 不被安装器修改

### Requirement: 冲突入口必须先保留再替换

当目标 `AGENTS.md` 与安装清单内容不同时，系统 SHALL 在调用安装器前将其重命名为明确的备份路径，并验证备份内容与重命名前一致；系统 SHALL NOT 覆盖、合并或丢弃旧入口内容。

#### Scenario: 目标已有差异 AGENTS.md

- **WHEN** 目标 `AGENTS.md` SHA-256 为 `74d7b6cd7d755cb07b04f205e5b6beef9ca7c7412379c2bbd9db166f1bac47cc`
- **THEN** 系统先将其重命名为 `AGENTS.pre-codex-workflow.md`
- **AND** 备份 SHA-256 保持不变
- **AND** 新 `AGENTS.md` 只能由安装器从显式清单创建

### Requirement: 安装必须可验证且不触及嵌套业务仓库

系统 SHALL 在写入前后运行与安装契约相称的预览、事务和验证；成功标准 SHALL 包含目标工作流校验全部通过、OpenSpec 严格校验通过，以及旧入口备份内容不变。系统 SHALL NOT 修改目标下任何嵌套业务仓库、执行联网、安装依赖或创建 Git 提交。

#### Scenario: 安装后验证

- **WHEN** Codex 工作流安装完成
- **THEN** 在目标根目录运行 `bash scripts/validate-workflow.sh --require-openspec` 且无 `FAIL`
- **AND** 在目标根目录运行 `openspec validate --all --strict --no-interactive` 并通过
- **AND** 备份 `AGENTS.pre-codex-workflow.md` 的 SHA-256 仍为 `74d7b6cd7d755cb07b04f205e5b6beef9ca7c7412379c2bbd9db166f1bac47cc`

#### Scenario: 目标根不是 Git 仓库

- **WHEN** 目标根包含工作流 `.gitignore` 但本身没有 `.git`
- **AND** 用户要求不初始化 Git 仓库
- **THEN** 目标 required 校验用目标 `.gitignore` 判定 Python 缓存与 SDD 路径是否忽略
- **AND** 校验过程不在目标根创建 `.git` 或修改嵌套业务仓库
