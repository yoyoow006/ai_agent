# 任务清单

- [x] 1.1 在 `scripts/tests/test_install_ai_workflow.py` 增加辅助 `_git_index_mode(relpath)`（`git -C <repo> ls-files -s -- <path>`，返回 0o644/0o755/None），先写未跟踪 fail-fast 与索引模式比对的用例并确认红（本机现状 ：236 环境红即是缺陷红，直接作为 1.2 的红证据）。
- [x] 1.2 重写 `test_manifest_modes_are_exact_and_match_files`：manifest 声明 == git 索引规范模式（未跟踪 fail-fast）+ 工作树可执行位一致性；同步处理 `test_parallel_runner_asset_is_manifested_and_byte_identical` 的 `0o644` stat 断言。
- [x] 1.3 反向锁定：临时改一个资产的索引模式（chmod + git add）确认红后还原；本机与干净 worktree 探针各跑一次 `PortableAssetManifestTests` 全类确认绿。
- [x] 1.4 required 层验证（后台）：`bash scripts/validate-workflow.sh --require-openspec`、`openspec validate asset-manifest-mode-assertion-env-robust --strict --no-interactive`、`git diff --check`，逐项读取退出码。

## 本地整合策略

- 分支/worktree：主会话 feature 分支 `fix/manifest-mode-assertion-env-robust`（基于 main）；无未提交修改冲突，不建 worktree。
- 提交边界：单一测试修复职责单元一次提交；默认不推送、不合并，整合方式由用户在 Verify/Archive 后裁定。
- 外部副作用授权：无外部副作用；探针 worktree 用后即删。

## Verify 综合自查终局记录（2026-11-09，标准小任务）

- summary: SUMMARY change=asset-manifest-mode-assertion-env-robust mode=标准 status=待归档 unchecked=0/4 head=2c4d6ea rules=c1f51966572f
- 测试证据：required 门禁 PASS=284 FAIL=0 SKIP=0（gate_rc=0）；openspec validate --strict valid；git diff --check clean；完整 `test_install_ai_workflow.py` 套件 90 passed + 172 subtests（0:05:49，含此前环境性失败用例现绿、无 pycache 瞬态）；本机 PortableAssetManifestTests 4 passed。
- diff 范围：单文件 `scripts/tests/test_install_ai_workflow.py` +38/-5（git_index_mode 辅助 + 两处断言重写）+ 本变更 OpenSpec 产物；无镜像（该测试文件不随资产分发）。
- finding 状态：无 open finding（本变更即缺陷修复自身；反向锁定证明断言有效咬合：临时索引 100644 → `git index mode drift` 精准红，还原后绿）。
- 未验证范围：非 sharedRepository 规范环境未直接执行——断言逻辑环境无关（git 索引 + 可执行位），干净 worktree 探针在 2026-11-06 已证明该环境路径，本变更后断言不再触碰环境敏感位。
- 残余风险：`core.fileMode=false` 场景下 git 索引不反映磁盘模式（本仓未启用；可执行位断言兜底）；枚举断言的 `__pycache__` 瞬态未在本变更处理（单独运行与全套件本次均绿，保持观察）。
