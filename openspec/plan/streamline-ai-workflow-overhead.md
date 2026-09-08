# 实现计划: streamline-ai-workflow-overhead

零上下文执行者可直接实施。状态真源：`openspec/changes/streamline-ai-workflow-overhead/proposal.md`（`模式: 严格`、`状态: 待确认计划`）。

## 目标与全局约束（逐字遵守）

- **目标**：把流程成本绑定到可观察风险边界——标准三件套条件化、严格第二次确认按硬风险触发、任务级审查按高风险不变量冻结、Archive 按 Verify 后 diff 选择门禁层级、`.ai-local` 缓存精确清理；权限/资金/Schema/迁移/破坏性/外部副作用的硬门禁保持不变。
- **不命中硬二次确认集合**：本 plan 不涉及权限行为、资金账务、数据库 Schema/迁移、数据删除、破坏性操作、外部副作用；可连续进入 Build（按 delta spec 强一致实现）。
- **delta spec 真源**：`openspec/changes/streamline-ai-workflow-overhead/specs/risk-tiered-ai-workflow/spec.md`；本 plan 不引入 spec 之外的新需求。
- **任务级审查按两个高风险不变量组织**（来自 proposal+design+delta 收敛）：
  1. **工作流状态/确认语义**——AGENTS.md/技能/主规格中"标准三件套条件、严格风险触发二次确认、状态路径"必须与 delta spec 强一致。
  2. **验证降级判定**——`scripts/validate-workflow.sh` 的归档轻量门禁 + diff 分类升级必须能由契约测试与 mutation 测试双向钉死。
- **runtime 行为变更必须 TDD 红—绿**（校验器升级）；纯文档/规格用内容契约、结构、字符口径、diff 校验。
- **核心交付物**（`delta spec` → `master` 合并发生在 Archive 阶段；本 plan 不预合并主规格）：
  - `AGENTS.md`（根入口：风险路由 / 标准 / 严格 / 共享审查 / 状态真源 等节）
  - `openspec/specs/risk-tiered-ai-workflow/spec.md`（Archive 时合并）
  - `.codex/skills/open|design|build|verify|archive/SKILL.md`（5 文件）
  - `.ai/rules/review.md`
  - `scripts/validate-workflow.sh`（新增 `--archive-light` 入口 + diff 分类自动升级）
  - `scripts/tests/test_validate_workflow.py`（新增 mutation + 契约测试）
  - `.codex/skills/archive/SKILL.md` 中关于 `.ai-local` 精确清理段落
- **本地整合策略**（沿用 proposal 已确认）：worktree `feature/streamline-ai-workflow-overhead`；通过 Archive 后本地 `--no-ff` 合回 `master`，不 push、不创建 PR；`master` 干净后按确认包含的清理策略删 feature/worktree。
- **用户修改保护**：实施前记录 `git status` 现状（已知有 `.ai/memory/git-worktrees.md`、`.vscode/settings.json`、`http-client.http` 处于本机工作区），worktree 内不携带这些；任何目标文件若出现新用户修改，立即暂停并重新隔离或请求决定。
- **不得修改业务子仓库运行时代码 / API / 数据库 Schema / 部署配置**（proposal 非目标）。

## 任务 1：根入口 `AGENTS.md` 规则改写（内容契约）

- **Modify**：`AGENTS.md`
- **改写点**（按节，文字级别精确到标题与子句）：
  1. `## 风险路由` 表的标准路径列：从 `Open 一次产出可执行四件套` 改为 `Open 一次产出可执行三件套+条件 design`（并在表后加一句解释："标准三件套即 proposal/delta spec/tasks；存在跨模块取舍、新依赖、状态模型、重要替代方案或无法在 proposal/tasks 中清晰表达的架构决策时增加 design"）。
  2. `### 标准模式` 节：删除 "Open 一次创建 ... `design.md`" 一句；增加 "design 由可观察条件触发（见风险路由表注）"；并把"不创建 `openspec/plan/<变更名>.md`"明确为 "标准模式不得生成独立 plan"。
  3. `### 严格模式` 节：增加 "第二次实施前确认由不可逆风险触发：权限认证、资金账务、数据库 Schema/迁移、数据删除、破坏性动作、外部副作用，或计划引入规范未覆盖的选择/假设/依赖/范围时，必须将状态置为`待确认计划`并等待用户确认；不命中上述集合且未引入新选择的严格计划，可在完成计划自审后连续进入 Build。"
  4. 新增 `### 审查单元` 子节（隶属 `## 共享审查与有限角色`）："任务级审查对象为高风险实现单元（并发不变量、权限边界、跨服务契约、资金/账务不可逆性等）；多个 checklist 共享同一不变量时合并为一次审查。Verify 双阶段（规格符合性、代码质量）保持独立关注面。"
  5. 新增 `### 归档门禁` 子节（隶属 `## 共享审查与有限角色`）："Archive 运行 `bash scripts/validate-workflow.sh --archive-light`；当 Verify 完整门禁通过后发生了工作流可执行文件、助手入口、技能语义、契约测试或治理规格变化，Archive 自动升级为 `bash scripts/validate-workflow.sh --require-openspec`；判定依据为 Verify 后 diff 分类，禁止人工口头跳过。"
  6. 新增 `### .ai-local 缓存清理` 子节（隶属 `## 共享审查与有限角色`）："OpenSpec 归档文件写入最终 manifest ID、comparison base、finding 状态、未验证范围、残余风险后，可删除对应 `.ai-local/reviews/<change>/`；活跃 review、STALE manifest、未持久化最终证据的目录不得自动清理；不得递归清理整个 `.ai-local`。"
  7. 保留"标准仍至多一次综合审查；严格仍为任务级审查加 Verify 两个独立关注面"原句不变。
- **验证**：
  ```bash
  # 关键短语存在性
  grep -F "Open 一次产出可执行三件套" AGENTS.md
  grep -F "design 由可观察条件触发" AGENTS.md
  grep -F "标准模式不得生成独立 plan" AGENTS.md
  grep -F "第二次实施前确认由不可逆风险触发" AGENTS.md
  grep -F "任务级审查对象为高风险实现单元" AGENTS.md
  grep -F "bash scripts/validate-workflow.sh --archive-light" AGENTS.md
  grep -F "自动升级为" AGENTS.md && grep -F "diff 分类" AGENTS.md
  grep -F "可删除对应 \`.ai-local/reviews/<change>/\`" AGENTS.md
  # 旧四件套契约未残留
  ! grep -F "Open 一次创建 \`proposal.md\`、delta \`spec.md\`、\`design.md\`、含精确步骤和命令的 \`tasks.md\`" AGENTS.md
  ```
- **提交**：`docs(workflow): AGENTS.md 按风险触发精简流程开销`（仅 AGENTS.md）。

## 任务 2：阶段技能 SKILL.md 同步（5 文件，内容契约）

- **Modify**：`.codex/skills/open/SKILL.md`、`.codex/skills/design/SKILL.md`、`.codex/skills/build/SKILL.md`、`.codex/skills/verify/SKILL.md`、`.codex/skills/archive/SKILL.md`
- **改写点**（按文件，句子级别精确）：
  1. `open/SKILL.md` 分类契约表的"标准"出口行：把 "一次产出可执行四件套" 改为 "一次产出可执行三件套，存在独立架构决策时增 design"；状态字段保持 `状态: 待确认计划`。
  2. `open/SKILL.md` 标准模式段落：删除 "design.md：关键决策、替代方案、风险与边界" 一行；增加 "design（仅当跨模块取舍、新依赖、状态模型、重要替代方案或架构决策无法在 proposal/tasks 中清晰表达时生成）"；并增加 "不得为无独立设计决策的变更制造空壳 design"。
  3. `design/SKILL.md` 顶部增加"严格第二次确认按不可逆风险触发"段：列出硬集合（权限/资金/Schema/迁移/数据删除/破坏性/外部副作用）+ "未命中则 plan 自审后连续 Build"；并删去任何"标准模式也进入 Design"或"标准要 design"的暗示。
  4. `build/SKILL.md` 标准小任务表加注："小任务不因模式存在而机械分派多代理；标准模式 Build 内只自查，综合审查留给 Verify 一次。"（保持与现有 `build/SKILL.md` 中"标准小任务不得仅为形式创建 SDD 台账..."一致，仅收紧措辞而非新增）
  5. `verify/SKILL.md` "标准：一次综合审查" 段首加 "审查单元以高风险不变量划分；多 checklist 共享同一不变量时合并为一次审查"；其余不变。
  6. `archive/SKILL.md` "4. 归档后强制验证" 节替换为：
     ```text
     4. 归档后强制验证
     - 运行 `bash scripts/validate-workflow.sh --archive-light`；
     - 若 Verify 完整门禁通过后工作流可执行文件、助手入口、技能语义、契约测试或治理规格发生变化，升级为 `bash scripts/validate-workflow.sh --require-openspec`；
     - 失败立即停止归档并修复；严格模式 OpenSpec 与仓库自带必需测试不得 SKIP。
     ```
  7. `archive/SKILL.md` 末尾"分支整合"前新增 `.ai-local` 清理段："在归档 tasks 持久最终 manifest ID、comparison base、finding 状态、未验证范围、残余风险后，删除 `.ai-local/reviews/<change>/`（仅该路径，不得 `rm -rf .ai-local`）。活跃/STALE/未持久化最终证据的目录保留。"
- **验证**：
  ```bash
  bash scripts/validate-workflow.sh --fast  # 既有结构校验仍全绿
  for s in open design build verify archive; do
    test -f .codex/skills/$s/SKILL.md
  done
  # 关键短语存在
  grep -F "三件套" .codex/skills/open/SKILL.md
  grep -F "存在独立架构决策时增 design" .codex/skills/open/SKILL.md
  grep -F "不可逆风险触发" .codex/skills/design/SKILL.md
  grep -F "高风险不变量" .codex/skills/verify/SKILL.md
  grep -F "--archive-light" .codex/skills/archive/SKILL.md
  ! grep -F "rm -rf .ai-local" .codex/skills/archive/SKILL.md
  # 旧契约未残留
  ! grep -F "一次产出可执行四件套" .codex/skills/open/SKILL.md
  ```
- **提交**：`docs(skills): 阶段技能按风险触发与高风险不变量同步`（5 文件，原子提交；不按文件拆提交）。

## 任务 3：共享审查规则 `.ai/rules/review.md` 改写（内容契约）

- **Modify**：`.ai/rules/review.md`
- **改写点**：
  1. 顶部"冻结与陈旧检测"节追加："任务级审查对象为高风险不变量；多个 checklist 共享同一不变量时合并为一次审查，冻结范围时按不变量名聚合。"
  2. finding 台账示例后追加 "manifest 清理约束" 段："OpenSpec 归档文件持久化最终 manifest ID 与 finding 结论后，对应 `.ai-local/reviews/<change>/` 可作缓存清理；活跃/未归档/STALE manifest 不得清理；不得递归删除整个 `.ai-local`。"
  3. 保留"标准模式仍至多一次全 diff 综合审查"原句；保留"严格模式仍是 Build 的任务级审查，加 Verify 的规格符合性与代码质量两个独立关注面"原句。
- **验证**：
  ```bash
  grep -F "高风险不变量" .ai/rules/review.md
  grep -F "不得递归删除整个 \`.ai-local\`" .ai/rules/review.md
  # 旧契约未消失
  grep -F "标准模式仍至多一次全 diff 综合审查" .ai/rules/review.md
  grep -F "规格符合性与代码质量两个独立关注面" .ai/rules/review.md
  ```
- **提交**：`docs(review): 任务级审查按高风险不变量冻结`。

## 任务 4：校验器 `scripts/validate-workflow.sh` 新增归档轻量门禁 + diff 分类升级（runtime 行为变更，TDD 红—绿）

- **Modify**：`scripts/validate-workflow.sh`（优先把归档轻量入口放在 wrapper；core 不动）
- **设计**：
  - wrapper 新增参数 `--archive-light`：跳过顶层契约套件（`unittest` 调用），仅运行 core（与 `--fast` 等价语义但语义上区分用途：fast = 终验分层、archive-light = 归档专用）；与 `--require-openspec` 互斥，后出现者优先并打印冲突错误。
  - wrapper 新增自动升级判定（仅在未显式传 `--archive-light` 时）：在归档入口被调用时（新增环境变量 `WORKFLOW_ARCHIVE_GATE=1`），若核心完成 Verify 后 `git diff --name-only <base> -- <list>`（base 取 `$WORKFLOW_ARCHIVE_BASE` 或 `HEAD`）的输出非空，则把内部 mode 升级为 `--require-openspec`；否则保持 `--archive-light`。
- **红（先写，先失败）**——`scripts/tests/test_validate_workflow.py` 新增测试类 `ArchiveLightGateTest`：
  - `test_archive_light_skips_top_level_suite_when_no_semantic_diff`：stub core `exit 0` + INTERNAL_RESULT 串；`--archive-light` 入口；断言退出码 0 且 wrapper 未尝试调用 `unittest`（通过环境变量 `WORKFLOW_SKIP_CONTRACT_FOR_TEST=1` 透传控制）。
  - `test_archive_light_promotes_to_require_openspec_when_workflow_assets_changed`：stub core 串；调用 `WORKFLOW_ARCHIVE_GATE=1 bash scripts/validate-workflow.sh --archive-light --archive-files scripts/validate-workflow.sh AGENTS.md`；断言 wrapper 检测到变更并改跑契约套件（stub `unittest` 改为 `python3 -B -m unittest -v scripts.tests.test_validate_workflow --help` 跑出 0；或断言日志含 "promoted to --require-openspec"）。
  - `test_archive_light_rejects_conflict_with_require_openspec`：`--archive-light --require-openspec` 同时传，断言 exit 2 且 stderr 含 "conflict" 字样。
  - `test_archive_light_exit_two_on_invalid_args`：仅 `--archive-light` 缺文件列表，断言 exit 2。
  - `test_archive_light_passthrough_uses_core_exit`：stub core `exit 1` 不写 INTERNAL_RESULT，断言 wrapper 退出码非零且不进入契约套件。
- **绿**——`scripts/validate-workflow.sh`：
  1. 参数解析循环增加 `--archive-light`、`--archive-files`；冲突检测。
  2. 设置内部变量 `archive_light=0`、`archive_files=()`、`require_openspec_user=0`。
  3. 当 `archive_light=1` 时跳过 `python3 -B -m unittest -v scripts.tests.test_validate_workflow` 块；保留 core 调用与 INTERNAL_RESULT 解析。
  4. 当 `WORKFLOW_ARCHIVE_GATE=1` 且 `--archive-files` 列表非空时：若 `git diff --name-only <comparison_base> -- <list>` 输出非空，则把内部 mode 设为 `require_openspec` 并打印 `[INFO] archive gate promoted to --require-openspec: <file>`（每文件一行）。
  5. `require_openspec_user=1` 与 `archive_light=1` 互斥 → 打印冲突错误到 stderr → exit 2。
  6. 退出码：保持现有"FAIL>0 或 core_status != 0 → exit 1；core_status=2 → exit 2；否则 0"。
- **验证**：
  ```bash
  # 红→绿基线
  uv run pytest -q scripts/tests/test_validate_workflow.py -k ArchiveLight  # 先红
  # 实现 wrapper 后
  uv run pytest -q scripts/tests/test_validate_workflow.py -k ArchiveLight  # 后绿
  # 端到端
  bash scripts/validate-workflow.sh --archive-light  # 缺文件列表 → exit 2
  WORKFLOW_ARCHIVE_GATE=1 bash scripts/validate-workflow.sh --archive-light --archive-files AGENTS.md  # 自动升级
  # 既有 fast/全量仍绿
  bash scripts/validate-workflow.sh --fast
  ```
- **提交**：`feat(workflow): 归档轻量门禁与 diff 分类自动升级`（wrapper + tests 一起，避免半提交状态）。

## 任务 5：mutation + 契约测试扩充（覆盖 delta spec 全部 Scenario）

- **Modify**：`scripts/tests/test_validate_workflow.py`
- **新增测试类**（仿既有 `test_rejects_*` 模式：临时目录改 fixture → 跑 wrapper → 断言非零 + `[FAIL]` 标签 → `finally` 恢复）：
  - `MutationStandardThreePieceSuiteTest`：
    - `test_rejects_standard_four_piece_doc`：在临时仓内放标准模式 proposal 带四件套路径（proposal+spec+design+tasks），断言 `bash scripts/validate-workflow.sh --fast` 非零且带 `[FAIL]` 标签。
    - `test_accepts_standard_three_piece_doc`：同 fixture 但无 design.md，断言 wrapper 退出 0。
    - `test_accepts_standard_with_design_when_decision_signal_present`：fixture proposal 含 "跨模块取舍" 关键字 + 有 design.md，断言通过。
  - `StrictSecondConfirmHardSetTest`：
    - `test_rejects_strict_plan_without_hard_risk_when_plan_marks_pending`：fixture 严格 plan 含资金/Schema 关键字，断言非零。
    - `test_accepts_strict_plan_without_hard_risk_when_plan_self_audited`：fixture 严格 plan 不含硬风险关键字且 proposal 写 "已计划自审连续进入 Build"，断言通过。
  - `ArchiveLightPromotionTest`（与任务 4 共享部分用例，独立类便于 failure 定位）：
    - `test_archive_light_no_promotion_when_no_files`：stub core exit 0 + INTERNAL_RESULT 串；无 `--archive-files`，断言不升级。
    - `test_archive_light_promotion_triggered_by_workflow_script_change`：`--archive-files scripts/validate-workflow.sh`，断言日志含 "promoted"。
- **验证**：
  ```bash
  uv run pytest -q scripts/tests/test_validate_workflow.py -k "Mutation or StrictSecondConfirm or ArchiveLight"  # 全绿
  bash scripts/validate-workflow.sh --require-openspec  # 全量绿
  ```
- **提交**：`test(workflow): 风险触发与归档轻量门禁 mutation+契约测试`。

## 任务 6：Archive 缓存清理规则（落到 archive SKILL.md 与 review.md 双写）

- **Modify**：`.codex/skills/archive/SKILL.md`、`.ai/rules/review.md`
- **改写点**：
  1. `archive/SKILL.md` 新增 `.ai-local` 清理段（任务 2 段 7 已包含），并在"3. 归档数据"节插入"持久最终证据"子步骤：在把 `openspec/changes/<变更名>/` 移到 `openspec/archive/` 之前，确保 `tasks.md` 包含 `最终 manifest ID`（链接到最近一次 valid manifest）、`comparison base`（commit SHA）、`finding 状态`（open/resolved/not-an-issue/accepted-risk 计数）、`未验证范围`、`残余风险` 五段；不完整则停止归档。
  2. `review.md` 已包含的清理约束（任务 3）保留；`archive/SKILL.md` 引入 shell 片段：
     ```bash
     change=streamline-ai-workflow-overhead
     test -d .ai-local/reviews/$change || { echo "no cache dir"; exit 0; }
     # 仅精确删该 change 目录;禁止 rm -rf .ai-local
     rm -rf .ai-local/reviews/$change
     ```
- **验证**：
  ```bash
  grep -F "最终 manifest ID" .codex/skills/archive/SKILL.md
  grep -F "comparison base" .codex/skills/archive/SKILL.md
  grep -F "未验证范围" .codex/skills/archive/SKILL.md
  grep -F "残余风险" .codex/skills/archive/SKILL.md
  # 禁止性检查
  ! grep -E "rm -rf \.ai-local\b" .codex/skills/archive/SKILL.md  # 仅 rm -rf .ai-local (无子路径) 禁止
  ```
- **提交**：`docs(workflow): .ai-local 精确清理与归档证据持久化契约`。

## 任务 7：worktree 隔离、跑全量门禁、严格双阶段审查前自检

- **前置**：基线 `master` 干净（`git status --porcelain` 为空），当前未检出 feature。
- **动作**：
  1. 在主工作区创建并切到 `feature/streamline-ai-workflow-overhead`，只暂存四件套与本 plan，提交 `chore(openspec): streamline-ai-workflow-overhead 四件套与实现计划`；状态置为`构建中`。
  2. 切回 `master`，`git worktree add ../wt-streamline-ai-workflow-overhead feature/streamline-ai-workflow-overhead`（顺序：先有 feature 分支提交明确文件，再挂载）。
  3. 在 worktree 内按任务 1–6 顺序执行；每个任务完成后在该 worktree 跑任务自带验证再勾选。
  4. 全部 tasks 完成后跑：
     ```bash
     uv run pytest -q
     uv run ruff check .
     bash scripts/validate-workflow.sh --require-openspec
     openspec validate --all --strict --no-interactive
     git diff --check
     ```
     全部 0 退出码再进入 Verify。
- **任务级审查**（两个高风险不变量各一次独立审查；不是按任务数）：
  1. **不变量 A · 工作流状态/确认语义**：reviewer 检查 AGENTS.md / 5 技能 / review.md / 主规格与 delta 强一致；finding 字段、comparison base、未验证范围、残余风险按 `.ai/rules/review.md` 模板。
  2. **不变量 B · 验证降级判定**：reviewer 检查 `--archive-light` + diff 分类升级 + 5 个新增测试 + mutation 测试红—绿对的语义与退出码；同样的 finding 模板。
- **提交节奏**：每个任务自带一次提交；任务 4 wrapper + tests 一起；任务 5 mutation + 契约一起。
- **验证**：见各任务自带的验证命令；终态 `git status --short` 仅含 worktree 内未提交修改或为空。

## 任务 8：Verify 双阶段独立审查、Archive 合并、严格双关注面

- **Verify 阶段**（独立上下文顺序两次）：
  1. **阶段 1 · 规格符合性**：新 reviewer 读取 delta spec 全部 Scenario 与 `openspec/changes/.../tasks.md` 已勾项，独立核对实现；`review_manifest.py verify --manifest <manifest>` 两次 VALID。
  2. **阶段 2 · 代码质量**：新 reviewer 在阶段 1 通过后审查 wrapper / tests / SKILL.md 改写；重点是 `--archive-light` 升级分支的副作用、mutation 测试是否真能红、是否漏检。
  3. 任何 Critical/Important：复现 → 修 → delta 复审；最多五轮后争议升级用户。
- **Archive 阶段**（仅在 Verify 通过后）：
  1. 合并 delta 到 `openspec/specs/risk-tiered-ai-workflow/spec.md`（按 ADDED/MODIFIED/REMOVED 规则；ADDED 整段并入主规格、MODIFIED 整 Requirement 替换）。
  2. memory 沉淀：`.ai/memory/workflow.md` 新增"标准三件套条件生成"、"严格风险触发二次确认"、"归档轻量门禁与 diff 分类升级"、"`.ai-local` 精确清理"四条（各 ≤6 行，遵循既有 `[YYYY-MM-DD] · 来源变更 …**坑**/**解**` 格式）。
  3. rules 路由：`.ai/rules/index.md` 在"风险分级工作流"行追加关键词"标准三件套条件 design、严格风险触发二次确认、归档轻量门禁、`.ai-local` 精确清理"（与既有"快速模式、标准模式、严格模式"等并列）。
  4. 移动 `openspec/changes/streamline-ai-workflow-overhead/` → `openspec/archive/streamline-ai-workflow-overhead/`；移动 `openspec/plan/streamline-ai-workflow-overhead.md` → 归档目录 `plan.md`。
  5. 追加 `openspec/archive/README.md` 索引行：`streamline-ai-workflow-overhead — 进一步精简 AI 助手工作流开销（标准三件套条件 + 严格风险触发二次确认 + 归档轻量门禁 + .ai-local 精确清理）（严格）`。
  6. 跑 `bash scripts/validate-workflow.sh --archive-light`（默认轻量；检测到工作流治理规格变化应自动升级为 `--require-openspec`，否则本变更无新增 wrapper 行为可判升级；如未升级，人工复核并按"禁止人工口头跳过"补一次 `--require-openspec`）。
  7. 提交 `chore(archive): streamline-ai-workflow-overhead`。
  8. 精确清理 `.ai-local/reviews/streamline-ai-workflow-overhead/`（仅该子路径），命令：
     ```bash
     change=streamline-ai-workflow-overhead
     [ -d .ai-local/reviews/$change ] && rm -rf .ai-local/reviews/$change
     ```
  9. 本地 `--no-ff` 合回 `master`（worktree 外主会话执行），在 `master` 上重跑 `bash scripts/validate-workflow.sh --require-openspec` 与 `openspec validate streamline-ai-workflow-overhead --strict --no-interactive` → 0 退出码。
  10. 不 push、不创建 PR；按确认包含的清理策略在 `master` 干净后删 feature 分支与 worktree。
- **完成声明**：`openspec/specs/risk-tiered-ai-workflow/spec.md` 已合并；`.ai/memory/workflow.md` 已沉淀；`.ai/rules/index.md` 已更新；`openspec/archive/` 已包含本变更目录与索引行；`master` 上 `--require-openspec` 0 退出码；feature/worktree 删除。

## 不可变项与防回流断言

下列断言在任务 7 终态与任务 8 完成后必须全部 0 命中：

```bash
! grep -E "Open 一次创建 .*proposal\.md.*design\.md" AGENTS.md
! grep -E "保留两次实施前确认" AGENTS.md
! grep -E "一次产出可执行四件套" .codex/skills/open/SKILL.md
! grep -E "rm -rf \.ai-local\b" .codex/skills/archive/SKILL.md
```

下列断言在 Archive 后必须全部命中：

```bash
grep -F "标准三件套条件" .ai/rules/index.md
grep -F "streamline-ai-workflow-overhead" openspec/archive/README.md
test -f openspec/archive/streamline-ai-workflow-overhead/plan.md
test -f openspec/archive/streamline-ai-workflow-overhead/proposal.md
test -f openspec/archive/streamline-ai-workflow-overhead/tasks.md
```

## 风险与控制

- **风险 1 · 可选 design 被滥用**：用"跨模块取舍 / 新依赖 / 状态模型 / 重要替代方案 / 架构决策无法清晰表达"作正向触发；mutation 测试双向钉死。
- **风险 2 · 条件式二次确认漏判**：硬编码不可跳过的硬风险集合（6 项）；`StrictSecondConfirmHardSetTest` 双向测试。
- **风险 3 · 轻量 Archive 漏检语义变化**：以 Verify 后 diff 文件分类触发完整门禁；`ArchiveLightPromotionTest` 与 `test_archive_light_promotion_triggered_by_workflow_script_change` 钉死。
- **风险 4 · `.ai-local` 清理误删**：精确路径 `rm -rf .ai-local/reviews/<change>/`；archive SKILL.md 与 review.md 双写明文禁止 `rm -rf .ai-local`（无子路径）；任务 8 步骤 8 强制仅删该子路径。

## 当前用户修改保护

实施前记录：

```bash
git status --short
git rev-parse --abbrev-ref HEAD
git worktree list
```

worktree 内不携带 `.ai/memory/git-worktrees.md`、`.vscode/settings.json`、`http-client.http`；目标文件若出现新用户修改立即暂停。
