模板版本: 1
# 构建任务清单

- [x] 1. 确认 comparison.md 的采用/排除清单与风险路由政策，随后按 design 技能编写独立计划。
- [x] 2. 同步双助手入口、阶段技能、review/archive/Git 规则及知识路由，保留标准小任务豁免与验证入口。
- [x] 3. 用 TDD 增加 task_id/phase 汇总、review finalize、proposal 预检和通用项目登记工具，覆盖失败路径。
- [x] 4. 同步治理规格、压力场景、校验器与契约测试，验证五类风险路由及旧保障不回退。
- [x] 5. 同步 scripts/ai-workflow-assets 下双助手和共享资产、清单，执行单/双助手安装回归；初次失败及精确复验见 verification.md。
- [x] 6. 按门禁不变量完成任务级审查及最小修复差异复审，记录 findings 和证据。
- [x] 7. 准备自身 delta、知识沉淀与本地整合策略，不触碰已有待验证变更。

规范阶段的第 6、7 项包含后续 Verify/Archive 生命周期动作；此处将构建验收与阶段收尾分开记录，避免提前勾选尚未执行的归档。范围不变。

后续阶段：Verify 双阶段独立审查与主会话完整终验待执行；Archive 的规格合并、归档移动、本地合回 main 与复验待执行。以 proposal 状态和 verification.md 记录实际完成结果。

验证命令与预期见 design.md 验证矩阵；预期结果：所有目标契约、required、OpenSpec strict、安装回归通过且无未决 Critical/Important。确认后独立计划细化文件与执行顺序。

## 本地整合策略

- 分支/worktree：确认后创建隔离 feature/merge-lc-workflow-improvements；主仓元数据只读时采用可写隔离克隆，不绕过挂载限制。
- 提交边界：按风险路由、通用工具、安装传播等可回滚职责组织；验证审查后本地合回 main，不能整合则交付补丁及准确状态。
- 外部副作用授权：本方案仅请求本地实现和整合，不含 push、PR、发布、删除用户工作或来源项目修改。
- 手工测试编译输出：无手工编译；测试临时产物使用临时目录或 .ai-local。
