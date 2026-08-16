#!/usr/bin/env bash
# 结构不变量校验——工作流的"测试套件"。骨架项立即绿，技能项随任务推进转绿。
set -u
cd "$(dirname "$0")/.."
fail=0
check() { if eval "$2" >/dev/null 2>&1; then echo "✓ $1"; else echo "✗ $1"; fail=1; fi; }

for d in openspec/changes openspec/plan openspec/specs openspec/archive \
         .claude/skills .claude/ai-kb/kb .claude/ai-kb/memory .claude/ai-kb/rules \
         .codex/skills .codex/sdd .codex/ai-kb/kb .codex/ai-kb/memory .codex/ai-kb/rules; do
  check "目录存在: $d" "[ -d '$d' ]"
done

for f in openspec/AGENTS.md openspec/project.md .claude/ai-kb/README.md .codex/README.md; do
  check "文件存在: $f" "[ -f '$f' ]"
done

for agent in .claude .codex; do
  for s in open design build verify archive tdd subagent-driven code-review \
           systematic-debugging verification git-worktrees parallel-agents writing-skills; do
    f="$agent/skills/$s/SKILL.md"
    check "技能存在: $agent/skills/$s" "[ -f '$f' ]"
    nm="$(awk 'NR>1&&/^---/{exit} NR>1' "$f" 2>/dev/null | sed -n 's/^name:[[:space:]]*//p' | head -1 | tr -d '\"' | tr -d '[:space:]')"
    check "frontmatter: $agent/skills/$s" "head -1 '$f' | grep -q '^---' && awk 'NR>1&&/^---/{exit} NR>1' '$f' | grep -q '^description:' && [ '${nm:-}' = '$s' ]"
  done
done

for c in openspec/changes/*/; do
  [ -f "${c}proposal.md" ] || continue
  check "proposal 状态字段: ${c%/}" "sed -n '1,15p' '${c}proposal.md' | grep -q '^状态:'"
done

for doc in CLAUDE.md AGENTS.md; do
  check "$doc 硬门禁" "grep -q '硬门禁' '$doc'"
  check "$doc 8态" "grep -q '草稿' '$doc' && grep -q '待确认规范' '$doc' && grep -q '设计中' '$doc' && grep -q '待确认计划' '$doc' && grep -q '构建中' '$doc' && grep -q '待验证' '$doc' && grep -q '待归档' '$doc' && grep -q '已归档' '$doc'"
  check "$doc ai-kb" "grep -q 'ai-kb' '$doc'"
done

for agent in .claude .codex; do
  check "$agent rules/index.md" "[ -f $agent/ai-kb/rules/index.md ]"
  check "$agent kb/overview.md" "[ -f $agent/ai-kb/kb/overview.md ]"
  check "$agent tdd 红绿重构" "grep -q '红' $agent/skills/tdd/SKILL.md && grep -q '绿' $agent/skills/tdd/SKILL.md && grep -q '重构' $agent/skills/tdd/SKILL.md"
  check "$agent debugging 记 memory" "grep -q 'ai-kb/memory' $agent/skills/systematic-debugging/SKILL.md"
  check "$agent verify 两阶段审查" "grep -q '规格符合性' $agent/skills/verify/SKILL.md && grep -q '代码质量' $agent/skills/verify/SKILL.md"
  check "$agent archive 知识沉淀" "grep -q '知识沉淀' $agent/skills/archive/SKILL.md"
  check "$agent archive delta 合并" "grep -q 'ADDED' $agent/skills/archive/SKILL.md"
  check "$agent open 四件套" "grep -q 'proposal' $agent/skills/open/SKILL.md && grep -q 'tasks' $agent/skills/open/SKILL.md"
  check "$agent archive 提交路径" "grep -q 'git add openspec/ $agent/ai-kb/' $agent/skills/archive/SKILL.md"
done
check "Codex 工具映射" "grep -q 'spawn_agent' .codex/README.md && grep -q 'fork_context' .codex/README.md"
check "Codex 派发适配注入" "grep -q 'Codex 执行环境' .codex/skills/build/SKILL.md && grep -q 'Codex 执行环境' .codex/skills/verify/SKILL.md && grep -q 'Codex 执行环境' .codex/skills/subagent-driven/SKILL.md && grep -q 'Codex 执行环境' .codex/skills/code-review/SKILL.md && grep -q 'Codex 执行环境' .codex/skills/parallel-agents/SKILL.md"
check "Codex SDD 工作区" "grep -q '.codex/sdd' .codex/skills/subagent-driven/SKILL.md"

if command -v openspec >/dev/null 2>&1; then
  check "openspec list 可运行" "openspec list --json"
  check "openspec validate --all" "openspec validate --all --no-interactive"
fi
exit $fail
