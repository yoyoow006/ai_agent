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
  AGENTS.md                     工作流总纲（Codex 入口）
  .claude/skills/               本仓库全部技能（5 阶段 + 8 支撑，随源仓库演进）
  .claude/ai-kb/                知识库骨架（memory 只补缺，永不覆盖已有内容）
  .codex/                       Codex 版工作流（skills/ai-kb/sdd，随源仓库演进）
  openspec/                     变更数据层骨架 + 通用版 project.md（请装后填写）
  scripts/validate-workflow.sh  结构校验脚本

选项:
  --force   覆盖目标已存在的同名资产（覆盖前备份为 <原名>.bak；
            已有 .bak 会被替换；ai-kb/memory 例外——永不覆盖不备份）

退出码: 0=成功  1=冲突、安装失败或装后自检失败  2=用法/路径错误
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
norm_target="$(cd -- "$TARGET" && pwd)" || die "无法进入目标路径: $TARGET"
TARGET="$norm_target"
[ "$TARGET" = "/" ] && die "拒绝安装到根目录 /"

# ---------- 源预检 ----------
[ -d "$SRC_ROOT/.claude/skills" ] || die "源仓库异常: 找不到 .claude/skills（脚本须在本仓库内运行）"

# ---------- 工具 ----------
say()  { echo "  $*"; }
install_file() {  # 单文件复制；目标是目录时拒绝（cp 会静默复制进目录），cp 失败即中止
  [ ! -d "$2" ] || { echo "错误: 目标是目录，无法安装为文件: $2" >&2; exit 1; }
  cp -p "$1" "$2" || { echo "错误: 复制失败 $1 -> $2" >&2; exit 1; }
}
install_tree() {  # 目录递归复制，失败即中止
  cp -R "$1" "$2" || { echo "错误: 复制失败 $1 -> $2" >&2; exit 1; }
}
make_dir() {  # mkdir -p，失败即中止
  mkdir -p "$@" || { echo "错误: 创建目录失败 $*" >&2; exit 1; }
}
backup_file() {  # 文件型资产备份；幂等
  [ -f "$1" ] || return 0
  install_file "$1" "$1.bak"
  say "备份: ${1#"$TARGET"/} -> ${1#"$TARGET"/}.bak"
}

# ---------- 冲突扫描 ----------
conflicts=""
add_conflict() { conflicts="$conflicts
  - $1"; }

[ -e "$TARGET/CLAUDE.md" ]                      && add_conflict "CLAUDE.md"
[ -e "$TARGET/AGENTS.md" ]                      && add_conflict "AGENTS.md"
[ -e "$TARGET/scripts/validate-workflow.sh" ]   && add_conflict "scripts/validate-workflow.sh"
[ -e "$TARGET/openspec/project.md" ]            && add_conflict "openspec/project.md（将被通用占位版替换）"
[ -e "$TARGET/openspec/AGENTS.md" ]             && add_conflict "openspec/AGENTS.md"
[ -e "$TARGET/.codex/README.md" ]               && add_conflict ".codex/README.md"
for f in README.md kb/overview.md rules/index.md; do
  [ -e "$TARGET/.claude/ai-kb/$f" ]             && add_conflict ".claude/ai-kb/$f"
  [ -e "$TARGET/.codex/ai-kb/$f" ]              && add_conflict ".codex/ai-kb/$f"
done
for d in "$SRC_ROOT"/.claude/skills/*/; do
  name="$(basename "$d")"
  [ -e "$TARGET/.claude/skills/$name" ]         && add_conflict ".claude/skills/$name/"
done
for d in "$SRC_ROOT"/.codex/skills/*/; do
  name="$(basename "$d")"
  [ -e "$TARGET/.codex/skills/$name" ]          && add_conflict ".codex/skills/$name/"
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
make_dir "$TARGET"
install_file "$SRC_ROOT/CLAUDE.md" "$TARGET/CLAUDE.md"
say "已装: CLAUDE.md"

# 1b) AGENTS.md（Codex 入口）
backup_file "$TARGET/AGENTS.md"
install_file "$SRC_ROOT/AGENTS.md" "$TARGET/AGENTS.md"
say "已装: AGENTS.md"

# 2) 全部技能目录（整目录备份为 <技能名>.bak/）
make_dir "$TARGET/.claude/skills"
for d in "$SRC_ROOT"/.claude/skills/*/; do
  name="$(basename "$d")"
  dst="$TARGET/.claude/skills/$name"
  if [ -e "$dst" ]; then
    rm -rf "${dst:?}.bak" || { echo "错误: 清理旧备份失败 $dst.bak" >&2; exit 1; }
    mv "$dst" "$dst.bak" || { echo "错误: 备份失败 $dst -> $dst.bak" >&2; exit 1; }
    say "备份: .claude/skills/$name/ -> .claude/skills/$name.bak/"
  fi
  make_dir "$dst"
  install_tree "$d." "$dst/"
  say "已装: .claude/skills/$name/"
done

# 3) ai-kb 骨架（memory 只补缺，永不覆盖）
make_dir "$TARGET/.claude/ai-kb/kb" "$TARGET/.claude/ai-kb/rules" "$TARGET/.claude/ai-kb/memory"
backup_file "$TARGET/.claude/ai-kb/README.md"
install_file "$SRC_ROOT/.claude/ai-kb/README.md" "$TARGET/.claude/ai-kb/README.md"
backup_file "$TARGET/.claude/ai-kb/kb/overview.md"
install_file "$SRC_ROOT/.claude/ai-kb/kb/overview.md" "$TARGET/.claude/ai-kb/kb/overview.md"
backup_file "$TARGET/.claude/ai-kb/rules/index.md"
install_file "$SRC_ROOT/.claude/ai-kb/rules/index.md" "$TARGET/.claude/ai-kb/rules/index.md"
[ -f "$TARGET/.claude/ai-kb/memory/.gitkeep" ] || touch "$TARGET/.claude/ai-kb/memory/.gitkeep" \
  || { echo "错误: 创建失败 $TARGET/.claude/ai-kb/memory/.gitkeep" >&2; exit 1; }
say "已装: .claude/ai-kb/（memory 保持/新建空骨架）"

# 3b) .codex 工作流（README + skills + ai-kb，memory 同样永不覆盖）
make_dir "$TARGET/.codex/skills" "$TARGET/.codex/sdd" \
         "$TARGET/.codex/ai-kb/kb" "$TARGET/.codex/ai-kb/rules" "$TARGET/.codex/ai-kb/memory"
backup_file "$TARGET/.codex/README.md"
install_file "$SRC_ROOT/.codex/README.md" "$TARGET/.codex/README.md"
for d in "$SRC_ROOT"/.codex/skills/*/; do
  name="$(basename "$d")"
  dst="$TARGET/.codex/skills/$name"
  if [ -e "$dst" ]; then
    rm -rf "${dst:?}.bak" || { echo "错误: 清理旧备份失败 $dst.bak" >&2; exit 1; }
    mv "$dst" "$dst.bak" || { echo "错误: 备份失败 $dst -> $dst.bak" >&2; exit 1; }
    say "备份: .codex/skills/$name/ -> .codex/skills/$name.bak/"
  fi
  make_dir "$dst"
  install_tree "$d." "$dst/"
done
backup_file "$TARGET/.codex/ai-kb/README.md"
install_file "$SRC_ROOT/.codex/ai-kb/README.md" "$TARGET/.codex/ai-kb/README.md"
backup_file "$TARGET/.codex/ai-kb/kb/overview.md"
install_file "$SRC_ROOT/.codex/ai-kb/kb/overview.md" "$TARGET/.codex/ai-kb/kb/overview.md"
backup_file "$TARGET/.codex/ai-kb/rules/index.md"
install_file "$SRC_ROOT/.codex/ai-kb/rules/index.md" "$TARGET/.codex/ai-kb/rules/index.md"
[ -f "$TARGET/.codex/ai-kb/memory/.gitkeep" ] || touch "$TARGET/.codex/ai-kb/memory/.gitkeep" \
  || { echo "错误: 创建失败 $TARGET/.codex/ai-kb/memory/.gitkeep" >&2; exit 1; }
[ -f "$TARGET/.codex/sdd/.gitkeep" ] || touch "$TARGET/.codex/sdd/.gitkeep" \
  || { echo "错误: 创建失败 $TARGET/.codex/sdd/.gitkeep" >&2; exit 1; }
say "已装: .codex/（README + skills + ai-kb，memory 保持/新建空骨架）"

# 4) openspec 骨架（project.md 写通用占位版）
make_dir "$TARGET/openspec/changes" "$TARGET/openspec/plan" \
         "$TARGET/openspec/specs" "$TARGET/openspec/archive"
for sd in changes plan specs archive; do
  [ -f "$TARGET/openspec/$sd/.gitkeep" ] || touch "$TARGET/openspec/$sd/.gitkeep" \
    || { echo "错误: 创建失败 $TARGET/openspec/$sd/.gitkeep" >&2; exit 1; }
done
backup_file "$TARGET/openspec/AGENTS.md"
install_file "$SRC_ROOT/openspec/AGENTS.md" "$TARGET/openspec/AGENTS.md"
backup_file "$TARGET/openspec/project.md"
cat > "$TARGET/openspec/project.md" <<'EOF' || { echo "错误: 写入失败 $TARGET/openspec/project.md" >&2; exit 1; }
# 项目上下文

<!-- install-workflow.sh 生成的占位模板：请替换为本项目的真实描述 -->

本仓库使用五阶段 AI 编程助手工作流（Open → Design → Build → Verify → Archive），
总纲见 CLAUDE.md（Claude）与 AGENTS.md（Codex），变更数据层见 openspec/，
知识库见 .claude/ai-kb/ 与 .codex/ai-kb/。

## 本项目是什么

（请填写：项目用途、技术栈、关键模块）

## 团队约定

（请填写：命名、分支、提交规范等）
EOF
say "已装: openspec/ 骨架 + 通用版 project.md（请填写项目上下文）"

# 5) 校验脚本
make_dir "$TARGET/scripts"
backup_file "$TARGET/scripts/validate-workflow.sh"
install_file "$SRC_ROOT/scripts/validate-workflow.sh" "$TARGET/scripts/validate-workflow.sh"
chmod +x "$TARGET/scripts/validate-workflow.sh" \
  || { echo "错误: 赋执行位失败 $TARGET/scripts/validate-workflow.sh" >&2; exit 1; }
say "已装: scripts/validate-workflow.sh（已赋执行位）"

# 6) .gitignore 补充（幂等追加工作流草稿区规则，不动既有内容）
gi="$TARGET/.gitignore"
touch "$gi" || { echo "错误: 无法写入 $gi" >&2; exit 1; }
for rule in '.codex/sdd/*' '!.codex/sdd/.gitkeep'; do
  grep -qxF "$rule" "$gi" || printf '%s\n' "$rule" >> "$gi"
done
say "已装: .gitignore 已确保 .codex/sdd 草稿区忽略规则"

# ---------- 装后自检 ----------
echo "装后自检: 运行目标项目 ./scripts/validate-workflow.sh"
if (cd "$TARGET" && ./scripts/validate-workflow.sh); then
  echo "✓ 安装完成，自检全绿。下一步：填写 openspec/project.md 项目上下文；"
  echo "  在目标项目重启 Claude Code 或 Codex 会话即可使用五阶段工作流。"
  exit 0
else
  echo "错误: 装后自检未全绿，请把上方输出反馈给维护者。" >&2
  exit 1
fi
