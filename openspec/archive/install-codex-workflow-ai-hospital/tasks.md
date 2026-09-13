# 任务范围

## 1. 规范确认

- [x] 1.1 用户确认本四件套及外部目标写入边界。

## 2. 独立计划

- [x] 2.1 产出严格模式实施计划并等待第二次确认。

## 3. 写入前保护

- [x] 3.1 重新解析真实路径并确认目标仍不是 Git 仓库。
- [x] 3.2 复核目标工作流入口不存在且没有 Claude 适配残留。
- [x] 3.3 复核 `docs/好实用合作协议I51.2.doc` SHA-256。
- [x] 3.4 重新执行安装器 dry-run 并确认仍为 55 个 CREATE、0 个 UPDATE。
- [x] 3.5 用户确认 `fuseblk` 文件系统的空父目录预创建适配；确认前不重试安装。
- [x] 3.6 用户确认修正后的 37 个空父目录集合；确认前不继续创建或安装。

## 4. 目标安装

- [x] 4.1 用真实路径和 `--assistant codex` 执行离线安装。
- [x] 4.2 确认安装台账、Codex 入口和共享资产存在。
- [x] 4.3 确认 `.claude/`、`CLAUDE.md` 和 `.git` 未被创建。

## 5. 目标验证

- [x] 5.1 执行安装器幂等 dry-run，确认 55 个资产均为 unchanged。
- [x] 5.2 运行 `bash scripts/validate-workflow.sh --require-openspec`。
- [x] 5.3 运行 `openspec validate --all --strict --no-interactive`。
- [x] 5.4 复核用户文档 SHA-256 与权限不变。
- [x] 5.5 检查完整文件清单与目标 diff，确认无计划外写入。

## 6. 审查与收尾

- [x] 6.1 完成严格模式任务级审查。
- [x] 6.2 完成 Verify 规格符合性与代码质量两个独立关注面审查。
- [x] 6.3 通过归档门禁并沉淀必要知识。

## 7. 归档终证

- 最终 manifest ID：`0f9272dc1737c5e26c30cba6938f465187b9beb27654d7eae8a757ebba121917`。
- comparison base：输入 `main`，解析为 `1fbad77089b52c424bc06c3b0759048d4618ef9e`。
- finding 状态：`resolved=1`（Minor `verify-quality-001`），`open=0`，`not-an-issue=0`，`accepted-risk=0`；Critical/Important 均为 0。
- 未验证范围：目标非 Git 且未做并发写入监控；`fuseblk` mount ACL 与其他本地用户写权限未审计；未重放最初安装过程；未读取用户合作文档正文。
- 残余风险：目标后续仍可能被外部进程修改；文件系统呈现宽权限，实际跨用户可写性未证明；源 feature/worktree 的合并、推送或清理尚未执行。
