# 工作流提速增量缓存上下文优化 规范

## Purpose

约束 `--standard` 层验证的指纹缓存复用、契约套件按工作流资产分类裁剪、共享 memory 轮转与变更续传摘要命令的行为边界：提速不改变门禁通过/失败、必需执行与证据契约，不确定情形一律全量执行。

## Requirements

### Requirement: 标准层增量缓存仅复用 PASS 结果

系统 SHALL 在 `--standard` 层复用与 `--fast` 相同的指纹缓存语义：cache key 包含检查命令、core 自身与声明输入内容指纹；实际执行 FAIL 或 SKIP 时删除该检查缓存；输入缺失时只实际执行不读写缓存；命中时在检查行内标注指纹来源且仍记 PASS。

#### Scenario: standard 暖跑命中

- **WHEN** 运行 `--standard` 且缓存指纹未变
- **THEN** 输出沿用标注并跳过实际执行
- **AND** 汇总 PASS/FAIL/SKIP 计数与冷跑一致

#### Scenario: FAIL 清缓存

- **WHEN** 某检查实际执行返回 FAIL
- **THEN** 该检查缓存被删除
- **AND** 输入回退后重新实际执行，不掩盖失败

#### Scenario: 输入缺失不命中

- **WHEN** 声明输入文件不存在
- **THEN** 不生成指纹且不命中缓存
- **AND** 实际执行检查并按真实结果汇总

### Requirement: 契约套件按工作流资产分类裁剪且不确定时全量

系统 SHALL 仅在调用方显式提供 `WORKFLOW_STANDARD_BASE` 且基线后（含未跟踪文件）无工作流资产变更时，裁剪 standard 层顶层契约套件；工作流资产 SHALL 覆盖 AGENTS.md、CLAUDE.md、README.md、.ai/、.claude/、.codex/、.github/、shared/、docs/、scripts/ 及源仓形态下的 openspec/。git 缺失、diff 失败、未跟踪工作流资产或层级升级为 required 时 SHALL 保持全量；裁剪决定 SHALL 可经 `--print-plan` 审计。

#### Scenario: 无工作流资产变更裁剪

- **WHEN** 显式基线后变更仅含非工作流资产（如安装目标内的业务 openspec 数据）
- **THEN** 跳过顶层契约套件并输出裁剪原因
- **AND** core 层检查仍全量执行

#### Scenario: 工作流资产或不确定时全量

- **WHEN** 基线后存在工作流资产变更、未跟踪工作流资产、git 不可用、diff 失败或层级升级
- **THEN** 顶层契约套件全量执行
- **AND** `--print-plan` 输出对应原因

### Requirement: 内存轮转控制上下文规模

系统 SHALL 将 `.ai/memory/workflow.md` 单模块条目限制为最近 30 条，超出部分按时间顺序移入同目录 `<模块>-archive.md` 且不删改内容；主文件仅保留最近 30 条时新会话决策链上下文 MUST <350 行。

#### Scenario: memory 轮转

- **WHEN** Archive 执行且 workflow.md 条目 >30
- **THEN** 超出部分按模块归档文件保存
- **AND** 主文件仅保留最近 30 条

### Requirement: 续传摘要命令一行输出

系统 SHALL 扩展 `new-openspec-change.py` 新增摘要子命令，输出状态、未勾任务数、基线 commit、规则指纹四元一行结果；未提供全量内容时 SHALL NOT 全读四件套。

#### Scenario: 摘要可独立解析

- **WHEN** 运行摘要命令于活跃变更目录
- **THEN** 输出一行含状态/计数/commit/指纹
- **AND** 不修改变更状态
