## REMOVED Requirements

### Requirement: 五阶段工作流
系统 SHALL 以 Open → Design → Build → Verify → Archive 五阶段组织代码变更，每阶段有独立技能与产出物。
#### Scenario: 新需求进入
- **WHEN** 用户提出开发需求
- **THEN** 助手进入 Open 阶段产出四件套（proposal/specs delta/design/tasks），等待用户确认

### Requirement: 硬门禁
系统 SHALL 在四个推进点强制门禁：Open→Design 需用户确认四件套；Design→Build 需用户确认计划书；Build→Verify 需 tasks 全勾+测试全绿+有证据；Verify→Archive 需两阶段审查通过。
#### Scenario: 未确认不得推进
- **WHEN** 四件套未获用户确认
- **THEN** 不得开始计划编写

### Requirement: 状态真源与断点续传
系统 SHALL 将变更状态存于 proposal.md 的 状态 字段（8 态）与 tasks.md 勾选率，新会话凭文件恢复现场。
#### Scenario: 会话中断恢复
- **WHEN** 新会话开始且存在活跃变更
- **THEN** 读取状态字段与勾选率，从断点阶段继续

### Requirement: 原生技能库
系统 SHALL 提供 13 个技能：open/design/build/verify/archive 五阶段技能 + tdd/subagent-driven/code-review/systematic-debugging/verification/git-worktrees/parallel-agents/writing-skills 支撑技能。
#### Scenario: 显式调用
- **WHEN** 用户输入 /build
- **THEN** 加载 build 技能并从 tasks.md 断点继续

### Requirement: ai-kb 知识库
系统 SHALL 维护 .claude/ai-kb/ 三层知识：kb（功能/架构）、memory（踩坑/注意事项，追加式）、rules（全局路由表）。Open 阶段先读后探索；Build 派发附 memory 摘要；坑解决后即时记 memory；Archive 阶段三写沉淀。
#### Scenario: 归档沉淀
- **WHEN** 变更通过验证进入归档
- **THEN** memory/kb/rules 依据本变更新知识完成更新

### Requirement: TDD 硬规则
Build 阶段 SHALL 遵循红-绿-重构：先写失败测试并运行确认失败，再最小实现，再重构；禁止先写实现。
#### Scenario: 实现前必须有失败测试
- **WHEN** 子代理开始实现某任务
- **THEN** 其首个产出是对应的失败测试与失败运行证据

### Requirement: 两阶段审查
Verify 阶段 SHALL 由独立子代理执行规格符合性审查与代码质量审查；审查意见先验证后实施，争议由用户仲裁。
#### Scenario: 规格偏差
- **WHEN** 阶段一发现代码与 delta 不符
- **THEN** 退回 Build 补齐后复审

### Requirement: 归档六步
Archive 阶段 SHALL 依次：合并 delta 进主 specs → 知识沉淀 → 变更目录与计划书移入 archive（含 tasks 全勾终检+状态改已归档）→ 分支收尾（用户选择：合并/PR/保留）→ git commit。
#### Scenario: 计划书归位
- **WHEN** 归档完成
- **THEN** openspec/plan/ 不再含该变更计划，计划书已移入 archive/（移动而非复制）

### Requirement: openspec CLI 兼容
目录格式 SHALL 兼容 openspec CLI：装有 CLI 的机器可通过 list/validate 校验；未安装时工作流完整可用。
#### Scenario: 无 CLI 环境
- **WHEN** 机器未装 openspec CLI
- **THEN** 五阶段流程仍可完整走通

### Requirement: 零插件依赖
全部能力 SHALL 由本仓库内纯文本文件承载，不引用任何插件市场技能名。
#### Scenario: 裸机复制
- **WHEN** 仓库被复制到无任何插件的新机器
- **THEN** 工作流全部功能可用
