模板版本: 1
# 工作流提速增量缓存上下文优化

## ADDED Requirements

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

### Requirement: 校验按变更分类增量裁剪且分类外全量

系统 SHALL 依据变更文件分类决定检查集合：文档变更跳过契约树复制；core 脚本变更跑对应单测子集；分类外任意变更全量执行 281 项。裁剪规则 MUST 可审计且命中全覆盖。

#### Scenario: 文档-only 变更裁剪

- **WHEN** 变更仅含 Markdown/纯文本且不命中工作流入口
- **THEN** 跳过契约树复制类检查
- **AND** 其余检查全量执行

#### Scenario: 分类外全量回退

- **WHEN** 变更文件未被任一裁剪规则覆盖
- **THEN** 全量执行全部检查
- **AND** 裁剪规则输出未匹配告警

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
