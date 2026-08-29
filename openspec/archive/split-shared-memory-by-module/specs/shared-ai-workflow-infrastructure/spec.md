## ADDED Requirements

### Requirement: 共享 memory 按模块文件维护

`.ai/memory/` SHALL 按知识模块分文件维护跨会话踩坑记录,条目格式与追加式维护规则不变;工作流治理与流程类条目 SHALL 位于 `workflow.md`,安装器契约类条目 SHALL 位于 `installer.md`,新增模块 SHALL 在出现首个条目时建同名模块文件。条目移动 SHALL NOT 改写正文;Archive 知识沉淀与日常"新坑立即写" SHALL 把条目写入对应模块文件。

#### Scenario: 安装器域新坑落盘

- **WHEN** 构建或审查发现属于便携安装器契约模块的新坑
- **THEN** 条目追加到 `.ai/memory/installer.md`,不写入 `workflow.md`
- **AND** 条目保持 `## 日期 · 来源变更` + 坑/解 固定格式

#### Scenario: 模块文件拆分保持逐字无损

- **WHEN** 维护者把既有条目在模块文件间移动
- **THEN** 每条正文(标题、坑、解)逐字不变
- **AND** 移动前后全部条目拼接比对无差异、总条目数不变

#### Scenario: 断点恢复读取模块 memory

- **WHEN** 助手按 `.ai/rules/index.md` 路由命中某模块并读取其踩坑记录
- **THEN** 对应模块文件存在且包含该模块历史条目
- **AND** 不要求读取与当前模块无关的 memory 文件
