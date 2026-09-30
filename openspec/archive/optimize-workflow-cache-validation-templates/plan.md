# 实施计划：工作流优化

## 目标与全局约束

将已确认的三项治理优化落到现有 Bash/Python 工作流校验器和 OpenSpec 入口：

1. 静态规则缓存内容寻址、可失效、可审计，required 门禁始终实际执行。
2. fast、standard、required 三层验证覆盖和升级条件明确，兼容现有 CLI。
3. OpenSpec 标准产物可以从统一模板生成并由预检拒绝不完整内容。

全局约束：不修改业务运行时/API/Schema/数据库，不联网、不推送、不发布，
不自动创建提交以外的外部副作用；缓存只存在 `.ai-local/rules-cache/`，不
进入版本库，不成为 OpenSpec 状态真源；所有校验输出继续使用 PASS/FAIL/SKIP，
不引入第四种顶层状态；保护工作区已有 `.gitignore`、`.vscode/`、
`httpclient.http`、`work_daily.md` 修改。

## 架构与接口决策

### 缓存

- 由 `scripts/lib/validate-workflow-core.sh` 调用一个 Python 小工具计算并
  校验静态规则快照；输入清单固定来自 core 的声明列表，路径必须位于仓库
  边界内且为普通文件。
- 每条记录使用独立检查 ID 文件，至少包含 `schema_version`、`check_id`、
  `implementation_fingerprint`、`input_fingerprint`、`command_fingerprint`、
  `status=PASS`、`executed_at`。写入采用临时文件加原子替换；解析或替换失败
  按未命中，不让缓存写入错误阻断真实检查。
- fast 只复用记录；standard 运行 core 和目标/回归测试；required 清空
  继承的缓存开关并禁止读写规则缓存。失败或输入缺失清除对应记录。

### 验证层级

| 层级 | 入口 | 覆盖 | 缓存 | 结果 |
|---|---|---|---|---|
| fast | `--fast` | core 静态结构检查 | 可复用 PASS | 适合探索和标准 Verify 前置 |
| standard | 默认全量或显式标准入口 | core + 顶层契约套件 + 变更目标测试 | 不沿用 fast 结果作为终验 | 允许声明的可选 SKIP |
| required | `--require-openspec` | OpenSpec strict、core、全部必需契约/测试 | 禁止读写 | 任一 FAIL/SKIP 门禁阻断 |

升级依据由变更文件分类函数统一实现；命中入口、技能、core、模板或安装
资产时，standard 终验提示并执行 required。旧参数组合冲突仍以退出码 2
拒绝，不先跑部分检查。

### 模板与预检

- `openspec/templates/` 保存四类静态 Markdown 模板；模板只提供字段槽位，
  不承载变更状态。
- `scripts/new-openspec-change.py` 提供 `create` 和 `check` 两个子命令：
  `create` 只接受安全变更名和 `standard|strict`，目标必须为空或不存在；
  `check` 只读解析指定目录并报告文件/字段错误。
- 生成 strict 时创建 design 模板；standard 默认不创建 design，只有调用者
  明确 `--with-design` 才生成。所有命令字段必须是一行 shell 命令，场景必须
  同时含 WHEN/THEN，模板中的 `{{...}}` 槽位在 check 时一律报错。

## 任务与实施顺序

### 1. 缓存工具与 core 接口

- Create `scripts/lib/validation_cache.py`：实现输入清单规范化、SHA-256
  指纹、严格 JSON 解析（拒绝重复键/未知字段）、原子写入和命中判定。
- Modify `scripts/lib/validate-workflow-core.sh`：声明规则输入、接入工具、
  区分 fast/standard/required，记录透明来源；保留现有业务检查和汇总格式。
- Modify `scripts/validate-workflow.sh`：规范层级参数转发、冲突检测和 required
  缓存禁用；不改变已有调用的退出码。
- Test `scripts/tests/test_validate_workflow.py`：新增暖命中、每类失效、损坏、
  失败清除、原子写入中断、required 绕过和并发锁用例。
- Run `python3 -B -m unittest -v scripts.tests.test_validate_workflow`；预期
  全部 PASS，且缓存命中仍渲染 `[PASS]` 与 `PASS=... FAIL=0`。

### 2. 分层矩阵和自动升级

- Modify `scripts/validate-workflow.sh` 与 core：实现层级元数据输出、文件分类
  升级和参数冲突 fail-closed。
- Modify `AGENTS.md`、`.codex/README.md`、`.codex/skills/{open,build,verify,archive}/SKILL.md`、
  `.ai/rules/index.md`、`scripts/workflow-pressure-scenarios.md`：同步三层
  命令、缓存边界、升级条件和终验证据要求。
- Modify `scripts/tests/test_validate_workflow.py`：覆盖默认/fast/required
  矩阵、工作流文件命中升级、非命中保持层级和冲突退出码。
- Run `bash scripts/validate-workflow.sh --fast`、`bash scripts/validate-workflow.sh`
  和 `bash scripts/validate-workflow.sh --require-openspec`；记录每次的退出码、
  PASS/FAIL/SKIP 汇总和 required 的实际执行证据。

### 3. 模板、生成器和预检

- Create `openspec/templates/proposal.md`、`spec.md`、`tasks.md`、`design.md`，
  固定必需字段、场景和验证槽位。
- Create `scripts/new-openspec-change.py`：实现安全路径检查、空目录创建、
  模式/状态初始化、strict design 条件和只读 check；禁止路径穿越、绝对路径、
  非空覆盖和目录外写入。
- Modify `scripts/lib/validate-workflow-core.sh`：加入模板文件枚举、结构契约
  和活动变更产物预检，不把历史已归档产物强制迁移到新模板。
- Test `scripts/tests/test_openspec_templates.py`：临时目录成功生成；缺字段、
  空场景、占位符、多行命令、非法变更名、非空目录和目录越界均失败。
- Run `python3 -B -m unittest -v scripts.tests.test_openspec_templates`、
  `git diff --check`；预期生成目录文件数和内容稳定可复现。

### 4. 规格、镜像、压力场景和证据

- Modify `openspec/specs/risk-tiered-ai-workflow/spec.md` 与
  `openspec/specs/shared-ai-workflow-infrastructure/spec.md`：合并本变更
  Requirements/Scenarios，保持缓存、层级和模板语义唯一。
- Modify 必要的 Codex 随包资产与结构清单，保证镜像检查、安装 manifest 和
  旧工具名扫描仍通过。
- Run `bash scripts/validate-workflow.sh --require-openspec`、相关压力场景、
  OpenSpec strict 校验、模板测试、`git diff --check`；保留 manifest、命令
  输出、未验证范围和残余风险。

## 自审结论

- 三条 delta Requirement 均有对应实现任务、失败路径和验证命令。
- 未新增权限、资金、数据库迁移、删除、发布或远程副作用；计划只写本地
  工作流文件和临时缓存。
- 所有新增选择均已在已确认 proposal 的三个假设中声明；未引入需要第二次
  实施确认的硬风险。计划完成后可进入 Build。
