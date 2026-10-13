# 设计：合并标准小任务轻量工作流

## 目标与约束

目标是把源分支 `feature/simplify-standard-task-workflow` 中已验证的治理语义移植到本仓库，同时保留本仓库已演进的分层验证、代理门控、输出协议、缓存和安装资产契约。约束是：只做本地 main 合并与复验；不修改源仓库；不复制业务项目知识；严格模式门禁不得降低。

## 方案与替代方案

- 方案：以本仓库当前文件为基准，逐语义移植源分支的四组能力：
  1. 标准小任务判定与 Verify/Archive 轻量路径；
  2. 条件知识沉淀与两提交粒度；
  3. 手工 Java 测试输出约束；
  4. OpenSpec 归档辅助脚本与 required 测试。
- 替代方案及取舍：
  - 直接 `git cherry-pick` 源分支两个提交：速度快，但两仓 OpenSpec 历史和校验器测试基线不同，极易带入业务仓路径、旧契约或无关冲突；不采用。
  - 只改根入口不改主规格和测试：实现最小，但会违反双运行时语义同步与 mutation 回归契约；不采用。
  - 完整重写归档器支持通用 OpenSpec delta 合并：长期更优，但超出本需求；本次采用保守追加并明确残余风险。

## 边界与错误路径

- 归档辅助脚本发现未勾选任务、状态非`待归档`、终局证据缺失或目标目录已存在时必须非零退出且不产生半归档状态。
- 本仓库已有 `--archive-light`/required 分类门禁，源分支的 Archive 规则合并到该现有模型，不复制旧的按模式固定选择逻辑。
- 手工 Java 编译规则只作为 Maven 不可用时的临时通道；生产编译门禁失败仍不得声明完成。
- 安装资产清单若新增脚本但不纳入复制清单，安装后语义会漂移；实现时必须同步 manifest 和安装器测试。

## 验证矩阵

| 场景 | 命令 | 预期 |
|---|---|---|
| 归档辅助脚本单测 | `python3 -B -m unittest -v scripts.tests.test_archive_openspec_change` | PASS，覆盖拒绝、dry-run、归档和重复目标 |
| 模板生成/预检 | `python3 -B -m unittest -v scripts.tests.test_openspec_templates` | PASS，新增默认字段和占位符拒绝有效 |
| 工作流契约 | `python3 -B -m unittest -v scripts.tests.test_validate_workflow` | PASS，覆盖小任务语义、镜像、安装资产和归档索引 |
| 严格变更门禁 | `bash scripts/validate-workflow.sh --require-openspec` | PASS，禁用缓存并执行 OpenSpec strict 与必需测试 |
| 合并复验 | 切回 main 后运行 `bash scripts/validate-workflow.sh --require-openspec` 与 `git diff --check` | 本地合并结果全绿 |
