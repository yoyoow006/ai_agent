#!/usr/bin/env bash
# 把 .ai/skills/ 同步到 .claude/skills/ 和 .codex/skills/
# skill 内容只维护 .ai/skills/ 一份，改完跑本脚本。
set -euo pipefail
cd "$(dirname "$0")/.."

for target in .claude/skills .codex/skills; do
  mkdir -p "$target"
  for skill_dir in .ai/skills/*/; do
    name=$(basename "$skill_dir")
    mkdir -p "$target/$name"
    cp "$skill_dir/SKILL.md" "$target/$name/SKILL.md"
  done
done

# 入口文件同样从 .ai/ 分发（内容一致，仅文件名不同）
# CLAUDE.md / AGENTS.md 已是薄入口，指向 .ai/workflow.md，通常无需同步。

echo "synced: $(ls .ai/skills | tr '\n' ' ')"
