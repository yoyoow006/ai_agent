# Build 审查与验证记录

## 任务级审查

- 最终任务级 manifest ID：`ed8a806b9ed69a9cd4aea0a91a133ff9f41eebf1503930aa2482552907140255`
- comparison base：`main` / merge-base `9122102074df77d02b385b3b31ac3143440735aa`
- 审查 HEAD：`2288115`

### 单元 A：多仓 registry、项目上下文与 Git 基线边界

- 初审发现：
  - `A-1-git-baseline-escapes-workspace` Important：`.git` symlink/gitfile 可读取 workspace 外 Git 元数据。
  - 复审补充：workspace 内 `.git` 目录可通过外部 `commondir` 获得外部 HEAD。
  - `A-2-git-config-fsmonitor-command-execution` Critical：Git config include + `core.fsmonitor` 可在 `workspace-search` 中执行脚本。
- 修复提交：
  - `a519cb8`：基础 Git metadata 边界与证据复用语义修复。
  - `4286a05`：覆盖 commondir、alternates、内部 symlink 与外部 `GIT_*` 环境。
  - `2288115`：最高优先级禁用 fsmonitor/hooks/外部 attributes/excludes/pager，并固定 global/system config。
- 最终复审：PASS；A-1、A-2 均 resolved，无未决 Critical/Important。

### 单元 B：验证证据复用、OpenSpec 状态与知识分层

- 初审发现：
  - `F-B1` Important：证据复用条件曾允许 HEAD 漂移但输入未变时复用，与规格和失效条件冲突。
- 修复：统一为“当前项目 HEAD 等于证据 commit，且相关登记输入指纹未变化”。
- 最终复审：PASS；F-B1 resolved，无未决 Critical/Important。
- 确认证据复用不是任务状态，不替代 OpenSpec，不削弱当前任务完成前新鲜验证。

## Build 验证

- `python3 -B -m unittest discover -v -s .ai/tools/tests -p 'test_*.py'`：63 tests，OK。
- `python3 -B -m unittest -v scripts.tests.test_validate_workflow`：201 tests，OK。
- `python3 -B -m unittest -v scripts.tests.test_install_ai_workflow`：89 tests，OK。
- `python3 -B -m unittest -v scripts.tests.test_install_workflow`：8 tests，OK。
- `bash scripts/validate-workflow.sh --require-openspec`：PASS=200 FAIL=0 SKIP=0。
- `openspec validate --all --strict --no-interactive`：11 passed，0 failed。
- `git diff --check`：通过。

## finding 状态

- Critical：0 open / 1 resolved。
- Important：0 open / 2 resolved。
- Minor：0 open / 0 total。

## 未验证范围

- 未穷尽 Git 所有平台版本和历史配置向量；当前覆盖工具实际调用的 `rev-parse` / `ls-files` 路径和已识别执行面。
- 未模拟并发替换 `.git` 元数据的 TOCTOU 对抗场景。
- 未使用真实外部业务项目 registry 或外部日志做端到端证据复用。
- 未验证目标项目证据文档正文质量；源 registry 与安装资产 registry 均保持空数组。

## 残余风险

- 依赖与验证声明可能过期，仍需目标维护者从权威源码、构建清单和契约复核。
- `verified_commit=current` 只说明 HEAD 与登记基线一致，不覆盖 dirty worktree，也不代表当前任务通过。
- Git 本地 config 仍会被解析；已知执行/外扩路径已被命令行最高优先级覆盖，未来 Git 新执行机制需重新评估。
