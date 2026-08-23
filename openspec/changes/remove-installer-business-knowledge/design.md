# 设计

## 初步方向

本文件是严格模式 Open 四件套的一部分，不是独立实施计划。第一次确认后需要产出 `openspec/plan/remove-installer-business-knowledge.md` 并再次确认。

清理策略是“保留通用框架，删除业务实例”：

- `.ai/kb/projects/README.md` 与空 registry 是通用能力，保留。
- 项目卡、契约和业务 memory 是目标项目数据，删除。
- overview/rules/tools 是 mixed 文档，只删除业务段落或替换示例，不削弱通用说明。
- 根 `.gitignore` 增加源仓库专用防回流规则，但安装器目标的 managed ignore 逻辑不变。

历史处理沿用无 remote 本地仓库的安全重建方式：清理当前树并验证后，用最终 tree 创建新的 root commit，替换 `main`，删除临时 feature 引用，expire reflog 并 prune。旧业务知识对象不再 reachable。

## 风险与边界

- 用户已选择不另存；历史重建后指定业务知识无法从本仓库恢复。
- 只扫描和处理本次列明的业务路径与 mixed 段落，不做无边界的内容审查。
- 不修改 `scripts/ai-workflow-assets/`，避免影响安装器分发内容。
- 不把清理过程产生的本地 manifest 或临时清单入库。

## 待 Design 细化

- 精确文件删除清单与 mixed 段落修改文本。
- root `.gitignore` 的防回流规则与 negation 顺序。
- 安装器相关测试范围与严格工作流验证矩阵。
- 历史 root 重建、对象修剪和 reachable 树扫描命令。
