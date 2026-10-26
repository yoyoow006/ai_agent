# Archive 执行细则

- `--archive-files` 只能传 Verify 后 diff 中精确变更的治理/工作流文件路径，禁止传目录或预设大清单。
- 业务归档未触及工作流可执行文件、助手入口、技能语义、契约测试或治理规格时，直接运行 `--archive-light`。
- 误传目录级清单会把普通归档/知识文件也纳入 required 升级判断，导致全量契约套件误触发。

执行前记录最新有效 Verify 的 comparison base，并读取 wrapper 的参数接口。`--archive-files` 接收逐个文件路径参数，基线用 `WORKFLOW_ARCHIVE_BASE` 传入，不是清单文件参数。先用 `git diff --name-only <verify-base> --` 与 `git ls-files --others --exclude-standard` 核对已跟踪和新增文件，将实际治理/工作流文件逐个列入。删除文件仍保留其精确旧路径；未跟踪治理文件不会出现在 wrapper 的 git diff 中，存在这类新增文件时直接 required。无法完整确定差异时直接 required。

```bash
# 示例：Verify 后确实仅修改了该治理文件时
WORKFLOW_ARCHIVE_GATE=1 WORKFLOW_ARCHIVE_BASE="$verify_base" \
  bash scripts/validate-workflow.sh --archive-light --archive-files .ai/rules/review.md
```

`verify_base` 必须是已记录的有效 Verify 基线；当时存在未提交差异时，同时比对持久化审查快照，不能以 HEAD 代替证据身份。不得用预设目录扩大分类范围，也不得漏列变化来避免升级。
