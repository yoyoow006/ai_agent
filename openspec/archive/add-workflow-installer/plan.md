# add-workflow-installer 实现计划

> **执行者须知：** 必须使用 subagent-driven（推荐）或逐任务直执方式实现本计划，一次一个任务。步骤用 `- [ ]` 复选框追踪。

**目标：** 提供 `scripts/install-workflow.sh`，一条命令把本仓库的五阶段工作流全套资产安装到任意目标项目，装后自检全绿。

**架构：** 单文件 bash 安装器，源=本仓库自身（单源维护）。三段式：参数与目标校验 → 冲突扫描（默认中止 / `--force` 备份覆盖）→ 复制清单执行 + 装后自检（复用 `validate-workflow.sh` 作验收器）。目标项目的 `openspec/project.md` 写通用占位版；`ai-kb/memory/` 只补缺永不覆盖（用户数据）。

**技术栈：** 纯 bash（`set -u`，兼容旧 bash/git，不用 bash4+ 特性）、cp/mkdir/mv。

## 全局约束

- 零依赖：不依赖 openspec CLI、不引入包管理器（spec：零依赖可移植）
- 退出码约定：0=成功；1=冲突或装后自检失败；2=用法/路径错误（spec：一键安装/冲突防护 Scenario）
- `--force` 覆盖前每个文件型资产备份为 `<原名>.bak`（.bak 已存在则被替换）；技能目录备份为 `<技能名>.bak/`（目录整体 mv，旧 .bak 先删）（spec：冲突防护）
- `ai-kb/memory/` 只补 `.gitkeep` 缺失，**永不覆盖、不备份**已有内容
- 目标路径必须已存在且是目录，不代建（spec：目标路径无效 Scenario）
- 装后自检 = 在目标路径运行 `./scripts/validate-workflow.sh`，全绿才 exit 0（spec：装后自检）
- 脚本提交须 `git update-index --chmod=+x scripts/install-workflow.sh`（本机 core.fileMode=false 坑）
- 提交规范：`feat:`/`docs:` 前缀 + 中文描述；禁止 `git add -A`，只 add 明确路径
- 全中文输出文案

## 文件结构总览

| 文件 | 职责 | 产生任务 |
|---|---|---|
| `scripts/install-workflow.sh` | 一键安装器（参数/冲突/复制/自检） | 1 |
| `/tmp 试验场目录`（不入库） | 实测证据（空装/冲突/强制/无 CLI） | 1, 2 |

---

### Task 1: 安装脚本主体

**Files:**
- Create: `scripts/install-workflow.sh`
- 勾选: `openspec/changes/add-workflow-installer/tasks.md`（1.1、1.2）

**Interfaces:**
- Consumes: 本仓库现有资产（CLAUDE.md、`.claude/skills/*/`、`.claude/ai-kb/{README.md,kb/overview.md,rules/index.md}`、`openspec/AGENTS.md`、`scripts/validate-workflow.sh`）
- Produces: `bash scripts/install-workflow.sh <目标> [--force]`；退出码 0/1/2（Task 2 的实测依赖此约定）

- [ ] **Step 1: 写脚本全文**

创建 `scripts/install-workflow.sh`：

```bash
#!/usr/bin/env bash
# install-workflow.sh —— 把本仓库的五阶段工作流资产一键安装到目标项目
# 用法: bash scripts/install-workflow.sh <目标项目路径> [--force]
set -u

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SRC_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

FORCE=0
TARGET=""

usage() {
  cat <<'EOF'
用法: bash scripts/install-workflow.sh <目标项目路径> [--force]

把本仓库的五阶段 AI 编程助手工作流安装到目标项目：
  CLAUDE.md                     工作流总纲
  .claude/skills/               13 个技能（5 阶段 + 8 支撑）
  .claude/ai-kb/                知识库骨架（memory 只补缺，永不覆盖已有内容）
  openspec/                     变更数据层骨架 + 通用版 project.md（请装后填写）
  scripts/validate-workflow.sh  结构校验脚本

选项:
  --force   覆盖目标已存在的同名资产（覆盖前备份为 <原名>.bak；
            已有 .bak 会被替换；ai-kb/memory 例外——永不覆盖不备份）

退出码: 0=成功  1=冲突或装后自检失败  2=用法/路径错误
EOF
}

die() { echo "错误: $*" >&2; exit 2; }

# ---------- 参数解析 ----------
while [ $# -gt 0 ]; do
  case "$1" in
    --force) FORCE=1 ;;
    --help)  usage; exit 2 ;;
    -*)      die "未知选项: $1（--help 查看用法）" ;;
    *)       if [ -n "$TARGET" ]; then die "只接受一个目标路径"; fi
             TARGET="$1" ;;
  esac
  shift
done

[ -n "$TARGET" ] || { usage >&2; exit 2; }
[ -d "$TARGET" ] || die "目标路径不存在或不是目录: $TARGET（不代建，请先创建目标项目）"
TARGET="$(cd "$TARGET" && pwd)"

# ---------- 工具 ----------
say()  { echo "  $*"; }
backup_file() {  # 文件型资产备份；幂等
  [ -f "$1" ] || return 0
  cp -p "$1" "$1.bak"
  say "备份: ${1#"$TARGET"/} -> ${1#"$TARGET"/}.bak"
}

# ---------- 冲突扫描 ----------
conflicts=""
add_conflict() { conflicts="$conflicts
  - $1"; }

[ -e "$TARGET/CLAUDE.md" ]                      && add_conflict "CLAUDE.md"
[ -e "$TARGET/scripts/validate-workflow.sh" ]   && add_conflict "scripts/validate-workflow.sh"
[ -e "$TARGET/openspec/project.md" ]            && add_conflict "openspec/project.md（将被通用占位版替换）"
[ -e "$TARGET/openspec/AGENTS.md" ]             && add_conflict "openspec/AGENTS.md"
for f in README.md kb/overview.md rules/index.md; do
  [ -e "$TARGET/.claude/ai-kb/$f" ]             && add_conflict ".claude/ai-kb/$f"
done
for d in "$SRC_ROOT"/.claude/skills/*/; do
  name="$(basename "$d")"
  [ -e "$TARGET/.claude/skills/$name" ]         && add_conflict ".claude/skills/$name/"
done

if [ -n "$conflicts" ] && [ "$FORCE" -ne 1 ]; then
  echo "错误: 目标项目存在以下同名资产，未安装：" >&2
  echo "$conflicts" >&2
  echo "确认覆盖请加 --force（覆盖前备份为 <原名>.bak）。" >&2
  exit 1
fi

# ---------- 安装 ----------
echo "安装五阶段工作流到: $TARGET"
[ "$FORCE" -ne 1 ] || say "模式: --force（覆盖前备份）"

# 1) CLAUDE.md
backup_file "$TARGET/CLAUDE.md"
mkdir -p "$TARGET"
cp -p "$SRC_ROOT/CLAUDE.md" "$TARGET/CLAUDE.md"
say "已装: CLAUDE.md"

# 2) 13 个技能目录（整目录备份为 <技能名>.bak/）
mkdir -p "$TARGET/.claude/skills"
for d in "$SRC_ROOT"/.claude/skills/*/; do
  name="$(basename "$d")"
  dst="$TARGET/.claude/skills/$name"
  if [ -e "$dst" ]; then
    rm -rf "${dst:?}.bak"
    mv "$dst" "$dst.bak"
    say "备份: .claude/skills/$name/ -> .claude/skills/$name.bak/"
  fi
  mkdir -p "$dst"
  cp -R "$d." "$dst/"
  say "已装: .claude/skills/$name/"
done

# 3) ai-kb 骨架（memory 只补缺，永不覆盖）
mkdir -p "$TARGET/.claude/ai-kb/kb" "$TARGET/.claude/ai-kb/rules" "$TARGET/.claude/ai-kb/memory"
backup_file "$TARGET/.claude/ai-kb/README.md"
cp -p "$SRC_ROOT/.claude/ai-kb/README.md" "$TARGET/.claude/ai-kb/README.md"
backup_file "$TARGET/.claude/ai-kb/kb/overview.md"
cp -p "$SRC_ROOT/.claude/ai-kb/kb/overview.md" "$TARGET/.claude/ai-kb/kb/overview.md"
backup_file "$TARGET/.claude/ai-kb/rules/index.md"
cp -p "$SRC_ROOT/.claude/ai-kb/rules/index.md" "$TARGET/.claude/ai-kb/rules/index.md"
[ -f "$TARGET/.claude/ai-kb/memory/.gitkeep" ] || touch "$TARGET/.claude/ai-kb/memory/.gitkeep"
say "已装: .claude/ai-kb/（memory 保持/新建空骨架）"

# 4) openspec 骨架（project.md 写通用占位版）
mkdir -p "$TARGET/openspec/changes" "$TARGET/openspec/plan" \
         "$TARGET/openspec/specs" "$TARGET/openspec/archive"
for sd in changes plan specs archive; do
  [ -f "$TARGET/openspec/$sd/.gitkeep" ] || touch "$TARGET/openspec/$sd/.gitkeep"
done
backup_file "$TARGET/openspec/AGENTS.md"
cp -p "$SRC_ROOT/openspec/AGENTS.md" "$TARGET/openspec/AGENTS.md"
if [ -f "$TARGET/openspec/project.md" ]; then
  cp -p "$TARGET/openspec/project.md" "$TARGET/openspec/project.md.bak"
  say "备份: openspec/project.md -> openspec/project.md.bak"
fi
cat > "$TARGET/openspec/project.md" <<'EOF'
# 项目上下文

<!-- install-workflow.sh 生成的占位模板：请替换为本项目的真实描述 -->

本仓库使用五阶段 AI 编程助手工作流（Open → Design → Build → Verify → Archive），
总纲见 CLAUDE.md，变更数据层见 openspec/，知识库见 .claude/ai-kb/。

## 本项目是什么

（请填写：项目用途、技术栈、关键模块）

## 团队约定

（请填写：命名、分支、提交规范等）
EOF
say "已装: openspec/ 骨架 + 通用版 project.md（请填写项目上下文）"

# 5) 校验脚本
mkdir -p "$TARGET/scripts"
backup_file "$TARGET/scripts/validate-workflow.sh"
cp -p "$SRC_ROOT/scripts/validate-workflow.sh" "$TARGET/scripts/validate-workflow.sh"
chmod +x "$TARGET/scripts/validate-workflow.sh"
say "已装: scripts/validate-workflow.sh（已赋执行位）"

# ---------- 装后自检 ----------
echo "装后自检: 运行目标项目 ./scripts/validate-workflow.sh"
if (cd "$TARGET" && ./scripts/validate-workflow.sh); then
  echo "✓ 安装完成，自检全绿。下一步：填写 openspec/project.md 项目上下文；"
  echo "  在目标项目重启 Claude Code 会话即可使用五阶段工作流。"
  exit 0
else
  echo "错误: 装后自检未全绿，请把上方输出反馈给维护者。" >&2
  exit 1
fi
```

- [ ] **Step 2: 空目标实测**

```bash
chmod +x scripts/install-workflow.sh
T1="$(mktemp -d)"
bash scripts/install-workflow.sh "$T1"; echo "exit=$?"
ls "$T1" && ls "$T1/.claude/skills" | wc -l && ls "$T1/openspec"
```
Expected: `exit=0`；自检全绿；根下 `CLAUDE.md  openspec  scripts  .claude`（及目标原有内容）；技能目录数 `13`；openspec 下 `AGENTS.md  project.md  changes  plan  specs  archive`。

- [ ] **Step 3: 用法与无效路径实测**

```bash
bash scripts/install-workflow.sh; echo "exit=$?"
bash scripts/install-workflow.sh --help; echo "exit=$?"
bash scripts/install-workflow.sh /tmp/definitely-not-exist-$$; echo "exit=$?"
```
Expected: 前两条打印用法、`exit=2`；第三条报“目标路径不存在”、`exit=2`。

- [ ] **Step 4: 提交（含执行位）**

勾选 tasks.md 的 1.1、1.2 后：

```bash
git add scripts/install-workflow.sh openspec/changes/add-workflow-installer/tasks.md \
  && git update-index --chmod=+x scripts/install-workflow.sh \
  && git commit -m "feat: 工作流一键安装脚本 install-workflow.sh"
```

---

### Task 2: 冲突与降级环境实测

**Files:**
- Modify: 发现问题时的 `scripts/install-workflow.sh`
- 勾选: `openspec/changes/add-workflow-installer/tasks.md`（2.1、2.2、2.3、3.1）

**Interfaces:**
- Consumes: Task 1 的脚本与退出码约定（0/1/2）；`.bak` 备份约定
- Produces: 三场景实测证据（归档材料）

- [ ] **Step 1: 冲突默认中止实测**

```bash
T2="$(mktemp -d)"
echo "原有总纲" > "$T2/CLAUDE.md"
mkdir -p "$T2/.claude/skills/tdd"
echo "伪技能" > "$T2/.claude/skills/tdd/SKILL.md"
bash scripts/install-workflow.sh "$T2"; echo "exit=$?"
```
Expected: `exit=1`；错误清单含 `CLAUDE.md` 与 `.claude/skills/tdd/`；提示 `--force`。

- [ ] **Step 2: --force 备份覆盖实测**

```bash
bash scripts/install-workflow.sh "$T2" --force; echo "exit=$?"
cat "$T2/CLAUDE.md.bak" && ls -d "$T2/.claude/skills/tdd.bak" \
  && grep -q '铁律\|红' "$T2/.claude/skills/tdd/SKILL.md" && echo "新技能就位"
```
Expected: `exit=0` 自检全绿；`.bak` 内容为“原有总纲”；`tdd.bak/` 目录存在；新 tdd 技能为真技能（含 TDD 纪律关键词）。

- [ ] **Step 3: 无 openspec CLI 环境模拟**

```bash
T3="$(mktemp -d)"
env PATH="$(dirname "$(command -v bash)"):/usr/bin:/bin" \
  bash scripts/install-workflow.sh "$T3"; echo "exit=$?"
env PATH="$(dirname "$(command -v bash)"):/usr/bin:/bin" \
  openspec list 2>/dev/null && echo "CLI 仍在（模拟失败）" || echo "CLI 确实不可用"
```
Expected: 安装 `exit=0`（校验脚本 `command -v` 门控跳过 CLI 两项仍全绿）；第二命令输出 `CLI 确实不可用`。

- [ ] **Step 4: 问题修复回跑与提交**

实测暴露脚本缺陷 → 修复 → 重跑 Step 1-3 全过 → 勾选 tasks.md 2.1-2.3、3.1：

```bash
git add scripts/install-workflow.sh openspec/changes/add-workflow-installer/tasks.md \
  && git update-index --chmod=+x scripts/install-workflow.sh \
  && git commit -m "test: 安装脚本三场景实测修正（如无修正则仅勾选）"
```

---

## 计划自审结论

- **Spec 覆盖**：一键安装（Task 1 Step 2）／冲突防护两 Scenario（Task 2 Steps 1-2）／装后自检（Task 1 Step 2、脚本内建）／零依赖可移植（Task 2 Step 3、全局约束）／初始化适配（脚本 3)4) 段：通用 project.md、memory 只补缺）／目标路径无效与无参数（Task 1 Step 3）。无缺口。
- **占位符扫描**：脚本全文照写、测试命令带 Expected，无 TBD/“适当处理”类模式。
- **接口一致性**：退出码 0/1/2 与 `--force`/`.bak` 约定在全局约束、脚本 usage、Task 2 断言三处一致；`.gitkeep` 补缺逻辑与校验脚本“目录存在”检查对齐。

## 后续跟进（计划外，自然发生）

- 卸载命令：需要时另立变更（设计取舍已记录）
- 增量/版本比对：重跑 `--force` 即全量同步，暂不做
