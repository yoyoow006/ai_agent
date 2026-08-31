#!/usr/bin/env bash
# install-workflow.sh —— 把本仓库的风险分级工作流资产一键安装到目标项目
# 用法: bash scripts/install-workflow.sh <目标项目路径> [--force]
#
# 资产源是 scripts/ai-workflow-assets/{shared,claude,codex} 三棵树（与
# install-ai-workflow.sh 共用同一单一来源，由结构校验保持与活动树字节一致）。
# 整树复制意味着仓库布局迁移后本脚本不会残留悬空源路径。
set -u

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SRC_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ASSETS="$SRC_ROOT/scripts/ai-workflow-assets"
SIDES=(shared claude codex)

FORCE=0
TARGET=""

usage() {
  cat <<'EOF'
用法: bash scripts/install-workflow.sh <目标项目路径> [--force]

把本仓库的风险分级 AI 编程助手工作流安装到目标项目（双运行时一次装齐）：
  CLAUDE.md / AGENTS.md          双运行时工作流总纲
  .ai/                            共享知识层骨架（kb/rules/prompts/tools；
                                  memory 只补缺，永不覆盖已有内容）
  .claude/ .codex/                双侧技能、角色适配与 ai-kb 兼容重定向入口
  openspec/                       变更数据层骨架 + 通用版 project.md（请装后填写）
  scripts/                        校验套件（validate-workflow.sh + lib + tests）

选项:
  --force   覆盖目标已存在的同名资产（覆盖前备份为 <原名>.bak；
            已有 .bak 会被替换；.ai/memory/ 例外——永不覆盖不备份）

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
for s in "${SIDES[@]}"; do
  [ -d "$ASSETS/$s" ] || die "源仓库异常: 找不到 scripts/ai-workflow-assets/$s（脚本须在本仓库内运行）"
done

# ---------- 工具 ----------
say()  { echo "  $*"; }
install_file() {  # 单文件复制；目标是目录时拒绝（cp 会静默复制进目录），cp 失败即中止
  [ ! -d "$2" ] || { echo "错误: 目标是目录，无法安装为文件: $2" >&2; exit 1; }
  cp -p "$1" "$2" || { echo "错误: 复制失败 $1 -> $2" >&2; exit 1; }
}
make_dir() {  # mkdir -p，失败即中止
  mkdir -p "$@" || { echo "错误: 创建目录失败: $*" >&2; exit 1; }
}
backup_file() {  # 文件型资产备份；幂等
  [ -f "$1" ] || return 0
  install_file "$1" "$1.bak"
  say "备份: ${1#"$TARGET"/} -> ${1#"$TARGET"/}.bak"
}

# 资产树文件清单：每行一个相对路径（按侧遍历，排序保证输出稳定）
asset_files() {
  (cd "$ASSETS/$1" && find . -type f) | sed 's|^\./||' | sort
}

# memory 只补缺：.ai/memory/ 下既有文件不冲突、不覆盖、不备份
is_memory() {
  case "$1" in
    .ai/memory/*) return 0 ;;
    *)            return 1 ;;
  esac
}

# ---------- 迁移前旧布局残留检测 ----------
# 迁移前安装的目标会残留 ai-kb/{kb,rules,memory} 平行正文，使目标校验器
# legacy_ai_kb_body_absent 红项；无 --force 时明确中止，有 --force 时整目录备份后清除。
legacy_found=""
for side in .claude .codex; do
  for sub in kb rules memory; do
    d="$TARGET/$side/ai-kb/$sub"
    if [ -d "$d" ] && find "$d" -type f -print -quit | grep -q .; then
      legacy_found="$legacy_found $side/ai-kb/$sub"
    fi
  done
done
if [ -n "$legacy_found" ]; then
  if [ "$FORCE" -ne 1 ]; then
    echo "错误: 检测到迁移前旧布局残留（含正文）:$legacy_found" >&2
    echo "加 --force 将把各侧 ai-kb 整目录备份为 ai-kb.bak/ 后重装重定向入口，或先人工迁移到 .ai/。" >&2
    exit 1
  fi
  for side in .claude .codex; do
    d="$TARGET/$side/ai-kb"
    if [ -d "$d" ]; then
      rm -rf "${d:?}.bak" || { echo "错误: 清理旧备份失败 $d.bak" >&2; exit 1; }
      mv "$d" "$d.bak" || { echo "错误: 备份失败 $d -> $d.bak" >&2; exit 1; }
      say "备份: $side/ai-kb/ -> $side/ai-kb.bak/（迁移前旧布局整体备份）"
    fi
  done
fi

# ---------- 冲突扫描（覆盖三棵资产树全量文件） ----------
conflicts=""
add_conflict() { conflicts="$conflicts
  - $1"; }

for s in "${SIDES[@]}"; do
  while IFS= read -r f; do
    [ -n "$f" ] || continue
    is_memory "$f" && continue
    [ -e "$TARGET/$f" ] && add_conflict "$f"
  done < <(asset_files "$s")
done

if [ -n "$conflicts" ] && [ "$FORCE" -ne 1 ]; then
  echo "错误: 目标项目存在以下同名资产，未安装：" >&2
  echo "$conflicts" >&2
  echo "确认覆盖请加 --force（覆盖前备份为 <原名>.bak）。" >&2
  exit 1
fi

# ---------- 安装 ----------
echo "安装风险分级工作流到: $TARGET"
[ "$FORCE" -ne 1 ] || say "模式: --force（覆盖前备份）"

total=0
for s in "${SIDES[@]}"; do
  count=0
  while IFS= read -r f; do
    [ -n "$f" ] || continue
    dst="$TARGET/$f"
    if is_memory "$f" && [ -e "$dst" ]; then
      say "保留: $f（memory 永不覆盖）"
      count=$((count + 1))
      continue
    fi
    make_dir "${dst%/*}"
    if [ "$FORCE" -eq 1 ]; then
      backup_file "$dst"
    fi
    install_file "$ASSETS/$s/$f" "$dst"
    count=$((count + 1))
  done < <(asset_files "$s")
  say "已装: $s 资产树（$count 个文件）"
  total=$((total + count))
done
say "共 $total 个资产文件落位"

# 说明：随包契约套件把 scripts/lib/install_ai_workflow.py 视为"源仓库标记"，且其目标模型为
# "单侧+profile"；双运行时目标无法通过该套件全绿（源仓专属用例）。因此本安装器：
#   1) 不随附便携安装器三件、不生成 assistant-profile，保持无 profile 的双侧必检语义；
#   2) 装后自检跑 --fast（秒级 core 结构校验），完整契约套件归源仓 CI 职责。

# 校验脚本确保可执行（防御：资产树 mode 应已是 0755）
if [ -f "$TARGET/scripts/validate-workflow.sh" ]; then
  chmod +x "$TARGET/scripts/validate-workflow.sh" \
    || { echo "错误: 赋执行位失败 $TARGET/scripts/validate-workflow.sh" >&2; exit 1; }
fi

# ---------- .gitignore 补充（幂等追加标记块，不动既有内容） ----------
gi="$TARGET/.gitignore"
touch "$gi" || { echo "错误: 无法写入 $gi" >&2; exit 1; }
if ! grep -qxF '# >>> install-workflow.sh >>>' "$gi"; then
  printf '%s\n' \
    '# >>> install-workflow.sh >>>' \
    '/.ai-local/' \
    '/.codex/sdd/' \
    '/.claude/sdd/' \
    '/.worktrees/' \
    '__pycache__/' \
    '*.py[cod]' \
    '# <<< install-workflow.sh <<<' >> "$gi" \
    || { echo "错误: 追加失败 $gi" >&2; exit 1; }
fi
say "已装: .gitignore 已确保草稿区/Python 缓存忽略规则"

# ---------- 装后自检（--fast：秒级 core 结构校验） ----------
echo "装后自检: 运行目标项目 ./scripts/validate-workflow.sh --fast"
if (cd "$TARGET" && ./scripts/validate-workflow.sh --fast); then
  echo "✓ 安装完成，自检全绿。下一步：填写 openspec/project.md 项目上下文；"
  echo "  在目标项目重启 Claude Code 或 Codex 会话即可使用风险分级工作流。"
  echo "  注：完整契约套件属源仓 CI 职责；双运行时目标内跑全量校验会有源仓专属用例不适用。"
  exit 0
else
  echo "错误: 装后自检未全绿，请把上方输出反馈给维护者。" >&2
  exit 1
fi
