#!/usr/bin/env bash
# 结构不变量校验——工作流的"测试套件"。骨架项立即绿，技能项随任务推进转绿。
set -u
cd "$(dirname "$0")/.."
fail=0
check() { if eval "$2" >/dev/null 2>&1; then echo "✓ $1"; else echo "✗ $1"; fail=1; fi; }

for d in openspec/changes openspec/plan openspec/specs openspec/archive \
         .claude/skills .claude/ai-kb/kb .claude/ai-kb/memory .claude/ai-kb/rules; do
  check "目录存在: $d" "[ -d '$d' ]"
done

for s in open design build verify archive tdd subagent-driven code-review \
         systematic-debugging verification git-worktrees parallel-agents writing-skills; do
  f=".claude/skills/$s/SKILL.md"
  check "技能存在: $s" "[ -f '$f' ]"
  check "frontmatter: $s" "head -1 '$f' | grep -q '^---' && awk 'NR>1&&/^---/{exit} NR>1' '$f' | grep -q '^name:' && awk 'NR>1&&/^---/{exit} NR>1' '$f' | grep -q '^description:'"
done

check "CLAUDE.md 硬门禁" "grep -q '硬门禁' CLAUDE.md"
check "CLAUDE.md 8态" "grep -q '待确认规范' CLAUDE.md && grep -q '已归档' CLAUDE.md"
check "CLAUDE.md ai-kb" "grep -q 'ai-kb' CLAUDE.md"
check "rules/index.md" "[ -f .claude/ai-kb/rules/index.md ]"
check "kb/overview.md" "[ -f .claude/ai-kb/kb/overview.md ]"
check "tdd 红绿重构" "grep -q '红' .claude/skills/tdd/SKILL.md && grep -q '绿' .claude/skills/tdd/SKILL.md && grep -q '重构' .claude/skills/tdd/SKILL.md"
check "debugging 记 memory" "grep -q 'ai-kb/memory' .claude/skills/systematic-debugging/SKILL.md"
check "verify 两阶段审查" "grep -q '规格符合性' .claude/skills/verify/SKILL.md && grep -q '代码质量' .claude/skills/verify/SKILL.md"
check "archive 知识沉淀" "grep -q '知识沉淀' .claude/skills/archive/SKILL.md"
check "archive delta 合并" "grep -q 'ADDED' .claude/skills/archive/SKILL.md"
check "open 四件套" "grep -q 'proposal' .claude/skills/open/SKILL.md && grep -q 'tasks' .claude/skills/open/SKILL.md"

if command -v openspec >/dev/null 2>&1; then
  check "openspec list 可运行" "openspec list --json"
  check "openspec validate --all" "openspec validate --all --no-interactive"
fi
exit $fail
