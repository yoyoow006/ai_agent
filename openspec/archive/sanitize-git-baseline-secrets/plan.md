# 清理 Git 基线凭据实施计划

## 目标与全局约束

- 清除 tracked 知识库正文和全部 reachable Git 历史中的两处已确认凭据形态，同时保留仓库的工作流、OpenSpec、安装器和业务知识功能。
- 全程不得把被发现的凭据字面值写入新的文档、计划、提交信息、命令输出或 review 记录。
- 不添加 remote、不推送、不创建 pack、不访问外部凭据系统，不声称凭据未泄露或已轮换。
- 历史重建只处理当前两个本地提交：`62a92d774c6068a0902f9c2f6a2d8c39a1894129` 与 `4e197a777672c7acf23842a795bf3a5c424cc3b5`。执行前 `git remote -v` 必须为空。
- 本变更是纯文档与 Git 元数据操作，不修改运行时代码；使用内容契约、Secret 扫描、Git 完整性和工作流回归验证，不使用形式化 TDD。
- 严格模式通常默认额外 worktree；本任务必须清理共享对象库和当前 `main` 的 root 历史，额外 worktree 会保留旧引用并增加泄露面。因此在当前工作区使用 feature 分支执行，最终把 `main` 替换为净化 root。此例外由本计划显式声明。

## 任务 1：提交严格流程产物并建立实施分支

### Modify

- `openspec/changes/sanitize-git-baseline-secrets/proposal.md`：状态改为`构建中`。
- `openspec/changes/sanitize-git-baseline-secrets/tasks.md`：只勾选已完成流程项。

### Commands

```bash
git status --short --branch
git remote -v
git switch -c feature/sanitize-git-baseline-secrets
git add openspec/changes/sanitize-git-baseline-secrets openspec/plan/sanitize-git-baseline-secrets.md
git diff --cached --name-status
git commit -m "chore: plan sanitized git baseline"
```

### Expected

- 除本严格变更四件套与计划外，无其他未提交修改。
- `git remote -v` 为空。
- feature 提交只包含流程产物，不包含新的凭据字面值。

## 任务 2：脱敏知识库并修复任务格式

### Modify

- `.ai/kb/projects/pms-core.md`
  - 将 Nexus 上传账号示例改为“Nexus 上传账号/密码（已脱敏）”。
  - 保留“各 yml 明文密钥勿外泄、勿打印日志”的告警语义。
- `.ai/kb/projects/pms.md`
  - 将数据库/RabbitMQ/第三方明文凭据示例改为“凭据示例已脱敏”。
  - 保留“不要把它们复制到对话、commit message 或 PR”的告警语义。
- `openspec/changes/initialize-git-repository/tasks.md`
  - 按节编号所有 checkbox：1.1–1.3、2.1–2.3、3.1–3.4、4.1–4.7、5.1–5.2。
- `.ai/memory/workflow.md`
  - 追加来源变更 `sanitize-git-baseline-secrets`：创建 Git root 前必须先做 secret scan；初始提交后才发现凭据时，必须同时清理当前树和 unreachable 历史，并提示外部轮换。

### Content verification

```bash
git grep -nI -E 'deployment[0-9]+|yxr[0-9]+' -- .ai/kb
grep -nE '已脱敏|勿外泄|不要把它们复制到对话' .ai/kb/projects/pms-core.md .ai/kb/projects/pms.md
grep -nE '^- \[[ x]\] [1-5]\.[1-9][0-9]* ' openspec/changes/initialize-git-repository/tasks.md
git diff --check
```

### Expected

- 第一条 `git grep` 退出码为 1 且无输出。
- 脱敏告警与编号 checkbox 检查均有匹配。
- `git diff --check` 退出码为 0。

### Commit

```bash
git add .ai/kb/projects/pms-core.md .ai/kb/projects/pms.md openspec/changes/initialize-git-repository/tasks.md .ai/memory/workflow.md
git diff --cached --check
git commit -m "docs: sanitize workflow knowledge credentials"
```

## 任务 3：内容变更任务级审查

### Freeze

```bash
python3 .ai/tools/review_manifest.py freeze \
  --change sanitize-git-baseline-secrets \
  --workspace "$PWD" \
  --repo-spec "$PWD::main" \
  --output .ai-local/reviews/sanitize-git-baseline-secrets/task-1.json
```

### Review

- 独立 reviewer 在读取范围前和结论前分别运行：

```bash
python3 .ai/tools/review_manifest.py verify \
  --manifest .ai-local/reviews/sanitize-git-baseline-secrets/task-1.json
```

- 审查范围为 `main..feature/sanitize-git-baseline-secrets`。
- 审查内容：脱敏完整性、告警语义、tasks 编号、是否引入新敏感值、是否超出计划。
- Critical/Important 必须最小修复并做 delta manifest 复审；未归零不得进入历史重建。

## 任务 4：历史重建前置检查

### Status update

- 任务级审查通过后，将严格 proposal 置为`待验证`，勾选已完成实施项，保留最终验证与收尾项。
- 暂存并提交上述状态更新与必要的计划执行澄清，确保任务 5 使用的 feature tree 已包含完整 OpenSpec 状态。

### Commands

```bash
git status --short --branch
git remote -v
git log --oneline --decorate --all
git grep -nI -E 'deployment[0-9]+|yxr[0-9]+' -- .ai/kb
bash scripts/install-ai-workflow.sh --help
openspec validate --all --no-interactive
```

### Expected

- 工作区仅包含 OpenSpec 状态更新。
- 无 remote。
- 当前树 secret scan 无匹配。
- 安装器 help 退出码 0、stderr 为空。
- OpenSpec 全部通过。

## 任务 5：重建净化 root 并移除旧历史

### Preconditions

- 任务 3 无未决 Critical/Important。
- 任务 4 全部通过。
- 当前分支为 `feature/sanitize-git-baseline-secrets`，工作树已脱敏。

### Commands

```bash
old_main=$(git rev-parse main)
tree=$(git rev-parse feature/sanitize-git-baseline-secrets^{tree})
new_root=$(git commit-tree "$tree" -m "chore: initialize sanitized AI workflow repository")
git update-ref refs/heads/main "$new_root" "$old_main"
git switch main
git branch -D feature/sanitize-git-baseline-secrets
git reflog expire --expire=now --expire-unreachable=now --all
git gc --prune=now
```

### Expected

- `main` 指向新的净化 root commit。
- feature 分支删除。
- `git status --short --branch` 为 clean。
- `git log --oneline --all` 不显示旧两个提交或 feature 提交。
- 两个旧提交的 `git cat-file -e <commit>^{commit}` 均失败。

## 任务 6：最终验证

### Git 与 secret 验证

```bash
git rev-parse --is-inside-work-tree
git branch --show-current
git remote -v
git status --short --branch
git fsck --full
git grep -nI -E 'deployment[0-9]+|yxr[0-9]+' -- .ai/kb
python3 - <<'PY'
import subprocess

pattern = "deployment[0-9]+|yxr[0-9]+"
revisions = subprocess.check_output(["git", "rev-list", "--all"], text=True).splitlines()
findings = []
for revision in revisions:
    result = subprocess.run(
        ["git", "grep", "-I", "-E", pattern, revision, "--", ".ai/kb"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode == 0:
        findings.append((revision, result.stdout))
if findings:
    raise SystemExit("secret pattern remains in reachable history")
print(f"scanned_reachable_commits={len(revisions)} secret_findings=0")
PY
```

### Workflow verification

```bash
bash scripts/install-ai-workflow.sh --help
openspec validate --all --no-interactive
bash scripts/validate-workflow.sh
```

### Expected

- 分支为 `main`，remote 为空，status clean。
- `git fsck --full` 退出码 0。
- 当前树与全部 reachable 历史均无已确认凭据形态。
- 安装器 help 退出码 0 且 stderr 为空。
- OpenSpec 全部通过。
- 工作流校验末尾 `FAIL=0`。

## 任务 7：状态提交与双阶段 Verify

### Status update

- 将严格 proposal 置为`待归档`。
- 勾选全部已完成任务；外部凭据轮换保持用户责任，不标记为由本仓库完成。
- 提交状态更新。

### Independent reviews

- 以 sanitized root 为 comparison base，冻结最终 manifest。
- Reviewer A 只审规格符合性：逐条核对 Requirements/Scenarios、破坏性授权、凭据轮换边界和 OpenSpec 状态。
- Reviewer B 只审仓库质量：当前树与 reachable 历史扫描、Git 对象清理、忽略规则、工作流验证和残余风险。
- 两个 reviewer 读取范围前和结论前均运行 manifest verify；任一 `STALE` 立即停止。

## 任务 8：归档

- 双阶段 Verify 无未决 Critical/Important 后，按 Archive 技能执行：
  - 合并 `git-baseline-secret-hygiene` delta 到主规格；
  - 归档严格变更目录与独立计划；
  - proposal 状态置为`已归档`；
  - 提交归档结果；
  - 复跑 `openspec validate --all --no-interactive` 与 `bash scripts/validate-workflow.sh`。
- 最终汇报必须明确：本地 Git 清理完成不证明凭据未泄露；如凭据可能已在仓库外出现，用户必须自行轮换。
