# Tasks — fix-install-workflow-legacy-ai-kb

前置：工作区干净；分支 `fix-install-workflow-legacy-ai-kb`。

## 1. 失败测试先行（红）

- [ ] 新建 `scripts/tests/test_install_workflow.py`（unittest，参照 `scripts/tests/test_install_ai_workflow.py` 风格），先写两个用例：
      `test_fresh_install_succeeds`（空目标装完断言：退出码 0；`.ai/rules/index.md`、`.ai/kb/overview.md`、`.ai/tools/review_manifest.py` 存在；`.claude/skills/open/`、`.codex/skills/open/` 存在；`CLAUDE.md`、`AGENTS.md` 存在；`scripts/lib/validate-workflow-core.sh`、`scripts/tests/` 存在；`.claude/ai-kb/` 仅 README；project.md 含占位提示）
      `test_invalid_target_exit2`（不存在路径 → 退出码 2、零写入）
- [ ] 运行 `python3 -m unittest scripts.tests.test_install_workflow -v` → `test_fresh_install_succeeds` 必须红（复现 cp stat 失败），`test_invalid_target_exit2` 应绿。记录红证据。
- 验证命令：`python3 -m unittest scripts.tests.test_install_workflow -v`
- 预期结果：1 failed（fresh install 退出码 1）, 1 passed

## 2. 重构 install-workflow.sh 资产段

- [ ] 通读现脚本 1-127 行（参数/冲突扫描/辅助函数），确认冲突中止与 --force 备份现有实现。
- [ ] 将第 2)-3b) 段（技能循环 + 双 ai-kb 手工清单）与第 4)-5) 段（openspec 骨架 + 单文件校验脚本）替换为：从 `scripts/ai-workflow-assets/shared/`、`.../claude/`、`.../codex/` 三棵树复制到 `$TARGET/`（cp -r，保留 mode；`.gitkeep` 随树落位）。
- [ ] 冲突扫描扩展到三棵树全量文件；`--force` 逐文件 `<原名>.bak`；`.ai/memory/` 一律只补缺（不覆盖、不备份、不删除）。
- [ ] project.md 占位改用资产树内 `openspec/project.md`；若其文案仍含"五阶段/旧 ai-kb 路径"，同步修正资产树该文件（含其副本一致性）。
- [ ] `.gitignore` 追加规则补齐 `.claude/sdd/*`、`!.claude/sdd/.gitkeep`、`.worktrees/`（幂等追加，不动既有行）。
- [ ] 装后自检段保持：目标内 `./scripts/validate-workflow.sh` 全绿才退出 0。
- 验证命令：`bash scripts/install-workflow.sh /tmp/<新目录>`（预 mkdir）
- 预期结果：退出码 0；自检全绿；无 cp 报错

## 3. 补齐测试用例（绿 + 契约面）

- [ ] 追加用例：`test_no_args_exit2`、`test_help_exit2`、`test_conflict_aborts_without_force`（预置 CLAUDE.md → 非零退出、目标未被覆盖）、`test_force_backs_up`（--force 后存在 `CLAUDE.md.bak`）、`test_memory_never_overwritten`（预置 `.ai/memory/workflow.md` 打标 → 安装后内容不变且无 `.bak`）。
- [ ] 运行 `python3 -m unittest scripts.tests.test_install_workflow -v` → 全绿。
- 验证命令：`python3 -m unittest scripts.tests.test_install_workflow -v`
- 预期结果：OK（N 个用例全过）

## 4. 端到端 + 全量门禁

- [ ] 端到端：临时目录分别验证「空装」「--force 重装」「半装自愈」（模拟用户当前半装状态：预置 CLAUDE.md/.claude/skills 后重跑）。
- [ ] 全量门禁（触及安装资产，禁用 --fast）：`bash scripts/validate-workflow.sh` → FAIL=0。
- [ ] `openspec validate fix-install-workflow-legacy-ai-kb --strict --no-interactive` → 通过。
- 验证命令：`bash scripts/validate-workflow.sh && openspec validate fix-install-workflow-legacy-ai-kb --strict --no-interactive`
- 预期结果：PASS，FAIL=0；strict 校验通过

## 5. 知识沉淀

- [ ] `.ai/memory/installer.md` 追加本次坑条目（格式按 `.ai/memory/README.md`）：布局迁移未同步安装器资产清单 + 无测试覆盖导致必然失败。
- 验证命令：`tail -5 .ai/memory/installer.md`
- 预期结果：新条目三行格式完整

## 6. Verify 与收尾

- [ ] 状态置`待验证`，派发一次全 diff 综合审查（manifest 冻结按 `.ai/rules/review.md`）。
- [ ] finding 处置完毕、Critical/Important 归零后状态置`待归档`。
- [ ] Archive：delta 并入 `openspec/specs/workflow-installer/spec.md`（Purpose 的"五阶段"措辞一并更新为风险分级），目录移入 archive，合并 `fix-install-workflow-legacy-ai-kb` 回 main，归档后全量门禁复跑 FAIL=0。推送另行授权。
