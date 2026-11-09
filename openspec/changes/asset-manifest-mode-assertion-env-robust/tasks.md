# 任务清单

- [ ] 1.1 在 `scripts/tests/test_install_ai_workflow.py` 增加辅助 `_git_index_mode(relpath)`（`git -C <repo> ls-files -s -- <path>`，返回 0o644/0o755/None），先写未跟踪 fail-fast 与索引模式比对的用例并确认红（本机现状 ：236 环境红即是缺陷红，直接作为 1.2 的红证据）。
- [ ] 1.2 重写 `test_manifest_modes_are_exact_and_match_files`：manifest 声明 == git 索引规范模式（未跟踪 fail-fast）+ 工作树可执行位一致性；同步处理 `test_parallel_runner_asset_is_manifested_and_byte_identical` 的 `0o644` stat 断言。
- [ ] 1.3 反向锁定：临时改一个资产的索引模式（chmod + git add）确认红后还原；本机与干净 worktree 探针各跑一次 `PortableAssetManifestTests` 全类确认绿。
- [ ] 1.4 required 层验证（后台）：`bash scripts/validate-workflow.sh --require-openspec`、`openspec validate asset-manifest-mode-assertion-env-robust --strict --no-interactive`、`git diff --check`，逐项读取退出码。

## 本地整合策略

- 分支/worktree：主会话 feature 分支 `fix/manifest-mode-assertion-env-robust`（基于 main）；无未提交修改冲突，不建 worktree。
- 提交边界：单一测试修复职责单元一次提交；默认不推送、不合并，整合方式由用户在 Verify/Archive 后裁定。
- 外部副作用授权：无外部副作用；探针 worktree 用后即删。
