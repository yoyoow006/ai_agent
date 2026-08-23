# 移除安装工具仓库业务知识实施计划

## 目标与全局约束

- 目标是从安装工具源码仓库的当前树和全部 reachable Git 历史中移除指定业务项目知识，同时保留安装器通用能力与空白项目登记骨架。
- 用户已选择方案 2：不迁移、不备份、不另存。
- 不添加 remote、不推送、不创建 pack、不访问外部系统。
- 本变更是纯文档、registry 与 Git 元数据操作，不修改安装器运行时代码和 `scripts/ai-workflow-assets/`。
- 严格模式通常默认额外 worktree；本任务必须重写当前仓库共享对象库和 `main` root 历史，额外 worktree 会保留旧引用并增加回流风险。因此在当前工作区使用 feature 分支执行，最终把 `main` 替换为净化 root。此例外由本计划显式声明。

## 任务 1：提交严格流程产物并建立实施分支

### Modify

- `openspec/changes/remove-installer-business-knowledge/proposal.md`：状态改为`构建中`。
- `openspec/changes/remove-installer-business-knowledge/tasks.md`：只勾选已完成流程项。

### Commands

```bash
git status --short --branch
git remote -v
git switch -c feature/remove-installer-business-knowledge
git add openspec/changes/remove-installer-business-knowledge openspec/plan/remove-installer-business-knowledge.md
git diff --cached --name-status
git commit -m "chore: plan installer knowledge separation"
```

### Expected

- 除本严格变更四件套与计划外，无其他未提交修改。
- `git remote -v` 为空。
- feature 提交只包含流程产物。

## 任务 2：删除业务文件并恢复通用骨架

### Delete

删除以下 tracked 业务文件：

```text
.ai/kb/contracts/willing-sign-frontend.md
.ai/kb/projects/api-service.md
.ai/kb/projects/crm.md
.ai/kb/projects/pms-core.md
.ai/kb/projects/pms-hpc.md
.ai/kb/projects/pms.md
.ai/kb/projects/sua.md
.ai/kb/projects/tapp.md
.ai/kb/projects/yuxiaor-e-signature.md
.ai/kb/projects/yuxiaor-pms.md
.ai/kb/projects/yuxiaor-xxljob.md
.ai/memory/api-server.md
.ai/memory/yuxiaor-server.md
REVIEW.md
pms-vs.code-workspace
```

### Modify

- `.ai/kb/projects/registry.json` 写为：

```json
{
  "schema_version": 1,
  "projects": []
}
```

- `.ai/kb/overview.md`
  - 保留工作流组成、风险模式、共享底线、事实查询与审查证据。
  - 删除“模块速查”、业务模块表和项目定位映射。
- `.ai/rules/index.md`
  - 保留工作流、安装器、共享知识、项目登记、OpenSpec、校验器、忽略规则和 Git 基线安全路由。
  - 删除最后三行业务模块路由。
- `.ai/tools/README.md`
  - 将三个事实查询示例改为：

```bash
python3 .ai/tools/project_facts.py project-context --workspace /path/to/workspace --project example-project
python3 .ai/tools/project_facts.py server-registry --workspace /path/to/workspace --server example-server --project example-project
python3 .ai/tools/project_facts.py workspace-search --workspace /path/to/workspace --project example-project --text ExampleSymbol --limit 20 --offset 0
```

- `.ai/memory/workflow.md`
  - 删除两条业务来源记录：`document-willing-sign-frontend-integration` 与 `extend-willing-sign-frontend-integration-docs`。
  - 保留通用 patch、worktree、安装器、工作流和 Git 基线安全经验。
- `.gitignore` 增加源仓库专用防回流规则：

```gitignore
/.ai/kb/contracts/
/.ai/kb/projects/*
!/.ai/kb/projects/README.md
!/.ai/kb/projects/registry.json
/.ai/memory/*
!/.ai/memory/README.md
!/.ai/memory/workflow.md
/REVIEW.md
/*.code-workspace
```

### Content verification

```bash
python3 - <<'PY'
import json
from pathlib import Path

removed = [
    ".ai/kb/contracts/willing-sign-frontend.md",
    ".ai/kb/projects/api-service.md",
    ".ai/kb/projects/crm.md",
    ".ai/kb/projects/pms-core.md",
    ".ai/kb/projects/pms-hpc.md",
    ".ai/kb/projects/pms.md",
    ".ai/kb/projects/sua.md",
    ".ai/kb/projects/tapp.md",
    ".ai/kb/projects/yuxiaor-e-signature.md",
    ".ai/kb/projects/yuxiaor-pms.md",
    ".ai/kb/projects/yuxiaor-xxljob.md",
    ".ai/memory/api-server.md",
    ".ai/memory/yuxiaor-server.md",
    "REVIEW.md",
    "pms-vs.code-workspace",
]
existing = [path for path in removed if Path(path).exists()]
if existing:
    raise SystemExit(f"designated business paths remain: {existing}")
registry = json.loads(Path(".ai/kb/projects/registry.json").read_text(encoding="utf-8"))
assert registry == {"schema_version": 1, "projects": []}
print("designated_paths=0 registry_projects=0")
PY

if grep -nE 'yuxiaor|pms-hpc|api-service|willing-sign' \
  .ai/kb/overview.md .ai/rules/index.md .ai/tools/README.md .ai/memory/workflow.md; then
  echo "business terms remain in shared workflow documents" >&2
  exit 1
fi
grep -Fq -- '--project example-project' .ai/tools/README.md
grep -Fq -- '--server example-server --project example-project' .ai/tools/README.md
grep -Fq -- '--text ExampleSymbol' .ai/tools/README.md
git diff --check
```

### Expected

- designated 路径全部不存在。
- registry 为空。
- overview/rules/tools 中没有业务模块路由或业务查询示例；工具示例使用 `example-project` / `ExampleSymbol`。
- memory 中两条业务来源记录不存在，通用经验保留。
- `git diff --check` 退出码 0。

### Commit

```bash
git add -A .ai REVIEW.md pms-vs.code-workspace .gitignore
git diff --cached --name-status
git diff --cached --check
git commit -m "docs: separate installer workflow from project knowledge"
```

## 任务 3：内容与资产契约验证

### Commands

```bash
python3 -B -m unittest discover -v -s .ai/tools/tests -p 'test_*.py'
python3 -B -m unittest -v \
  scripts.tests.test_install_ai_workflow.PortableAssetManifestTests \
  scripts.tests.test_install_ai_workflow.PortableAssetContentTests
python3 -B -m json.tool .ai/kb/projects/registry.json
bash scripts/install-ai-workflow.sh --help
```

### Expected

- 事实工具测试全部通过。
- 安装器资产 manifest 与内容契约测试全部通过。
- registry JSON 可解析。
- 安装器 help 退出码 0 且 stderr 为空。

## 任务 4：内容变更任务级审查

### Freeze

```bash
python3 .ai/tools/review_manifest.py freeze \
  --change remove-installer-business-knowledge \
  --workspace "$PWD" \
  --repo-spec "$PWD::main" \
  --output .ai-local/reviews/remove-installer-business-knowledge/task-1.json
```

### Review

- 独立 reviewer 在读取范围前和结论前分别运行：

```bash
python3 .ai/tools/review_manifest.py verify \
  --manifest .ai-local/reviews/remove-installer-business-knowledge/task-1.json
```

- 审查范围为 `main..feature/remove-installer-business-knowledge`。
- 必须核对：删除清单完整、通用能力保留、mixed 文件业务段落移除、防回流规则有效、不修改安装器资产、不引入新的业务或敏感内容。
- Critical/Important 必须最小修复并做 delta manifest 复审；未归零不得进入历史重建。

## 任务 5：历史重建前置检查

### Status update

- 将严格 proposal 置为`待验证`，勾选已完成实施项，保留最终验证与收尾项。
- 暂存并提交状态更新，确保后续 root tree 包含完整 OpenSpec 状态。

### Commands

```bash
git status --short --branch
git remote -v
git log --oneline --decorate --all
bash scripts/install-ai-workflow.sh --help
openspec validate --all --no-interactive
```

### Expected

- 工作区仅包含 OpenSpec 状态更新。
- 无 remote。
- 安装器 help 正常。
- OpenSpec 全部通过。

## 任务 6：重建净化 root 并移除旧历史

### Preconditions

- 任务 4 无未决 Critical/Important。
- 任务 5 全部通过。
- 当前分支为 `feature/remove-installer-business-knowledge`，工作区 clean。

### Commands

```bash
old_main=$(git rev-parse main)
tree=$(git rev-parse feature/remove-installer-business-knowledge^{tree})
new_root=$(git commit-tree "$tree" -m "chore: initialize installer-only workflow repository")
git update-ref refs/heads/main "$new_root" "$old_main"
git switch main
git branch -D feature/remove-installer-business-knowledge
git reflog expire --expire=now --expire-unreachable=now --all
git gc --prune=now
```

### Expected

- `main` 指向新的 installer-only root commit。
- feature 分支删除。
- 工作区 clean。
- `git log --oneline --all` 不显示旧 root 或 feature 提交。
- 旧提交对象查询失败。

## 任务 7：最终验证

### Current tree and reachable history

```bash
python3 - <<'PY'
import json
import subprocess
from pathlib import Path

removed = [
    ".ai/kb/contracts/willing-sign-frontend.md",
    ".ai/kb/projects/api-service.md",
    ".ai/kb/projects/crm.md",
    ".ai/kb/projects/pms-core.md",
    ".ai/kb/projects/pms-hpc.md",
    ".ai/kb/projects/pms.md",
    ".ai/kb/projects/sua.md",
    ".ai/kb/projects/tapp.md",
    ".ai/kb/projects/yuxiaor-e-signature.md",
    ".ai/kb/projects/yuxiaor-pms.md",
    ".ai/kb/projects/yuxiaor-xxljob.md",
    ".ai/memory/api-server.md",
    ".ai/memory/yuxiaor-server.md",
    "REVIEW.md",
    "pms-vs.code-workspace",
]
existing = [path for path in removed if Path(path).exists()]
if existing:
    raise SystemExit(f"designated business paths remain in worktree: {existing}")
registry = json.loads(Path(".ai/kb/projects/registry.json").read_text(encoding="utf-8"))
assert registry == {"schema_version": 1, "projects": []}
revisions = subprocess.check_output(["git", "rev-list", "--all"], text=True).splitlines()
findings = []
for revision in revisions:
    listing = subprocess.check_output(
        ["git", "ls-tree", "-r", "--name-only", revision], text=True
    ).splitlines()
    matches = sorted(set(removed).intersection(listing))
    if matches:
        findings.append((revision, matches))
if findings:
    raise SystemExit(f"designated business paths remain in reachable history: {findings}")
print(
    f"designated_current_paths=0 registry_projects=0 "
    f"scanned_reachable_commits={len(revisions)} designated_history_paths=0"
)
PY

git rev-parse --is-inside-work-tree
git branch --show-current
git remote -v
git status --short --branch
git fsck --full
```

### Workflow verification

```bash
python3 -B -m unittest discover -v -s .ai/tools/tests -p 'test_*.py'
python3 -B -m unittest -v \
  scripts.tests.test_install_ai_workflow.PortableAssetManifestTests \
  scripts.tests.test_install_ai_workflow.PortableAssetContentTests
bash scripts/install-ai-workflow.sh --help
openspec validate --all --no-interactive
bash scripts/validate-workflow.sh --require-openspec
```

### Expected

- 当前树和全部 reachable 历史都没有 designated 业务路径。
- registry 为空。
- 分支为 `main`，remote 为空，status clean。
- `git fsck --full` 退出码 0。
- 事实工具、安装器资产契约、安装器 help、OpenSpec 和严格工作流门禁全部通过。

## 任务 8：状态提交与双阶段 Verify

### Status update

- 将严格 proposal 置为`待归档`。
- 勾选全部已完成任务。
- 提交状态更新。

### Independent reviews

- 以 installer-only root 为 comparison base，冻结最终 manifest。
- Reviewer A 只审规格符合性：逐条核对 Requirements/Scenarios、两次确认、不可逆删除边界和 OpenSpec 状态。
- Reviewer B 只审仓库质量：当前树与 reachable 历史 designated 路径扫描、通用能力保留、ignore 防回流、Git 对象清理、测试证据和残余风险。
- 两个 reviewer 读取范围前和结论前均运行 manifest verify；任一 `STALE` 立即停止。

## 任务 9：归档

- 双阶段 Verify 无未决 Critical/Important 后，按 Archive 技能执行：
  - 合并 `installer-knowledge-separation` delta 到主规格；
  - 归档严格变更目录与独立计划；
  - proposal 状态置为`已归档`；
  - 提交归档结果；
  - 复跑 `openspec validate --all --no-interactive` 与 `bash scripts/validate-workflow.sh --require-openspec`。
- 最终汇报必须明确：指定业务内容已按用户选择永久移除，未创建迁移或备份。
