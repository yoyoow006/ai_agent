# Tasks

- [x] 1.1 基线与落点:记录当前分支(main)与 `git status`,确认工作区仅有本变更产物(memory 追加 + 四件套);创建并切到 `feature/fix-merged-legacy-ai-kb-regression`,把 proposal(`状态: 构建中`)、specs、design、tasks 与 `.ai/memory/workflow.md` 审计条目作为首个职责单元提交。
      验证:`git log --oneline -1` 显示四件套提交;`git show --stat HEAD` 仅含上述文件;`git branch --show-current` 为 feature 分支。(aa4cd28,5 文件 +107)
- [x] 1.2 迁移 memory:把 `.claude/ai-kb/memory/installer.md`(2 条)、`.claude/ai-kb/memory/workflow-system.md`(5 条)与 `.codex/ai-kb/memory/workflow-system.md` 尾部 3 条独有条目共 10 条 2026-08-16 条目逐字插入 `.ai/memory/workflow.md` 顶部(现第一条 `## 2026-08-17` 之前),保持条目间空行与格式不变。
      验证:`grep -c "^## 2026-08-16" .ai/memory/workflow.md` 返回 10;`grep -c "^## "` 返回 56;与三份原文的标题+坑/解行逐字 diff 一致。(初版仅迁 claude 侧 7 条,综合审查 VQ-C01 核实 codex 侧另有 3 条独有条目共享层零命中,已在已确认范围内补迁并更正本条)
- [x] 1.3 删除复活旧正文:`git rm` 移除两侧共 10 个文件:`.claude|.codex/ai-kb/{kb/overview.md,rules/index.md,memory/.gitkeep,memory/installer.md,memory/workflow-system.md}`;保留两侧 `ai-kb/README.md`。
      验证:`git ls-files .claude/ai-kb .codex/ai-kb` 仅剩两个 README;磁盘上 `kb/`、`rules/`、`memory/` 目录消失;`git status --short` 无未预期文件。(已核对)
- [x] 1.4 结构与内容校验(串行):`bash scripts/lib/validate-workflow-core.sh` 全绿(重点:`旧 ai-kb 不含平行正文` PASS,汇总 FAIL=0)。
      验证:退出码 0 且输出末尾 `PASS=… FAIL=0 SKIP=…`。(INTERNAL_RESULT PASS=184 FAIL=0 SKIP=0)
- [x] 1.5 完整门禁(串行、后台等待、不加短 timeout):`bash scripts/validate-workflow.sh`。
      验证:退出码 0,汇总 `FAIL=0`,契约套件 82/82(`Ran 82 tests … OK`);另跑 `openspec validate fix-merged-legacy-ai-kb-regression --strict --no-interactive` 通过。(FULL_EXIT=0,PASS=185 FAIL=0;strict 校验在 Open 期与 core 内各过一次)
- [x] 1.6 diff 卫生:`git diff --check` 无输出;`git diff HEAD --stat` 仅含预期文件;按职责单元提交(memory 迁移+删除为一个职责单元,或按 1.2/1.3 分两个可独立回滚提交)。
      验证:`git log --oneline` 新增提交信息明确;`git status --short` 干净(允许后续 Verify 产物)。(943d914,+28/-122;diff-check CLEAN)
- [x] 2.1 状态推进:tasks 全勾后把 proposal `状态:` 置为`待验证`并提交,交 Verify。
      验证:proposal 头部显示 `状态: 待验证`。
- [x] 3.1 Verify 综合审查:主会话 `python3 .ai/tools/review_manifest.py freeze` 冻结范围,派独立上下文 reviewer 按 `.ai/rules/review.md` 全 diff 综合审查(关注面:delta 场景落地、迁移逐字无损、删除清单精确、无范围扩大);finding 按"验证→处置"闭环。
      验证:manifest 两次 `verify` 均 `VALID`;审查结论引用 manifest id;Critical/Important 全部关闭。(首轮 FAIL:VQ-C01 Critical 经核实为真——codex 侧 3 条独有条目未迁;cdcf5a2 修复后重冻结 1bddc094 差异复审通过,VQ-C01 resolved、无新增 finding;台账见 review-findings.md)
- [x] 4.1 终验:主会话现跑 `bash scripts/validate-workflow.sh`(全绿)与 `git diff --check`;状态置`待归档`并提交审查修复。
      验证:退出码 0、FAIL=0;`状态: 待归档` 已提交。(fda139b 树上 FINAL_EXIT=0、PASS=185 FAIL=0;diff --check 干净;finding 台账 Critical=0 未决)
- [x] 5.1 归档:delta 合并入 `openspec/specs/shared-ai-workflow-infrastructure/spec.md`(MODIFIED 整体替换,含新增场景);proposal `状态: 已归档`;目录移入 `openspec/archive/`;归档后现跑 `bash scripts/validate-workflow.sh` 全绿;`git add openspec/ .ai/ && git commit -m "chore(archive): fix-merged-legacy-ai-kb-regression"`。
      验证:主规格含新场景"合并复活已删除的旧正文";archive 目录就位;校验 FAIL=0。(主规格场景已并入;目录已移动;知识三写按需完成——memory 已沉淀逐侧计数教训,kb/rules 无稳定事实变化;提交前归档后校验结果记录于归档提交信息)
- [x] 6.1 整合:按已确认策略本地 `--no-ff` 合回 main,合并结果上复跑 `bash scripts/validate-workflow.sh` 全绿;推送 origin/main 等待用户单独授权。
      验证:main HEAD 为合并提交;校验退出码 0、FAIL=0;未执行任何 push。(合并 90d5959;合并结果现跑 MAIN_EXIT=0、PASS=183 FAIL=0;推送授权来自用户实施确认时选择的"--no-ff 合回 main 并推送(本次一并对推送授权)",推送在本回填提交后执行)
