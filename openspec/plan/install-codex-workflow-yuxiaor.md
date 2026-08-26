# 独立实施计划：安装 Codex 工作流到 yuxiaor_prj_2025

## 全局约束

- 源工作区：`/media/shitou/石头/wksource/git_me_prj/ai_agent/.worktrees/install-codex-workflow-yuxiaor`，分支 `feature/install-codex-workflow-yuxiaor`。
- 目标真实根目录：`/media/shitou/石头/wksource/yuxiaor_prj_2025`。不得把 `/home/shitou/workspace/src/yuxiaor_prj_2025` 传给安装器，因为其中 `/home/shitou/workspace/src` 是符号链接。
- 只安装 Codex 单侧适配；不安装 `.claude/`，不修改目标现有 `CLAUDE.md`、`REVIEW.md`、`docs/`、`.idea/` 或任何嵌套业务仓库。
- 不联网、不安装依赖、不在目标执行 `git init`、提交、推送或远程操作。
- 目标旧 `AGENTS.md` 必须先重命名为 `AGENTS.pre-codex-workflow.md`，不得合并或覆盖旧内容。
- 所有目标写入命令需要用户本计划的第二次确认；安装器失败时不手工删除未知内容。
- OpenSpec CLI 版本为 1.3.1；严格验证不得把 OpenSpec 项记为 `SKIP`。

## 固定身份

| 对象 | 期望 SHA-256 | 说明 |
|---|---|---|
| 目标旧 `AGENTS.md` | `74d7b6cd7d755cb07b04f205e5b6beef9ca7c7412379c2bbd9db166f1bac47cc` | 安装前与备份后必须一致 |
| 安装清单中的新 `AGENTS.md` | `961dbcbb03b2311656d155818a80cbdca57ad6b15e8ed70eee0061d1207bfe71` | 安装后必须一致 |
| 目标安装前 `.gitignore` | `bec10e5dc357805b65436e39e33433be69f6366bd88d336ffb1c94b69b6b581f` | 473 字节 |
| 目标安装后 `.gitignore` | `0cd57481fa44d1d0a42baedcca91bea7078982f3ad9345315aa7990c96df9889` | 604 字节，只追加一个受管块 |
| 目标 `CLAUDE.md` | `0aaefece9c24a67288c16760ddad79d30f395537dc50a1c8c23fcbabde5366fc` | 保持不变 |
| 目标 `REVIEW.md` | `624d52371c932b3699c01e84956f6f91bbd446f84608c9b954876f1b7d332f35` | 保持不变 |
| 生成的 `.ai/assistant-profile.json` | `27e9b41320f1df7479e2dcb81605c3c260108214c0055c2b99b5eae69908d289` | 内容为 Codex profile v1 |

## Task 0：固化已确认计划并建立干净构建基线

**Modify**

- `openspec/changes/install-codex-workflow-yuxiaor/proposal.md`：状态改为`构建中`。
- `openspec/changes/install-codex-workflow-yuxiaor/tasks.md`：勾选第二次确认。

**Execute**

```bash
cd /media/shitou/石头/wksource/git_me_prj/ai_agent/.worktrees/install-codex-workflow-yuxiaor
git add openspec/changes/install-codex-workflow-yuxiaor openspec/plan/install-codex-workflow-yuxiaor.md
git commit -m "chore(workflow): plan codex installation"
bash scripts/validate-workflow.sh --require-openspec
git status --short --branch
```

**Expected**

- 本地提交只包含四件套与独立计划，不推送。
- required 工作流门禁最终精确输出 `PASS=169 FAIL=0 SKIP=0`。
- 提交后工作区除本计划允许的后续 evidence/finding 文件外保持干净。

## Task 1：安装前目标与嵌套仓边界快照

**Create**

- `openspec/changes/install-codex-workflow-yuxiaor/evidence/nested-repos-before.sha256`
- `openspec/changes/install-codex-workflow-yuxiaor/evidence/preflight.txt`

**Execute**

```bash
SOURCE='/media/shitou/石头/wksource/git_me_prj/ai_agent/.worktrees/install-codex-workflow-yuxiaor'
TARGET='/media/shitou/石头/wksource/yuxiaor_prj_2025'

set -euo pipefail

mkdir -p "$SOURCE/openspec/changes/install-codex-workflow-yuxiaor/evidence"

python3 -B - "$TARGET" <<'PY'
from pathlib import Path
import sys

target = Path(sys.argv[1])
current = Path(target.anchor)
for component in target.parts[1:]:
    current = current / component
    if current.is_symlink():
        raise SystemExit(f"symlink component: {current}")
if not target.is_dir() or target.resolve(strict=True) != target:
    raise SystemExit("target is not the canonical existing directory")
PY

test "$(sha256sum "$TARGET/AGENTS.md" | awk '{print $1}')" = '74d7b6cd7d755cb07b04f205e5b6beef9ca7c7412379c2bbd9db166f1bac47cc'
test "$(sha256sum "$TARGET/.gitignore" | awk '{print $1}')" = 'bec10e5dc357805b65436e39e33433be69f6366bd88d336ffb1c94b69b6b581f'
test "$(sha256sum "$TARGET/CLAUDE.md" | awk '{print $1}')" = '0aaefece9c24a67288c16760ddad79d30f395537dc50a1c8c23fcbabde5366fc'
test "$(sha256sum "$TARGET/REVIEW.md" | awk '{print $1}')" = '624d52371c932b3699c01e84956f6f91bbd446f84608c9b954876f1b7d332f35'
test ! -e "$TARGET/AGENTS.pre-codex-workflow.md"
test ! -e "$TARGET/.ai"
test ! -e "$TARGET/.codex"
test ! -e "$TARGET/openspec"
test ! -e "$TARGET/scripts"
test ! -e "$TARGET/.claude"
if grep -Fq '# >>> portable-ai-workflow installer >>>' "$TARGET/.gitignore"; then exit 1; fi

python3 -B - "$TARGET" > "$SOURCE/openspec/changes/install-codex-workflow-yuxiaor/evidence/nested-repos-before.sha256" <<'PY'
from pathlib import Path
import hashlib
import subprocess
import sys

target = Path(sys.argv[1])
repos = sorted(path.parent for path in target.glob('*/.git') if path.exists())
if len(repos) != 10:
    raise SystemExit(f'expected 10 nested repositories, found {len(repos)}')
for repo in repos:
    head = subprocess.check_output(['git', '-C', str(repo), 'rev-parse', 'HEAD'])
    status = subprocess.check_output(['git', '-C', str(repo), 'status', '--porcelain=v1', '-z'])
    digest = hashlib.sha256(b'HEAD\0' + head + b'STATUS\0' + status).hexdigest()
    print(f'{digest}  {repo.name}')
PY

{
  printf '%s\n' 'PATH_COMPONENTS_NO_SYMLINK=PASS'
  printf '%s\n' 'ROOT_HASHES_AND_ABSENCE_CHECKS=PASS'
  printf '%s\n' 'NESTED_REPOSITORIES=10'
} > "$SOURCE/openspec/changes/install-codex-workflow-yuxiaor/evidence/preflight.txt"
```

**Expected**

- 所有 `test`、路径检查和嵌套仓快照命令退出码为 0。
- 快照只记录每个嵌套仓 HEAD+状态摘要的 SHA-256，不保存文件名或正文，避免泄露用户数据。
- 任一身份不匹配即停止，不重命名、不安装、不删除。

## Task 2：保留旧入口、复验计划并事务安装

**Modify**

- 目标 `AGENTS.md` → `AGENTS.pre-codex-workflow.md`：原子重命名，保留原字节与元数据。
- 目标根下共享 `.ai/`、`.codex/`、`openspec/`、`scripts/` 和 `.gitignore`：仅由安装器写入。

**Create evidence**

- `openspec/changes/install-codex-workflow-yuxiaor/evidence/install.txt`

**Execute**

```bash
SOURCE='/media/shitou/石头/wksource/git_me_prj/ai_agent/.worktrees/install-codex-workflow-yuxiaor'
TARGET='/media/shitou/石头/wksource/yuxiaor_prj_2025'
EVIDENCE="$SOURCE/openspec/changes/install-codex-workflow-yuxiaor/evidence/install.txt"

set -euo pipefail
test ! -e "$TARGET/AGENTS.pre-codex-workflow.md"
mv --no-clobber "$TARGET/AGENTS.md" "$TARGET/AGENTS.pre-codex-workflow.md"
test "$(sha256sum "$TARGET/AGENTS.pre-codex-workflow.md" | awk '{print $1}')" = '74d7b6cd7d755cb07b04f205e5b6beef9ca7c7412379c2bbd9db166f1bac47cc'

bash "$SOURCE/scripts/install-ai-workflow.sh" \
  --target "$TARGET" --assistant codex --dry-run | tee "$EVIDENCE"
grep -Fx 'RESULT assistant=codex target=/media/shitou/石头/wksource/yuxiaor_prj_2025 created=52 updated=1 unchanged=0 dry_run=1' "$EVIDENCE"

bash "$SOURCE/scripts/install-ai-workflow.sh" \
  --target "$TARGET" --assistant codex | tee -a "$EVIDENCE"
grep -Fx 'RESULT assistant=codex target=/media/shitou/石头/wksource/yuxiaor_prj_2025 created=52 updated=1 unchanged=0 dry_run=0' "$EVIDENCE"
```

**Failure path**

- 若 dry-run 或安装器返回非零：
  1. 不删除任何目标路径。
  2. 仅当 `$TARGET/AGENTS.md` 不存在且 `.ai/`、`.codex/`、`openspec/`、`scripts/` 均不存在时，执行 `mv --no-clobber "$TARGET/AGENTS.pre-codex-workflow.md" "$TARGET/AGENTS.md"` 恢复旧入口，并复核旧 SHA-256。
  3. 若出现任何部分安装内容或安装器报告 rollback failed，保留现场并立即停止请求用户决定；不得猜测性清理。

**Expected**

- dry-run 与实际安装均成功，实际结果 `created=52 updated=1 unchanged=0 dry_run=0`。
- 备份 `AGENTS.pre-codex-workflow.md` SHA-256 保持 `74d7b6cd7d755cb07b04f205e5b6beef9ca7c7412379c2bbd9db166f1bac47cc`。
- 新 `AGENTS.md` SHA-256 为 `961dbcbb03b2311656d155818a80cbdca57ad6b15e8ed70eee0061d1207bfe71`。
- `.gitignore` SHA-256 为 `0cd57481fa44d1d0a42baedcca91bea7078982f3ad9345315aa7990c96df9889`，且原内容仍为前缀。

## Task 3：目标安装后验证与边界复核

**Create**

- `openspec/changes/install-codex-workflow-yuxiaor/evidence/target-validation.txt`
- `openspec/changes/install-codex-workflow-yuxiaor/evidence/nested-repos-after.sha256`
- `openspec/changes/install-codex-workflow-yuxiaor/evidence/postflight.txt`

**Execute**

```bash
SOURCE='/media/shitou/石头/wksource/git_me_prj/ai_agent/.worktrees/install-codex-workflow-yuxiaor'
TARGET='/media/shitou/石头/wksource/yuxiaor_prj_2025'
EVIDENCE="$SOURCE/openspec/changes/install-codex-workflow-yuxiaor/evidence"

set -euo pipefail
cd "$TARGET"
bash scripts/validate-workflow.sh --require-openspec | tee "$EVIDENCE/target-validation.txt"
openspec validate --all --strict --no-interactive | tee -a "$EVIDENCE/target-validation.txt"

bash "$SOURCE/scripts/install-ai-workflow.sh" \
  --target "$TARGET" --assistant codex --dry-run | tee -a "$EVIDENCE/target-validation.txt"
grep -Fx 'RESULT assistant=codex target=/media/shitou/石头/wksource/yuxiaor_prj_2025 created=0 updated=0 unchanged=53 dry_run=1' "$EVIDENCE/target-validation.txt"

test "$(sha256sum "$TARGET/AGENTS.pre-codex-workflow.md" | awk '{print $1}')" = '74d7b6cd7d755cb07b04f205e5b6beef9ca7c7412379c2bbd9db166f1bac47cc'
test "$(sha256sum "$TARGET/AGENTS.md" | awk '{print $1}')" = '961dbcbb03b2311656d155818a80cbdca57ad6b15e8ed70eee0061d1207bfe71'
test "$(sha256sum "$TARGET/.gitignore" | awk '{print $1}')" = '0cd57481fa44d1d0a42baedcca91bea7078982f3ad9345315aa7990c96df9889'
test "$(sha256sum "$TARGET/.ai/assistant-profile.json" | awk '{print $1}')" = '27e9b41320f1df7479e2dcb81605c3c260108214c0055c2b99b5eae69908d289'
test "$(sha256sum "$TARGET/CLAUDE.md" | awk '{print $1}')" = '0aaefece9c24a67288c16760ddad79d30f395537dc50a1c8c23fcbabde5366fc'
test "$(sha256sum "$TARGET/REVIEW.md" | awk '{print $1}')" = '624d52371c932b3699c01e84956f6f91bbd446f84608c9b954876f1b7d332f35'
test ! -e "$TARGET/.claude"

python3 -B - "$TARGET" > "$EVIDENCE/nested-repos-after.sha256" <<'PY'
from pathlib import Path
import hashlib
import subprocess
import sys

target = Path(sys.argv[1])
repos = sorted(path.parent for path in target.glob('*/.git') if path.exists())
if len(repos) != 10:
    raise SystemExit(f'expected 10 nested repositories, found {len(repos)}')
for repo in repos:
    head = subprocess.check_output(['git', '-C', str(repo), 'rev-parse', 'HEAD'])
    status = subprocess.check_output(['git', '-C', str(repo), 'status', '--porcelain=v1', '-z'])
    digest = hashlib.sha256(b'HEAD\0' + head + b'STATUS\0' + status).hexdigest()
    print(f'{digest}  {repo.name}')
PY
cmp "$EVIDENCE/nested-repos-before.sha256" "$EVIDENCE/nested-repos-after.sha256"
{
  printf '%s\n' 'REQUIRED_WORKFLOW_NO_FAIL=PASS'
  printf '%s\n' 'OPENSPEC_STRICT=PASS'
  printf '%s\n' 'IDEMPOTENT_DRY_RUN_UNCHANGED_53=PASS'
  printf '%s\n' 'ROOT_HASHES_PROFILE_AND_ABSENCE=PASS'
  printf '%s\n' 'NESTED_REPOSITORIES_BYTE_IDENTICAL_SUMMARY=PASS'
} > "$EVIDENCE/postflight.txt"
```

**Expected**

- `scripts/validate-workflow.sh --require-openspec` 最终无 `FAIL`、无 OpenSpec `SKIP`。
- `openspec validate --all --strict --no-interactive` 输出全部有效。
- 重复 dry-run 证明 53 个安装项全部 `unchanged`。
- 十个嵌套业务仓的 HEAD+状态摘要逐字节一致；`CLAUDE.md` 与 `REVIEW.md` 未变。

## Task 4：严格审查、状态推进与归档

**Create/Modify**

- `openspec/changes/install-codex-workflow-yuxiaor/review-findings.md`
- `.ai-local/reviews/install-codex-workflow-yuxiaor/full-1.json`
- 必要时仅修复审查发现的 Critical/Important，并追加 evidence。

**Execute**

```bash
SOURCE='/media/shitou/石头/wksource/git_me_prj/ai_agent/.worktrees/install-codex-workflow-yuxiaor'
cd "$SOURCE"
python3 -B .ai/tools/review_manifest.py freeze \
  --change install-codex-workflow-yuxiaor \
  --workspace "$SOURCE" \
  --repo-spec "$SOURCE::main" \
  --output .ai-local/reviews/install-codex-workflow-yuxiaor/full-1.json
python3 -B .ai/tools/review_manifest.py verify \
  --manifest .ai-local/reviews/install-codex-workflow-yuxiaor/full-1.json
```

**Review gates**

1. Build 任务级 reviewer：核对 Task 0–3 的命令、输出、失败路径和目标边界。
2. Verify reviewer A：规格符合性，逐条覆盖 delta Requirement/Scenario。
3. Verify reviewer B：安装质量与安全边界，重点检查路径、事务、备份、嵌套仓、敏感信息与验证有效性。
4. 每个 reviewer 读取范围前和结论前都运行上述 `review_manifest.py verify`，任一 `STALE` 立即停止。
5. finding 使用 `.ai/rules/review.md` 固定字段；Critical/Important 未关闭不得进入归档。

**State transitions**

- Build 任务级审查通过：proposal 改为`待验证`，勾选 Build/验证任务并提交构建证据。
- 双阶段 Verify 通过：proposal 改为`待归档`，提交审查台账与状态。
- Archive：合并 `codex-workflow-target-installation` delta 到主规格，完成 `.ai/` 三写，移动变更与计划到 `openspec/archive/install-codex-workflow-yuxiaor/`，运行严格门禁并提交归档。

**Local integration**

- 归档后暂停，向用户提供且仅提供：本地 `--no-ff` 合回 main 并复验、保留 feature 稍后推送/PR、保留分支和 worktree 稍后处理。
- 本次计划确认不授权推送、创建 PR、强推或删除已合并分支/worktree。
