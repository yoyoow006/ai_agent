#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHANGES = ROOT / "openspec" / "changes"
ARCHIVE = ROOT / "openspec" / "archive"
SPEC_ROOT = ROOT / "openspec" / "specs"


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def validate(change: Path) -> str | None:
    proposal = change / "proposal.md"
    tasks = change / "tasks.md"
    if not change.is_dir() or change.is_symlink():
        return None
    if not proposal.is_file() or not tasks.is_file():
        fail("proposal.md 或 tasks.md 不存在")
        return None
    text = read(proposal)
    mode_match = re.search(r"^模式:\s*(标准|严格)\s*$", text, re.M)
    status_match = re.search(r"^状态:\s*待归档\s*$", text, re.M)
    if not mode_match:
        fail("proposal 模式非法或未找到")
        return None
    if not status_match:
        fail("proposal 状态必须为 待归档")
        return None
    task_text = read(tasks)
    if re.search(r"^\s*-\s*\[\s\]\s+", task_text, re.M):
        fail("tasks 仍有未勾选任务")
        return None
    for record in (change / "review-findings.md", tasks):
        if not record.exists():
            continue
        content = read(record)
        if all(k in content for k in ("未验证范围", "残余风险")) and "finding 状态" in content:
            return mode_match.group(1)
    fail("终局记录缺少 finding 状态/未验证范围/残余风险")
    return None


def merge_specs(change: Path) -> list[Path]:
    changed: list[Path] = []
    specs = change / "specs"
    if not specs.is_dir():
        fail("缺少 specs 目录")
        return changed
    for delta in sorted(specs.glob("*/spec.md")):
        target = SPEC_ROOT / delta.parent.name / "spec.md"
        if not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(delta, target)
            changed.append(target)
            continue
        current = read(target)
        incoming = read(delta)
        if incoming in current:
            changed.append(target)
            continue
        # Conservative merge: append delta requirements not represented by heading.
        sections = re.split(r"(?=^### Requirement:)", incoming, flags=re.M)
        output = current.rstrip() + "\n\n"
        appended = 0
        for section in sections:
            if not section.startswith("### Requirement:"):
                continue
            heading = section.splitlines()[0]
            if heading not in current:
                output += section.rstrip() + "\n\n"
                appended += 1
        if appended:
            target.write_text(output.rstrip() + "\n", encoding="utf-8")
        changed.append(target)
    return changed


def update_index(change: Path, mode: str) -> None:
    line_match = re.search(r"^#\s*(.+)$", read(change / "proposal.md"), re.M)
    summary = line_match.group(1).strip() if line_match else change.name
    line = f"- `{change.name}` — {summary}（{mode}）\n"
    readme = change.parent / "README.md"
    current = read(readme) if readme.exists() else "# 归档变更索引\n"
    if f"- `{change.name}` —" not in current:
        readme.write_text(current.rstrip() + "\n" + line, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("change", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    change = args.change if args.change.is_absolute() else ROOT / args.change
    mode = validate(change)
    if mode is None:
        return 1
    if args.dry_run:
        print(f"PASS: {change.name} 可归档（dry-run）")
        print("后续门禁：bash scripts/validate-workflow.sh --archive-light")
        return 0
    destination = ARCHIVE / change.name
    if destination.exists() or destination.is_symlink():
        fail(f"归档目标已存在：{destination}")
        return 1
    changed_specs = merge_specs(change)
    if not changed_specs:
        return 1
    proposal = change / "proposal.md"
    proposal.write_text(read(proposal).replace("状态: 待归档", "状态: 已归档"), encoding="utf-8")
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    shutil.move(str(change), str(destination))
    update_index(destination, mode)
    print(f"ARCHIVED: {destination}")
    for path in changed_specs:
        print(f"SPEC: {path}")
    print("NEXT: 人工判断知识沉淀；运行 bash scripts/validate-workflow.sh --archive-light")
    print("NEXT: git diff --check && git status --short")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
