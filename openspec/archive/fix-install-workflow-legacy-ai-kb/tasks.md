# Tasks — fix-install-workflow-legacy-ai-kb

前置：工作区干净；分支 `fix-install-workflow-legacy-ai-kb`。

## 1. 失败测试先行（红） ✓

- [x] 新建 `scripts/tests/test_install_workflow.py`，先写 `test_fresh_install_succeeds` + `test_invalid_target_exit2`
- [x] 运行 `python3 -m unittest scripts.tests.test_install_workflow -v` → 红证据：fresh install 退出码 1（复现 cp stat 失败），invalid_target 绿（1 failed, 1 passed）

## 2. 重构 install-workflow.sh 资产段 ✓

- [x] 资产源改为 `scripts/ai-workflow-assets/{shared,claude,codex}` 三树整体复制（`asset_files` 清单 + 逐文件 `cp -p`，`.gitkeep` 随树落位）
- [x] 冲突扫描覆盖三棵树全量文件；`--force` 逐文件 `<原名>.bak`；`.ai/memory/` 一律只补缺（不覆盖、不备份、不删除）
- [x] project.md 占位取资产树内版本（`openspec/project.md` 随 shared 树落位）
- [x] `.gitignore` 写带标记幂等块：`/.ai-local/`、双侧 sdd、`/.worktrees/`、`__pycache__/`、`*.py[cod]`（core 有"Python 缓存路径已忽略"检查）
- [x] 【构建中新增】迁移前旧布局残留检测：无 `--force` 专属错误中止，有 `--force` 各侧 `ai-kb/` 整目录备份 `ai-kb.bak/` 后重装重定向入口（否则目标校验器 `legacy_ai_kb_body_absent` 必红）
- [x] 【构建中重确认】装后自检改 `./scripts/validate-workflow.sh --fast`（秒级 core；双运行时目标无法通过随包套件全绿——profile 方案 2→10 例失败、随附安装器撞源仓标记，证据见 design.md D5）

## 3. 补齐测试用例（绿） ✓

- [x] 7 用例全绿（45 秒）：空装（含布局/gitignore 块/无 profile/无安装器文件/--fast 自检）、无效目标、无参、--help、冲突中止、--force 备份+memory 保护、旧布局残留
- 验证命令：`python3 -m unittest scripts.tests.test_install_workflow -v`
- 证据：Ran 7 tests in 45.060s — OK

## 4. 端到端 + 全量门禁（进行中）

- [x] 端到端三场景：空装（test 覆盖）、--force 重装+memory 保护（test 覆盖）、半装/旧布局自愈（LegacyLayoutTests 覆盖：--force 后自检全绿）
- [x] 新回归测试挂入源仓 CI：`.github/workflows/validate.yml` 新增 `Bash installer contract tests` 步骤（源仓专属，零目标面影响）
- [x] 全量门禁：`bash scripts/validate-workflow.sh` → **PASS=191 FAIL=0 SKIP=0**
- [x] `openspec validate fix-install-workflow-legacy-ai-kb --strict --no-interactive` → 通过（Change is valid）

## 5. 知识沉淀 ✓

- [x] `.ai/memory/installer.md` 追加坑条目，并随终局方案两次修订（profile/随附安装器尝试均记录否证证据）
- 证据：`tail .ai/memory/installer.md` 三行格式完整，含源仓标记教训

## 6. Verify 与收尾

- [ ] 状态置`待验证`，manifest 冻结 + 一次全 diff 综合审查（按 `.ai/rules/review.md`）
- [ ] finding 处置完毕、Critical/Important 归零后状态置`待归档`
- [ ] Archive：delta 并入 `openspec/specs/workflow-installer/spec.md`（Purpose"五阶段"措辞一并更新），目录移入 archive，合并回 main，归档后全量门禁复跑 FAIL=0。推送另行授权。
