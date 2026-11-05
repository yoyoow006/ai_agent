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

### Requirement: 巨型技能核心与附录分离

系统 SHALL 将 `systematic-debugging` 与 `writing-skills` 拆分为核心 ≤80 行与按需附录；决策链默认只读核心，触发条件命中时再加载附录.Double-check 索引、`.claude/skills/` 与 `.codex/skills/` 镜像 byte-identical。

#### Scenario: 主路径只读核心

- **WHEN** 新会话进入标准/严格主路径
- **THEN** 只加载两技能核心
- **AND** 未命中触发条件不读附录

#### Scenario: 附录按需加载

- **WHEN** 用户触发 debugging 或 writing-skills 触发条件
- **THEN** 加载对应附录
- **AND** 双树镜像校验保持通过

### Requirement: 内存轮转与路由索引瘦身

系统 SHALL 将 `.ai/memory/workflow.md` 轮转至最近 30 条分模块文件；`.ai/rules/index.md` 保留短别名与关键词，完整路由表放附录。新会话上下文 MUST <350 行且路由准确率不降。

#### Scenario: memory 轮转

- **WHEN** Archive 执行且 workflow.md 条目 >30
- **THEN** 超出部分按模块文件归档
- **AND** 主文件仅保留最近 30 条

#### Scenario: 索引瘦身

- **WHEN** 读取 index.md 进行路由
- **THEN** 只读短别名表
- **AND** 完整表在附录按需加载

### Requirement: 续传摘要命令一行输出

系统 SHALL 扩展 `new-openspec-change.py` 新增摘要子命令，输出状态、未勾任务数、基线 commit、规则指纹四元一行结果；未提供全量内容时 SHALL NOT 全读四件套。

#### Scenario: 摘要可独立解析

- **WHEN** 运行摘要命令于活跃变更目录
- **THEN** 输出一行含状态/计数/commit/指纹
- **AND** 不修改变更状态

### Requirement: 待验证变更收尾归档

系统 SHALL 在确认 `layered-validation-agent-gating-output-metrics` 的最终 manifest ID、comparison base、finding 状态已持久化后归档该变更，并精确清理 `.ai-local/reviews/<change>/` 子路径。

#### Scenario: 精确清理

- **WHEN** 归档证据已持久化
- **THEN** 仅删除对应子路径
- **AND** 不递归删除 `.ai-local` 或活跃 review
