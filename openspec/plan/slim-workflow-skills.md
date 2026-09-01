# 实现计划: slim-workflow-skills

零上下文执行者可直接实施。状态真源：`openspec/changes/slim-workflow-skills/proposal.md`（`模式: 严格`）。

## 目标与全局约束（逐字遵守）

- **目标**：三个技能正文瘦身与示例本土化、字符口径验证命令、技能编辑↔施压场景重跑绑定、校验器三守卫，delta spec 全 Scenario 落地。
- **技术栈**：中文 Markdown 技能文本（内容契约校验）；bash 结构校验器＋python unittest 契约套件（运行时行为，TDD 红—绿）。
- **四副本同步**：每个技能编辑任务内一次更新 `.claude/skills/<s>/SKILL.md`、`.codex/skills/<s>/SKILL.md`、`scripts/ai-workflow-assets/claude/.claude/skills/<s>/SKILL.md`、`scripts/ai-workflow-assets/codex/.codex/skills/<s>/SKILL.md`。两侧唯一允许差异：`.claude`/`.codex` 路径前缀改写（`mirror_equal` 归一化登记项）。
- **不得破坏的锚定**：适配注记行（`> **Codex 执行环境`，全仓恰 1 条，位于 parallel-agents 的 .codex 侧）及其中 `spawn_agent`/`followup_task`/`send_message`/`wait_agent`/`fork_turns`；废弃工具名零残留。
- **校验器零新增外部命令**：新守卫只用既有 `grep`/`test`。
- **顺序约束**：技能文本任务（1–3）必须先于守卫任务（5）——absence 守卫的"干净必绿"依赖瘦身后的正文。
- **终验链（任务 6）启动后仓库零编辑**；一切验证现跑并读取退出码；umask-002 检出环境在跑安装器套件前先做权限规范化（目录/文件 644，两个可执行脚本 755：`validate-workflow.sh`、`pre-push`）。

## 任务 1：writing-skills 内联瘦身（四副本一体）

- **Modify**：上述四路径的 `writing-skills/SKILL.md`。
- **内容契约**：
  1. 5 处"（源技能……未随本仓库迁移……）"注记删除，概述处保留一行来源说明（"本技能改写自宿主 superpowers:writing-skills；其伴生参考未随仓库迁移，核心规则已内联"——不得含"未随本仓库迁移"字样）。
  2. "token 效率"验证命令块改为字符口径并登记阈值（常规技能 ≤5000、本技能 ≤7500 去空白字符）：
     ```bash
     tr -d '[:space:]' < .claude/skills/<技能名>/SKILL.md | wc -m   # codex 侧路径前缀相应改写
     ```
  3. 编辑/部署流程节新增绑定句（两侧逐字同文，因引用共享路径 `scripts/workflow-pressure-scenarios.md` 无前缀差异）："修改任一工作流技能正文后，Verify 终验必须重跑 `scripts/workflow-pressure-scenarios.md` 中与该技能行为相关的场景（相关性无法判定时重跑全部），逐场景记录 PASS/FAIL 于变更目录。"
  4. 保留 delta/design 红线语义：TDD 映射、SDO（含反工作流捷径实测理由）、形式匹配失败类型表、合理化免疫、微测措辞 5 条、测试类型分型、部署清单、"100+ 行重型参考拆分"规则。
  5. 压缩目标：去空白字符 ≤7500（现 9780）；示例单例化、去重"铁律/停下"重复段。
- **验证**：`bash scripts/validate-workflow.sh --fast` 全绿（覆盖 mirror/注记计数/工具名）；`tr -d '[:space:]' < .claude/skills/writing-skills/SKILL.md | wc -m` ≤7500；`grep -rc "未随本仓库迁移" .claude .codex scripts/ai-workflow-assets` 全部为 0；四副本剥离路径前缀后逐字一致。
- **提交**：`feat(skills): writing-skills 内联瘦身与字符口径验证`（仅四文件）。

## 任务 2：parallel-agents 示例本土化（四副本一体）

- **Modify**：四路径的 `parallel-agents/SKILL.md`。
- **内容契约**：
  1. TS 测试文件示例（`agent-tool-abort.test.ts` 等）替换为本仓库场景最小示例：三个互相独立的安装器/校验失败域（如 `test_install_workflow.py` 某用例红、core 某结构检查红、`pre-push` 钩子行为异常），一个示例贯穿"识别域→聚焦派发→并行→汇合"即可。
  2. 删除"来自真实会话的示例"整节（叙事反模式）。
  3. 保留：dot 决策流程图、使用/不使用条件、代理提示结构四要素、常见错误、验证四步、**Codex 适配注记行原样**。
  4. 压缩目标：去空白字符 ≤1800（现 2518）。
- **验证**：`--fast` 全绿；`grep -Ec "\.test\.ts|codesign" <四副本>` = 0；字符数达标。
- **提交**：`feat(skills): parallel-agents 示例本土化`。

## 任务 3：systematic-debugging 示例本土化（四副本一体）

- **Modify**：四路径的 `systematic-debugging/SKILL.md`。
- **内容契约**：
  1. 阶段 1 第 4 条的 macOS 签名 4 层示例替换为安装器多层排查示例（安装入口 shell → `lib/install_ai_workflow.py` Python 层 → 目标 git/权限层 → 校验器层，每层一条探测命令＋"哪一层断"结论）。
  2. "Ultra-think 这个"等宿主语汇改为中性表述（"深度推演这个"）。
  3. 保留：铁律、四阶段结构、"3 次修复失败质疑架构"、红旗清单、合理化表、坑位即时入库（`.ai/memory` 三行格式）、速查表。
  4. 压缩目标：去空白字符 ≤5000（现 3640，主要替换示例，允许持平）。
- **验证**：`--fast` 全绿；`grep -c "codesign\|list-keychains\|Ultra-think"` = 0；字符数达标。
- **提交**：`feat(skills): systematic-debugging 示例本土化`。

## 任务 4：9 场景全量重跑（行为验证）

- **执行**：按 `scripts/workflow-pressure-scenarios.md` 共同要求＋9 个场景（R/Q/S/X/I/O/N/W/A/M），逐字文本派发全新上下文子代理；结果按该文件"结果记录"格式写入 `openspec/changes/slim-workflow-skills/scenario-rerun.md`（逐字回答摘要、逐条 PASS/FAIL、理由归类）。
- **预期**：9/9 PASS。任一 FAIL → 定位对应措辞 → 回退该处（回到任务 1–3 修正）→ 复跑该场景；不带 FAIL 前进。
- **提交**：`docs(slim-workflow-skills): 9 场景重跑记录`（仅记录文件）。

## 任务 5：校验器三守卫（TDD 红—绿）

- **红（先写，先失败）**——Modify `scripts/tests/test_validate_workflow.py`，在既有拒收用例区（`test_rejects_*`，约 982–1021 行后）仿照模式新增 3 用例（改 fixture → `self._run_validator()` → 断言非零＋`[FAIL]` 标签 → `finally` 恢复；codex 侧用例带 `skipTest` 守卫）：
  1. `test_rejects_migration_notes_in_guarded_skills`：向 `.claude/skills/writing-skills/SKILL.md` 追加一行含"未随本仓库迁移"注记 → 期望 `[FAIL] 技能迁移注记零残留`。
  2. `test_rejects_writing_skills_without_char_metric`：将正文中 `tr -d` 整行替换回 `wc -w` 旧命令 → 期望 `[FAIL] writing-skills 字符口径锚串`。
  3. `test_rejects_writing_skills_without_scenario_binding`：删除绑定句所在行 → 期望 `[FAIL] writing-skills 场景重跑绑定`。
  - 运行：`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest scripts.tests.test_validate_workflow.ValidateWorkflowContractTest.test_rejects_migration_notes_in_guarded_skills ...` —— **预期 3 用例全部 FAIL**（校验器尚无守卫，注入后仍退出 0）。- **红（先写，先失败）**——Modify `scripts/tests/test_validate_workflow.py`，在既有拒收用例区（`test_rejects_*`，约 982–1021 行后）仿照模式新增 3 用例（改 fixture → `self._run_validator()` → 断言非零＋`[FAIL]` 标签 → `finally` 恢复；所用助手侧不在 fixture 时 `skipTest` 守卫，与既有用例同款）：
- **绿**——Modify `scripts/lib/validate-workflow-core.sh`，在"注记现行工具名"检查后新增：
  1. `skill_migration_notes_absent()`：对两侧 `writing-skills`/`parallel-agents`/`systematic-debugging` 的 SKILL.md（按 `assistant_required` 判定存在侧）`grep -F -q -e '未随本仓库迁移' -- <file>`，任一命中 `return 1`；循环结束**显式 `return 0`**（shell 返回值坑）。注册：`check "技能迁移注记零残留" skill_migration_notes_absent`。
  2. `check "writing-skills 字符口径锚串"`：既有 `contains_all` idiom，双侧分别断言 `tr -d` 与 `wc -m`。
  3. `check "writing-skills 场景重跑绑定"`：双侧分别断言 `workflow-pressure-scenarios.md` 与 `重跑`。
  - 锚串均不以 `--` 开头；仅用 grep/test，零新外部命令。
- **验证**：3 用例转绿；`bash scripts/validate-workflow.sh --fast` 干净全绿（PASS 计数 +3 左右，摘要行 `PASS=… FAIL=0 SKIP=0`）；注入探针手工复验任一守卫非零。
- **提交**：`feat(gate): 技能迁移注记与 writing-skills 锚串守卫`（core＋契约套件两文件）。

## 任务 6：严格终验链

1. `bash scripts/validate-workflow.sh --require-openspec`（全量，含契约套件约 5 分钟；串行、后台长跑、不设武断超时）。
2. `openspec validate --all --strict --no-interactive`（CLI 缺失时装入已忽略的 `.ai-local` 并临时扩展 `PATH`；不运行 init/update）。
3. 安装器套件：umask-002 环境先权限规范化，再 `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest scripts.tests.test_install_workflow scripts.tests.test_install_ai_workflow`（约 20 分钟，串行、后台；覆盖四副本字节一致性 `test_reusable_assets_are_byte_synchronized_with_active_sources`）。
4. `git diff --check`、目标 diff 与状态清单核对。
5. 预期全部绿；任一红 → 停链修复 → 从第 1 步整链重跑（链内零提交零编辑原则只在最终证据轮生效）。

## 提交结构

1 → 2 → 3 → 4 → 5 → 6（如有修复）各自独立可回滚；不拆机械 checklist 提交。
