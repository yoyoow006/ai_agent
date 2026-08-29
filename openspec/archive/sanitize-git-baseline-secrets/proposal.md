# 清理 Git 基线中的知识库凭据

模式: 严格
状态: 已归档

## Why

Git 初始化后的独立综合审查发现 `.ai/kb/projects/pms-core.md` 与 `.ai/kb/projects/pms.md` 含有两处字面账号/密码示例。它们已进入本地 root commit 与当前提交的 Git 对象历史。当前 `git remote -v` 为空，未发现该仓库已外传的证据，但未来 push、clone、pack 传输或备份都会暴露这些内容。

该处理涉及安全合规与本地 Git 历史重建，按仓库风险路由必须从原初始化任务升级为严格模式。历史重建会丢弃刚刚生成的两个本地提交并建立净化后的新基线，属于破坏性操作，必须获得用户明确授权。

## What Changes

- 将两处知识库文档中的字面凭据替换为不泄露值的占位描述，保留“不要外泄/不要复制”的安全语义。
- 修复 `initialize-git-repository` tasks 的编号格式，满足仓库 artifact 契约。
- 在用户确认后产出严格模式独立实现计划，再执行本地历史重建：
  - 以净化后的当前工作树建立新的 sanitized root commit；
  - 移除旧 main 引用与可达历史；
  - 清理 reflog 并修剪不可达对象，使旧凭据对象不再随常规 Git 操作传输。
- 复核仓库结构、OpenSpec、工作流校验和 Git 对象完整性。
- 不添加 remote、不推送、不访问凭据提供方；凭据轮换由用户在外部系统自行决定并执行。

## Impact

- 受影响文件：`.ai/kb/projects/pms-core.md`、`.ai/kb/projects/pms.md`、`openspec/changes/initialize-git-repository/tasks.md`，以及本地 Git 历史。
- 破坏性影响：丢弃当前两个本地提交 `62a92d7`、`4e197a7`，用净化后的新基线替代；提交哈希会改变。
- 安全影响：降低本仓库后续传输泄露风险；不能证明凭据从未通过其他渠道暴露，也不能替代外部凭据轮换。
- 运行时影响：不修改安装器代码、资产清单或业务系统。

## Verification Evidence

- 任务级内容审查通过，manifest `97444b9525a8c96395c3e58dc155adb2bfe04317d04c3a5679964e3556163be9`。
- 净化 root：`1ab208b6c77bbf9a9389ba16232f995d78048b94`；当前分支为 `main`，`git remote -v` 为空。
- 旧提交 `62a92d774c6068a0902f9c2f6a2d8c39a1894129` 与 `4e197a777672c7acf23842a795bf3a5c424cc3b5` 的对象查询均失败，说明已从本地对象库修剪。
- 当前 `.ai/kb` 已确认凭据形态扫描退出码 1；全部 reachable 历史扫描 `secret_findings=0`。
- `git fsck --full` 退出码 0，工作区 clean。
- `bash scripts/install-ai-workflow.sh --help` 退出码 0，stderr 为空。
- `openspec validate --all --no-interactive` 输出 5 passed、0 failed。
- `bash scripts/validate-workflow.sh` 输出 `PASS=169 FAIL=0 SKIP=0`。
- 已向用户明确汇报：本地清理不证明凭据未曾外泄，外部轮换由用户在对应系统自行决定和执行。
