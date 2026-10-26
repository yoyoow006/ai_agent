模板版本: 1
# 设计：选择性回流 LC 工作流改进

## 目标与约束

将来源通用能力回流双助手源仓，保留当前已完善的轻量路径、分层验证及安装契约。四件套确认前不修改工作流实现、不编写独立计划。

## 方案与替代方案

- 方案：按能力做语义移植；风险路由同步入口、阶段技能、规则、主规格、压力场景和校验器；工具以当前实现为基线增量扩展，最后同步安装资产清单及镜像。
- 替代方案及取舍：整树覆盖会带入业务登记、删除历史知识、破坏小任务豁免并遗漏 Claude；直接 cherry-pick 来源初始化/治理提交无法覆盖两仓不同资产边界，均不采用。
- 任务事件保持旧消费者兼容；task_id 为可选字段，阶段汇总仅统计定义明确的阶段事件，不重复累加总汇总，畸形记录不能导致假成功。
- finalize 必须验证 manifest 当前身份；记录身份、comparison base、finding 状态、未验证范围和残余风险，不替代 reviewer 结论或自动关闭 finding。写入受审范围后仍执行陈旧检测规则。
- 项目登记只生成显式输出目录内的草稿，不修改真实 registry、不扫描业务仓、不执行登记命令；库模块允许空应用，已有任一输出默认拒绝覆盖，显式 force 才允许覆盖。
- 本地分支保护规则使用通用名称与路径，保护用户修改；恢复默认分支和清理仍遵守授权边界。

## 边界与错误路径

不导入目标安装身份、业务事实和机器配置。旧事件无 task_id 可继续读取；输出失败不能伪造门禁通过。缺文件、无效 JSON、STALE、路径冲突和非法 proposal 字段必须可诊断。标准小任务终局证据继续区别于完整 manifest。既有活跃变更不迁移、不取消。

## 验证矩阵

| 场景 | 命令 | 预期 |
|---|---|---|
| 四件套 | `python3 scripts/new-openspec-change.py check openspec/changes/merge-lc-workflow-improvements` | 无占位符、结构通过 |
| 工具 | `python3 -B -m unittest discover -s .ai/tools/tests` | 项目登记、finalize、旧查询与 manifest 回归通过 |
| 事件与 wrapper | `python3 -B -m unittest scripts.tests.test_workflow_events scripts.tests.test_workflow_wrapper` | 兼容性、错误及传播通过 |
| required | `bash scripts/validate-workflow.sh --require-openspec` | 必需测试实际执行，无 FAIL 或必需 SKIP |
| OpenSpec | `openspec validate --all --strict --no-interactive` | 规格有效 |
| 安装 | `python3 -B -m unittest scripts.tests.test_install_ai_workflow scripts.tests.test_install_workflow` | 单助手、双助手分发一致 |
| 差异 | `git diff --check` | 无空白错误，完整 diff 无越界内容 |
