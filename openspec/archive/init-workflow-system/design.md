# 设计：init-workflow-system

详细设计见已批准文档：docs/superpowers/specs/2026-08-16-ai-agent-workflow-design.md（本文件为索引）。

## 关键决策
1. 可复制模板仓库形态（资产纯文本随仓库走）
2. 保持 openspec CLI 兼容（零依赖但白赚校验）
3. 全中文
4. feature 分支流（worktree 可选）
5. 技能分层：5 编排 + 8 支撑
6. ai-kb 四读写点（Open 读 / Build 读 / 随时写 / Archive 写）
7. 迁移映射表 = 无损验收清单（设计文档第 6 节）
